from app.downloader.downloader import Downloader
from app.torrent_client.qbittorrent import TorrentClient, torrent_client

class DownloadService:
    def __init__(
        self,
        downloader: Downloader = Downloader,
        torrent_cli: TorrentClient = torrent_client,
    ):
        self._downloader = downloader
        self._torrent_client = torrent_cli


download_service = DownloadService()
