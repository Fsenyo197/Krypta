from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class PermissionBase(BaseModel):
    name: str


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: UUID
    date_created: datetime
    date_updated: datetime

    class Config:
        orm_mode = True
