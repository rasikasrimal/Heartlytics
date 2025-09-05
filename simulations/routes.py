from __future__ import annotations

"""Routes for simulations dashboard."""

from flask import current_app, render_template, request
from flask_login import login_required

from services.auth import role_required

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

    # baseline defaults; developers may expand to collect from user input
    baseline = {
        "age": int(request.args.get("age", 50)),
        "sex": 1,
        "chest_pain_type": "non-anginal",
        "resting_blood_pressure": float(request.args.get("resting_blood_pressure", 120)),
        "cholesterol": float(request.args.get("cholesterol", 200)),
        "fasting_blood_sugar": 0,
        "Restecg": "normal",
        "max_heart_rate_achieved": 150,
        "exercise_induced_angina": 0,
        "st_depression": 1.0,
        "st_slope_type": "flat",
        "num_major_vessels": 0,
        "thalassemia_type": "normal",
    }

    results = {}
    errors = {}

    if features.get("what_if"):
        try:
            variable = request.args.get("variable", "cholesterol")
            base_val = baseline.get(variable, 0)
            # simple +/- range around baseline
            values = [base_val - 50, base_val, base_val + 50]
            results["what_if"] = {
                "variable": variable,
                "data": simulate_variable_sensitivity(model, baseline, variable, values),
            }
        except Exception as e:  # pragma: no cover - defensive
            errors["what_if"] = str(e)

    if features.get("age_projection"):
        try:
            start = int(baseline["age"])
            end = start + 20
            results["age_projection"] = age_risk_projection(model, baseline, start, end)
        except Exception as e:  # pragma: no cover - defensive
            errors["age_projection"] = str(e)

    return render_template(
        "simulations/index.html",
        features=features,
        results=results,
        errors=errors,
    )
