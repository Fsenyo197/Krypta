from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class SessionBase(BaseModel):
    user_id: UUID
    refresh_token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    is_valid: bool = True
    expires_at: datetime


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    is_valid: Optional[bool]
    expires_at: Optional[datetime]


class SessionResponse(SessionBase):
    id: UUID
    date_created: datetime
    date_updated: datetime

    class Config:
        orm_mode = True
