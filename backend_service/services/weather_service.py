import os
import requests
from datetime import datetime
from typing import Any, Dict
from backend_service.models import WeatherData

OPENWEATHER_KEY = os.getenv('OPENWEATHER_API_KEY', '')
OPENWEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'


def fetch_weather_for_city(city: str) -> Dict[str, Any]:
    params = {'q': city, 'appid': OPENWEATHER_KEY}
    resp = requests.get(OPENWEATHER_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def parse_and_create_weather(db, city: str, raw: dict) -> WeatherData:
    """Parse OpenWeather current response and save into WeatherData model.

    This synchronous helper is kept for backward compatibility with the
    `/weather/fetch` endpoint. Prefer the async ingestion service
    `weather_ingestion_service` for production ingestion.
    """
    main = raw.get('main', {})
    temp_k = main.get('temp')
    temperature = None
    if temp_k is not None:
        try:
            temp_v = float(temp_k)
            if temp_v > 100:  # likely Kelvin
                temperature = temp_v - 273.15
            else:
                temperature = temp_v
        except Exception:
            temperature = None

    humidity = main.get('humidity')
    pressure = main.get('pressure')
    wind = raw.get('wind', {})
    wind_speed = wind.get('speed')
    weather_arr = raw.get('weather') or []
    description = None
    if weather_arr:
        description = weather_arr[0].get('description')

    # rainfall may appear in 'rain'
    rain = 0.0
    rain_obj = raw.get('rain', {})
    if isinstance(rain_obj, dict):
        rain = rain_obj.get('1h') or rain_obj.get('3h') or 0.0

    rec = WeatherData(
        village_id=None,
        city=city,
        temperature=temperature or 0.0,
        humidity=humidity or 0.0,
        pressure=pressure,
        wind_speed=wind_speed,
        rainfall=rain,
        uvi=None,
        description=description,
        recorded_at=datetime.utcnow(),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
