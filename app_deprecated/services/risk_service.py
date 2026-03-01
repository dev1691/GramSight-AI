from typing import Dict
from ..modules.risk_engine.engine import compute_risk


def get_risk_for_village(village_id: int) -> Dict:
    """Service wrapper to compute risk for a given village.

    TODO: Replace with DB reads and caching. For now call the risk_engine placeholder.
    """
    score = compute_risk(village_id)
    category = "low"
    if score > 0.7:
        category = "high"
    elif score > 0.4:
        category = "medium"

    return {"village_id": village_id, "score": score, "category": category}
