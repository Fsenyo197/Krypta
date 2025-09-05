from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import enum


class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_KYC = "pending_kyc"
    KYC_REJECTED = "kyc_rejected"


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_KYC, index=True)
    twofa_secret = Column(String(64), nullable=True)

    # --- Relationships ---
    kyc_verifications = relationship(
        "KYCVerification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    permissions = relationship("Permission", secondary="user_permissions", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
