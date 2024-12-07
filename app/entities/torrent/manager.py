from app.entities.torrent.dao import TorrentDAO
from app.entities.torrent.schema import TorrentSaveSchema
from app.models import Torrent


class TorrentManager:
    def __init__(self, dao: TorrentDAO = TorrentDAO):
        self._dao = dao

    async def save(self, torrent: dict) -> Torrent:
        torrent = TorrentSaveSchema(
            user_id=torrent['user_id'],
            hash=torrent['info_hash'],
            magnet_link=torrent['magnet_link'],
            size=torrent['size'],
        )
        return await self._dao.insert(**torrent.model_dump())
    
    async def get(self, info_hash: str) -> Torrent | None:
        return await self._dao.find_one_or_none(hash=info_hash)


torrent_manager = TorrentManager()
