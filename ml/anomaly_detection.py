"""Rule-based and model-based anomaly detection for energy consumption series."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def rolling_zscore_anomalies(df: pd.DataFrame, window: int = 14, threshold: float = 3.0) -> pd.DataFrame:
    df = df.copy()
    roll_mean = df["energy_consumption"].rolling(window, min_periods=3).mean()
    roll_std = df["energy_consumption"].rolling(window, min_periods=3).std()
    z = (df["energy_consumption"] - roll_mean) / roll_std.replace(0, np.nan)
    df["zscore"] = z
    df["is_anomaly_zscore"] = (z.abs() > threshold).fillna(False)
    df["expected_low"] = roll_mean - threshold * roll_std
    df["expected_high"] = roll_mean + threshold * roll_std
    return df


def iqr_anomalies(df: pd.DataFrame, multiplier: float = 1.5) -> pd.DataFrame:
    df = df.copy()
    q1 = df["energy_consumption"].quantile(0.25)
    q3 = df["energy_consumption"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    df["is_anomaly_iqr"] = (df["energy_consumption"] < lower) | (df["energy_consumption"] > upper)
    df["iqr_lower"] = lower
    df["iqr_upper"] = upper
    return df


def isolation_forest_anomalies(df: pd.DataFrame, contamination: float = 0.02) -> pd.DataFrame:
    df = df.copy()
    if len(df) < 20:
        df["is_anomaly_iforest"] = False
        return df
    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)
    X = df[["energy_consumption"]].values
    preds = model.fit_predict(X)
    df["is_anomaly_iforest"] = preds == -1
    return df


def detect_anomalies(df: pd.DataFrame, method: str = "zscore") -> pd.DataFrame:
    """
    df must contain columns: timestamp, energy_consumption.
    Returns df with anomaly flag columns added. `method` in {zscore, iqr, isolation_forest, all}.
    """
    result = df.copy()
    if method in ("zscore", "all"):
        result = rolling_zscore_anomalies(result)
    if method in ("iqr", "all"):
        result = iqr_anomalies(result)
    if method in ("isolation_forest", "all"):
        result = isolation_forest_anomalies(result)

    anomaly_cols = [c for c in result.columns if c.startswith("is_anomaly")]
    if anomaly_cols:
        result["is_anomaly"] = result[anomaly_cols].any(axis=1)
    else:
        result["is_anomaly"] = False
    return result


def summarize_anomalies(df: pd.DataFrame) -> list[dict]:
    anomalies = df[df["is_anomaly"]]
    summary = []
    for _, row in anomalies.iterrows():
        entry = {
            "date": row["timestamp"].strftime("%Y-%m-%d"),
            "consumption": round(float(row["energy_consumption"]), 3),
        }
        if "expected_low" in row and "expected_high" in row and pd.notna(row.get("expected_low")):
            entry["expected_range"] = [
                round(float(row["expected_low"]), 2),
                round(float(row["expected_high"]), 2),
            ]
        summary.append(entry)
    return summary
