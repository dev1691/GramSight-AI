#!/usr/bin/env python3
"""
Idempotent demo data seed script for GramSight AI.

Seeds the database with the exact DEMO_* data from the frontend so that
demo mode shows real backend-served data instead of hardcoded fallbacks.

Usage:
    docker exec gramsight-ai-backend-1 python /app/scripts/seed_demo_data.py

Safe to run multiple times — uses upsert-by-name logic and deletes
stale demo records before re-inserting.
"""
import sys
import os
import uuid
import logging
from datetime import datetime, timezone, timedelta

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from backend_service.database import SessionLocal, engine
from backend_service.models import (
    Village, WeatherData, MarketPrice, RiskScore, SoilHealth, AiReport, User,
)
from backend_service.core.security import get_password_hash

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('seed')

# ─── Deterministic UUIDs (so script is idempotent) ────────────────────────
NAMESPACE = uuid.UUID('a1b2c3d4-e5f6-7890-abcd-ef1234567890')


def demo_uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, name)


# ─── DEMO DATA (extracted from frontend DEMO_* constants) ────────────────

DEMO_VILLAGES = [
    {'name': 'Rajpur',     'district': 'Pune',       'crop': 'Rice',       'score': 72, 'lat': 18.5204, 'lon': 73.8567},
    {'name': 'Devgad',     'district': 'Sindhudurg', 'crop': 'Mango',      'score': 45, 'lat': 16.3907, 'lon': 73.3969},
    {'name': 'Malshiras',  'district': 'Solapur',    'crop': 'Sugarcane',   'score': 83, 'lat': 17.8466, 'lon': 75.1025},
    {'name': 'Kothrud',    'district': 'Pune',       'crop': 'Wheat',       'score': 28, 'lat': 18.5074, 'lon': 73.8077},
    {'name': 'Sinhagad',   'district': 'Pune',       'crop': 'Soybean',     'score': 56, 'lat': 18.3664, 'lon': 73.7557},
    {'name': 'Baramati',   'district': 'Pune',       'crop': 'Sugarcane',   'score': 91, 'lat': 18.1537, 'lon': 74.5777},
    {'name': 'Pandharpur', 'district': 'Solapur',    'crop': 'Jowar',       'score': 67, 'lat': 17.6790, 'lon': 75.3256},
    {'name': 'Wai',        'district': 'Satara',     'crop': 'Strawberry',  'score': 34, 'lat': 17.9509, 'lon': 73.8903},
]

# Weather data per day (Mon→Fri). Frontend shows these after reversing
# the API response (which is DESC). So DB must store newest-first order.
# Frontend expects: temp=[28,31,33,30,27], rain=[5,12,2,0,8], hum=[65,72,58,54,68]
# Reversed (DB order, newest first): temp=[27,30,33,31,28], rain=[8,0,2,12,5], hum=[68,54,58,72,65]
DEMO_WEATHER_DB_ORDER = [
    {'temperature': 27, 'rainfall': 8,  'humidity': 68, 'description': 'partly cloudy'},
    {'temperature': 30, 'rainfall': 0,  'humidity': 54, 'description': 'clear sky'},
    {'temperature': 33, 'rainfall': 2,  'humidity': 58, 'description': 'scattered clouds'},
    {'temperature': 31, 'rainfall': 12, 'humidity': 72, 'description': 'light rain'},
    {'temperature': 28, 'rainfall': 5,  'humidity': 65, 'description': 'overcast clouds'},
]

# Market data (farmer view). Frontend takes 5 most recent (DESC) as Week 1-5.
# DEMO_MARKET: prices=[2200,2180,2250,2300,2280], crop='Rice'
# DB order (newest first): [2200, 2180, 2250, 2300, 2280]
DEMO_MARKET_FARMER_DB_ORDER = [2200, 2180, 2250, 2300, 2280]

