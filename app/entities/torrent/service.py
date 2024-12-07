
from app.config import config
from app.entities.torrent.manager import TorrentManager, torrent_manager
from app.models import Torrent


class TorrentService:
    def __init__(self, torrent_manager: TorrentManager = torrent_manager):
        self._torrent_mng = torrent_manager

    async def save_or_get_existing(self, torrent: dict) -> Torrent:
        existing_torrent = await self._torrent_mng.get(torrent['info_hash'])
        if not existing_torrent:
            torrent = await self._torrent_mng.save(torrent)
        return existing_torrent or torrent


torrent_service = TorrentService()
