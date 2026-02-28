from typing import Dict


def compute_risk(village_id: int) -> float:
    """Placeholder weighted risk formula.

    TODO: Replace with real feature extraction, weights, and ML model.
    """
    # Simple deterministic placeholder using id to vary result
    base = (village_id % 10) / 10.0
    # pretend we combined weather/soil/market factors
    weather_factor = 0.3
    soil_factor = 0.2
    market_factor = 0.2

    score = min(1.0, base * (weather_factor + soil_factor + market_factor) + 0.1)
    return round(score, 3)
