from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import Dict, Any

from backend_service.core.dependencies import require_role, get_current_active_user
from backend_service.models import RoleEnum
from backend_service.services import risk_engine_service
from backend_service import cache

router = APIRouter(prefix="")


@router.post('/internal/calculate-risk/{village_id}')
async def calc_village_risk(village_id: UUID, current_user=Depends(require_role(RoleEnum.admin))):
    key = f"risk:village:{village_id}"
    # force recalculation
    res = await risk_engine_service.calculate_village_risk(village_id)
    await cache.set_cached(key, res, ttl=6 * 3600)
    return res


@router.post('/farmer/calculate-risk')
async def calc_farmer_risk(payload: Dict[str, str], current_user=Depends(require_role(RoleEnum.farmer))):
    # payload must contain farmer_id and village_id
    farmer_id = payload.get('farmer_id')
    village_id = payload.get('village_id')
    if not farmer_id or not village_id:
        raise HTTPException(status_code=400, detail='farmer_id and village_id required')
    res = await risk_engine_service.calculate_farmer_risk(UUID(farmer_id), UUID(village_id))
    key = f"risk:farmer:{farmer_id}"
    await cache.set_cached(key, res, ttl=6 * 3600)
    return res


@router.get('/admin/risk/{village_id}')
async def get_admin_risk(village_id: UUID, current_user=Depends(require_role(RoleEnum.admin))):
    key = f"risk:village:{village_id}"
    cached = await cache.get_cached(key)
    if cached:
        return cached
    res = await risk_engine_service.calculate_village_risk(village_id)
    await cache.set_cached(key, res, ttl=6 * 3600)
    return res


@router.get('/farmer/risk')
async def get_farmer_risk(current_user=Depends(get_current_active_user)):
    farmer_id = getattr(current_user, 'id', None)
    if not farmer_id:
        raise HTTPException(status_code=400, detail='farmer id missing')
    key = f"risk:farmer:{farmer_id}"
    cached = await cache.get_cached(key)
    if cached:
        return cached
    # try to use village_id from user
    village_id = getattr(current_user, 'village_id', None)
    if not village_id:
        raise HTTPException(status_code=400, detail='village_id required for farmer risk')
    res = await risk_engine_service.calculate_farmer_risk(UUID(str(farmer_id)), UUID(str(village_id)))
    await cache.set_cached(key, res, ttl=6 * 3600)
    return res
