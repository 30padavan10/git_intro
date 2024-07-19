from functools import lru_cache
from fastapi import Depends
from redis.asyncio import Redis

redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis


@lru_cache()
def get_redis_service(
    redis: Redis = Depends(get_redis),
) -> RedisService:
    return RedisService(redis)
