import logging
from datetime import datetime, timezone
from dateutil import parser as dateparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from backend_service.config import MARKET_API_KEY
from backend_service.models import MarketPrice
from backend_service.database_async import AsyncSessionLocal

logger = logging.getLogger('backend.market_ingest')

BASE_URL = 'https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24'

# ── District → State lookup (all demo villages are in Maharashtra) ────────
# Extend as needed when new villages are added.
DISTRICT_STATE_MAP = {
    'Pune': 'Maharashtra',
    'Sindhudurg': 'Maharashtra',
    'Solapur': 'Maharashtra',
    'Satara': 'Maharashtra',
    'Mumbai': 'Maharashtra',
    'Nashik': 'Maharashtra',
    'Nagpur': 'Maharashtra',
    'Kolhapur': 'Maharashtra',
}
DEFAULT_STATE = 'Maharashtra'
DEFAULT_COMMODITY = 'Rice'


async def fetch_market_prices(state: str, district: str, commodity: str, limit: int = 10):
    filters = {}
    if state:
        filters['filters[State]'] = state
    if district:
        filters['filters[District]'] = district
    if commodity:
        filters['filters[Commodity]'] = commodity

    params = {
        'api-key': MARKET_API_KEY,
        'format': 'json',
        'limit': limit,
        **filters,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json()


async def ingest_market(db: AsyncSession, village_id, state: str, district: str,
                        commodity: str, *, auto_commit: bool = True):
    # ── Validate inputs — never call API with empty filters ───────────
    if not state or not commodity:
        logger.warning('Skipping market ingest for village %s — missing state or commodity', village_id)
        return []

    try:
        body = await fetch_market_prices(state, district, commodity, limit=10)
    except Exception:
        logger.exception('Market API fetch failed for village %s', village_id)
        raise

    records = body.get('records') or []
    saved = []
    for r in records:
        arrival = r.get('Arrival_Date')
        arrival_dt = None
        if arrival:
            try:
                arrival_dt = dateparser.parse(arrival)
            except Exception:
                try:
                    arrival_dt = datetime.fromisoformat(arrival)
                except Exception:
                    arrival_dt = None
        variety = r.get('Variety') or None
        modal = r.get('Modal_Price')
        minp = r.get('Min_Price')
        maxp = r.get('Max_Price')
        market_name = r.get('Market') or r.get('Market_Name') or None

        # ── Validate price values ────────────────────────────────────
        try:
            modal_f = float(modal) if modal else None
        except (ValueError, TypeError):
            modal_f = None
        try:
            min_f = float(minp) if minp else None
        except (ValueError, TypeError):
            min_f = None
        try:
            max_f = float(maxp) if maxp else None
        except (ValueError, TypeError):
            max_f = None

        # Skip records with no usable price at all
        if modal_f is None and min_f is None and max_f is None:
            logger.debug('Skipping market record with no valid prices')
            continue

        # Reject obviously invalid prices (negative or absurdly high)
        if modal_f is not None and (modal_f < 0 or modal_f > 500000):
            logger.warning('Rejecting invalid modal_price %.2f', modal_f)
            continue

        # ── Deduplication: commodity + arrival_date + village_id ──────
        if arrival_dt is not None:
            exists_q = await db.execute(
                select(MarketPrice).where(
                    MarketPrice.commodity == commodity,
                    MarketPrice.arrival_date == arrival_dt,
                    MarketPrice.village_id == village_id,
                ).limit(1)
            )
            if exists_q.scalars().first():
                continue

        rec = MarketPrice(
            village_id=village_id,
            commodity=commodity,
            variety=variety,
            min_price=min_f,
            max_price=max_f,
            modal_price=modal_f,
            arrival_date=arrival_dt,
            market_name=market_name,
            created_at=datetime.now(timezone.utc),
        )
        db.add(rec)
        saved.append(rec)

    if auto_commit:
        await db.commit()
        for s in saved:
            await db.refresh(s)
    return saved


async def ingest_market_for_all_villages(state: str = None, district: str = None,
                                         commodity: str = None):
    """Worker helper to ingest market data for all villages.

    Uses each village's own district and crop for targeted API queries
    instead of sending empty filters.
    """
    from backend_service.models import Village
    async with AsyncSessionLocal() as session:
        q = select(Village)
        res = await session.execute(q)
        villages = res.scalars().all()
        out = []
        for v in villages:
            # Derive state/district/commodity from village metadata
            v_district = district or getattr(v, 'district', None) or ''
            v_state = state or DISTRICT_STATE_MAP.get(v_district, DEFAULT_STATE)
            v_commodity = commodity or getattr(v, 'crop', None) or DEFAULT_COMMODITY

            if not v_state:
                logger.warning('No state for village %s (district=%s) — skipping market ingest',
                               v.name, v_district)
                continue

            try:
                sv = await ingest_market(session, v.id, v_state, v_district, v_commodity)
                out.extend(sv)
            except Exception:
                logger.exception('Failed market ingest for village %s (%s)', v.name, v.id)
    return out
