from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend_service.database import get_db
from backend_service.services.market_service import create_market_entry
from backend_service.schemas import MarketOut, MarketCreate
from backend_service.core.dependencies import get_current_active_user
import logging

from backend_service.database_async import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend_service.services.market_ingestion_service import ingest_market

router = APIRouter(prefix='/market', tags=['market'])
logger = logging.getLogger('backend')


@router.post('/fetch', response_model=MarketOut)
def fetch_market(payload: MarketCreate, db: Session = Depends(get_db), _user=Depends(get_current_active_user)):
    try:
        rec = create_market_entry(db, payload.commodity, payload.modal_price, payload.market_name)
        return rec
    except Exception as e:
        logger.exception('Failed to save market data')
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/ingest')
async def ingest(village_id: str, state: str, district: str, commodity: str, db: AsyncSession = Depends(get_async_db), _user=Depends(get_current_active_user)):
    try:
        saved = await ingest_market(db, village_id, state, district, commodity)
        return {'saved': len(saved)}
    except Exception as e:
        logger.exception('Failed to ingest market data')
        raise HTTPException(status_code=500, detail=str(e))
