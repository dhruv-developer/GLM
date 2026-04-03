"""
Demo Workflows and Examples for ZIEL-MAS
Run this to see example workflows in action
"""

import asyncio
from backend.core.controller import ControllerAgent
from backend.models.task import TaskExecution, TaskStatus


async def demo_birthday_message():
    """
    Demo: "Send birthday message to my mother at 12 AM"
    Demonstrates scheduling + communication agents
    """
    print("=" * 70)
    print("🎂 DEMO 1: Scheduled Birthday Message")
    print("=" * 70)

    controller = ControllerAgent(
        glm_api_key="demo_key",
        glm_api_url="https://demo.api.com"
    )

    intent = "Send birthday message to my mother at 12 AM"
    print(f"\n📝 User Intent: \"{intent}\"")

    # Step 1: Parse Intent
    print("\n1️⃣  PARSING INTENT...")
    parsed = await controller.parse_intent(intent)
    print(f"   ✓ Detected Task Type: {parsed['task_type']}")
    print(f"   ✓ Priority: {parsed['priority']}")
    print(f"   ✓ Time Info: {parsed['time_info']}")

    # Step 2: Generate Task Graph
    print("\n2️⃣  GENERATING TASK GRAPH...")
    graph = await controller.generate_task_graph(parsed)

    print(f"   ✓ Created {len(graph.nodes)} tasks:")
    for i, (task_id, task) in enumerate(graph.nodes.items(), 1):
        print(f"      {i}. {task.action} → {task.agent.value}")

    # Step 3: Execution Plan
    print("\n3️⃣  EXECUTION PLAN:")
    print("   ✓ Controller: Prepare message content")
    print("   ✓ Scheduler: Set trigger for 12:00 AM")
    print("   ✓ Communication: Send email/message")
    print("   ✓ Validation: Verify delivery")

    print("\n✅ WORKFLOW READY FOR EXECUTION")
    print("=" * 70 + "\n")


async def demo_job_application():
    """
    Demo: "Apply for Software Engineer position at Google"
    Demonstrates web automation agent
    """
    print("=" * 70)
    print("💼 DEMO 2: Automated Job Application")
    print("=" * 70)

    controller = ControllerAgent(
        glm_api_key="demo_key",
        glm_api_url="https://demo.api.com"
    )

    intent = "Apply for Software Engineer position at Google"
    print(f"\n📝 User Intent: \"{intent}\"")

    # Step 1: Parse Intent
    print("\n1️⃣  PARSING INTENT...")
    parsed = await controller.parse_intent(intent)
    print(f"   ✓ Detected Task Type: {parsed['task_type']}")

    # Step 2: Generate Task Graph
    print("\n2️⃣  GENERATING TASK GRAPH...")
    graph = await controller.generate_task_graph(parsed)

    print(f"   ✓ Created {len(graph.nodes)} tasks:")
    for i, (task_id, task) in enumerate(graph.nodes.items(), 1):
        print(f"      {i}. {task.action} → {task.agent.value}")

    # Step 3: Execution Plan
    print("\n3️⃣  EXECUTION PLAN:")
    print("   ✓ Web Automation: Navigate to job posting")
    print("   ✓ Web Automation: Fill application form")
    print("   ✓ Web Automation: Upload documents")
    print("   ✓ Web Automation: Submit application")
    print("   ✓ Validation: Verify submission confirmation")

    print("\n✅ WORKFLOW READY FOR EXECUTION")
    print("=" * 70 + "\n")


async def demo_restaurant_search():
    """
    Demo: "Find top 5 Italian restaurants nearby"
    Demonstrates data agent
    """
    print("=" * 70)
    print("🍕 DEMO 3: Restaurant Search & Ranking")
    print("=" * 70)

    controller = ControllerAgent(
        glm_api_key="demo_key",
        glm_api_url="https://demo.api.com"
    )

    intent = "Find top 5 Italian restaurants nearby"
    print(f"\n📝 User Intent: \"{intent}\"")

    # Step 1: Parse Intent
    print("\n1️⃣  PARSING INTENT...")
    parsed = await controller.parse_intent(intent)
    print(f"   ✓ Detected Task Type: {parsed['task_type']}")

    # Step 2: Generate Task Graph
    print("\n2️⃣  GENERATING TASK GRAPH...")
    graph = await controller.generate_task_graph(parsed)

    print(f"   ✓ Created {len(graph.nodes)} tasks:")
    for i, (task_id, task) in enumerate(graph.nodes.items(), 1):
        print(f"      {i}. {task.action} → {task.agent.value}")

    # Step 3: Execution Plan
    print("\n3️⃣  EXECUTION PLAN:")
    print("   ✓ Data: Fetch restaurants from location APIs")
    print("   ✓ Data: Filter by cuisine (Italian)")
    print("   ✓ Data: Filter by distance/radius")
    print("   ✓ Data: Rank by rating and reviews")
    print("   ✓ Data: Return top 5 results")

    print("\n✅ WORKFLOW READY FOR EXECUTION")
    print("=" * 70 + "\n")


async def demo_cab_booking():
    """
    Demo: "Book an Uber to the airport at 3 PM"
    Demonstrates API agent + scheduling
    """
    print("=" * 70)
    print("🚗 DEMO 4: Cab Booking")
    print("=" * 70)

    controller = ControllerAgent(
        glm_api_key="demo_key",
        glm_api_url="https://demo.api.com"
    )

    intent = "Book an Uber to the airport at 3 PM"
    print(f"\n📝 User Intent: \"{intent}\"")

    # Step 1: Parse Intent
    print("\n1️⃣  PARSING INTENT...")
    parsed = await controller.parse_intent(intent)
    print(f"   ✓ Detected Task Type: {parsed['task_type']}")
    print(f"   ✓ Entities: {parsed['entities']}")

    # Step 2: Generate Task Graph
    print("\n2️⃣  GENERATING TASK GRAPH...")
    graph = await controller.generate_task_graph(parsed)

    print(f"   ✓ Created {len(graph.nodes)} tasks:")
    for i, (task_id, task) in enumerate(graph.nodes.items(), 1):
        print(f"      {i}. {task.action} → {task.agent.value}")

    # Step 3: Execution Plan
    print("\n3️⃣  EXECUTION PLAN:")
    print("   ✓ Controller: Prepare booking details")
    print("   ✓ API: Call ride-sharing service API")
    print("   ✓ Scheduler: Schedule for 3 PM")
    print("   ✓ Validation: Confirm booking")

    print("\n✅ WORKFLOW READY FOR EXECUTION")
    print("=" * 70 + "\n")


async def run_all_demos():
    """Run all demo workflows"""
    print("\n" + "🎯" * 35)
    print("ZIEL-MAS: DEMO WORKFLOWS")
    print("Zero-Interaction Execution Links with Multi-Agent System")
    print("🎯" * 35 + "\n")

    await demo_birthday_message()
    await demo_job_application()
    await demo_restaurant_search()
    await demo_cab_booking()

    print("=" * 70)
    print("🎉 ALL DEMO WORKFLOWS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📊 SUMMARY:")
    print("   • Birthday Message: Scheduling + Communication")
    print("   • Job Application: Web Automation")
    print("   • Restaurant Search: Data Processing")
    print("   • Cab Booking: API Integration")
    print("\n💡 Each workflow is autonomous, secure, and zero-interaction!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_demos())
