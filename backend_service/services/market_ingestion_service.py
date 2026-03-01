import logging
from datetime import datetime
from dateutil import parser as dateparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from backend_service.config import MARKET_API_KEY
from backend_service.models import MarketPrice
from backend_service.database_async import AsyncSessionLocal

logger = logging.getLogger('backend.market_ingest')

BASE_URL = 'https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24'


async def fetch_market_prices(state: str, district: str, commodity: str, limit: int = 10):
    params = {
        'api-key': MARKET_API_KEY,
        'format': 'json',
        'filters[State]': state,
        'filters[District]': district,
        'filters[Commodity]': commodity,
        'limit': limit
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json()


async def ingest_market(db: AsyncSession, village_id, state: str, district: str, commodity: str):
    try:
        body = await fetch_market_prices(state, district, commodity, limit=10)
    except Exception as e:
        logger.exception('Market API fetch failed')
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
        # avoid duplicates by checking commodity + arrival_date
        # simple approach: check existing modal by arrival_date and commodity
        # avoid duplicates using ORM
        if arrival_dt is not None:
            exists_q = await db.execute(select(MarketPrice).where(MarketPrice.commodity == commodity).where(MarketPrice.arrival_date == arrival_dt).limit(1))
            if exists_q.scalars().first():
                continue
        rec = MarketPrice(
            village_id=village_id,
            commodity=commodity,
            variety=variety,
            min_price=float(minp) if minp else None,
            max_price=float(maxp) if maxp else None,
            modal_price=float(modal) if modal else None,
            arrival_date=arrival_dt,
            market_name=market_name,
            created_at=datetime.utcnow()
        )
        db.add(rec)
        saved.append(rec)

    await db.commit()
    for s in saved:
        await db.refresh(s)
    return saved


async def ingest_market_for_all_villages(state: str = None, district: str = None, commodity: str = None):
    """Worker helper to ingest market data for all villages optionally filtered."""
    from backend_service.models import Village
    async with AsyncSessionLocal() as session:
        q = select(Village)
        res = await session.execute(q)
        villages = res.scalars().all()
        out = []
        for v in villages:
            try:
                sv = await ingest_market(session, v.id, state or '', district or '', commodity or '')
                out.extend(sv)
            except Exception:
                logging.exception(f'Failed market ingest for village {v.id}')
    return out
