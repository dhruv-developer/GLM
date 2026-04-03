"""
Scheduler Agent for ZIEL-MAS
Handles delayed and recurring task execution
"""

import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from backend.agents.base_agent import BaseAgent


class SchedulerAgent(BaseAgent):
    """
    Scheduler Agent - Manages task scheduling
    Handles one-time and recurring scheduled tasks
    """

    def __init__(self):
        super().__init__("Scheduler Agent", "scheduler")
        self.scheduled_tasks = {}

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a scheduling action"""
        try:
            if action == "schedule_once":
                return await self._schedule_once(parameters)
            elif action == "schedule_recurring":
                return await self._schedule_recurring(parameters)
            elif action == "cancel_schedule":
                return await self._cancel_schedule(parameters)
            elif action == "get_schedule":
                return await self._get_schedule(parameters)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            return await self.handle_error(action, e)

    async def _schedule_once(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a task for a specific time"""
        execute_at = params.get("execute_at")
        task = params.get("task")

        if not execute_at or not task:
            return self._create_response(
                status="failed",
                error="Execute time and task are required"
            )

        # Parse execute_at if it's a string
        if isinstance(execute_at, str):
            execute_at = datetime.fromisoformat(execute_at)

        schedule_id = f"schedule_{datetime.utcnow().timestamp()}"

        # Calculate delay
        now = datetime.utcnow()
        delay = (execute_at - now).total_seconds()

        if delay <= 0:
            return self._create_response(
                status="failed",
                error="Scheduled time must be in the future"
            )

        logger.info(f"Scheduling task for {execute_at} (in {delay}s)")

        # Schedule the task
        async def scheduled_task():
            await asyncio.sleep(delay)
            logger.info(f"Executing scheduled task {schedule_id}")
            # In production, this would trigger the actual task execution
            # For now, we just log it

        # Start the scheduled task in the background
        asyncio.create_task(scheduled_task())

        # Store reference
        self.scheduled_tasks[schedule_id] = {
            "execute_at": execute_at,
            "task": task,
            "type": "once"
        }

        return self._create_response(
            status="completed",
            output={
                "schedule_id": schedule_id,
                "execute_at": execute_at.isoformat(),
                "delay_seconds": delay
            }
        )

    async def _schedule_recurring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a recurring task using cron expression"""
        cron = params.get("cron")
        task = params.get("task")

        if not cron or not task:
            return self._create_response(
                status="failed",
                error="Cron expression and task are required"
            )

        schedule_id = f"recurring_{datetime.utcnow().timestamp()}"

        logger.info(f"Scheduling recurring task with cron: {cron}")

        # Store reference
        self.scheduled_tasks[schedule_id] = {
            "cron": cron,
            "task": task,
            "type": "recurring"
        }

        # In production, this would use a proper cron scheduler
        # For now, we just acknowledge the schedule

        return self._create_response(
            status="completed",
            output={
                "schedule_id": schedule_id,
                "cron": cron,
                "type": "recurring"
            }
        )

    async def _cancel_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a scheduled task"""
        schedule_id = params.get("schedule_id")

        if not schedule_id:
            return self._create_response(
                status="failed",
                error="Schedule ID is required"
            )

        if schedule_id in self.scheduled_tasks:
            del self.scheduled_tasks[schedule_id]
            logger.info(f"Cancelled schedule {schedule_id}")

            return self._create_response(
                status="completed",
                output={
                    "schedule_id": schedule_id,
                    "cancelled": True
                }
            )
        else:
            return self._create_response(
                status="failed",
                error=f"Schedule {schedule_id} not found"
            )

    async def _get_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a scheduled task"""
        schedule_id = params.get("schedule_id")

        if not schedule_id:
            return self._create_response(
                status="failed",
                error="Schedule ID is required"
            )

        schedule = self.scheduled_tasks.get(schedule_id)

        if schedule:
            return self._create_response(
                status="completed",
                output={
                    "schedule_id": schedule_id,
                    "schedule": schedule
                }
            )
        else:
            return self._create_response(
                status="failed",
                error=f"Schedule {schedule_id} not found"
            )
