# Energy Consumption Forecasting System

A complete, production-style energy consumption forecasting platform: a
time-series ML pipeline (baselines through XGBoost) plus a Flask dashboard
for forecasting, analytics, anomaly detection, and forecast history.

## Overview

The system loads historical household electricity consumption, cleans and
resamples it, engineers calendar/cyclical/lag/rolling features, trains and
compares five forecasting approaches on a strictly chronological
train/validation/test split, and serves the best model through a Flask API
and dashboard. Every number shown in the UI — current/average/peak
consumption, forecasts, model metrics, feature importance, insights — is
computed from the real dataset and the real trained model. Nothing is
hardcoded.

## Features

- Automated data cleaning: timestamp parsing, dedup, missing-value handling, resampling, gap detection
- Feature engineering: calendar, cyclical (sin/cos), lag, and rolling-window features with no future leakage
- Five forecasting models compared on real metrics: Naive, Moving Average, Linear Regression, Random Forest, XGBoost
- Chronological (non-shuffled) train/val/test splitting
- Interactive dashboard: current/average/peak consumption, next-7-day forecast total, best model
- Forecast page: pick frequency + horizon (7/14/30/60/90), see chart + table, download `forecast.csv`
- Confidence intervals from validation-error residuals (only shown when genuinely available)
- Energy analytics: hourly pattern, day-of-week pattern, weekly/monthly trends, rule-based insights
- Anomaly detection: rolling z-score, IQR, and Isolation Forest, visualized on the historical chart
- CSV upload with full server-side validation (columns, types, size, chronology, minimum row count)
- Forecast run history stored in SQLite
- Model performance page with a full model comparison table and feature importance
- JSON API for dashboard, forecast, analytics, anomalies, model, and history
- Security basics: CSRF protection on forms, secure filenames, upload size limits, no stack traces in responses, no arbitrary file/code execution

## Dataset

Reference dataset: **UCI Individual Household Electric Power Consumption**
(Hebrail & Berard, 2006) — minute-level readings from one household near
Paris, Dec 2006–Nov 2010.

- https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
- Kaggle mirror: https://www.kaggle.com/datasets/uciml/electric-power-consumption-data-set

See [`data/README.md`](data/README.md) for the full column reference and
download instructions. A synthetic sample dataset with the identical schema
ships with the repo (`data/generate_sample_data.py`) so the project runs
immediately without any download — replace it with the real file before
drawing conclusions from the numbers.

## Forecasting Pipeline

```
Historical Data → Load → Validate → Parse Timestamps → Sort → Handle Missing
→ Resample → Feature Engineering → Chronological Train/Val/Test Split
→ Train Models → Compare → Select Best → Forecast Future → Evaluate
→ Save Model → Flask API → Dashboard
```

Data is **never shuffled** — all splits are chronological, and lag/rolling
features are computed using `.shift()` before any window so no future value
ever leaks into a feature.

## Machine Learning Models

| Model             | Notes                                             |
|--------------------|----------------------------------------------------|
| Naive              | Predicts the previous observed value                |
| Moving Average     | 7-period trailing rolling mean                      |
| Linear Regression  | Calendar + cyclical + lag + rolling features        |
| Random Forest      | 300 trees, max depth 12                             |
| XGBoost            | 400 rounds, learning rate 0.03, early-stopping-ready via validation set |

The best model is selected automatically by **lowest validation RMSE** —
never hardcoded. Run `ml/train.py` yourself to see which model wins on your
data; it can (and does, on the shipped sample data) turn out to be the
simpler Linear Regression model rather than XGBoost.

## Feature Engineering

- **Calendar:** year, month, day, day_of_week, day_of_year, week_of_year, hour, is_weekend
- **Cyclical:** sin_hour, cos_hour, sin_day, cos_day, sin_month, cos_month
- **Lag:** configurable per frequency (e.g. daily: 1, 2, 3, 7, 14, 30 days)
- **Rolling:** mean/std over configurable windows, computed on the *shifted* series only

