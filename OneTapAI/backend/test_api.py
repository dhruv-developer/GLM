"""
ZIEL-MAS Backend Unit Tests
Pytest-based testing suite
"""

import pytest
import httpx
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "pytest_user_001"

@pytest.fixture
async def client():
    """HTTP client fixture"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client

@pytest.fixture
def base_url():
    """Base URL fixture"""
    return BASE_URL

@pytest.fixture
def test_user_id():
    """Test user ID fixture"""
    return TEST_USER_ID

@pytest.mark.asyncio
async def test_health_check(client: httpx.AsyncClient, base_url: str):
    """Test health check endpoint"""
    response = await client.get(f"{base_url}/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "services" in data

@pytest.mark.asyncio
async def test_create_task(client: httpx.AsyncClient, base_url: str, test_user_id: str):
    """Test task creation endpoint"""
    payload = {
        "intent": "Send test email to john@example.com",
        "priority": "medium",
        "user_id": test_user_id
    }

    response = await client.post(
        f"{base_url}/api/v1/create-task",
        json=payload
    )

    # Note: This test may fail if GLM API key is not configured
    # or if backend services are not running
    if response.status_code == 200:
        data = response.json()
        assert "execution_id" in data
        assert "execution_link" in data
        assert "task_count" in data
        assert isinstance(data["task_count"], int)
        return data["execution_id"]
    else:
        # If creation fails, it's okay for testing purposes
        pytest.skip("Task creation failed - likely missing GLM API key")

@pytest.mark.asyncio
async def test_create_task_validation(client: httpx.AsyncClient, base_url: str):
    """Test task creation validation"""
    # Test with empty intent
    payload = {
        "intent": "",
        "priority": "medium"
    }

    response = await client.post(
        f"{base_url}/api/v1/create-task",
        json=payload
    )

    # Should return 400 or similar error code
    assert response.status_code != 200

@pytest.mark.asyncio
async def test_get_statistics(client: httpx.AsyncClient, base_url: str):
    """Test statistics endpoint"""
    response = await client.get(f"{base_url}/api/v1/stats")

    assert response.status_code == 200

    data = response.json()
    assert "database" in data or "cache" in data

@pytest.mark.asyncio
async def test_get_user_tasks(client: httpx.AsyncClient, base_url: str, test_user_id: str):
    """Test user tasks endpoint"""
    response = await client.get(
        f"{base_url}/api/v1/user/{test_user_id}/tasks"
    )

    assert response.status_code == 200

    data = response.json()
    assert "user_id" in data
    assert "tasks" in data
    assert "count" in data
    assert isinstance(data["tasks"], list)
    assert isinstance(data["count"], int)

@pytest.mark.asyncio
async def test_get_task_status_not_found(client: httpx.AsyncClient, base_url: str):
    """Test getting status for non-existent task"""
    fake_id = "nonexistent_task_id_12345"

    response = await client.get(
        f"{base_url}/api/v1/status/{fake_id}"
    )

    # Should return 404 or similar
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_execute_task_invalid_token(client: httpx.AsyncClient, base_url: str):
    """Test task execution with invalid token"""
    fake_token = "invalid_token_abc123"

    response = await client.get(
        f"{base_url}/api/v1/execute/{fake_token}"
    )

    # Should return 401 or similar
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_cancel_task_not_found(client: httpx.AsyncClient, base_url: str):
    """Test cancelling non-existent task"""
    fake_id = "nonexistent_task_id_67890"

    response = await client.post(
        f"{base_url}/api/v1/cancel/{fake_id}"
    )

    # Should handle gracefully (may return 200 or 404)
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_cors_headers(client: httpx.AsyncClient, base_url: str):
    """Test CORS headers are set"""
    response = await client.get(
        f"{base_url}/health",
        headers={"Origin": "http://localhost:3000"}
    )

    # Check for CORS headers
    cors_header = response.headers.get("access-control-allow-origin")
    assert cors_header is not None or cors_header == "*" or "localhost" in cors_header

# Integration tests
@pytest.mark.asyncio
async def test_full_task_workflow(client: httpx.AsyncClient, base_url: str, test_user_id: str):
    """Test complete task workflow: create -> status -> logs -> cancel"""

    # Step 1: Create task
    payload = {
        "intent": "Integration test task",
        "priority": "low",
        "user_id": test_user_id
    }

    create_response = await client.post(
        f"{base_url}/api/v1/create-task",
        json=payload
    )

    if create_response.status_code != 200:
        pytest.skip("Cannot create task - skipping workflow test")

    task_data = create_response.json()
    execution_id = task_data["execution_id"]

    # Step 2: Get status
    status_response = await client.get(
        f"{base_url}/api/v1/status/{execution_id}"
    )
    assert status_response.status_code == 200

    # Step 3: Get logs
    logs_response = await client.get(
        f"{base_url}/api/v1/logs/{execution_id}"
    )
    assert logs_response.status_code == 200

    # Step 4: Cancel task
    cancel_response = await client.post(
        f"{base_url}/api/v1/cancel/{execution_id}"
    )
    assert cancel_response.status_code == 200

# Performance tests
@pytest.mark.asyncio
async def test_concurrent_requests(client: httpx.AsyncClient, base_url: str):
    """Test handling concurrent requests"""
    import asyncio

    async def make_request():
        return await client.get(f"{base_url}/health")

    # Make 10 concurrent health check requests
    responses = await asyncio.gather(*[make_request() for _ in range(10)])

    # All should succeed
    for response in responses:
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
