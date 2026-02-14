from sqlalchemy import Column, Integer, String, DateTime, Enum, func, UUID, Index, Boolean
from ..configs.db import Base
import enum
import uuid

class RoleEnum(enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum, name="user_role"), default=RoleEnum.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_user_username", "username"),
        Index("idx_user_role", "role"),
        Index("idx_user_is_active", "is_active"),
    )




