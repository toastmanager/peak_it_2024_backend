from abc import ABC, abstractmethod
from functools import reduce
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import Select, Sequence, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)  # type: ignore


class DatabaseRepository(ABC, Generic[ModelType]):
    @abstractmethod
    async def create(self, attributes: dict[str, Any] = {}) -> ModelType:
        """Creates a new model instance."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> Sequence[ModelType]:
        """Retrieves all model instances."""
        raise NotImplementedError

    @abstractmethod
    async def get_by(
        self,
        field: str,
        value: Any,
        join_: set[str] | None = None,
        unique: bool = False,
    ) -> ModelType | Sequence[ModelType]:  # Return type adjusted for flexibility
        """Retrieves a model instance or instances by a specific field and value."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, model: ModelType) -> None:
        """Deletes a model instance."""
        raise NotImplementedError

    # @abstractmethod
    # async def update(self, model: ModelType) -> None:
    #     """Updates a model instance"""
    #     raise NotImplementedError


class SQLAlchemyRepository(DatabaseRepository, Generic[ModelType]):
    model: Type[ModelType]
    session: AsyncSession

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.session = session
        self.model: Type[ModelType] = model
        super().__init__()

    async def create(self, attributes: dict[str, Any] = {}) -> ModelType | None:
        """
        Creates the model instance.

        :param attributes: The attributes to create the model with.
        :return: The created model instance.
        """
        stmt = insert(self.model).values(**attributes).returning(self.model)
        model = await self.session.execute(stmt)
        await self.session.commit()
        return model.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> Sequence[ModelType]:
        """
        Returns a list of model instances.

        :param skip: The number of records to skip.
        :param limit: The number of record to return.
        :param join_: The joins to make.
        :return: A list of model instances.
        """
        query = self._query(join_)
        query = query.offset(skip).limit(limit)

        if join_ is not None:
            return await self._all_unique(query)

        return await self._all(query)

    async def get_by(
        self,
        field: str,
        value: Any,
        join_: set[str] | None = None,
        unique: bool = False,
    ) -> ModelType | Sequence[ModelType] | None:
        """
        Returns the model instance matching the field and value.

        :param field: The field to match.
        :param value: The value to match.
        :param join_: The joins to make.
        :return: The model instance.
        """
        query = self._query(join_)
        query = await self._get_by(query, field, value)

        if join_ is not None:
            return await self._all_unique(query)
        if unique:
            return await self._one_or_none(query)

        return await self._all(query)

    async def delete(self, model: ModelType) -> None:
        """
        Deletes the model.

        :param model: The model to delete.
        :return: None
        """
        await self.session.delete(model)

    def _query(
        self,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ) -> Select:
        """
        Returns a callable that can be used to query the model.

        :param join_: The joins to make.
        :param order_: The order of the results. (e.g desc, asc)
        :return: A callable that can be used to query the model.
        """
        query = select(self.model)
        query = self._maybe_join(query, join_)
        query = self._maybe_ordered(query, order_)

        return query

    async def _all(self, query: Select) -> Sequence[ModelType]:
        """
        Returns all results from the query.

        :param query: The query to execute.
        :return: A list of model instances.
        """
        new_query = await self.session.scalars(query)
        return new_query.all()  # type: ignore

    async def _all_unique(self, query: Select) -> Sequence[ModelType]:
        result = await self.session.execute(query)
        return result.unique().scalars().all()  # type: ignore

    async def _first(self, query: Select) -> ModelType | None:
        """
        Returns the first result from the query.

        :param query: The query to execute.
        :return: The first model instance.
        """
        new_query = await self.session.scalars(query)
        return new_query.first()

    async def _one_or_none(self, query: Select) -> ModelType | None:
        """Returns the first result from the query or None."""
        new_query = await self.session.scalars(query)
        return new_query.one_or_none()

    async def _one(self, query: Select) -> ModelType:
        """
        Returns the first result from the query or raises NoResultFound.

        :param query: The query to execute.
        :return: The first model instance.
        """
        new_query = await self.session.scalars(query)
        return new_query.one()

    async def _count(self, query: Select) -> int:
        """
        Returns the count of the records.

        :param query: The query to execute.
        """
        new_query = query.subquery()
        new_query = await self.session.scalars(
            select(func.count()).select_from(new_query)
        )
        return new_query.one()

    async def _sort_by(
        self,
        query: Select,
        sort_by: str,
        order: str | None = "asc",
        model: Type[ModelType] | None = None,
        case_insensitive: bool = False,
    ) -> Select:
        """
        Returns the query sorted by the given column.

        :param query: The query to sort.
        :param sort_by: The column to sort by.
        :param order: The order to sort by.
        :param model: The model to sort.
        :param case_insensitive: Whether to sort case insensitively.
        :return: The sorted query.
        """
        model = model or self.model

        order_column = None

        if case_insensitive:
            order_column = func.lower(getattr(model, sort_by))
        else:
            order_column = getattr(model, sort_by)

        if order == "desc":
            return query.order_by(order_column.desc())

        return query.order_by(order_column.asc())

    async def _get_by(self, query: Select, field: str, value: Any) -> Select:
        """
        Returns the query filtered by the given column.

        :param query: The query to filter.
        :param field: The column to filter by.
        :param value: The value to filter by.
        :return: The filtered query.
        """
        return query.where(getattr(self.model, field) == value)

    def _maybe_join(self, query: Select, join_: set[str] | None = None) -> Select:
        """
        Returns the query with the given joins.

        :param query: The query to join.
        :param join_: The joins to make.
        :return: The query with the given joins.
        """
        if not join_:
            return query

        if not isinstance(join_, set):
            raise TypeError("join_ must be a set")

        return reduce(self._add_join_to_query, join_, query)  # type: ignore

    def _maybe_ordered(self, query: Select, order_: dict | None = None) -> Select:
        """
        Returns the query ordered by the given column.

        :param query: The query to order.
        :param order_: The order to make.
        :return: The query ordered by the given column.
        """
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    query = query.order_by(getattr(self.model, order).asc())
            else:
                for order in order_["desc"]:
                    query = query.order_by(getattr(self.model, order).desc())

        return query

    def _add_join_to_query(self, query: Select, join_: set[str]) -> Select:
        """
        Returns the query with the given join.

        :param query: The query to join.
        :param join_: The join to make.
        :return: The query with the given join.
        """
        return getattr(self, "_join_" + join_)(query)  # type: ignore
