"""
Tests for Controller Agent
"""

import pytest
import asyncio
from backend.core.controller import ControllerAgent
from backend.models.task import TaskStatus, AgentType


@pytest.mark.asyncio
async def test_parse_intent():
    """Test intent parsing"""
    controller = ControllerAgent(
        glm_api_key="33d3ae7a00b546b086be648f9491f8b5.NrDQpTb0etb17xhK",
        glm_api_url="https://test.api.com"
    )

    intent = "Send birthday message to mom at 12 AM"
    parsed = await controller.parse_intent(intent)

    assert parsed is not None
    assert parsed["task_type"] == "communication" or parsed["task_type"] == "scheduling"
    assert "entities" in parsed
    assert "time_info" in parsed


@pytest.mark.asyncio
async def test_generate_task_graph():
    """Test task graph generation"""
    controller = ControllerAgent(
        glm_api_key="test_key",
        glm_api_url="https://test.api.com"
    )

    parsed_intent = {
        "task_type": "communication",
        "entities": {"emails": ["test@example.com"]},
        "time_info": {},
        "priority": "medium",
        "original_intent": "Send email to test@example.com"
    }

    graph = await controller.generate_task_graph(parsed_intent)

    assert graph is not None
    assert len(graph.nodes) > 0
    assert graph.is_complete() == False


@pytest.mark.asyncio
async def test_re_plan():
    """Test re-planning logic"""
    controller = ControllerAgent(
        glm_api_key="test_key",
        glm_api_url="https://test.api.com"
    )

    # Create a simple graph
    from backend.models.task import TaskGraph, TaskNode

    graph = TaskGraph()
    task = TaskNode(
        agent=AgentType.API,
        action="test_action",
        parameters={"test": "value"}
    )
    graph.add_node(task)

    # Re-plan for failed task
    new_graph = await controller.re_plan(graph, task.task_id, "Test error")

    assert new_graph is not None
