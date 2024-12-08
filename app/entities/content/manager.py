from app.entities.content.dao import ContentDAO
from app.models import Content


class ContentManager:
    def __init__(self, dao: ContentDAO = ContentDAO):
        self._dao = dao

    async def save_many(self, contents: list[dict]) -> Content:
        return await self._dao.insert_many(contents)
    
    async def get_by_hash(self, file_hash_md5: str) -> list[Content]:
        return await self._dao.find_one_or_none(file_hash_md5=file_hash_md5)


content_manager = ContentManager()
