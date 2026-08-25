"""
Loads raw energy datasets and converts them into the internal canonical
representation used everywhere else in the pipeline:

    timestamp             datetime64
    energy_consumption    float  (kW, for the default UCI-style dataset)

Two entry points:
  - load_uci_household_power(path): the semicolon-delimited UCI-format file
  - load_generic_csv(path, timestamp_col, value_col): any user-provided CSV
"""
from __future__ import annotations

import pandas as pd

CANONICAL_COLUMNS = ["timestamp", "energy_consumption"]


class DatasetValidationError(Exception):
    """Raised when an uploaded/loaded dataset fails validation."""


def load_uci_household_power(path: str) -> pd.DataFrame:
    """
    Loads the UCI 'Individual Household Electric Power Consumption' file
    (or our synthetic stand-in, which uses the identical schema).

    Target metric: Global_active_power, in kilowatts (kW) — the household's
    global minute-averaged active power. This is documented explicitly so
    units are never silently mixed with anything else downstream.
    """
    df = pd.read_csv(
        path,
        sep=";",
        na_values=["?"],
        low_memory=False,
    )

    required = {"Date", "Time", "Global_active_power"}
    missing = required - set(df.columns)
    if missing:
        raise DatasetValidationError(f"Missing required columns: {sorted(missing)}")

    df["timestamp"] = pd.to_datetime(
        df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    )
    df["energy_consumption"] = pd.to_numeric(df["Global_active_power"], errors="coerce")

    out = df[CANONICAL_COLUMNS].copy()
    return out


def load_generic_csv(
    path: str, timestamp_col: str = "timestamp", value_col: str = "energy_consumption"
) -> pd.DataFrame:
    """
    Loads a user-provided CSV. Expects (at minimum) a timestamp column and
    an energy-consumption column. Extra columns are ignored for forecasting
    but are not an error.
    """
    df = pd.read_csv(path)

    if timestamp_col not in df.columns:
        raise DatasetValidationError(f"Required column '{timestamp_col}' is missing.")
    if value_col not in df.columns:
        raise DatasetValidationError(f"Required column '{value_col}' is missing.")

    df["timestamp"] = pd.to_datetime(df[timestamp_col], errors="coerce")
    df["energy_consumption"] = pd.to_numeric(df[value_col], errors="coerce")

    out = df[CANONICAL_COLUMNS].copy()
    return out


def validate_canonical(df: pd.DataFrame, min_observations: int = 30) -> None:
    """Shared validation applied after any loader produces the canonical frame."""
    if df is None or len(df) == 0:
        raise DatasetValidationError("The dataset contains no rows.")

    if df["timestamp"].isna().all():
        raise DatasetValidationError("No valid timestamps could be parsed.")

    valid = df.dropna(subset=["timestamp", "energy_consumption"])
    if len(valid) < min_observations:
        raise DatasetValidationError(
            "The uploaded dataset does not contain enough historical observations "
            f"(found {len(valid)}, need at least {min_observations})."
        )
