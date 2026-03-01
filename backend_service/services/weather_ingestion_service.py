import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from backend_service.config import OPENWEATHER_API_KEY
from backend_service.models import WeatherData
from backend_service.database_async import AsyncSessionLocal

logger = logging.getLogger('backend.weather_ingest')

OPENWEATHER_URL = 'https://api.openweathermap.org/data/3.0/onecall'


async def fetch_weather(lat: float, lon: float):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(OPENWEATHER_URL, params=params)
        resp.raise_for_status()
        return resp.json()


async def ingest_weather(db: AsyncSession, village_id, lat: float, lon: float):
    try:
        raw = await fetch_weather(lat, lon)
    except Exception as e:
        logger.exception('OpenWeather fetch failed')
        raise

    current = raw.get('current', {})
    daily = (raw.get('daily') or [])
    today = daily[0] if daily else {}

    temperature = current.get('temp')
    humidity = current.get('humidity')
    pressure = current.get('pressure')
    wind_speed = current.get('wind_speed')
    description = None
    weather_arr = current.get('weather') or []
    if weather_arr:
        description = weather_arr[0].get('description')

    rainfall = today.get('rain') or 0.0
    uvi = today.get('uvi')
    min_temp = today.get('temp', {}).get('min') if isinstance(today.get('temp'), dict) else None
    max_temp = today.get('temp', {}).get('max') if isinstance(today.get('temp'), dict) else None

    rec = WeatherData(
        village_id=village_id,
        city=None,
        temperature=temperature or 0.0,
        humidity=humidity or 0.0,
        pressure=pressure,
        wind_speed=wind_speed,
        rainfall=rainfall,
        uvi=uvi,
        description=description,
        recorded_at=datetime.utcnow()
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


async def ingest_weather_for_all_villages():
    """Helper to ingest weather for all villages. Worker can call this."""
    from backend_service.models import Village
    async with AsyncSessionLocal() as session:
        q = select(Village)
        res = await session.execute(q)
        villages = res.scalars().all()
        results = []
        for v in villages:
            # if coordinates available
            if getattr(v, 'latitude', None) is None or getattr(v, 'longitude', None) is None:
                continue
            try:
                r = await ingest_weather(session, v.id, float(v.latitude), float(v.longitude))
                results.append(r)
            except Exception:
                logging.exception(f'Failed to ingest weather for village {v.id}')
    return results
