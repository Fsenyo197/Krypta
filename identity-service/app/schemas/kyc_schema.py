from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from enum import Enum


class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class KYCVerificationBase(BaseModel):
    full_name: Optional[str]
    date_of_birth: Optional[date]
    nationality: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    document_type: Optional[str]
    document_number: Optional[str]
    document_image_url: Optional[str]
    selfie_image_url: Optional[str]
    kyc_notes: Optional[str]
    status: Optional[KYCStatus] = KYCStatus.PENDING


class KYCVerificationCreate(KYCVerificationBase):
    pass


class KYCVerificationUpdate(KYCVerificationBase):
    pass


class KYCVerificationResponse(KYCVerificationBase):
    id: UUID
    date_created: datetime
    date_updated: datetime

    class Config:
        orm_mode = True
