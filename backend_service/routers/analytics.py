from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import WeatherData, MarketPrice

router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/summary')
def summary(db: Session = Depends(get_db)):
    total_weather = db.query(func.count(WeatherData.id)).scalar()
    total_market = db.query(func.count(MarketPrice.id)).scalar()
    # avg temp per city
    avg_temps = db.query(WeatherData.city, func.avg(WeatherData.temperature).label('avg_temp')).group_by(WeatherData.city).all()
    avg_temps_dict = [{ 'city': r[0], 'avg_temp': float(r[1]) } for r in avg_temps]
    # highest commodity modal price
    highest = db.query(func.max(MarketPrice.modal_price)).scalar()

    return {
        'total_weather_entries': int(total_weather or 0),
        'average_temperature_per_city': avg_temps_dict,
        'total_market_entries': int(total_market or 0),
        'highest_commodity_price': float(highest) if highest is not None else None
    }
