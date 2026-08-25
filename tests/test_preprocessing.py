import pandas as pd
import pytest

from ml.preprocessing import (
    sort_and_dedupe,
    handle_missing_values,
    resample,
    detect_gaps,
)


def make_df():
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2024-01-02", "2024-01-01", "2024-01-01", "2024-01-03"]
            ),
            "energy_consumption": [2.0, 1.0, 1.0, None],
        }
    )


def test_sort_and_dedupe_sorts_and_drops_duplicates():
    df, n_dupes = sort_and_dedupe(make_df())
    assert n_dupes == 1
    assert df["timestamp"].is_monotonic_increasing
    assert len(df) == 3


def test_handle_missing_values_fills_nans():
    df, _ = sort_and_dedupe(make_df())
    filled = handle_missing_values(df)
    assert filled["energy_consumption"].isna().sum() == 0


def test_handle_missing_values_removes_negatives():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
            "energy_consumption": [1.0, -5.0, 1.2, 1.1, 1.3],
        }
    )
    filled = handle_missing_values(df)
    assert (filled["energy_consumption"] >= 0).all()


def test_resample_daily():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=48, freq="h"),
            "energy_consumption": [1.0] * 48,
        }
    )
    resampled = resample(df, "daily")
    assert len(resampled) == 2
    assert resampled["energy_consumption"].iloc[0] == 1.0


def test_resample_rejects_unknown_frequency():
    df = make_df().dropna()
    with pytest.raises(ValueError):
        resample(df, "yearly")


def test_detect_gaps_reports_expected_and_actual():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=3, freq="D"),
            "energy_consumption": [1.0, 1.0, 1.0],
        }
    )
    gaps = detect_gaps(df, "daily")
    assert gaps["expected_periods"] == 3
    assert gaps["missing_periods"] == 0
