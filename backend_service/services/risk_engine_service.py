from typing import Dict, Any, Optional
from uuid import UUID
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_service.models import WeatherData, MarketPrice, RiskScore, SoilHealth
from backend_service.database_async import AsyncSessionLocal as async_session

logger = logging.getLogger(__name__)


def _risk_level_from_score(score: float) -> str:
    if score <= 30:
        return 'Low'
    if score <= 60:
        return 'Moderate'
    if score <= 80:
        return 'High'
    return 'Critical'


def _market_trend_score(prices: list) -> float:
    """Compute a simple trend metric from last 7 modal_price values.
    Returns a 0-30 scaled component (Market Risk weight 30%).
    """
    if not prices:
        return 0.0
    vals = [p.modal_price for p in prices if p.modal_price is not None]
    if len(vals) < 2:
        return 0.0
    last = vals[:3]
    prev = vals[3:6]
    if not prev:
        return 0.0
    avg_last = sum(last) / len(last)
    avg_prev = sum(prev) / len(prev)
    if avg_prev == 0:
        return 0.0
    pct_change = (avg_last - avg_prev) / avg_prev * 100
    if pct_change < -5:
        return min(30.0, abs(pct_change))
    if pct_change > 5:
        return 0.0
    return max(0.0, min(30.0, abs(pct_change)))


def _soil_risk_score(soil: Optional[Any]) -> float:
    """Soil risk component (20%). Based on pH, organic matter, nitrogen."""
    if soil is None:
        return 10.0  # default moderate risk when no data
    score = 0.0
    ph = getattr(soil, 'ph', None)
    if ph is not None:
        if ph < 5.5 or ph > 8.5:
            score += 10.0
        elif ph < 6.0 or ph > 8.0:
            score += 5.0
    else:
        score += 5.0  # unknown pH → moderate risk

    organic = getattr(soil, 'organic_matter', None)
    if organic is not None:
        if organic < 1.0:
            score += 5.0
        elif organic < 2.0:
            score += 2.5
    else:
        score += 2.5

    nitrogen = getattr(soil, 'nitrogen', None)
    if nitrogen is not None:
        if nitrogen < 150:
            score += 5.0
        elif nitrogen < 250:
            score += 2.5
    else:
        score += 2.5

    return min(20.0, score)


async def calculate_village_risk(village_id: UUID) -> Dict[str, Any]:
    """Deterministic risk calculation. Returns score, level and breakdown."""
    async with async_session() as session:  # type: AsyncSession
        # fetch latest weather
        q = select(WeatherData).where(WeatherData.village_id == village_id).order_by(WeatherData.recorded_at.desc()).limit(7)
        res = await session.execute(q)
        weather_rows = res.scalars().all()

        # fetch recent market
        q2 = select(MarketPrice).where(MarketPrice.village_id == village_id).order_by(MarketPrice.created_at.desc()).limit(7)
        res2 = await session.execute(q2)
        market_rows = res2.scalars().all()

        # fetch latest soil health
        q3 = select(SoilHealth).where(SoilHealth.village_id == village_id).limit(1)
        res3 = await session.execute(q3)
        soil_row = res3.scalars().first()

        # ---- Weather risk (40%) ----
        weather_component = 0.0
        has_weather = bool(weather_rows)
        if has_weather:
            temps = [w.temperature for w in weather_rows if w.temperature is not None]
            humidity = [w.humidity for w in weather_rows if w.humidity is not None]
            rain = [w.rainfall for w in weather_rows if w.rainfall is not None]
            uvi = [w.uvi for w in weather_rows if w.uvi is not None]

            avg_temp = sum(temps) / len(temps) if temps else 0.0
            avg_hum = sum(humidity) / len(humidity) if humidity else 0.0
            total_rain = sum(rain) if rain else 0.0
            avg_uvi = sum(uvi) / len(uvi) if uvi else 0.0

            if avg_temp > 35:
                weather_component += 15
            if avg_temp < 10:
                weather_component += 15
            if avg_hum > 85:
                weather_component += 10
            if total_rain > 100:
                weather_component += 10
            if avg_uvi > 8:
                weather_component += 5
        else:
            weather_component = 20.0  # insufficient data → moderate default
        weather_component = min(40.0, weather_component)

        # ---- Market risk (30%) ----
        market_component = _market_trend_score(market_rows)
        market_component = min(30.0, market_component)

        # ---- Soil risk (20%) ----
        soil_component = _soil_risk_score(soil_row)

        # ---- Historical modifier (10%) ----
        historical_component = 5.0  # baseline until historical trend is implemented

        total = weather_component + market_component + soil_component + historical_component
        score = max(0.0, min(100.0, total))
        level = _risk_level_from_score(score)

        breakdown = {
            'weather': weather_component,
            'market': market_component,
            'soil': soil_component,
            'historical': historical_component,
            'has_weather_data': has_weather,
            'has_soil_data': soil_row is not None,
        }

        # persist risk score
        risk = RiskScore(village_id=village_id, farmer_id=None, score=score, risk_level=level, breakdown=breakdown)
        session.add(risk)
        await session.commit()

    return {'score': score, 'risk_level': level, 'breakdown': breakdown}


async def calculate_farmer_risk(farmer_id: UUID, village_id: Optional[UUID] = None) -> Dict[str, Any]:
    """Calculate farmer-level risk by applying crop modifiers on top of village risk."""
    if village_id is None:
        return {'error': 'village_id required for farmer risk'}

    base = await calculate_village_risk(village_id)
    score = base.get('score', 0.0)
    crop_modifier = 5.0
    final_score = max(0.0, min(100.0, score + crop_modifier))
    level = _risk_level_from_score(final_score)
    breakdown = base.get('breakdown', {})
    breakdown['crop_modifier'] = crop_modifier

    async with async_session() as session:
        risk = RiskScore(village_id=village_id, farmer_id=farmer_id, score=final_score, risk_level=level, breakdown=breakdown)
        session.add(risk)
        await session.commit()

    return {'score': final_score, 'risk_level': level, 'breakdown': breakdown}
