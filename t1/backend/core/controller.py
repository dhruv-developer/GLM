"""
Controller Agent for ZIEL-MAS
Central orchestrator that uses GLM 5.1 to parse intent and generate task graphs
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from backend.models.task import (
    TaskGraph, TaskNode, TaskStatus, AgentType, ConditionalBranch
)
from backend.models.agent import AGENT_CONFIGS


class ControllerAgent:
    """
    Controller Agent - The central brain of ZIEL-MAS
    Uses GLM 5.1 to:
    1. Parse natural language intent
    2. Decompose tasks into sub-tasks
    3. Generate task DAGs
    4. Assign agents to tasks
    5. Monitor and re-plan on failures
    """

    def __init__(self, glm_api_key: str, glm_api_url: str = "https://api.glm.ai/v1"):
        self.glm_api_key = glm_api_key
        self.glm_api_url = glm_api_url
        self.agent_configs = AGENT_CONFIGS

    async def parse_intent(self, intent: str) -> Dict[str, Any]:
        """
        Parse user intent and extract key information
        Returns structured understanding of the request
        """
        logger.info(f"Parsing intent: {intent}")

        # In production, this would call GLM 5.1
        # For now, we'll use pattern matching and heuristics

        intent_lower = intent.lower()

        # Extract task type
        task_type = self._detect_task_type(intent_lower)

        # Extract entities (dates, contacts, services, etc.)
        entities = self._extract_entities(intent)

        # Extract time information
        time_info = self._extract_time_info(intent_lower)

        # Detect urgency
        priority = self._detect_priority(intent_lower)

        return {
            "task_type": task_type,
            "entities": entities,
            "time_info": time_info,
            "priority": priority,
            "original_intent": intent
        }

    def _detect_task_type(self, intent: str) -> str:
        """Detect the type of task from intent"""
        task_keywords = {
            "communication": ["send", "email", "message", "whatsapp", "sms", "notify"],
            "scheduling": ["schedule", "remind", "at", "tomorrow", "today", "oclock"],
            "web_automation": ["fill", "form", "apply", "submit", "login", "scrape"],
            "data_processing": ["fetch", "get", "find", "search", "filter", "rank"],
            "api_call": ["api", "call", "request", "webhook"],
            "booking": ["book", "reserve", "cab", "table", "ticket"]
        }

        for task_type, keywords in task_keywords.items():
            if any(keyword in intent for keyword in keywords):
                return task_type

        return "general"

    def _extract_entities(self, intent: str) -> Dict[str, Any]:
        """Extract entities from intent (names, emails, services, etc.)"""
        entities = {}

        # Simple email extraction
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', intent)
        if emails:
            entities["emails"] = emails

        # Phone number extraction
        phones = re.findall(r'\+?\d{10,15}', intent)
        if phones:
            entities["phones"] = phones

        # URL extraction
        urls = re.findall(r'https?://[^\s]+', intent)
        if urls:
            entities["urls"] = urls

        # Common service names
        services = ["gmail", "whatsapp", "twitter", "facebook", "github", "slack", "telegram"]
        found_services = [s for s in services if s in intent.lower()]
        if found_services:
            entities["services"] = found_services

        return entities

    def _extract_time_info(self, intent: str) -> Dict[str, Any]:
        """Extract time-related information from intent"""
        time_info = {}

        # Check for scheduling keywords
        if any(word in intent for word in ["schedule", "remind", "at", "until"]):
            time_info["scheduled"] = True

        # Extract time patterns (12 AM, 3:30 PM, etc.)
        import re
        time_patterns = re.findall(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)', intent)
        if time_patterns:
            time_info["times"] = time_patterns

        return time_info

    def _detect_priority(self, intent: str) -> str:
        """Detect task priority from intent"""
        urgent_keywords = ["urgent", "asap", "immediately", "now", "emergency"]
        if any(keyword in intent for keyword in urgent_keywords):
            return "high"

        low_priority_keywords = ["whenever", "eventually", "sometime", "no rush"]
        if any(keyword in intent for keyword in low_priority_keywords):
            return "low"

        return "medium"

    async def generate_task_graph(
        self,
        parsed_intent: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> TaskGraph:
        """
        Generate a task DAG from parsed intent
        This is the core planning function
        """
        logger.info("Generating task graph from parsed intent")

        task_graph = TaskGraph()

        task_type = parsed_intent["task_type"]
        entities = parsed_intent["entities"]

        # Generate task nodes based on task type
        if task_type == "communication":
            await self._generate_communication_tasks(task_graph, parsed_intent)
        elif task_type == "scheduling":
            await self._generate_scheduling_tasks(task_graph, parsed_intent)
        elif task_type == "web_automation":
            await self._generate_web_automation_tasks(task_graph, parsed_intent)
        elif task_type == "data_processing":
            await self._generate_data_tasks(task_graph, parsed_intent)
        elif task_type == "booking":
            await self._generate_booking_tasks(task_graph, parsed_intent)
        else:
            await self._generate_general_tasks(task_graph, parsed_intent)

        logger.info(f"Generated task graph with {len(task_graph.nodes)} nodes")
        return task_graph

    async def _generate_communication_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for communication-type requests"""
        # Example: "Send email to john@example.com with birthday wishes"

        # Task 1: Prepare message content
        prepare_task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="prepare_message",
            parameters={
                "intent": intent["original_intent"],
                "entities": intent["entities"]
            }
        )
        graph.add_node(prepare_task)

        # Task 2: Send the message
        send_task = TaskNode(
            agent=AgentType.COMMUNICATION,
            action="send_message",
            parameters={
                "recipient": intent["entities"].get("emails", [""])[0],
                "service": intent["entities"].get("services", ["email"])[0]
            },
            dependencies=[prepare_task.task_id]
        )
        graph.add_node(send_task)

        # Task 3: Validate delivery
        validate_task = TaskNode(
            agent=AgentType.VALIDATION,
            action="verify_delivery",
            parameters={},
            dependencies=[send_task.task_id]
        )
        graph.add_node(validate_task)

    async def _generate_scheduling_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for scheduling-type requests"""
        # Example: "Send birthday message at 12 AM"

        # Task 1: Prepare the scheduled task
        prepare_task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="prepare_scheduled_task",
            parameters={"intent": intent["original_intent"]}
        )
        graph.add_node(prepare_task)

        # Task 2: Schedule execution
        schedule_task = TaskNode(
            agent=AgentType.SCHEDULER,
            action="schedule_task",
            parameters={
                "time_info": intent["time_info"],
                "task_data": intent["original_intent"]
            },
            dependencies=[prepare_task.task_id]
        )
        graph.add_node(schedule_task)

    async def _generate_web_automation_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for web automation requests"""
        # Example: "Apply for job at company.com"

        # Task 1: Navigate to URL
        navigate_task = TaskNode(
            agent=AgentType.WEB_AUTOMATION,
            action="navigate",
            parameters={"url": intent["entities"].get("urls", [""])[0]}
        )
        graph.add_node(navigate_task)

        # Task 2: Fill form
        fill_task = TaskNode(
            agent=AgentType.WEB_AUTOMATION,
            action="fill_form",
            parameters={"intent": intent["original_intent"]},
            dependencies=[navigate_task.task_id]
        )
        graph.add_node(fill_task)

        # Task 3: Submit
        submit_task = TaskNode(
            agent=AgentType.WEB_AUTOMATION,
            action="submit",
            parameters={},
            dependencies=[fill_task.task_id]
        )
        graph.add_node(submit_task)

        # Task 4: Validate submission
        validate_task = TaskNode(
            agent=AgentType.VALIDATION,
            action="verify_submission",
            parameters={},
            dependencies=[submit_task.task_id]
        )
        graph.add_node(validate_task)

    async def _generate_data_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for data processing requests"""
        # Example: "Find top 10 restaurants nearby"

        # Task 1: Fetch data
        fetch_task = TaskNode(
            agent=AgentType.DATA,
            action="fetch_data",
            parameters={
                "query": intent["original_intent"],
                "entities": intent["entities"]
            }
        )
        graph.add_node(fetch_task)

        # Task 2: Filter data
        filter_task = TaskNode(
            agent=AgentType.DATA,
            action="filter_data",
            parameters={},
            dependencies=[fetch_task.task_id]
        )
        graph.add_node(filter_task)

        # Task 3: Rank/sort results
        rank_task = TaskNode(
            agent=AgentType.DATA,
            action="rank_data",
            parameters={},
            dependencies=[filter_task.task_id]
        )
        graph.add_node(rank_task)

    async def _generate_booking_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for booking requests"""
        # Example: "Book a cab to location"

        # Task 1: Prepare booking details
        prepare_task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="prepare_booking",
            parameters={"intent": intent["original_intent"]}
        )
        graph.add_node(prepare_task)

        # Task 2: Call booking API
        book_task = TaskNode(
            agent=AgentType.API,
            action="book_cab",
            parameters={
                "service": "uber",  # or from intent
                "details": intent["entities"]
            },
            dependencies=[prepare_task.task_id]
        )
        graph.add_node(book_task)

        # Task 3: Confirm booking
        confirm_task = TaskNode(
            agent=AgentType.VALIDATION,
            action="verify_booking",
            parameters={},
            dependencies=[book_task.task_id]
        )
        graph.add_node(confirm_task)

    async def _generate_general_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for general requests"""
        # Create a simple single-task graph for unknown types
        task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="process_request",
            parameters={"intent": intent["original_intent"]}
        )
        graph.add_node(task)

    async def re_plan(
        self,
        graph: TaskGraph,
        failed_task_id: str,
        error: str
    ) -> Optional[TaskGraph]:
        """
        Re-plan the task graph when a task fails
        Attempts to find alternative execution paths
        """
        logger.info(f"Re-planning for failed task: {failed_task_id}")

        failed_task = graph.nodes.get(failed_task_id)
        if not failed_task:
            logger.error(f"Task {failed_task_id} not found in graph")
            return None

        # Check if retry is possible
        if failed_task.retry_count < failed_task.max_retries:
            failed_task.retry_count += 1
            failed_task.status = TaskStatus.PENDING
            logger.info(f"Will retry task {failed_task_id} (attempt {failed_task.retry_count})")
            return graph

        # Try alternative agent
        alternative_agent = self._find_alternative_agent(failed_task.agent)
        if alternative_agent:
            new_task = TaskNode(
                agent=alternative_agent,
                action=failed_task.action,
                parameters=failed_task.parameters,
                dependencies=failed_task.dependencies
            )
            graph.add_node(new_task)

            # Update dependent tasks to use new task
            for task in graph.nodes.values():
                if failed_task_id in task.dependencies:
                    task.dependencies.remove(failed_task_id)
                    task.dependencies.append(new_task.task_id)

            # Remove failed task
            del graph.nodes[failed_task_id]
            logger.info(f"Created alternative task with {alternative_agent}")
            return graph

        logger.error("No alternative execution path found")
        return None

    def _find_alternative_agent(self, current_agent: AgentType) -> Optional[AgentType]:
        """Find an alternative agent that can handle the task"""
        alternatives = {
            AgentType.API: [AgentType.WEB_AUTOMATION],
            AgentType.WEB_AUTOMATION: [AgentType.API],
            AgentType.COMMUNICATION: [],
            AgentType.DATA: [],
            AgentType.SCHEDULER: []
        }

        return alternatives.get(current_agent, [None])[0]

    async def estimate_execution_time(self, graph: TaskGraph) -> int:
        """Estimate total execution time for a task graph"""
        total_time = 0
        for task in graph.nodes.values():
            # Base time for each task (configurable per agent type)
            agent_config = self.agent_configs.get(task.agent)
            if agent_config:
                total_time += agent_config.estimated_duration if hasattr(agent_config, 'estimated_duration') else 60

            # Add task timeout
            total_time += task.timeout

        # Add buffer time
        return int(total_time * 1.2)

    async def optimize_graph(self, graph: TaskGraph) -> TaskGraph:
        """Optimize the task graph for parallel execution"""
        # Find tasks that can be executed in parallel
        ready_tasks = graph.get_ready_tasks()

        # Mark parallelizable tasks
        if len(ready_tasks) > 1:
            graph.parallel_execution = True

        return graph
