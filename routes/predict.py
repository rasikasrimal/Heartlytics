from __future__ import annotations

import pandas as pd
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_required

from services.security import csrf_protect
from services.data import (
    INPUT_COLUMNS,
    NUMERIC_COLS,
    CATEGORICAL_COLS,
)
from services.simulation import simulate_risk_over_time


predict_bp = Blueprint("predict", __name__, url_prefix="/")


@predict_bp.get("/predict")
@login_required
def predict_page():
    """Display a single patient prediction overview."""
    return render_template(
        "predict/result.html",
        pred=None,
        pos_prob=None,
        risk_band=None,
        risk_pct=None,
        risk_pct_val=None,
        confidence_pct=None,
        confidence_pct_val=None,
        projection=None,
    )


@predict_bp.post("/predict")
@login_required
@csrf_protect
def predict():
    """Handle single prediction submissions."""
    # Access shared objects via ``current_app`` to avoid importing the main
    # module, which can create a secondary Flask application instance.
    db = current_app.db
    Prediction = current_app.Prediction
    model = current_app.model
    model_name = current_app.model_name

    if model is None:
        flash("Model not loaded. Please place ml/model.pkl and restart the app.", "error")
        return redirect(url_for("index"))

    payload = {k: request.form.get(k) for k in (["patient_name"] + INPUT_COLUMNS)}

    errors = {}
    cleaned: dict[str, object] = {}

    # numerics
    for col, caster in NUMERIC_COLS.items():
        try:
            v = caster((payload.get(col) or "").strip())
            cleaned[col] = v
        except Exception:
            errors[col] = f"Must be {caster.__name__}"

    # categoricals
    for col, allowed in CATEGORICAL_COLS.items():
        v = (payload.get(col) or "").strip()
        if v not in allowed:
            errors[col] = f"Must be one of: {', '.join(sorted(allowed))}"
        else:
            cleaned[col] = v

    # optional patient_name
    patient_name = (payload.get("patient_name") or "").strip()
    if patient_name and len(patient_name) > 120:
        errors["patient_name"] = "Max length is 120"

    if errors:
        for f, msg in errors.items():
            flash(f"{f}: {msg}", "error")
        return redirect(url_for("index"))

    row = {col: cleaned[col] for col in INPUT_COLUMNS}
    X = pd.DataFrame([row], columns=INPUT_COLUMNS)

    try:
        yhat = int(model.predict(X)[0])
        pos_prob = float(model.predict_proba(X)[0][1]) if hasattr(model, "predict_proba") else None
        confidence = pos_prob if yhat == 1 else (1.0 - pos_prob) if pos_prob is not None else 0.5
        confidence_pct_val = round(confidence * 100, 1)
    except Exception as e:
        flash(f"Prediction failed: {e}", "error")
        return redirect(url_for("index"))

    pred = Prediction(
        patient_name=patient_name or None,
        age=int(cleaned["age"]),
        sex=int(cleaned["sex"]),
        chest_pain_type=str(cleaned["chest_pain_type"]),
        resting_bp=float(cleaned["resting_blood_pressure"]),
        cholesterol=float(cleaned["cholesterol"]),
        fasting_blood_sugar=int(cleaned["fasting_blood_sugar"]),
        resting_ecg=str(cleaned["Restecg"]),
        max_heart_rate=float(cleaned["max_heart_rate_achieved"]),
        exercise_angina=int(cleaned["exercise_induced_angina"]),
        oldpeak=float(cleaned["st_depression"]),
        st_slope=str(cleaned["st_slope_type"]),
        num_major_vessels=int(cleaned["num_major_vessels"]),
        thalassemia_type=str(cleaned["thalassemia_type"]),
        prediction=yhat,
        confidence=float(confidence),
        model_version=model_name
    )

    db.session.add(pred)
    db.session.commit()

    # risk band
    risk_band = None
    risk_pct_val: float | None = None
    risk_pct: str | None = None
    if pos_prob is not None:
        risk_pct_val = round(pos_prob * 100.0, 1)
        risk_pct = f"{risk_pct_val:.1f}%"
        rp = risk_pct_val
        risk_band = "Low" if rp < 30 else "Moderate" if rp < 60 else "High"

    projection = simulate_risk_over_time(model, row, int(cleaned["age"]), 90)

    return render_template(
        "predict/result.html",
        pred=pred,
        pos_prob=pos_prob,
        label_text="Heart Disease: YES" if yhat == 1 else "Heart Disease: NO",
        confidence_pct=f"{confidence_pct_val:.1f}%",
        confidence_pct_val=confidence_pct_val,
        risk_band=risk_band,
        risk_pct=risk_pct,
        risk_pct_val=risk_pct_val,
        projection=projection,
    )
