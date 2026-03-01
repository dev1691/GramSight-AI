from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend_service.database import get_db
from backend_service.services.weather_service import fetch_weather_for_city, parse_and_create_weather
from backend_service.schemas import WeatherOut
import logging

from backend_service.database_async import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend_service.services.weather_ingestion_service import ingest_weather

router = APIRouter(prefix='/weather', tags=['weather'])
logger = logging.getLogger('backend')


@router.post('/fetch', response_model=WeatherOut)
def fetch_weather(city: str, db: Session = Depends(get_db)):
    try:
        raw = fetch_weather_for_city(city)
        saved = parse_and_create_weather(db, city, raw)
        return saved
    except Exception as e:
        logger.exception('Failed to fetch weather')
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/ingest')
async def ingest(village_id: str, lat: float, lon: float, db: AsyncSession = Depends(get_async_db)):
    try:
        rec = await ingest_weather(db, village_id, lat, lon)
        return rec
    except Exception as e:
        logger.exception('Failed to ingest weather')
        raise HTTPException(status_code=500, detail=str(e))
