from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Annotated
from uuid import UUID
from datetime import datetime, date
from enum import Enum
from app.schemas.kyc_schema import KYCVerificationResponse, KYCVerificationCreate, KYCVerificationUpdate


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_KYC = "pending_kyc"
    KYC_REJECTED = "kyc_rejected"


# -----------------------------
# User Schemas
# -----------------------------
class UserBase(BaseModel):
    username: Annotated[str, constr(min_length=3, max_length=50)]
    email: EmailStr
    phone_number: str
    is_verified: bool = False
    is_staff: bool = False
    status: UserStatus = UserStatus.PENDING_KYC


class UserCreate(UserBase):
    password: Annotated[str, constr(min_length=8)]
    twofa_secret: Optional[str] = None
    kyc: Optional[KYCVerificationCreate]


class UserUpdate(BaseModel):
    username: Optional[Annotated[str, constr(min_length=3, max_length=50)]]
    email: Optional[EmailStr]
    
    phone_number: Optional[str]
    password: Optional[Annotated[str, constr(min_length=8)]]
    is_verified: Optional[bool]
    status: Optional[UserStatus]
    twofa_secret: Optional[str]
    kyc: Optional[KYCVerificationUpdate]


class UserResponse(UserBase):
    id: UUID
    date_created: datetime
    date_updated: datetime
    latest_kyc: Optional[KYCVerificationResponse]

    class Config:
        orm_mode = True
