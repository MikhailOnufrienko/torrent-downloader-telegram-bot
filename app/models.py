from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import orm, ForeignKey

from app.database import Base, datetime_default_now, flag_default_false, intpk


user_torrent_association = sa.Table(
    'user_torrent', 
    Base.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('torrent_id', sa.Integer, sa.ForeignKey('torrent.id'), primary_key=True),
)

user_content_association = sa.Table(
    'user_content',
    Base.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('content_id', sa.Integer, sa.ForeignKey('content.id'), primary_key=True),
)


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
    torrents: orm.Mapped[list['Torrent']] = orm.relationship(
        'Torrent',
        secondary=user_torrent_association,
        back_populates='users',
    )
    contents: orm.Mapped[list['Content']] = orm.relationship(
        'Content',
        secondary=user_content_association,
        back_populates='users',
    )

    __tablename__ = 'user'


class Torrent(Base):
    id: orm.Mapped[intpk]
    title: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    hash: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(65))
    magnet_link: orm.Mapped[str] = orm.mapped_column(sa.Text())
    size: orm.Mapped[int] = orm.mapped_column(sa.BigInteger)
    created_at: orm.Mapped[datetime_default_now]
    is_task_sent: orm.Mapped[flag_default_false]
    is_task_failed: orm.Mapped[flag_default_false]
    task_sent_at: orm.Mapped[Optional[datetime]] = orm.mapped_column(default=None)
    is_processing: orm.Mapped[flag_default_false]
    is_bad: orm.Mapped[flag_default_false]
    users: orm.Mapped[list[User]] = orm.relationship(
        'User',
        secondary=user_torrent_association,
        back_populates='torrents',
    )

    __tablename__ = 'torrent'
    __table_args__ = (
        sa.Index('idx_torrent_hash', 'hash', postgresql_using='hash'),
    )


class Content(Base):
    id: orm.Mapped[intpk]
    index: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    save_path: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text())
    file_name: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    file_hash_md5: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(32))
    size: orm.Mapped[int] = orm.mapped_column(sa.BigInteger)
    created_at: orm.Mapped[datetime_default_now]
    is_deleted: orm.Mapped[flag_default_false]
    ready: orm.Mapped[flag_default_false]
    torrent_id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer, ForeignKey('torrent.id', ondelete='CASCADE'), nullable=False
    )
    users: orm.Mapped[list[User]] = orm.relationship(
        'User',
        secondary=user_content_association,
        back_populates='contents',
    )

    __tablename__ = 'content'
    __table_args__ = (
        sa.Index('idx_content_hash', 'file_hash_md5', postgresql_using='hash'),
    )


Models: list[type[Base]] = [User, Torrent, Content]
