from app.dao import BaseDAO
from app.models import User, user_torrent_association


class UserDAO(BaseDAO):
    model = User


class UserTorrentDAO(BaseDAO):
    model = user_torrent_association
