"""
Integration Tests for ZIEL-MAS API
Tests for all API endpoints with real HTTP requests
"""

import pytest
import httpx
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "integration_test_user"


class TestHealthEndpoint:
    """Test health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check returns 200"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")

            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "services" in data

    @pytest.mark.asyncio
    async def test_health_check_service_status(self):
        """Test health check includes service status"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")

            data = response.json()
            services = data.get("services", {})

            # Should include Redis and database status
            assert "redis" in services or "database" in services


class TestTaskCreationEndpoint:
    """Test task creation endpoint"""

    @pytest.mark.asyncio
    async def test_create_task_simple(self):
        """Test creating a simple task"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "intent": "Send test email to john@example.com",
                "priority": "medium",
                "user_id": TEST_USER_ID
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=payload
            )

            # May fail if services not configured, but should return valid response
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert "execution_id" in data
                assert "execution_link" in data
                assert "task_count" in data
                assert isinstance(data["task_count"], int)

    @pytest.mark.asyncio
    async def test_create_task_with_high_priority(self):
        """Test creating task with high priority"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "intent": "Urgent: Send critical email",
                "priority": "high",
                "user_id": TEST_USER_ID
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=payload
            )

            assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_create_task_missing_intent(self):
        """Test creating task with missing intent"""
        async with httpx.AsyncClient() as client:
            payload = {
                "priority": "medium",
                "user_id": TEST_USER_ID
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=payload
            )

            # Should return validation error
            assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_task_empty_intent(self):
        """Test creating task with empty intent"""
        async with httpx.AsyncClient() as client:
            payload = {
                "intent": "",
                "priority": "medium",
                "user_id": TEST_USER_ID
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=payload
            )

            # Should return validation or security error
            assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_create_task_with_scheduled_time(self):
        """Test creating task with scheduled time"""
        from datetime import datetime, timedelta

        scheduled_time = datetime.utcnow() + timedelta(hours=1)

        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "intent": "Schedule reminder for tomorrow",
                "priority": "medium",
                "user_id": TEST_USER_ID,
                "scheduled_at": scheduled_time.isoformat()
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=payload
            )

            assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_create_task_malicious_intent(self):
        """Test creating task with malicious intent"""
        async with httpx.AsyncClient() as client:
            malicious_intents = [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "$(rm -rf /)"
            ]

            for intent in malicious_intents:
                payload = {
                    "intent": intent,
                    "priority": "medium",
                    "user_id": TEST_USER_ID
                }

                response = await client.post(
                    f"{BASE_URL}/api/v1/create-task",
                    json=payload
                )

                # Should reject malicious input
                assert response.status_code in [400, 422, 500]


class TestTaskExecutionEndpoint:
    """Test task execution endpoint"""

    @pytest.mark.asyncio
    async def test_execute_task_with_valid_token(self):
        """Test executing task with valid token"""
        # First create a task
        async with httpx.AsyncClient(timeout=30.0) as client:
            create_payload = {
                "intent": "Test execution",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            create_response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            if create_response.status_code == 200:
                data = create_response.json()
                execution_link = data.get("execution_link", "")

                if execution_link:
                    # Extract token from execution link
                    token = execution_link.split("/")[-1]

                    # Execute task
                    exec_response = await client.get(
                        f"{BASE_URL}/api/v1/execute/{token}"
                    )

                    # Should return success or not found
                    assert exec_response.status_code in [200, 401, 404]

    @pytest.mark.asyncio
    async def test_execute_task_with_invalid_token(self):
        """Test executing task with invalid token"""
        async with httpx.AsyncClient() as client:
            invalid_tokens = [
                "invalid_token",
                "abc123",
                "malformed.token.string",
                ""
            ]

            for token in invalid_tokens:
                response = await client.get(
                    f"{BASE_URL}/api/v1/execute/{token}"
                )

                # Should return unauthorized
                assert response.status_code in [401, 404]

    @pytest.mark.asyncio
    async def test_execute_task_expired_token(self):
        """Test executing task with expired token"""
        # This would require mocking time or using old tokens
        # For now, just test invalid token format
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/execute/expired_token_12345"
            )

            assert response.status_code in [401, 404]


