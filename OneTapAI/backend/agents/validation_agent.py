"""
Validation Agent for ZIEL-MAS
Verifies correctness of outputs and results
"""

import json
from typing import Dict, Any, List
from loguru import logger

from backend.agents.base_agent import BaseAgent


class ValidationAgent(BaseAgent):
    """
    Validation Agent - Validates outputs and results
    Ensures correctness and consistency
    """

    def __init__(self):
        super().__init__("Validation Agent", "validation")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a validation action"""
        try:
            if action == "validate_output":
                return await self._validate_output(parameters)
            elif action == "verify_result":
                return await self._verify_result(parameters)
            elif action == "sanity_check":
                return await self._sanity_check(parameters)
            elif action == "verify_delivery":
                return await self._verify_delivery(parameters)
            elif action == "verify_submission":
                return await self._verify_submission(parameters)
            elif action == "verify_booking":
                return await self._verify_booking(parameters)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            return await self.handle_error(action, e)

    async def _validate_output(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output against a schema"""
        output = params.get("output")
        schema = params.get("schema", {})

        if not output:
            return self._create_response(
                status="failed",
                error="Output is required for validation"
            )

        logger.info("Validating output against schema")

        # Simple schema validation
        is_valid = True
        errors = []

        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in output:
                is_valid = False
                errors.append(f"Missing required field: {field}")

        # Check types
        type_schema = schema.get("types", {})
        for field, expected_type in type_schema.items():
            if field in output:
                if expected_type == "string" and not isinstance(output[field], str):
                    is_valid = False
                    errors.append(f"Field {field} should be string")
                elif expected_type == "number" and not isinstance(output[field], (int, float)):
                    is_valid = False
                    errors.append(f"Field {field} should be number")
                elif expected_type == "array" and not isinstance(output[field], list):
                    is_valid = False
                    errors.append(f"Field {field} should be array")

        return self._create_response(
            status="success",
            output={
                "is_valid": is_valid,
                "errors": errors
            }
        )

    async def _verify_result(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify result meets criteria"""
        result = params.get("result")
        criteria = params.get("criteria", {})

        if not result:
            return self._create_response(
                status="failed",
                error="Result is required for verification"
            )

        logger.info("Verifying result against criteria")

        # Verify criteria
        checks_passed = []
        checks_failed = []

        # Check if result is not empty
        if criteria.get("not_empty", False):
            if result:
                checks_passed.append("Result is not empty")
            else:
                checks_failed.append("Result is empty")

        # Check if result contains expected values
        if "contains" in criteria:
            for item in criteria["contains"]:
                if item in str(result):
                    checks_passed.append(f"Contains {item}")
                else:
                    checks_failed.append(f"Does not contain {item}")

        # Check numeric criteria
        if "min_value" in criteria:
            if isinstance(result, (int, float)) and result >= criteria["min_value"]:
                checks_passed.append(f"Value >= {criteria['min_value']}")
            else:
                checks_failed.append(f"Value < {criteria['min_value']}")

        return self._create_response(
            status="success",
            output={
                "verified": len(checks_failed) == 0,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed
            }
        )

    async def _sanity_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sanity check on output"""
        output = params.get("output")
        checks = params.get("checks", [])

        logger.info("Performing sanity checks")

        results = []

        for check in checks:
            if check == "not_null":
                passed = output is not None
                results.append({"check": check, "passed": passed})
            elif check == "not_empty":
                passed = len(output) > 0 if isinstance(output, (list, dict, str)) else True
                results.append({"check": check, "passed": passed})
            elif check == "has_keys":
                passed = isinstance(output, dict) and len(output.keys()) > 0
                results.append({"check": check, "passed": passed})
            elif check == "is_json":
                try:
                    json.dumps(output)
                    passed = True
                except:
                    passed = False
                results.append({"check": check, "passed": passed})

        all_passed = all(r["passed"] for r in results)

        return self._create_response(
            status="success",
            output={
                "all_checks_passed": all_passed,
                "results": results
            }
        )

    async def _verify_delivery(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify message delivery"""
        # Mock implementation
        logger.info("Verifying message delivery")

        return self._create_response(
            status="success",
            output={
                "delivered": True,
                "delivery_time": "2024-01-01T00:00:00Z",
                "recipient": "verified@example.com"
            }
        )

    async def _verify_submission(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify form submission"""
        # Mock implementation
        logger.info("Verifying form submission")

        return self._create_response(
            status="success",
            output={
                "submitted": True,
                "submission_id": "sub_123456",
                "confirmation": "Application submitted successfully"
            }
        )

    async def _verify_booking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify booking confirmation"""
        # Mock implementation
        logger.info("Verifying booking")

        return self._create_response(
            status="success",
            output={
                "booked": True,
                "booking_id": "book_123456",
                "confirmation": "Booking confirmed"
            }
        )
