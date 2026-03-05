from typing import Dict


def generate_advisory(village_data: Dict) -> str:
    """Return a mock AI advisory explanation string.

    TODO: Integrate with real AI/ML advisory engine and templates.
    """
    # Simple placeholder explanation
    name = village_data.get("name", "the village")
    return f"Preliminary advisory for {name}: monitor soil moisture and local market prices."
