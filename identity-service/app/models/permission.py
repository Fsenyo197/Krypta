import uuid
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False)

    users = relationship("User", secondary="user_permissions", back_populates="permissions")



UserPermissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)
