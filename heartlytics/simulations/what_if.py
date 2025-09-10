from __future__ import annotations

"""Variable sensitivity (what-if) simulation module."""

from typing import Dict, Iterable, List

import pandas as pd

from ..services.data import INPUT_COLUMNS


def simulate_variable_sensitivity(
    model, baseline: Dict[str, object], variable: str, values: Iterable[float]
) -> List[Dict[str, float]]:
    """Return predicted risk percentages for each ``value`` of ``variable``.

    Parameters
    ----------
    model: object
        Trained model supporting ``predict_proba``.
    baseline: dict
        Baseline feature values.
    variable: str
        Feature name to vary.
    values: iterable
        Values to substitute for ``variable``.
    """
    if not hasattr(model, "predict_proba"):
        return []
    base = baseline.copy()
    results: List[Dict[str, float]] = []
    for v in values:
        row = base.copy()
        row[variable] = v
        X = pd.DataFrame([row], columns=INPUT_COLUMNS)
        prob = float(model.predict_proba(X)[0][1])
        results.append({"value": v, "risk_pct": round(prob * 100.0, 1)})
    return results
