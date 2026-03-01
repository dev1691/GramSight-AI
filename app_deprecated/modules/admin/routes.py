from fastapi import APIRouter, Depends
from ...core.dependencies import require_role
from ...models.users import RoleEnum
from fastapi import APIRouter

router = APIRouter()


@router.get("/villages")
async def list_villages(current_user=Depends(require_role(RoleEnum.admin))):
    # TODO: Replace with DB queries
    return [{"id": "00000000-0000-0000-0000-000000000000", "name": "Example Village"}]


@router.get("/village/{village_id}/overview")
async def village_overview(id: str, current_user=Depends(require_role(RoleEnum.admin))):
    # TODO: Return real overview data
    return {"village_id": id, "name": "Example Village", "risk_score": 0.42}
