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


torrent_service = TorrentService()
