"""Demo status endpoint — judge-proof demo verification."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend_service.database import get_db
from backend_service.models import Village, RiskScore, MarketPrice, WeatherData, SoilHealth, AiReport, User

router = APIRouter(tags=["demo"])


@router.get("/demo/status")
def demo_status(db: Session = Depends(get_db)):
    """Public endpoint returning demo data statistics. No auth required."""
    villages = db.query(func.count(Village.id)).scalar() or 0
    risk_scores = db.query(func.count(RiskScore.id)).scalar() or 0
    market_entries = db.query(func.count(MarketPrice.id)).scalar() or 0
    weather_entries = db.query(func.count(WeatherData.id)).scalar() or 0
    soil_entries = db.query(func.count(SoilHealth.id)).scalar() or 0
    advisory_entries = db.query(func.count(AiReport.id)).filter(AiReport.report_type == 'advisory').scalar() or 0
    farmer_count = db.query(func.count(User.id)).filter(User.role == 'farmer').scalar() or 0

    demo_farmer = db.query(User).filter(User.email == 'demo-farmer@gramsight.ai').first()
    demo_admin = db.query(User).filter(User.email == 'demo-admin@gramsight.ai').first()

    return {
        "demo_mode": True,
        "data_source": "database",
        "seeded_records": {
            "villages": villages,
            "risk_scores": risk_scores,
            "market_entries": market_entries,
            "weather_entries": weather_entries,
            "soil_entries": soil_entries,
            "advisory_entries": advisory_entries,
        },
        "demo_users": {
            "farmer": demo_farmer.email if demo_farmer else None,
            "admin": demo_admin.email if demo_admin else None,
        },
        "farmer_count": farmer_count,
    }
