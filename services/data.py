from __future__ import annotations

import re
from typing import Dict, List, Tuple, Set, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ---------------------------
# Column definitions and mappings
# ---------------------------

INPUT_COLUMNS = [
    "age", "sex", "chest_pain_type",
    "resting_blood_pressure", "cholesterol",
    "fasting_blood_sugar", "Restecg",
    "max_heart_rate_achieved", "exercise_induced_angina",
    "st_depression", "st_slope_type",
    "num_major_vessels", "thalassemia_type",
]

NUMERIC_COLS = {
    "age": int,
    "sex": int,
    "resting_blood_pressure": float,
    "cholesterol": float,
    "fasting_blood_sugar": int,
    "max_heart_rate_achieved": float,
    "exercise_induced_angina": int,
    "st_depression": float,
    "num_major_vessels": int,
}

CATEGORICAL_COLS = {
    "chest_pain_type": {"typical_angina", "atypical_angina", "non-anginal", "asymptomatic"},
    "Restecg": {"normal", "left_ventricular_hypertrophy", "st_t_wave_abnormality"},
    "st_slope_type": {"upsloping", "flat", "downsloping"},
    "thalassemia_type": {"normal", "fixed_defect", "reversible_defect"},
}

CATEGORICAL_ALLOWED = {
    "chest_pain_type": CATEGORICAL_COLS["chest_pain_type"],
    "Restecg": CATEGORICAL_COLS["Restecg"],
    "st_slope_type": CATEGORICAL_COLS["st_slope_type"],
    "thalassemia_type": CATEGORICAL_COLS["thalassemia_type"],
}

CATEGORICAL_FEATURES = {
    "sex", "fasting_blood_sugar", "exercise_induced_angina",
    "chest_pain_type", "Restecg", "st_slope_type", "thalassemia_type"
}

REQUIRED_INTERNAL_COLUMNS = set(INPUT_COLUMNS)
OPTIONAL_KEEP = set()
NUMERIC_FEATURES_INT = {"age", "resting_blood_pressure", "cholesterol", "max_heart_rate_achieved", "num_major_vessels"}
NUMERIC_FEATURES_FLOAT = {"st_depression"}
BINARY_FEATURES = {"sex", "fasting_blood_sugar", "exercise_induced_angina"}

# Category mappers robust to numeric/string inputs
CP_MAP_NUM = {
    0: "typical_angina", 1: "atypical_angina", 2: "non-anginal", 3: "asymptomatic",
    1.0: "typical_angina", 2.0: "atypical_angina", 3.0: "non-anginal", 4.0: "asymptomatic",
}
RESTECG_MAP_NUM = {
    0: "normal",
    1: "st_t_wave_abnormality",
    2: "left_ventricular_hypertrophy",
    "lv_hypertrophy": "left_ventricular_hypertrophy",
    "left_ventricular_hypertrophy": "left_ventricular_hypertrophy",
    "lvhypertrophy": "left_ventricular_hypertrophy",
    "st_t_wave_abnormality": "st_t_wave_abnormality",
    "normal": "normal",
}
SLOPE_MAP_NUM = {
    0: "upsloping", 1: "flat", 2: "downsloping",
    1.0: "upsloping", 2.0: "flat", 3.0: "downsloping",
}
THAL_MAP_NUM = {
    1: "normal", 2: "fixed_defect", 3: "reversible_defect",
    3.0: "normal", 6.0: "fixed_defect", 7.0: "reversible_defect",
    "fixed_defect": "fixed_defect",
    "fixeddefect": "fixed_defect",
    "reversible_defect": "reversible_defect",
    "reversable_defect": "reversible_defect",
    "normal": "normal",
}

COLUMN_ALIASES = {
    # core
    "age": "age",
    "sex": "sex",



    # chest pain
    "cp": "chest_pain_type",
    "chest_pain_type": "chest_pain_type",

    # resting bp
    "trestbps": "resting_blood_pressure",
    "resting_blood_bressure": "resting_blood_pressure",
    "resting_blood_pressure": "resting_blood_pressure",

    # cholesterol
    "chol": "cholesterol",

    # other common UCI aliases
    "thalach": "max_heart_rate_achieved",
    "thalch": "max_heart_rate_achieved",
    "fbs": "fasting_blood_sugar",
    "restecg": "Restecg",
    "exang": "exercise_induced_angina",
    "oldpeak": "st_depression",
    "slope": "st_slope_type",
    "ca": "num_major_vessels",
    "thal": "thalassemia_type",
}

