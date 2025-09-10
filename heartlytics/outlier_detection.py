import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
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
    """Flag IQR-based column outliers and report counts."""
    counts: Dict[str, int] = {}
    col_masks: Dict[str, pd.Series] = {}
    for col in NUMERIC_COLS:
        if col not in df:
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        mask = (df[col] < low) | (df[col] > high)
        counts[col] = int(mask.sum())
        col_masks[col] = mask
    reasons: Dict[int, list[str]] = {}
    for col, mask in col_masks.items():
        for idx in df[mask].index:
            reasons.setdefault(idx, []).append(col)
    rows = df.loc[reasons.keys()].copy()
    rows["outlier_cols"] = [", ".join(reasons[idx]) for idx in rows.index]
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


def detect_lof_outliers(df: pd.DataFrame, n_neighbors: int = 20) -> pd.DataFrame:
    """Detect outliers using Local Outlier Factor."""
    feats = df.select_dtypes(include="number").drop(columns=["id"], errors="ignore")
    if feats.shape[0] <= 1:
        return pd.DataFrame(columns=["id", "outlier_cols", "score"])
    n_neighbors = min(n_neighbors, max(2, feats.shape[0] - 1))
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination="auto")
    preds = lof.fit_predict(feats)
    scores = -lof.negative_outlier_factor_
    mask = preds == -1
    rows = df[mask].copy()
    rows["outlier_cols"] = ""
    rows["score"] = scores[mask].round(3)
    return rows[["id", "outlier_cols", "score"]]


def detect_dbscan_outliers(df: pd.DataFrame, eps: float = 0.5, min_samples: int = 5) -> pd.DataFrame:
    """Flag points labeled as noise by DBSCAN."""
    feats = df.select_dtypes(include="number").drop(columns=["id"], errors="ignore")
    if feats.empty:
        return pd.DataFrame(columns=["id", "outlier_cols", "score"])
    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(feats)
    mask = labels == -1
    rows = df[mask].copy()
    rows["outlier_cols"] = ""
    rows["score"] = 1.0
    return rows[["id", "outlier_cols", "score"]]


OUTLIER_METHODS: Dict[str, Tuple[str, callable]] = {
    "iqr": ("IQR", _iqr_rows),
    "iforest": ("Isolation Forest", _iforest_rows),
    "zscore": ("Z-Score", detect_zscore_outliers),
    "lof": ("LOF", detect_lof_outliers),
    "dbscan": ("DBSCAN", detect_dbscan_outliers),
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
            thresh = rows["score"].quantile(0.95)
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
