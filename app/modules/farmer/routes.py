from fastapi import APIRouter, Depends
from ...services.risk_service import get_risk_for_village
from ...core.dependencies import require_role
from ...models.users import RoleEnum

router = APIRouter()


@router.get("/{village_id}/risk")
async def get_risk(village_id: int, current_user=Depends(require_role(RoleEnum.farmer))):
    """Return mock risk for a village. Business logic lives in services."""
    risk = get_risk_for_village(village_id)
    return {"village_id": village_id, "risk": risk}


@router.get("/{village_id}/weather")
async def get_weather(village_id: int, current_user=Depends(require_role(RoleEnum.farmer))):
    # TODO: Replace with DB query
    return {"village_id": village_id, "weather": {"temperature": 28.5, "precipitation": 0.0}}


@router.get("/{village_id}/market")
async def get_market(village_id: int, current_user=Depends(require_role(RoleEnum.farmer))):
    # TODO: Replace with DB query
    return {"village_id": village_id, "markets": [{"commodity": "wheat", "price": 250.0}]}
