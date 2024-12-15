from typing import Sequence

from sqlalchemy import insert

from app.dao import BaseDAO
from app.models import User, user_torrent_association, user_content_association


class UserDAO(BaseDAO):
    model = User


class UserTorrentDAO(BaseDAO):
    model = user_torrent_association


class UserContentDAO(BaseDAO):
    model = user_content_association
