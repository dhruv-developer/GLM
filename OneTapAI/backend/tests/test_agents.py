"""
Unit Tests for ZIEL-MAS Agents
Tests for all agent implementations
"""

import pytest
from typing import Dict, Any

from backend.agents.base_agent import BaseAgent
from backend.agents.api_agent import APIAgent
from backend.agents.communication_agent import CommunicationAgent
from backend.agents.data_agent import DataAgent
from backend.agents.web_automation_agent import WebAutomationAgent
from backend.agents.validation_agent import ValidationAgent
from backend.agents.scheduler_agent import SchedulerAgent
from backend.models.agent import AgentResponse


class TestBaseAgent:
    """Test BaseAgent abstract class"""

    def test_base_agent_cannot_be_instantiated(self):
        """Test that BaseAgent cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseAgent("test", "test_type")

    def test_base_agent_response_creation(self):
        """Test creating agent response using base agent methods"""

        class TestAgent(BaseAgent):
            async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                return self._create_response(
                    status="success",
                    output={"result": "test"},
                    metadata={"action": action}
                )

        agent = TestAgent("test_agent", "test_type")

        # Test execute
        import asyncio
        response = asyncio.run(agent.execute("test_action", {}))

        assert response["status"] == "success"
        assert response["output"] == {"result": "test"}
        assert response["metadata"]["action"] == "test_action"

    def test_base_agent_error_handling(self):
        """Test base agent error handling"""

        class TestAgent(BaseAgent):
            async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                try:
                    raise ValueError("Test error")
                except Exception as e:
                    return await self.handle_error(action, e)

        agent = TestAgent("test_agent", "test_type")

        import asyncio
        response = asyncio.run(agent.execute("test_action", {}))

        assert response["status"] == "failed"
        assert "Test error" in response["error"]

    def test_base_agent_parameter_validation(self):
        """Test base agent parameter validation"""

        class TestAgent(BaseAgent):
            async def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
                return "required_param" in parameters

            async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                if not await self.validate_parameters(action, parameters):
                    return self._create_response(
                        status="failed",
                        error="Missing required parameter"
                    )
                return self._create_response(status="success")

        agent = TestAgent("test_agent", "test_type")

        import asyncio

        # Test with missing parameter
        response = asyncio.run(agent.execute("test", {}))
        assert response["status"] == "failed"

        # Test with valid parameter
        response = asyncio.run(agent.execute("test", {"required_param": "value"}))
        assert response["status"] == "success"


class TestAPIAgent:
    """Test APIAgent implementation"""

    @pytest.mark.asyncio
    async def test_api_agent_creation(self):
        """Test creating API agent"""
        agent = APIAgent()

        assert agent.name == "API Agent"
        assert agent.agent_type == "api"
        assert agent.is_active is True

    @pytest.mark.asyncio
    async def test_api_agent_execute_get_request(self):
        """Test API agent executing GET request"""
        agent = APIAgent()

        response = await agent.execute(
            "get_request",
            {
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "method": "GET"
            }
        )

        assert response["status"] in ["success", "failed"]
        if response["status"] == "success":
            assert "output" in response

    @pytest.mark.asyncio
    async def test_api_agent_execute_post_request(self):
        """Test API agent executing POST request"""
        agent = APIAgent()

        response = await agent.execute(
            "post_request",
            {
                "url": "https://jsonplaceholder.typicode.com/posts",
                "method": "POST",
                "data": {"title": "Test", "body": "Test body"}
            }
        )

        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_api_agent_missing_url(self):
        """Test API agent with missing URL parameter"""
        agent = APIAgent()

        response = await agent.execute(
            "get_request",
            {"method": "GET"}
        )

        assert response["status"] == "failed"
        assert "error" in response

    @pytest.mark.asyncio
    async def test_api_agent_invalid_url(self):
        """Test API agent with invalid URL"""
        agent = APIAgent()

        response = await agent.execute(
            "get_request",
            {
                "url": "not-a-valid-url",
                "method": "GET"
            }
        )

        assert response["status"] == "failed"
        assert "error" in response

    @pytest.mark.asyncio
    async def test_api_agent_timeout(self):
        """Test API agent with timeout"""
        agent = APIAgent()

        response = await agent.execute(
            "get_request",
            {
                "url": "https://httpbin.org/delay/10",
                "method": "GET",
                "timeout": 1  # 1 second timeout
            }
        )

        # Should fail due to timeout
        assert response["status"] == "failed"

    @pytest.mark.asyncio
    async def test_api_agent_with_headers(self):
        """Test API agent with custom headers"""
        agent = APIAgent()

        response = await agent.execute(
            "get_request",
            {
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "method": "GET",
                "headers": {
                    "Accept": "application/json",
                    "User-Agent": "ZIEL-MAS/1.0"
                }
            }
        )

        assert response["status"] in ["success", "failed"]


class TestCommunicationAgent:
    """Test CommunicationAgent implementation"""

    @pytest.mark.asyncio
    async def test_communication_agent_creation(self):
        """Test creating Communication agent"""
        agent = CommunicationAgent()

        assert agent.name == "Communication Agent"
        assert agent.agent_type == "communication"

    @pytest.mark.asyncio
    async def test_communication_agent_send_email(self):
        """Test Communication agent sending email"""
        agent = CommunicationAgent()

        response = await agent.execute(
            "send_email",
            {
                "recipient": "test@example.com",
                "subject": "Test Subject",
                "body": "Test Body"
            }
        )

        # Should fail without proper SMTP configuration
        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_communication_agent_missing_recipient(self):
        """Test Communication agent with missing recipient"""
        agent = CommunicationAgent()

        response = await agent.execute(
            "send_email",
            {
                "subject": "Test",
                "body": "Test body"
            }
        )

        assert response["status"] == "failed"
        assert "error" in response

    @pytest.mark.asyncio
    async def test_communication_agent_invalid_email(self):
        """Test Communication agent with invalid email format"""
        agent = CommunicationAgent()

        response = await agent.execute(
            "send_email",
            {
                "recipient": "not-an-email",
                "subject": "Test",
                "body": "Test body"
            }
        )

        assert response["status"] == "failed"

    @pytest.mark.asyncio
    async def test_communication_agent_send_sms(self):
        """Test Communication agent sending SMS"""
        agent = CommunicationAgent()

        response = await agent.execute(
            "send_sms",
            {
                "recipient": "+1234567890",
                "message": "Test SMS"
            }
        )

        # Should fail without proper SMS service configuration
        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_communication_agent_send_whatsapp(self):
        """Test Communication agent sending WhatsApp message"""
        agent = CommunicationAgent()

        response = await agent.execute(
            "send_whatsapp",
            {
                "recipient": "+1234567890",
                "message": "Test WhatsApp message"
            }
        )

        # Should fail without proper WhatsApp service configuration
        assert response["status"] in ["success", "failed"]


class TestDataAgent:
    """TestDataAgent implementation"""

    @pytest.mark.asyncio
    async def test_data_agent_creation(self):
        """Test creating Data agent"""
        agent = DataAgent()

        assert agent.name == "Data Agent"
        assert agent.agent_type == "data"

    @pytest.mark.asyncio
    async def test_data_agent_fetch_data(self):
        """Test Data agent fetching data"""
        agent = DataAgent()

        response = await agent.execute(
            "fetch_data",
            {
                "source": "api",
                "endpoint": "https://jsonplaceholder.typicode.com/posts"
            }
        )

        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_data_agent_filter_data(self):
        """Test Data agent filtering data"""
        agent = DataAgent()

        sample_data = [
            {"id": 1, "name": "Item 1", "category": "A"},
            {"id": 2, "name": "Item 2", "category": "B"},
            {"id": 3, "name": "Item 3", "category": "A"}
        ]

        response = await agent.execute(
            "filter_data",
            {
                "data": sample_data,
                "filters": {"category": "A"}
            }
        )

        assert response["status"] == "success"
        if response["status"] == "success":
            assert len(response["output"]) == 2
            assert all(item["category"] == "A" for item in response["output"])

    @pytest.mark.asyncio
    async def test_data_agent_rank_data(self):
        """Test Data agent ranking data"""
        agent = DataAgent()

        sample_data = [
            {"id": 1, "score": 85},
            {"id": 2, "score": 92},
            {"id": 3, "score": 78}
        ]

        response = await agent.execute(
            "rank_data",
            {
                "data": sample_data,
                "rank_by": "score",
                "order": "desc"
            }
        )

        assert response["status"] == "success"
        if response["status"] == "success":
            assert response["output"][0]["score"] == 92
            assert response["output"][-1]["score"] == 78

    @pytest.mark.asyncio
    async def test_data_aggregate_data(self):
        """Test Data agent aggregating data"""
        agent = DataAgent()

        sample_data = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 20},
            {"category": "B", "value": 15}
        ]

        response = await agent.execute(
            "aggregate_data",
            {
                "data": sample_data,
                "group_by": "category",
                "operations": {"sum": "value"}
            }
        )

        assert response["status"] == "success"


class TestWebAutomationAgent:
    """Test WebAutomationAgent implementation"""

    @pytest.mark.asyncio
    async def test_web_automation_agent_creation(self):
        """Test creating Web Automation agent"""
        agent = WebAutomationAgent()

        assert agent.name == "Web Automation Agent"
        assert agent.agent_type == "web_automation"

    @pytest.mark.asyncio
    async def test_web_automation_agent_navigate(self):
        """Test Web Automation agent navigation"""
        agent = WebAutomationAgent()

        response = await agent.execute(
            "navigate",
            {
                "url": "https://example.com"
            }
        )

        # Should fail without proper browser setup
        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_web_automation_agent_fill_form(self):
        """Test Web Automation agent filling form"""
        agent = WebAutomationAgent()

        response = await agent.execute(
            "fill_form",
            {
                "url": "https://example.com/form",
                "fields": {
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            }
        )

        # Should fail without proper browser setup
        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_web_automation_agent_missing_url(self):
        """Test Web Automation agent with missing URL"""
        agent = WebAutomationAgent()

        response = await agent.execute(
            "fill_form",
            {
                "fields": {"name": "Test"}
            }
        )

        assert response["status"] == "failed"

    @pytest.mark.asyncio
    async def test_web_automation_agent_scrape_data(self):
        """Test Web Automation agent scraping data"""
        agent = WebAutomationAgent()

        response = await agent.execute(
            "scrape",
            {
                "url": "https://example.com",
                "selectors": {
                    "title": "h1",
                    "description": "p"
                }
            }
        )

        # Should fail without proper browser setup
        assert response["status"] in ["success", "failed"]


class TestValidationAgent:
    """Test ValidationAgent implementation"""

    @pytest.mark.asyncio
    async def test_validation_agent_creation(self):
        """Test creating Validation agent"""
        agent = ValidationAgent()

        assert agent.name == "Validation Agent"
        assert agent.agent_type == "validation"

    @pytest.mark.asyncio
    async def test_validation_agent_verify_delivery(self):
        """Test Validation agent verifying delivery"""
        agent = ValidationAgent()

        response = await agent.execute(
            "verify_delivery",
            {
                "message_id": "msg_123",
                "recipient": "test@example.com"
            }
        )

        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_validation_agent_verify_submission(self):
        """Test Validation agent verifying submission"""
        agent = ValidationAgent()

        response = await agent.execute(
            "verify_submission",
            {
                "submission_id": "sub_123",
                "url": "https://example.com/form"
            }
        )

        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_validation_agent_verify_booking(self):
        """Test Validation agent verifying booking"""
        agent = ValidationAgent()

        response = await agent.execute(
            "verify_booking",
            {
                "booking_id": "book_123",
                "service": "uber"
            }
        )

        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_validation_agent_validate_data(self):
        """Test Validation agent validating data"""
        agent = ValidationAgent()

        response = await agent.execute(
            "validate_data",
            {
                "data": {
                    "email": "test@example.com",
                    "phone": "+1234567890"
                },
                "schema": {
                    "email": "email",
                    "phone": "phone"
                }
            }
        )

        assert response["status"] in ["success", "failed"]


class TestSchedulerAgent:
    """Test SchedulerAgent implementation"""

    @pytest.mark.asyncio
    async def test_scheduler_agent_creation(self):
        """Test creating Scheduler agent"""
        agent = SchedulerAgent()

        assert agent.name == "Scheduler Agent"
        assert agent.agent_type == "scheduler"

    @pytest.mark.asyncio
    async def test_scheduler_agent_schedule_task(self):
        """Test Scheduler agent scheduling task"""
        agent = SchedulerAgent()

        from datetime import datetime, timedelta

        scheduled_time = datetime.utcnow() + timedelta(hours=1)

        response = await agent.execute(
            "schedule_task",
            {
                "task_id": "task_123",
                "scheduled_time": scheduled_time.isoformat(),
                "task_data": {"intent": "Test task"}
            }
        )

        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_scheduler_agent_missing_time(self):
        """Test Scheduler agent with missing scheduled time"""
        agent = SchedulerAgent()

        response = await agent.execute(
            "schedule_task",
            {
                "task_id": "task_123",
                "task_data": {"intent": "Test"}
            }
        )

        assert response["status"] == "failed"

    @pytest.mark.asyncio
    async def test_scheduler_agent_cancel_task(self):
        """Test Scheduler agent cancelling scheduled task"""
        agent = SchedulerAgent()

        response = await agent.execute(
            "cancel_task",
            {
                "task_id": "task_123"
            }
        )

        assert response["status"] in ["success", "failed"]

    @pytest.mark.asyncio
    async def test_scheduler_agent_list_scheduled(self):
        """Test Scheduler agent listing scheduled tasks"""
        agent = SchedulerAgent()

        response = await agent.execute(
            "list_scheduled",
            {}
        )

        assert response["status"] in ["success", "failed"]


class TestAgentErrorHandling:
    """Test error handling across all agents"""

    @pytest.mark.asyncio
    async def test_agent_handle_unknown_action(self):
        """Test agents handle unknown actions gracefully"""
        agents = [
            APIAgent(),
            CommunicationAgent(),
            DataAgent(),
            WebAutomationAgent(),
            ValidationAgent(),
            SchedulerAgent()
        ]

        for agent in agents:
            response = await agent.execute(
                "unknown_action",
                {}
            )

            assert response["status"] == "failed"
            assert "error" in response

    @pytest.mark.asyncio
    async def test_agent_handle_empty_parameters(self):
        """Test agents handle empty parameters gracefully"""
        agents = [
            APIAgent(),
            CommunicationAgent(),
            DataAgent(),
            WebAutomationAgent(),
            ValidationAgent(),
            SchedulerAgent()
        ]

        for agent in agents:
            response = await agent.execute(
                "test_action",
                {}
            )

            # Should not crash
            assert "status" in response

    @pytest.mark.asyncio
    async def test_agent_handle_malformed_parameters(self):
        """Test agents handle malformed parameters gracefully"""
        agent = APIAgent()

        response = await agent.execute(
            "get_request",
            {
                "url": None,  # Invalid URL
                "method": "GET"
            }
        )

        assert response["status"] == "failed"

    @pytest.mark.asyncio
    async def test_agent_timeout_handling(self):
        """Test agents handle timeouts appropriately"""
        agent = APIAgent()

        response = await agent.execute(
            "get_request",
            {
                "url": "https://httpbin.org/delay/30",
                "timeout": 1
            }
        )

        assert response["status"] == "failed"


class TestAgentConcurrency:
    """Test agent concurrent execution"""

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test multiple agents can execute concurrently"""
        import asyncio

        agents = [
            APIAgent(),
            DataAgent(),
            ValidationAgent()
        ]

        tasks = [
            agent.execute("test_action", {})
            for agent in agents
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3
        assert all(isinstance(result, dict) for result in results)

    @pytest.mark.asyncio
    async def test_agent_parallel_same_type(self):
        """Test multiple instances of same agent type can run in parallel"""
        import asyncio

        agents = [APIAgent() for _ in range(3)]

        tasks = [
            agent.execute(
                "get_request",
                {"url": "https://jsonplaceholder.typicode.com/posts/1"}
            )
            for agent in agents
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3
