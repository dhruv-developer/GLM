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


class ExecutionEngine:
    """
    Task Graph Execution Engine
    Traverses the DAG, dispatches tasks to agents, and handles failures
    """

    def __init__(
        self,
        redis_service: RedisService,
        db_service: DatabaseService,
        controller: ControllerAgent
    ):
        self.redis = redis_service
        self.db = db_service
        self.controller = controller
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
        Execute a task graph end-to-end
        Returns the final result
        """
        logger.info(f"Starting execution for {execution_id}")
        graph = execution.task_graph

        # Update status
        await self._update_execution_status(execution_id, TaskStatus.RUNNING)
        await self._log_execution(
            execution_id,
            "Execution started",
            level="INFO"
        )

        try:
            # Main execution loop
            start_time = time.time()

            while not graph.is_complete():
                # Get ready tasks (dependencies satisfied)
                ready_tasks = graph.get_ready_tasks()

                if not ready_tasks:
                    # Check if we're stuck
                    if any(t.status == TaskStatus.RUNNING for t in graph.nodes.values()):
                        # Wait for running tasks to complete
                        await asyncio.sleep(1)
                        continue
                    else:
                        # No progress possible, likely an error
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

            await self._update_execution_status(execution_id, TaskStatus.COMPLETED)
            await self._log_execution(
                execution_id,
                f"Execution completed in {execution_time:.2f}s",
                level="INFO"
            )

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "tasks_executed": len(graph.nodes)
            }

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

        await self._log_execution(
            execution_id,
            f"Task {task.task_id} started with {task.agent.value}",
            level="INFO",
            task_id=task.task_id
        )

        try:
            # Dispatch to appropriate worker agent
            result = await self._dispatch_to_agent(task)

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

            # Attempt re-planning
            if task.retry_count < task.max_retries:
                logger.info(f"Attempting to re-plan for task {task.task_id}")
                new_graph = await self.controller.re_plan(graph, task.task_id, str(e))
                if new_graph:
                    # Update graph reference
                    graph = new_graph

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

        # Agent mapping
        agents = {
            AgentType.API: APIAgent(),
            AgentType.WEB_AUTOMATION: WebAutomationAgent(),
            AgentType.COMMUNICATION: CommunicationAgent(),
            AgentType.DATA: DataAgent(),
            AgentType.SCHEDULER: SchedulerAgent(),
            AgentType.VALIDATION: ValidationAgent(),
        }

        agent = agents.get(task.agent)
        if not agent:
            raise ValueError(f"Unknown agent type: {task.agent}")

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
                results[task_id] = {
                    "action": task.action,
                    "output": task.output,
                    "agent": task.agent.value
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
