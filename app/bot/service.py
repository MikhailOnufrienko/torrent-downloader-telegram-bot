import hashlib
from typing import BinaryIO

import bencodepy

from app.downloader.service import downloader_service


class BotService:
    def __init__(self, downloader_svc=downloader_service):
        self._downl_svc = downloader_service

    @staticmethod
    def generate_hash_and_magnet_link_from_file(self, file: BinaryIO) -> tuple[str, str]:
        """Generate an info hash and a magnet link from the given torrent file."""
        with open(file, "rb") as f:
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

    async def process_magnet_link(self, magnet_link: str, info_hash: str = None):
        if not info_hash:
            info_hash = self.extract_info_hash_from_magnet_link(magnet_link)
    
    def extract_info_hash_from_magnet_link(magnet_link: str) -> str:
        pass 


bot_service = BotService()
