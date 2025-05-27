from app.entities.content.manager import ContentManager, content_manager
from app.models import Content

class ContentService:
    def __init__(self,
        content_manager: ContentManager = content_manager,

    ):
        self._content_mng = content_manager
    
    async def get(self, content_id: int) -> Content | None:
        return await self._content_mng.get(content_id)

    async def save_many_if_not_exists(self, torrent_files: dict, torrent_id: int) -> list[Content]:
        contents = await self._content_mng.get_by_torrent_id(torrent_id)
        if not contents:    
            contents_of_torrent = [
                {'index': file['index'], 'torrent_id': torrent_id, 'file_name': file['name'], 'size': file['size']}
                for file in torrent_files
            ]
            contents = await self._content_mng.save_many(contents_of_torrent)
        return contents

    async def get_by_torrent_id(self, torrent_id: int) -> list[Content]:
        return await self._content_mng.get_by_torrent_id(torrent_id)
    
    async def update(self, data: dict, torrent_id: int, index: int) -> Content:
        return await self._content_mng.update(data, torrent_id, index)


content_service = ContentService()
