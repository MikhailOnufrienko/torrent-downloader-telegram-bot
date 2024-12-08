from app.entities.content.manager import ContentManager, content_manager
from app.models import Content


class ContentService:
    def __init__(self, content_manager: ContentManager = content_manager):
        self._content_mng = content_manager

    async def save_many(self, torrent_files: dict) -> list[int]:
        contents_of_torrent = [{'file_name': file['name'], 'size': file['size']} for file in torrent_files]
        contents = await self._content_mng.save_many(contents_of_torrent)
        return [entity.id for entity in contents]


content_service = ContentService()
