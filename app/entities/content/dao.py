from typing import Sequence

from sqlalchemy import insert

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
