import os

from flask import Flask
from flask_wtf import CSRFProtect

from app.config import Config
from app.services.data_service import DataService
from app.services.forecast_service import ForecastService
from app.services.analytics_service import AnalyticsService
from app.services.anomaly_service import AnomalyService
from app.services.history_db import HistoryDB

csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)
    os.makedirs(os.path.dirname(app.config["DATABASE_PATH"]), exist_ok=True)

    csrf.init_app(app)

    # Shared services, attached to the app so blueprints can reach them
    # via `current_app.extensions[...]`.
    data_service = DataService(app.config)
    app.extensions["data_service"] = data_service
    app.extensions["forecast_service"] = ForecastService(data_service)
    app.extensions["analytics_service"] = AnalyticsService(data_service)
    app.extensions["anomaly_service"] = AnomalyService(data_service)
    app.extensions["history_db"] = HistoryDB(app.config["DATABASE_PATH"])

    from app.routes.main import main_bp
    from app.routes.forecast import forecast_bp
    from app.routes.upload import upload_bp
    from app.routes.analytics import analytics_bp
    from app.routes.history import history_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(forecast_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(history_bp)

    # These blueprints expose JSON-only APIs (POST bodies are application/json,
    # not browser <form> submissions), so session-cookie CSRF tokens don't
    # apply the same way; they're exempted from Flask-WTF's CSRF check.
    # File upload validation, size limits, and input validation are still
    # enforced inside each route/service.
    csrf.exempt(forecast_bp)
    csrf.exempt(upload_bp)

    # Uploaded CSV content is never executed and templates auto-escape by
    # default (Jinja2), which covers the main injection surfaces here.

    @app.errorhandler(413)
    def too_large(e):
        return {"error": "Uploaded file is too large."}, 413

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found."}, 404

    @app.errorhandler(500)
    def server_error(e):
        # Never leak stack traces or internal paths to the client.
        app.logger.exception("Unhandled server error")
        return {"error": "An unexpected error occurred. Please try again."}, 500

    return app
