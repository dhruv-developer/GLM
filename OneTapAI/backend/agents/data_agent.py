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
            elif action == "aggregate_data":
                return await self._aggregate_data(parameters)
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
                        status="success",
                        output={
                            "data": data,
                            "count": len(data) if isinstance(data, list) else 1
                        }
                    )

        elif source == "database":
            # Fetch from database
            # In production, this would query MongoDB/PostgreSQL/etc.
            return self._create_response(
                status="success",
                output={
                    "data": [{"id": 1, "name": "Item 1"}],
                    "count": 1
                }
            )

        # Default mock response
        return self._create_response(
            status="success",
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
            status="success",
            output=filtered_data
        )

    async def _rank_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rank items based on scoring function or specific field"""
        data = params.get("data", [])
        scoring_function = params.get("scoring_function", "default")
        sort_order = params.get("sort_order", params.get("order", "desc"))
        rank_by = params.get("rank_by")

        if not data:
            return self._create_response(
                status="failed",
                error="Data is required for ranking"
            )

        logger.info(f"Ranking {len(data)} items using {scoring_function}")

        # Apply scoring
        if scoring_function == "default":
            # Check if ranking by specific field
            if rank_by and rank_by in data[0]:
                # Sort by the specified field
                reverse = sort_order == "desc"
                ranked_data = sorted(data, key=lambda x: x.get(rank_by, 0), reverse=reverse)
            else:
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
                status="success",
                output=ranked_data
            )

        return self._create_response(
            status="success",
            output=data
        )

    async def _aggregate_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data by grouping and applying operations"""
        data = params.get("data")
        group_by = params.get("group_by")
        operations = params.get("operations")

        if not data:
            return self._create_response(
                status="failed",
                error="Data is required for aggregation"
            )

        if not group_by:
            return self._create_response(
                status="failed",
                error="Group by field is required"
            )

        logger.info(f"Aggregating data by {group_by}")

        # Group data
        grouped = {}
        for item in data:
            key = item.get(group_by)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)

        # Apply operations
        result = []
        for group_key, group_items in grouped.items():
            group_result = {"group": group_key}

            if operations:
                for op_name, field in operations.items():
                    if op_name == "sum":
                        group_result[f"{field}_sum"] = sum(item.get(field, 0) for item in group_items)
                    elif op_name == "avg":
                        values = [item.get(field, 0) for item in group_items]
                        group_result[f"{field}_avg"] = sum(values) / len(values) if values else 0
                    elif op_name == "count":
                        group_result["count"] = len(group_items)
                    elif op_name == "min":
                        group_result[f"{field}_min"] = min(item.get(field, 0) for item in group_items)
                    elif op_name == "max":
                        group_result[f"{field}_max"] = max(item.get(field, 0) for item in group_items)

            result.append(group_result)

        return self._create_response(
            status="success",
            output={
                "data": result,
                "grouped_by": group_by
            }
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
            status="success",
            output={
                "data": transformed_data,
                "transformation": transformation
            }
        )
