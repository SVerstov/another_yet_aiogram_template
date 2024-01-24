import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import Config
from tests.db.utils import create_tables, drop_all_tables


@pytest_asyncio.fixture(autouse=True)
async def create_db(config: Config):
    engine = create_async_engine(config.db.uri)
    await create_tables(engine)
    yield
    engine = create_async_engine(config.db.uri)
    await drop_all_tables(engine)
