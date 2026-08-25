"""Computes analytics, rule-based insights, and feature importance from real data."""
from __future__ import annotations

import numpy as np
import pandas as pd

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class AnalyticsService:
    def __init__(self, data_service):
        self.data_service = data_service

    def _history(self) -> pd.DataFrame:
        df = self.data_service.history.copy()
        if df.empty:
            return df
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["month"] = df["timestamp"].dt.to_period("M").astype(str)
        df["week"] = df["timestamp"].dt.to_period("W").astype(str)
        df["hour"] = df["timestamp"].dt.hour
        return df

    def daily_series(self) -> list[dict]:
        df = self.data_service.history
        return [
            {"timestamp": t.strftime("%Y-%m-%d"), "value": round(float(v), 3)}
            for t, v in zip(df["timestamp"], df["energy_consumption"])
        ]

    def weekly_series(self) -> list[dict]:
        df = self._history()
        if df.empty:
            return []
        grouped = df.groupby("week")["energy_consumption"].mean().reset_index()
        return [
            {"period": row["week"], "value": round(float(row["energy_consumption"]), 3)}
            for _, row in grouped.iterrows()
        ]

    def monthly_series(self) -> list[dict]:
        df = self._history()
        if df.empty:
            return []
        grouped = df.groupby("month")["energy_consumption"].mean().reset_index()
        return [
            {"period": row["month"], "value": round(float(row["energy_consumption"]), 3)}
            for _, row in grouped.iterrows()
        ]

    def hourly_pattern(self) -> list[dict]:
        df = self._history()
        if df.empty or df["hour"].nunique() <= 1:
            return []
        grouped = df.groupby("hour")["energy_consumption"].mean().reset_index()
        return [
            {"hour": int(row["hour"]), "value": round(float(row["energy_consumption"]), 3)}
            for _, row in grouped.iterrows()
        ]

    def day_of_week_pattern(self) -> list[dict]:
        df = self._history()
        if df.empty:
            return []
        grouped = df.groupby("day_of_week")["energy_consumption"].mean().reindex(range(7))
        return [
            {"day": DAY_NAMES[i], "value": round(float(v), 3) if pd.notna(v) else 0.0}
            for i, v in grouped.items()
        ]

    def insights(self) -> list[str]:
        """Generates rule-based insights strictly from the actual dataset."""
        df = self._history()
        if df.empty or len(df) < 4:
            return ["Not enough historical data yet to generate insights."]

        insights = []

        if df["hour"].nunique() > 1:
            hourly = df.groupby("hour")["energy_consumption"].mean()
            peak_hour = int(hourly.idxmax())
            insights.append(
                f"Peak consumption typically occurs around {peak_hour:02d}:00."
            )

        weekday_avg = df[df["day_of_week"] < 5]["energy_consumption"].mean()
        weekend_avg = df[df["day_of_week"] >= 5]["energy_consumption"].mean()
        if pd.notna(weekday_avg) and pd.notna(weekend_avg) and weekday_avg > 0:
            pct_diff = (weekend_avg - weekday_avg) / weekday_avg * 100
            direction = "higher" if pct_diff >= 0 else "lower"
            insights.append(
                f"Weekend consumption is approximately {abs(pct_diff):.1f}% {direction} "
                f"than weekday consumption."
            )

        max_row = df.loc[df["energy_consumption"].idxmax()]
        insights.append(
            f"The highest recorded consumption ({max_row['energy_consumption']:.2f} "
            f"{self.data_service.unit}) occurred on {max_row['timestamp'].strftime('%Y-%m-%d')}."
        )

        half = len(df) // 2
        if half > 0:
            first_half_avg = df["energy_consumption"].iloc[:half].mean()
            second_half_avg = df["energy_consumption"].iloc[half:].mean()
            if first_half_avg > 0:
                pct_change = (second_half_avg - first_half_avg) / first_half_avg * 100
                direction = "increased" if pct_change >= 0 else "decreased"
                insights.append(
                    f"Average consumption {direction} by {abs(pct_change):.1f}% comparing "
                    f"the first half of the recorded period with the second half."
                )

        return insights

    def feature_importance(self) -> list[dict]:
        model = self.data_service.model
        cols = self.data_service.feature_columns
        if model is None or not cols or not hasattr(model, "feature_importances_"):
            return []
        importances = model.feature_importances_
        pairs = sorted(zip(cols, importances), key=lambda x: x[1], reverse=True)
        total = sum(v for _, v in pairs) or 1.0
        return [
            {"feature": name, "importance": round(float(val) / float(total), 4)}
            for name, val in pairs[:15]
        ]
