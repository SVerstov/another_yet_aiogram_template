from functools import wraps

from db.base import make_session_factory
from db import DAO
# todo del??

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
                kwargs["dao"] = DAO(session)
                result = await func(*args, **kwargs)
                await session.commit()
                return result
    return wrapper
