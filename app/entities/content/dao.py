from typing import Sequence

from sqlalchemy import insert, select

from app.dao import BaseDAO
from app.models import Content


class ContentDAO(BaseDAO):
    model = Content

    @classmethod
    async def insert_many(cls, records: Sequence[dict]) -> Sequence[model]:
        cls._check_model()
        query = insert(cls.model).values(records).returning(cls.model)
        result = await cls._execute_query(query)
        return result.scalars().all()

    @classmethod
    async def find_many_by_ids(cls, ids: Sequence[int]) -> Sequence[model]:
        cls._check_model()
        if not ids:
            return []
        query = select(cls.model).where(cls.model.id.in_(ids))
        result = await cls._execute_query(query)
        return result.scalars().all()
