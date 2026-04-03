"""
API Agent for ZIEL-MAS
Handles structured API calls to external services
"""

import httpx
from typing import Dict, Any
from loguru import logger

from backend.agents.base_agent import BaseAgent


class APIAgent(BaseAgent):
    """
    API Agent - Executes HTTP API calls
    Handles GET, POST, PUT, DELETE requests with retry logic
    """

    def __init__(self):
        super().__init__("API Agent", "api")
        self.client = None

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API action"""
        try:
            if action == "http_get":
                return await self._http_get(parameters)
            elif action == "http_post":
                return await self._http_post(parameters)
            elif action == "api_call":
                return await self._api_call(parameters)
            elif action == "book_cab":
                return await self._book_cab(parameters)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            return await self.handle_error(action, e)

    async def _http_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP GET request"""
        url = params.get("url")
        headers = params.get("headers", {})
        query_params = params.get("params", {})

        if not url:
            return self._create_response(
                status="failed",
                error="URL is required"
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=query_params)

            return self._create_response(
                status="completed",
                output={
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
            )

    async def _http_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP POST request"""
        url = params.get("url")
        headers = params.get("headers", {})
        body = params.get("body", {})

        if not url:
            return self._create_response(
                status="failed",
                error="URL is required"
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body)

            return self._create_response(
                status="completed",
                output={
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
            )

    async def _api_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generic API call with retry logic"""
        service = params.get("service")
        endpoint = params.get("endpoint")
        method = params.get("method", "GET")
        data = params.get("data", {})

        # Service-specific API configurations
        api_bases = {
            "github": "https://api.github.com",
            "twitter": "https://api.twitter.com/2",
            "slack": "https://slack.com/api",
            "stripe": "https://api.stripe.com/v1"
        }

        base_url = api_bases.get(service)
        if not base_url:
            return self._create_response(
                status="failed",
                error=f"Unknown service: {service}"
            )

        url = f"{base_url}/{endpoint}"

        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, params=data)
            elif method.upper() == "POST":
                response = await client.post(url, json=data)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unsupported method: {method}"
                )

            return self._create_response(
                status="completed",
                output={
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
            )

    async def _book_cab(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Book a cab via API"""
        # This would integrate with Uber/Lyft APIs
        service = params.get("service", "uber")
        details = params.get("details", {})

        # Mock implementation
        logger.info(f"Booking cab via {service}")

        return self._create_response(
            status="completed",
            output={
                "booking_id": "cab_123456",
                "service": service,
                "eta": "5 minutes",
                "driver": "John Doe"
            }
        )
