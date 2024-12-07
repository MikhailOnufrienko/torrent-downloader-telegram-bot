from typing import Optional

from pydantic import BaseModel, Field


class TorrentSaveSchema(BaseModel):
    user_id: int
    hash: str
    magnet_link: str
    size: int
