"""
Loads the trained model + historical series and exposes the active dataset
to the rest of the app. Also handles validated CSV uploads.
"""
from __future__ import annotations

import json
import os

import joblib
import pandas as pd
from werkzeug.utils import secure_filename

from ml.dataset_loader import (
    DatasetValidationError,
    load_generic_csv,
    validate_canonical,
)
from ml.preprocessing import run_preprocessing_pipeline


class DataService:
    def __init__(self, config):
        self.config = config
        self._model = None
        self._feature_columns = None
        self._metadata = None
        self._history = None  # canonical cleaned history dataframe
        self._active_dataset_name = "Sample Household Dataset (synthetic demo data)"
        self._load_artifacts()

    # ---------- model / history loading ----------

    def _load_artifacts(self):
        models_dir = self.config["MODELS_FOLDER"]
        model_path = os.path.join(models_dir, "forecasting_model.pkl")
        features_path = os.path.join(models_dir, "feature_columns.pkl")
        metadata_path = os.path.join(models_dir, "model_metadata.json")
        history_path = os.path.join(models_dir, "history.csv")

        if os.path.exists(model_path):
            self._model = joblib.load(model_path)
        if os.path.exists(features_path):
            self._feature_columns = joblib.load(features_path)
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                self._metadata = json.load(f)
        if os.path.exists(history_path):
            self._history = pd.read_csv(history_path, parse_dates=["timestamp"])

    def is_ready(self) -> bool:
        return self._model is not None and self._history is not None

    @property
    def model(self):
        return self._model

    @property
    def feature_columns(self):
        return self._feature_columns or []

    @property
    def metadata(self):
        return self._metadata or {}

    @property
    def history(self) -> pd.DataFrame:
        if self._history is None:
            return pd.DataFrame(columns=["timestamp", "energy_consumption"])
        return self._history

    @property
    def frequency(self) -> str:
        return self.metadata.get("frequency", "daily")

    @property
    def active_dataset_name(self) -> str:
        return self._active_dataset_name

    @property
    def unit(self) -> str:
        return self.metadata.get("unit", "kW")

    # ---------- CSV upload handling ----------

    def allowed_file(self, filename: str) -> bool:
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.config["ALLOWED_UPLOAD_EXTENSIONS"]
        )

    def process_upload(self, file_storage) -> dict:
        """
        Validates and loads an uploaded CSV. Returns a preview dict.
        Raises DatasetValidationError with a user-safe message on failure.
        """
        filename = file_storage.filename or ""
        if not filename:
            raise DatasetValidationError("No file was selected.")
        if not self.allowed_file(filename):
            raise DatasetValidationError("Invalid file type. Only .csv files are accepted.")

        safe_name = secure_filename(filename)
        save_path = os.path.join(self.config["UPLOAD_FOLDER"], safe_name)
        # Path traversal / directory safety: secure_filename strips path
        # separators, and we constrain the save path to UPLOAD_FOLDER.
        save_path = os.path.abspath(save_path)
        if not save_path.startswith(os.path.abspath(self.config["UPLOAD_FOLDER"])):
            raise DatasetValidationError("Invalid file path.")

        file_storage.save(save_path)

        try:
            df = pd.read_csv(save_path, nrows=5)
        except Exception:
            raise DatasetValidationError("Invalid CSV file.")

        cols_lower = {c.lower(): c for c in df.columns}
        ts_col = cols_lower.get("timestamp") or cols_lower.get("date")
        val_col = cols_lower.get("energy_consumption") or cols_lower.get("consumption")

        if ts_col is None:
            raise DatasetValidationError("Required column 'timestamp' is missing.")
        if val_col is None:
            raise DatasetValidationError("Required column 'energy_consumption' is missing.")

        canonical = load_generic_csv(save_path, timestamp_col=ts_col, value_col=val_col)
        validate_canonical(canonical, min_observations=10)

        n_missing = canonical["energy_consumption"].isna().sum()
        chronological = canonical["timestamp"].is_monotonic_increasing

        preview = {
            "filename": safe_name,
            "rows": len(canonical),
            "date_range": [
                canonical["timestamp"].min().strftime("%Y-%m-%d"),
                canonical["timestamp"].max().strftime("%Y-%m-%d"),
            ],
            "missing_values": int(n_missing),
            "chronological_order": bool(chronological),
            "average_consumption": round(float(canonical["energy_consumption"].mean()), 3),
            "min_consumption": round(float(canonical["energy_consumption"].min()), 3),
            "max_consumption": round(float(canonical["energy_consumption"].max()), 3),
            "preview_rows": canonical.head(5).assign(
                timestamp=lambda d: d["timestamp"].astype(str)
            ).to_dict(orient="records"),
            "saved_path": save_path,
        }
        return preview

    def load_uploaded_as_active(self, saved_path: str, frequency: str = "daily") -> None:
        """Swaps the in-memory active history to an uploaded dataset (session-scoped use)."""
        df = pd.read_csv(saved_path)
        cols_lower = {c.lower(): c for c in df.columns}
        ts_col = cols_lower.get("timestamp") or cols_lower.get("date")
        val_col = cols_lower.get("energy_consumption") or cols_lower.get("consumption")
        canonical = load_generic_csv(saved_path, timestamp_col=ts_col, value_col=val_col)
        validate_canonical(canonical, min_observations=10)
        prep = run_preprocessing_pipeline(canonical, frequency=frequency)
        self._history = prep["data"]
        self._active_dataset_name = os.path.basename(saved_path)
