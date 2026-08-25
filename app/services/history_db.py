"""Lightweight SQLite storage for forecast run history (no ORM needed)."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager

_SCHEMA = """
CREATE TABLE IF NOT EXISTS forecast_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    forecast_frequency TEXT NOT NULL,
    forecast_horizon INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    forecast_start TEXT NOT NULL,
    forecast_end TEXT NOT NULL,
    forecast_json TEXT NOT NULL
);
"""


class HistoryDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(_SCHEMA)

    def add_run(
        self,
        created_at: str,
        dataset_name: str,
        forecast_frequency: str,
        forecast_horizon: int,
        model_name: str,
        forecast_start: str,
        forecast_end: str,
        forecast_json: str,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO forecast_runs
                   (created_at, dataset_name, forecast_frequency, forecast_horizon,
                    model_name, forecast_start, forecast_end, forecast_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    created_at,
                    dataset_name,
                    forecast_frequency,
                    forecast_horizon,
                    model_name,
                    forecast_start,
                    forecast_end,
                    forecast_json,
                ),
            )
            return cur.lastrowid

    def list_runs(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM forecast_runs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_run(self, run_id: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM forecast_runs WHERE id = ?", (run_id,)
            ).fetchone()
            return dict(row) if row else None
