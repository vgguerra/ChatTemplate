from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MessageRead(BaseModel):
    id: int
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    title: str = "New chat"


class SessionRead(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionDetail(SessionRead):
    messages: list[MessageRead] = []
