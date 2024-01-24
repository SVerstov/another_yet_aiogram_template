import traceback

from aiogram import Bot, Dispatcher, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import ErrorEvent, Update
from aiogram_dialog import DialogManager
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import close_all_sessions

from bot.middleware.chat_mw import ChatMiddleware
from bot.middleware.user_mw import UserMiddleware
from bot.start import start_router
from config import BotConfig, Config
from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, ReplyKeyboardMarkup
from bot.middleware.config_mw import ConfigMiddleware
from bot.middleware.dao_mw import DaoMiddleware


def setup_routers(dp):
    dp.include_routers(start_router)


def setup_middleware(dp, config):
    engine = create_async_engine(config.db.uri)
    sessionmaker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=config.db.autoflush,
    )
    dp.update.middleware(DaoMiddleware(sessionmaker))
    dp.update.middleware(UserMiddleware())
    dp.update.middleware(ChatMiddleware())
    dp.update.middleware(ConfigMiddleware(config))


def setup_dp(config: Config) -> Dispatcher:
    dp = Dispatcher(storage=get_redis_storage(config))

    setup_middleware(dp, config)

    setup_routers(dp)
    return dp


def run_bot(config: Config):
    bot = Bot(
        token=config.bot.token,
        parse_mode=config.bot.parse_mode,
    )
    dp = setup_dp(config)

    try:
        dp.run_polling(bot)
    finally:
        close_all_sessions()
        logger.info("Bot stopped")


def get_redis_storage(config):
    redis = Redis(
        host=config.cache.host,
        port=config.cache.port,
        db=config.cache.db_num_bot,
        password=config.cache.password,
    )
    return RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))
