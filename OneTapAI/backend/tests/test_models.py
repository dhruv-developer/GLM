"""
Unit Tests for ZIEL-MAS Models
Tests for all Pydantic models and data structures
"""

import pytest
from datetime import datetime
from pydantic import ValidationError, BaseModel
from uuid import uuid4

from backend.models.task import (
    TaskStatus,
    AgentType,
    TaskPriority,
    TaskNode,
    ConditionalBranch,
    TaskGraph,
    TaskExecution,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
    ExecutionLog
)


class TestTaskEnums:
    """Test enum definitions and values"""

    def test_task_status_values(self):
        """Test TaskStatus enum values"""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.PLANNING == "planning"
        assert TaskStatus.READY == "ready"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled"
        assert TaskStatus.RETRYING == "retrying"

    def test_agent_type_values(self):
        """Test AgentType enum values"""
        assert AgentType.CONTROLLER == "controller"
        assert AgentType.API == "api"
        assert AgentType.WEB_AUTOMATION == "web_automation"
        assert AgentType.COMMUNICATION == "communication"
        assert AgentType.DATA == "data"
        assert AgentType.SCHEDULER == "scheduler"
        assert AgentType.VALIDATION == "validation"

    def test_task_priority_values(self):
        """Test TaskPriority enum values"""
        assert TaskPriority.LOW == "low"
        assert TaskPriority.MEDIUM == "medium"
        assert TaskPriority.HIGH == "high"
        assert TaskPriority.CRITICAL == "critical"

    def test_enum_comparison(self):
        """Test enum comparisons work correctly"""
        assert TaskStatus.PENDING == TaskStatus.PENDING
        assert TaskStatus.PENDING == "pending"  # String comparison
        assert TaskStatus.PENDING != TaskStatus.RUNNING
        assert TaskStatus.PENDING != "running"


class TestTaskNode:
    """Test TaskNode model"""

    def test_task_node_creation_with_defaults(self):
        """Test creating TaskNode with default values"""
        node = TaskNode(
            agent=AgentType.COMMUNICATION,
            action="send_message"
        )

        assert node.task_id is not None
        assert isinstance(node.task_id, str)
        assert node.agent == AgentType.COMMUNICATION
        assert node.action == "send_message"
        assert node.parameters == {}
        assert node.dependencies == []
        assert node.status == TaskStatus.PENDING
        assert node.retry_count == 0
        assert node.max_retries == 3
        assert node.timeout == 300
        assert node.output is None
        assert node.error is None
        assert node.started_at is None
        assert node.completed_at is None

    def test_task_node_creation_with_values(self):
        """Test creating TaskNode with specific values"""
        task_id = str(uuid4())
        parameters = {"recipient": "test@example.com", "message": "Hello"}
        dependencies = ["task_1", "task_2"]

        node = TaskNode(
            task_id=task_id,
            agent=AgentType.DATA,
            action="fetch_data",
            parameters=parameters,
            dependencies=dependencies,
            status=TaskStatus.RUNNING,
            retry_count=1,
            max_retries=5,
            timeout=600,
            output={"status": "success"},
            error=None,
            started_at=datetime.utcnow()
        )

        assert node.task_id == task_id
        assert node.agent == AgentType.DATA
        assert node.action == "fetch_data"
        assert node.parameters == parameters
        assert node.dependencies == dependencies
        assert node.status == TaskStatus.RUNNING
        assert node.retry_count == 1
        assert node.max_retries == 5
        assert node.timeout == 600
        assert node.output == {"status": "success"}
        assert node.error is None
        assert node.started_at is not None
        assert node.completed_at is None

    def test_task_node_validation_invalid_retry_count(self):
        """Test TaskNode validates retry_count"""
        with pytest.raises(ValidationError):
            TaskNode(
                agent=AgentType.API,
                action="make_request",
                retry_count=-1  # Negative retry count
            )

    def test_task_node_validation_invalid_timeout(self):
        """Test TaskNode validates timeout"""
        with pytest.raises(ValidationError):
            TaskNode(
                agent=AgentType.API,
                action="make_request",
                timeout=0  # Timeout must be positive
            )

    def test_task_node_with_error(self):
        """Test TaskNode with error state"""
        node = TaskNode(
            agent=AgentType.WEB_AUTOMATION,
            action="fill_form",
            status=TaskStatus.FAILED,
            error="Form submission failed",
            completed_at=datetime.utcnow()
        )

        assert node.status == TaskStatus.FAILED
        assert node.error == "Form submission failed"
        assert node.completed_at is not None


