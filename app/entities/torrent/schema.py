from typing import Optional

from pydantic import BaseModel, Field


class TorrentSaveSchema(BaseModel):
    title: str
    hash: str
    magnet_link: str
    size: int
