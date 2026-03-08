"""Farmland CRUD endpoints — Farm Registry feature."""
import logging
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend_service.database import get_db
from backend_service.models import Farmland, Village, WeatherData, MarketPrice, RiskScore
from backend_service.core.dependencies import get_current_active_user

router = APIRouter(prefix="/farmland", tags=["farmland"])
logger = logging.getLogger("backend.farmland")


# ── Schemas ──────────────────────────────────────────────────────
class FarmlandCreate(BaseModel):
    land_name: str = Field(..., min_length=1, max_length=255)
    total_acres: float = Field(..., gt=0, le=10000)
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    crop_type: Optional[str] = None
    sowing_date: Optional[datetime] = None
    harvest_date: Optional[datetime] = None
    village_id: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    notes: Optional[str] = None


class FarmlandUpdate(BaseModel):
    land_name: Optional[str] = None
    total_acres: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    crop_type: Optional[str] = None
    sowing_date: Optional[datetime] = None
    harvest_date: Optional[datetime] = None
    village_id: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    notes: Optional[str] = None


class FarmlandOut(BaseModel):
    id: str
    land_name: str
    total_acres: float
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    crop_type: Optional[str] = None
    sowing_date: Optional[str] = None
    harvest_date: Optional[str] = None
    village_id: Optional[str] = None
    village_name: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    notes: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    ai_insight: Optional[dict] = None
    created_at: Optional[str] = None


def _serialize_farmland(f: Farmland) -> dict:
    return {
        "id": str(f.id),
        "land_name": f.land_name,
        "total_acres": f.total_acres,
        "soil_type": f.soil_type,
        "irrigation_type": f.irrigation_type,
        "crop_type": f.crop_type,
        "sowing_date": f.sowing_date.isoformat() if f.sowing_date else None,
        "harvest_date": f.harvest_date.isoformat() if f.harvest_date else None,
        "village_id": str(f.village_id) if f.village_id else None,
        "village_name": f.village.name if f.village else None,
        "geo_lat": f.geo_lat,
        "geo_lng": f.geo_lng,
        "notes": f.notes,
        "risk_score": f.risk_score,
        "risk_level": f.risk_level,
        "ai_insight": f.ai_insight,
        "created_at": f.created_at.isoformat() if f.created_at else None,
    }


