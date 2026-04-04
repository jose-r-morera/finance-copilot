import json
from typing import Any

import structlog
from redis.asyncio import Redis, from_url  # type: ignore

from backend.app.core.config import settings

logger = structlog.get_logger(__name__)


class RedisService:
    """
    Asynchronous Redis client for caching API responses and agent state.
    """

    def __init__(self, url: str) -> None:
        self.url = url
        self._redis: Redis | None = None

    async def get_client(self) -> Redis:
        if self._redis is None:
            logger.info("Initializing async Redis client", url=self.url)
            self._redis = from_url(self.url, decode_responses=True)
        return self._redis

    async def get(self, key: str) -> Any | None:
        """Retrieve and deserialize JSON data from Redis."""
        try:
            client = await self.get_client()
            data = await client.get(key)
            if data:
                logger.debug("Cache HIT", key=key)
                return json.loads(data)
            logger.debug("Cache MISS", key=key)
            return None
        except Exception as e:
            logger.error("Redis GET failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, expire: int = 86400) -> bool:
        """Serialize and store data in Redis with an expiration (default 24h)."""
        try:
            client = await self.get_client()
            serialized_value = json.dumps(value)
            await client.set(key, serialized_value, ex=expire)
            logger.debug("Cache SET", key=key, expire=expire)
            return True
        except Exception as e:
            logger.error("Redis SET failed", key=key, error=str(e))
            return False

    async def clear(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            client = await self.get_client()
            await client.delete(key)
            logger.debug("Cache CLEAR", key=key)
            return True
        except Exception as e:
            logger.error("Redis CLEAR failed", key=key, error=str(e))
            return False


# Global instance for easy injection
redis_service = RedisService(settings.REDIS_URL)
