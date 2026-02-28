from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from ...core.dependencies import require_role
from ...models.users import RoleEnum

router = APIRouter()


class WeatherIngestPayload(BaseModel):
    village_id: int
    temperature: float | None = None
    precipitation: float | None = None
    humidity: float | None = None


@router.post("/weather")
async def ingest_weather(payload: WeatherIngestPayload, background_tasks: BackgroundTasks, current_user=Depends(require_role(RoleEnum.admin))):
    # TODO: Persist to DB and trigger downstream processing (risk recompute)
    # Placeholder: schedule an async background task stub
    def _stub_process(data):
        # stub for calling external APIs or heavier processing
        pass

    background_tasks.add_task(_stub_process, payload.dict())
    return {"status": "accepted"}
