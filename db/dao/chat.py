from datetime import date, timedelta, datetime

from aiogram.types import Chat as TgChat
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.dao.base import BaseDAO

from db.models import Chat

from logging import getLogger


logger = getLogger(__name__)


class ChatDAO(BaseDAO[Chat]):
    def __init__(self, session: AsyncSession):
        super().__init__(Chat, session)

    async def get_by_tg_id(self, tg_id: int) -> Chat:
        tg_id = int(tg_id)
        result = await self.session.execute(select(Chat).where(Chat.tg_id == tg_id))
        return result.scalar_one_or_none()

    async def get_create_or_update_chat(self, tg_chat: TgChat) -> Chat:
        chat = await self.get_by_tg_id(tg_chat.id)
        if not chat:
            return await self._save_new_chat(tg_chat)
        elif (
            chat.username != tg_chat.username
            or chat.title != tg_chat.title
            or chat.type != tg_chat.type
        ):
            chat = await self._upgrade_chat(tg_chat)
        return chat

    async def _upgrade_chat(self, tg_chat) -> Chat:
        update_stmt = (
            update(Chat)
            .where(Chat.tg_id == tg_chat.id)
            .values(
                username=tg_chat.username,
                title=tg_chat.title,
                type=tg_chat.type,
            )
            .returning(Chat)
        )
        result = await self.session.execute(update_stmt)
        return result.scalar_one_or_none()

    async def _save_new_chat(self, tg_chat: TgChat) -> Chat:
        """
        Create new chat
        """
        new_chat = Chat(
            tg_id=tg_chat.id,
            username=tg_chat.username,
            title=tg_chat.title,
            type=tg_chat.type,
        )
        self.session.add(new_chat)
        await self.session.flush()
        return new_chat
