"""
Cache Service for ZIEL-MAS
Redis-based caching and state management
"""

import json
import asyncio
from typing import Optional, Dict, Any, List, Set
from datetime import timedelta
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from loguru import logger


class RedisService:
    """
    Redis service for caching and state management
    Handles fast state tracking, task queues, and temporary data
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Establish Redis connection"""
        try:
            self.pool = ConnectionPool.from_url(self.redis_url, decode_responses=True)
            self.client = redis.Redis(connection_pool=self.pool)
            await self.client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()

    # State Management Methods

    async def set_task_status(self, execution_id: str, status: str, ttl: int = 86400):
        """Set task execution status"""
        key = f"task:{execution_id}:status"
        await self.client.setex(key, ttl, status)

    async def get_task_status(self, execution_id: str) -> Optional[str]:
        """Get task execution status"""
        key = f"task:{execution_id}:status"
        return await self.client.get(key)

    async def set_task_progress(self, execution_id: str, progress: float, ttl: int = 86400):
        """Set task execution progress (0.0 to 1.0)"""
        key = f"task:{execution_id}:progress"
        await self.client.setex(key, ttl, str(progress))

    async def get_task_progress(self, execution_id: str) -> Optional[float]:
        """Get task execution progress"""
        key = f"task:{execution_id}:progress"
        value = await self.client.get(key)
        return float(value) if value else None

    async def update_task_state(self, execution_id: str, state_data: Dict[str, Any], ttl: int = 86400):
        """Update task execution state"""
        key = f"task:{execution_id}:state"
        await self.client.hset(key, mapping={
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in state_data.items()
        })
        await self.client.expire(key, ttl)

    async def get_task_state(self, execution_id: str) -> Dict[str, Any]:
        """Get task execution state"""
        key = f"task:{execution_id}:state"
        data = await self.client.hgetall(key)
        return {
            k: json.loads(v) if v.startswith('{') or v.startswith('[') else v
            for k, v in data.items()
        }

    # Queue Management Methods

    async def push_to_queue(self, queue_name: str, item: Any):
        """Push item to a queue (FIFO)"""
        key = f"queue:{queue_name}"
        if isinstance(item, (dict, list)):
            item = json.dumps(item)
        await self.client.rpush(key, item)

    async def pop_from_queue(self, queue_name: str, timeout: int = 5) -> Optional[Any]:
        """Pop item from queue (blocking)"""
        key = f"queue:{queue_name}"
        result = await self.client.blpop(key, timeout=timeout)
        if result:
            _, value = result
            try:
                return json.loads(value)
            except:
                return value
        return None

    async def get_queue_length(self, queue_name: str) -> int:
        """Get queue length"""
        key = f"queue:{queue_name}"
        return await self.client.llen(key)

    async def clear_queue(self, queue_name: str):
        """Clear all items from a queue"""
        key = f"queue:{queue_name}"
        await self.client.delete(key)

    # Agent State Methods

    async def set_agent_status(self, agent_id: str, status: str, ttl: int = 3600):
        """Set agent status"""
        key = f"agent:{agent_id}:status"
        await self.client.setex(key, ttl, status)

    async def get_agent_status(self, agent_id: str) -> Optional[str]:
        """Get agent status"""
        key = f"agent:{agent_id}:status"
        return await self.client.get(key)

    async def assign_task_to_agent(self, agent_id: str, task_id: str):
        """Assign a task to an agent"""
        key = f"agent:{agent_id}:tasks"
        await self.client.sadd(key, task_id)

    async def remove_task_from_agent(self, agent_id: str, task_id: str):
        """Remove a task from an agent"""
        key = f"agent:{agent_id}:tasks"
        await self.client.srem(key, task_id)

    async def get_agent_tasks(self, agent_id: str) -> Set[str]:
        """Get all tasks assigned to an agent"""
        key = f"agent:{agent_id}:tasks"
        return await self.client.smembers(key)

    async def get_agent_task_count(self, agent_id: str) -> int:
        """Get number of tasks assigned to an agent"""
        key = f"agent:{agent_id}:tasks"
        return await self.client.scard(key)

    async def update_heartbeat(self, agent_id: str):
        """Update agent heartbeat"""
        key = f"agent:{agent_id}:heartbeat"
        await self.client.setex(key, 300, str(asyncio.get_event_loop().time()))

    async def check_agent_alive(self, agent_id: str) -> bool:
        """Check if agent is alive (recent heartbeat)"""
        key = f"agent:{agent_id}:heartbeat"
        heartbeat = await self.client.get(key)
        return heartbeat is not None

    # Token Management Methods

    async def store_token(self, token: str, execution_id: str, ttl: int = 86400):
        """Store execution token mapping"""
        key = f"token:{token}"
        await self.client.setex(key, ttl, execution_id)

    async def get_execution_id_from_token(self, token: str) -> Optional[str]:
        """Get execution ID from token"""
        key = f"token:{token}"
        return await self.client.get(key)

    async def invalidate_token(self, token: str):
        """Invalidate a token"""
        key = f"token:{token}"
        await self.client.delete(key)

    # Lock Management Methods (for distributed coordination)

    async def acquire_lock(self, lock_name: str, ttl: int = 60) -> bool:
        """Acquire a distributed lock"""
        key = f"lock:{lock_name}"
        return await self.client.set(key, "1", nx=True, ex=ttl)

    async def release_lock(self, lock_name: str):
        """Release a distributed lock"""
        key = f"lock:{lock_name}"
        await self.client.delete(key)

    # Cache Methods

    async def cache_get(self, cache_key: str) -> Optional[Any]:
        """Get value from cache"""
        value = await self.client.get(cache_key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None

    async def cache_set(self, cache_key: str, value: Any, ttl: int = 3600):
        """Set value in cache"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.client.setex(cache_key, ttl, value)

    async def cache_delete(self, cache_key: str):
        """Delete value from cache"""
        await self.client.delete(cache_key)

    # Pub/Sub Methods (for real-time updates)

    async def publish(self, channel: str, message: Any):
        """Publish message to channel"""
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        await self.client.publish(channel, message)

    async def subscribe(self, channel: str):
        """Subscribe to a channel (returns pubsub object)"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    # Statistics and Monitoring

    async def increment_counter(self, counter_name: str, amount: int = 1):
        """Increment a counter"""
        key = f"counter:{counter_name}"
        return await self.client.incrby(key, amount)

    async def get_counter(self, counter_name: str) -> int:
        """Get counter value"""
        key = f"counter:{counter_name}"
        value = await self.client.get(key)
        return int(value) if value else 0

    async def reset_counter(self, counter_name: str):
        """Reset counter to zero"""
        key = f"counter:{counter_name}"
        await self.client.delete(key)

    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server info"""
        info = await self.client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            "total_commands_processed": info.get("total_commands_processed", 0)
        }
