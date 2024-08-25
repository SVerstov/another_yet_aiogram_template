# import pytest
# import pytest_asyncio
# from sqlalchemy.ext.asyncio import create_async_engine
#
# from config import DBConfig
# from db import DAO
# from tests.db.utils import create_tables, make_dao
#
# TEST_DAO_SET = ["sqlite_dao", "postgres_dao"]
#
# sqlite_conf = {
#     "type": "sqlite",
#     "name": ":memory:",
# }
#
# postgres_conf = {
#     "type": "postgresql",
#     "connector": "asyncpg",
#     "login": "postgres",
#     "password": "020390",
#     "autoflush": False,
#     "host_and_port": "192.168.0.12:5433",
#     "name": "test_db",
# }
#
#
# @pytest.fixture(params=TEST_DAO_SET)
# def dao(request) -> DAO:
#     """DAO pytest fixture for several DBases"""
#     return request.getfixturevalue(request.param)
#
#
# @pytest_asyncio.fixture
# async def sqlite_dao() -> DAO:
#     """Make an SQLite Data Access Object (DAO)."""
#     db_conf = DBConfig.model_validate(sqlite_conf)
#
#     engine = create_async_engine(db_conf.uri)
#     await create_tables(engine)
#     async for dao in make_dao(engine, db_conf=db_conf):
#         yield dao
#
#