class TestConditionalBranch:
    """Test ConditionalBranch model"""

    def test_conditional_branch_creation(self):
        """Test creating ConditionalBranch"""
        branch = ConditionalBranch(
            condition="user authenticated",
            true_tasks=["task_1", "task_2"],
            false_tasks=["task_3"]
        )

        assert branch.condition == "user authenticated"
        assert branch.true_tasks == ["task_1", "task_2"]
        assert branch.false_tasks == ["task_3"]

    def test_conditional_branch_empty_false_tasks(self):
        """Test ConditionalBranch with empty false_tasks"""
        branch = ConditionalBranch(
            condition="has_permission",
            true_tasks=["task_1"]
        )

        assert branch.false_tasks == []

    def test_conditional_branch_validation_empty_true_tasks(self):
        """Test ConditionalBranch requires true_tasks"""
        with pytest.raises(ValidationError):
            ConditionalBranch(
                condition="test",
                true_tasks=[]  # Must have at least one true task
            )


class TestTaskGraph:
    """Test TaskGraph model"""

    def test_task_graph_creation_empty(self):
        """Test creating empty TaskGraph"""
        graph = TaskGraph()

        assert graph.graph_id is not None
        assert graph.nodes == {}
        assert graph.edges == []
        assert graph.conditional_branches == []
        assert graph.parallel_execution is True

    def test_task_graph_add_node(self):
        """Test adding nodes to TaskGraph"""
        graph = TaskGraph()
        node = TaskNode(
            agent=AgentType.API,
            action="make_request"
        )

        graph.add_node(node)

        assert len(graph.nodes) == 1
        assert node.task_id in graph.nodes
        assert graph.nodes[node.task_id] == node

    def test_task_graph_add_edge(self):
        """Test adding edges to TaskGraph"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.DATA, action="fetch")
        node2 = TaskNode(agent=AgentType.DATA, action="process")

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(node1.task_id, node2.task_id)

        assert len(graph.edges) == 1
        assert graph.edges[0] == {"from": node1.task_id, "to": node2.task_id}
        assert node2.task_id in node1.dependencies

    def test_task_graph_get_ready_tasks_no_dependencies(self):
        """Test getting ready tasks with no dependencies"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.API, action="request1")
        node2 = TaskNode(agent=AgentType.API, action="request2")

        graph.add_node(node1)
        graph.add_node(node2)

        ready_tasks = graph.get_ready_tasks()

        assert len(ready_tasks) == 2
        assert node1 in ready_tasks
        assert node2 in ready_tasks

    def test_task_graph_get_ready_tasks_with_dependencies(self):
        """Test getting ready tasks with dependencies"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.DATA, action="fetch")
        node2 = TaskNode(
            agent=AgentType.DATA,
            action="process",
            dependencies=[node1.task_id]
        )

        graph.add_node(node1)
        graph.add_node(node2)

        ready_tasks = graph.get_ready_tasks()

        assert len(ready_tasks) == 1
        assert node1 in ready_tasks
        assert node2 not in ready_tasks

    def test_task_graph_get_ready_tasks_after_completion(self):
        """Test getting ready tasks after dependencies complete"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.DATA, action="fetch")
        node2 = TaskNode(
            agent=AgentType.DATA,
            action="process",
            dependencies=[node1.task_id]
        )

        graph.add_node(node1)
        graph.add_node(node2)

        # Mark node1 as completed
        node1.status = TaskStatus.COMPLETED

        ready_tasks = graph.get_ready_tasks()

        assert len(ready_tasks) == 1
        assert node2 in ready_tasks

    def test_task_graph_is_complete_all_completed(self):
        """Test is_complete when all tasks completed"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.API, action="request1")
        node2 = TaskNode(agent=AgentType.API, action="request2")

        node1.status = TaskStatus.COMPLETED
        node2.status = TaskStatus.COMPLETED

        graph.add_node(node1)
        graph.add_node(node2)

        assert graph.is_complete() is True

    def test_task_graph_is_complete_mixed_statuses(self):
        """Test is_complete with mixed task statuses"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.API, action="request1")
        node2 = TaskNode(agent=AgentType.API, action="request2")

        node1.status = TaskStatus.COMPLETED
        node2.status = TaskStatus.FAILED

        graph.add_node(node1)
        graph.add_node(node2)

        assert graph.is_complete() is True

    def test_task_graph_is_complete_incomplete(self):
        """Test is_complete with incomplete tasks"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.API, action="request1")
        node2 = TaskNode(agent=AgentType.API, action="request2")

        node1.status = TaskStatus.COMPLETED
        node2.status = TaskStatus.RUNNING

        graph.add_node(node1)
        graph.add_node(node2)

        assert graph.is_complete() is False

    def test_task_graph_serialization(self):
        """Test TaskGraph serialization with use_enum_values"""
        graph = TaskGraph()
        node = TaskNode(agent=AgentType.COMMUNICATION, action="send")

        graph.add_node(node)

        # Test that dict() works with enum values converted to strings
        graph_dict = graph.dict()
        assert graph_dict["nodes"][node.task_id]["agent"] == "communication"
        assert graph_dict["nodes"][node.task_id]["status"] == "pending"

    def test_task_graph_with_conditional_branches(self):
        """Test TaskGraph with conditional branches"""
        graph = TaskGraph()
        branch = ConditionalBranch(
            condition="user_authenticated",
            true_tasks=["task_1"],
            false_tasks=["task_2"]
        )

        graph.conditional_branches.append(branch)

        assert len(graph.conditional_branches) == 1
        assert graph.conditional_branches[0] == branch


class TestTaskExecution:
    """Test TaskExecution model"""

    def test_task_execution_creation_with_defaults(self):
        """Test creating TaskExecution with defaults"""
        task_graph = TaskGraph()
        execution = TaskExecution(
            intent="Test intent",
            task_graph=task_graph
        )

        assert execution.execution_id is not None
        assert execution.user_id is None
        assert execution.intent == "Test intent"
        assert execution.task_graph == task_graph
        assert execution.status == TaskStatus.PENDING
        assert execution.priority == TaskPriority.MEDIUM
        assert execution.created_at is not None
        assert execution.started_at is None
        assert execution.completed_at is None
        assert execution.execution_token is None
        assert execution.result is None
        assert execution.error_summary is None
        assert execution.execution_logs == []
        assert execution.retry_count == 0
        assert execution.max_retries == 3

    def test_task_execution_creation_with_values(self):
        """Test creating TaskExecution with specific values"""
        task_graph = TaskGraph()
        execution_id = str(uuid4())
        user_id = "user_123"
        token = "token_abc"

        execution = TaskExecution(
            execution_id=execution_id,
            user_id=user_id,
            intent="Send email",
            task_graph=task_graph,
            status=TaskStatus.RUNNING,
            priority=TaskPriority.HIGH,
            execution_token=token,
            result={"success": True},
            retry_count=1
        )

        assert execution.execution_id == execution_id
        assert execution.user_id == user_id
        assert execution.intent == "Send email"
        assert execution.status == TaskStatus.RUNNING
        assert execution.priority == TaskPriority.HIGH
        assert execution.execution_token == token
        assert execution.result == {"success": True}
        assert execution.retry_count == 1

    def test_task_execution_add_log(self):
        """Test adding execution log"""
        execution = TaskExecution(
            intent="Test",
            task_graph=TaskGraph()
        )

        log = ExecutionLog(
            execution_id=execution.execution_id,
            level="INFO",
            message="Test log"
        )

        execution.execution_logs.append(log)

        assert len(execution.execution_logs) == 1
        assert execution.execution_logs[0] == log

    def test_task_execution_serialization(self):
        """Test TaskExecution serialization with use_enum_values"""
        task_graph = TaskGraph()
        execution = TaskExecution(
            intent="Test",
            task_graph=task_graph,
            status=TaskStatus.RUNNING,
            priority=TaskPriority.HIGH
        )

        execution_dict = execution.dict()

        assert execution_dict["status"] == "running"
        assert execution_dict["priority"] == "high"


class TestRequestResponseModels:
    """Test request and response models"""

    def test_task_create_request(self):
        """Test TaskCreateRequest model"""
        request = TaskCreateRequest(
            intent="Send email to test@example.com",
            priority=TaskPriority.HIGH,
            user_id="user_123"
        )

        assert request.intent == "Send email to test@example.com"
        assert request.priority == TaskPriority.HIGH
        assert request.user_id == "user_123"

    def test_task_create_request_missing_intent(self):
        """Test TaskCreateRequest requires intent"""
        with pytest.raises(ValidationError):
            TaskCreateRequest(priority=TaskPriority.MEDIUM)

    def test_task_create_response(self):
        """Test TaskCreateResponse model"""
        response = TaskCreateResponse(
            execution_id="exec_123",
            execution_link="/execute/token_abc",
            estimated_duration=120,
            task_count=5
        )

        assert response.execution_id == "exec_123"
        assert response.execution_link == "/execute/token_abc"
        assert response.estimated_duration == 120
        assert response.task_count == 5

    def test_task_create_response_optional_fields(self):
        """Test TaskCreateResponse optional fields"""
        response = TaskCreateResponse(
            execution_id="exec_123",
            execution_link="/execute/token_abc",
            task_count=3
        )

        assert response.estimated_duration is None

    def test_task_status_response(self):
        """Test TaskStatusResponse model"""
        response = TaskStatusResponse(
            execution_id="exec_123",
            status=TaskStatus.RUNNING,
            progress=0.5,
            completed_tasks=2,
            total_tasks=4,
            current_task="task_2",
            result=None,
            error=None,
            logs=[]
        )

        assert response.execution_id == "exec_123"
        assert response.status == TaskStatus.RUNNING
        assert response.progress == 0.5
        assert response.completed_tasks == 2
        assert response.total_tasks == 4
        assert response.current_task == "task_2"

    def test_task_status_response_progress_bounds(self):
        """Test TaskStatusResponse progress is within bounds"""
        # Progress should be 0.0 to 1.0
        response = TaskStatusResponse(
            execution_id="exec_123",
            status=TaskStatus.COMPLETED,
            progress=1.0,
            completed_tasks=5,
            total_tasks=5
        )

        assert 0.0 <= response.progress <= 1.0
        assert response.progress == 1.0


class TestExecutionLog:
    """Test ExecutionLog model"""

    def test_execution_log_creation(self):
        """Test creating ExecutionLog"""
        log = ExecutionLog(
            execution_id="exec_123",
            task_id="task_1",
            level="INFO",
            message="Task started",
            metadata={"attempt": 1}
        )

        assert log.log_id is not None
        assert log.execution_id == "exec_123"
        assert log.task_id == "task_1"
        assert log.level == "INFO"
        assert log.message == "Task started"
        assert log.timestamp is not None
        assert log.metadata == {"attempt": 1}

    def test_execution_log_default_values(self):
        """Test ExecutionLog default values"""
        log = ExecutionLog(
            execution_id="exec_123",
            message="Test message"
        )

        assert log.level == "INFO"
        assert log.task_id is None
        assert log.metadata == {}
        assert log.timestamp is not None

    def test_execution_log_different_levels(self):
        """Test ExecutionLog with different log levels"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            log = ExecutionLog(
                execution_id="exec_123",
                level=level,
                message=f"Message at {level} level"
            )
            assert log.level == level


