import io
import json
from datetime import datetime, timezone

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
)

from app.services.forecast_service import VALID_FREQUENCIES, VALID_HORIZONS

forecast_bp = Blueprint("forecast", __name__)


def _safe_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@forecast_bp.route("/forecast")
def forecast_page():
    data_service = current_app.extensions["data_service"]
    return render_template(
        "forecast.html",
        horizons=VALID_HORIZONS,
        frequencies=VALID_FREQUENCIES,
        best_model=data_service.metadata.get("best_model", "N/A"),
        ready=data_service.is_ready(),
    )


@forecast_bp.route("/api/forecast", methods=["POST"])
def api_forecast():
    data_service = current_app.extensions["data_service"]
    forecast_service = current_app.extensions["forecast_service"]
    history_db = current_app.extensions["history_db"]

    if not data_service.is_ready():
        return _safe_error("No trained model is available. Run ml/train.py first.", 503)

    payload = request.get_json(silent=True) or {}
    horizon = payload.get("horizon", 7)
    frequency = payload.get("frequency", data_service.frequency)

    try:
        horizon = int(horizon)
    except (TypeError, ValueError):
        return _safe_error("Horizon must be an integer.")

    if horizon <= 0 or horizon > 90:
        return _safe_error("Horizon must be between 1 and 90.")
    if frequency not in VALID_FREQUENCIES:
        return _safe_error(f"Frequency must be one of {VALID_FREQUENCIES}.")

    try:
        forecast_df = forecast_service.generate(horizon=horizon, frequency=frequency)
    except RuntimeError as exc:
        return _safe_error(str(exc), 503)
    except Exception:
        current_app.logger.exception("Forecast generation failed")
        return _safe_error("Unable to generate forecast.", 500)

    records = forecast_df.assign(
        timestamp=lambda d: d["timestamp"].dt.strftime("%Y-%m-%d")
    ).to_dict(orient="records")

    # Persist this run to history
    try:
        history_db.add_run(
            created_at=datetime.now(timezone.utc).isoformat(),
            dataset_name=data_service.active_dataset_name,
            forecast_frequency=data_service.frequency,
            forecast_horizon=horizon,
            model_name=forecast_service.best_model_name(),
            forecast_start=records[0]["timestamp"] if records else "",
            forecast_end=records[-1]["timestamp"] if records else "",
            forecast_json=json.dumps(records),
        )
    except Exception:
        current_app.logger.exception("Failed to persist forecast run")

    return jsonify(
        {
            "model": forecast_service.best_model_name(),
            "frequency": data_service.frequency,
            "horizon": horizon,
            "unit": data_service.unit,
            "forecast": records,
            "history": data_service.history.assign(
                timestamp=lambda d: d["timestamp"].dt.strftime("%Y-%m-%d")
            ).tail(90).to_dict(orient="records"),
        }
    )


@forecast_bp.route("/api/forecast/download")
def download_forecast():
    """Regenerates the last-requested forecast as a downloadable CSV."""
    data_service = current_app.extensions["data_service"]
    forecast_service = current_app.extensions["forecast_service"]

    horizon = request.args.get("horizon", 7, type=int)
    if horizon <= 0 or horizon > 90:
        return _safe_error("Horizon must be between 1 and 90.")

    if not data_service.is_ready():
        return _safe_error("No trained model is available.", 503)

    try:
        forecast_df = forecast_service.generate(horizon=horizon)
    except Exception:
        return _safe_error("Unable to generate forecast.", 500)

    cols = ["timestamp", "predicted_consumption"]
    if "lower_bound" in forecast_df.columns and "upper_bound" in forecast_df.columns:
        cols += ["lower_bound", "upper_bound"]

    buf = io.StringIO()
    export_df = forecast_df[cols].copy()
    export_df["timestamp"] = export_df["timestamp"].dt.strftime("%Y-%m-%d")
    export_df.to_csv(buf, index=False)

    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=forecast.csv"},
    )
