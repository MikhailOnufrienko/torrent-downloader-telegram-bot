from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import orm

from app.database import datetime_default_now, flag_default_false, intpk


class User(orm.DeclarativeBase):
    id: orm.Mapped[intpk]
    tg_id: orm.Mapped[int]
    is_subscriber: orm.Mapped[flag_default_false]


class Torrent(orm.DeclarativeBase):
    id: orm.Mapped[intpk]
    user_id:  orm.Mapped[int]
    hash: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(65))
    magnet_link: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text(), nullable=True)
    file: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text(), nullable=True)
    size: orm.Mapped[int]
    added_on: orm.Mapped[datetime_default_now]
    is_task_sent: orm.Mapped[flag_default_false]
    is_task_failed: orm.Mapped[flag_default_false]
    task_sent_on: orm.Mapped[Optional[datetime]] = orm.mapped_column(default=None)
    is_processing: orm.Mapped[flag_default_false]
    is_bad: orm.Mapped[flag_default_false]
    