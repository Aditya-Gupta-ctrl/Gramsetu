"""
Redis client wrapper for job queue and caching
Used by all services for async communication
"""
import redis.asyncio as redis
from typing import Optional, Any
import json
from shared.config import get_settings
from shared.logging_config import logger

settings = get_settings()


class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Establish Redis connection"""
        self.client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Redis connection established")
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def set_json(self, key: str, value: Any, expire: Optional[int] = None):
        """Store JSON-serializable value"""
        json_str = json.dumps(value)
        await self.client.set(key, json_str, ex=expire)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Retrieve JSON value"""
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def publish(self, channel: str, message: dict):
        """Publish message to channel"""
        await self.client.publish(channel, json.dumps(message))
    
    async def enqueue_job(self, queue_name: str, job_data: dict):
        """Add job to queue"""
        await self.client.rpush(queue_name, json.dumps(job_data))
        logger.info(f"Job enqueued to {queue_name}", job_id=job_data.get("job_id"))
    
    async def dequeue_job(self, queue_name: str, timeout: int = 5) -> Optional[dict]:
        """Pop job from queue (blocking)"""
        result = await self.client.blpop(queue_name, timeout=timeout)
        if result:
            _, job_json = result
            return json.loads(job_json)
        return None


# Global instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency injection for FastAPI"""
    if not redis_client.client:
        await redis_client.connect()
    return redis_client
