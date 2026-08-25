"""
Cleans and resamples the canonical (timestamp, energy_consumption) frame.

Pipeline stage: Sorting -> Missing Value Handling -> Resampling -> Gap detection
"""
from __future__ import annotations

import pandas as pd

FREQ_MAP = {
    "hourly": "h",
    "daily": "D",
    "weekly": "W",
    "monthly": "MS",
}


def sort_and_dedupe(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Sorts chronologically and drops duplicate timestamps (keeps first)."""
    df = df.dropna(subset=["timestamp"]).copy()
    df = df.sort_values("timestamp")
    n_before = len(df)
    df = df.drop_duplicates(subset="timestamp", keep="first")
    n_duplicates = n_before - len(df)
    return df.reset_index(drop=True), n_duplicates


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fills missing/invalid readings via time-aware linear interpolation, then
    forward/back-fills any remaining edge gaps. Negative consumption values
    are treated as invalid (energy consumption cannot be negative) and are
    interpolated the same way.
    """
    df = df.copy()
    df.loc[df["energy_consumption"] < 0, "energy_consumption"] = pd.NA
    df = df.set_index("timestamp")
    df["energy_consumption"] = pd.to_numeric(df["energy_consumption"], errors="coerce")
    df["energy_consumption"] = df["energy_consumption"].interpolate(method="time")
    df["energy_consumption"] = df["energy_consumption"].bfill().ffill()
    return df.reset_index()


def resample(df: pd.DataFrame, frequency: str = "daily") -> pd.DataFrame:
    """
    Resamples to the requested frequency using the mean consumption within
    each bucket. `frequency` must be one of hourly/daily/weekly/monthly.
    """
    if frequency not in FREQ_MAP:
        raise ValueError(f"Unsupported frequency '{frequency}'. Use one of {list(FREQ_MAP)}.")

    df = df.set_index("timestamp")
    resampled = df["energy_consumption"].resample(FREQ_MAP[frequency]).mean()
    resampled = resampled.interpolate(method="linear").bfill().ffill()
    return resampled.reset_index().rename(columns={"index": "timestamp"})


def detect_gaps(df: pd.DataFrame, frequency: str = "daily") -> dict:
    """Reports on gaps in the raw (pre-resample) timestamp series."""
    if len(df) < 2:
        return {"expected_periods": 0, "actual_periods": len(df), "missing_periods": 0}

    freq = FREQ_MAP[frequency]
    full_range = pd.date_range(df["timestamp"].min(), df["timestamp"].max(), freq=freq)
    expected = len(full_range)
    actual = df["timestamp"].nunique()
    return {
        "expected_periods": expected,
        "actual_periods": actual,
        "missing_periods": max(expected - actual, 0),
    }


def run_preprocessing_pipeline(df: pd.DataFrame, frequency: str = "daily") -> dict:
    """Runs sort -> dedupe -> missing-value handling -> gap detection -> resample."""
    df, n_dupes = sort_and_dedupe(df)
    gaps = detect_gaps(df, frequency)
    df = handle_missing_values(df)
    resampled = resample(df, frequency)

    return {
        "data": resampled,
        "duplicates_removed": n_dupes,
        "gap_report": gaps,
        "date_range": (resampled["timestamp"].min(), resampled["timestamp"].max()),
        "n_observations": len(resampled),
    }
