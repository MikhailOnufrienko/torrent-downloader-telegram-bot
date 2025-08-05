from typing import Union
from telegram import User as TGUser

from app.entities.user.dao import UserDAO, UserTorrentDAO, UserContentDAO
from app.entities.user.schema import UserSaveSchema
from app.models import Torrent, User


class UserManager:
    def __init__(self, dao: UserDAO = UserDAO):
        self._dao = dao

    async def save(self, user: TGUser) -> User:
        user = UserSaveSchema(
            tg_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_bot=user.is_bot,
            language_code=user.language_code,
        )  # type: ignore
        return await self._dao.insert(**user.model_dump())  # type: ignore
    
    async def get_by_tg_id(self, user_tg_id: int) -> User | None:
        return await self._dao.find_one_or_none(tg_id=user_tg_id)
    
    async def get(self, user_id: int) -> User | None:
        return await self._dao.find_one_or_none(id=user_id)
    
    async def update(self, user_id: int, payload: dict) -> User:
        return await self._dao.update(payload, id=user_id)


class UserTorrentManager:
    def __init__(self, dao: UserTorrentDAO = UserTorrentDAO):
        self._dao = dao
    
    async def save(self, user_id: int, torrent_id: int) -> None:
        if not await self._dao.find_one_or_none(user_id=user_id, torrent_id=torrent_id):
            await self._dao.insert(user_id=user_id, torrent_id=torrent_id)
    
    async def get(self, user_id: int, torrent_id: int):
        return await self._dao.find_one_or_none(user_id=user_id, torrent_id=torrent_id)
    
    async def get_many(self, user_id: int | None = None, torrent_id: int | None = None):
        """Either parameter must be None!"""
        if user_id:
            return await self._dao.find_all_in_secondary(user_id=user_id)
        elif torrent_id:
            return await self._dao.find_all_in_secondary(torrent_id=torrent_id)

    async def delete(self, user_id: int, torrent_id: int | None = None) -> int:
        if torrent_id:
            rows_affected = await self._dao.delete(user_id=user_id, torrent_id=torrent_id)
            return rows_affected
        rows_affected = await self._dao.delete(user_id=user_id)
        return rows_affected
    
    async def fetch_torrents(self, user_id: int) -> list[Torrent]:
        return await self._dao.fetch_user_torrents(user_id)


class UserContentManager:
    def __init__(self, dao: UserContentDAO = UserContentDAO):
        self._dao = dao
    
    async def save(self, user_id: int, content_id: int) -> None:
        if not await self._dao.find_one_or_none(user_id=user_id, content_id=content_id):
            await self._dao.insert(user_id=user_id, content_id=content_id)
    
    async def get(self, user_id: int, content_id: int):
        return await self._dao.find_one_or_none(user_id=user_id, content_id=content_id)
    
    async def get_many(self, user_id: int | None = None, content_id: int | None = None):
        """Either parameter must be None!"""
        if user_id:
            return await self._dao.find_all_in_secondary(user_id=user_id)
        if content_id:
            return await self._dao.find_all_in_secondary(content_id=content_id)

    async def delete(self, user_id: int, content_id: int) -> int:
        rows_affected = await self._dao.delete(user_id=user_id, content_id=content_id)
        return rows_affected
    
    async def delete_many(self, user_id: int, content_ids: list[int]) -> int:
        rows_affected = await self._dao.delete_many_specific(user_id, content_ids)
        return rows_affected


user_manager = UserManager()
user_torrent_manager = UserTorrentManager()
user_content_manager = UserContentManager()
