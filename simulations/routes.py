from __future__ import annotations

"""Routes for simulations dashboard."""

from flask import current_app, render_template, request
from flask_login import login_required

import pandas as pd

from services.auth import role_required
from services.data import INPUT_COLUMNS

from . import simulations_bp
from .what_if import simulate_variable_sensitivity
from .age_projection import age_risk_projection


@simulations_bp.route("/")
@login_required
@role_required(["Doctor", "SuperAdmin"])
def index():
    """Render simulations page with enabled modules."""
    model = current_app.model
    features = current_app.config.get("SIMULATION_FEATURES", {})

    # Collect full patient data (defaults provided)
    baseline = {
        "age": int(request.args.get("age", 50)),
        "sex": int(request.args.get("sex", 1)),
        "chest_pain_type": request.args.get("chest_pain_type", "non-anginal"),
        "resting_blood_pressure": float(request.args.get("resting_blood_pressure", 120)),
        "cholesterol": float(request.args.get("cholesterol", 200)),
        "fasting_blood_sugar": int(request.args.get("fasting_blood_sugar", 0)),
        "Restecg": request.args.get("Restecg", "normal"),
        "max_heart_rate_achieved": float(request.args.get("max_heart_rate_achieved", 150)),
        "exercise_induced_angina": int(request.args.get("exercise_induced_angina", 0)),
        "st_depression": float(request.args.get("st_depression", 1.0)),
        "st_slope_type": request.args.get("st_slope_type", "flat"),
        "num_major_vessels": int(request.args.get("num_major_vessels", 0)),
        "thalassemia_type": request.args.get("thalassemia_type", "normal"),
    }

    results: dict = {}
    errors: dict = {}
    prediction = None

    # Baseline prediction with confidence
    try:
        X = pd.DataFrame([baseline], columns=INPUT_COLUMNS)
        yhat = int(model.predict(X)[0])
        pos_prob = (
            float(model.predict_proba(X)[0][1])
            if hasattr(model, "predict_proba")
            else None
        )
        confidence = pos_prob if yhat == 1 else (1.0 - pos_prob) if pos_prob is not None else None
        prediction = {
            "label": "Heart Disease" if yhat == 1 else "No Heart Disease",
            "risk_pct": round(pos_prob * 100.0, 1) if pos_prob is not None else None,
            "confidence_pct": round(confidence * 100.0, 1) if confidence is not None else None,
        }
    except Exception as e:  # pragma: no cover - defensive
        errors["prediction"] = str(e)

    if features.get("what_if"):
        try:
            variable = request.args.get("variable", "cholesterol")
            ranges = {
                "age": (0, 120),
                "resting_blood_pressure": (80, 250),
                "cholesterol": (100, 600),
                "max_heart_rate_achieved": (60, 220),
                "st_depression": (0, 10),
            }
            vmin, vmax = ranges.get(variable, (baseline.get(variable, 0) - 50, baseline.get(variable, 0) + 50))
            steps = 50
            step = (vmax - vmin) / steps
            values = [vmin + i * step for i in range(steps + 1)]
            raw = simulate_variable_sensitivity(model, baseline, variable, values)
            seg = {
                "low": [r for r in raw if r["risk_pct"] < 30],
                "mid": [r for r in raw if 30 <= r["risk_pct"] < 60],
                "high": [r for r in raw if r["risk_pct"] >= 60],
            }
            results["what_if"] = {"variable": variable, "segments": seg}
        except Exception as e:  # pragma: no cover - defensive
            errors["what_if"] = str(e)

    if features.get("age_projection"):
        try:
            start = int(baseline["age"])
            end = start + 20
            raw = age_risk_projection(model, baseline, start, end)
            seg = {
                "low": [r for r in raw if r["risk_pct"] < 30],
                "mid": [r for r in raw if 30 <= r["risk_pct"] < 60],
                "high": [r for r in raw if r["risk_pct"] >= 60],
            }
            results["age_projection"] = seg
        except Exception as e:  # pragma: no cover - defensive
            errors["age_projection"] = str(e)

    return render_template(
        "simulations/index.html",
        features=features,
        baseline=baseline,
        prediction=prediction,
        results=results,
        errors=errors,
    )
