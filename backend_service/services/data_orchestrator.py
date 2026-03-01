import logging
from sqlalchemy.ext.asyncio import AsyncSession
from services.weather_ingestion_service import ingest_weather
from services.market_ingestion_service import ingest_market

logger = logging.getLogger('backend.orchestrator')


async def refresh_village_data(db: AsyncSession, village_id, lat: float = None, lon: float = None, crops: list | None = None, state: str = None, district: str = None):
    """
    Refresh data for a village. If lat/lon not provided, attempt to look up from villages table.
    crops: list of commodity names to fetch market data for.
    state/district: used to restrict market API calls.
    """
    if lat is None or lon is None:
        # attempt to query villages table if present
        try:
            res = await db.execute("SELECT latitude, longitude FROM villages WHERE id = :id LIMIT 1", {'id': str(village_id)})
            row = res.first()
            if row:
                lat, lon = row[0], row[1]
        except Exception:
            logger.info('Villages table not available or village not found; require lat/lon')

    if lat is None or lon is None:
        raise ValueError('lat and lon required to refresh village data')

    saved = {'weather': None, 'market': []}
    # use a transaction for all writes
    async with db.begin():
        try:
            saved['weather'] = await ingest_weather(db, village_id, lat, lon)
        except Exception:
            logger.exception('Weather ingestion failed')

        if crops:
            for c in crops:
                try:
                    s = await ingest_market(db, village_id, state or '', district or '', c)
                    saved['market'].extend(s)
                except Exception:
                    logger.exception('Market ingestion failed for %s', c)

    return saved
