import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import DBConfig
from db import DAO
from db.base import Base


async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def make_dao(engine, db_conf: DBConfig):
    """Setup the DAO (Data Access Object) for the given engine."""

    sessionmaker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=db_conf.autoflush,
    )
    async with sessionmaker() as session:
        yield DAO(session)

