from typing import Optional

from app.torrent_client.qbittorrent import torrent_client, TorrentClient


class Downloader:
    _torrent_client_connection_retries = 360
    _delay = 5

    def __init__(self, client: TorrentClient):
        self._client = client
        self._filename: Optional[str] = None

    def __call__(self, magnet_link: str):
        # torrent_files = self._download_files(torrent)
        pass
