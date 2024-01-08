from typing import Any

from sqlalchemy import Executable, Result, text
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from .base import BaseDAO

from .user import UserDAO


class DAO:
    """The main DAO. Plug models dao here"""

    def __init__(self, session: AsyncSession):
        self.session = session

        self.user = UserDAO(session)

    async def commit(self):
        await self.session.commit()

    async def execute(self, stmt: Executable) -> Result[Any]:
        return await self.session.execute(stmt)

    async def execute_raw_sql(self, sql: str) -> Result[Any]:
        return await self.session.execute(text(sql))


__all__ = [BaseDAO, DAO]
