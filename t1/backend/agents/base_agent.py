"""
Base Agent Class for ZIEL-MAS
All worker agents inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
from loguru import logger


class BaseAgent(ABC):
    """
    Base class for all worker agents
    Provides common functionality and enforces agent interface
    """

    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self.is_active = True

    @abstractmethod
    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific action with given parameters
        Must be implemented by each agent
        """
        pass

    async def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for an action
        Override in subclasses for specific validation
        """
        return True

    async def handle_error(self, action: str, error: Exception) -> Dict[str, Any]:
        """
        Handle errors during execution
        Can be overridden for custom error handling
        """
        logger.error(f"{self.name} error during {action}: {error}")
        return {
            "status": "failed",
            "error": str(error),
            "agent": self.agent_type
        }

    def _create_response(
        self,
        status: str,
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a standardized response"""
        response = {
            "status": status,
            "agent": self.agent_type,
            "metadata": metadata or {}
        }

        if output:
            response["output"] = output
        if error:
            response["error"] = error

        return response
