import pandas as pd

from app import build_eda_payload


def test_build_eda_payload_excludes_removed_visuals_with_predictions():
    df = pd.DataFrame(
        {
            "resting_blood_pressure": [120, 130, 140],
            "cholesterol": [200, 210, 220],
            "prediction": [0, 1, 0],
        }
    )
    payload = build_eda_payload(df)
    assert payload["viz"] == {}


def test_build_eda_payload_excludes_removed_visuals_without_target():
    df = pd.DataFrame(
        {
            "resting_blood_pressure": [120, 130, 140],
            "cholesterol": [200, 210, 220],
        }
    )
    payload = build_eda_payload(df)
    assert payload["viz"] == {}