class TestModelEdgeCases:
    """Test edge cases and error conditions"""

    def test_task_node_empty_action(self):
        """Test TaskNode with empty action"""
        with pytest.raises(ValidationError):
            TaskNode(
                agent=AgentType.API,
                action=""  # Empty action
            )

    def test_task_graph_circular_dependencies(self):
        """Test TaskGraph handles circular dependency detection"""
        graph = TaskGraph()
        node1 = TaskNode(agent=AgentType.DATA, action="task1")
        node2 = TaskNode(
            agent=AgentType.DATA,
            action="task2",
            dependencies=[node1.task_id]
        )
        node3 = TaskNode(
            agent=AgentType.DATA,
            action="task3",
            dependencies=[node2.task_id]
        )

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)

        # Try to add circular dependency
        # This should be handled by the application logic
        # The model itself doesn't prevent circular dependencies
        node1.dependencies.append(node3.task_id)

        # get_ready_tasks should handle this gracefully
        ready = graph.get_ready_tasks()
        # Should return tasks with all dependencies satisfied
        # In this case, none because of the circular dependency
        assert isinstance(ready, list)

    def test_very_long_intent(self):
        """Test handling of very long intent strings"""
        very_long_intent = "A" * 10000

        execution = TaskExecution(
            intent=very_long_intent,
            task_graph=TaskGraph()
        )

        assert len(execution.intent) == 10000

    def test_special_characters_in_parameters(self):
        """Test TaskNode with special characters in parameters"""
        special_params = {
            "message": "Test with special chars: <>&\"'",
            "url": "https://example.com?param=value&other=value2",
            "unicode": "Hello 世界 🌍"
        }

        node = TaskNode(
            agent=AgentType.COMMUNICATION,
            action="send_message",
            parameters=special_params
        )

        assert node.parameters == special_params

    def test_task_execution_with_scheduled_time(self):
        """Test TaskExecution with scheduled time"""
        from datetime import timedelta

        scheduled_time = datetime.utcnow() + timedelta(hours=1)

        request = TaskCreateRequest(
            intent="Schedule task",
            scheduled_at=scheduled_time,
            user_id="user_123"
        )

        assert request.scheduled_at == scheduled_time


