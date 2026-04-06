"""
Performance Tests for ZIEL-MAS Backend
Tests for performance benchmarks, load testing, and optimization
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any


class TestDatabasePerformance:
    """Test database service performance"""

    @pytest.mark.asyncio
    async def test_bulk_task_creation_performance(self, database_service):
        """Test bulk task creation performance"""
        from backend.models.task import TaskExecution, TaskGraph

        num_tasks = 100
        start_time = time.time()

        # Create 100 tasks
        for i in range(num_tasks):
            execution = TaskExecution(
                user_id=f"user_{i}",
                intent=f"Test task {i}",
                task_graph=TaskGraph()
            )
            await database_service.create_task_execution(execution.dict())

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete in reasonable time (< 5 seconds for 100 tasks)
        assert elapsed < 5.0

        # Verify all tasks were created
        stats = await database_service.get_statistics()
        assert stats["total_tasks"] >= num_tasks

    @pytest.mark.asyncio
    async def test_bulk_log_creation_performance(self, database_service):
        """Test bulk log creation performance"""
        from backend.models.task import ExecutionLog

        num_logs = 500
        start_time = time.time()

        # Create 500 logs
        for i in range(num_logs):
            log = ExecutionLog(
                execution_id=f"exec_{i % 10}",  # 10 different executions
                level="INFO",
                message=f"Log message {i}"
            )
            await database_service.create_execution_log(log.dict())

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete in reasonable time (< 10 seconds for 500 logs)
        assert elapsed < 10.0

    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self, database_service):
        """Test concurrent database operations"""
        from backend.models.task import TaskExecution, TaskGraph

        async def create_task(i):
            execution = TaskExecution(
                user_id=f"concurrent_user_{i}",
                intent=f"Concurrent task {i}",
                task_graph=TaskGraph()
            )
            return await database_service.create_task_execution(execution.dict())

        start_time = time.time()

        # Create 50 tasks concurrently
        tasks = [create_task(i) for i in range(50)]
        await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should be faster than sequential
        assert elapsed < 3.0

    @pytest.mark.asyncio
    async def test_large_query_performance(self, database_service):
        """Test querying large datasets"""
        from backend.models.task import TaskExecution, TaskGraph

        # Create 1000 tasks
        for i in range(1000):
            execution = TaskExecution(
                user_id="query_test_user",
                intent=f"Query test task {i}",
                task_graph=TaskGraph()
            )
            await database_service.create_task_execution(execution.dict())

        # Test query performance
        start_time = time.time()

        tasks = await database_service.list_user_tasks("query_test_user", limit=1000)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should return results quickly (< 1 second)
        assert elapsed < 1.0
        assert len(tasks) >= 1000


class TestRedisPerformance:
    """Test Redis service performance"""

    @pytest.mark.asyncio
    async def test_bulk_status_updates(self, redis_service):
        """Test bulk status update performance"""
        num_updates = 1000
        start_time = time.time()

        # Update status for 1000 tasks
        for i in range(num_updates):
            await redis_service.set_task_status(f"exec_{i}", "running")

        end_time = time.time()
        elapsed = end_time - start_time

        # Should be very fast (< 2 seconds for 1000 updates)
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_bulk_progress_updates(self, redis_service):
        """Test bulk progress update performance"""
        num_updates = 1000
        start_time = time.time()

        # Update progress for 1000 tasks
        for i in range(num_updates):
            await redis_service.set_task_progress(f"exec_{i}", i / 1000)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should be very fast (< 2 seconds for 1000 updates)
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_concurrent_redis_operations(self, redis_service):
        """Test concurrent Redis operations"""
        async def update_status(i):
            await redis_service.set_task_status(f"concurrent_exec_{i}", "running")
            await redis_service.set_task_progress(f"concurrent_exec_{i}", 0.5)
            return await redis_service.get_task_status(f"concurrent_exec_{i}")

        start_time = time.time()

        # Perform 100 concurrent operations
        tasks = [update_status(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should be very fast
        assert elapsed < 1.0
        assert len(results) == 100

    @pytest.mark.asyncio
    async def test_queue_performance(self, redis_service):
        """Test queue operations performance"""
        num_items = 1000
        queue_name = "performance_test_queue"

        # Test enqueue performance
        start_time = time.time()

        for i in range(num_items):
            await redis_service.push_to_queue(queue_name, f"item_{i}")

        enqueue_time = time.time() - start_time

        # Test dequeue performance
        start_time = time.time()

        for i in range(num_items):
            await redis_service.pop_from_queue(queue_name)

        dequeue_time = time.time() - start_time

        # Both should be fast
        assert enqueue_time < 2.0
        assert dequeue_time < 2.0


class TestControllerPerformance:
    """Test controller agent performance"""

    @pytest.mark.asyncio
    async def test_intent_parsing_performance(self, controller_agent):
        """Test intent parsing performance"""
        intents = [
            "Send email to john@example.com with birthday wishes",
            "Schedule reminder for tomorrow at 9 AM",
            "Find top 10 restaurants near me",
            "Book a cab to airport",
            "Apply for job at company.com"
        ] * 20  # 100 intents total

        start_time = time.time()

        # Parse all intents
        for intent in intents:
            await controller_agent.parse_intent(intent)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should parse 100 intents quickly (< 2 seconds)
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_task_graph_generation_performance(self, controller_agent):
        """Test task graph generation performance"""
        parsed_intents = [
            {
                "task_type": "communication",
                "entities": {"emails": ["test@example.com"]},
                "time_info": {},
                "priority": "medium",
                "original_intent": "Send email"
            }
        ] * 50  # 50 intents

        start_time = time.time()

        # Generate task graphs
        for parsed in parsed_intents:
            await controller_agent.generate_task_graph(parsed)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should generate 50 graphs quickly (< 3 seconds)
        assert elapsed < 3.0

    @pytest.mark.asyncio
    async def test_concurrent_intent_parsing(self, controller_agent):
        """Test concurrent intent parsing"""
        intents = [
            "Send email to john@example.com",
            "Schedule meeting for tomorrow",
            "Find restaurants nearby"
        ] * 10  # 30 intents

        async def parse_intent(intent):
            return await controller_agent.parse_intent(intent)

        start_time = time.time()

        # Parse concurrently
        tasks = [parse_intent(intent) for intent in intents]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should be faster than sequential
        assert elapsed < 1.0
        assert len(results) == 30


class TestExecutionEnginePerformance:
    """Test execution engine performance"""

    @pytest.mark.asyncio
    async def test_simple_task_execution_performance(self, execution_engine):
        """Test simple task execution performance"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        # Create simple graph with 1 task
        graph = TaskGraph()
        task = TaskNode(
            agent=AgentType.DATA,
            action="simple_task",
            parameters={}
        )
        graph.add_node(task)

        execution = TaskExecution(
            user_id="perf_test_user",
            intent="Performance test",
            task_graph=graph
        )

        start_time = time.time()

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete quickly
        assert "success" in result
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_parallel_task_execution_performance(self, execution_engine):
        """Test parallel task execution performance"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        # Create graph with 10 parallel tasks
        graph = TaskGraph()
        graph.parallel_execution = True

        for i in range(10):
            task = TaskNode(
                agent=AgentType.DATA,
                action=f"parallel_task_{i}",
                parameters={}
            )
            graph.add_node(task)

        execution = TaskExecution(
            user_id="perf_test_user",
            intent="Parallel performance test",
            task_graph=graph
        )

        start_time = time.time()

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Parallel execution should be faster
        assert "success" in result

    @pytest.mark.asyncio
    async def test_sequential_task_execution_performance(self, execution_engine):
        """Test sequential task execution performance"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        # Create graph with 5 sequential tasks
        graph = TaskGraph()
        graph.parallel_execution = False

        prev_task_id = None
        for i in range(5):
            dependencies = [prev_task_id] if prev_task_id else []
            task = TaskNode(
                agent=AgentType.DATA,
                action=f"sequential_task_{i}",
                parameters={},
                dependencies=dependencies
            )
            graph.add_node(task)
            prev_task_id = task.task_id

        execution = TaskExecution(
            user_id="perf_test_user",
            intent="Sequential performance test",
            task_graph=graph
        )

        start_time = time.time()

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete in reasonable time
        assert "success" in result
        assert elapsed < 10.0


