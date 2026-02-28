import uuid
from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..database import Base


class SoilHealth(Base):
    __tablename__ = "soil_health"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    village_id = Column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=False, index=True)
    ph = Column(Float, nullable=True)
    organic_matter = Column(Float, nullable=True)
    nitrogen = Column(Float, nullable=True)
