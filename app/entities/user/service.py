from telegram import User as TGUser

from app.config import config
from app.entities.user.manager import (
    UserManager, UserTorrentManager, user_manager, user_torrent_manager,
    UserContentManager, user_content_manager,
)
from app.models import User


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


class UserTorrentService:
    def __init__(self, user_torrent_manager: UserTorrentManager = user_torrent_manager):
        self._user_torrent_mng = user_torrent_manager
    
    async def save_association(self, user_id: int, torrent_id: int) -> None:
        await self._user_torrent_mng.save(user_id, torrent_id)
    
    async def delete_association(self, user_id: int, torrent_id: int) -> None:
        await self._user_torrent_mng.delete(user_id, torrent_id)


class UserContentService:
    def __init__(self, user_content_manager: UserContentManager = user_content_manager):
        self._user_content_mng = user_content_manager
    
    async def save_association(self, user_id: int, content_id: int) -> None:
        await self._user_content_mng.save(user_id, content_id)
    
    async def delete_association(self, user_id: int, content_id: int) -> None:
        await self._user_content_mng.delete(user_id, content_id)


user_service = UserService()
user_torrent_service = UserTorrentService()
user_content_service = UserContentService()
