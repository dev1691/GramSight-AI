from typing import Dict, Any, Optional
from uuid import UUID
import math
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_service.models import WeatherData, MarketPrice, RiskScore
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


async def _market_trend_score(prices: list) -> float:
    """Compute a simple trend metric from last 7 modal_price values.
    Returns a 0-30 scaled component (Market Risk weight 30%).
    """
    if not prices:
        return 0.0
    vals = [p.modal_price for p in prices if p.modal_price is not None]
    if len(vals) < 2:
        return 0.0
    # average last 3 vs previous 3
    last = vals[:3]
    prev = vals[3:6]
    if not prev:
        return 0.0
    avg_last = sum(last) / len(last)
    avg_prev = sum(prev) / len(prev)
    if avg_prev == 0:
        return 0.0
    pct_change = (avg_last - avg_prev) / avg_prev * 100
    #_scale: if drop >5% -> add risk, if rise -> subtract
    if pct_change < -5:
        return min(30.0, abs(pct_change))
    if pct_change > 5:
        return 0.0
    return max(0.0, min(30.0, abs(pct_change)))


async def calculate_village_risk(village_id: UUID) -> Dict[str, Any]:
    """Deterministic risk calculation as specified. Returns score, level and breakdown."""
    async with async_session() as session:  # type: AsyncSession
        # fetch latest weather
        q = select(WeatherData).where(WeatherData.village_id == village_id).order_by(WeatherData.recorded_at.desc()).limit(7)
        res = await session.execute(q)
        weather_rows = res.scalars().all()

        # fetch recent market
        q2 = select(MarketPrice).where(MarketPrice.village_id == village_id).order_by(MarketPrice.created_at.desc()).limit(7)
        res2 = await session.execute(q2)
        market_rows = res2.scalars().all()

        # Weather risk (40%) - simple rules
        weather_component = 0.0
        if weather_rows:
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
        weather_component = min(40.0, weather_component)

        # Market risk (30%)
        market_component = await _market_trend_score(market_rows)
        market_component = min(30.0, market_component)

        # Soil risk (20%) - placeholder (requires soil table)
        soil_component = 0.0

        # Historical modifier (10%) - placeholder
        historical_component = 0.0

        total = weather_component + market_component + soil_component + historical_component
        # normalize to 0-100
        score = max(0.0, min(100.0, total))
        level = _risk_level_from_score(score)

        breakdown = {
            'weather': weather_component,
            'market': market_component,
            'soil': soil_component,
            'historical': historical_component,
        }

        # persist risk score
        risk = RiskScore(village_id=village_id, farmer_id=None, score=score, risk_level=level, breakdown=breakdown)
        session.add(risk)
        await session.commit()

    return {'score': score, 'risk_level': level, 'breakdown': breakdown}


async def calculate_farmer_risk(farmer_id: UUID, village_id: Optional[UUID] = None) -> Dict[str, Any]:
    """Calculate farmer-level risk by applying crop modifiers. Placeholder implementation.
    Assumes farmland and crop tables exist; will use village risk as base.
    """
    # For now, fetch village risk (most recent) and apply small modifiers
    # TODO: fetch actual farmer crops and apply sensitivity rules
    if village_id is None:
        return {'error': 'village_id required for farmer risk in this placeholder'}

    base = await calculate_village_risk(village_id)
    score = base.get('score', 0.0)
    # example crop modifier
    crop_modifier = 5.0
    final_score = max(0.0, min(100.0, score + crop_modifier))
    level = _risk_level_from_score(final_score)
    breakdown = base.get('breakdown', {})
    breakdown['crop_modifier'] = crop_modifier

    # store
    async with async_session() as session:
        risk = RiskScore(village_id=village_id, farmer_id=farmer_id, score=final_score, risk_level=level, breakdown=breakdown)
        session.add(risk)
        await session.commit()

    return {'score': final_score, 'risk_level': level, 'breakdown': breakdown}
