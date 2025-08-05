from typing import Any, Callable

from qbittorrent import Client
from requests import HTTPError

from app.config import config


class TorrentClient:
    def __init__(self, dsn: str, username: str, password: str):
        self._client = Client(dsn)
        self._client.login(username, password)

    def __getattr__(self, name):
        return getattr(self._client, name)

    def login(self, username=config.QBITTORRENT_AUTH_USER, password=config.qbittorrent_auth_pass):
        return self._client.login(username, password)


def with_relogin(func: Callable) -> Callable:
    def wrapper(self, *args, **kwargs) -> Any:
        try:
            return func(self, *args, **kwargs)
        except HTTPError:
            self._torrent_cli.login()
            return func(self, *args, **kwargs)
    return wrapper


torrent_client = TorrentClient(
    config.QBITTORRENT_CLIENT_DSN,
    config.QBITTORRENT_AUTH_USER,
    config.qbittorrent_auth_pass,
)
