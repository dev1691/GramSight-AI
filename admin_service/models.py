import uuid
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base


class WeatherData(Base):
    __tablename__ = 'weather_data'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    village_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)
    city = Column(String(128), index=True, nullable=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    pressure = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    uvi = Column(Float, nullable=True)
    description = Column(String(256), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MarketPrice(Base):
    __tablename__ = 'market_prices'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    village_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)
    commodity = Column(String(128), index=True, nullable=False)
    variety = Column(String(128), nullable=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    modal_price = Column(Float, nullable=True)
    arrival_date = Column(DateTime(timezone=True), nullable=True)
    market_name = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
