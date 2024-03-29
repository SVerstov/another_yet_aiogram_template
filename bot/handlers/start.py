from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from cache import Cache
from config import Config
from db import DAO, User, Chat

start_router = Router()


@start_router.message(F.text == "/start")
async def start(message: Message, config: Config):
    await message.answer("ok")


@start_router.message(F.text == "/test")
async def test(
    message: Message,
    config: Config,
    user: User,
    chat: Chat | None,
    dao: DAO,
    cache: Cache,
):
    await message.answer("ok")


@start_router.callback_query(F.data == "test")
async def simple_callback(call: CallbackQuery):
    await call.message.answer("call")


@start_router.message(F.text == "/user")
async def register_check(message: Message, dao: DAO, user: User):
    await message.answer(user.first_name)
