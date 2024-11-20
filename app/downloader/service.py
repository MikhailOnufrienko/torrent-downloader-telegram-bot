from app.downloader.downloader import Downloader
from app.client.qbittorrent import TorrentClient, torrent_client

class DownloadService:
    def __init__(
        self,
        downloader: Downloader = Downloader,
        torrent_cli: TorrentClient = torrent_client,
    ):
        self._downloader = downloader
        self._torrent_client = torrent_cli
    
    def fetch_torrent_info(link: str):
        pass


downloader_service = DownloadService()
