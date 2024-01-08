import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import DBConfig
from db.base import Base
from db.dao import DAO

TEST_DAO_SET = ["sqlite_dao", "postgres_dao"]

sqlite_conf = {
    "type": "sqlite",
    "name": ":memory:",
}

postgres_conf = {
    "type": "postgresql",
    "connector": "asyncpg",
    "login": "postgres",
    "password": "020390",
    "host_and_port": "192.168.0.12:5433",
    "name": "test_db",
}


@pytest.fixture(params=TEST_DAO_SET)
def dao(request) -> DAO:
    """ DAO pytest fixture for several DBases """
    return request.getfixturevalue(request.param)


@pytest_asyncio.fixture
async def sqlite_dao() -> DAO:
    """Make an SQLite Data Access Object (DAO)."""
    db_conf = DBConfig.model_validate(sqlite_conf)

    async_engine = create_async_engine(db_conf.uri)
    await create_tables(async_engine)
    async for dao in setup_dao(async_engine):
        yield dao


@pytest_asyncio.fixture
async def postgres_dao() -> DAO:
    """Make an POSTGRES Data Access Object (DAO)."""
    db_conf = DBConfig.model_validate(postgres_conf)
    async_engine = create_async_engine(db_conf.uri)
    await create_tables(async_engine)
    async for dao in setup_dao(async_engine):
        yield dao
    await drop_all_tables(async_engine)


async def create_tables(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def setup_dao(async_engine):
    """Setup the DAO (Data Access Object) for the given async_engine."""
    async_session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with async_session_factory() as session:
        yield DAO(session)
