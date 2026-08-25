import json

from flask import Blueprint, current_app, jsonify, render_template

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
def history_page():
    history_db = current_app.extensions["history_db"]
    runs = history_db.list_runs(limit=50)
    return render_template("history.html", runs=runs)


@history_bp.route("/api/history")
def api_history():
    history_db = current_app.extensions["history_db"]
    runs = history_db.list_runs(limit=50)
    return jsonify({"runs": runs})


@history_bp.route("/api/history/<int:run_id>")
def api_history_detail(run_id):
    history_db = current_app.extensions["history_db"]
    run = history_db.get_run(run_id)
    if run is None:
        return jsonify({"error": "Forecast run not found."}), 404
    run["forecast"] = json.loads(run["forecast_json"])
    del run["forecast_json"]
    return jsonify(run)
