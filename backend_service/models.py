import uuid
from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from backend_service.database import Base


class WeatherData(Base):
    __tablename__ = 'weather_data'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    village_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)
    city = Column(String(128), index=True, nullable=False)
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
    arrival_date = Column(DateTime(timezone=True), nullable=True, index=True)
    market_name = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

Index('ix_market_prices_commodity_arrival', MarketPrice.commodity, MarketPrice.arrival_date)


from sqlalchemy import Integer, JSON


class RiskScore(Base):
    __tablename__ = 'risk_scores'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    village_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)
    farmer_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)
    score = Column(Float, nullable=False)
    risk_level = Column(String(32), nullable=False)
    breakdown = Column(JSON, nullable=True)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class AiReport(Base):
    __tablename__ = 'ai_reports'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    village_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)
    farmer_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)
    report_type = Column(String(32), nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


from enum import Enum as PyEnum
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import relationship


class RoleEnum(PyEnum):
    farmer = "farmer"
    admin = "admin"


class User(Base):
    __tablename__ = 'users'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(512), nullable=False)
    role = Column(String(32), nullable=False, default=RoleEnum.farmer.value)
    is_active = Column(Boolean, default=True)
    village_id = Column(PG_UUID(as_uuid=True), ForeignKey('villages.id'), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    village = relationship('Village', backref='users')


class Village(Base):
    __tablename__ = 'villages'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


class SoilHealth(Base):
    __tablename__ = 'soil_health'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    village_id = Column(PG_UUID(as_uuid=True), ForeignKey('villages.id'), nullable=False, index=True)
    ph = Column(Float, nullable=True)
    organic_matter = Column(Float, nullable=True)
    nitrogen = Column(Float, nullable=True)
