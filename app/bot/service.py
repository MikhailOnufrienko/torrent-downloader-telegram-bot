import asyncio
import hashlib
import re
from typing import BinaryIO

import bencodepy
from telegram import User as TGUser

from app.client.qbittorrent import TorrentClient, torrent_client
from app.config import config
from app.downloader.service import DownloadService, download_service
from app.entities.torrent.service import TorrentService, torrent_service
from app.entities.user.service import UserService, user_service, UserTorrentService, user_torrent_service
from app.models import Torrent


class BotService:
    def __init__(
        self,
        download_svc: DownloadService = download_service,
        torrent_client: TorrentClient = torrent_client,
        torrent_service: TorrentService = torrent_service,
        user_service: UserService = user_service,
        user_torrent_service: UserTorrentService = user_torrent_service,
    ):
        self._downl_svc = download_svc
        self._torrent_cli = torrent_client
        self._torrent_svc = torrent_service
        self._user_svc = user_service
        self._user_torrent_svc = user_torrent_service
    
    async def save_user_if_not_exists(self, user: TGUser) -> None:
        await self._user_svc.save_if_not_exists(user)

    @staticmethod
    def generate_hash_and_magnet_link_from_file(file: BinaryIO) -> tuple[str, str]:
        """Generate an info hash and a magnet link from the given torrent file."""
        with open(file, 'rb') as f:
            torrent_data = bencodepy.decode(f.read())
        info = torrent_data[b"info"]
        info_hash = hashlib.sha1(bencodepy.encode(info)).hexdigest()
        magnet_link = f"magnet:?xt=urn:btih:{info_hash}"
        if b"announce-list" in torrent_data:
            for tier in torrent_data[b"announce-list"]:
                for tracker in tier:
                    magnet_link += f"&tr={tracker.decode()}"
        elif b"announce" in torrent_data:
            magnet_link += f'&tr={torrent_data[b"announce"].decode()}'
        return info_hash, magnet_link
    
    async def save_torrent_or_get_existing(
        self, user_tg_id: int, magnet_link: str, info_hash: str = None
     ) -> Torrent | None:
        if not info_hash:
            info_hash = self.extract_info_hash_from_magnet_link(magnet_link)
            if not info_hash:
                return None
        user = await self._user_svc.get_by_tg_id(user_tg_id)
        if not user:
            return None
        torrent_info = await self.fetch_torrent_info(magnet_link, info_hash)
        torrent = {
            'user': user,
            'title': torrent_info['name'],
            'info_hash': info_hash,
            'magnet_link': magnet_link,
            'size': torrent_info['total_size'],
        }
        torrent = await self._torrent_svc.save_or_get_existing(torrent)
        await self._user_torrent_svc.save_association(user.id, torrent.id)

    async def fetch_torrent_info(self, magnet_link: str, info_hash: str) -> dict:
        self._torrent_cli.download_from_link(magnet_link, savepath=config.SAVEPATH)
        await asyncio.sleep(10)
        return self._torrent_cli.get_torrent(info_hash)

    @staticmethod
    def extract_info_hash_from_magnet_link(magnet_link: str) -> str | None:
        pattern = r'magnet:\?xt=urn:btih:([a-fA-F0-9]{40}|[a-zA-Z0-9]{32})'
        match = re.search(pattern, magnet_link)
        if match:
            return match.group(1).lower()
        return None
    
    async def construct_torrent_files_hierarchy(self, info_hash: str) -> dict:
        torrent_files = self._torrent_cli.get_torrent_files(info_hash)
        hierarchy = {(file['index'], file['name'], file['size']) for file in torrent_files}
        return hierarchy


bot_service = BotService()
