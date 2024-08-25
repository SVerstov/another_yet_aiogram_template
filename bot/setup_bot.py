from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import close_all_sessions

from bot.handlers.start import start_router
from bot.middleware.cache_mw import CacheMiddleware
from bot.middleware.chat_mw import ChatMiddleware
from bot.middleware.clear_state_mw import ClearStateMiddleware
from bot.middleware.config_mw import ConfigMiddleware
from bot.middleware.dao_mw import DaoMiddleware
from bot.middleware.user_mw import UserMiddleware
from config import Config


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
    dp.update.middleware(CacheMiddleware(config.cache))
    dp.message.middleware(ClearStateMiddleware())


def setup_dp(config: Config) -> Dispatcher:
    dp = Dispatcher(storage=get_redis_storage(config))

    setup_middleware(dp, config)

    setup_routers(dp)
    return dp


def get_redis_storage(config):
    redis = Redis(
        host=config.cache.host,
        port=config.cache.port,
        db=config.cache.db_num,
        password=config.cache.password,
    )
    return RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))


def run_bot(config: Config):
    bot = Bot(
        token=config.bot.token,
        # parse_mode=config.bot.parse_mode,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    dp = setup_dp(config)

    try:
        dp.run_polling(bot)
    finally:
        close_all_sessions()
        logger.info("Bot stopped")
