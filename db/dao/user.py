from datetime import date, timedelta, datetime

from aiogram.types import User as TgUser
from asyncpg import UniqueViolationError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.dao.base import BaseDAO

from db.models import User

from logging import getLogger


logger = getLogger(__name__)


class UserDAO(BaseDAO[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_tg_id(self, tg_id: int) -> User:
        tg_id = int(tg_id)
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()

    async def get_create_or_update_user(self, tg_user: TgUser) -> User:
        """
        Get or create a user based on Telegram info, updating any changed details.

        This method should only be used in Telegram handlers. It fetches or creates a
        user based on their Telegram ID, updating the user's details if needed.

        Returns:
            User: The updated or newly created user.

        Raises:
            EnvironmentError: If called outside a Telegram handler context.
        """
        user = await self.get_by_tg_id(tg_user.id)
        if not user:
            return await self._save_new_user(tg_user)
        elif (
            user.username != tg_user.username
            or user.first_name != tg_user.first_name
            or user.last_name != tg_user.last_name
        ):
            user = await self._upgrade_user(tg_user)
        return user

    async def _upgrade_user(self, tg_user) -> User:
        update_stmt = (
            update(User)
            .where(User.tg_id == tg_user.id)
            .values(
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
            )
            .returning(User)
        )
        result = await self.session.execute(update_stmt)
        await self.commit()
        return result.scalar_one_or_none()

    async def _save_new_user(self, tg_user) -> User:
        """create_new_user
        Create new user
        """
        user = User(
            tg_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )
        self.session.add(user)
        await self.commit()
        user.register_at_this_moment = True
        return user
