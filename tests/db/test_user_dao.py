import pytest

from db import DAO
from aiogram.types import User as TgUser


@pytest.mark.asyncio
async def test_get_by_tg_id(dao_w_users: DAO):
    user = await dao_w_users.user.get_by_tg_id(55)
    assert user.tg_id == 55


@pytest.mark.asyncio
async def test_save_update_user_from_tg(dao):
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
