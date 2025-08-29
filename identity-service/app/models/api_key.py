import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class APIKey(BaseModel):
    __tablename__ = "api_keys"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    key_hash = Column(String(255), nullable=False)
    secret = Column(String(128), nullable=False)               
    permissions = relationship("Permission", secondary="api_key_permissions") 
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")


api_key_permissions = Table(
    "api_key_permissions",
    Column("api_key_id", Integer, ForeignKey("api_keys.id")),
    Column("permission_id", Integer, ForeignKey("permissions.id"))
)