from flask import Blueprint, current_app, jsonify, render_template, request

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
def analytics_page():
    analytics_service = current_app.extensions["analytics_service"]
    data_service = current_app.extensions["data_service"]

    return render_template(
        "analytics.html",
        insights=analytics_service.insights(),
        weekly=analytics_service.weekly_series(),
        monthly=analytics_service.monthly_series(),
        hourly=analytics_service.hourly_pattern(),
        day_of_week=analytics_service.day_of_week_pattern(),
        ready=data_service.is_ready(),
    )


@analytics_bp.route("/api/analytics")
def api_analytics():
    analytics_service = current_app.extensions["analytics_service"]
    return jsonify(
        {
            "insights": analytics_service.insights(),
            "weekly": analytics_service.weekly_series(),
            "monthly": analytics_service.monthly_series(),
            "hourly": analytics_service.hourly_pattern(),
            "day_of_week": analytics_service.day_of_week_pattern(),
            "daily": analytics_service.daily_series(),
        }
    )


@analytics_bp.route("/anomalies")
def anomalies_page():
    anomaly_service = current_app.extensions["anomaly_service"]
    data_service = current_app.extensions["data_service"]
    result = anomaly_service.detect(method="all")
    return render_template(
        "anomalies.html",
        anomalies=result["anomalies"],
        chart_data=result["chart_data"],
        count=result["count"],
        ready=data_service.is_ready(),
    )


@analytics_bp.route("/api/anomalies")
def api_anomalies():
    anomaly_service = current_app.extensions["anomaly_service"]
    method = request.args.get("method", "all")
    return jsonify(anomaly_service.detect(method=method))
