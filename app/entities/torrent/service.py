from app.entities.torrent.manager import TorrentManager, torrent_manager
from app.models import Torrent


class TorrentService:
    def __init__(self, torrent_manager: TorrentManager = torrent_manager):
        self._torrent_mng = torrent_manager

    async def save_or_get_existing(self, torrent: dict) -> Torrent:
        torrent_ = await self._torrent_mng.get_by_info_hash(torrent['info_hash'])
        if not torrent_:
            torrent_ = await self._torrent_mng.save(torrent)
        return torrent_
    
    async def get_by_info_hash(self, info_hash: str) -> Torrent | None:
        return await self._torrent_mng.get_by_info_hash(info_hash)
    
    async def get_many(self, filter_by: dict) -> list[Torrent]:
        return await self._torrent_mng.get_many(filter_by)
    
    async def update_torrent(self, data: dict, torrent_id: int) -> Torrent | None:
        torrent = await self._torrent_mng.get(torrent_id)
        if torrent:
            return await self._torrent_mng.update(data, torrent_id)


torrent_service = TorrentService()
