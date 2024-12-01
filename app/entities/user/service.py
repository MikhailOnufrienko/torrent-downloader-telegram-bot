from app.entities.user.dao import UserDAO
from app.entities.user.schema import UserCreateSchema


class UserService:
    def __init__(self, dao: UserDAO = UserDAO):
        self._dao = dao

    def save(self, user: UserCreateSchema):
        user = self._dao.insert(user.model_dump())