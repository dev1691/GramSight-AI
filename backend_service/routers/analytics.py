from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend_service.database import get_db
from backend_service.models import WeatherData, MarketPrice, Village, RiskScore, User
from backend_service.core.dependencies import get_current_active_user, require_role
from backend_service.models import RoleEnum

router = APIRouter(prefix='', tags=['analytics'])


@router.get('/analytics/summary')
def summary(
    db: Session = Depends(get_db),
    _user=Depends(get_current_active_user),
    limit: int = Query(default=50, le=500, description="Max cities to return"),
):
    total_weather = db.query(func.count(WeatherData.id)).scalar()
    total_market = db.query(func.count(MarketPrice.id)).scalar()
    avg_temps = (
        db.query(WeatherData.city, func.avg(WeatherData.temperature).label('avg_temp'))
        .group_by(WeatherData.city)
        .limit(limit)
        .all()
    )
    avg_temps_dict = [{'city': r[0], 'avg_temp': round(float(r[1]), 2)} for r in avg_temps]
    highest = db.query(func.max(MarketPrice.modal_price)).scalar()

    return {
        'total_weather_entries': int(total_weather or 0),
        'average_temperature_per_city': avg_temps_dict,
        'total_market_entries': int(total_market or 0),
        'highest_commodity_price': float(highest) if highest is not None else None
    }


@router.get('/admin/villages')
def admin_villages(
    db: Session = Depends(get_db),
    _user=Depends(require_role(RoleEnum.admin)),
):
    """List all villages with their latest risk scores."""
    villages = db.query(Village).order_by(Village.name).all()
    result = []
    for v in villages:
        latest_risk = (
            db.query(RiskScore)
            .filter(RiskScore.village_id == v.id)
            .order_by(desc(RiskScore.calculated_at))
            .first()
        )
        result.append({
            'id': str(v.id),
            'name': v.name,
            'district': v.district or 'Unknown',
            'risk_score': round(latest_risk.score) if latest_risk else None,
            'crop': v.crop or 'Mixed',
            'latitude': v.latitude,
            'longitude': v.longitude,
        })
    return result


@router.get('/admin/market-trend')
def admin_market_trend(
    db: Session = Depends(get_db),
    _user=Depends(require_role(RoleEnum.admin)),
    limit: int = Query(default=6, le=24),
):
    """Aggregated market prices over recent months for admin chart."""
    from sqlalchemy import extract
    rows = (
        db.query(
            func.date_trunc('month', MarketPrice.created_at).label('month'),
            func.avg(MarketPrice.modal_price).label('avg_price'),
        )
        .group_by('month')
        .order_by(desc('month'))
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))
    labels = [r[0].strftime('%b') if r[0] else '?' for r in rows]
    prices = [round(float(r[1])) if r[1] else 0 for r in rows]
    return {'labels': labels, 'prices': prices, 'crop': 'Avg All Commodities'}


@router.get('/admin/risk-trend')
def admin_risk_trend(
    db: Session = Depends(get_db),
    _user=Depends(require_role(RoleEnum.admin)),
    limit: int = Query(default=6, le=24),
):
    """Aggregated avg risk scores over recent months."""
    rows = (
        db.query(
            func.date_trunc('month', RiskScore.calculated_at).label('month'),
            func.avg(RiskScore.score).label('avg_score'),
        )
        .group_by('month')
        .order_by(desc('month'))
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))
    labels = [r[0].strftime('%b') if r[0] else '?' for r in rows]
    scores = [round(float(r[1])) if r[1] else 0 for r in rows]
    return {'labels': labels, 'scores': scores}


@router.get('/admin/stats')
def admin_stats(
    db: Session = Depends(get_db),
    _user=Depends(require_role(RoleEnum.admin)),
):
    """Aggregated stats for admin KPI cards."""
    farmer_count = db.query(func.count(User.id)).filter(User.role == 'farmer').scalar()
    return {'farmer_count': int(farmer_count or 0)}
