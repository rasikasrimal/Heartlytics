from __future__ import annotations

"""Routes for simulations dashboard."""

from flask import current_app, render_template, request, jsonify
from flask_login import login_required

import pandas as pd

from ..auth.decorators import require_roles
from ..services.data import INPUT_COLUMNS

from . import simulations_bp
from .angina_curve import simulate_angina_sensitivity


def _run_simulation(form: dict, defaults: dict):
    """Execute the heart disease risk simulation."""
    model = current_app.model

    baseline = {
        "age": int(form.get("age", defaults["age"])),
        "sex": int(form.get("sex", defaults["sex"])),
        "chest_pain_type": form.get("chest_pain_type", defaults["chest_pain_type"]),
        "resting_blood_pressure": float(
            form.get("resting_blood_pressure", defaults["resting_blood_pressure"])
        ),
        "cholesterol": float(form.get("cholesterol", defaults["cholesterol"])),
        "fasting_blood_sugar": float(
            form.get("fasting_blood_sugar", defaults["fasting_blood_sugar"])
        ),
        "Restecg": form.get("Restecg", defaults["Restecg"]),
        "max_heart_rate_achieved": float(
            form.get("max_heart_rate_achieved", defaults["max_heart_rate_achieved"])
        ),
        "exercise_induced_angina": int(
            form.get("exercise_induced_angina", defaults["exercise_induced_angina"])
        ),
        "st_depression": float(form.get("st_depression", defaults["st_depression"])),
        "st_slope_type": form.get("st_slope_type", defaults["st_slope_type"]),
        "num_major_vessels": int(
            form.get("num_major_vessels", defaults["num_major_vessels"])
        ),
        "thalassemia_type": form.get("thalassemia_type", defaults["thalassemia_type"]),
    }

    variable = form.get("variable", "age")

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
        confidence = (
            pos_prob if yhat == 1 else (1.0 - pos_prob)
            if pos_prob is not None
            else None
        )
        prediction = {
            "label": "Heart Disease" if yhat == 1 else "No Heart Disease",
            "risk_pct": round(pos_prob * 100.0, 1) if pos_prob is not None else None,
            "confidence_pct": round(confidence * 100.0, 1)
            if confidence is not None
            else None,
        }
    except Exception as e:  # pragma: no cover - defensive
        errors["prediction"] = str(e)

    ranges = {
        "age": (0, 120),
        "resting_blood_pressure": (80, 250),
        "cholesterol": (100, 600),
        "fasting_blood_sugar": (60, 200),
        "max_heart_rate_achieved": (60, 220),
        "st_depression": (0, 6.2),
        "num_major_vessels": (0, 3),
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
            "st_depression": "ST Depression",
            "num_major_vessels": "Num Major Vessels",
        }
        current = simulate_angina_sensitivity(
            model, baseline, variable, [baseline[variable]]
        )
        current_key = "yes" if baseline["exercise_induced_angina"] else "no"
        results["exercise_angina"] = {
            "variable": variable,
            "label": labels.get(variable, variable),
            "vmin": vmin,
            "vmax": vmax,
            "no": curves["no"],
            "yes": curves["yes"],
            "current": {
                "value": baseline[variable],
                "risk_pct": current[current_key][0]["risk_pct"],
                "angina": baseline["exercise_induced_angina"],
            },
        }
    except Exception as e:  # pragma: no cover - defensive
        errors["exercise_angina"] = str(e)

    return baseline, prediction, results, errors, variable


@simulations_bp.route("/", methods=["GET"])
@login_required
@require_roles("Doctor", "SuperAdmin")
def index():
    """Render simulations page with enabled modules."""
    defaults = {
        "age": 50,
        "sex": 1,
        "chest_pain_type": "non-anginal",
        "resting_blood_pressure": 120.0,
        "cholesterol": 200.0,
        "fasting_blood_sugar": 100.0,
        "Restecg": "normal",
        "max_heart_rate_achieved": 150.0,
        "exercise_induced_angina": 0,
        "st_depression": 1.0,
        "st_slope_type": "flat",
        "num_major_vessels": 0,
        "thalassemia_type": "normal",
    }
    baseline = defaults.copy()
    return render_template("simulations/index.html", baseline=baseline)


@simulations_bp.route("/run", methods=["POST"])
@login_required
@require_roles("Doctor", "SuperAdmin")
def run():
    """Run simulation and return JSON data."""
    defaults = {
        "age": 50,
        "sex": 1,
        "chest_pain_type": "non-anginal",
        "resting_blood_pressure": 120.0,
        "cholesterol": 200.0,
        "fasting_blood_sugar": 100.0,
        "Restecg": "normal",
        "max_heart_rate_achieved": 150.0,
        "exercise_induced_angina": 0,
        "st_depression": 1.0,
        "st_slope_type": "flat",
        "num_major_vessels": 0,
        "thalassemia_type": "normal",
    }
    baseline, prediction, results, errors, variable = _run_simulation(
        request.form, defaults
    )
    return jsonify(
        baseline=baseline,
        prediction=prediction,
        results=results,
        errors=errors,
        variable=variable,
    )

