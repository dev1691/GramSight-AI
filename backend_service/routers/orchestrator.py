from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database_async import get_async_db
from services.data_orchestrator import refresh_village_data
import logging

router = APIRouter(prefix='/orchestrator', tags=['orchestrator'])
logger = logging.getLogger('backend.orchestrator')


@router.post('/refresh')
async def refresh(village_id: str, lat: float = None, lon: float = None, crops: list[str] | None = None, state: str = None, district: str = None, db: AsyncSession = Depends(get_async_db)):
    try:
        res = await refresh_village_data(db, village_id, lat=lat, lon=lon, crops=crops, state=state, district=district)
        return {'status': 'ok', 'result': res}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception('Orchestrator failed')
        raise HTTPException(status_code=500, detail='orchestrator failed')
