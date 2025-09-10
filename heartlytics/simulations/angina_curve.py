from __future__ import annotations

"""Simulation of risk curves for exercise-induced angina."""

from typing import Dict, Iterable, List

import pandas as pd

from ..services.data import INPUT_COLUMNS


def simulate_angina_sensitivity(
    model, baseline: Dict[str, object], variable: str, values: Iterable[float]
) -> Dict[str, List[Dict[str, float]]]:
    """Return risk percentages for each value of *variable* with and without angina.

    Parameters
    ----------
    model: object
        Trained model supporting ``predict_proba``.
    baseline: dict
        Baseline feature values.
    variable: str
        Feature to vary along the X-axis.
    values: iterable of float
        Values to substitute for ``variable``.
    """
    if not hasattr(model, "predict_proba"):
        return {"no": [], "yes": []}

    base = baseline.copy()
    no: List[Dict[str, float]] = []
    yes: List[Dict[str, float]] = []
    for v in values:
        row_no = base.copy()
        row_yes = base.copy()
        row_no[variable] = v
        row_yes[variable] = v
        row_no["exercise_induced_angina"] = 0
        row_yes["exercise_induced_angina"] = 1
        X = pd.DataFrame([row_no, row_yes], columns=INPUT_COLUMNS)
        probs = model.predict_proba(X)[:, 1]
        no.append({"value": v, "risk_pct": round(probs[0] * 100.0, 1)})
        yes.append({"value": v, "risk_pct": round(probs[1] * 100.0, 1)})
    return {"no": no, "yes": yes}
