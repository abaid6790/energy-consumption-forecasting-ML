import numpy as np
import pandas as pd

from ml.anomaly_detection import (
    rolling_zscore_anomalies,
    iqr_anomalies,
    detect_anomalies,
    summarize_anomalies,
)


def make_df_with_spike():
    values = [1.0] * 30
    values[15] = 20.0  # obvious spike
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=30, freq="D"),
            "energy_consumption": values,
        }
    )


def test_rolling_zscore_flags_spike():
    df = rolling_zscore_anomalies(make_df_with_spike())
    assert df.loc[15, "is_anomaly_zscore"] == True  # noqa: E712


def test_iqr_flags_spike():
    df = iqr_anomalies(make_df_with_spike())
    assert df.loc[15, "is_anomaly_iqr"] == True  # noqa: E712


def test_detect_anomalies_all_methods_combine():
    result = detect_anomalies(make_df_with_spike(), method="all")
    assert "is_anomaly" in result.columns
    assert result["is_anomaly"].sum() >= 1


def test_summarize_anomalies_returns_dates():
    flagged = detect_anomalies(make_df_with_spike(), method="all")
    summary = summarize_anomalies(flagged)
    assert isinstance(summary, list)
    if summary:
        assert "date" in summary[0]
        assert "consumption" in summary[0]


def test_no_anomalies_in_flat_series():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=20, freq="D"),
            "energy_consumption": [1.0] * 20,
        }
    )
    result = detect_anomalies(df, method="iqr")
    assert result["is_anomaly"].sum() == 0
