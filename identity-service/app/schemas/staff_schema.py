from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum
from app.schemas.permission_schema import PermissionResponse


class StaffRole(str, Enum):
    ADMIN = "admin"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    MANAGER = "manager"


class StaffBase(BaseModel):
    department: Optional[str]
    role: Optional[StaffRole]


class StaffCreate(StaffBase):
    user_id: UUID 
    permissions: Optional[List[str]]


class StaffUpdate(BaseModel):
    department: Optional[str]
    role: Optional[StaffRole]
    permissions: Optional[List[str]]


class StaffResponse(StaffBase):
    id: UUID
    user_id: UUID
    date_created: datetime
    date_updated: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        orm_mode = True
