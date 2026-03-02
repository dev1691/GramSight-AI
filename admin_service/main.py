import os
from pathlib import Path
import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import DataError

from database import get_db, engine
from models import WeatherData, MarketPrice

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger('admin_service')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

app = FastAPI(title='GramSight Admin')

# Resolve template/static directories relative to this file so paths are correct
base_dir = Path(__file__).resolve().parent
templates_dir = base_dir / 'templates'
static_dir = base_dir / 'static'

templates = Jinja2Templates(directory=str(templates_dir))

# Only mount static files if the directory exists; avoid runtime crash if missing
if static_dir.exists():
    app.mount('/static', StaticFiles(directory=str(static_dir)), name='static')
else:
    logger.warning("admin_service: static directory not found (%s); not mounting /static", str(static_dir))


# ── Global exception handler — never expose stack traces ──────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


def admin_auth(request: Request):
    """Accept auth via x-admin-key header OR admin_key cookie."""
    key = os.getenv('ADMIN_API_KEY')
    header = request.headers.get('x-admin-key')
    cookie = request.cookies.get('admin_key')
    if not key or (header != key and cookie != key):
        raise HTTPException(status_code=403, detail='access denied')
    return True


# ── Login / Logout (browser-friendly) ────────────────────────────────────
@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request, error: str = None):
    return templates.TemplateResponse('login.html', {'request': request, 'error': error})


@app.post('/login', response_class=HTMLResponse)
async def login_submit(request: Request):
    form = await request.form()
    submitted_key = form.get('key', '')
    expected_key = os.getenv('ADMIN_API_KEY')
    if not expected_key or submitted_key != expected_key:
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid admin key'})
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='admin_key', value=submitted_key, httponly=True, samesite='lax')
    return response


@app.get('/logout')
def logout():
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie('admin_key')
    return response


def _safe_page(page: int) -> int:
    """Clamp page to >= 1 to prevent negative OFFSET errors."""
    return max(1, page)


def _safe_limit(limit: int) -> int:
    """Clamp limit to 1–100 to prevent fetching entire tables."""
    return max(1, min(100, limit))


def _validate_uuid(value: str) -> str:
    """Validate UUID format; raise 400 if invalid."""
    import uuid
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="invalid UUID format")
    return value


@app.get('/', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _: bool = Depends(admin_auth)):
    totals = {
        'weather': db.query(func.count(WeatherData.id)).scalar() or 0,
        'market': db.query(func.count(MarketPrice.id)).scalar() or 0
    }
    latest_weather = db.query(WeatherData).order_by(WeatherData.recorded_at.desc()).first()
    latest_market = db.query(MarketPrice).order_by(MarketPrice.created_at.desc()).first()
    return templates.TemplateResponse('dashboard.html', {'request': request, 'totals': totals, 'latest_weather': latest_weather, 'latest_market': latest_market})


@app.get('/weather', response_class=HTMLResponse)
def weather_list(request: Request, page: int = 1, limit: int = 25, city: str = None, db: Session = Depends(get_db), _: bool = Depends(admin_auth)):
    page = _safe_page(page)
    limit = _safe_limit(limit)
    q = db.query(WeatherData)
    if city:
        q = q.filter(WeatherData.city.ilike(f"%{city}%"))
    offset = (page-1)*limit
    rows = q.order_by(WeatherData.recorded_at.desc()).offset(offset).limit(limit+1).all()
    more = len(rows) > limit
    rows = rows[:limit]
    return templates.TemplateResponse('weather.html', {'request': request, 'rows': rows, 'page': page, 'more': more})


@app.get('/market', response_class=HTMLResponse)
def market_list(request: Request, page: int = 1, limit: int = 25, commodity: str = None, db: Session = Depends(get_db), _: bool = Depends(admin_auth)):
    page = _safe_page(page)
    limit = _safe_limit(limit)
    q = db.query(MarketPrice)
    if commodity:
        q = q.filter(MarketPrice.commodity.ilike(f"%{commodity}%"))
    offset = (page-1)*limit
    rows = q.order_by(MarketPrice.arrival_date.desc()).offset(offset).limit(limit+1).all()
    more = len(rows) > limit
    rows = rows[:limit]
    return templates.TemplateResponse('market.html', {'request': request, 'rows': rows, 'page': page, 'more': more})


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/admin/weather/{village_id}')
def admin_latest_weather(village_id: str, db: Session = Depends(get_db), _: bool = Depends(admin_auth)):
    _validate_uuid(village_id)
    rec = db.query(WeatherData).filter(WeatherData.village_id == village_id).order_by(WeatherData.recorded_at.desc()).first()
    if not rec:
        raise HTTPException(status_code=404, detail='no weather data')
    return JSONResponse({
        'village_id': str(rec.village_id) if rec.village_id else None,
        'temperature': rec.temperature,
        'humidity': rec.humidity,
        'rainfall': rec.rainfall,
        'risk_factor': 'moderate'
    })


@app.get('/admin/market/trends/{commodity}')
def admin_market_trends(commodity: str, db: Session = Depends(get_db), _: bool = Depends(admin_auth)):
    rows = db.query(MarketPrice).filter(MarketPrice.commodity.ilike(commodity)).order_by(MarketPrice.arrival_date.desc()).limit(7).all()
    prices = [r.modal_price for r in rows if r.modal_price is not None]
    trend = 'stable'
    if len(prices) >= 2:
        if prices[0] > prices[-1]:
            trend = 'up'
        elif prices[0] < prices[-1]:
            trend = 'down'
    return {'commodity': commodity, 'trend': trend, 'recent_prices': prices}


@app.get('/admin/market/{village_id}')
def admin_latest_market(village_id: str, db: Session = Depends(get_db), _: bool = Depends(admin_auth)):
    _validate_uuid(village_id)
    rows = db.query(MarketPrice).filter(MarketPrice.village_id == village_id).order_by(MarketPrice.arrival_date.desc()).limit(10).all()
    out = []
    for r in rows:
        out.append({
            'commodity': r.commodity,
            'modal_price': r.modal_price,
            'arrival_date': str(r.arrival_date) if r.arrival_date else None,
            'market_name': r.market_name,
        })
    return out
