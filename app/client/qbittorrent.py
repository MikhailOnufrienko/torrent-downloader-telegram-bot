from qbittorrent import Client

from app.config import config


class TorrentClient:
    def __init__(self, dsn: str, username: str, password: str):
        self._client = Client(dsn)
        self._client.login(username, password)

    def __getattr__(self, name):
        return getattr(self._client, name)


torrent_client = TorrentClient(
    config.QBITTORRENT_CLIENT_DSN,
    config.QBITTORRENT_AUTH_USER,
    config.qbittorrent_auth_pass,
)
