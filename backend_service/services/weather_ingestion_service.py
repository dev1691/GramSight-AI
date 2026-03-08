import logging
from datetime import datetime, timedelta, timezone
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


async def ingest_weather(db: AsyncSession, village_id, lat: float, lon: float,
                         city_name: str = 'unknown', *, auto_commit: bool = True):
    try:
        raw = await fetch_weather(lat, lon)
    except Exception:
        logger.exception('OpenWeather fetch failed for village %s', village_id)
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

    # ── Data validation ──────────────────────────────────────────────
    # Reject clearly invalid readings (sensor errors / API glitches)
    if temperature is None or not (-60 <= temperature <= 60):
        logger.warning('Invalid temperature %.2f for village %s — skipping',
                       temperature if temperature else 0, village_id)
        return None
    if humidity is not None and not (0 <= humidity <= 100):
        logger.warning('Invalid humidity %.1f for village %s — clamping', humidity, village_id)
        humidity = max(0, min(100, humidity))
    if rainfall is not None and rainfall < 0:
        rainfall = 0.0

    # ── Deduplication: skip if a record already exists within the last hour
    now_utc = datetime.now(timezone.utc)
    one_hour_ago = now_utc - timedelta(hours=1)
    dup_q = await db.execute(
        select(WeatherData.id).where(
            WeatherData.village_id == village_id,
            WeatherData.recorded_at >= one_hour_ago,
        ).limit(1)
    )
    if dup_q.scalars().first() is not None:
        logger.debug('Skipping weather for village %s — recent record exists', village_id)
        return None

    rec = WeatherData(
        village_id=village_id,
        city=city_name,
        temperature=round(temperature, 2),
        humidity=round(humidity, 1) if humidity else 0.0,
        pressure=pressure,
        wind_speed=wind_speed,
        rainfall=round(rainfall, 1),
        uvi=uvi,
        description=description,
        recorded_at=now_utc,
    )
    db.add(rec)
    if auto_commit:
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
            if getattr(v, 'latitude', None) is None or getattr(v, 'longitude', None) is None:
                continue
            try:
                r = await ingest_weather(
                    session, v.id, float(v.latitude), float(v.longitude),
                    city_name=v.name,
                )
                if r is not None:
                    results.append(r)
            except Exception:
                logger.exception('Failed to ingest weather for village %s (%s)', v.name, v.id)
    return results