# ── LIST my farmlands ───────────────────────────────────────────
@router.get("/", response_model=List[FarmlandOut])
def list_farmlands(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    rows = (
        db.query(Farmland)
        .filter(Farmland.farmer_id == current_user.id)
        .order_by(desc(Farmland.created_at))
        .all()
    )
    return [_serialize_farmland(f) for f in rows]


# ── CREATE farmland ─────────────────────────────────────────────
@router.post("/", response_model=FarmlandOut, status_code=status.HTTP_201_CREATED)
def create_farmland(
    payload: FarmlandCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    village_uuid = None
    if payload.village_id:
        try:
            village_uuid = UUID(payload.village_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid village_id format")
        village = db.query(Village).filter(Village.id == village_uuid).first()
        if not village:
            raise HTTPException(status_code=404, detail="Village not found")

    farmland = Farmland(
        farmer_id=current_user.id,
        village_id=village_uuid,
        land_name=payload.land_name,
        total_acres=payload.total_acres,
        soil_type=payload.soil_type,
        irrigation_type=payload.irrigation_type,
        crop_type=payload.crop_type,
        sowing_date=payload.sowing_date,
        harvest_date=payload.harvest_date,
        geo_lat=payload.geo_lat,
        geo_lng=payload.geo_lng,
        notes=payload.notes,
    )

    # Compute initial risk score from village weather/market data
    if village_uuid:
        risk = _compute_farmland_risk(db, village_uuid, payload.crop_type)
        farmland.risk_score = risk["score"]
        farmland.risk_level = risk["level"]

    db.add(farmland)
    db.commit()
    db.refresh(farmland)
    logger.info("Farmland created: %s by farmer %s", farmland.id, current_user.id)
    return _serialize_farmland(farmland)


# ── GET single farmland ─────────────────────────────────────────
@router.get("/{farmland_id}", response_model=FarmlandOut)
def get_farmland(
    farmland_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    f = db.query(Farmland).filter(Farmland.id == farmland_id, Farmland.farmer_id == current_user.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Farmland not found")
    return _serialize_farmland(f)


# ── UPDATE farmland ─────────────────────────────────────────────
@router.put("/{farmland_id}", response_model=FarmlandOut)
def update_farmland(
    farmland_id: UUID,
    payload: FarmlandUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    f = db.query(Farmland).filter(Farmland.id == farmland_id, Farmland.farmer_id == current_user.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Farmland not found")

    update_data = payload.dict(exclude_unset=True)
    if "village_id" in update_data and update_data["village_id"]:
        try:
            update_data["village_id"] = UUID(update_data["village_id"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid village_id format")

    for key, val in update_data.items():
        setattr(f, key, val)

    # Recompute risk if village or crop changed
    vid = f.village_id
    if vid:
        risk = _compute_farmland_risk(db, vid, f.crop_type)
        f.risk_score = risk["score"]
        f.risk_level = risk["level"]

    db.commit()
    db.refresh(f)
    return _serialize_farmland(f)


# ── DELETE farmland ─────────────────────────────────────────────
@router.delete("/{farmland_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farmland(
    farmland_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    f = db.query(Farmland).filter(Farmland.id == farmland_id, Farmland.farmer_id == current_user.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Farmland not found")
    db.delete(f)
    db.commit()


# ── AI Insight for a farmland ───────────────────────────────────
@router.post("/{farmland_id}/ai-insight")
async def farmland_ai_insight(
    farmland_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    import asyncio

    def _fetch():
        return db.query(Farmland).filter(
            Farmland.id == farmland_id, Farmland.farmer_id == current_user.id
        ).first()

    f = await asyncio.to_thread(_fetch)
    if not f:
        raise HTTPException(status_code=404, detail="Farmland not found")

    from backend_service.services.ai_analysis_service import generate_farmland_analysis
    insight = await generate_farmland_analysis(f, db)

    # Persist insight on farmland — run sync ORM write in thread
    def _persist():
        f.ai_insight = insight
        if isinstance(insight, dict) and "risk_score" in insight:
            f.risk_score = insight["risk_score"]
            f.risk_level = insight.get("risk_level", _risk_level(insight["risk_score"]))
        db.commit()
        db.refresh(f)

    await asyncio.to_thread(_persist)
    return _serialize_farmland(f)


# ── Summary for admin: all farmlands across all farmers ─────────
@router.get("/admin/summary")
def admin_farmland_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    from backend_service.models import RoleEnum
    if current_user.role != RoleEnum.admin.value:
        raise HTTPException(status_code=403, detail="Admin only")

    from sqlalchemy import func
    total = db.query(func.count(Farmland.id)).scalar() or 0
    total_acres = db.query(func.sum(Farmland.total_acres)).scalar() or 0
    avg_risk = db.query(func.avg(Farmland.risk_score)).scalar()

    # Top crops
    crop_dist = (
        db.query(Farmland.crop_type, func.count(Farmland.id).label("cnt"))
        .filter(Farmland.crop_type.isnot(None))
        .group_by(Farmland.crop_type)
        .order_by(desc("cnt"))
        .limit(5)
        .all()
    )

    return {
        "total_farmlands": total,
        "total_acres": round(float(total_acres), 1),
        "avg_risk_score": round(float(avg_risk), 1) if avg_risk else None,
        "crop_distribution": [{"crop": c, "count": n} for c, n in crop_dist],
    }


# ── Internal helpers ─────────────────────────────────────────────
def _risk_level(score: float) -> str:
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Moderate"
    if score <= 80:
        return "High"
    return "Critical"


def _compute_farmland_risk(db: Session, village_id: UUID, crop_type: Optional[str] = None) -> dict:
    """Quick deterministic risk from latest village weather + market data."""
    score = 0.0

    # Weather component (0-40)
    weather = (
        db.query(WeatherData)
        .filter(WeatherData.village_id == village_id)
        .order_by(desc(WeatherData.recorded_at))
        .limit(7)
        .all()
    )
    if weather:
        temps = [w.temperature for w in weather if w.temperature is not None]
        avg_temp = sum(temps) / len(temps) if temps else 28
        rains = [w.rainfall or 0 for w in weather]
        total_rain = sum(rains)
        if avg_temp > 35:
            score += 15
        if avg_temp < 10:
            score += 15
        humidity = [w.humidity for w in weather if w.humidity is not None]
        avg_hum = sum(humidity) / len(humidity) if humidity else 60
        if avg_hum > 85:
            score += 10
        if total_rain > 100:
            score += 10
    else:
        score += 20  # no data = moderate risk

    # Market component (0-30)
    market = (
        db.query(MarketPrice)
        .filter(MarketPrice.village_id == village_id)
        .order_by(desc(MarketPrice.created_at))
        .limit(7)
        .all()
    )
    if crop_type and market:
        crop_prices = [m.modal_price for m in market if m.commodity and m.commodity.lower() == crop_type.lower() and m.modal_price]
        if len(crop_prices) >= 2:
            if crop_prices[0] < crop_prices[-1] * 0.9:
                score += 20  # price dropping
            elif crop_prices[0] < crop_prices[-1]:
                score += 10
    elif not market:
        score += 10

    # Stored risk (0-10)
    stored = (
        db.query(RiskScore)
        .filter(RiskScore.village_id == village_id)
        .order_by(desc(RiskScore.calculated_at))
        .first()
    )
    if stored:
        score += min(10, stored.score * 0.1)
    else:
        score += 5

    score = max(0, min(100, score))
    return {"score": round(score, 1), "level": _risk_level(score)}
