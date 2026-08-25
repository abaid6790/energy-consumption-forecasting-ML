from flask import Blueprint, current_app, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    forecast_service = current_app.extensions["forecast_service"]
    analytics_service = current_app.extensions["analytics_service"]
    data_service = current_app.extensions["data_service"]

    summary = forecast_service.dashboard_summary()
    daily = analytics_service.daily_series()

    return render_template(
        "dashboard.html",
        summary=summary,
        daily=daily,
        dataset_name=data_service.active_dataset_name,
        ready=data_service.is_ready(),
    )


@main_bp.route("/model")
def model_performance():
    data_service = current_app.extensions["data_service"]
    analytics_service = current_app.extensions["analytics_service"]

    metadata = data_service.metadata
    metrics = metadata.get("metrics", {})
    best_model = metadata.get("best_model")

    comparison = []
    for name, m in metrics.items():
        row = {"model": name, **m.get("test", {})}
        comparison.append(row)
    comparison.sort(key=lambda r: r.get("RMSE", float("inf")))

    feature_importance = analytics_service.feature_importance()

    return render_template(
        "model.html",
        best_model=best_model,
        comparison=comparison,
        feature_importance=feature_importance,
        metadata=metadata,
        ready=data_service.is_ready(),
    )


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/api/dashboard")
def api_dashboard():
    forecast_service = current_app.extensions["forecast_service"]
    return jsonify(forecast_service.dashboard_summary())


@main_bp.route("/api/model")
def api_model():
    data_service = current_app.extensions["data_service"]
    analytics_service = current_app.extensions["analytics_service"]
    return jsonify(
        {
            "metadata": data_service.metadata,
            "feature_importance": analytics_service.feature_importance(),
        }
    )
