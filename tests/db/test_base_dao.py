import pytest

from db.dao import DAO
from db.models import User
from tests.conftest import dao


@pytest.mark.asyncio
async def test_save_and_get_user(dao: DAO) -> None:
    new_user = User(tg_id=123456)
    dao.session.add(new_user)
    await dao.commit()
    user = await dao.user.get_by_tg_id(123456)
    assert user.tg_id == 123456


@pytest.mark.asyncio
async def test_count(dao_w_users: DAO):
    users_count = await dao_w_users.user.count()
    assert users_count == 100


@pytest.mark.asyncio
async def test_get_many(dao_w_users: DAO):
    users = await dao_w_users.user.get_many(
        User.tg_id > 10, order_by=User.tg_id, offset=10
    )
    assert users[-1].tg_id > users[0].tg_id
    assert len(users) == 80
    assert users[0].tg_id == 21

    users = await dao_w_users.user.get_many(order_by=-User.tg_id)
    users2 = await dao_w_users.user.get_many(order_by=User.tg_id.desc())
    assert users == users2
    assert users[-1].tg_id < users[0].tg_id


@pytest.mark.asyncio
async def test_get_chunk_iterator(dao_w_users: DAO):
    user_chunks = dao_w_users.user.get_chunk_iterator(User.tg_id > 10, chunk_size=10)
    count = 0
    async for chunk in user_chunks:
        assert len(chunk) == 10
        count += len(chunk)
        assert isinstance(chunk[0], User)
    assert count == 90


    # test with offset
    user_chunks = dao_w_users.user.get_chunk_iterator(offset=50, chunk_size=5)
    count = 0
    async for chunk in user_chunks:
        assert len(chunk) == 5
        count += len(chunk)
    assert count == 50


@pytest.mark.asyncio
async def test_get_last_elem(dao_w_users: DAO):
    user = await dao_w_users.user.get_last()
    assert user.tg_id == 100

    user = await dao_w_users.user.get_last(order_by=-User.id)
    assert user.tg_id == 1


@pytest.mark.asyncio
async def test_get_first(dao_w_users: DAO):
    user = await dao_w_users.user.get_first(User.tg_id >= 50, order_by=User.tg_id)
    assert user.tg_id == 50

    user = await dao_w_users.user.get_first(order_by=-User.tg_id)
    assert user.id == 100

    user = await dao_w_users.user.get_first(User.tg_id == 150)
    assert user is None


@pytest.mark.asyncio
async def test_deleted(dao_w_users: DAO):
    del_count = await dao_w_users.user.delete(User.tg_id >= 10, User.tg_id < 20)
    assert del_count == 10


@pytest.mark.asyncio
async def test_autoflush_effect(dao: DAO):
    dao.session.autoflush = True
    new_user = User(tg_id=1000, first_name="Test2")
    dao.session.add(new_user)
    user = await dao.user.get_by_tg_id(1000)
    assert user is not None

    dao.session.autoflush = False
    new_user = User(tg_id=999, first_name="Test")
    dao.session.add(new_user)
    user = await dao.user.get_by_tg_id(999)
    assert user is None

    new_user = User(tg_id=1001, first_name="Test3")
    dao.session.add(new_user)
    assert new_user.id is None
    await dao.flush()
    assert new_user.id is not None