# Market data for admin monthly trend (separate records per month)
# DEMO_MARKET_ADMIN: labels=[Jan..Jun], prices=[2100,2200,2150,2300,2250,2400]
# We'll use months Oct 2025 → Feb 2026 (5 months) plus the farmer records in March
DEMO_MARKET_ADMIN_MONTHLY = [
    (datetime(2025, 10, 15, 12, 0, tzinfo=timezone.utc), 2100),
    (datetime(2025, 11, 15, 12, 0, tzinfo=timezone.utc), 2200),
    (datetime(2025, 12, 15, 12, 0, tzinfo=timezone.utc), 2150),
    (datetime(2026,  1, 15, 12, 0, tzinfo=timezone.utc), 2300),
    (datetime(2026,  2, 15, 12, 0, tzinfo=timezone.utc), 2250),
]

# Soil health (DEMO_SOIL)
DEMO_SOIL = {'nitrogen': 65, 'phosphorus': 42, 'potassium': 72, 'moisture': 38, 'ph': 6.5, 'organic_matter': 3.2}

# Advisory (DEMO_ADVISORY)
DEMO_ADVISORY = [
    'Increase watering frequency — rising temperatures and low rainfall forecast for the next 3 days.',
    'Rice prices trending upward (+2.4%) — consider holding current stock for 1-2 more weeks before selling.',
    'Apply organic mulch to retain soil moisture. Current nitrogen levels are adequate, but phosphorus is low.',
    'Monitor weather alerts closely — dry spell expected. Plan irrigation schedules accordingly.',
]

# Risk trend (DEMO_TREND): monthly avg scores
# labels=[Jan..Jun], scores=[42,48,55,51,63,58]
# We map: Oct→42, Nov→48, Dec→55, Jan→51, Feb→63.
# March will use per-village scores (avg ≈ 59.5)
DEMO_RISK_TREND_MONTHLY = [
    (datetime(2025, 10, 15, 12, 0, tzinfo=timezone.utc), 42),
    (datetime(2025, 11, 15, 12, 0, tzinfo=timezone.utc), 48),
    (datetime(2025, 12, 15, 12, 0, tzinfo=timezone.utc), 55),
    (datetime(2026,  1, 15, 12, 0, tzinfo=timezone.utc), 51),
    (datetime(2026,  2, 15, 12, 0, tzinfo=timezone.utc), 63),
]

# Demo users
DEMO_USERS = [
    {'email': 'demo-farmer@gramsight.ai', 'password': 'DemoUser123!', 'role': 'farmer'},
    {'email': 'demo-admin@gramsight.ai',  'password': 'DemoUser123!', 'role': 'admin'},
]

# ─── Risk level helper ────────────────────────────────────────────────────
def _risk_level(score):
    if score <= 30: return 'Low'
    if score <= 60: return 'Moderate'
    if score <= 80: return 'High'
    return 'Critical'


# ─── Add missing DB columns (safe ALTER TABLE IF NOT EXISTS) ──────────────
def add_missing_columns(session):
    """Add new columns to existing tables without dropping data."""
    alter_stmts = [
        "ALTER TABLE villages ADD COLUMN IF NOT EXISTS district VARCHAR(128)",
        "ALTER TABLE villages ADD COLUMN IF NOT EXISTS crop VARCHAR(128)",
        "ALTER TABLE soil_health ADD COLUMN IF NOT EXISTS phosphorus FLOAT",
        "ALTER TABLE soil_health ADD COLUMN IF NOT EXISTS potassium FLOAT",
        "ALTER TABLE soil_health ADD COLUMN IF NOT EXISTS moisture FLOAT",
    ]
    for stmt in alter_stmts:
        try:
            session.execute(text(stmt))
        except Exception as e:
            log.warning("Column alter skipped: %s", e)
    session.commit()
    log.info("✔ Database columns verified")


