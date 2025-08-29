import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import enum


class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)  
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    twofa_secret = Column(String(64), nullable=True)

    # relationships
    permissions = relationship("Permission", secondary="user_permissions", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
