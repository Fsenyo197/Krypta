from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.schemas.permission_schema import PermissionResponse


class APIKeyBase(BaseModel):
    user_id: UUID
    key_hash: str
    secret: str
    is_active: bool = True
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    permissions: Optional[List[UUID]] = [] 


class APIKeyUpdate(BaseModel):
    is_active: Optional[bool]
    expires_at: Optional[datetime]
    permissions: Optional[List[UUID]]


class APIKeyResponse(APIKeyBase):
    id: UUID
    date_created: datetime
    date_updated: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        orm_mode = True