## Evaluation Metrics

MAE, MSE, RMSE, MAPE (safe against zero true values), and R² — see
`ml/evaluate.py`. Metrics are computed on a held-out chronological test set
that the models never touch during training or model selection.

## Installation

```bash
git clone <this-repo-url>
cd energy-consumption-forecasting
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then edit SECRET_KEY etc.
```

## Dataset Preparation

Either generate the bundled synthetic sample:

```bash
python data/generate_sample_data.py
```

or download the real UCI dataset per [`data/README.md`](data/README.md)
and place it at `data/household_power_consumption.csv`.

## Model Training

```bash
python ml/train.py --data data/household_power_consumption.csv --frequency daily
```

This prints a full model comparison table and saves everything the Flask
app needs to `models/`: `forecasting_model.pkl`, `feature_columns.pkl`,
`preprocessing_pipeline.pkl`, `model_metadata.json`, and `history.csv`.
**The Flask app loads this saved model — it never retrains at startup.**

## Running the Application

```bash
python run.py
```

Then open http://127.0.0.1:5000.

## API Documentation

| Endpoint                     | Method | Description                              |
|-------------------------------|--------|--------------------------------------------|
| `/api/dashboard`              | GET    | Current/average/peak, next-7-day total, best model |
| `/api/forecast`                | POST   | `{"horizon": 7, "frequency": "daily"}` → forecast array |
| `/api/forecast/download`       | GET    | `?horizon=7` → `forecast.csv` download     |
| `/api/analytics`               | GET    | Insights + hourly/day-of-week/weekly/monthly series |
| `/api/anomalies`               | GET    | `?method=all\|zscore\|iqr\|isolation_forest` |
| `/api/history`                 | GET    | Recent forecast runs                       |
| `/api/history/<id>`            | GET    | One run's stored forecast                  |
| `/api/model`                   | GET    | Metadata + feature importance              |
| `/api/upload`                  | POST   | Multipart CSV upload + validation preview  |

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{"horizon": 7, "frequency": "daily"}'
```

## Dashboard

Pages: Dashboard, Forecast, Dataset Upload, Energy Analytics, Anomaly
Detection, Forecast History, Model Performance, About. Built with
server-rendered Jinja templates, vanilla JS, and Plotly for interactive
charts — no frontend build step required.

## Screenshots

_Add screenshots of the running dashboard here (`screenshots/`) before
publishing to GitHub._

## Project Structure

```
energy-consumption-forecasting/
├── app/            # Flask app: routes, services, templates, static assets
├── ml/             # Data loading, preprocessing, features, training, forecasting, anomalies
├── models/         # Saved model + metadata (git-ignored; produced by ml/train.py)
├── data/           # Dataset README + sample-data generator (raw data git-ignored)
├── tests/          # pytest suite covering the pipeline and API
├── uploads/        # User CSV uploads (git-ignored)
├── exports/        # Reserved for exported artifacts (git-ignored)
├── instance/       # SQLite database (git-ignored)
├── run.py
├── requirements.txt
└── .env.example
```

## Security

- Server-side validation on every upload: extension, size (`MAX_UPLOAD_MB`), required columns, timestamp parsing, minimum row count
- `secure_filename()` + path-containment check against directory traversal
- CSRF protection enabled by default (JSON-only API blueprints are explicitly exempted, since they aren't form-submission vectors)
- Secrets and config come from environment variables (`.env`, never committed)
- No stack traces or filesystem paths in error responses (custom 404/413/500 handlers)
- Uploaded file content is parsed with pandas only — never executed
- SQLite access uses parameterized queries (no string-built SQL)

## Future Improvements

- LSTM / GRU / Transformer forecasting
- Prophet, SARIMA, Exponential Smoothing as additional model options
- Weather-aware and temperature-aware forecasting
- Solar generation and multi-building forecasting
- Real-time IoT ingestion and automated retraining
- User accounts and cloud deployment

## Author

Built as a portfolio-ready energy analytics and forecasting application.
