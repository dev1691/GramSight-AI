from pydantic import BaseModel
from typing import List, Optional


class FarmerRiskItem(BaseModel):
    village_id: int
    score: float
    category: str


class FarmerRiskResponse(BaseModel):
    village_id: int
    risk: FarmerRiskItem
    explanation: Optional[str] = None


class VillageOverviewResponse(BaseModel):
    village_id: int
    name: str
    latest_weather: Optional[dict] = None
    market_summary: Optional[List[dict]] = None
    risk_score: Optional[float] = None

    class Config:
        orm_mode = True
