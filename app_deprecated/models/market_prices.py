import uuid
from sqlalchemy import Column, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..database import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    village_id = Column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=False, index=True)
    commodity = Column(String(length=128), nullable=False)
    price = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
