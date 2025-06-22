from sqlalchemy import delete, and_

from app.dao import BaseDAO
from app.models import User, user_torrent_association, user_content_association


class UserDAO(BaseDAO):
    model = User


class UserTorrentDAO(BaseDAO):
    model = user_torrent_association


class UserContentDAO(BaseDAO):
    model = user_content_association

    @classmethod
    async def delete_many_specific(cls, user_id: int, content_ids: list[int]) -> int:
        query = (
            delete(cls.model)
            .where(
                and_(
                    cls.model.c.user_id == user_id,
                    cls.model.c.content_id.in_(content_ids)
                )
            )
        )
        result = await cls._execute_query(query)
        return result.rowcount
