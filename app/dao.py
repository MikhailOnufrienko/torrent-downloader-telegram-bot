from abc import ABC
from typing import Any, Generic, Optional, TypeVar

from loguru import logger
from sqlalchemy import delete, insert, select, update, and_
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import DeclarativeBase

from app.database import async_session

T = TypeVar("T", bound=DeclarativeBase)


class BaseDAO(Generic[T], ABC):
    model: type[T]

    @classmethod
    def _check_model(cls):
        if cls.model is None:
            raise NotImplementedError()

    @staticmethod
    async def _execute_query(query):
        try:
            async with async_session() as session:
                try:
                    result = await session.execute(query)
                    await session.commit()
                    return result
                except IntegrityError as e:
                    await session.rollback()
                    raise Exception(e)
        except (OSError, OperationalError) as e:
            logger.error(f"ERROR: CONNECTION TO DB FAILED! Stacktrace: {e}")

    @classmethod
    async def insert(cls, **kwargs) -> T:
        cls._check_model()
        query = insert(cls.model).values(**kwargs).returning(cls.model)
        result = await cls._execute_query(query)
        return result.scalar_one_or_none()

    @classmethod
    async def update(cls, values: dict[str, Any], **filter_by) -> T:
        cls._check_model()
        query = update(cls.model).values(**values).filter_by(**filter_by).returning(cls.model)
        result = await cls._execute_query(query)
        return result.scalar_one_or_none()

    @classmethod
    async def delete(cls, **filter_by) -> int:
        cls._check_model()
        query = delete(cls.model).filter_by(**filter_by)
        result = await cls._execute_query(query)
        return result.rowcount

    @classmethod
    async def find_all(cls, limit: Optional[int] = None, offset: Optional[int] = None, **filter_by) -> list[T]:
        cls._check_model()
        query = select(cls.model).filter_by(**filter_by).order_by(cls.model.id)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        async with async_session() as session:
            try:
                result = await session.execute(query)
                return result.scalars().all()
            except IntegrityError as e:
                raise Exception(e)

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> Optional[T]:
        cls._check_model()
        async with async_session() as session:
            try:
                query = select(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.scalar_one_or_none()
            except IntegrityError as e:
                raise Exception(e)
    
    @classmethod
    async def find_all_in_secondary(cls, limit: Optional[int] = None, offset: Optional[int] = None, **filter_by) -> list[T]:
        cls._check_model()
        query = select(cls.model)
        if filter_by:
            conditions = [getattr(cls.model.c, key) == value for key, value in filter_by.items()]
            query = query.where(and_(*conditions))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        async with async_session() as session:
            try:
                result = await session.execute(query)
                rows = result.mappings().all()
                return rows
            except IntegrityError as e:
                raise Exception(e)
