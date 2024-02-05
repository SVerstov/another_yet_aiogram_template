from typing import List, TypeVar, Type, Generic, Iterable, AsyncIterator, Any

from sqlalchemy import (
    delete,
    func,
    select,
    update,
    Result,
    ScalarResult,
    text,
    ClauseElement,
    UnaryExpression,
    desc,
    ColumnElement,
    Row,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from sqlalchemy.sql.base import ExecutableOption, Executable
from db.base import Base
from sqlalchemy.sql._typing import _JoinTargetArgument

Model = TypeVar("Model", Base, Base)


class BaseDAO(Generic[Model]):
    def __init__(self, model: Type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_many(
        self,
        *whereclauses: ClauseElement,
        options: Iterable[ExecutableOption] | ExecutableOption | None = None,
        limit: int | None = None,
        order_by: ColumnElement | None = None,
        offset: int | None = None,
        join: _JoinTargetArgument | None = None,
        get_only: ColumnElement | None = None,
    ) -> list[Model] | list[Any]:
        """
        Fetch all records from the database with optional filtering, limiting, and offset.

        :param whereclauses: Additional SQLAlchemy WHERE clauses to filter the results. Each will be added to the query.
        :param options: An optional variable. Can be single option or list. Add options too statement
        :param limit: An optional limit on the number of results to return.
        :param offset: An optional number of initial results to skip.
        :param get_only: Optional parameter to specify a subset of columns to retrieve. If provided, only these columns are selected from the model. Useful for fetching specific fields without retrieving the entire row. Accepts a list of column attributes.
        :param join: Optional parameter to specify a join condition. Use this to perform a SQL JOIN with another table or relationship. This is useful for fetching related data in a single query.
        :param order_by: Optional parameter to specify how to sort the results.


        :return: A list of instances of the Model that match the query.
        :rtype: List[Model]
        """
        if get_only:
            stmt = select(get_only)
        else:
            stmt = select(self.model)

        if whereclauses:
            stmt = stmt.where(*whereclauses)
        if join:
            stmt = stmt.join(join)
        if options:
            if isinstance(options, ExecutableOption):
                stmt = stmt.options(options)
            elif isinstance(options, Iterable):
                stmt = stmt.options(*options)
        if limit:
            stmt = stmt.limit(limit)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if offset:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_chunk_iterator(
        self, *whereclauses: ClauseElement, chunk_size: int = 10_000, offset: int = 0
    ) -> AsyncIterator[List[Model]]:
        """
        Generator function that fetches records from the database in batches.
        Usage example:
        async for user_batch in user_dao.get_iterator(User.age > 18, chunk_size=100):
            for user in user_batch:
                print(user)
        """
        stmt = select(self.model)
        if whereclauses:
            stmt = stmt.where(*whereclauses)
        if offset:
            stmt = stmt.offset(offset)
        stream = await self.session.stream(stmt.execution_options(yield_per=chunk_size))
        async for chunk in stream.partitions():
            chunk: list[Row]
            chunk = [x[0] for x in chunk]  # extract objects from Row
            yield chunk

    async def get_last(
        self,
        *whereclauses: ClauseElement,
        order_by: ColumnElement = None,
    ) -> Model | None:
        """
        An instance of the Model class representing the last row that matches the given WHERE clauses and ordered by the specified column.
        If no matching row is found, None is returned.
        """
        if order_by is not None:
            order_by = order_by
        else:
            order_by = self.model.id
        return await self.get_first(*whereclauses, order_by=order_by.desc())

    async def get_all(self):
        return await self.get_many()

    async def get_by_id(self, id_: int) -> Model | None:
        stmt = select(self.model).where(self.model.id == id_)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_first(
        self,
        *whereclauses: ClauseElement,
        order_by: ColumnElement = None,
        offset: int = 0,
    ) -> Model | None:
        """
        Get one model from the database
        """
        stmt = select(self.model)
        if whereclauses:
            stmt = stmt.where(*whereclauses)
        if order_by is None:
            stmt = stmt.order_by(self.model.id)
        else:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(1)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def delete(self, *whereclauses: ClauseElement) -> int:
        """
        Remove records from the database based on the given `whereclauses`.
        :return The number of deleted rows.
        """
        if not whereclauses:
            raise AttributeError("Func delete need at least one whereclause")
        statement = delete(self.model).where(*whereclauses)
        res = await self.session.execute(statement)
        return res.rowcount

    def delete_obj(self, obj: Model):
        self.session.delete(obj)

    def save_obj(self, obj: Model):
        self.session.add(obj)

    async def delete_all(self):
        await self.session.execute(delete(self.model))

    async def count(self, *whereclauses, join=None):
        """
        Count the number of rows in the table with a given where clause or without.

        :param whereclauses: Clause by which rows will be counted
        :return: Count of rows satisfying the where clause
        """
        stmt = select(func.count(self.model.id))
        if join:
            stmt = stmt.join(join)
        if whereclauses:
            stmt = stmt.where(*whereclauses)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_records(self, *whereclauses, **values) -> int:
        """
        Update models from the database

        :param whereclauses: (Optional) Clauses by which entries will be found
        :param values: key-value pairs where key is column name and value is new value
        :return: number of updated rows
        """
        if not values or not whereclauses:
            raise AttributeError(
                "Func need at least one whereclaus and one key-value pair to update"
            )

        stmt = update(self.model).where(*whereclauses).values(**values)
        res = await self.session.execute(stmt)
        return res.rowcount

    async def upsert_record(self, *whereclauses, **values) -> int:
        """update or create new record"""
        rowcount = await self.update_records(*whereclauses, **values)

        if not rowcount:
            new_record = self.model(**values)
            self.session.add(new_record)
            return new_record

        return rowcount

    async def calc_sum(self, column, *whereclauses) -> int:
        stmt = select(func.sum(column)).where(*whereclauses)
        result = await self.session.execute(stmt)
        result = result.scalar_one()
        if result is None:
            return 0
        return result

    async def execute_stmt(self, stmt: Executable) -> Result:
        """Process any SQLAlchemy statement"""
        return await self.session.execute(stmt)

    async def execute_raw_sql(self, sql: str) -> Result:
        """Process any raw sql"""
        return await self.session.execute(text(sql))
