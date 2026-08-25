"""Business logic for generating forecasts and dashboard summary stats."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ml.forecast import generate_forecast

VALID_HORIZONS = [7, 14, 30, 60, 90]
VALID_FREQUENCIES = ["hourly", "daily", "weekly", "monthly"]


class ForecastService:
    def __init__(self, data_service):
        self.data_service = data_service

    def _residual_std(self) -> float | None:
        """
        Derives a simple uncertainty estimate from the saved validation
        metrics (RMSE approximates residual std for a well-fit model).
        Returns None if unavailable, so the caller can omit intervals
        rather than fabricate them.
        """
        metrics = self.data_service.metadata.get("metrics", {})
        best_model = self.data_service.metadata.get("best_model")
        model_metrics = metrics.get(best_model, {})
        val_metrics = model_metrics.get("val", {})
        rmse = val_metrics.get("RMSE")
        return float(rmse) if rmse is not None else None

    def best_model_name(self) -> str:
        return self.data_service.metadata.get("best_model", "N/A")

    def generate(self, horizon: int, frequency: str | None = None) -> pd.DataFrame:
        if not self.data_service.is_ready():
            raise RuntimeError("Unable to generate forecast: no trained model is available.")

        freq = frequency or self.data_service.frequency
        if freq != self.data_service.frequency:
            # The saved model was trained at a specific frequency. Forecasting
            # at a different frequency would require retraining, which the
            # spec says happens offline via ml/train.py, not at request time.
            freq = self.data_service.frequency

        residual_std = self._residual_std()
        forecast_df = generate_forecast(
            model=self.data_service.model,
            feature_columns=self.data_service.feature_columns,
            history=self.data_service.history,
            frequency=freq,
            horizon=horizon,
            residual_std=residual_std,
        )
        return forecast_df

    def dashboard_summary(self) -> dict:
        history = self.data_service.history
        if history.empty:
            return {
                "current": None,
                "average": None,
                "peak": None,
                "next_7_days_total": None,
                "best_model": self.best_model_name(),
                "unit": self.data_service.unit,
            }

        current = float(history["energy_consumption"].iloc[-1])
        average = float(history["energy_consumption"].mean())
        peak = float(history["energy_consumption"].max())

        next7_total = None
        try:
            fc = self.generate(horizon=7)
            next7_total = float(fc["predicted_consumption"].sum())
        except Exception:
            next7_total = None

        return {
            "current": round(current, 3),
            "average": round(average, 3),
            "peak": round(peak, 3),
            "next_7_days_total": round(next7_total, 3) if next7_total is not None else None,
            "best_model": self.best_model_name(),
            "unit": self.data_service.unit,
        }
