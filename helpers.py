import pandas as pd
from typing import Sequence, Union, List, Dict, Iterable

NUMERIC_OUTLIER_COLS = [
    "age",
    "resting_blood_pressure",
    "cholesterol",
    "max_heart_rate_achieved",
    "st_depression",
    "num_major_vessels",
]

def detect_outliers(data: Union[pd.DataFrame, Sequence[Dict]], num_cols: Iterable[str] = NUMERIC_OUTLIER_COLS) -> List[Dict]:
    """Detect numeric outliers using the IQR method.

    Parameters
    ----------
    data : DataFrame or sequence of dict
        The data to examine.
    num_cols : iterable of str
        Columns to check for outliers.

    Returns
    -------
    List[Dict]
        List of rows considered outliers with an ``outlier_cols`` key
        describing the offending columns.
    """
    df = data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame(list(data))
    if df.empty:
        return []
    mask = pd.Series(False, index=df.index)
    reasons: Dict[object, List[str]] = {}
    for col in num_cols:
        if col not in df:
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        col_mask = (df[col] < low) | (df[col] > high)
        mask |= col_mask
        for idx in df[col_mask].index:
            reasons.setdefault(idx, []).append(col)
    out_df = df[mask].copy()
    if out_df.empty:
        return []
    out_df["outlier_cols"] = out_df.index.map(lambda i: ", ".join(reasons.get(i, [])))
    return out_df.to_dict(orient="records")
