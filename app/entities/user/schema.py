from typing import Optional

from pydantic import BaseModel, Field


class UserCreateSchema(BaseModel):
    tg_id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_bot: bool
    language_code: str
