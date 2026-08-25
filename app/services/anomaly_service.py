"""Wraps ml/anomaly_detection.py for the Flask app."""
from __future__ import annotations

from ml.anomaly_detection import detect_anomalies, summarize_anomalies


class AnomalyService:
    def __init__(self, data_service):
        self.data_service = data_service

    def detect(self, method: str = "all") -> dict:
        history = self.data_service.history
        if history.empty:
            return {"anomalies": [], "chart_data": []}

        flagged = detect_anomalies(history, method=method)
        anomalies = summarize_anomalies(flagged)

        chart_data = [
            {
                "timestamp": row["timestamp"].strftime("%Y-%m-%d"),
                "value": round(float(row["energy_consumption"]), 3),
                "is_anomaly": bool(row["is_anomaly"]),
            }
            for _, row in flagged.iterrows()
        ]
        return {"anomalies": anomalies, "chart_data": chart_data, "count": len(anomalies)}
