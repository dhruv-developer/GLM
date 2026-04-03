"""
Tests for Worker Agents
"""

import pytest
from backend.agents.api_agent import APIAgent
from backend.agents.communication_agent import CommunicationAgent
from backend.agents.data_agent import DataAgent


@pytest.mark.asyncio
async def test_api_agent():
    """Test API agent execution"""
    agent = APIAgent()

    # Test with mock data
    result = await agent.execute("http_get", {
        "url": "https://api.github.com/zen"
    })

    assert result is not None
    assert result["status"] in ["completed", "failed"]
    assert "agent" in result


@pytest.mark.asyncio
async def test_communication_agent():
    """Test communication agent"""
    agent = CommunicationAgent()

    result = await agent.execute("send_message", {
        "recipient": "test@example.com",
        "message": "Test message"
    })

    assert result is not None
    assert "status" in result


@pytest.mark.asyncio
async def test_data_agent():
    """Test data agent"""
    agent = DataAgent()

    result = await agent.execute("filter_data", {
        "data": [
            {"name": "Item 1", "value": 10},
            {"name": "Item 2", "value": 20},
            {"name": "Item 3", "value": 5}
        ],
        "filters": {"value": {"$gt": 8}}
    })

    assert result is not None
    assert result["status"] == "completed"
    assert len(result["output"]["data"]) == 2
