from datetime import date, datetime
from typing import Annotated

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, sessionmaker

from app.config import config

engine = create_async_engine(config.postgres_dsn)

if config.is_test_mode:
    engine = create_async_engine(config.postgres_dsn, poolclass=sa.NullPool)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True, index=True)]

flag_default_true = Annotated[bool, mapped_column(default=True, server_default=sa.true())]

flag_default_false = Annotated[bool, mapped_column(default=False, server_default=sa.false())]

datetime_default_now = Annotated[
    datetime, mapped_column(default=lambda: datetime.now().replace(microsecond=0))
]

class Base(DeclarativeBase):
    type_annotation_map = {
        int: sa.Integer,
        bool: sa.Boolean,
        date: sa.Date,
        datetime: sa.DateTime,
    }
