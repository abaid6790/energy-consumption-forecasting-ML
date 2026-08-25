"""
Time-series feature engineering. All rolling/lag features are computed using
only past observations (shift before rolling) to avoid leakage.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Lag/rolling windows are expressed in *periods*, which adapt to frequency.
LAGS_BY_FREQUENCY = {
    "hourly": [1, 2, 3, 6, 12, 24, 48, 72, 168],
    "daily": [1, 2, 3, 7, 14, 30],
    "weekly": [1, 2, 3, 4],
    "monthly": [1, 2, 3, 6, 12],
}

ROLLING_WINDOWS_BY_FREQUENCY = {
    "hourly": [3, 7, 24, 168],
    "daily": [3, 7, 14, 30],
    "weekly": [3, 4, 8],
    "monthly": [3, 6, 12],
}


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = df["timestamp"]
    df["year"] = ts.dt.year
    df["month"] = ts.dt.month
    df["day"] = ts.dt.day
    df["day_of_week"] = ts.dt.dayofweek
    df["day_of_year"] = ts.dt.dayofyear
    df["week_of_year"] = ts.dt.isocalendar().week.astype(int)
    df["hour"] = ts.dt.hour
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    return df


def add_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["sin_day"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["cos_day"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    df["sin_month"] = np.sin(2 * np.pi * df["month"] / 12)
    df["cos_month"] = np.cos(2 * np.pi * df["month"] / 12)
    return df


def add_lag_features(df: pd.DataFrame, frequency: str = "daily") -> pd.DataFrame:
    df = df.copy()
    for lag in LAGS_BY_FREQUENCY.get(frequency, LAGS_BY_FREQUENCY["daily"]):
        df[f"lag_{lag}"] = df["energy_consumption"].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, frequency: str = "daily") -> pd.DataFrame:
    """
    Rolling stats computed on the SHIFTED series (shift(1) first) so that the
    rolling window for row t only ever sees observations strictly before t.
    """
    df = df.copy()
    shifted = df["energy_consumption"].shift(1)
    for window in ROLLING_WINDOWS_BY_FREQUENCY.get(frequency, ROLLING_WINDOWS_BY_FREQUENCY["daily"]):
        df[f"rolling_mean_{window}"] = shifted.rolling(window, min_periods=1).mean()
        df[f"rolling_std_{window}"] = shifted.rolling(window, min_periods=1).std()
    return df


def build_features(df: pd.DataFrame, frequency: str = "daily") -> tuple[pd.DataFrame, list[str]]:
    """
    Full feature-engineering pass. Returns (dataframe_with_features, feature_columns).
    Rows with NaN in any feature (from the longest lag) are dropped.
    """
    df = add_calendar_features(df)
    df = add_cyclical_features(df)
    df = add_lag_features(df, frequency)
    df = add_rolling_features(df, frequency)

    feature_cols = [
        c
        for c in df.columns
        if c not in ("timestamp", "energy_consumption")
    ]

    df_clean = df.dropna(subset=feature_cols).reset_index(drop=True)
    return df_clean, feature_cols
