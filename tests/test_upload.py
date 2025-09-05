"""Tests for upload workflow."""

import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def test_upload_page(auth_client):
    response = auth_client.get("/upload")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "missing_column, attr",
    [
        ("fasting_blood_sugar", "fasting_blood_sugar"),
        ("exercise_induced_angina", "exercise_angina"),
    ],
)
def test_batch_prediction_handles_missing_int_fields(auth_client, missing_column, attr):
    uid = uuid.uuid4().hex
    uploads_base = Path(auth_client.application.instance_path) / "uploads" / uid
    uploads_base.mkdir(parents=True, exist_ok=True)
    data = {
        "age": [63],
        "sex": [1],
        "chest_pain_type": ["typical_angina"],
        "resting_blood_pressure": [145.0],
        "cholesterol": [233.0],
        "fasting_blood_sugar": [0],
        "Restecg": ["normal"],
        "max_heart_rate_achieved": [150.0],
        "exercise_induced_angina": [0],
        "st_depression": [2.3],
        "st_slope_type": ["upsloping"],
        "num_major_vessels": [0],
        "thalassemia_type": ["normal"],
    }
    data[missing_column] = [np.nan]
    df = pd.DataFrame(data)
    df.to_csv(uploads_base / "clean.csv", index=False)
    with auth_client.application.app_context():
        from app import Prediction, db
        before = Prediction.query.count()
    response = auth_client.post(f"/upload/{uid}/predict")
    assert response.status_code == 200
    with auth_client.application.app_context():
        from app import Prediction
        after = Prediction.query.count()
        assert after == before + 1
        pred = Prediction.query.order_by(Prediction.id.desc()).first()
        assert getattr(pred, attr) is None
