from telegram import User as TGUser

from app.entities.user.dao import UserDAO
from app.entities.user.schema import UserSaveSchema
from app.models import User


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
        )
        return await self._dao.insert(**user.model_dump())
    
    async def get(self, user_tg_id: int) -> User | None:
        return await self._dao.find_one_or_none(tg_id=user_tg_id)


user_manager = UserManager()
