import numpy as np
import pandas as pd

from ml.feature_engineering import (
    add_calendar_features,
    add_cyclical_features,
    add_lag_features,
    add_rolling_features,
    build_features,
)
from ml.baselines import NaiveForecaster, MovingAverageForecaster
from ml.evaluate import compute_metrics, mape


def make_daily_df(n=60):
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="D"),
            "energy_consumption": np.linspace(1.0, 2.0, n),
        }
    )


def test_calendar_features_present():
    df = add_calendar_features(make_daily_df())
    for col in ["year", "month", "day", "day_of_week", "is_weekend"]:
        assert col in df.columns


def test_cyclical_features_bounded():
    df = add_calendar_features(make_daily_df())
    df = add_cyclical_features(df)
    for col in ["sin_hour", "cos_hour", "sin_day", "cos_day"]:
        assert df[col].between(-1.0001, 1.0001).all()


def test_lag_features_no_future_leakage():
    df = add_lag_features(make_daily_df(), "daily")
    # lag_1 at row i must equal energy_consumption at row i-1
    assert df["lag_1"].iloc[5] == df["energy_consumption"].iloc[4]
    assert pd.isna(df["lag_1"].iloc[0])


def test_rolling_features_use_only_past_values():
    df = add_rolling_features(make_daily_df(), "daily")
    # rolling_mean_3 at row i should not use energy_consumption[i] itself
    manual_mean = make_daily_df()["energy_consumption"].iloc[2:5].mean()
    assert abs(df["rolling_mean_3"].iloc[5] - manual_mean) < 1e-9


def test_build_features_drops_incomplete_rows():
    featured, feature_cols = build_features(make_daily_df(60), "daily")
    assert featured[feature_cols].isna().sum().sum() == 0
    assert len(featured) < 60


def test_naive_forecaster_predicts_previous_value():
    y = pd.Series([1.0, 2.0, 3.0, 4.0])
    model = NaiveForecaster().fit(y)
    preds = model.predict(y)
    assert list(preds) == [1.0, 1.0, 2.0, 3.0]


def test_moving_average_forecaster():
    y = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    model = MovingAverageForecaster(window=2).fit(y)
    preds = model.predict(y)
    assert preds[2] == 1.5  # mean of [1.0, 2.0]


def test_compute_metrics_perfect_prediction():
    y_true = [1.0, 2.0, 3.0]
    metrics = compute_metrics(y_true, y_true)
    assert metrics["MAE"] == 0.0
    assert metrics["RMSE"] == 0.0
    assert metrics["R2"] == 1.0


def test_mape_handles_zero_true_values():
    result = mape([0.0, 2.0], [0.1, 2.0])
    assert np.isfinite(result)
