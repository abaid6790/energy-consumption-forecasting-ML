"""
Generates future forecasts from the saved model + historical series.

Because lag/rolling features depend on prior values, multi-step forecasts
are generated recursively: predict step 1, append it to the working
history, recompute features, predict step 2, and so on.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ml.feature_engineering import build_features

FREQ_OFFSET = {
    "hourly": pd.Timedelta(hours=1),
    "daily": pd.Timedelta(days=1),
    "weekly": pd.Timedelta(weeks=1),
    "monthly": pd.DateOffset(months=1),
}


def _n_recent_for_features(frequency: str) -> int:
    # Keep enough trailing history so the longest lag/rolling window is valid.
    return {"hourly": 24 * 10, "daily": 45, "weekly": 20, "monthly": 24}.get(frequency, 45)


def generate_forecast(
    model,
    feature_columns: list[str],
    history: pd.DataFrame,
    frequency: str,
    horizon: int,
    residual_std: float | None = None,
) -> pd.DataFrame:
    """
    model: fitted sklearn/xgboost regressor with .predict(X)
    history: dataframe with columns [timestamp, energy_consumption], sorted ascending
    residual_std: if provided (e.g. validation-set residual std), used to build
                  a simple +/- 1.96*std confidence interval. Omitted if None.

    Returns a dataframe: timestamp, predicted_consumption, [lower_bound, upper_bound]
    """
    working = history[["timestamp", "energy_consumption"]].copy().sort_values("timestamp")
    working = working.tail(max(len(working), _n_recent_for_features(frequency) + horizon))
    offset = FREQ_OFFSET[frequency]

    predictions = []
    last_ts = working["timestamp"].iloc[-1]

    for step in range(horizon):
        next_ts = working["timestamp"].iloc[-1] + offset

        # Append a placeholder row so build_features can compute calendar
        # features for next_ts; the target value itself is not used as input
        # (lag/rolling features are shifted, so the placeholder's own value
        # never leaks into its own prediction).
        placeholder = pd.DataFrame(
            {"timestamp": [next_ts], "energy_consumption": [np.nan]}
        )
        candidate = pd.concat([working, placeholder], ignore_index=True)

        # Temporarily fill NaN target with last known value purely so
        # feature engineering doesn't drop the row; it is not used as a
        # lag/rolling input for itself (those use .shift already).
        candidate_filled = candidate.copy()
        candidate_filled["energy_consumption"] = candidate_filled["energy_consumption"].ffill()

        featured, _ = build_features(candidate_filled, frequency=frequency)
        last_row = featured.iloc[[-1]]
        X_next = last_row[feature_columns]

        pred = float(model.predict(X_next)[0])
        pred = max(pred, 0.0)  # energy consumption can't be negative

        row = {"timestamp": next_ts, "predicted_consumption": round(pred, 3)}
        if residual_std is not None:
            margin = 1.96 * residual_std
            row["lower_bound"] = round(max(pred - margin, 0.0), 3)
            row["upper_bound"] = round(pred + margin, 3)

        predictions.append(row)

        # Append the real prediction (not the placeholder) to working history
        # so the next step's lag/rolling features see it.
        working = pd.concat(
            [working, pd.DataFrame({"timestamp": [next_ts], "energy_consumption": [pred]})],
            ignore_index=True,
        )

    return pd.DataFrame(predictions)
