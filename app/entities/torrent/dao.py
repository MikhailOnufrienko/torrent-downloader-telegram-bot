from app.dao import BaseDAO
from app.models import Torrent


class TorrentDAO(BaseDAO):
    model = Torrent
