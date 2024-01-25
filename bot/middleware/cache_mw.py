from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from cache import Cache
from config import CacheConfig, Config
from db import DAO


class CacheMiddleware(BaseMiddleware):
    """Middleware that adds a Cache instance to all handlers."""

    def __init__(self, config: CacheConfig):
        self.cache = Cache(config)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["cache"] = self.cache
        return await handler(event, data)
