from datetime import datetime

from telegram import User as TGUser

from app.config import config
from app.entities.user.manager import (
    UserManager, UserTorrentManager, user_manager, user_torrent_manager,
    UserContentManager, user_content_manager,
)
from app.models import Torrent, User, user_content_association, user_torrent_association


class UserService:
    def __init__(self, user_manager: UserManager = user_manager):
        self._user_mng = user_manager
    
    async def save_or_get_existing(self, user: TGUser) -> User:
        user_ = await self._user_mng.get_by_tg_id(user.id)
        if not user_:
            user_ = await self._user_mng.save(user)
            config.logger.debug(
                f'User saved: id {user_.id}, tg_id {user_.tg_id}, username {user_.username}'
            )
        return user_
    
    async def get_by_tg_id(self, tg_id: int) -> User | None:
        return await self._user_mng.get_by_tg_id(tg_id)
    
    async def get(self, user_id: int) -> User | None:
        return await self._user_mng.get(user_id)
    
    async def set_user_unblocked(self, user_id: int) -> User:
        payload = {"is_blocked": False, "updated_at": datetime.now().replace(microsecond=0)}
        return await self._user_mng.update(user_id, payload)
    
    async def set_user_blocked(self, user_id: int) -> User:
        payload = {"is_blocked": True, "is_unblocking_message_sent": False, "updated_at": datetime.now().replace(microsecond=0)}
        return await self._user_mng.update(user_id, payload)
    
    async def set_user_is_unblocking_message_sent(self, user_id: int) -> User:
        payload = {"is_unblocking_message_sent": True, "updated_at": datetime.now().replace(microsecond=0)}
        return await self._user_mng.update(user_id, payload)


class UserTorrentService:
    def __init__(self, user_torrent_manager: UserTorrentManager = user_torrent_manager):
        self._user_torrent_mng = user_torrent_manager
    
    async def find_associations_by_torrent_id(self, torrent_id: int) -> user_torrent_association:
        return await self._user_torrent_mng.get_many(torrent_id=torrent_id)
    
    async def save_association(self, user_id: int, torrent_id: int) -> None:
        await self._user_torrent_mng.save(user_id, torrent_id)
    
    async def delete_association(self, user_id: int, torrent_id: int) -> int:
        rows_affected = await self._user_torrent_mng.delete(user_id, torrent_id)
        return rows_affected

    async def delete_associations(self, user_id: int) -> int:
        rows_affected = await self._user_torrent_mng.delete(user_id)
        return rows_affected
    
    async def count_user_torrent_associations(self, user_id: int | None = None, torrent_id: int | None = None) -> int:
        params = {}
        if user_id:
            params.update({"user_id": user_id})
        elif torrent_id:
            params.update({"torrent_id": torrent_id})
        associations = await self._user_torrent_mng.get_many(**params)
        if associations:
            return len(associations)
        return 0
    
    async def fetch_torrents_titles(self, user_id: int) -> list[Torrent]:
        torrents = await self._user_torrent_mng.fetch_torrents(user_id)
        return torrents


class UserContentService:
    def __init__(self, user_content_manager: UserContentManager = user_content_manager):
        self._user_content_mng = user_content_manager
    
    async def find_associations_by_user_id(self, user_id: int) -> user_content_association:
        return await self._user_content_mng.get_many(user_id=user_id)
    
    async def find_associations_by_content_id(self, content_id: int) -> user_content_association:
        return await self._user_content_mng.get_many(content_id=content_id)
    
    async def save_association(self, user_id: int, content_id: int) -> None:
        await self._user_content_mng.save(user_id, content_id)
    
    async def delete_association(self, user_id: int, content_id: int) -> int:
        rows_affected = await self._user_content_mng.delete(user_id, content_id)
        return rows_affected
    
    async def delete_associations(self, user_id: int, content_ids: list[int]) -> int:
        rows_affected = await self._user_content_mng.delete_many(user_id, content_ids)
        return rows_affected


user_service = UserService()
user_torrent_service = UserTorrentService()
user_content_service = UserContentService()
