"""Forecast evaluation metrics."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-3) -> float:
    """
    Mean Absolute Percentage Error. Zero/near-zero true values are handled by
    flooring the denominator at `epsilon` rather than dividing by zero.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.where(np.abs(y_true) < epsilon, epsilon, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100)


def compute_metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_true, y_pred) if len(y_true) > 1 else float("nan")

    return {
        "MAE": round(float(mae), 4),
        "MSE": round(float(mse), 4),
        "RMSE": round(rmse, 4),
        "MAPE": round(mape(y_true, y_pred), 4),
        "R2": round(float(r2), 4),
    }
