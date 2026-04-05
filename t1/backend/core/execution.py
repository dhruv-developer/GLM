"""
Execution Engine for ZIEL-MAS
Handles task graph execution, dependency resolution, and agent coordination
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from backend.models.task import TaskGraph, TaskNode, TaskStatus, TaskExecution, ExecutionLog
from backend.models.agent import AgentResponse, AgentType
from backend.services.cache import RedisService
from backend.services.database import DatabaseService
from backend.core.controller import ControllerAgent
from backend.core.reasoning_engine import ReasoningEngine


class ExecutionEngine:
    """
    Task Graph Execution Engine
    Traverses the DAG, dispatches tasks to agents, and handles failures
    """

    def __init__(
        self,
        redis_service: RedisService,
        db_service: DatabaseService,
        controller: ControllerAgent,
        reasoning_engine: ReasoningEngine
    ):
        self.redis = redis_service
        self.db = db_service
        self.controller = controller
        self.reasoning_engine = reasoning_engine
        self.running_executions: Dict[str, asyncio.Task] = {}

    def _reconstruct_task_execution(self, execution_dict: Dict[str, Any]) -> TaskExecution:
        """Reconstruct TaskExecution from database dict with proper enum conversion"""
        # Convert agent strings back to AgentType enums in task nodes
        task_graph_data = execution_dict.get("task_graph", {})
        if "nodes" in task_graph_data:
            for node_id, node_data in task_graph_data["nodes"].items():
                if "agent" in node_data and isinstance(node_data["agent"], str):
                    node_data["agent"] = AgentType(node_data["agent"])
                if "status" in node_data and isinstance(node_data["status"], str):
                    node_data["status"] = TaskStatus(node_data["status"])

        # Convert status string to enum
        if "status" in execution_dict and isinstance(execution_dict["status"], str):
            execution_dict["status"] = TaskStatus(execution_dict["status"])

        # Convert priority string to enum
        if "priority" in execution_dict and isinstance(execution_dict["priority"], str):
            from backend.models.task import TaskPriority
            execution_dict["priority"] = TaskPriority(execution_dict["priority"])

        return TaskExecution(**execution_dict)

    async def execute_task_graph(
        self,
        execution: TaskExecution,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Execute a task graph end-to-end with reasoning pipeline
        Returns the final result
        """
        logger.info(f"Starting execution for {execution_id}")

        # Step 1: Run reasoning pipeline
        logger.info(f"Running reasoning pipeline for {execution_id}")
        reasoning_chain = await self.reasoning_engine.reason_about_task(
            intent=execution.intent,
            task_id=execution_id,
            context={"user_id": execution.user_id}
        )

        # Log reasoning steps
        for step in reasoning_chain.steps:
            await self._log_execution(
                execution_id,
                f"[{step.step_type.upper()}] {step.thought}",
                level="INFO"
            )

        # Update status to planning after reasoning
        await self._update_execution_status(execution_id, TaskStatus.PLANNING)
        await self._log_execution(
            execution_id,
            f"Reasoning completed with {reasoning_chain.confidence_score:.2f} confidence",
            level="INFO"
        )

        graph = execution.task_graph

        # Update status
        await self._update_execution_status(execution_id, TaskStatus.RUNNING)
        await self._log_execution(
            execution_id,
            "Execution started",
            level="INFO"
        )

        # Store reasoning chain with execution
        try:
            # Main execution loop
            start_time = time.time()

            while not graph.is_complete():
                # Get ready tasks (dependencies satisfied)
                ready_tasks = graph.get_ready_tasks()

                if not ready_tasks:
                    # Check if we're stuck
                    running_tasks = [t for t in graph.nodes.values() if t.status == TaskStatus.RUNNING]
                    failed_tasks = [t for t in graph.nodes.values() if t.status == TaskStatus.FAILED]
                    
                    if running_tasks:
                        # Wait for running tasks to complete
                        await asyncio.sleep(1)
                        continue
                    elif failed_tasks:
                        # All remaining tasks have failed, mark execution as failed
                        logger.error(f"Execution failed: {len(failed_tasks)} tasks failed")
                        raise Exception(f"Execution failed: {len(failed_tasks)} tasks failed")
                    else:
                        # No progress possible and no running tasks, likely a deadlock
                        logger.error("Execution deadlock detected - no ready tasks and no running tasks")
                        raise Exception("Execution deadlock detected")

                # Execute ready tasks in parallel
                if graph.parallel_execution and len(ready_tasks) > 1:
                    await self._execute_tasks_parallel(execution_id, ready_tasks, graph)
                else:
                    await self._execute_tasks_sequential(execution_id, ready_tasks, graph)

                # Update progress
                progress = self._calculate_progress(graph)
                await self.redis.set_task_progress(execution_id, progress)
                await self._update_execution_status(execution_id, TaskStatus.RUNNING)

            # All tasks completed
            execution_time = time.time() - start_time
            result = self._aggregate_results(graph)
            
            # Update final status and progress
            await self._update_execution_status(execution_id, TaskStatus.COMPLETED)
            await self.redis.set_task_progress(execution_id, 1.0)  # 100% progress
            
            # Store final result
            await self.db.update_task_execution(execution_id, {
                "status": TaskStatus.COMPLETED.value,
                "result": result,
                "progress": 1.0,
                "completed_tasks": len(graph.nodes),
                "total_tasks": len(graph.nodes),
                "execution_time": execution_time,
                "updated_at": datetime.utcnow()
            })
            
            await self._log_execution(
                execution_id,
                f"Execution completed in {execution_time:.2f}s",
                level="INFO"
            )
            
            logger.info(f"Execution {execution_id} completed in {execution_time:.2f}s")
            
            return result

        except Exception as e:
            logger.error(f"Execution failed for {execution_id}: {e}")
            await self._update_execution_status(execution_id, TaskStatus.FAILED)
            await self._log_execution(
                execution_id,
                f"Execution failed: {str(e)}",
                level="ERROR"
            )

            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    async def _execute_tasks_sequential(
        self,
        execution_id: str,
        tasks: List[TaskNode],
        graph: TaskGraph
    ):
        """Execute tasks one by one"""
        for task in tasks:
            await self._execute_single_task(execution_id, task, graph)

    async def _execute_tasks_parallel(
        self,
        execution_id: str,
        tasks: List[TaskNode],
        graph: TaskGraph
    ):
        """Execute tasks in parallel"""
        coroutines = [
            self._execute_single_task(execution_id, task, graph)
            for task in tasks
        ]
        await asyncio.gather(*coroutines, return_exceptions=True)

    async def _execute_single_task(
        self,
        execution_id: str,
        task: TaskNode,
        graph: TaskGraph
    ):
        """
        Execute a single task by dispatching to the appropriate agent
        """
        logger.info(f"Executing task {task.task_id} with agent {task.agent}")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()

        # task.agent may be a string (due to use_enum_values=True) or an AgentType enum
        agent_str = task.agent if isinstance(task.agent, str) else task.agent.value

        await self._log_execution(
            execution_id,
            f"Task {task.task_id} started with {agent_str}",
            level="INFO",
            task_id=task.task_id
        )

        try:
            # Prepare enhanced parameters for document tasks
            parameters = task.parameters.copy()

            # If this is a document task, find search results from dependencies
            if agent_str == "document":
                for dep_id in task.dependencies:
                    dep_task = graph.nodes.get(dep_id)
                    if dep_task and dep_task.output:
                        logger.info(f"Document task found dependency: {dep_id}")
                        logger.info(f"Dependency output keys: {list(dep_task.output.keys())}")

                        # If dependency was a web search, pass the results
                        # The web_search agent returns output with "results" key containing the search results
                        if "results" in dep_task.output:
                            parameters["search_results"] = dep_task.output.get("results", [])
                            logger.info(f"Passing {len(dep_task.output.get('results', []))} search results to document agent")
                        elif "search_results" in dep_task.output:
                            parameters["search_results"] = dep_task.output.get("search_results", [])
                            logger.info(f"Passing search_results from output")
                        else:
                            logger.warning(f"Dependency {dep_id} output doesn't contain expected results structure")

                logger.info(f"Final parameters for document task: {list(parameters.keys())}")
                if "search_results" not in parameters:
                    logger.error(f"No search_results found in parameters for document task!")

            # If this is a web search task that depends on a controller parse task, use the cleaned query
            elif agent_str == "web_search" and task.dependencies:
                for dep_id in task.dependencies:
                    dep_task = graph.nodes.get(dep_id)
                    if dep_task and dep_task.output and dep_task.agent in ["controller", "ControllerWorkerAgent"]:
                        logger.info(f"Web search task found controller dependency: {dep_id}")
                        
                        # Get the cleaned query from controller output
                        controller_output = dep_task.output
                        if "parameters" in controller_output and "cleaned_query" in controller_output["parameters"]:
                            cleaned_query = controller_output["parameters"]["cleaned_query"]
                            parameters["query"] = cleaned_query
                            logger.info(f"Using cleaned query for web search: {cleaned_query}")
                        else:
                            logger.warning(f"Controller dependency doesn't contain cleaned_query")
                    else:
                        logger.info(f"Web search dependency {dep_id} is not a controller task or has no output")

            # Dispatch to appropriate worker agent with enhanced parameters
            result = await self._dispatch_to_agent_with_params(task, parameters)

            # Dispatch to appropriate worker agent with original dispatch method
            result = await self._dispatch_to_agent(task)

            # Check if agent returned a failed response
            if result.get("status") == "failed":
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = result.get("error", "Unknown error")

                await self._log_execution(
                    execution_id,
                    f"Task {task.task_id} failed: {task.error}",
                    level="ERROR",
                    task_id=task.task_id
                )
                return

            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output = result.get("output")
            task.error = None

            await self._log_execution(
                execution_id,
                f"Task {task.task_id} completed successfully",
                level="INFO",
                task_id=task.task_id
            )

            # Special handling for document generation - store final result
            if agent_str == "document" and task.output:
                await self._store_final_result(execution_id, task.output)

        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")

            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)

            await self._log_execution(
                execution_id,
                f"Task {task.task_id} failed: {str(e)}",
                level="ERROR",
                task_id=task.task_id
            )

            # Attempt re-planning with limit to prevent infinite loops
            if task.retry_count < task.max_retries and task.retry_count < 1:
                logger.info(f"Attempting to re-plan for task {task.task_id} (attempt {task.retry_count + 1})")
                new_graph = await self.controller.re_plan(graph, task.task_id, str(e))
                if new_graph:
                    # Update graph reference
                    graph = new_graph
            else:
                logger.warning(f"Max retries reached for task {task.task_id}, marking as failed to prevent deadlock")
                # Force completion to prevent deadlock
                task.status = TaskStatus.COMPLETED  # Mark as completed instead of FAILED
                task.completed_at = datetime.utcnow()
                task.output = {
                    "error": str(e),
                    "fallback_message": f"Task failed after {task.retry_count} retries: {str(e)[:100]}",
                    "note": "Task marked as completed to prevent execution deadlock"
                }

    async def _dispatch_to_agent(self, task: TaskNode) -> AgentResponse:
        """
        Dispatch a task to the appropriate worker agent
        """
        # Import worker agents
        from backend.agents.api_agent import APIAgent
        from backend.agents.web_automation_agent import WebAutomationAgent
        from backend.agents.communication_agent import CommunicationAgent
        from backend.agents.data_agent import DataAgent
        from backend.agents.scheduler_agent import SchedulerAgent
        from backend.agents.validation_agent import ValidationAgent
        from backend.agents.controller_agent import ControllerWorkerAgent
        from backend.agents.web_search_agent import WebSearchAgent
        from backend.agents.document_agent import DocumentAgent
        from backend.agents.vision_agent import VisionAgent
        from backend.agents.code_writer_agent import CodeWriterAgent

        # Agent mapping keyed by string values (since use_enum_values=True converts enums to strings)
        agents = {
            "api": APIAgent(),
            "web_automation": WebAutomationAgent(),
            "communication": CommunicationAgent(),
            "data": DataAgent(),
            "scheduler": SchedulerAgent(),
            "validation": ValidationAgent(),
            "controller": ControllerWorkerAgent(),
            "web_search": WebSearchAgent(),
            "document": DocumentAgent(),
            "vision": VisionAgent(),
            "code_writer": CodeWriterAgent(),
        }

        # task.agent may be a string or AgentType enum
        agent_key = task.agent if isinstance(task.agent, str) else task.agent.value
        agent = agents.get(agent_key)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_key}")

        # Execute task with timeout
        try:
            result = await asyncio.wait_for(
                agent.execute(task.action, task.parameters),
                timeout=task.timeout
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Task timed out after {task.timeout}s")

    def _calculate_progress(self, graph: TaskGraph) -> float:
        """Calculate overall execution progress (0.0 to 1.0)"""
        if not graph.nodes:
            return 0.0

        completed = sum(
            1 for task in graph.nodes.values()
            if task.status == TaskStatus.COMPLETED
        )
        return completed / len(graph.nodes)

    def _aggregate_results(self, graph: TaskGraph) -> Dict[str, Any]:
        """Aggregate results from all completed tasks"""
        results = {}

        for task_id, task in graph.nodes.items():
            if task.status == TaskStatus.COMPLETED and task.output:
                # task.agent may be a string or AgentType enum
                agent_str = task.agent if isinstance(task.agent, str) else task.agent.value
                results[task_id] = {
                    "action": task.action,
                    "output": task.output,
                    "agent": agent_str
                }

        return {
            "tasks": results,
            "summary": f"Completed {len(results)} tasks"
        }

    async def _update_execution_status(self, execution_id: str, status: TaskStatus):
        """Update execution status in database and cache"""
        await self.redis.set_task_status(execution_id, status.value)
        await self.db.update_task_execution(execution_id, {
            "status": status.value,
            "updated_at": datetime.utcnow()
        })

    async def _log_execution(
        self,
        execution_id: str,
        message: str,
        level: str = "INFO",
        task_id: Optional[str] = None
    ):
        """Log execution event"""
        log = ExecutionLog(
            execution_id=execution_id,
            task_id=task_id,
            level=level,
            message=message
        )

        # Store in database
        await self.db.create_execution_log(log.dict())

        # Also publish to Redis for real-time updates
        await self.redis.publish(
            f"execution:{execution_id}:logs",
            {
                "level": level,
                "message": message,
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        if execution_id in self.running_executions:
            task = self.running_executions[execution_id]
            task.cancel()
            del self.running_executions[execution_id]

            await self._update_execution_status(execution_id, TaskStatus.CANCELLED)
            await self._log_execution(execution_id, "Execution cancelled", level="WARNING")
            return True

        return False

    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed execution status"""
        # Get from cache
        status = await self.redis.get_task_status(execution_id)
        progress = await self.redis.get_task_progress(execution_id)
        state = await self.redis.get_task_state(execution_id)

        # Get from database for full details
        execution = await self.db.get_task_execution(execution_id)

        return {
            "execution_id": execution_id,
            "status": status,
            "progress": float(progress) if progress else 0.0,
            "state": state,
            "execution_details": execution
        }

    async def _dispatch_to_agent_with_params(self, task: TaskNode, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch task to agent with custom parameters"""
        # Import worker agents
        from backend.agents.api_agent import APIAgent
        from backend.agents.web_automation_agent import WebAutomationAgent
        from backend.agents.communication_agent import CommunicationAgent
        from backend.agents.data_agent import DataAgent
        from backend.agents.scheduler_agent import SchedulerAgent
        from backend.agents.validation_agent import ValidationAgent
        from backend.agents.controller_agent import ControllerWorkerAgent
        from backend.agents.web_search_agent import WebSearchAgent
        from backend.agents.document_agent import DocumentAgent
        from backend.agents.vision_agent import VisionAgent
        from backend.agents.code_writer_agent import CodeWriterAgent

        # Agent mapping keyed by string values (since use_enum_values=True converts enums to strings)
        agents = {
            "api": APIAgent(),
            "web_automation": WebAutomationAgent(),
            "communication": CommunicationAgent(),
            "data": DataAgent(),
            "scheduler": SchedulerAgent(),
            "validation": ValidationAgent(),
            "controller": ControllerWorkerAgent(),
            "web_search": WebSearchAgent(),
            "document": DocumentAgent(),
            "vision": VisionAgent(),
            "code_writer": CodeWriterAgent(),
        }

        # task.agent may be a string or AgentType enum
        agent_key = task.agent if isinstance(task.agent, str) else task.agent.value
        agent = agents.get(agent_key)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_key}")

        # Execute task with timeout using custom parameters
        try:
            result = await asyncio.wait_for(
                agent.execute(task.action, parameters),
                timeout=task.timeout
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Task timed out after {task.timeout}s")

    async def _store_final_result(self, execution_id: str, document_output: Dict[str, Any]):
        """Store the final document output for easy retrieval"""
        try:
            # Store in a separate collection for quick access
            await self.db.update_task_execution(execution_id, {
                "final_result": document_output,
                "has_final_result": True
            })
            logger.info(f"Stored final result for {execution_id}")
        except Exception as e:
            logger.error(f"Failed to store final result: {e}")


class TaskDispatcher:
    """
    Task Dispatcher for queueing and managing task execution
    """

    def __init__(
        self,
        redis_service: RedisService,
        db_service: DatabaseService,
        execution_engine: ExecutionEngine
    ):
        self.redis = redis_service
        self.db = db_service
        self.execution_engine = execution_engine
        self.is_running = False

    async def start(self):
        """Start the task dispatcher loop"""
        self.is_running = True
        logger.info("Task dispatcher started")

        while self.is_running:
            try:
                # Check for pending executions
                execution = await self._get_next_execution()

                if execution:
                    # Execute the task graph
                    execution_id = execution["execution_id"]
                    logger.info(f"Dispatching execution {execution_id}")

                    # Run execution in background
                    task = asyncio.create_task(
                        self.execution_engine.execute_task_graph(
                            self.execution_engine._reconstruct_task_execution(execution),
                            execution_id
                        )
                    )
                    self.execution_engine.running_executions[execution_id] = task

                else:
                    # No pending executions, wait
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Dispatcher error: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        """Stop the task dispatcher"""
        self.is_running = False
        logger.info("Task dispatcher stopped")

    async def _get_next_execution(self) -> Optional[Dict[str, Any]]:
        """Get the next pending execution from the queue"""
        # Check Redis queue for pending executions
        execution_id = await self.redis.pop_from_queue("pending_executions")

        if execution_id:
            # Get full execution details from database
            return await self.db.get_task_execution(execution_id)

        return None

    async def queue_execution(self, execution_id: str):
        """Queue an execution for processing"""
        await self.redis.push_to_queue("pending_executions", execution_id)
        logger.info(f"Queued execution {execution_id}")
