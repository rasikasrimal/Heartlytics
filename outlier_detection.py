import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Tuple, List


NUMERIC_COLS = [
    "age",
    "resting_blood_pressure",
    "cholesterol",
    "max_heart_rate_achieved",
    "st_depression",
    "num_major_vessels",
]


def detect_iqr_outliers(df: pd.DataFrame) -> Dict:
    """Flag IQR-based column outliers and report counts.

    Also compute a per-row 'score' equal to the maximum distance from the
    nearest quartile in IQR units. Typical outliers have score > 1.5; extreme
    outliers have score >= 3.0.
    """
    counts: Dict[str, int] = {}
    col_masks: Dict[str, pd.Series] = {}
    quartiles: Dict[str, tuple[float, float, float]] = {}
    # Precompute quartiles for numeric cols
    for col in NUMERIC_COLS:
        if col not in df:
            continue
        q1 = float(df[col].quantile(0.25))
        q3 = float(df[col].quantile(0.75))
        iqr = float(q3 - q1) if pd.notna(q3) and pd.notna(q1) else 0.0
        quartiles[col] = (q1, q3, iqr)
        if iqr <= 0:
            # Flat or insufficient spread; skip flagging for this column
            counts[col] = 0
            col_masks[col] = pd.Series(False, index=df.index)
            continue
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        mask = (df[col] < low) | (df[col] > high)
        counts[col] = int(mask.sum())
        col_masks[col] = mask

    # Build reasons and compute IQR-based score per row
    reasons: Dict[int, list[str]] = {}
    scores: Dict[int, float] = {}
    for col, mask in col_masks.items():
        if not mask.any():
            continue
        q1, q3, iqr = quartiles.get(col, (0.0, 0.0, 0.0))
        if iqr <= 0:
            continue
        sub = df.loc[mask, col]
        # Distance from nearest quartile in IQR units
        below = sub[sub < q1]
        above = sub[sub > q3]
        if not below.empty:
            s = (q1 - below) / iqr
            for idx, val in s.items():
                reasons.setdefault(idx, []).append(col)
                scores[idx] = max(scores.get(idx, 0.0), float(val))
        if not above.empty:
            s = (above - q3) / iqr
            for idx, val in s.items():
                reasons.setdefault(idx, []).append(col)
                scores[idx] = max(scores.get(idx, 0.0), float(val))

    if not reasons:
        return {"counts": counts, "rows": pd.DataFrame(columns=df.columns)}
    rows = df.loc[reasons.keys()].copy()
    rows["outlier_cols"] = [", ".join(reasons[idx]) for idx in rows.index]
    rows["score"] = [scores.get(int(idx), float("nan")) for idx in rows.index]
    return {"counts": counts, "rows": rows}


def detect_isolation_forest_outliers(df: pd.DataFrame) -> Dict:
    """Detect dataset-level anomalies using Isolation Forest."""
    feats = df.select_dtypes(include="number").drop(columns=["id"], errors="ignore")
    if feats.empty:
        return {"rows": pd.DataFrame(columns=df.columns)}
    iso = IsolationForest(random_state=42, contamination="auto")
    preds = iso.fit_predict(feats)
    scores = iso.decision_function(feats)
    mask = preds == -1
    rows = df[mask].copy()
    rows["anomaly_score"] = (-scores[mask]).round(3)
    return {"rows": rows}


def _iqr_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows flagged by the IQR detector with a common schema."""
    res = detect_iqr_outliers(df)
    rows = res["rows"].copy()
    if "score" not in rows:
        rows["score"] = pd.NA
    return rows[["id", "outlier_cols", "score"]]


def _iforest_rows(df: pd.DataFrame) -> pd.DataFrame:
    res = detect_isolation_forest_outliers(df)
    rows = res["rows"].copy()
    rows["outlier_cols"] = ""
    rows.rename(columns={"anomaly_score": "score"}, inplace=True)
    return rows[["id", "outlier_cols", "score"]]


def detect_zscore_outliers(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Classical z-score method for column-level outliers."""
    feats = df.select_dtypes(include="number").drop(columns=["id"], errors="ignore")
    if feats.empty:
        return pd.DataFrame(columns=["id", "outlier_cols", "score"])
    z = (feats - feats.mean()) / feats.std(ddof=0)
    mask = (z.abs() > threshold)
    row_mask = mask.any(axis=1)
    rows = df[row_mask].copy()
    rows["outlier_cols"] = mask[row_mask].apply(
        lambda r: ", ".join(feats.columns[r]), axis=1
    )
    rows["score"] = z[row_mask].abs().max(axis=1).round(3)
    return rows[["id", "outlier_cols", "score"]]


OUTLIER_METHODS: Dict[str, Tuple[str, callable]] = {
    "iqr": ("IQR", _iqr_rows),
    "iforest": ("Isolation Forest", _iforest_rows),
    "zscore": ("Z-Score", detect_zscore_outliers),
}


def run_outlier_methods(df: pd.DataFrame, methods: List[str]) -> Dict[str, Dict]:
    """Execute selected outlier detectors and return their rows and thresholds."""
    results: Dict[str, Dict] = {}
    for key in methods:
        entry = OUTLIER_METHODS.get(key)
        if not entry:
            continue
        label, func = entry
        rows = func(df)
        thresh = None
        if not rows.empty and rows["score"].dtype.kind in "fc" and not rows["score"].isna().all():
            if key == "iqr":
                # Extreme outliers for IQR: >= 3.0 IQR units from quartile
                thresh = 3.0
            else:
                # For Isolation Forest / Z-Score, consider the top 5% scores as extreme
                thresh = float(rows["score"].quantile(0.95))
            rows = rows[rows["score"] >= thresh]
        results[key] = {"label": label, "rows": rows, "threshold": thresh}
    return results


def combine_outlier_reports(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Run both detectors, returning cleaned df and combined report."""
    iqr = detect_iqr_outliers(df)
    iforest = detect_isolation_forest_outliers(df)
    out_idx = iqr["rows"].index.union(iforest["rows"].index)
    out_df = df.loc[out_idx].copy()
    out_df["outlier_cols"] = iqr["rows"].reindex(out_idx)["outlier_cols"].fillna("")
    out_df["anomaly_score"] = iforest["rows"].reindex(out_idx)["anomaly_score"]
    clean_df = df.drop(index=out_idx)
    report = {
        "iqr_counts": iqr["counts"],
        "outliers": out_df,
        "iforest_scores": iforest["rows"][["id", "anomaly_score"]].dropna(),
    }
    return clean_df, report