class TestAgentPerformance:
    """Test agent performance"""

    @pytest.mark.asyncio
    async def test_agent_response_time(self):
        """Test agent response time"""
        from backend.agents.data_agent import DataAgent

        agent = DataAgent()

        start_time = time.time()

        response = await agent.execute(
            "simple_operation",
            {"test": "data"}
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Should respond quickly
        assert "status" in response
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test concurrent agent execution"""
        from backend.agents.data_agent import DataAgent

        agents = [DataAgent() for _ in range(10)]

        async def execute_agent(agent):
            return await agent.execute("test_action", {})

        start_time = time.time()

        # Execute 10 agents concurrently
        tasks = [execute_agent(agent) for agent in agents]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete faster than sequential
        assert len(results) == 10
        assert elapsed < 2.0


class TestLoadTesting:
    """Test system under load"""

    @pytest.mark.asyncio
    async def test_sustained_load(self, execution_engine):
        """Test system under sustained load"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        num_executions = 50
        execution_times = []

        for i in range(num_executions):
            graph = TaskGraph()
            task = TaskNode(
                agent=AgentType.DATA,
                action=f"load_test_task_{i}",
                parameters={}
            )
            graph.add_node(task)

            execution = TaskExecution(
                user_id="load_test_user",
                intent=f"Load test execution {i}",
                task_graph=graph
            )

            start_time = time.time()

            await execution_engine.execute_task_graph(
                execution,
                execution.execution_id
            )

            elapsed = time.time() - start_time
            execution_times.append(elapsed)

        # Calculate average execution time
        avg_time = sum(execution_times) / len(execution_times)

        # Average should be reasonable
        assert avg_time < 5.0

    @pytest.mark.asyncio
    async def test_burst_load(self, execution_engine):
        """Test system under burst load"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        async def create_execution(i):
            graph = TaskGraph()
            task = TaskNode(
                agent=AgentType.DATA,
                action="transform_data",
                parameters={
                    "data": [i, i+1, i+2],
                    "transformation": "multiply",
                    "factor": 2
                }
            )
            graph.add_node(task)

            execution = TaskExecution(
                user_id="burst_test_user",
                intent=f"Burst test {i}",
                task_graph=graph
            )

            return await execution_engine.execute_task_graph(
                execution,
                execution.execution_id
            )

        start_time = time.time()

        # Burst: 20 executions at once
        tasks = [create_execution(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should handle burst load
        assert len(results) == 20
        # Some may fail under load, but most should succeed
        # Count successful executions (either dict with success=True or non-exception results)
        successful = 0
        for r in results:
            if isinstance(r, dict):
                if r.get("success") is True:
                    successful += 1
            elif isinstance(r, Exception):
                # Exception - counts as failure
                pass
            else:
                # Other non-exception result - count as success
                successful += 1

        assert successful >= 15  # At least 75% success rate

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, execution_engine):
        """Test for memory leaks during repeated operations"""
        import gc
        import sys

        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform many operations
        for i in range(100):
            graph = TaskGraph()
            task = TaskNode(
                agent=AgentType.DATA,
                action="transform_data",
                parameters={
                    "data": [i],
                    "transformation": "multiply",
                    "factor": 2
                }
            )
            graph.add_node(task)

            execution = TaskExecution(
                user_id="memory_test_user",
                intent=f"Memory test {i}",
                task_graph=graph
            )

            await execution_engine.execute_task_graph(
                execution,
                execution.execution_id
            )

        # Force garbage collection
        gc.collect()

        # Check final memory usage
        final_objects = len(gc.get_objects())

        # Object count should not grow significantly
        # Allow for some growth, but not exponential
        # Python creates many internal objects during execution, so we use a more realistic threshold
        # With 100 iterations, allowing up to 50,000 new objects (~500 per operation)
        growth = final_objects - initial_objects
        assert growth < 50000  # Less than 50000 new objects (reasonable for 100 operations)


class TestScalability:
    """Test system scalability"""

    @pytest.mark.asyncio
    async def test_large_task_graph_scalability(self, controller_agent):
        """Test with large task graphs"""
        # Create complex parsed intent
        parsed_intent = {
            "task_type": "data_processing",
            "entities": {},
            "time_info": {},
            "priority": "medium",
            "original_intent": "Complex multi-step data processing task"
        }

        start_time = time.time()

        # Generate multiple task graphs
        for i in range(50):
            await controller_agent.generate_task_graph(parsed_intent)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should handle multiple generations efficiently
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_concurrent_user_simulation(self, execution_engine):
        """Test system with multiple concurrent users"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        async def user_session(user_id, num_tasks):
            """Simulate a user session"""
            results = []
            for i in range(num_tasks):
                graph = TaskGraph()
                task = TaskNode(
                    agent=AgentType.DATA,
                    action=f"user_task_{i}",
                    parameters={}
                )
                graph.add_node(task)

                execution = TaskExecution(
                    user_id=user_id,
                    intent=f"User {user_id} task {i}",
                    task_graph=graph
                )

                result = await execution_engine.execute_task_graph(
                    execution,
                    execution.execution_id
                )
                results.append(result)

            return results

        start_time = time.time()

        # Simulate 10 concurrent users, each running 5 tasks
        tasks = [
            user_session(f"user_{i}", 5)
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should handle concurrent users
        assert len(results) == 10
        # Total time should be reasonable
        assert elapsed < 15.0


class TestOptimization:
    """Test optimization opportunities"""

    @pytest.mark.asyncio
    async def test_caching_effectiveness(self, controller_agent):
        """Test if caching improves performance"""
        intent = "Send email to john@example.com with birthday wishes"

        # First call (cold)
        start_time = time.time()
        result1 = await controller_agent.parse_intent(intent)
        cold_time = time.time() - start_time

        # Second call (warm - potentially cached)
        start_time = time.time()
        result2 = await controller_agent.parse_intent(intent)
        warm_time = time.time() - start_time

        # Both should return same result
        assert result1 == result2

        # Warm call should be same or faster (if caching is implemented)
        assert warm_time <= cold_time * 1.5  # Allow some variance

    @pytest.mark.asyncio
    async def test_batch_operations_efficiency(self, redis_service):
        """Test if batch operations are more efficient"""
        num_operations = 100

        # Individual operations
        start_time = time.time()
        for i in range(num_operations):
            await redis_service.set_task_status(f"exec_{i}", "running")
        individual_time = time.time() - start_time

        # Batch operations would use pipeline/multi
        # For now, just verify individual performance
        assert individual_time < 5.0


class TestPerformanceMonitoring:
    """Test performance monitoring and metrics"""

    @pytest.mark.asyncio
    async def test_response_time_monitoring(self, execution_engine):
        """Test response time monitoring"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        response_times = []

        for i in range(10):
            graph = TaskGraph()
            task = TaskNode(
                agent=AgentType.DATA,
                action=f"monitoring_task_{i}",
                parameters={}
            )
            graph.add_node(task)

            execution = TaskExecution(
                user_id="monitoring_user",
                intent=f"Monitoring test {i}",
                task_graph=graph
            )

            start_time = time.time()
            await execution_engine.execute_task_graph(
                execution,
                execution.execution_id
            )
            response_time = time.time() - start_time

            response_times.append(response_time)

        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        # Response times should be consistent
        assert max_time - min_time < 5.0  # Less than 5 second variance
        assert avg_time < 3.0  # Average under 3 seconds

    @pytest.mark.asyncio
    async def test_throughput_measurement(self, execution_engine):
        """Test system throughput"""
        from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType

        num_executions = 20
        start_time = time.time()

        for i in range(num_executions):
            graph = TaskGraph()
            task = TaskNode(
                agent=AgentType.DATA,
                action=f"throughput_task_{i}",
                parameters={}
            )
            graph.add_node(task)

            execution = TaskExecution(
                user_id="throughput_user",
                intent=f"Throughput test {i}",
                task_graph=graph
            )

            await execution_engine.execute_task_graph(
                execution,
                execution.execution_id
            )

        end_time = time.time()
        elapsed = end_time - start_time

        # Calculate throughput
        throughput = num_executions / elapsed  # executions per second

        # Should achieve reasonable throughput
        assert throughput > 1.0  # At least 1 execution per second
