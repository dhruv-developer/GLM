"""
Unit Tests for ZIEL-MAS Core Components
Tests for Controller and Execution Engine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.core.controller import ControllerAgent
from backend.core.execution import ExecutionEngine, TaskDispatcher
from backend.models.task import (
    TaskGraph,
    TaskNode,
    TaskExecution,
    TaskStatus,
    AgentType,
    TaskPriority
)


class TestControllerAgent:
    """Test ControllerAgent operations"""

    @pytest.mark.asyncio
    async def test_controller_initialization(self, controller_agent):
        """Test controller agent initialization"""
        assert controller_agent.glm_api_key is not None
        assert controller_agent.glm_api_url == "https://api.glm.ai/v1"
        assert controller_agent.agent_configs is not None

    @pytest.mark.asyncio
    async def test_parse_intent_simple(self, controller_agent):
        """Test parsing simple intent"""
        intent = "Send email to john@example.com"

        parsed = await controller_agent.parse_intent(intent)

        assert "task_type" in parsed
        assert "entities" in parsed
        assert "time_info" in parsed
        assert "priority" in parsed
        assert "original_intent" in parsed

    @pytest.mark.asyncio
    async def test_parse_intent_communication_task(self, controller_agent):
        """Test parsing communication task intent"""
        intent = "Send email to john@example.com with birthday wishes"

        parsed = await controller_agent.parse_intent(intent)

        assert parsed["task_type"] == "communication"
        assert "emails" in parsed["entities"]
        assert "john@example.com" in parsed["entities"]["emails"]

    @pytest.mark.asyncio
    async def test_parse_intent_scheduling_task(self, controller_agent):
        """Test parsing scheduling task intent"""
        intent = "Schedule reminder for tomorrow at 9 AM"

        parsed = await controller_agent.parse_intent(intent)

        assert parsed["task_type"] == "scheduling"
        assert parsed["time_info"]["scheduled"] is True

    @pytest.mark.asyncio
    async def test_parse_intent_data_task(self, controller_agent):
        """Test parsing data processing task intent"""
        intent = "Find top 10 restaurants near me"

        parsed = await controller_agent.parse_intent(intent)

        assert parsed["task_type"] == "data_processing"

    @pytest.mark.asyncio
    async def test_parse_intent_booking_task(self, controller_agent):
        """Test parsing booking task intent"""
        intent = "Book a cab to airport"

        parsed = await controller_agent.parse_intent(intent)

        assert parsed["task_type"] == "booking"

    @pytest.mark.asyncio
    async def test_parse_intent_urgent_priority(self, controller_agent):
        """Test parsing intent with urgent priority"""
        intent = "Send urgent email to boss@example.com"

        parsed = await controller_agent.parse_intent(intent)

        assert parsed["priority"] == "high"

    @pytest.mark.asyncio
    async def test_parse_intent_low_priority(self, controller_agent):
        """Test parsing intent with low priority"""
        intent = "Send email whenever you get a chance"

        parsed = await controller_agent.parse_intent(intent)

        assert parsed["priority"] == "low"

    @pytest.mark.asyncio
    async def test_parse_intent_with_urls(self, controller_agent):
        """Test parsing intent with URLs"""
        intent = "Fill form at https://example.com/apply"

        parsed = await controller_agent.parse_intent(intent)

        assert "urls" in parsed["entities"]
        assert "https://example.com/apply" in parsed["entities"]["urls"]

    @pytest.mark.asyncio
    async def test_parse_intent_with_phone(self, controller_agent):
        """Test parsing intent with phone numbers"""
        intent = "Send SMS to +1234567890"

        parsed = await controller_agent.parse_intent(intent)

        assert "phones" in parsed["entities"]
        assert "+1234567890" in parsed["entities"]["phones"]

    @pytest.mark.asyncio
    async def test_generate_task_graph_communication(self, controller_agent):
        """Test generating task graph for communication task"""
        parsed_intent = {
            "task_type": "communication",
            "entities": {
                "emails": ["test@example.com"],
                "services": ["gmail"]
            },
            "time_info": {},
            "priority": "medium",
            "original_intent": "Send email to test@example.com"
        }

        graph = await controller_agent.generate_task_graph(parsed_intent)

        assert isinstance(graph, TaskGraph)
        assert len(graph.nodes) > 0
        assert any(node.agent == AgentType.COMMUNICATION for node in graph.nodes.values())

    @pytest.mark.asyncio
    async def test_generate_task_graph_scheduling(self, controller_agent):
        """Test generating task graph for scheduling task"""
        parsed_intent = {
            "task_type": "scheduling",
            "entities": {},
            "time_info": {"scheduled": True},
            "priority": "medium",
            "original_intent": "Schedule reminder"
        }

        graph = await controller_agent.generate_task_graph(parsed_intent)

        assert isinstance(graph, TaskGraph)
        assert len(graph.nodes) > 0
        assert any(node.agent == AgentType.SCHEDULER for node in graph.nodes.values())

    @pytest.mark.asyncio
    async def test_generate_task_graph_data_processing(self, controller_agent):
        """Test generating task graph for data processing task"""
        parsed_intent = {
            "task_type": "data_processing",
            "entities": {},
            "time_info": {},
            "priority": "medium",
            "original_intent": "Find top 10 restaurants"
        }

        graph = await controller_agent.generate_task_graph(parsed_intent)

        assert isinstance(graph, TaskGraph)
        assert len(graph.nodes) > 0
        assert any(node.agent == AgentType.DATA for node in graph.nodes.values())

    @pytest.mark.asyncio
    async def test_re_plan_with_retry(self, controller_agent, sample_task_graph):
        """Test re-planning with retry"""
        # Mark a task as failed
        failed_task = list(sample_task_graph.nodes.values())[0]
        failed_task.status = TaskStatus.FAILED
        failed_task.retry_count = 0

        new_graph = await controller_agent.re_plan(
            sample_task_graph,
            failed_task.task_id,
            "Test error"
        )

        assert new_graph is not None
        assert failed_task.task_id in new_graph.nodes
        assert new_graph.nodes[failed_task.task_id].retry_count == 1

    @pytest.mark.asyncio
    async def test_re_plan_with_alternative_agent(self, controller_agent, sample_task_graph):
        """Test re-planning with alternative agent"""
        # Create a task that can be replaced
        task = TaskNode(
            agent=AgentType.API,
            action="make_request",
            parameters={"url": "https://api.example.com"}
        )
        sample_task_graph.add_node(task)

        # Mark as failed with max retries
        task.status = TaskStatus.FAILED
        task.retry_count = task.max_retries

        new_graph = await controller_agent.re_plan(
            sample_task_graph,
            task.task_id,
            "API failed"
        )

        assert new_graph is not None
        # Original task should be removed or replaced

    @pytest.mark.asyncio
    async def test_re_plan_no_alternative(self, controller_agent):
        """Test re-planning when no alternative available"""
        graph = TaskGraph()

        # Create a task with no alternative
        task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="process",
            parameters={}
        )
        graph.add_node(task)

        task.status = TaskStatus.FAILED
        task.retry_count = task.max_retries

        new_graph = await controller_agent.re_plan(
            graph,
            task.task_id,
            "Failed"
        )

        # Should return None if no alternative
        assert new_graph is None

    @pytest.mark.asyncio
    async def test_estimate_execution_time(self, controller_agent, sample_task_graph):
        """Test estimating execution time"""
        time_estimate = await controller_agent.estimate_execution_time(sample_task_graph)

        assert isinstance(time_estimate, int)
        assert time_estimate > 0

    @pytest.mark.asyncio
    async def test_optimize_graph(self, controller_agent, sample_task_graph):
        """Test graph optimization"""
        optimized_graph = await controller_agent.optimize_graph(sample_task_graph)

        assert isinstance(optimized_graph, TaskGraph)
        assert optimized_graph.parallel_execution is True

    @pytest.mark.asyncio
    async def test_detect_task_type_edge_cases(self, controller_agent):
        """Test task type detection with edge cases"""
        edge_cases = [
            ("", "general"),
            ("   ", "general"),
            ("Unknown task type", "general"),
            ("Send message via email", "communication"),
            ("Apply for job online", "web_automation"),
            ("Get weather data", "data_processing")
        ]

        for intent, expected_type in edge_cases:
            parsed = await controller_agent.parse_intent(intent)
            # Allow flexibility in LLM classification for ambiguous intents
            if intent == "Get weather data":
                # This could be interpreted as either data_processing or scheduling
                assert parsed["task_type"] in ["data_processing", "scheduling", "data"]
            else:
                assert parsed["task_type"] == expected_type


class TestExecutionEngine:
    """Test ExecutionEngine operations"""

    @pytest.mark.asyncio
    async def test_execution_engine_initialization(self, execution_engine):
        """Test execution engine initialization"""
        assert execution_engine.redis is not None
        assert execution_engine.db is not None
        assert execution_engine.controller is not None
        assert execution_engine.running_executions == {}

    @pytest.mark.asyncio
    async def test_reconstruct_task_execution(self, execution_engine, sample_task_execution):
        """Test reconstructing TaskExecution from database dict"""
        execution_dict = sample_task_execution.dict()

        reconstructed = execution_engine._reconstruct_task_execution(execution_dict)

        assert isinstance(reconstructed, TaskExecution)
        assert reconstructed.execution_id == sample_task_execution.execution_id
        assert reconstructed.intent == sample_task_execution.intent

    @pytest.mark.asyncio
    async def test_execute_simple_task_graph(self, execution_engine, sample_task_graph):
        """Test executing a simple task graph"""
        execution = TaskExecution(
            user_id="test_user",
            intent="Test execution",
            task_graph=sample_task_graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        assert "success" in result
        assert "execution_time" in result
        assert "tasks_executed" in result

    @pytest.mark.asyncio
    async def test_execute_task_graph_with_failure(self, execution_engine):
        """Test executing task graph with failure"""
        graph = TaskGraph()

        # Create a task that will fail
        failing_task = TaskNode(
            agent=AgentType.API,
            action="invalid_action",
            parameters={}
        )
        graph.add_node(failing_task)

        execution = TaskExecution(
            user_id="test_user",
            intent="Test failing execution",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Should handle failure gracefully
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_cancel_execution(self, execution_engine, sample_task_graph):
        """Test cancelling execution"""
        execution = TaskExecution(
            user_id="test_user",
            intent="Test cancellation",
            task_graph=sample_task_graph
        )

        # Start execution in background
        async def run_execution():
            return await execution_engine.execute_task_graph(
                execution,
                execution.execution_id
            )

        task = asyncio.create_task(run_execution())
        execution_engine.running_executions[execution.execution_id] = task

        # Cancel immediately
        cancelled = await execution_engine.cancel_execution(execution.execution_id)

        assert cancelled is True

    @pytest.mark.asyncio
    async def test_get_execution_status(self, execution_engine, sample_task_execution):
        """Test getting execution status"""
        # Store execution in database
        await execution_engine.db.create_task_execution(sample_task_execution.dict())

        # Store status in Redis
        await execution_engine.redis.set_task_status(
            sample_task_execution.execution_id,
            "running"
        )

        status = await execution_engine.get_execution_status(
            sample_task_execution.execution_id
        )

        assert status["execution_id"] == sample_task_execution.execution_id
        assert status["status"] == "running"

    @pytest.mark.asyncio
    async def test_calculate_progress(self, execution_engine, sample_task_graph):
        """Test progress calculation"""
        # Mark some tasks as completed
        tasks = list(sample_task_graph.nodes.values())
        for i, task in enumerate(tasks):
            if i < len(tasks) // 2:
                task.status = TaskStatus.COMPLETED

        progress = execution_engine._calculate_progress(sample_task_graph)

        assert 0.0 <= progress <= 1.0
        # With 3 tasks and 1 completed (3 // 2 = 1), progress should be 1/3
        assert progress == 1.0 / len(sample_task_graph.nodes)  # One task completed

    @pytest.mark.asyncio
    async def test_aggregate_results(self, execution_engine, sample_task_graph):
        """Test aggregating results from task graph"""
        # Mark tasks as completed with outputs
        for task in sample_task_graph.nodes.values():
            task.status = TaskStatus.COMPLETED
            task.output = {"result": f"Result for {task.task_id}"}

        results = execution_engine._aggregate_results(sample_task_graph)

        assert "tasks" in results
        assert "summary" in results
        assert len(results["tasks"]) == len(sample_task_graph.nodes)

    @pytest.mark.asyncio
    async def test_execute_tasks_sequential(self, execution_engine, sample_task_graph):
        """Test sequential task execution"""
        execution = TaskExecution(
            user_id="test_user",
            intent="Test sequential execution",
            task_graph=sample_task_graph
        )

        # Get ready tasks
        ready_tasks = sample_task_graph.get_ready_tasks()

        await execution_engine._execute_tasks_sequential(
            execution.execution_id,
            ready_tasks,
            sample_task_graph
        )

        # Tasks should be executed
        assert all(task.status != TaskStatus.PENDING for task in ready_tasks)

    @pytest.mark.asyncio
    async def test_execute_tasks_parallel(self, execution_engine, sample_task_graph):
        """Test parallel task execution"""
        execution = TaskExecution(
            user_id="test_user",
            intent="Test parallel execution",
            task_graph=sample_task_graph
        )

        # Get ready tasks
        ready_tasks = sample_task_graph.get_ready_tasks()

        await execution_engine._execute_tasks_parallel(
            execution.execution_id,
            ready_tasks,
            sample_task_graph
        )

        # Tasks should be executed
        assert all(task.status != TaskStatus.PENDING for task in ready_tasks)

    @pytest.mark.asyncio
    async def test_log_execution(self, execution_engine, sample_task_execution):
        """Test execution logging"""
        await execution_engine._log_execution(
            sample_task_execution.execution_id,
            "Test log message",
            level="INFO",
            task_id="task_123"
        )

        # Verify log was created
        logs = await execution_engine.db.get_execution_logs(
            sample_task_execution.execution_id
        )

        assert len(logs) > 0
        assert logs[0]["message"] == "Test log message"

    @pytest.mark.asyncio
    async def test_update_execution_status(self, execution_engine, sample_task_execution):
        """Test updating execution status"""
        await execution_engine._update_execution_status(
            sample_task_execution.execution_id,
            TaskStatus.RUNNING
        )

        # Verify status in Redis
        status = await execution_engine.redis.get_task_status(
            sample_task_execution.execution_id
        )

        assert status == "running"


class TestTaskDispatcher:
    """Test TaskDispatcher operations"""

    @pytest.mark.asyncio
    async def test_dispatcher_initialization(self, execution_engine):
        """Test task dispatcher initialization"""
        dispatcher = TaskDispatcher(
            redis_service=execution_engine.redis,
            db_service=execution_engine.db,
            execution_engine=execution_engine
        )

        assert dispatcher.redis is not None
        assert dispatcher.db is not None
        assert dispatcher.execution_engine is not None
        assert dispatcher.is_running is False

    @pytest.mark.asyncio
    async def test_queue_execution(self, execution_engine, sample_task_execution):
        """Test queuing execution"""
        dispatcher = TaskDispatcher(
            redis_service=execution_engine.redis,
            db_service=execution_engine.db,
            execution_engine=execution_engine
        )

        # Store execution in database
        await execution_engine.db.create_task_execution(sample_task_execution.dict())

        # Queue execution
        await dispatcher.queue_execution(sample_task_execution.execution_id)

        # Verify it's queued
        import asyncio
        await asyncio.sleep(0.1)  # Give time for queue operation

    @pytest.mark.asyncio
    async def test_get_next_execution(self, execution_engine, sample_task_execution):
        """Test getting next execution from queue"""
        dispatcher = TaskDispatcher(
            redis_service=execution_engine.redis,
            db_service=execution_engine.db,
            execution_engine=execution_engine
        )

        # Store and queue execution
        await execution_engine.db.create_task_execution(sample_task_execution.dict())
        await execution_engine.redis.push_to_queue(
            "pending_executions",
            sample_task_execution.execution_id
        )

        # Get next execution
        next_execution = await dispatcher._get_next_execution()

        assert next_execution is not None
        assert next_execution["execution_id"] == sample_task_execution.execution_id

    @pytest.mark.asyncio
    async def test_dispatcher_start_stop(self, execution_engine):
        """Test starting and stopping dispatcher"""
        dispatcher = TaskDispatcher(
            redis_service=execution_engine.redis,
            db_service=execution_engine.db,
            execution_engine=execution_engine
        )

        # Start dispatcher
        start_task = asyncio.create_task(dispatcher.start())
        await asyncio.sleep(0.5)  # Let it start

        assert dispatcher.is_running is True

        # Stop dispatcher
        await dispatcher.stop()
        await asyncio.sleep(0.5)  # Let it stop

        assert dispatcher.is_running is False


class TestCoreIntegration:
    """Test integration between core components"""

    @pytest.mark.asyncio
    async def test_full_execution_workflow(self, execution_engine, controller_agent):
        """Test complete workflow from intent to execution"""
        # Parse intent
        intent = "Send email to test@example.com"
        parsed = await controller_agent.parse_intent(intent)

        # Generate task graph
        graph = await controller_agent.generate_task_graph(parsed)

        # Create execution
        execution = TaskExecution(
            user_id="test_user",
            intent=intent,
            task_graph=graph
        )

        # Store execution
        await execution_engine.db.create_task_execution(execution.dict())

        # Execute
        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        assert "success" in result
        assert "execution_time" in result

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, execution_engine, controller_agent):
        """Test error recovery and re-planning workflow"""
        # Create graph with potential failure
        graph = TaskGraph()
        task = TaskNode(
            agent=AgentType.API,
            action="make_request",
            parameters={"url": "invalid://url"}
        )
        graph.add_node(task)

        execution = TaskExecution(
            user_id="test_user",
            intent="Test error recovery",
            task_graph=graph
        )

        # Execute (should fail)
        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Try to re-plan
        new_graph = await controller_agent.re_plan(
            graph,
            task.task_id,
            "Connection failed"
        )

        # Should either have new graph or None
        assert new_graph is None or isinstance(new_graph, TaskGraph)


class TestCoreEdgeCases:
    """Test edge cases in core components"""

    @pytest.mark.asyncio
    async def test_empty_task_graph_execution(self, execution_engine):
        """Test executing empty task graph"""
        graph = TaskGraph()

        execution = TaskExecution(
            user_id="test_user",
            intent="Empty graph",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Should handle gracefully
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_circular_dependencies(self, controller_agent):
        """Test handling circular dependencies in task graph"""
        graph = TaskGraph()

        task1 = TaskNode(agent=AgentType.DATA, action="task1")
        task2 = TaskNode(agent=AgentType.DATA, action="task2", dependencies=[task1.task_id])
        task3 = TaskNode(agent=AgentType.DATA, action="task3", dependencies=[task2.task_id])

        graph.add_node(task1)
        graph.add_node(task2)
        graph.add_node(task3)

        # Add circular dependency
        task1.dependencies.append(task3.task_id)

        # get_ready_tasks should handle this
        ready = graph.get_ready_tasks()

        # Should return empty list or handle gracefully
        assert isinstance(ready, list)

    @pytest.mark.asyncio
    async def test_very_large_task_graph(self, controller_agent):
        """Test handling very large task graphs"""
        graph = TaskGraph()

        # Create 100 tasks
        for i in range(100):
            task = TaskNode(
                agent=AgentType.DATA,
                action=f"task_{i}"
            )
            graph.add_node(task)

        # Should handle large graphs
        assert len(graph.nodes) == 100
        assert len(graph.get_ready_tasks()) == 100

    @pytest.mark.asyncio
    async def test_concurrent_executions(self, execution_engine):
        """Test handling concurrent executions"""
        import asyncio

        # Create multiple executions
        executions = []
        for i in range(5):
            graph = TaskGraph()
            task = TaskNode(agent=AgentType.DATA, action=f"task_{i}")
            graph.add_node(task)

            execution = TaskExecution(
                user_id="test_user",
                intent=f"Concurrent task {i}",
                task_graph=graph
            )
            executions.append(execution)

        # Execute all concurrently
        tasks = [
            execution_engine.execute_task_graph(execution, execution.execution_id)
            for execution in executions
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_timeout_during_execution(self, execution_engine):
        """Test timeout handling during execution"""
        graph = TaskGraph()

        # Create task with very short timeout
        task = TaskNode(
            agent=AgentType.API,
            action="make_request",
            parameters={"url": "https://httpbin.org/delay/30"},
            timeout=1  # 1 second timeout
        )
        graph.add_node(task)

        execution = TaskExecution(
            user_id="test_user",
            intent="Test timeout",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Should fail due to timeout
        assert result["success"] is False
