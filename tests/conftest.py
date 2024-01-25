import asyncio
import os
from pathlib import Path

import pytest_asyncio
from aiogram import Dispatcher
from aiogram.methods import SendMessage
from aiogram.types import Update
from sqlalchemy.ext.asyncio import create_async_engine

from bot.setup_bot import setup_dp
from config import Config

import pytest

from db import User, DAO
from tests.db.utils import create_tables, make_dao, drop_all_tables
from tests.mocked_bot import MockedBot


@pytest.fixture(scope="session", autouse=True)
def config() -> Config:
    if os.getcwd().endswith("/tests"):
        conf_path = Path("config/t_config.toml")
    else:
        conf_path = Path("tests/config/t_config.toml")
    return Config(conf_path)


@pytest_asyncio.fixture()
async def dao(config: Config) -> DAO:
    """Make a DB tables, clear Tables after tests.
    Return Data Access Object (DAO)."""
    engine = create_async_engine(config.db.uri)
    await create_tables(engine)
    try:
        async for dao in make_dao(engine, db_conf=config.db):
            yield dao

    finally:
        await drop_all_tables(engine)

@pytest_asyncio.fixture
async def dao_w_users(dao):
    """create 100 users with tg_id from 1 to 100"""
    for i in range(1, 101):
        new_user = User(tg_id=i)
        dao.session.add(new_user)
    await dao.session.commit()
    return dao


@pytest.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture(scope='session')
async def dp(config: Config):
    dp = setup_dp(config)

    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()
