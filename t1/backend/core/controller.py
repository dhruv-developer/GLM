"""
Controller Agent for ZIEL-MAS
Central orchestrator that uses GLM 5.1 to parse intent and generate task graphs
"""

import json
import asyncio
import httpx
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
        Parse user intent using GLM 5.1 API
        Returns structured understanding of the request
        """
        logger.info(f"Parsing intent with GLM API: {intent}")

        try:
            # Use GLM API to parse intent
            parsed = await self._call_glm_for_intent_parsing(intent)
            return parsed
        except Exception as e:
            logger.error(f"GLM API intent parsing failed: {e}")
            # Fallback to basic pattern matching only if API fails
            logger.warning("Falling back to pattern matching for intent parsing")
            return await self._parse_intent_fallback(intent)

    async def _call_glm_for_intent_parsing(self, intent: str) -> Dict[str, Any]:
        """Call GLM API for intent parsing"""
        if not self.glm_api_key:
            raise Exception("GLM API key not configured")

        prompt = f"""Analyze this user intent and extract structured information:

Intent: "{intent}"

Return a JSON object with:
{{
    "task_type": "one of: web_search, code_generation, communication, scheduling, web_automation, data_processing, api_call, booking, general",
    "entities": {{
        "emails": ["email1@example.com", "email2@example.com"],
        "phones": ["+1234567890"],
        "urls": ["https://example.com"],
        "services": ["gmail", "whatsapp", "twitter"],
        "names": ["John Doe"],
        "locations": ["New York"],
        "dates": ["2024-04-05"],
        "times": ["12:00 PM"]
    }},
    "time_info": {{
        "scheduled": true/false,
        "times": ["12:00 AM"],
        "urgency": "immediate/normal/low"
    }},
    "priority": "high/medium/low",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this classification was chosen"
}}

