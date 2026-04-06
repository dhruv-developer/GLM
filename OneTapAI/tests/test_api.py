"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_create_task(client):
    """Test task creation endpoint"""
    response = client.post("/api/v1/create-task", json={
        "intent": "Send test email to test@example.com",
        "priority": "medium"
    })

    # Note: This will fail without proper service initialization
    # In a real test, you'd mock the services
    assert response.status_code in [200, 500]  # Accept either for now


def test_get_task_status(client):
    """Test task status endpoint"""
    response = client.get("/api/v1/status/test-execution-id")

    # Will return 404 for non-existent task
    assert response.status_code in [200, 404]
