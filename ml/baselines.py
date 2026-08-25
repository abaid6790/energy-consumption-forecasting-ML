"""Simple baseline forecasters that any ML model must beat to be worth using."""
from __future__ import annotations

import numpy as np
import pandas as pd


class NaiveForecaster:
    """Predicts the next value as equal to the previous observed value."""

    name = "Naive"

    def fit(self, y_train: pd.Series):
        self._last_train_value = y_train.iloc[-1]
        return self

    def predict(self, y_context: pd.Series) -> np.ndarray:
        """y_context: the true series immediately preceding each prediction point."""
        return y_context.shift(1).bfill().to_numpy()


class MovingAverageForecaster:
    """Predicts using a trailing rolling average of the previous `window` values."""

    name = "Moving Average"

    def __init__(self, window: int = 7):
        self.window = window

    def fit(self, y_train: pd.Series):
        return self

    def predict(self, y_context: pd.Series) -> np.ndarray:
        shifted = y_context.shift(1)
        return shifted.rolling(self.window, min_periods=1).mean().bfill().to_numpy()
