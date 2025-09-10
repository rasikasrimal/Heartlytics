from __future__ import annotations

"""Future risk projection simulation module."""

from typing import Dict, List

from ..services.simulation import simulate_risk_over_time


def age_risk_projection(model, baseline: Dict[str, object], start_age: int, end_age: int) -> List[Dict[str, float]]:
    """Wrapper around :func:`simulate_risk_over_time` for clarity."""
    return simulate_risk_over_time(model, baseline, start_age, end_age)
