import uuid
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from ..database import Base


class RoleEnum(PyEnum):
    farmer = "farmer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(length=255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=512), nullable=False)
    role = Column(SAEnum(RoleEnum, name="roleenum"), nullable=False, default=RoleEnum.farmer)
    is_active = Column(Boolean, default=True)
    village_id = Column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    village = relationship("Village")
