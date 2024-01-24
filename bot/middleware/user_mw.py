from datetime import date
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db import DAO, User


class UserMiddleware(BaseMiddleware):
    """add User to middleware"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        dao: DAO = data.get("dao")
        tg_user = data["event_from_user"]
        user = await dao.user.get_create_or_update_user(tg_user)
        self.collect_stats(user)
        data["user"] = user
        result = await handler(event, data)
        return result

    def collect_stats(self, user: User):
        if user.is_bot_blocked:
            user.is_bot_blocked = False
        if user.last_active_at != date.today():
            user.last_active_at = date.today()
