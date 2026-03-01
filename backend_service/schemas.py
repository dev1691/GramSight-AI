from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class MarketCreate(BaseModel):
    commodity: str = Field(..., min_length=1)
    modal_price: float
    market_name: Optional[str] = None


class MarketOut(BaseModel):
    id: UUID
    commodity: str
    variety: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    modal_price: Optional[float] = None
    arrival_date: Optional[datetime] = None
    market_name: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

    class Config:
        orm_mode = True


class WeatherOut(BaseModel):
    id: UUID
    village_id: Optional[UUID] = None
    city: Optional[str] = None
    temperature: float
    humidity: float
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    rainfall: Optional[float] = None
    uvi: Optional[float] = None
    description: Optional[str] = None
    recorded_at: datetime

    class Config:
        orm_mode = True

    class Config:
        orm_mode = True
