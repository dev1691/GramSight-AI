import uuid
from sqlalchemy import Column, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    village_id = Column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
