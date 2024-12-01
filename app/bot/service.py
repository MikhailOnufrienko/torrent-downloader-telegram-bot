import hashlib
import re
from typing import BinaryIO

import bencodepy

from app.client.qbittorrent import TorrentClient, torrent_client
from app.downloader.service import DownloadService, download_service


class BotService:
    def __init__(
            self,
            download_svc: DownloadService = download_service,
            torrent_client: TorrentClient = torrent_client,
    ):
        self._downl_svc = download_svc
        self._torrent_cli = torrent_client

    @staticmethod
    def generate_hash_and_magnet_link_from_file(self, file: BinaryIO) -> tuple[str, str]:
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

    async def fetch_torrent_info(self, magnet_link: str, info_hash: str = None) -> dict | None:
        if not info_hash:
            info_hash = self.extract_info_hash_from_magnet_link(magnet_link)
            if not info_hash:
                return None
            return self._torrent_cli.get_torrent(info_hash)

    @staticmethod
    def extract_info_hash_from_magnet_link(magnet_link: str) -> str | None:
        pattern = r'magnet:\?xt=urn:btih:([a-fA-F0-9]{40}|[a-zA-Z0-9]{32})'
        match = re.search(pattern, magnet_link)
        if match:
            return match.group(1).lower()
        return None


bot_service = BotService()
