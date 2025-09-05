from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum
from app.models.base_model import BaseModel


class StaffRole(str, enum.Enum):
    ADMIN = "admin"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    MANAGER = "manager"


class Staff(BaseModel):
    __tablename__ = "staffs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department = Column(String(100), nullable=True)
    role = Column(Enum(StaffRole), nullable=True)


    # relationship
    permissions = relationship("Permission", secondary="staff_permissions", back_populates="staffs")
    user = relationship("User", back_populates="staff_profile")
