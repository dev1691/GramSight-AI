from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from backend_service.services import ai_analysis_service
from backend_service.core.dependencies import require_role, get_current_active_user
from backend_service.models import RoleEnum
from backend_service import cache

router = APIRouter(prefix="/ai")


@router.post('/farmer/ai-analysis')
async def farmer_ai_analysis(payload: dict, current_user=Depends(require_role(RoleEnum.farmer))):
    farmer_id = payload.get('farmer_id') or getattr(current_user, 'id', None)
    if not farmer_id:
        raise HTTPException(status_code=400, detail='farmer_id required')
    key = f"ai:farmer:{farmer_id}"
    cached = await cache.get_cached(key)
    if cached:
        return cached
    res = await ai_analysis_service.generate_farmer_analysis(UUID(str(farmer_id)))
    await cache.set_cached(key, res, ttl=12 * 3600)
    return res


@router.post('/admin/ai-analysis/{village_id}')
async def admin_ai_analysis(village_id: UUID, current_user=Depends(require_role(RoleEnum.admin))):
    key = f"ai:village:{village_id}"
    cached = await cache.get_cached(key)
    if cached:
        return cached
    res = await ai_analysis_service.generate_village_analysis(village_id)
    await cache.set_cached(key, res, ttl=12 * 3600)
    return res
