from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import Config
from db import DAO


class ConfigMiddleware(BaseMiddleware):
    """Middleware that adds a DAO instance to all handlers."""

    def __init__(self, config: Config):
        self.config = config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if "config" not in data:
            data["config"] = self.config
        result = await handler(event, data)
        return result
