from telegram import User as TGUser

from app.config import config
from app.entities.user.manager import UserManager, user_manager
from app.models import User


class UserService:
    def __init__(self, user_manager: UserManager = user_manager):
        self._user_mng = user_manager
    
    async def save_if_not_exists(self, user: TGUser) -> User | None:
        if not await self._user_mng.get(user.id):
            user_saved = await self._user_mng.save(user)
            config.logger.debug(
                f'User saved: id {user_saved.id}, tg_id {user_saved.tg_id}, username {user_saved.username}'
            )
            return user_saved
    
    async def get_by_tg_id(self, tg_id: int) -> User | None:
        return await self._user_mng.get(tg_id)


user_service = UserService()
