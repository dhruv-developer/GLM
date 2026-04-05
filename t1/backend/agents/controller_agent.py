"""
Controller Worker Agent for ZIEL-MAS
Handles controller-type task actions (preparation and coordination tasks)
This is the *worker* agent for CONTROLLER tasks in the task graph.
Not to be confused with backend/core/controller.py (the orchestrator).
"""

from typing import Dict, Any
from datetime import datetime
from loguru import logger

from backend.agents.base_agent import BaseAgent


class ControllerWorkerAgent(BaseAgent):
    """
    Controller Worker Agent - Executes controller-type tasks in a task graph.
    Handles preparation and coordination tasks such as:
      - prepare_scheduled_task
      - prepare_message
      - prepare_booking
      - process_request
    """

    def __init__(self):
        super().__init__("Controller Worker Agent", "controller")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a controller action"""
        try:
            if action == "prepare_scheduled_task":
                return await self._prepare_scheduled_task(parameters)
            elif action == "prepare_message":
                return await self._prepare_message(parameters)
            elif action == "prepare_booking":
                return await self._prepare_booking(parameters)
            elif action == "process_request":
                return await self._process_request(parameters)
            elif action == "parse_search_query":
                return await self._parse_search_query(parameters)
            else:
                # Gracefully handle unknown controller actions
                logger.warning(f"Controller worker: unknown action '{action}', returning generic success")
                return self._create_response(
                    status="success",
                    output={
                        "action": action,
                        "message": f"Controller action '{action}' processed",
                        "parameters": parameters,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

        except Exception as e:
            return await self.handle_error(action, e)

    async def _prepare_scheduled_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a task for scheduling"""
        intent = params.get("intent", "")
        logger.info(f"Preparing scheduled task for intent: {intent}")

        return self._create_response(
            status="success",
            output={
                "intent": intent,
                "prepared_at": datetime.utcnow().isoformat(),
                "task_data": {
                    "type": "scheduled",
                    "description": intent,
                    "ready": True
                }
            }
        )

    async def _prepare_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare message content for communication"""
        intent = params.get("intent", "")
        entities = params.get("entities", {})
        logger.info(f"Preparing message for intent: {intent}")

        return self._create_response(
            status="success",
            output={
                "subject": f"Task: {intent[:50]}",
                "body": intent,
                "recipients": entities.get("emails", []),
                "prepared_at": datetime.utcnow().isoformat()
            }
        )

    async def _prepare_booking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare booking details"""
        intent = params.get("intent", "")
        logger.info(f"Preparing booking for intent: {intent}")

        return self._create_response(
            status="success",
            output={
                "booking_type": "general",
                "description": intent,
                "prepared_at": datetime.utcnow().isoformat(),
                "ready": True
            }
        )

    async def _process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a general request"""
        intent = params.get("intent", "")
        logger.info(f"Processing general request: {intent}")

        return self._create_response(
            status="success",
            output={
                "request": intent,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "processed",
                "message": f"Request processed successfully: {intent[:100]}"
            }
        )

    async def _parse_search_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and clean search query for web search"""
        intent = params.get("intent", "")
        logger.info(f"Original search intent: {intent}")
        
        # Clean the search query by removing emojis and quotes
        import re
        
        # Remove emojis
        cleaned_query = re.sub(r'[^\w\s\-.,!?()[\]{}"\'/:;@#$%^&*+=<>~`|\\]', '', intent)
        
        # Remove extra quotes and clean up whitespace
        cleaned_query = cleaned_query.replace('"', '').replace("'", "")
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        
        logger.info(f"Cleaned search query: {cleaned_query}")
        
        return self._create_response(
            status="success",
            output={
                "action": "parse_search_query",
                "message": "Controller action 'parse_search_query' processed",
                "parameters": {
                    "original_intent": intent,
                    "cleaned_query": cleaned_query,
                    "entities": params.get("entities", {})
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
