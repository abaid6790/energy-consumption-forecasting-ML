import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me-in-production")
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH", os.path.join(BASE_DIR, "instance", "app.db")
    )

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    EXPORT_FOLDER = os.path.join(BASE_DIR, "exports")
    MODELS_FOLDER = os.path.join(BASE_DIR, "models")
    DATA_FOLDER = os.path.join(BASE_DIR, "data")

    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", 25)) * 1024 * 1024
    ALLOWED_UPLOAD_EXTENSIONS = {"csv"}

    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
