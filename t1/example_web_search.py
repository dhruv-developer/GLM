"""
Example: Using the Web Search Agent in a Complete Workflow
Demonstrates how to use the new web search capabilities
"""

import asyncio
import sys
sys.path.insert(0, '/Users/druvdawar11/Desktop/Projects/GLM-Hack/t1')

from backend.core.execution import ExecutionEngine
from backend.models.task import TaskGraph, TaskNode, TaskExecution, AgentType
from backend.services.database import DatabaseService
from backend.services.cache import RedisService
from backend.services.security import SecurityService
from backend.core.controller import ControllerAgent
from backend.agents.web_search_agent import WebSearchAgent


class SimpleDatabase:
    """Simple in-memory database for testing"""
    def __init__(self):
        self.tasks = {}
        self.logs = []

    async def connect(self):
        pass

    async def close(self):
        pass

    async def create_task_execution(self, execution_data):
        execution_id = execution_data["execution_id"]
        self.tasks[execution_id] = execution_data
        return execution_id

    async def update_task_execution(self, execution_id, updates):
        if execution_id in self.tasks:
            self.tasks[execution_id].update(updates)
            return True
        return False

    async def get_task_execution(self, execution_id):
        return self.tasks.get(execution_id)

    async def create_execution_log(self, log_data):
        log_id = log_data["log_id"]
        self.logs.append(log_data)
        return log_id

    async def get_execution_logs(self, execution_id, level=None, limit=100):
        return self.logs[-limit:]

    async def get_task_by_token(self, token):
        for task in self.tasks.values():
            if task.get("execution_token") == token:
                return task
        return None

    async def update_agent_state(self, agent_id, state_data):
        return True

    async def get_agent_state(self, agent_id):
        return {}

    async def list_agents(self, status=None):
        return []

    async def create_user(self, user_data):
        return user_data["user_id"]

    async def get_user(self, user_id):
        return None

    async def get_user_by_email(self, email):
        return None

    async def update_user(self, user_id, updates):
        return False

    async def list_user_tasks(self, user_id, status=None, limit=50, skip=0):
        return []

    async def delete_task_execution(self, execution_id):
        if execution_id in self.tasks:
            del self.tasks[execution_id]
            return True
        return False

    async def get_statistics(self):
        return {"total_tasks": len(self.tasks)}


class SimpleRedis:
    """Simple in-memory Redis for testing"""
    def __init__(self):
        self.data = {}

    async def connect(self):
        pass

    async def close(self):
        pass

    async def set_task_status(self, execution_id, status):
        pass

    async def get_task_status(self, execution_id):
        return "pending"

    async def set_task_progress(self, execution_id, progress):
        pass

    async def get_task_progress(self, execution_id):
        return 0.0

    async def set_task_state(self, execution_id, state):
        pass

    async def get_task_state(self, execution_id):
        return {}

    async def store_token(self, token, execution_id, expiry=3600):
        pass

    async def get_execution_id_from_token(self, token):
        return None

    async def push_to_queue(self, queue_name, value):
        pass

    async def pop_from_queue(self, queue_name):
        return None

    async def publish(self, channel, message):
        pass

    async def get_info(self):
        return {}


async def test_web_search_workflow():
    """Test a complete workflow using web search"""
    print("🔍 Testing Web Search Workflow")
    print("=" * 60)

    # Initialize services
    db = SimpleDatabase()
    redis = SimpleRedis()
    security = SecurityService("test-jwt-secret-key-for-testing-development-environment-32chars", "test-encryption-key-32-bytes-long")
    controller = ControllerAgent(glm_api_key="test", glm_api_url="https://api.glm.ai/v1")

    # Create execution engine with web search agent
    from backend.core.execution import ExecutionEngine

    execution_engine = ExecutionEngine(
        redis_service=redis,
        db_service=db,
        controller=controller
    )

    print("\n✅ Services initialized")

    # Create a task graph with web search
    print("\n📋 Creating Task Graph with Web Search...")

    graph = TaskGraph()

    # Task 1: Search for latest AI trends
    search_task = TaskNode(
        agent=AgentType.WEB_SEARCH,
        action="search_web",
        parameters={
            "query": "artificial intelligence trends 2024",
            "max_results": 5
        }
    )
    graph.add_node(search_task)

    # Task 2: Search for Python async best practices
    python_search = TaskNode(
        agent=AgentType.WEB_SEARCH,
        action="search_technical",
        parameters={
            "query": "async await best practices",
            "tech_stack": "Python",
            "max_results": 3
        }
    )
    graph.add_node(python_search)

    print(f"   Created graph with {len(graph.nodes)} tasks")

    # Create task execution
    execution = TaskExecution(
        user_id="test_user",
        intent="Research latest AI trends and Python async best practices",
        task_graph=graph
    )

    print(f"   Execution ID: {execution.execution_id}")

    # Execute the task graph
    print("\n🚀 Executing Task Graph...")

    result = await execution_engine.execute_task_graph(
        execution,
        execution.execution_id
    )

    print(f"\n📊 Execution Results:")
    print(f"   Success: {result.get('success')}")
    print(f"   Tasks Executed: {result.get('tasks_executed')}")
    print(f"   Execution Time: {result.get('execution_time', 0):.2f}s")

    if result.get("success"):
        print(f"\n✅ Workflow completed successfully!")
        print(f"   All web search tasks executed")
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")

    print("\n" + "=" * 60)
    print("✨ Web Search Agent workflow test completed!")


async def test_direct_web_search():
    """Test web search agent directly"""
    print("\n🔍 Testing Web Search Agent Directly")
    print("=" * 60)

    agent = WebSearchAgent()

    # Test without API key (error handling)
    print("\n1️⃣  Testing Error Handling (no API key)...")
    result = await agent.execute("search_web", {"query": "test"})

    if result["status"] == "failed":
        print(f"   ✅ Error handled correctly: {result['error']}")
    else:
        print(f"   ❌ Unexpected success (might have API key)")

    # Test missing query parameter
    print("\n2️⃣  Testing Parameter Validation...")
    result = await agent.execute("search_web", {})

    if result["status"] == "failed":
        print(f"   ✅ Validation working: {result['error']}")
    else:
        print(f"   ❌ Validation failed")

    print("\n" + "=" * 60)
    print("✨ Direct agent test completed!")


if __name__ == "__main__":
    print("🌐 ZIEL-MAS Web Search Agent Demo")
    print("=" * 60)

    # Check for API key
    import os
    if not os.getenv("ZAI_API_KEY") or os.getenv("ZAI_API_KEY") == "your-zai-api-key-here":
        print("\n⚠️  Note: ZAI_API_KEY not configured")
        print("   The agent will demonstrate error handling")
        print("   To test with real searches, add your API key to backend/.env")
    else:
        print("\n✅ ZAI_API_KEY configured - Ready for real searches!")

    print("\nRunning tests...\n")

    # Run tests
    asyncio.run(test_direct_web_search())
    print()
    asyncio.run(test_web_search_workflow())

    print("\n🎉 All tests completed!")
    print("\n💡 To use web search in your tasks:")
    print("   agent: AgentType.WEB_SEARCH")
    print("   action: 'search_web', 'search_news', or 'search_technical'")
    print("   parameters: { query: 'your search term' }")
