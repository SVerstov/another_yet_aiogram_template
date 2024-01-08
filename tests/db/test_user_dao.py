import pytest

from db.dao import DAO
from db.models import User
from tests.db.conftest import dao
from aiogram.types import User as TgUser
import pytest_asyncio


@pytest_asyncio.fixture
async def users_dao(dao):
    """ create 100 users with tg_id from 1 to 100"""
    for i in range(1, 101):
        new_user = User(tg_id=i)
        dao.session.add(new_user)
    await dao.session.commit()
    return dao


class TestUserDao:
    @pytest.mark.asyncio
    async def test_save_and_get_user(self, dao: DAO) -> None:
        new_user = User(tg_id=123456)
        dao.session.add(new_user)
        await dao.commit()
        user = await dao.user.get_by_tg_id(123456)
        assert user.tg_id == 123456

    @pytest.mark.asyncio
    async def test_count(self, users_dao: DAO):
        users_count = await users_dao.user.count()
        assert users_count == 100

    @pytest.mark.asyncio
    async def test_save_update_user_from_tg(self, dao):
        tg_obj = TgUser(id=999, is_bot=False, first_name="John", last_name="Snow")
        user = await dao.user.get_create_or_update_user(tg_obj)

        assert user.tg_id == 999
        assert isinstance(user.id, int)
        assert user.first_name == "John"
        assert user.last_name == "Snow"
        user_id = user.id

        tg_obj = TgUser(id=999, is_bot=False, first_name="John", last_name="Targaryen")
        user = await dao.user.get_create_or_update_user(tg_obj)
        assert user_id == user.id  # id mustn't change
        assert user.last_name == "Targaryen"

    @pytest.mark.asyncio
    async def test_get_many_with_sort(self, users_dao: DAO):
        users = await users_dao.user.get_many(order_by=User.tg_id)
        assert users[-1].tg_id > users[0].tg_id
        users = await users_dao.user.get_many(order_by=-User.tg_id)
        assert users[-1].tg_id < users[0].tg_id

    @pytest.mark.asyncio
    async def test_get_chunk_iterator(self, users_dao: DAO):
        user_chunks = users_dao.user.get_chunk_iterator(User.tg_id > 10, chunk_size=10)
        count = 0
        async for chunk in user_chunks:
            assert len(chunk) == 10
            count += len(chunk)
        assert count == 90

        user_chunks = users_dao.user.get_chunk_iterator(offset=50, chunk_size=5)
        count = 0
        async for chunk in user_chunks:
            assert len(chunk) == 5
            count += len(chunk)
        assert count == 50

    @pytest.mark.asyncio
    async def test_get_last_elem(self, users_dao: DAO):
        user = await users_dao.user.get_last_elem()
        assert user.tg_id == 100


    @pytest.mark.asyncio
    async def test_get_one(self, users_dao: DAO):
        user = await users_dao.user.get_one(User.tg_id==50)
        assert user.tg_id == 50

        user = await users_dao.user.get_one(User.tg_id==150)
        assert user is None