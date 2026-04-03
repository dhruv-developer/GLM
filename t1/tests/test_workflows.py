"""
Demo Workflows for ZIEL-MAS
Example end-to-end workflows
"""

import asyncio
from backend.core.controller import ControllerAgent
from backend.models.task import TaskExecution, TaskStatus
from datetime import datetime


async def workflow_birthday_message():
    """
    Demo Workflow: Send birthday message at midnight
    Intent: "Send birthday message to my mother at 12 AM"
    """
    print("=" * 60)
    print("DEMO WORKFLOW: Birthday Message Scheduler")
    print("=" * 60)

    # Initialize controller
    controller = ControllerAgent(
        glm_api_key="test_key",
        glm_api_url="https://test.api.com"
    )

    # Parse intent
    intent = "Send birthday message to my mother at 12 AM"
    print(f"\n1. Parsing Intent: '{intent}'")

    parsed_intent = await controller.parse_intent(intent)
    print(f"   Task Type: {parsed_intent['task_type']}")
    print(f"   Entities: {parsed_intent['entities']}")
    print(f"   Priority: {parsed_intent['priority']}")

    # Generate task graph
    print("\n2. Generating Task Graph...")
    task_graph = await controller.generate_task_graph(parsed_intent)

    print(f"   Tasks Created: {len(task_graph.nodes)}")
    for task_id, task in task_graph.nodes.items():
        print(f"   - {task.action} (Agent: {task.agent.value})")

    # Create execution
    print("\n3. Creating Execution...")
    execution = TaskExecution(
        intent=intent,
        task_graph=task_graph,
        status=TaskStatus.PENDING
    )

    print(f"   Execution ID: {execution.execution_id}")
    print(f"   Status: {execution.status.value}")

    print("\n4. Execution Plan:")
    print("   ✓ Prepare message content")
    print("   ✓ Schedule task for 12 AM")
    print("   ✓ Send message via Communication Agent")
    print("   ✓ Verify delivery via Validation Agent")

    print("\n" + "=" * 60)
    print("WORKFLOW CREATED SUCCESSFULLY")
    print("=" * 60)

    return execution


async def workflow_job_application():
    """
    Demo Workflow: Automated Job Application
    Intent: "Apply for Software Engineer position at Google"
    """
    print("\n" + "=" * 60)
    print("DEMO WORKFLOW: Automated Job Application")
    print("=" * 60)

    # Initialize controller
    controller = ControllerAgent(
        glm_api_key="test_key",
        glm_api_url="https://test.api.com"
    )

    # Parse intent
    intent = "Apply for Software Engineer position at Google"
    print(f"\n1. Parsing Intent: '{intent}'")

    parsed_intent = await controller.parse_intent(intent)
    print(f"   Task Type: {parsed_intent['task_type']}")

    # Generate task graph
    print("\n2. Generating Task Graph...")
    task_graph = await controller.generate_task_graph(parsed_intent)

    print(f"   Tasks Created: {len(task_graph.nodes)}")
    for task_id, task in task_graph.nodes.items():
        print(f"   - {task.action} (Agent: {task.agent.value})")

    print("\n3. Execution Plan:")
    print("   ✓ Navigate to job posting")
    print("   ✓ Fill application form with user data")
    print("   ✓ Upload resume and cover letter")
    print("   ✓ Submit application")
    print("   ✓ Verify submission confirmation")

    print("\n" + "=" * 60)
    print("WORKFLOW CREATED SUCCESSFULLY")
    print("=" * 60)

    return task_graph


async def workflow_data_fetching():
    """
    Demo Workflow: Data Fetching and Ranking
    Intent: "Find top 5 Italian restaurants nearby"
    """
    print("\n" + "=" * 60)
    print("DEMO WORKFLOW: Data Fetching & Ranking")
    print("=" * 60)

    # Initialize controller
    controller = ControllerAgent(
        glm_api_key="test_key",
        glm_api_url="https://test.api.com"
    )

    # Parse intent
    intent = "Find top 5 Italian restaurants nearby"
    print(f"\n1. Parsing Intent: '{intent}'")

    parsed_intent = await controller.parse_intent(intent)
    print(f"   Task Type: {parsed_intent['task_type']}")

    # Generate task graph
    print("\n2. Generating Task Graph...")
    task_graph = await controller.generate_task_graph(parsed_intent)

    print(f"   Tasks Created: {len(task_graph.nodes)}")
    for task_id, task in task_graph.nodes.items():
        print(f"   - {task.action} (Agent: {task.agent.value})")

    print("\n3. Execution Plan:")
    print("   ✓ Fetch restaurant data from APIs")
    print("   ✓ Filter by cuisine type (Italian)")
    print("   ✓ Filter by location (nearby)")
    print("   ✓ Rank by rating/reviews")
    print("   ✓ Return top 5 results")

    print("\n" + "=" * 60)
    print("WORKFLOW CREATED SUCCESSFULLY")
    print("=" * 60)

    return task_graph


async def workflow_cab_booking():
    """
    Demo Workflow: Cab Booking
    Intent: "Book an Uber to the airport at 3 PM"
    """
    print("\n" + "=" * 60)
    print("DEMO WORKFLOW: Cab Booking")
    print("=" * 60)

    # Initialize controller
    controller = ControllerAgent(
        glm_api_key="test_key",
        glm_api_url="https://test.api.com"
    )

    # Parse intent
    intent = "Book an Uber to the airport at 3 PM"
    print(f"\n1. Parsing Intent: '{intent}'")

    parsed_intent = await controller.parse_intent(intent)
    print(f"   Task Type: {parsed_intent['task_type']}")

    # Generate task graph
    print("\n2. Generating Task Graph...")
    task_graph = await controller.generate_task_graph(parsed_intent)

    print(f"   Tasks Created: {len(task_graph.nodes)}")
    for task_id, task in task_graph.nodes.items():
        print(f"   - {task.action} (Agent: {task.agent.value})")

    print("\n3. Execution Plan:")
    print("   ✓ Extract booking details")
    print("   ✓ Call ride-sharing API")
    print("   ✓ Book cab for specified time")
    print("   ✓ Confirm booking details")
    print("   ✓ Return booking confirmation")

    print("\n" + "=" * 60)
    print("WORKFLOW CREATED SUCCESSFULLY")
    print("=" * 60)

    return task_graph


async def run_all_demos():
    """Run all demo workflows"""
    print("\n" + "🚀" * 30)
    print("ZIEL-MAS DEMO WORKFLOWS")
    print("🚀" * 30)

    await workflow_birthday_message()
    await workflow_job_application()
    await workflow_data_fetching()
    await workflow_cab_booking()

    print("\n" + "✅" * 30)
    print("ALL DEMO WORKFLOWS COMPLETED")
    print("✅" * 30 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_demos())
