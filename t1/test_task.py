import asyncio
import sys
sys.path.append('/Users/dhruvdawar11/Desktop/Projects/GLM-Hack/t1')

from backend.core.controller import ControllerAgent
from backend.models.task import TaskExecution, TaskStatus
from backend.services.database import DatabaseService
from backend.services.cache import RedisService
import os

async def test_task_creation():
    # Initialize services
    db = DatabaseService(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    await db.connect()
    
    redis = RedisService(os.getenv("REDIS_URI", "redis://localhost:6379/0"))
    await redis.connect()
    
    controller = ControllerAgent(
        glm_api_key=os.getenv("GLM_API_KEY", "test-key"),
        glm_api_url=os.getenv("GLM_API_URL", "https://api.glm.ai/v1")
    )
    
    # Test intent parsing
    print("Testing intent parsing...")
    intent = "Search for the latest Python async best practices"
    parsed = await controller.parse_intent(intent)
    print(f"Parsed intent: {parsed}")
    
    # Test task graph generation
    print("\nGenerating task graph...")
    task_graph = await controller.generate_task_graph(parsed, "test_user")
    print(f"Task graph nodes: {len(task_graph.nodes)}")
    
    for node_id, node in task_graph.nodes.items():
        print(f"  - {node_id}: {node.action} ({node.agent})")
    
    # Create execution
    print("\nCreating task execution...")
    execution = TaskExecution(
        user_id="test_user",
        intent=intent,
        task_graph=task_graph,
        priority="medium",
        status=TaskStatus.PENDING
    )
    
    # Store in database
    await db.create_task_execution(execution.model_dump())
    print(f"Created execution: {execution.execution_id}")
    
    # Clean up
    await db.close()
    await redis.close()

if __name__ == "__main__":
    asyncio.run(test_task_creation())