# ---------------------------
# Helper functions
# ---------------------------

def _yes_no_to_binary(x):
    """Convert yes/no style values to binary."""
    if pd.isna(x):
        return None
    s = str(x).strip().lower()
    if s in {"1", "true", "t", "yes", "y"}:
        return 1
    if s in {"0", "false", "f", "no", "n"}:
        return 0
    try:
        v = float(s)
        return 1 if v >= 1 else 0
    except Exception:
        return None


def _sex_to_binary(x):
    """Convert gender strings/numbers to 0/1."""
    if pd.isna(x):
        return None
    s = str(x).strip().lower()
    if s in {"male", "m", "1"}:
        return 1
    if s in {"female", "f", "0"}:
        return 0
    try:
        v = float(s)
        return 1 if int(round(v)) == 1 else 0
    except Exception:
        return None


def _normalize_key(val: object) -> str:
    return re.sub(r"[_\s-]", "", str(val).strip().lower())


def _map_with_dict(x, mapping, fallback_allowed=None):
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)) and x in mapping:
        return mapping[x]
    s = _normalize_key(x).replace("reversabledefect", "reversibledefect")
    norm_map = {(_normalize_key(k), v) for k, v in mapping.items()}
    norm_lookup = dict(norm_map)
    if s in norm_lookup:
        return norm_lookup[s]
    if fallback_allowed and s in {_normalize_key(v) for v in fallback_allowed}:
        return s
    return None


