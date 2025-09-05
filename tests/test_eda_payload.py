import pandas as pd
from app import build_eda_payload


def test_build_eda_payload_with_predictions():
    df = pd.DataFrame({
        "resting_blood_pressure": [120, 130, 140],
        "cholesterol": [200, 210, 220],
        "prediction": [0, 1, 0],
    })
    payload = build_eda_payload(df)
    viz = payload["viz"]
    assert viz["bp_box_by_status"]
    assert len(viz["bp_box_by_status"]) >= 3
    assert viz["chol_violin_by_stage"]
    assert len(viz["chol_violin_by_stage"]) >= 3


def test_build_eda_payload_with_string_target():
    df = pd.DataFrame({
        "resting_blood_pressure": [120, 130, 140],
        "cholesterol": [200, 210, 220],
        "target": ["No Disease", "Heart Disease", "No Disease"],
    })
    payload = build_eda_payload(df)
    viz = payload["viz"]
    names_bp = {s["name"] for s in viz["bp_box_by_status"]}
    names_chol = {s["name"] for s in viz["chol_violin_by_stage"]}
    expected = {"All Patients", "No Disease", "Heart Disease"}
    assert names_bp == expected
    assert names_chol == expected


def test_build_eda_payload_without_target():
    df = pd.DataFrame({
        "resting_blood_pressure": [120, 130, 140],
        "cholesterol": [200, 210, 220],
    })
    payload = build_eda_payload(df)
    viz = payload["viz"]
    assert viz["bp_box_by_status"]
    assert len(viz["bp_box_by_status"]) == 1
    assert viz["bp_box_by_status"][0]["name"] == "All Patients"
    assert viz["chol_violin_by_stage"]
    assert len(viz["chol_violin_by_stage"]) == 1
    assert viz["chol_violin_by_stage"][0]["name"] == "All Patients"
