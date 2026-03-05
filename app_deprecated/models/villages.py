import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..database import Base


class Village(Base):
    __tablename__ = "villages"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(length=255), nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