def normalize_log(log: List[Union[dict, str]]) -> List[dict]:
    """Normalize cleaning log entries.

    Collapses different line endings, trims whitespace, and removes blank
    lines so the log renders compactly in templates.
    """

    normalized: List[dict] = []
    for item in log:
        entry = item.copy() if isinstance(item, dict) else {"text": str(item)}
        text = entry.get("text", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [ln.strip() for ln in text.split("\n")]
        lines = [ln for ln in lines if ln]
        if not lines:
            continue
        entry["text"] = "\n".join(lines)
        normalized.append(entry)
    return normalized


def group_cleaning_log(log: List[dict]) -> Dict[str, List[dict]]:
    """Group cleaning log entries by step."""
    groups = {"dup": [], "invalid": [], "impute": [], "outliers": [], "other": []}
    for idx, item in enumerate(log):
        item["idx"] = idx
        step = item.get("step", "other")
        (groups[step] if step in groups else groups["other"]).append(item)
    return groups


def normalize_columns(df: pd.DataFrame, log: List[str]) -> pd.DataFrame:
    """Rename columns based on COLUMN_ALIASES."""
    colmap = {}
    for c in df.columns:
        key = str(c).strip()
        key_norm = key.lower().strip().replace(" ", "_")
        colmap[key] = COLUMN_ALIASES.get(key_norm, key)
    df = df.rename(columns=colmap)
    log.append(f"Renamed columns using aliases: {sum(k != v for k, v in colmap.items())} renamed.")
    return df


def validate_structure(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate presence of required columns."""
    errs: List[str] = []
    cols = set(df.columns)
    missing = sorted(list(REQUIRED_INTERNAL_COLUMNS - cols))
    if missing:
        errs.append(f"Missing required columns: {', '.join(missing)}")
    return (len(errs) == 0), errs


def _encode_frame_for_ml(X: pd.DataFrame):
    """Label-encode object/category columns for ML."""
    X_enc = X.copy()
    encoders = {}
    for col in X_enc.columns:
        if X_enc[col].dtype == "object" or str(X_enc[col].dtype).startswith("category"):
            le = LabelEncoder()
            vals = X_enc[col].astype(str).fillna("_nan_")
            le.fit(vals)
            X_enc[col] = le.transform(vals)
            encoders[col] = le
    return X_enc, encoders


def find_optional_in_raw(df: pd.DataFrame, internal_name: str) -> str | None:
    """Locate an optional column in the uploaded CSV using COLUMN_ALIASES."""
    for col in df.columns:
        key_norm = str(col).lower().strip().replace(" ", "_")
        if COLUMN_ALIASES.get(key_norm) == internal_name:
            return col
    return None


def impute_categorical_missing(
    df: pd.DataFrame,
    target_col: str,
    bool_cols: Set[str] | None = None,
    log: List[str] | None = None,
) -> pd.Series:
    """Impute a categorical/binary column using RandomForest + IterativeImputer."""
    if bool_cols is None:
        bool_cols = set()
    df_null = df[df[target_col].isna()]
    df_not_null = df[df[target_col].notna()]
    if df_null.empty:
        return df[target_col]

    drop_cols = {target_col}
    for lab_col in ("target", "prediction"):
        if lab_col in df.columns:
            drop_cols.add(lab_col)

    if len(df_not_null) == 0:
        fillv = 0 if target_col in bool_cols else "_missing_"
        if log is not None:
            log.append(f"{target_col}: all values missing; filled {len(df_null)} NaNs with '{fillv}'.")
        return pd.Series([fillv] * len(df), index=df.index)

    y = df_not_null[target_col].copy()
    if len(df_not_null) < 2 or y.nunique(dropna=True) < 2:
        mode_val = y.mode(dropna=True)
        fillv = mode_val.iloc[0] if len(mode_val) else y.dropna().iloc[0]
        if log is not None:
            log.append(f"{target_col}: insufficient data; filled {len(df_null)} NaNs with mode '{fillv}'.")
        return df[target_col].fillna(fillv)

    X = df_not_null.drop(columns=list(drop_cols))
    X_enc, _ = _encode_frame_for_ml(X)

    y_enc = y.copy()
    y_was_encoded = False
    if (y.dtype == "object") or str(y.dtype).startswith("category") or (target_col in bool_cols):
        y_le = LabelEncoder()
        y_le.fit(y_enc.astype(str).fillna("_nan_"))
        y_enc = pd.Series(y_le.transform(y_enc.astype(str).fillna("_nan_")), index=y.index)
        y_was_encoded = True

    iter_imp = IterativeImputer(estimator=RandomForestRegressor(random_state=42), add_indicator=True, random_state=42)
    try:
        X_imp = pd.DataFrame(iter_imp.fit_transform(X_enc), index=X_enc.index, columns=X_enc.columns)
    except Exception:
        X_imp = X_enc.fillna(X_enc.median(numeric_only=True))

    X_train, X_test, y_train, y_test = train_test_split(X_imp, y_enc, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(random_state=42, n_jobs=-1)
    try:
        clf.fit(X_train, y_train)
        try:
            acc = accuracy_score(y_test, clf.predict(X_test))
            if log is not None:
                log.append(f"{target_col}: categorical imputed with RF (acc≈{acc:.3f}, n_missing={len(df_null)}).")
        except Exception:
            if log is not None:
                log.append(f"{target_col}: categorical imputed with RF (n_missing={len(df_null)}).")
    except Exception:
        mode_val = y.mode(dropna=True)
        fillv = mode_val.iloc[0] if len(mode_val) else y.dropna().iloc[0]
        if log is not None:
            log.append(f"{target_col}: RF failed; filled {len(df_null)} NaNs with mode '{fillv}'.")
        return df[target_col].fillna(fillv)

    Xn = df_null.drop(columns=list(drop_cols))
    Xn_enc, _ = _encode_frame_for_ml(Xn)
    try:
        Xn_imp = pd.DataFrame(iter_imp.transform(Xn_enc), index=Xn_enc.index, columns=Xn_enc.columns)
    except Exception:
        Xn_imp = Xn_enc.fillna(Xn_enc.median(numeric_only=True))

    pred_enc = pd.Series(clf.predict(Xn_imp), index=Xn_imp.index)
    if y_was_encoded:
        pred = pd.Series(y_le.inverse_transform(pred_enc.astype(int)), index=pred_enc.index).replace({"_nan_": np.nan})
    else:
        pred = pred_enc
    out = df[target_col].copy()
    out.loc[df_null.index] = pred
    return out


def impute_continuous_missing(
    df: pd.DataFrame,
    target_col: str,
    log: List[str] | None = None,
) -> pd.Series:
    """Impute a continuous column using RandomForest + IterativeImputer."""
    df_null = df[df[target_col].isna()]
    df_not_null = df[df[target_col].notna()]
    if df_null.empty:
        return df[target_col]

    drop_cols = {target_col}
    for lab_col in ("target", "prediction"):
        if lab_col in df.columns:
            drop_cols.add(lab_col)

    X = df_not_null.drop(columns=list(drop_cols))
    y = df_not_null[target_col].astype(float)
    X_enc, _ = _encode_frame_for_ml(X)

    iter_imp = IterativeImputer(estimator=RandomForestRegressor(random_state=42), add_indicator=True, random_state=42)
    try:
        X_imp = pd.DataFrame(iter_imp.fit_transform(X_enc), index=X_enc.index, columns=X_enc.columns)
    except Exception:
        X_imp = X_enc.fillna(X_enc.median(numeric_only=True))

    X_train, X_test, y_train, y_test = train_test_split(X_imp, y, test_size=0.2, random_state=42)
    reg = RandomForestRegressor(random_state=42, n_jobs=-1)
    try:
        reg.fit(X_train, y_train)
        try:
            r2 = reg.score(X_test, y_test)
            if log is not None:
                log.append(f"{target_col}: continuous imputed with RF (r2≈{r2:.3f}, n_missing={len(df_null)}).")
        except Exception:
            if log is not None:
                log.append(f"{target_col}: continuous imputed with RF (n_missing={len(df_null)}).")
    except Exception:
        median = y.median()
        if log is not None:
            log.append(f"{target_col}: RF failed; filled {len(df_null)} NaNs with median {median}.")
        return df[target_col].fillna(median)

    Xn = df_null.drop(columns=list(drop_cols))
    Xn_enc, _ = _encode_frame_for_ml(Xn)
    try:
        Xn_imp = pd.DataFrame(iter_imp.transform(Xn_enc), index=Xn_enc.index, columns=Xn_enc.columns)
    except Exception:
        Xn_imp = Xn_enc.fillna(Xn_enc.median(numeric_only=True))

    pred = pd.Series(reg.predict(Xn_imp), index=Xn_imp.index)
    out = df[target_col].copy()
    out.loc[df_null.index] = pred
    return out


def clean_dataframe(
    df: pd.DataFrame,
    *,
    handle_duplicates: bool = True,
    invalid_to_nan: bool = True,
    impute_missing: bool = True,
    soften_outliers: bool = True,
) -> Tuple[pd.DataFrame, List[str]]:
    """Clean a dataframe according to selectable steps."""
    log: List[str] = []
    df = normalize_columns(df, log)

    ok, errs = validate_structure(df)
    if not ok:
        raise ValueError("; ".join(errs))

    keep_cols = list(REQUIRED_INTERNAL_COLUMNS | OPTIONAL_KEEP | ({"target"} if "target" in df.columns else set()))
    existing_keep = [c for c in keep_cols if c in df.columns]
    df = df[existing_keep]

    if handle_duplicates:
        before = len(df)
        df = df.drop_duplicates()
        log.append(f"Duplicates removed: {before - len(df)}")
    else:
        log.append("Duplicate handling skipped.")

    if "sex" in df.columns:
        df["sex"] = df["sex"].apply(_sex_to_binary)

    for b in ["fasting_blood_sugar", "exercise_induced_angina"]:
        if b in df.columns:
            df[b] = df[b].apply(_yes_no_to_binary)

    if "chest_pain_type" in df.columns:
        df["chest_pain_type"] = df["chest_pain_type"].apply(
            lambda x: _map_with_dict(x, CP_MAP_NUM, CATEGORICAL_ALLOWED["chest_pain_type"])
        )
    if "Restecg" in df.columns:
        df["Restecg"] = df["Restecg"].apply(
            lambda x: _map_with_dict(x, RESTECG_MAP_NUM, CATEGORICAL_ALLOWED["Restecg"])
        )
    if "st_slope_type" in df.columns:
        df["st_slope_type"] = df["st_slope_type"].apply(
            lambda x: _map_with_dict(x, SLOPE_MAP_NUM, CATEGORICAL_ALLOWED["st_slope_type"])
        )
    if "thalassemia_type" in df.columns:
        df["thalassemia_type"] = df["thalassemia_type"].apply(
            lambda x: _map_with_dict(x, THAL_MAP_NUM, CATEGORICAL_ALLOWED["thalassemia_type"])
        )

    def _coerce_int_series(s, name):
        return s.apply(lambda v: None if pd.isna(v) or str(v).strip() == "" else int(round(float(v))))

    def _coerce_float_series(s, name):
        return s.apply(lambda v: None if pd.isna(v) or str(v).strip() == "" else float(v))

    for n in NUMERIC_FEATURES_INT:
        if n in df.columns:
            df[n] = _coerce_int_series(df[n], n)
    for n in NUMERIC_FEATURES_FLOAT:
        if n in df.columns:
            df[n] = _coerce_float_series(df[n], n)

    fixes: List[str] = []
    if invalid_to_nan:
        def _mark_nan(mask, col, note):
            n = int(mask.sum())
            if n:
                df.loc[mask, col] = np.nan
                fixes.append(f"{col}: set {n} implausible values -> NaN ({note})")

        if "cholesterol" in df.columns:
            _mark_nan(df["cholesterol"] <= 0, "cholesterol", "<= 0 not allowed")

        if "fasting_blood_sugar" in df.columns:
            mask = ~df["fasting_blood_sugar"].isin([0, 1])
            _mark_nan(mask, "fasting_blood_sugar", "not 0 or 1")

        if "exercise_induced_angina" in df.columns:
            mask = ~df["exercise_induced_angina"].isin([0, 1])
            _mark_nan(mask, "exercise_induced_angina", "not 0 or 1")

        if "st_depression" in df.columns:
            neg = df["st_depression"] < 0
            n_neg = int(neg.sum())
            if n_neg:
                df.loc[neg, "st_depression"] = 0.0
                fixes.append(f"st_depression: clamped {n_neg} negatives to 0")
            high = df["st_depression"] > 7
            n_high = int(high.sum())
            if n_high:
                df.loc[high, "st_depression"] = 7.0
                fixes.append(f"st_depression: capped {n_high} values at 7.0")

        if "max_heart_rate_achieved" in df.columns:
            mask = ~df["max_heart_rate_achieved"].between(60, 250)
            _mark_nan(mask, "max_heart_rate_achieved", "outside [60, 250]")

        if "resting_blood_pressure" in df.columns:
            mask = ~df["resting_blood_pressure"].between(80, 260)
            _mark_nan(mask, "resting_blood_pressure", "outside [80, 260]")

        if "num_major_vessels" in df.columns:
            mask = ~df["num_major_vessels"].between(0, 4)
            _mark_nan(mask, "num_major_vessels", "outside [0, 4]")

        if fixes:
            log.extend(fixes)

        for col, allowed in CATEGORICAL_ALLOWED.items():
            if col in df.columns:
                bad_mask = ~df[col].isin(allowed)
                n_bad = int(bad_mask.sum())
                if n_bad:
                    df.loc[bad_mask, col] = np.nan
                    log.append(f"{col}: set {n_bad} unknown categories -> NaN (will impute).")
    else:
        log.append("Invalid/implausible value handling skipped.")

    if impute_missing:
        bool_cols = {"sex", "fasting_blood_sugar", "exercise_induced_angina"}
        for col in sorted((NUMERIC_FEATURES_INT | NUMERIC_FEATURES_FLOAT)):
            if col in df.columns and df[col].isna().any():
                df[col] = impute_continuous_missing(df, col, log=log)
        for col in ["sex", "fasting_blood_sugar", "exercise_induced_angina",
                    "chest_pain_type", "Restecg", "st_slope_type", "thalassemia_type"]:
            if (col in df.columns) and df[col].isna().any():
                df[col] = impute_categorical_missing(df, col, bool_cols=bool_cols, log=log)
    else:
        log.append("Missing value imputation skipped.")

    if soften_outliers:
        for col in (NUMERIC_FEATURES_INT | NUMERIC_FEATURES_FLOAT):
            if col in df.columns:
                s = pd.to_numeric(df[col], errors="coerce").astype(float)
                q1, q3 = s.quantile([0.25, 0.75])
                iqr = q3 - q1
                if np.isfinite(iqr) and iqr > 0:
                    low = q1 - 1.5 * iqr
                    high = q3 + 1.5 * iqr
                    n_clip = int((s < low).sum() + (s > high).sum())
                    if n_clip:
                        df[col] = s.clip(lower=low, upper=high)
                        log.append(f"{col}: softened {n_clip} outliers using IQR bounds [{low:.2f}, {high:.2f}].")
    else:
        log.append("Outlier handling skipped.")

    if "num_major_vessels" in df.columns:
        df["num_major_vessels"] = (
            pd.to_numeric(df["num_major_vessels"], errors="coerce")
            .round()
            .clip(0, 4)
            .astype("Int64")
        )

    if "sex" in df.columns:
        df["sex"] = (
            pd.to_numeric(df["sex"], errors="coerce")
            .round()
            .clip(0, 1)
            .astype("Int64")
        )

    return df, log
