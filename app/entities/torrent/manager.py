from app.entities.torrent.dao import TorrentDAO
from app.entities.torrent.schema import TorrentSaveSchema
from app.models import Torrent


class TorrentManager:
    def __init__(self, dao: TorrentDAO = TorrentDAO):
        self._dao = dao

    async def save(self, torrent: dict) -> Torrent:
        torrent = TorrentSaveSchema(
            title=torrent['title'],
            hash=torrent['info_hash'],
            magnet_link=torrent['magnet_link'],
            size=torrent['size'],
        )
        return await self._dao.insert(**torrent.model_dump())
    
    async def get(self, torrent_id: int) -> Torrent | None:
        return await self._dao.find_one_or_none(id=torrent_id)
    
    async def get_by_info_hash(self, info_hash: str) -> Torrent | None:
        return await self._dao.find_one_or_none(hash=info_hash)

    async def get_many(self, data: dict) -> list[Torrent]:
        return await self._dao.find_all(**data)
    
    async def update(self, data: dict, torrent_id: int) -> Torrent:
        return await self._dao.update(data, id=torrent_id)


torrent_manager = TorrentManager()
