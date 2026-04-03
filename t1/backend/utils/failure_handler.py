"""
Failure Handler for ZIEL-MAS
Handles task failures, retries, and alternative execution strategies
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from backend.models.task import TaskNode, TaskStatus, TaskGraph


class FailureHandler:
    """
    Handles task failures with intelligent retry strategies
    Implements exponential backoff, alternative agent selection, and partial re-execution
    """

    def __init__(self):
        self.retry_strategies = {
            "exponential_backoff": self._exponential_backoff,
            "fixed_delay": self._fixed_delay,
            "immediate": self._immediate_retry,
            "alternative_agent": self._alternative_agent_retry
        }

    async def handle_failure(
        self,
        task: TaskNode,
        error: Exception,
        graph: TaskGraph,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Handle a task failure
        Determines if and how to retry the task
        """
        logger.error(f"Task {task.task_id} failed: {error}")

        # Check if retries are exhausted
        if retry_count >= task.max_retries:
            logger.error(f"Max retries exceeded for task {task.task_id}")
            return {
                "should_retry": False,
                "strategy": None,
                "reason": "max_retries_exceeded"
            }

        # Determine retry strategy based on error type
        strategy = self._determine_retry_strategy(error, retry_count)

        # Calculate retry delay
        delay = await self._calculate_retry_delay(strategy, retry_count)

        return {
            "should_retry": True,
            "strategy": strategy,
            "delay": delay,
            "retry_count": retry_count + 1
        }

    def _determine_retry_strategy(self, error: Exception, retry_count: int) -> str:
        """Determine the best retry strategy based on error type"""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Network/timeout errors -> exponential backoff
        if any(err in error_type.lower() for err in ["timeout", "connection", "network"]):
            return "exponential_backoff"

        # Rate limit errors -> longer delays
        if "rate limit" in error_message or "429" in error_message:
            return "fixed_delay"

        # Authentication errors -> try alternative agent
        if "auth" in error_message or "unauthorized" in error_message:
            return "alternative_agent"

        # Default to exponential backoff
        return "exponential_backoff"

    async def _calculate_retry_delay(self, strategy: str, retry_count: int) -> float:
        """Calculate delay before retry"""
        if strategy == "exponential_backoff":
            return await self._exponential_backoff(retry_count)
        elif strategy == "fixed_delay":
            return await self._fixed_delay(retry_count)
        elif strategy == "immediate":
            return await self._immediate_retry(retry_count)
        elif strategy == "alternative_agent":
            return 0  # No delay, switch agent immediately

        return 1.0  # Default 1 second delay

    async def _exponential_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff delay: 2^retry_count seconds"""
        delay = 2 ** retry_count
        max_delay = 60  # Cap at 60 seconds
        return min(delay, max_delay)

    async def _fixed_delay(self, retry_count: int) -> float:
        """Fixed delay regardless of retry count"""
        return 5.0  # 5 seconds

    async def _immediate_retry(self, retry_count: int) -> float:
        """No delay, immediate retry"""
        return 0.0

    async def _alternative_agent_retry(self, retry_count: int) -> float:
        """No delay when switching to alternative agent"""
        return 0.0


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures
    Stops calling failing services after threshold is reached
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.open_circuits: Dict[str, bool] = {}

    async def call(self, service_name: str, func, *args, **kwargs):
        """Execute a function with circuit breaker protection"""
        if self._is_circuit_open(service_name):
            raise Exception(f"Circuit breaker is open for {service_name}")

        try:
            result = await func(*args, **kwargs)
            self._reset_failures(service_name)
            return result
        except Exception as e:
            self._record_failure(service_name)
            if self._should_open_circuit(service_name):
                self._open_circuit(service_name)
            raise e

    def _is_circuit_open(self, service_name: str) -> bool:
        """Check if circuit is open for a service"""
        if not self.open_circuits.get(service_name, False):
            return False

        # Check if timeout has elapsed
        last_failure = self.last_failure_time.get(service_name)
        if last_failure:
            elapsed = (datetime.utcnow() - last_failure).total_seconds()
            if elapsed > self.timeout:
                # Close circuit after timeout
                self.open_circuits[service_name] = False
                return False

        return True

    def _record_failure(self, service_name: str):
        """Record a failure for a service"""
        self.failures[service_name] = self.failures.get(service_name, 0) + 1
        self.last_failure_time[service_name] = datetime.utcnow()

    def _reset_failures(self, service_name: str):
        """Reset failure count for a service"""
        self.failures[service_name] = 0
        self.open_circuits[service_name] = False

    def _should_open_circuit(self, service_name: str) -> bool:
        """Check if circuit should be opened"""
        return self.failures.get(service_name, 0) >= self.failure_threshold

    def _open_circuit(self, service_name: str):
        """Open circuit for a service"""
        self.open_circuits[service_name] = True
        logger.warning(f"Circuit breaker opened for {service_name}")


class RetryMiddleware:
    """
    Middleware for automatic retry logic
    Wraps function calls with retry capabilities
    """

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def execute_with_retry(
        self,
        func,
        *args,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        **kwargs
    ):
        """
        Execute a function with automatic retry logic
        """
        max_attempts = max_retries or self.max_retries
        backoff = backoff_factor or self.backoff_factor

        for attempt in range(max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_attempts - 1:
                    # Last attempt failed, raise the error
                    raise e

                # Calculate delay and wait
                delay = backoff ** attempt
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)

        # Should never reach here
        raise Exception("All retry attempts exhausted")


class GracefulDegradation:
    """
    Handles graceful degradation when services are unavailable
    Falls back to alternative implementations or cached results
    """

    def __init__(self):
        self.fallback_implementations: Dict[str, Any] = {}
        self.cache: Dict[str, Any] = {}

    def register_fallback(self, service_name: str, fallback_func):
        """Register a fallback implementation for a service"""
        self.fallback_implementations[service_name] = fallback_func

    async def execute_with_fallback(
        self,
        service_name: str,
        primary_func,
        *args,
        use_cache: bool = True,
        cache_ttl: int = 300,
        **kwargs
    ):
        """
        Execute a function with fallback support
        """
        # Check cache first
        cache_key = f"{service_name}:{args}:{kwargs}"
        if use_cache and cache_key in self.cache:
            logger.info(f"Using cached result for {service_name}")
            return self.cache[cache_key]

        try:
            # Try primary function
            result = await primary_func(*args, **kwargs)

            # Cache successful result
            if use_cache:
                self.cache[cache_key] = result

            return result

        except Exception as e:
            logger.warning(f"Primary function failed for {service_name}: {e}")

            # Try fallback
            if service_name in self.fallback_implementations:
                logger.info(f"Using fallback for {service_name}")
                fallback_result = await self.fallback_implementations[service_name](*args, **kwargs)

                # Cache fallback result
                if use_cache:
                    self.cache[cache_key] = fallback_result

                return fallback_result

            # No fallback available, raise the error
            raise e

    def clear_cache(self):
        """Clear the fallback cache"""
        self.cache.clear()
