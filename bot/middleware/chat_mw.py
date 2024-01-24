from datetime import date
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db import DAO, Chat


class ChatMiddleware(BaseMiddleware):
    """add chat to middleware if chat id < 0,
    else add chat=None"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        dao: DAO = data.get("dao")
        tg_chat = data["event_chat"]
        if tg_chat.id < 0:
            chat = await dao.chat.get_create_or_update_user(tg_chat)
            self.collect_stats(tg_chat)
        else:
            chat = None
        data["chat"] = chat
        result = await handler(event, data)
        return result

    def collect_stats(self, chat: Chat):
        if chat.is_bot_blocked:
            chat.is_bot_blocked = False
        if chat.last_active_at != date.today():
            chat.last_active_at = date.today()