# ─── Main seed logic ──────────────────────────────────────────────────────
def seed():
    session = SessionLocal()
    try:
        add_missing_columns(session)

        # ── 1. Villages ──────────────────────────────────────────────────
        village_ids = {}
        for v in DEMO_VILLAGES:
            vid = demo_uuid(f"village:{v['name']}")
            existing = session.query(Village).filter(Village.name == v['name']).first()
            if existing:
                existing.district = v['district']
                existing.crop = v['crop']
                existing.latitude = v['lat']
                existing.longitude = v['lon']
                existing.id = existing.id  # keep existing UUID
                village_ids[v['name']] = existing.id
                log.info("  ↻ Village '%s' updated", v['name'])
            else:
                village = Village(
                    id=vid, name=v['name'], district=v['district'], crop=v['crop'],
                    latitude=v['lat'], longitude=v['lon'],
                )
                session.add(village)
                village_ids[v['name']] = vid
                log.info("  + Village '%s' created (%s)", v['name'], vid)
        session.commit()
        log.info("✔ %d villages seeded", len(DEMO_VILLAGES))

        # ── 2. Demo users ────────────────────────────────────────────────
        # Assign demo-farmer to first village (Rajpur → alphabetically first is Baramati)
        first_village_id = village_ids.get('Baramati') or list(village_ids.values())[0]
        for u in DEMO_USERS:
            existing = session.query(User).filter(User.email == u['email']).first()
            if existing:
                existing.is_active = True
                log.info("  ↻ User '%s' already exists", u['email'])
            else:
                user = User(
                    id=demo_uuid(f"user:{u['email']}"),
                    email=u['email'],
                    hashed_password=get_password_hash(u['password']),
                    role=u['role'],
                    is_active=True,
                    village_id=first_village_id if u['role'] == 'farmer' else None,
                )
                session.add(user)
                log.info("  + User '%s' created (role=%s)", u['email'], u['role'])
        session.commit()
        log.info("✔ Demo users seeded")

        # ── 3. Weather data (per village, 5 records) ─────────────────────
        now = datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc)
        for vname, vid in village_ids.items():
            # Delete existing weather for this village
            session.query(WeatherData).filter(WeatherData.village_id == vid).delete()
            for i, w in enumerate(DEMO_WEATHER_DB_ORDER):
                # Most recent first: now, now-1day, now-2day, ...
                recorded = now - timedelta(days=i)
                wd = WeatherData(
                    id=demo_uuid(f"weather:{vname}:{i}"),
                    village_id=vid,
                    city=vname,
                    temperature=w['temperature'],
                    humidity=w['humidity'],
                    rainfall=w['rainfall'],
                    wind_speed=round(2.5 + i * 0.3, 1),
                    description=w['description'],
                    recorded_at=recorded,
                )
                session.add(wd)
        session.commit()
        log.info("✔ Weather data seeded (%d records)", len(DEMO_VILLAGES) * len(DEMO_WEATHER_DB_ORDER))

        # ── 4. Market data (farmer weekly + admin monthly) ───────────────
        for vname, vid in village_ids.items():
            session.query(MarketPrice).filter(MarketPrice.village_id == vid).delete()

            # Farmer weekly records (5 most recent days)
            for i, price in enumerate(DEMO_MARKET_FARMER_DB_ORDER):
                created = now - timedelta(days=i)
                mp = MarketPrice(
                    id=demo_uuid(f"market:farmer:{vname}:{i}"),
                    village_id=vid,
                    commodity='Rice',
                    variety='Common',
                    modal_price=price,
                    min_price=round(price * 0.85),
                    max_price=round(price * 1.15),
                    market_name=f"{vname} Mandi",
                    arrival_date=created,
                    created_at=created,
                )
                session.add(mp)

            # Admin monthly records (5 months for admin trend)
            for j, (month_dt, price) in enumerate(DEMO_MARKET_ADMIN_MONTHLY):
                mp = MarketPrice(
                    id=demo_uuid(f"market:admin:{vname}:{j}"),
                    village_id=vid,
                    commodity='Rice',
                    variety='Common',
                    modal_price=price,
                    min_price=round(price * 0.88),
                    max_price=round(price * 1.12),
                    market_name=f"{vname} Mandi",
                    arrival_date=month_dt,
                    created_at=month_dt,
                )
                session.add(mp)
        session.commit()
        total_market = len(DEMO_VILLAGES) * (len(DEMO_MARKET_FARMER_DB_ORDER) + len(DEMO_MARKET_ADMIN_MONTHLY))
        log.info("✔ Market data seeded (%d records)", total_market)

        # ── 5. Risk scores (per village current + monthly trend) ──────────
        for vname, vid in village_ids.items():
            session.query(RiskScore).filter(RiskScore.village_id == vid).delete()

            # Find village score from DEMO_VILLAGES
            village_data = next(v for v in DEMO_VILLAGES if v['name'] == vname)
            score = village_data['score']

            # Current risk score (most recent)
            rs = RiskScore(
                id=demo_uuid(f"risk:current:{vname}"),
                village_id=vid,
                score=score,
                risk_level=_risk_level(score),
                breakdown={
                    'weather': round(score * 0.4),
                    'market': round(score * 0.3),
                    'soil': round(score * 0.2),
                    'historical': round(score * 0.1),
                    'has_weather_data': True,
                    'has_soil_data': True,
                },
                calculated_at=now,
            )
            session.add(rs)

            # Monthly risk scores for admin trend (uniform per month)
            for k, (month_dt, trend_score) in enumerate(DEMO_RISK_TREND_MONTHLY):
                rs_trend = RiskScore(
                    id=demo_uuid(f"risk:trend:{vname}:{k}"),
                    village_id=vid,
                    score=trend_score,
                    risk_level=_risk_level(trend_score),
                    breakdown={'source': 'demo_trend'},
                    calculated_at=month_dt,
                )
                session.add(rs_trend)
        session.commit()
        total_risk = len(DEMO_VILLAGES) * (1 + len(DEMO_RISK_TREND_MONTHLY))
        log.info("✔ Risk scores seeded (%d records)", total_risk)

        # ── 6. Soil health (per village) ──────────────────────────────────
        for vname, vid in village_ids.items():
            session.query(SoilHealth).filter(SoilHealth.village_id == vid).delete()
            sh = SoilHealth(
                id=demo_uuid(f"soil:{vname}"),
                village_id=vid,
                ph=DEMO_SOIL['ph'],
                organic_matter=DEMO_SOIL['organic_matter'],
                nitrogen=DEMO_SOIL['nitrogen'],
                phosphorus=DEMO_SOIL['phosphorus'],
                potassium=DEMO_SOIL['potassium'],
                moisture=DEMO_SOIL['moisture'],
            )
            session.add(sh)
        session.commit()
        log.info("✔ Soil health seeded (%d records)", len(DEMO_VILLAGES))

        # ── 7. AI Advisory reports (per village) ──────────────────────────
        for vname, vid in village_ids.items():
            session.query(AiReport).filter(
                AiReport.village_id == vid, AiReport.report_type == 'advisory'
            ).delete()
            report = AiReport(
                id=demo_uuid(f"advisory:{vname}"),
                village_id=vid,
                report_type='advisory',
                content={'items': DEMO_ADVISORY},
                created_at=now,
            )
            session.add(report)
        session.commit()
        log.info("✔ Advisory reports seeded (%d records)", len(DEMO_VILLAGES))

        # ── 8. Flush Redis cache so fresh data is served ──────────────────
        try:
            import redis
            r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379, db=0)
            keys = r.keys('risk:village:*') + r.keys('ai:village:*')
            if keys:
                r.delete(*keys)
                log.info("✔ Redis cache cleared (%d keys)", len(keys))
            else:
                log.info("✔ Redis cache already empty")
        except Exception as e:
            log.warning("Redis flush skipped: %s", e)

        # ── Summary ──────────────────────────────────────────────────────
        log.info("")
        log.info("=" * 60)
        log.info("  SEED COMPLETE")
        log.info("  Villages:       %d", len(DEMO_VILLAGES))
        log.info("  Demo users:     %d", len(DEMO_USERS))
        log.info("  Weather records: %d", len(DEMO_VILLAGES) * len(DEMO_WEATHER_DB_ORDER))
        log.info("  Market records:  %d", total_market)
        log.info("  Risk scores:    %d", total_risk)
        log.info("  Soil records:   %d", len(DEMO_VILLAGES))
        log.info("  Advisory:       %d", len(DEMO_VILLAGES))
        log.info("=" * 60)

    except Exception:
        session.rollback()
        log.exception("SEED FAILED — rolled back")
        sys.exit(1)
    finally:
        session.close()


if __name__ == '__main__':
    seed()
