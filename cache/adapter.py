from redis.asyncio.client import Redis
from redis.commands.core import ResponseT

from config import CacheConfig


class Prefix:
    USER = "user"



class Cache:
    prefix = Prefix

    def __init__(self, cache_config: CacheConfig):
        self.config = cache_config
        self.redis = Redis(
            host=self.config.host,
            port=self.config.port,
            password=self.config.password,
            db=self.config.db_num,
            encoding="utf-8",
            decode_responses=True,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.redis.close()

    def add_prefix(self, key, prefix) -> str:
        if prefix:
            key = f"{prefix}:{key}"
        if self.config.key_autoprefix:
            # add app prefix
            key = f"{self.config.key_autoprefix}:{key}"
        return key

    async def set(self, key, value, prefix=None, ttl: int = None) -> bool:
        key = self.add_prefix(key, prefix)
        ttl = ttl or self.config.ttl
        return await self.redis.set(key, value, ex=ttl)

    async def get(self, key, prefix=None):
        key = self.add_prefix(key, prefix)
        return await self.redis.get(key)

    async def delete(self, *keys, prefix=None) -> int:
        keys = [self.add_prefix(key, prefix=prefix) for key in keys]
        return await self.redis.delete(*keys)

    async def exists(self, *keys, prefix=None) -> int:
        keys = [self.add_prefix(key, prefix=prefix) for key in keys]
        return await self.redis.exists(*keys)

    async def delete_by_prefix(self, prefix) -> int:
        """delete all keys starting with prefix"""
        keys_with_prefix = await self.redis.keys(
            self.add_prefix(key="*", prefix=prefix)
        )
        if keys_with_prefix:
            return await self.redis.delete(*keys_with_prefix)

    async def flush_all(self) -> ResponseT:
        return await self.redis.flushall()
