import abc
from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

cache: Redis | None = None


async def get_cache() -> Redis:
    return cache


class ConnectionCacheError(Exception):
    """Ошибка подключения к кэшу"""


class Cache(abc.ABC):
    """Абстрактное кэш хранилище."""

    @abc.abstractmethod
    async def get(self, key: str):
        """Получить состояние из хранилища."""

    @abc.abstractmethod
    async def put(self, key: str, value: str, ttl: int) -> None:
        """Сохранить состояние в хранилище."""


class RedisCache(Cache):
    """Кэш хранилище в Redis"""

    def __init__(self, redis_cache: Redis):
        self.redis_cache = redis_cache

    async def get(self, key: str) -> dict:
        """Получить состояние из хранилища."""
        try:
            value = await self.redis_cache.get(key)
        except ConnectionError:
            raise ConnectionCacheError
        return value

    async def put(self, key: str, value: str, ttl: int) -> None:
        """Сохранить состояние в хранилище."""

        await self.redis_cache.set(key, value, ttl)


@lru_cache()
def get_cache_service(
    cache: Redis = Depends(get_cache),
) -> RedisCache:
    return RedisCache(cache)