Only return valid JSON, no explanations."""

        headers = {
            "Authorization": f"Bearer {self.glm_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "glm-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at understanding user intent and extracting structured information. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1000
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.glm_api_url}/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Parse JSON response
                try:
                    parsed = json.loads(content)
                    # Add original intent
                    parsed["original_intent"] = intent
                    return parsed
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GLM response as JSON: {e}")
                    logger.error(f"GLM response content: {content}")
                    raise Exception("Invalid JSON response from GLM")
            else:
                raise Exception(f"GLM API error: {response.status_code} - {response.text}")

    async def _parse_intent_fallback(self, intent: str) -> Dict[str, Any]:
        """Fallback pattern matching when GLM API is unavailable"""
        logger.warning("Using fallback pattern matching for intent parsing")
        
        intent_lower = intent.lower()

        # Extract task type using existing logic
        task_type = self._detect_task_type(intent_lower)

        # Extract entities using existing logic
        entities = self._extract_entities(intent)

        # Extract time information using existing logic
        time_info = self._extract_time_info(intent_lower)

        # Detect urgency using existing logic
        priority = self._detect_priority(intent_lower)

        return {
            "task_type": task_type,
            "entities": entities,
            "time_info": time_info,
            "priority": priority,
            "original_intent": intent,
            "confidence": 0.6,  # Lower confidence for fallback
            "reasoning": "Parsed using pattern matching fallback"
        }

    def _detect_task_type(self, intent: str) -> str:
        """Detect the type of task from intent"""
        # Priority order matters - check more specific types first
        task_keywords = {
            "web_search": ["search", "find", "google", "look up", "research"],
            "code_generation": ["write", "generate", "create code", "develop", "implement", "scrape", "scraping"],
            "communication": ["send", "email", "message", "whatsapp", "sms", "notify"],
            "scheduling": ["schedule", "remind", "at", "tomorrow", "today", "oclock"],
            "web_automation": ["fill", "form", "apply", "submit", "login", "automate", "click", "type"],
            "data_processing": ["fetch", "get", "filter", "rank", "analyze", "process"],
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
        Generate a task DAG from parsed intent using GLM 5.1 API
        This is the core planning function
        """
        logger.info("Generating task graph with GLM API from parsed intent")

        try:
            # Use GLM API to generate task graph
            task_graph = await self._call_glm_for_task_graph_generation(parsed_intent)
            return task_graph
        except Exception as e:
            logger.error(f"GLM API task graph generation failed: {e}")
            # Fallback to rule-based generation
            logger.warning("Falling back to rule-based task graph generation")
            return await self._generate_task_graph_fallback(parsed_intent)

    async def _call_glm_for_task_graph_generation(self, parsed_intent: Dict[str, Any]) -> TaskGraph:
        """Call GLM API for task graph generation"""
        if not self.glm_api_key:
            raise Exception("GLM API key not configured")

        intent = parsed_intent["original_intent"]
        task_type = parsed_intent.get("task_type", "general")

        prompt = f"""Generate a task execution plan for this user request:

Intent: "{intent}"
Task Type: {task_type}
Entities: {json.dumps(parsed_intent.get('entities', {}), indent=2)}

Create a detailed task plan by breaking this down into specific, executable steps.
For each step, specify:
1. The agent type that should handle it
2. The specific action to perform
3. Required parameters
4. Dependencies on other steps

Available agent types:
- controller: General processing, planning
- web_search: Search for information online
- api_call: Make API requests to external services
- web_automation: Automate web browser interactions
- communication: Send emails, messages
- data: Process and analyze data
- scheduler: Schedule tasks for later
- validation: Verify results and quality
- code_writer: Generate code
- document: Process documents

Return a JSON task graph:
{{
    "nodes": {{
        "task_1": {{
            "agent": "agent_type",
            "action": "specific_action",
            "parameters": {{"key": "value"}},
            "dependencies": [],
            "description": "What this task does"
        }},
        "task_2": {{
            "agent": "agent_type", 
            "action": "specific_action",
            "parameters": {{"key": "value"}},
            "dependencies": ["task_1"],
            "description": "What this task does"
        }}
    }},
    "reasoning": "Explanation of why this task breakdown was chosen"
}}

Only return valid JSON, no explanations."""

        headers = {
            "Authorization": f"Bearer {self.glm_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "glm-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at breaking down complex tasks into executable steps. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.glm_api_url}/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Parse JSON response
                try:
                    graph_data = json.loads(content)
                    return self._build_task_graph_from_glm_response(graph_data, parsed_intent)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GLM task graph response as JSON: {e}")
                    logger.error(f"GLM response content: {content}")
                    raise Exception("Invalid JSON response from GLM")
            else:
                raise Exception(f"GLM API error: {response.status_code} - {response.text}")

    def _build_task_graph_from_glm_response(self, graph_data: Dict[str, Any], parsed_intent: Dict[str, Any]) -> TaskGraph:
        """Build TaskGraph from GLM API response"""
        task_graph = TaskGraph()
        
        nodes_data = graph_data.get("nodes", {})
        
        for task_id, node_data in nodes_data.items():
            # Convert agent string to AgentType enum
            agent_str = node_data.get("agent", "controller")
            try:
                agent_type = AgentType(agent_str)
            except ValueError:
                logger.warning(f"Unknown agent type: {agent_str}, using controller")
                agent_type = AgentType.CONTROLLER

            task_node = TaskNode(
                agent=agent_type,
                action=node_data.get("action", "process"),
                parameters=node_data.get("parameters", {}),
                dependencies=node_data.get("dependencies", [])
            )
            task_graph.add_node(task_node)

            # Add edges for dependencies
            for dep in node_data.get("dependencies", []):
                task_graph.add_edge(dep, task_id)

        logger.info(f"Generated task graph with {len(task_graph.nodes)} nodes using GLM API")
        return task_graph

    async def _generate_task_graph_fallback(self, parsed_intent: Dict[str, Any]) -> TaskGraph:
        """Fallback rule-based task graph generation"""
        logger.warning("Using fallback rule-based task graph generation")
        
        task_graph = TaskGraph()
        task_type = parsed_intent["task_type"]
        entities = parsed_intent["entities"]

        # Generate task nodes based on task type (existing logic)
        if task_type == "web_search":
            await self._generate_web_search_tasks(task_graph, parsed_intent)
        elif task_type == "code_generation":
            await self._generate_code_generation_tasks(task_graph, parsed_intent)
        elif task_type == "communication":
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

        logger.info(f"Generated fallback task graph with {len(task_graph.nodes)} nodes")
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

    def _find_alternative_agent(self, current_agent) -> Optional[AgentType]:
        """Find an alternative agent that can handle the task"""
        # current_agent may be a string (due to use_enum_values=True) or AgentType enum
        agent_key = current_agent if isinstance(current_agent, str) else current_agent.value

        # Map by string values
        alternatives = {
            AgentType.API.value: AgentType.WEB_AUTOMATION,
            AgentType.WEB_AUTOMATION.value: AgentType.API,
            AgentType.COMMUNICATION.value: None,
            AgentType.DATA.value: None,
            AgentType.SCHEDULER.value: None,
            AgentType.CONTROLLER.value: None,
        }

        return alternatives.get(agent_key)

    async def estimate_execution_time(self, graph: TaskGraph) -> int:
        """Estimate total execution time for a task graph"""
        total_time = 0
        for task in graph.nodes.values():
            # task.agent may be a string or AgentType enum (due to use_enum_values=True)
            agent_key = task.agent
            if isinstance(agent_key, str):
                try:
                    agent_key = AgentType(agent_key)
                except ValueError:
                    agent_key = None

            # Base time for each task (configurable per agent type)
            agent_config = self.agent_configs.get(agent_key) if agent_key else None
            if agent_config:
                total_time += agent_config.estimated_duration if hasattr(agent_config, 'estimated_duration') else 60

            # Add task timeout
            total_time += task.timeout

        # Add buffer time
        return int(total_time * 1.2)

    async def _generate_web_search_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for web search requests"""
        # Example: "Search for the latest Python async best practices"

        # Task 1: Parse search query
        parse_task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="parse_search_query",
            parameters={
                "intent": intent["original_intent"],
                "entities": intent["entities"]
            }
        )
        graph.add_node(parse_task)

        # Task 2: Perform web search
        search_task = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={
                "query": intent["original_intent"],  # Will be replaced with cleaned query during execution
                "num_results": 10
            }
        )
        search_task.add_dependency(parse_task.task_id)  # Depends on parse task
        graph.add_node(search_task)

        # Task 3: Generate document/summary from results
        document_task = TaskNode(
            agent=AgentType.DOCUMENT,
            action="process_search_results",
            parameters={
                "intent": intent["original_intent"]
            },
            dependencies=[search_task.task_id]
        )
        graph.add_node(document_task)

    async def _generate_code_generation_tasks(self, graph: TaskGraph, intent: Dict[str, Any]):
        """Generate tasks for code generation requests"""
        # Example: "Write a Python function to fetch data from API"

        # Task 1: Understand requirements
        understand_task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="understand_code_requirements",
            parameters={
                "intent": intent["original_intent"],
                "entities": intent["entities"]
            }
        )
        graph.add_node(understand_task)

        # Task 2: Search for relevant code examples if needed
        search_task = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={
                "query": f"code examples: {intent['original_intent']}",
                "num_results": 5
            },
            dependencies=[understand_task.task_id]
        )
        graph.add_node(search_task)

        # Task 3: Generate the code
        generate_task = TaskNode(
            agent=AgentType.CONTROLLER,
            action="generate_code",
            parameters={
                "intent": intent["original_intent"]
            },
            dependencies=[search_task.task_id]
        )
        graph.add_node(generate_task)

        # Task 4: Validate and test the code
        validate_task = TaskNode(
            agent=AgentType.VALIDATION,
            action="validate_code",
            parameters={
                "check_syntax": True,
                "check_best_practices": True
            },
            dependencies=[generate_task.task_id]
        )
        graph.add_node(validate_task)

    async def optimize_graph(self, graph: TaskGraph) -> TaskGraph:
        """Optimize the task graph for parallel execution"""
        # Find tasks that can be executed in parallel
        ready_tasks = graph.get_ready_tasks()

        # Mark parallelizable tasks
        if len(ready_tasks) > 1:
            graph.parallel_execution = True

        return graph
