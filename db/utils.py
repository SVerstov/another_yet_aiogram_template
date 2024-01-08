from functools import wraps

from config import load_config
from db.base import make_session_factory
from db.dao import HolderDao

config = load_config()


def add_dao(func):
    """Оборачивает функцию в контекстный менеджер,
    добавляет в неё именованный аргумент dao"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "dao" in kwargs:
            return await func(*args, **kwargs)
        else:
            session_factory = make_session_factory(config.db)
            async with session_factory() as session:
                kwargs["dao"] = HolderDao(session)
                result = await func(*args, **kwargs)
                await session.commit()
                return result
    return wrapper
