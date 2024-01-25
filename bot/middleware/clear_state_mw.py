from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, Message


class ClearStateMiddleware(BaseMiddleware):
    """clear state if message text starts with /"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if event.text.startswith("/"):
            state: FSMContext = data["state"]
            await state.clear()
        return await handler(event, data)
