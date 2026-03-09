"""Farmer-facing read endpoints consumed by the React frontend."""
import asyncio
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend_service.database import get_db
from backend_service.models import (
    Village, WeatherData, MarketPrice, SoilHealth, RiskScore,
)
from backend_service.core.dependencies import get_current_active_user

router = APIRouter(prefix="/farmer", tags=["farmer"])
logger = logging.getLogger("backend.farmer")


# ── Village list (for VillageSelector) ──────────────────────────
@router.get("/villages")
def list_villages(db: Session = Depends(get_db), _user=Depends(get_current_active_user)):
    rows = db.query(Village).order_by(Village.name).all()
    return [
        {"id": str(v.id), "name": v.name, "latitude": v.latitude, "longitude": v.longitude}
        for v in rows
    ]


# ── Risk for a village ─────────────────────────────────────────
@router.get("/{village_id}/risk")
async def village_risk(
    village_id: UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_active_user),
):
    from backend_service.services import risk_engine_service
    from backend_service import cache

    key = f"risk:village:{village_id}"
    cached = await cache.get_cached(key)
    if cached:
        return {"risk": cached}

    # Check for stored risk score before calculating dynamically
    # Wrap sync ORM call in to_thread to avoid blocking the event loop
    def _fetch_stored():
        return (
            db.query(RiskScore)
            .filter(RiskScore.village_id == village_id)
            .order_by(desc(RiskScore.calculated_at))
            .first()
        )

    stored = await asyncio.to_thread(_fetch_stored)
    if stored:
        res = {
            "score": stored.score,
            "risk_level": stored.risk_level,
            "breakdown": stored.breakdown or {},
        }
        await cache.set_cached(key, res, ttl=6 * 3600)
        return {"risk": res}

    res = await risk_engine_service.calculate_village_risk(village_id)
    await cache.set_cached(key, res, ttl=6 * 3600)
    return {"risk": res}


# ── Weather for a village ──────────────────────────────────────
@router.get("/{village_id}/weather")
def village_weather(
    village_id: UUID,
    limit: int = Query(default=5, le=30),
    db: Session = Depends(get_db),
    _user=Depends(get_current_active_user),
):
    rows = (
        db.query(WeatherData)
        .filter(WeatherData.village_id == village_id)
        .order_by(desc(WeatherData.recorded_at))
        .limit(limit)
        .all()
    )
    if not rows:
        # Fallback: try city-based weather (any)
        rows = (
            db.query(WeatherData)
            .order_by(desc(WeatherData.recorded_at))
            .limit(limit)
            .all()
        )
    records = [
        {
            "temperature": r.temperature,
            "humidity": r.humidity,
            "rainfall": r.rainfall or 0,
            "wind_speed": r.wind_speed or 0,
            "description": r.description or "",
            "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
        }
        for r in rows
    ]
    # Summary for the quick-stat cards
    latest = records[0] if records else {}
    return {
        "weather": {
            "temperature": latest.get("temperature", 28),
            "humidity": latest.get("humidity", 60),
            "precipitation": latest.get("rainfall", 0),
            "wind_speed": latest.get("wind_speed", 0),
            "description": latest.get("description", ""),
        },
        "history": records,
    }


# ── Available crops for a village (distinct commodities in DB) ───
@router.get("/{village_id}/crops")
def village_crops(
    village_id: UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_active_user),
):
    """List distinct commodities (crops) with market data for the village."""
    rows = (
        db.query(MarketPrice.commodity)
        .filter(MarketPrice.village_id == village_id)
        .filter(MarketPrice.commodity.isnot(None))
        .distinct()
        .order_by(MarketPrice.commodity)
        .all()
    )
    crops = [r[0] for r in rows if r[0]]
    if not crops:
        rows = (
            db.query(MarketPrice.commodity)
            .filter(MarketPrice.commodity.isnot(None))
            .distinct()
            .order_by(MarketPrice.commodity)
            .limit(50)
            .all()
        )
        crops = [r[0] for r in rows if r[0]]
    if not crops:
        crops = [
            "Rice", "Wheat", "Sugarcane", "Cotton", "Soybean", "Jowar",
            "Bajra", "Maize", "Mango", "Onion", "Tomato", "Groundnut", "Paddy",
        ]
    return {"crops": crops}


# ── Market for a village ───────────────────────────────────────
@router.get("/{village_id}/market")
def village_market(
    village_id: UUID,
    limit: int = Query(default=10, le=50),
    commodity: str | None = Query(default=None, description="Filter by crop/commodity name"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_active_user),
):
    q = (
        db.query(MarketPrice)
        .filter(MarketPrice.village_id == village_id)
        .order_by(desc(MarketPrice.created_at))
    )
    if commodity and commodity.strip():
        q = q.filter(func.lower(MarketPrice.commodity) == commodity.strip().lower())
    rows = q.limit(limit).all()

    if not rows:
        q = db.query(MarketPrice).order_by(desc(MarketPrice.created_at))
        if commodity and commodity.strip():
            q = q.filter(func.lower(MarketPrice.commodity) == commodity.strip().lower())
        rows = q.limit(limit).all()

    markets = [
        {
            "commodity": r.commodity,
            "price": r.modal_price or 0,
            "modal_price": r.modal_price or 0,
            "min_price": r.min_price,
            "max_price": r.max_price,
            "market_name": r.market_name,
            "arrival_date": r.arrival_date.isoformat() if r.arrival_date else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return {"markets": markets}


# ── Soil health for a village ──────────────────────────────────
@router.get("/{village_id}/soil")
def village_soil(
    village_id: UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_active_user),
):
    row = (
        db.query(SoilHealth)
        .filter(SoilHealth.village_id == village_id)
        .first()
    )
    if not row:
        return {
            "nitrogen": None,
            "phosphorus": None,
            "potassium": None,
            "moisture": None,
            "ph": None,
        }
    return {
        "nitrogen": row.nitrogen,
        "phosphorus": getattr(row, 'phosphorus', None),
        "potassium": getattr(row, 'potassium', None),
        "moisture": getattr(row, 'moisture', None),
        "ph": row.ph,
        "organic_matter": row.organic_matter,
    }


# ── Advisory (wraps AI analysis) ──────────────────────────────
@router.get("/{village_id}/advisory")
async def village_advisory(
    village_id: UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_active_user),
):
    from backend_service.services import ai_analysis_service
    from backend_service import cache

    key = f"ai:village:{village_id}"
    cached = await cache.get_cached(key)
    if cached:
        recs = cached.get("recommendations", [])
        return {"items": recs if recs else ["AI analysis temporarily unavailable"]}

    # Check for stored advisory report in DB
    # Wrap sync ORM call in to_thread to avoid blocking the event loop
    from backend_service.models import AiReport

    def _fetch_report():
        return (
            db.query(AiReport)
            .filter(AiReport.village_id == village_id, AiReport.report_type == 'advisory')
            .order_by(desc(AiReport.created_at))
            .first()
        )

    report = await asyncio.to_thread(_fetch_report)
    if report and isinstance(report.content, dict):
        items = report.content.get('items', [])
        if items:
            return {"items": items}

    try:
        res = await ai_analysis_service.generate_village_analysis(village_id)
        await cache.set_cached(key, res, ttl=12 * 3600)
        recs = res.get("recommendations", [])
        return {"items": recs if recs else ["AI analysis temporarily unavailable"]}
    except Exception:
        logger.exception("Advisory generation failed")
        return {"items": ["AI advisory temporarily unavailable. Please try again later."]}