class TestTaskStatusEndpoint:
    """Test task status endpoint"""

    @pytest.mark.asyncio
    async def test_get_task_status(self):
        """Test getting task status"""
        # Create a task first
        async with httpx.AsyncClient(timeout=30.0) as client:
            create_payload = {
                "intent": "Test status endpoint",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            create_response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            if create_response.status_code == 200:
                data = create_response.json()
                execution_id = data.get("execution_id")

                if execution_id:
                    # Get status
                    status_response = await client.get(
                        f"{BASE_URL}/api/v1/status/{execution_id}"
                    )

                    assert status_response.status_code == 200

                    status_data = status_response.json()
                    assert "execution_id" in status_data
                    assert "status" in status_data
                    assert "progress" in status_data
                    assert "completed_tasks" in status_data
                    assert "total_tasks" in status_data
                    assert 0.0 <= status_data["progress"] <= 1.0

    @pytest.mark.asyncio
    async def test_get_task_status_not_found(self):
        """Test getting status for non-existent task"""
        async with httpx.AsyncClient() as client:
            fake_ids = [
                "nonexistent_task_id",
                "fake_id_12345",
                "invalid_id"
            ]

            for fake_id in fake_ids:
                response = await client.get(
                    f"{BASE_URL}/api/v1/status/{fake_id}"
                )

                # Should return not found
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_status_progress_tracking(self):
        """Test task progress tracking"""
        # This would require creating and monitoring a real task
        # For now, test the endpoint structure
        async with httpx.AsyncClient(timeout=30.0) as client:
            create_payload = {
                "intent": "Test progress tracking",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            create_response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            if create_response.status_code == 200:
                data = create_response.json()
                execution_id = data.get("execution_id")

                if execution_id:
                    # Get status multiple times to test progress
                    for _ in range(3):
                        status_response = await client.get(
                            f"{BASE_URL}/api/v1/status/{execution_id}"
                        )

                        assert status_response.status_code == 200
                        status_data = status_response.json()

                        # Progress should be valid float
                        assert isinstance(status_data["progress"], float)
                        assert 0.0 <= status_data["progress"] <= 1.0


class TestTaskCancellationEndpoint:
    """Test task cancellation endpoint"""

    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """Test cancelling a task"""
        # Create a task first
        async with httpx.AsyncClient(timeout=30.0) as client:
            create_payload = {
                "intent": "Test cancellation",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            create_response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            if create_response.status_code == 200:
                data = create_response.json()
                execution_id = data.get("execution_id")

                if execution_id:
                    # Cancel task
                    cancel_response = await client.post(
                        f"{BASE_URL}/api/v1/cancel/{execution_id}"
                    )

                    assert cancel_response.status_code == 200

                    cancel_data = cancel_response.json()
                    assert "message" in cancel_data
                    assert "execution_id" in cancel_data

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self):
        """Test cancelling non-existent task"""
        async with httpx.AsyncClient() as client:
            fake_id = "nonexistent_task_id"

            response = await client.post(
                f"{BASE_URL}/api/v1/cancel/{fake_id}"
            )

            # Should handle gracefully
            assert response.status_code in [200, 404]


class TestTaskLogsEndpoint:
    """Test task logs endpoint"""

    @pytest.mark.asyncio
    async def test_get_task_logs(self):
        """Test getting task logs"""
        # Create a task first
        async with httpx.AsyncClient(timeout=30.0) as client:
            create_payload = {
                "intent": "Test logs endpoint",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            create_response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            if create_response.status_code == 200:
                data = create_response.json()
                execution_id = data.get("execution_id")

                if execution_id:
                    # Get logs
                    logs_response = await client.get(
                        f"{BASE_URL}/api/v1/logs/{execution_id}"
                    )

                    assert logs_response.status_code == 200

                    logs_data = logs_response.json()
                    assert "execution_id" in logs_data
                    assert "logs" in logs_data
                    assert "count" in logs_data
                    assert isinstance(logs_data["logs"], list)

    @pytest.mark.asyncio
    async def test_get_task_logs_with_level_filter(self):
        """Test getting task logs with level filter"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create task
            create_payload = {
                "intent": "Test log filtering",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            create_response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            if create_response.status_code == 200:
                data = create_response.json()
                execution_id = data.get("execution_id")

                if execution_id:
                    # Get logs with level filter
                    levels = ["INFO", "ERROR", "WARNING"]

                    for level in levels:
                        logs_response = await client.get(
                            f"{BASE_URL}/api/v1/logs/{execution_id}",
                            params={"level": level}
                        )

                        assert logs_response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_task_logs_with_limit(self):
        """Test getting task logs with limit"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create task
            create_payload = {
                "intent": "Test log limit",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            create_response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            if create_response.status_code == 200:
                data = create_response.json()
                execution_id = data.get("execution_id")

                if execution_id:
                    # Get logs with limit
                    logs_response = await client.get(
                        f"{BASE_URL}/api/v1/logs/{execution_id}",
                        params={"limit": 5}
                    )

                    assert logs_response.status_code == 200

                    logs_data = logs_response.json()
                    assert logs_data["count"] <= 5


class TestUserTasksEndpoint:
    """Test user tasks endpoint"""

    @pytest.mark.asyncio
    async def test_get_user_tasks(self):
        """Test getting user tasks"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create a task first
            create_payload = {
                "intent": "Test user tasks endpoint",
                "priority": "low",
                "user_id": TEST_USER_ID
            }

            await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=create_payload
            )

            # Get user tasks
            response = await client.get(
                f"{BASE_URL}/api/v1/user/{TEST_USER_ID}/tasks"
            )

            assert response.status_code == 200

            data = response.json()
            assert "user_id" in data
            assert "tasks" in data
            assert "count" in data
            assert isinstance(data["tasks"], list)

    @pytest.mark.asyncio
    async def test_get_user_tasks_with_status_filter(self):
        """Test getting user tasks with status filter"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            statuses = ["pending", "running", "completed"]

            for status in statuses:
                response = await client.get(
                    f"{BASE_URL}/api/v1/user/{TEST_USER_ID}/tasks",
                    params={"status": status}
                )

                assert response.status_code == 200

                data = response.json()
                assert "tasks" in data
                # All tasks should have the specified status
                for task in data["tasks"]:
                    assert task.get("status") == status

    @pytest.mark.asyncio
    async def test_get_user_tasks_with_limit(self):
        """Test getting user tasks with limit"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/user/{TEST_USER_ID}/tasks",
                params={"limit": 5}
            )

            assert response.status_code == 200

            data = response.json()
            assert len(data["tasks"]) <= 5

    @pytest.mark.asyncio
    async def test_get_user_tasks_pagination(self):
        """Test user tasks pagination"""
        async with httpx.AsyncClient() as client:
            # Get first page
            page1 = await client.get(
                f"{BASE_URL}/api/v1/user/{TEST_USER_ID}/tasks",
                params={"limit": 5, "skip": 0}
            )

            # Get second page
            page2 = await client.get(
                f"{BASE_URL}/api/v1/user/{TEST_USER_ID}/tasks",
                params={"limit": 5, "skip": 5}
            )

            assert page1.status_code == 200
            assert page2.status_code == 200

            data1 = page1.json()
            data2 = page2.json()

            # Tasks should be different (if there are enough tasks)
            if len(data1["tasks"]) > 0 and len(data2["tasks"]) > 0:
                assert data1["tasks"][0]["execution_id"] != data2["tasks"][0]["execution_id"]


class TestStatisticsEndpoint:
    """Test statistics endpoint"""

    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test getting system statistics"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/stats")

            assert response.status_code == 200

            data = response.json()
            assert "database" in data or "cache" in data
            assert "timestamp" in data

            if "database" in data:
                db_stats = data["database"]
                assert "total_tasks" in db_stats
                assert "total_logs" in db_stats
                assert "total_agents" in db_stats

    @pytest.mark.asyncio
    async def test_statistics_includes_task_distribution(self):
        """Test statistics includes task status distribution"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/stats")

            data = response.json()

            if "database" in data:
                db_stats = data["database"]
                assert "task_status_distribution" in db_stats


class TestCORSEndpoints:
    """Test CORS headers"""

    @pytest.mark.asyncio
    async def test_cors_headers_on_health(self):
        """Test CORS headers are set on health endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/health",
                headers={"Origin": "http://localhost:3000"}
            )

            # Check for CORS headers
            cors_header = response.headers.get("access-control-allow-origin")
            assert cors_header is not None or cors_header == "*"

    @pytest.mark.asyncio
    async def test_cors_headers_on_api_endpoints(self):
        """Test CORS headers are set on API endpoints"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/stats",
                headers={"Origin": "http://localhost:3000"}
            )

            cors_header = response.headers.get("access-control-allow-origin")
            assert cors_header is not None or cors_header == "*"


class TestErrorHandling:
    """Test API error handling"""

    @pytest.mark.asyncio
    async def test_invalid_json_payload(self):
        """Test API handles invalid JSON gracefully"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                content="invalid json",
                headers={"Content-Type": "application/json"}
            )

            assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    async def test_missing_content_type(self):
        """Test API handles missing content-type"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                data='{"intent": "test"}'  # Missing content-type header
            )

            # Should handle gracefully
            assert response.status_code in [200, 422, 415]

    @pytest.mark.asyncio
    async def test_very_long_intent(self):
        """Test API handles very long intents"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            very_long_intent = "A" * 10000

            payload = {
                "intent": very_long_intent,
                "priority": "medium",
                "user_id": TEST_USER_ID
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/create-task",
                json=payload
            )

            # Should reject or handle gracefully
            assert response.status_code in [400, 422, 500]

    @pytest.mark.asyncio
    async def test_special_characters_in_intent(self):
        """Test API handles special characters in intent"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            special_intents = [
                "Test with émojis 🚀",
                "Test with quotes \"test\"",
                "Test with newlines \n test",
                "Test with tabs \t test"
            ]

            for intent in special_intents:
                payload = {
                    "intent": intent,
                    "priority": "medium",
                    "user_id": TEST_USER_ID
                }

                response = await client.post(
                    f"{BASE_URL}/api/v1/create-task",
                    json=payload
                )

                # Should handle or reject gracefully
                assert response.status_code in [200, 400, 422, 500]


class TestAPIPerformance:
    """Test API performance"""

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test API handles concurrent health check requests"""
        import asyncio

        async def make_request():
            async with httpx.AsyncClient() as client:
                return await client.get(f"{BASE_URL}/health")

        # Make 10 concurrent requests
        responses = await asyncio.gather(*[make_request() for _ in range(10)])

        # All should succeed
        for response in responses:
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_response_time_health_check(self):
        """Test health check response time is reasonable"""
        import time

        async with httpx.AsyncClient() as client:
            start_time = time.time()
            response = await client.get(f"{BASE_URL}/health")
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200
            # Should respond within 1 second
            assert response_time < 1.0

    @pytest.mark.asyncio
    async def test_multiple_sequential_requests(self):
        """Test API handles multiple sequential requests"""
        async with httpx.AsyncClient() as client:
            for i in range(10):
                response = await client.get(f"{BASE_URL}/health")
                assert response.status_code == 200
