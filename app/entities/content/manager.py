from app.entities.content.dao import ContentDAO
from app.models import Content


class ContentManager:
    def __init__(self, dao: ContentDAO = ContentDAO):
        self._dao = dao

    async def save_many(self, contents: list[dict]) -> list[Content]:
        return await self._dao.insert_many(contents)
    
    async def get(self, content_id: int) -> Content | None:
        return await self._dao.find_one_or_none(id=content_id)
    
    async def get_by_hash(self, file_hash_md5: str) -> Content:
        return await self._dao.find_one_or_none(file_hash_md5=file_hash_md5)
    
    async def get_by_torrent_id(self, torrent_id: int) -> list[Content]:
        return await self._dao.find_all(torrent_id=torrent_id)
    
    async def get_many_by_ids(self, content_ids: list[int]) -> list[Content]:
        return await self._dao.find_many_by_ids(content_ids)
    
    async def update(self, data: dict, torrent_id: int, index: int) -> Content:
        return await self._dao.update(data, torrent_id=torrent_id, index=index)
    
    async def delete_many(self, filter_by: dict) -> int:
        return await self._dao.delete(**filter_by)


content_manager = ContentManager()