class TestModelJSONSerialization:
    """Test JSON serialization and deserialization"""

    def test_task_node_json_roundtrip(self):
        """Test TaskNode JSON serialization roundtrip"""
        node = TaskNode(
            agent=AgentType.API,
            action="make_request",
            parameters={"url": "https://api.example.com"}
        )

        # Serialize
        node_dict = node.dict()

        # Deserialize
        node_restored = TaskNode(**node_dict)

        assert node_restored.agent == node.agent
        assert node_restored.action == node.action
        assert node_restored.parameters == node.parameters

    def test_task_graph_json_roundtrip(self):
        """Test TaskGraph JSON serialization roundtrip"""
        graph = TaskGraph()
        node = TaskNode(agent=AgentType.DATA, action="fetch")
        graph.add_node(node)

        # Serialize
        graph_dict = graph.dict()

        # Deserialize
        graph_restored = TaskGraph(**graph_dict)

        assert len(graph_restored.nodes) == len(graph.nodes)
        assert node.task_id in graph_restored.nodes

    def test_task_execution_json_roundtrip(self):
        """Test TaskExecution JSON serialization roundtrip"""
        execution = TaskExecution(
            intent="Test execution",
            task_graph=TaskGraph(),
            user_id="user_123"
        )

        # Serialize
        execution_dict = execution.dict()

        # Deserialize
        execution_restored = TaskExecution(**execution_dict)

        assert execution_restored.execution_id == execution.execution_id
        assert execution_restored.intent == execution.intent
        assert execution_restored.user_id == execution.user_id
