"""
Test Configuration and Fixtures for ZIEL-MAS Backend
Provides shared fixtures and test utilities
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Dict, Any
from datetime import datetime
import mongomock
import redis as redis_sync
from redis import asyncio as redis_async

# Mock services
from backend.services.database import DatabaseService
from backend.services.cache import RedisService
from backend.services.security import SecurityService
from backend.core.controller import ControllerAgent
from backend.core.execution import ExecutionEngine, TaskDispatcher
from backend.models.task import TaskExecution, TaskGraph, TaskNode, TaskStatus, AgentType


# Test configuration
TEST_MONGODB_URI = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017/test_ziel_mas")
TEST_REDIS_URI = os.getenv("TEST_REDIS_URI", "redis://localhost:6379/1")
TEST_JWT_SECRET = "test-jwt-secret-key-for-testing-only"
TEST_ENCRYPTION_KEY = "test-encryption-key-32-bytes-long"
TEST_GLM_API_KEY = os.getenv("TEST_GLM_API_KEY", "test-glm-api-key")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_database():
    """Mock MongoDB database for testing"""
    # Use mongomock for in-memory MongoDB
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.ziel_mas

    # Create collections
    mock_db.task_executions = mock_client["ziel_mas"].task_executions
    mock_db.execution_logs = mock_client["ziel_mas"].execution_logs
    mock_db.agent_states = mock_client["ziel_mas"].agent_states
    mock_db.audit_logs = mock_client["ziel_mas"].audit_logs
    mock_db.users = mock_client["ziel_mas"].users

    yield mock_db

    # Cleanup
    mock_client.drop_database('ziel_mas')


@pytest.fixture
async def mock_redis():
    """Mock Redis for testing"""
    # Try to connect to real Redis, fallback to mock
    try:
        redis_client = await redis_async.from_url(
            TEST_REDIS_URI,
            encoding="utf-8",
            decode_responses=True
        )

        # Test connection
        await redis_client.ping()

        yield redis_client

        # Cleanup
        await redis_client.flushdb()
        await redis_client.close()

    except Exception:
        # If Redis is not available, use a simple in-memory mock
        class MockRedis:
            def __init__(self):
                self._storage = {}
                self._queues = {}
                self._pubsub = {}

            async def set(self, key: str, value: str, ex: int = None):
                self._storage[key] = value

            async def get(self, key: str):
                return self._storage.get(key)

            async def delete(self, *keys):
                for key in keys:
                    if key in self._storage:
                        del self._storage[key]
                return len(keys)

            async def exists(self, key: str):
                return key in self._storage

            async def hset(self, name: str, key: str, value: str):
                if name not in self._storage:
                    self._storage[name] = {}
                self._storage[name][key] = value

            async def hget(self, name: str, key: str):
                if name in self._storage:
                    return self._storage[name].get(key)
                return None

            async def hgetall(self, name: str):
                return self._storage.get(name, {})

            async def incr(self, key: str):
                if key not in self._storage:
                    self._storage[key] = 0
                self._storage[key] = str(int(self._storage[key]) + 1)
                return int(self._storage[key])

            async def expire(self, key: str, seconds: int):
                pass

            async def lpush(self, name: str, *values):
                if name not in self._queues:
                    self._queues[name] = []
                for value in values:
                    self._queues[name].insert(0, value)
                return len(self._queues[name])

            async def rpop(self, name: str):
                if name in self._queues and self._queues[name]:
                    return self._queues[name].pop()
                return None

            async def rpush(self, name: str, *values):
                if name not in self._queues:
                    self._queues[name] = []
                for value in values:
                    self._queues[name].append(value)
                return len(self._queues[name])

            async def lpop(self, name: str):
                if name in self._queues and self._queues[name]:
                    return self._queues[name].pop(0)
                return None

            async def llen(self, name: str):
                return len(self._queues.get(name, []))

            async def publish(self, channel: str, message: Any):
                if channel not in self._pubsub:
                    self._pubsub[channel] = []
                self._pubsub[channel].append(message)

            async def ping(self):
                return True

            async def flushdb(self):
                self._storage.clear()
                self._queues.clear()
                self._pubsub.clear()

            async def close(self):
                pass

            async def info(self):
                return {"connected_clients": 1, "used_memory": "1024"}

        mock_redis_client = MockRedis()
        yield mock_redis_client


@pytest.fixture
def database_service():
    """Create database service with mock database - simplified version"""

    class MockDatabaseService:
        def __init__(self):
            self._task_executions = {}
            self._execution_logs = {}
            self._agent_states = {}
            self._users = {}

        async def connect(self):
            pass

        async def close(self):
            pass

        async def create_task_execution(self, execution_data: Dict[str, Any]) -> str:
            execution_id = execution_data["execution_id"]
            self._task_executions[execution_id] = execution_data
            return execution_id

        async def get_task_execution(self, execution_id: str) -> Dict[str, Any]:
            return self._task_executions.get(execution_id)

        async def update_task_execution(self, execution_id: str, updates: Dict[str, Any]) -> bool:
            if execution_id in self._task_executions:
                self._task_executions[execution_id].update(updates)
                return True
            return False

        async def get_task_by_token(self, token: str) -> Dict[str, Any]:
            for execution in self._task_executions.values():
                if execution.get("execution_token") == token:
                    return execution
            return None

        async def list_user_tasks(self, user_id: str, status: str = None, limit: int = 50, skip: int = 0) -> list:
            tasks = [
                task for task in self._task_executions.values()
                if task.get("user_id") == user_id and (status is None or task.get("status") == status)
            ]
            return tasks[:limit]

        async def delete_task_execution(self, execution_id: str) -> bool:
            if execution_id in self._task_executions:
                del self._task_executions[execution_id]
                return True
            return False

        async def create_execution_log(self, log_data: Dict[str, Any]) -> str:
            log_id = log_data["log_id"]
            if log_data["execution_id"] not in self._execution_logs:
                self._execution_logs[log_data["execution_id"]] = []
            self._execution_logs[log_data["execution_id"]].append(log_data)
            return log_id

        async def get_execution_logs(self, execution_id: str, level: str = None, limit: int = 100) -> list:
            logs = self._execution_logs.get(execution_id, [])
            if level:
                logs = [log for log in logs if log.get("level") == level]
            return logs[-limit:]

        async def delete_old_logs(self, days: int = 30) -> int:
            count = sum(len(logs) for logs in self._execution_logs.values())
            self._execution_logs.clear()
            return count

        async def update_agent_state(self, agent_id: str, state_data: Dict[str, Any]) -> bool:
            self._agent_states[agent_id] = state_data
            return True

        async def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
            return self._agent_states.get(agent_id)

        async def list_agents(self, status: str = None) -> list:
            agents = list(self._agent_states.values())
            if status:
                agents = [agent for agent in agents if agent.get("status") == status]
            return agents

        async def create_user(self, user_data: Dict[str, Any]) -> str:
            user_id = user_data["user_id"]
            self._users[user_id] = user_data
            return user_id

        async def get_user(self, user_id: str) -> Dict[str, Any]:
            return self._users.get(user_id)

        async def get_user_by_email(self, email: str) -> Dict[str, Any]:
            for user in self._users.values():
                if user.get("email") == email:
                    return user
            return None

        async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
            if user_id in self._users:
                self._users[user_id].update(updates)
                return True
            return False

        async def get_statistics(self) -> Dict[str, Any]:
            return {
                "total_tasks": len(self._task_executions),
                "total_logs": sum(len(logs) for logs in self._execution_logs.values()),
                "total_agents": len(self._agent_states),
                "total_users": len(self._users),
                "task_status_distribution": {}
            }

    return MockDatabaseService()


@pytest.fixture
def redis_service():
    """Create Redis service with mock Redis - simplified version"""

    class SimpleMockRedis:
        def __init__(self):
            self._storage = {}
            self._queues = {}

        async def hset(self, name: str, key: str, value: str):
            if name not in self._storage:
                self._storage[name] = {}
            self._storage[name][key] = value

        async def hget(self, name: str, key: str):
            if name in self._storage:
                return self._storage[name].get(key)
            return None

        async def set(self, key: str, value: str, ex: int = None):
            self._storage[key] = value

        async def get(self, key: str):
            return self._storage.get(key)

        async def rpush(self, name: str, *values):
            if name not in self._queues:
                self._queues[name] = []
            for value in values:
                self._queues[name].append(value)
            return len(self._queues[name])

        async def lpop(self, name: str):
            if name in self._queues and self._queues[name]:
                return self._queues[name].pop(0)
            return None

        async def publish(self, channel: str, message: str):
            pass

        async def info(self):
            return {"connected_clients": 1}

    class MockRedisService:
        def __init__(self):
            self.redis = SimpleMockRedis()

        async def connect(self):
            pass

        async def close(self):
            pass

        async def set_task_status(self, execution_id: str, status: str):
            await self.redis.hset(f"task:{execution_id}", "status", status)

        async def get_task_status(self, execution_id: str) -> str:
            return await self.redis.hget(f"task:{execution_id}", "status")

        async def set_task_progress(self, execution_id: str, progress: float):
            await self.redis.hset(f"task:{execution_id}", "progress", str(progress))

        async def get_task_progress(self, execution_id: str) -> float:
            progress = await self.redis.hget(f"task:{execution_id}", "progress")
            return float(progress) if progress else 0.0

        async def set_task_state(self, execution_id: str, state: Dict[str, Any]):
            import json
            await self.redis.set(f"task_state:{execution_id}", json.dumps(state))

        async def get_task_state(self, execution_id: str) -> Dict[str, Any]:
            import json
            state = await self.redis.get(f"task_state:{execution_id}")
            return json.loads(state) if state else {}

        async def store_token(self, token: str, execution_id: str, expiry: int = 3600):
            await self.redis.set(f"token:{token}", execution_id)

        async def get_execution_id_from_token(self, token: str) -> str:
            return await self.redis.get(f"token:{token}")

        async def push_to_queue(self, queue_name: str, value: str):
            await self.redis.rpush(queue_name, value)

        async def pop_from_queue(self, queue_name: str) -> str:
            return await self.redis.lpop(queue_name)

        async def publish(self, channel: str, message: Any):
            import json
            await self.redis.publish(channel, json.dumps(message))

        async def get_info(self) -> Dict[str, Any]:
            return await self.redis.info()

    return MockRedisService()


@pytest.fixture
def security_service():
    """Create security service for testing"""
    return SecurityService(
        jwt_secret=TEST_JWT_SECRET,
        encryption_key=TEST_ENCRYPTION_KEY
    )


@pytest.fixture
def controller_agent():
    """Create controller agent for testing"""
    return ControllerAgent(
        glm_api_key=TEST_GLM_API_KEY,
        glm_api_url="https://api.glm.ai/v1"
    )


@pytest.fixture
def web_search_agent():
    """Create web search agent for testing"""
    from backend.agents.web_search_agent import WebSearchAgent
    return WebSearchAgent()


@pytest.fixture
def execution_engine(redis_service, database_service, controller_agent):
    """Create execution engine for testing"""
    return ExecutionEngine(
        redis_service=redis_service,
        db_service=database_service,
        controller=controller_agent
    )


@pytest.fixture
def sample_task_execution():
    """Create sample task execution for testing"""
    task_graph = TaskGraph()

    task1 = TaskNode(
        agent=AgentType.COMMUNICATION,
        action="send_message",
        parameters={"recipient": "test@example.com", "message": "Test"}
    )
    task_graph.add_node(task1)

    return TaskExecution(
        user_id="test_user_123",
        intent="Send test message",
        task_graph=task_graph,
        priority="medium"
    )


@pytest.fixture
def sample_task_graph():
    """Create sample task graph for testing"""
    graph = TaskGraph()

    # Task 1: Prepare message
    task1 = TaskNode(
        agent=AgentType.CONTROLLER,
        action="prepare_message",
        parameters={"intent": "Test intent"}
    )
    graph.add_node(task1)

    # Task 2: Send message (depends on task1)
    task2 = TaskNode(
        agent=AgentType.COMMUNICATION,
        action="send_message",
        parameters={"recipient": "test@example.com", "message": "Test message body"},
        dependencies=[task1.task_id]
    )
    graph.add_node(task2)

    # Task 3: Validate (depends on task2)
    task3 = TaskNode(
        agent=AgentType.VALIDATION,
        action="verify_delivery",
        parameters={},
        dependencies=[task2.task_id]
    )
    graph.add_node(task3)

    return graph


# Test data fixtures
@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "created_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_task_requests():
    """Sample task requests for testing"""
    return [
        {
            "intent": "Send email to john@example.com with birthday wishes",
            "priority": "medium",
            "user_id": "test_user_123"
        },
        {
            "intent": "Schedule reminder for tomorrow at 9 AM",
            "priority": "high",
            "user_id": "test_user_123"
        },
        {
            "intent": "Find top 10 restaurants near me",
            "priority": "low",
            "user_id": "test_user_123"
        },
        {
            "intent": "Book a cab to airport",
            "priority": "high",
            "user_id": "test_user_456"
        },
        {
            "intent": "Search for the latest Python web framework trends and create a comparison report",
            "priority": "medium",
            "user_id": "test_user_123"
        },
        {
            "intent": "Research Docker containerization best practices and summarize key points",
            "priority": "high",
            "user_id": "test_user_789"
        },
        {
            "intent": "Find recent news about artificial intelligence and identify emerging trends",
            "priority": "low",
            "user_id": "test_user_456"
        }
    ]


@pytest.fixture
def malicious_intents():
    """Malicious intent examples for security testing"""
    return [
        "",  # Empty intent
        "   ",  # Whitespace only
        "A" * 10000,  # Extremely long intent
        "<script>alert('xss')</script>",  # XSS attempt
        "'; DROP TABLE users; --",  # SQL injection attempt
        "../../../etc/passwd",  # Path traversal attempt
        "$(rm -rf /)",  # Command injection attempt
    ]


@pytest.fixture
def sample_task_execution_with_web_search():
    """Create sample task execution with web search for testing"""
    task_graph = TaskGraph()

    # Task 1: Search for information
    search_task = TaskNode(
        agent=AgentType.WEB_SEARCH,
        action="search_web",
        parameters={
            "query": "Python async best practices 2024",
            "max_results": 5
        }
    )
    task_graph.add_node(search_task)

    # Task 2: Process the search results
    process_task = TaskNode(
        agent=AgentType.DATA,
        action="aggregate_data",
        parameters={
            "data_source": "search_results",
            "aggregation_type": "summary"
        },
        dependencies=[search_task.task_id]
    )
    task_graph.add_node(process_task)

    return TaskExecution(
        user_id="test_user_123",
        intent="Research Python async best practices and create a summary",
        task_graph=task_graph,
        priority="medium"
    )


@pytest.fixture
def sample_task_graph_with_web_search():
    """Create sample task graph with web search integration"""
    graph = TaskGraph()

    # Task 1: Web search for latest trends
    search_task = TaskNode(
        agent=AgentType.WEB_SEARCH,
        action="search_web",
        parameters={
            "query": "artificial intelligence trends 2024",
            "max_results": 10
        }
    )
    graph.add_node(search_task)

    # Task 2: Search for technical documentation
    tech_search = TaskNode(
        agent=AgentType.WEB_SEARCH,
        action="search_technical",
        parameters={
            "query": "neural network implementation",
            "tech_stack": "Python",
            "max_results": 5
        }
    )
    graph.add_node(tech_search)

    # Task 3: Aggregate and analyze results (depends on both searches)
    aggregate_task = TaskNode(
        agent=AgentType.DATA,
        action="aggregate_data",
        parameters={
            "data_source": "web_search",
            "analysis_type": "trend_analysis"
        },
        dependencies=[search_task.task_id, tech_search.task_id]
    )
    graph.add_node(aggregate_task)

    # Task 4: Create summary report
    summary_task = TaskNode(
        agent=AgentType.CONTROLLER,
        action="create_summary",
        parameters={
            "format": "detailed_report",
            "include_sources": True
        },
        dependencies=[aggregate_task.task_id]
    )
    graph.add_node(summary_task)

    return graph


@pytest.fixture
def test_task_requests_with_web_search():
    """Sample task requests including web search scenarios"""
    return [
        {
            "intent": "Search for the latest AI news and summarize the key developments",
            "priority": "medium",
            "user_id": "test_user_123"
        },
        {
            "intent": "Find Python FastAPI tutorials and create a learning roadmap",
            "priority": "high",
            "user_id": "test_user_123"
        },
        {
            "intent": "Research top 10 machine learning frameworks and compare their features",
            "priority": "low",
            "user_id": "test_user_456"
        },
        {
            "intent": "Search for recent cybersecurity news and identify emerging threats",
            "priority": "high",
            "user_id": "test_user_789"
        }
    ]


# Async test utilities
@pytest.fixture
def wait_for_condition():
    """Utility to wait for a condition to be true"""
    async def _wait_for_condition(condition_func, timeout=5.0, interval=0.1):
        """Wait for condition to be true or timeout"""
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        return False
    return _wait_for_condition
