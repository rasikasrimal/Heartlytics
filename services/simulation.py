from __future__ import annotations

from typing import List, Dict

import pandas as pd

from .data import INPUT_COLUMNS


def simulate_risk_over_time(model, patient_record: Dict[str, object], start_age: int, end_age: int) -> List[Dict[str, float]]:
    """Simulate future heart disease risk by varying age only.

    Parameters
    ----------
    model : object
        Trained model with ``predict_proba`` support.
    patient_record : dict
        Baseline feature values for a single patient.
    start_age : int
        Current age of the patient.
    end_age : int
        Final age (inclusive) for simulation.

    Returns
    -------
    list of dict
        Each dict contains ``age`` and ``risk_pct`` keys representing the
        model's positive class probability for that age.
    """
    if not hasattr(model, "predict_proba"):
        return []

    results: List[Dict[str, float]] = []
    base = patient_record.copy()
    for age in range(start_age, end_age + 1):
        row = base.copy()
        row["age"] = age
        X = pd.DataFrame([row], columns=INPUT_COLUMNS)
        prob = float(model.predict_proba(X)[0][1])
        results.append({"age": age, "risk_pct": round(prob * 100.0, 1)})
    return results
