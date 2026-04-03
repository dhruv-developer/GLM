"""
Data Agent for ZIEL-MAS
Fetches, filters, and ranks data from various sources
"""

import httpx
from typing import Dict, Any, List
from loguru import logger

from backend.agents.base_agent import BaseAgent


class DataAgent(BaseAgent):
    """
    Data Agent - Processes and transforms data
    Handles fetching, filtering, ranking, and transformation
    """

    def __init__(self):
        super().__init__("Data Agent", "data")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data processing action"""
        try:
            if action == "fetch_data":
                return await self._fetch_data(parameters)
            elif action == "filter_data":
                return await self._filter_data(parameters)
            elif action == "rank_data":
                return await self._rank_data(parameters)
            elif action == "transform_data":
                return await self._transform_data(parameters)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            return await self.handle_error(action, e)

    async def _fetch_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from API or database"""
        source = params.get("source")
        query = params.get("query", {})

        if not source:
            return self._create_response(
                status="failed",
                error="Data source is required"
            )

        logger.info(f"Fetching data from {source}")

        # Mock implementation - would connect to real APIs
        if source == "api":
            # Fetch from REST API
            url = query.get("url")
            if url:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    data = response.json()

                    return self._create_response(
                        status="completed",
                        output={
                            "data": data,
                            "count": len(data) if isinstance(data, list) else 1
                        }
                    )

        elif source == "database":
            # Fetch from database
            # In production, this would query MongoDB/PostgreSQL/etc.
            return self._create_response(
                status="completed",
                output={
                    "data": [{"id": 1, "name": "Item 1"}],
                    "count": 1
                }
            )

        # Default mock response
        return self._create_response(
            status="completed",
            output={
                "data": [{"id": 1, "name": "Sample Data"}],
                "count": 1
            }
        )

    async def _filter_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data based on criteria"""
        data = params.get("data", [])
        filters = params.get("filters", {})

        if not data:
            return self._create_response(
                status="failed",
                error="Data is required for filtering"
            )

        logger.info(f"Filtering {len(data)} items")

        # Apply filters
        filtered_data = data
        for key, value in filters.items():
            if isinstance(value, dict):
                # Handle operators like $gt, $lt, etc.
                if "$gt" in value:
                    filtered_data = [item for item in filtered_data if item.get(key, 0) > value["$gt"]]
                elif "$lt" in value:
                    filtered_data = [item for item in filtered_data if item.get(key, 0) < value["$lt"]]
                elif "$in" in value:
                    filtered_data = [item for item in filtered_data if item.get(key) in value["$in"]]
            else:
                # Exact match
                filtered_data = [item for item in filtered_data if item.get(key) == value]

        return self._create_response(
            status="completed",
            output={
                "data": filtered_data,
                "original_count": len(data),
                "filtered_count": len(filtered_data)
            }
        )

    async def _rank_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rank items based on scoring function"""
        data = params.get("data", [])
        scoring_function = params.get("scoring_function", "default")
        sort_order = params.get("sort_order", "desc")

        if not data:
            return self._create_response(
                status="failed",
                error="Data is required for ranking"
            )

        logger.info(f"Ranking {len(data)} items using {scoring_function}")

        # Apply scoring
        if scoring_function == "default":
            # Simple scoring based on item properties
            scored_data = []
            for item in data:
                score = sum(
                    isinstance(v, (int, float))
                    for v in item.values()
                )
                scored_data.append({**item, "_score": score})

            # Sort
            reverse = sort_order == "desc"
            ranked_data = sorted(scored_data, key=lambda x: x.get("_score", 0), reverse=reverse)

            return self._create_response(
                status="completed",
                output={
                    "data": ranked_data,
                    "count": len(ranked_data)
                }
            )

        return self._create_response(
            status="completed",
            output={"data": data, "count": len(data)}
        )

    async def _transform_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data structure"""
        data = params.get("data")
        transformation = params.get("transformation")

        if not data:
            return self._create_response(
                status="failed",
                error="Data is required for transformation"
            )

        logger.info(f"Applying transformation: {transformation}")

        transformed_data = data

        # Apply transformations
        if transformation == "lowercase":
            if isinstance(data, list) and all(isinstance(item, str) for item in data):
                transformed_data = [item.lower() for item in data]
        elif transformation == "uppercase":
            if isinstance(data, list) and all(isinstance(item, str) for item in data):
                transformed_data = [item.upper() for item in data]
        elif transformation == "extract_keys":
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                keys = params.get("keys", [])
                transformed_data = [{k: item.get(k) for k in keys} for item in data]

        return self._create_response(
            status="completed",
            output={
                "data": transformed_data,
                "transformation": transformation
            }
        )
