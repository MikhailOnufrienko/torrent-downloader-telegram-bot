from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Index
from sqlalchemy import orm

from app.database import Base, datetime_default_now, flag_default_false, intpk


class User(Base):
    id: orm.Mapped[intpk]
    tg_id: orm.Mapped[int] = orm.mapped_column(index=True)
    username: orm.Mapped[str]
    first_name: orm.Mapped[Optional[str]]
    last_name: orm.Mapped[Optional[str]]
    is_subscriber: orm.Mapped[flag_default_false]
    is_bot: orm.Mapped[bool]
    language_code: orm.Mapped[str]
    created_at: orm.Mapped[datetime_default_now]
    updated_at: orm.Mapped[Optional[datetime]]

    __tablename__ = 'user'


class Torrent(Base):
    id: orm.Mapped[intpk]
    user_id:  orm.Mapped[int] = orm.mapped_column(sa.Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    hash: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(65))
    magnet_link: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text())
    size: orm.Mapped[Optional[int]]
    created_at: orm.Mapped[datetime_default_now]
    is_task_sent: orm.Mapped[flag_default_false]
    is_task_failed: orm.Mapped[flag_default_false]
    task_sent_at: orm.Mapped[Optional[datetime]] = orm.mapped_column(default=None)
    is_processing: orm.Mapped[flag_default_false]
    is_bad: orm.Mapped[flag_default_false]
    
    __tablename__ = 'torrent'
    __table_args__ = (
        Index('idx_hash', 'hash', postgresql_using='hash'),
    )


class Content(Base):
    id: orm.Mapped[intpk]
    torrent_id: orm.Mapped[int] = orm.mapped_column(sa.Integer, ForeignKey('torrent.id', ondelete='CASCADE'), nullable=False)
    save_path: orm.Mapped[str] = orm.mapped_column(sa.Text())
    file_name: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    file_hash_md5: orm.Mapped[str] = orm.mapped_column(sa.String(32))
    size: orm.Mapped[int]
    created_at: orm.Mapped[datetime_default_now]
    is_deleted: orm.Mapped[flag_default_false]

    __tablename__ = 'content'
    __table_args__ = (
        Index('idx_hash', 'file_hash_md5', postgresql_using='hash'),
    )


Models: list[type[Base]] = [User, Torrent, Content]
