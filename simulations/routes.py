from __future__ import annotations

"""Routes for simulations dashboard."""

from flask import current_app, render_template, request
from flask_login import login_required

import pandas as pd

from services.auth import role_required
from services.data import INPUT_COLUMNS

from . import simulations_bp
from .angina_curve import simulate_angina_sensitivity


@simulations_bp.route("/")
@login_required
@role_required(["Doctor", "SuperAdmin"])
def index():
    """Render simulations page with enabled modules."""
    model = current_app.model

    # Collect full patient data (defaults provided)
    baseline = {
        "age": int(request.args.get("age", 50)),
        "sex": int(request.args.get("sex", 1)),
        "chest_pain_type": request.args.get("chest_pain_type", "non-anginal"),
        "resting_blood_pressure": float(request.args.get("resting_blood_pressure", 120)),
        "cholesterol": float(request.args.get("cholesterol", 200)),
        "fasting_blood_sugar": float(request.args.get("fasting_blood_sugar", 100)),
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

    variable = request.args.get("variable", "age")
    ranges = {
        "age": (0, 120),
        "resting_blood_pressure": (80, 250),
        "cholesterol": (100, 600),
        "fasting_blood_sugar": (60, 200),
        "max_heart_rate_achieved": (60, 220),
        "st_depression": (0, 10),
    }

    try:
        vmin, vmax = ranges.get(
            variable, (baseline.get(variable, 0) - 50, baseline.get(variable, 0) + 50)
        )
        steps = 50
        step = (vmax - vmin) / steps
        values = [vmin + i * step for i in range(steps + 1)]
        curves = simulate_angina_sensitivity(model, baseline, variable, values)
        labels = {
            "age": "Age",
            "cholesterol": "Cholesterol (mg/dL)",
            "resting_blood_pressure": "Resting Blood Pressure (systolic mmHg)",
            "fasting_blood_sugar": "Fasting Blood Sugar / Glucose (mg/dL)",
            "max_heart_rate_achieved": "Max Heart Rate Achieved (bpm)",
        }
        results["exercise_angina"] = {
            "variable": variable,
            "label": labels.get(variable, variable),
            "vmin": vmin,
            "vmax": vmax,
            "no": curves["no"],
            "yes": curves["yes"],
        }
    except Exception as e:  # pragma: no cover - defensive
        errors["exercise_angina"] = str(e)

    return render_template(
        "simulations/index.html",
        baseline=baseline,
        prediction=prediction,
        results=results,
        errors=errors,
    )
