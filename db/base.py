from sqlalchemy import MetaData
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import DBConfig

convention = {
    "ix": "ix__%(column_0_label)s",
    "uq": "uq__%(table_name)s__%(column_0_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(column_0_name)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


def make_session_factory(db_config: DBConfig) -> async_sessionmaker[AsyncSession]:
    conf=dict(url=make_url(db_config.uri),
        echo=db_config.show_echo,
        pool_size=db_config.pool_size,
        max_overflow=db_config.max_overflow)
    conf = {k:v for k,v in conf.items() if v}
    engine = create_async_engine(**conf)
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
