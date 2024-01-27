import os
from pathlib import Path

import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.methods import SendMessage
from sqlalchemy.ext.asyncio import create_async_engine

from config import Config
from tests.db.utils import create_tables, drop_all_tables
from tests.mocked_bot import MockedBot
from tests.utils import FakeUpdateMaker, get_expected_answer


# @pytest.mark.asyncio
# async def test_start(config: Config):
#     message = AsyncMock()
#     message.text = "/start"
#     await start(message)
#     message.answer.assert_called_with("ok")


# @pytest.mark.asyncio
# async def test_echo():
#     message = AsyncMock()
#     message.text = "any random text :-)"
#     await echo(message)
#     message.answer.assert_called_with(message.text)

@pytest.mark.skip
@pytest.mark.asyncio
async def test_dp_start(bot: MockedBot, dp: Dispatcher):
    update = FakeUpdateMaker(user_id=1234).message("/start")
    res = await get_expected_answer(bot, dp, update)
    assert isinstance(res, SendMessage)
    assert res.text == "ok"

@pytest.mark.skip
@pytest.mark.asyncio
async def test_dp_callback(bot: MockedBot, dp: Dispatcher):
    update = FakeUpdateMaker(user_id=1234).callback(callback_data="test")
    res = await get_expected_answer(bot, dp, update)
    assert isinstance(res, SendMessage)
    assert res.text == "call"

@pytest.mark.skip
class TestHandlers:
    config: Config = None
    id = 1

    @pytest_asyncio.fixture
    async def setup_method(self, request):
        if os.getcwd().endswith("/tests"):
            conf_path = Path("config/t_config.toml")
        else:
            conf_path = Path("tests/config/t_config.toml")
        self.config = Config(conf_path)
        self.engine = create_async_engine(self.config.db.uri)
        await create_tables(self.engine)

    @pytest.mark.asyncio
    async def test_user_check(bot: MockedBot, dp: Dispatcher):
        update = FakeUpdateMaker(user_id=1234, first_name="Gena").message("/user")
        res = await get_expected_answer(bot, dp, update)
        assert isinstance(res, SendMessage)
        assert res.text == "Gena"

    @pytest_asyncio.fixture
    async def teardown_method(self, method):
        await drop_all_tables(self.engine)
