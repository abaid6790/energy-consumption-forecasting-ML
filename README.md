# ⚡ Energy Consumption Forecasting System

A production-style **machine learning and energy analytics platform** for forecasting household electricity consumption, analyzing historical usage patterns, detecting anomalies, comparing forecasting models, and exploring future energy demand through an interactive Flask dashboard.

The system combines a complete **time-series machine learning pipeline** with a web-based analytics interface. It automatically cleans and transforms consumption data, engineers leakage-safe temporal features, trains multiple forecasting models, evaluates them using chronological validation, selects the best-performing model, and serves forecasts through both a dashboard and REST API.

> **No hardcoded analytics:** dashboard statistics, forecasts, model metrics, feature importance, anomalies, and insights are generated from the actual dataset and trained model.

---

## ✨ Key Highlights

* 📊 End-to-end energy consumption forecasting pipeline
* 🤖 Five machine learning and baseline forecasting approaches
* 🧠 Automatic best-model selection using validation RMSE
* ⏳ Strict chronological train/validation/test splitting
* 🔒 Leakage-safe lag and rolling-window feature engineering
* 📈 Interactive Plotly visualizations
* 🔮 Configurable 7/14/30/60/90-period forecasting
* 🚨 Multiple anomaly-detection techniques
* 📁 CSV upload with comprehensive server-side validation
* 🗂️ Forecast history stored in SQLite
* 📋 Model comparison and feature-importance analysis
* 🔌 REST API for dashboard and external integrations
* 🛡️ CSRF protection, secure uploads, size limits, and safe error handling
* 🧪 Automated testing with pytest
* 🖥️ No frontend build system required

---

## 📌 Overview

The application processes historical household electricity consumption through the following workflow:

```text
Historical Energy Data
        │
        ▼
   Data Loading
        │
        ▼
   Data Validation
        │
        ▼
 Timestamp Parsing & Sorting
        │
        ▼
 Missing-Value Handling
        │
        ▼
     Resampling
        │
        ▼
 Feature Engineering
        │
        ▼
Chronological Train / Validation / Test Split
        │
        ▼
   Model Training
        │
        ▼
 Model Comparison
        │
        ▼
 Best Model Selection
        │
        ▼
 Future Forecasting
        │
        ├──────────────► Analytics
        │
        ├──────────────► Anomaly Detection
        │
        ├──────────────► Model Evaluation
        │
        ▼
    Saved Model
        │
        ▼
 Flask API + Dashboard
```

The system is designed specifically for **time-series forecasting**, meaning historical observations are never randomly shuffled before training or evaluation.

---

## 🚀 Features

### 📊 Data Processing

* Automatic timestamp parsing
* Duplicate detection and removal
* Missing-value handling
* Chronological sorting
* Frequency resampling
* Gap detection
* Dataset validation
* Minimum-row validation
* CSV schema validation

### 🧩 Feature Engineering

The forecasting pipeline automatically generates:

* Calendar features
* Cyclical time features
* Lag features
* Rolling mean features
* Rolling standard-deviation features
* Weekend indicators
* Hour/day/month seasonal information

All lag and rolling features are generated using shifted historical values to prevent future-data leakage.

### 🤖 Forecasting Models

The system compares five approaches:

1. Naive Forecast
2. Moving Average
3. Linear Regression
4. Random Forest
5. XGBoost

The best model is selected automatically based on **validation RMSE**.

The winning model is **never hardcoded**.

Depending on the dataset, a simpler model such as Linear Regression may outperform more complex models such as XGBoost.

---

## 📈 Dashboard

The Flask dashboard provides multiple pages for exploring the forecasting system.

### Dashboard

Displays:

* Current consumption
* Average consumption
* Peak consumption
* Next 7-day forecast total
* Best-performing model
* Key energy statistics
* Forecast visualization

### Forecast

Users can:

* Select forecasting frequency
* Select forecast horizon
* Generate future predictions
* View forecast charts
* Inspect forecast tables
* Download predictions as `forecast.csv`

Supported horizons:

```text
7
14
30
60
90
```

### Energy Analytics

Provides:

* Hourly consumption patterns
* Day-of-week patterns
* Weekly trends
* Monthly trends
* Consumption summaries
* Rule-based energy insights

### Anomaly Detection

Historical consumption can be analyzed using:

* Rolling Z-Score
* IQR-based detection
* Isolation Forest

Detected anomalies can be visualized directly against historical consumption.

### Model Performance

Displays:

* Model comparison
* Validation metrics
* Test metrics
* Best model
* Feature importance
* Model metadata

### Forecast History

Stores previous forecasting runs in SQLite and allows users to review previously generated forecasts.

### Dataset Upload

Users can upload their own CSV dataset.

The server validates:

* File extension
* File size
* Required columns
* Timestamp format
* Data types
* Chronological validity
* Minimum row count
* Dataset structure

---

## 🧠 Machine Learning Pipeline

### 1. Data Preparation

Historical consumption data is loaded and validated before any modeling occurs.

### 2. Resampling

Minute-level readings can be transformed into the required forecasting frequency.

Examples:

```text
Hourly
Daily
Weekly
Monthly
```

### 3. Feature Engineering

Temporal features are generated from the timestamp and historical consumption.

### 4. Chronological Splitting

Data is divided without shuffling:

```text
Historical Data
│
├── Training Set
├── Validation Set
└── Test Set
```

The validation set is used for model selection, while the test set remains unseen until final evaluation.

### 5. Model Training

All forecasting approaches are trained using the prepared training data.

### 6. Model Comparison

Models are evaluated using validation metrics.

### 7. Best Model Selection

The model with the lowest validation RMSE is automatically selected.

### 8. Future Forecasting

The selected model is used to generate future consumption predictions.

### 9. Model Persistence

The trained model and supporting metadata are saved to the `models/` directory.

---

## 🤖 Machine Learning Models

| Model                 | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| **Naive**             | Uses the previous observed value as the prediction                   |
| **Moving Average**    | Uses a trailing 7-period rolling mean                                |
| **Linear Regression** | Uses calendar, cyclical, lag, and rolling features                   |
| **Random Forest**     | Ensemble model using 300 trees with maximum depth of 12              |
| **XGBoost**           | Gradient boosting model using 400 rounds and a learning rate of 0.03 |

### Model Selection

The system automatically selects the model with the lowest:

```text
Validation RMSE
```

This allows the application to adapt to the characteristics of the supplied dataset instead of assuming that a more complex model will always perform better.

---

## 🧩 Feature Engineering

### Calendar Features

```text
year
month
day
day_of_week
day_of_year
week_of_year
hour
is_weekend
```

### Cyclical Features

```text
sin_hour
cos_hour
sin_day
cos_day
sin_month
cos_month
```

Cyclical encoding helps machine learning models understand relationships such as:

```text
23:00 → 00:00
Sunday → Monday
December → January
```

### Lag Features

Lag configurations depend on the selected forecasting frequency.

For daily forecasting, examples include:

```text
lag_1
lag_2
lag_3
lag_7
lag_14
lag_30
```

### Rolling Features

Rolling statistics include:

```text
Rolling Mean
Rolling Standard Deviation
```

These calculations are performed on the **shifted historical series**, ensuring that future observations cannot influence current features.

---

## 🔒 Preventing Data Leakage

Time-series forecasting requires special care to prevent future information from entering the training features.

This project follows several safeguards:

* Data is never randomly shuffled
* Train/validation/test splits are chronological
* Lag features use `.shift()`
* Rolling statistics operate only on historical values
* Validation data is not used for training
* Test data remains unseen during model selection

Conceptually:

```text
Past ───────────────────────────────► Future

[ Training ] [ Validation ] [ Test ]
      │             │          │
      │             │          └── Final evaluation
      │             └───────────── Model selection
      └─────────────────────────── Model training
```

---

## 📏 Evaluation Metrics

The project calculates:

| Metric   | Purpose                            |
| -------- | ---------------------------------- |
| **MAE**  | Average absolute prediction error  |
| **MSE**  | Mean squared prediction error      |
| **RMSE** | Penalizes larger prediction errors |
| **MAPE** | Percentage-based error metric      |
| **R²**   | Measures explained variance        |

MAPE is implemented safely to avoid invalid calculations when true consumption values are zero.

Metrics are calculated on a held-out chronological test set using `ml/evaluate.py`.

---

## 📊 Confidence Intervals

Forecast confidence intervals are generated from validation-error residuals when sufficient information is available.

If reliable residual information is not available, confidence intervals are not displayed rather than presenting misleading uncertainty estimates.

---

## 🚨 Anomaly Detection

The system provides three complementary anomaly-detection techniques.

### Rolling Z-Score

Identifies observations that deviate significantly from their local rolling behavior.

### IQR

Uses the interquartile range to identify statistical outliers.

### Isolation Forest

Uses an unsupervised machine learning approach to identify unusual consumption patterns.

Users can compare the detected anomalies against historical consumption through the dashboard.

---

## 📚 Dataset

### Reference Dataset

**UCI Individual Household Electric Power Consumption**

Hebrail & Berard (2006)

The dataset contains minute-level electricity measurements from a household near Paris covering December 2006 through November 2010.

Official dataset:

[UCI Individual Household Electric Power Consumption Dataset](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption?utm_source=chatgpt.com)

Kaggle mirror:

[Electric Power Consumption Dataset — Kaggle](https://www.kaggle.com/datasets/uciml/electric-power-consumption-data-set?utm_source=chatgpt.com)

See:

```text
data/README.md
```

for the complete dataset structure, column reference, and preparation instructions.

### Synthetic Dataset

A synthetic dataset with the same schema is included so the project can be started without downloading the original dataset.

Generate it with:

```bash
python data/generate_sample_data.py
```

> **Important:** The synthetic dataset is intended for development and demonstration. Replace it with the real dataset before making conclusions about real-world energy consumption.

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* SQLite
* SQLAlchemy

### Machine Learning

* Scikit-learn
* XGBoost
* Pandas
* NumPy

### Data Processing

* Pandas
* NumPy
* Time-series resampling
* Statistical analysis

### Visualization

* Plotly
* HTML/CSS
* Vanilla JavaScript
* Jinja2

### Testing

* Pytest

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <this-repo-url>
cd energy-consumption-forecasting
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example configuration:

```bash
copy .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Then configure values such as:

```text
SECRET_KEY
MAX_UPLOAD_MB
```

Never commit your real `.env` file.

---

## 📁 Dataset Preparation

### Option 1 — Generate Sample Data

```bash
python data/generate_sample_data.py
```

### Option 2 — Use the Real Dataset

Download the UCI dataset and place the prepared CSV at:

```text
data/household_power_consumption.csv
```

Refer to:

```text
data/README.md
```

for detailed preparation instructions.

---

## 🧠 Train the Model

Run:

```bash
python ml/train.py \
  --data data/household_power_consumption.csv \
  --frequency daily
```

On Windows, the same command can be written as:

```bash
python ml/train.py --data data/household_power_consumption.csv --frequency daily
```

The training process:

1. Loads the dataset
2. Validates the data
3. Cleans and resamples it
4. Generates features
5. Creates chronological splits
6. Trains all forecasting models
7. Compares validation performance
8. Selects the best model
9. Evaluates the selected model
10. Saves the model and metadata

Generated artifacts include:

```text
models/
├── forecasting_model.pkl
├── feature_columns.pkl
├── preprocessing_pipeline.pkl
├── model_metadata.json
└── history.csv
```

> **Important:** The Flask application loads the saved model. It does **not retrain the model when the application starts**.

---

## ▶️ Run the Application

After training:

```bash
python run.py
```

Open the dashboard:

```text
http://127.0.0.1:5000
```

The application will load the saved forecasting model and expose the dashboard and REST API.

---

## 🔌 API Documentation

| Endpoint                 | Method | Description                                                          |
| ------------------------ | ------ | -------------------------------------------------------------------- |
| `/api/dashboard`         | GET    | Current, average, peak consumption, next-7-day total, and best model |
| `/api/forecast`          | POST   | Generate a future forecast                                           |
| `/api/forecast/download` | GET    | Download forecast as CSV                                             |
| `/api/analytics`         | GET    | Energy analytics and insights                                        |
| `/api/anomalies`         | GET    | Detect historical anomalies                                          |
| `/api/history`           | GET    | Retrieve recent forecast runs                                        |
| `/api/history/<id>`      | GET    | Retrieve a specific forecast run                                     |
| `/api/model`             | GET    | Model metadata and feature importance                                |
| `/api/upload`            | POST   | Upload and validate a CSV dataset                                    |

### Forecast Request

```http
POST /api/forecast
Content-Type: application/json
```

Request body:

```json
{
  "horizon": 7,
  "frequency": "daily"
}
```

### Forecast Download

```text
GET /api/forecast/download?horizon=7
```

Returns:

```text
forecast.csv
```

### Anomaly Detection

All methods:

```text
GET /api/anomalies?method=all
```

Z-score:

```text
GET /api/anomalies?method=zscore
```

IQR:

```text
GET /api/anomalies?method=iqr
```

Isolation Forest:

```text
GET /api/anomalies?method=isolation_forest
```

### Example API Request

```bash
curl -X POST http://127.0.0.1:5000/api/forecast \
  -H "Content-Type: application/json" \
  -d "{\"horizon\":7,\"frequency\":\"daily\"}"
```

---

## 🖥️ Dashboard Pages

```text
Dashboard
Forecast
Dataset Upload
Energy Analytics
Anomaly Detection
Forecast History
Model Performance
About
```

The interface uses:

* Flask
* Jinja templates
* Vanilla JavaScript
* Plotly
* HTML5
* CSS3

There is **no frontend build step** and no React/Next.js dependency.

---

## 📸 Screenshots

Add screenshots of the completed dashboard inside:

```text
screenshots/
```

Recommended screenshots:

```text
screenshots/
├── dashboard.png
├── forecast.png
├── analytics.png
├── anomalies.png
├── model-performance.png
├── history.png
└── dataset-upload.png
```

Example:

```markdown
## 📸 Screenshots

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Forecasting

![Forecast](screenshots/forecast.png)

### Energy Analytics

![Analytics](screenshots/analytics.png)

### Anomaly Detection

![Anomaly Detection](screenshots/anomalies.png)

### Model Performance

![Model Performance](screenshots/model-performance.png)
```

---

## 📂 Project Structure

```text
energy-consumption-forecasting/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   └── static/
│
├── ml/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── features.py
│   ├── train.py
│   ├── evaluate.py
│   ├── forecasting.py
│   └── anomalies.py
│
├── models/
│   ├── forecasting_model.pkl
│   ├── feature_columns.pkl
│   ├── preprocessing_pipeline.pkl
│   ├── model_metadata.json
│   └── history.csv
│
├── data/
│   ├── README.md
│   └── generate_sample_data.py
│
├── tests/
│   └── ...
│
├── uploads/
│
├── exports/
│
├── instance/
│   └── database.sqlite
│
├── run.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

> Generated models, uploaded datasets, SQLite files, exports, and other runtime artifacts should remain excluded from Git when appropriate.

---

## 🔐 Security

The application includes several security measures.

### File Upload Security

* Server-side file validation
* Allowed file extension checking
* Maximum upload-size enforcement
* Required-column validation
* Timestamp validation
* Minimum-row validation
* `secure_filename()` protection
* Directory traversal protection
* Path-containment checks

### Application Security

* CSRF protection for form submissions
* Environment-based secrets
* No secrets committed to source control
* Custom 404/413/500 error handlers
* No stack traces exposed to users
* No filesystem paths exposed in API responses
* Uploaded files are parsed as data only
* Uploaded content is never executed
* Parameterized SQLite queries

### API Security

JSON-only API endpoints are explicitly exempted from form CSRF protection because they are not browser form-submission vectors.

---

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

Tests cover key areas of:

* Data processing
* Feature engineering
* Forecasting
* Model evaluation
* Anomaly detection
* API behavior
* Validation logic

---

## ⚙️ Configuration

Application behavior can be configured through environment variables.

Example:

```env
SECRET_KEY=your-secret-key
MAX_UPLOAD_MB=50
```

Additional configuration can be added as the application evolves.

Never place production secrets directly inside Python source files.

---

## 📌 Important Notes & Limitations

This project is designed as a **portfolio-quality forecasting and analytics system**, not as a certified utility-grade energy forecasting solution.

Forecast quality depends heavily on:

* Dataset quality
* Sampling frequency
* Historical coverage
* Seasonal patterns
* Feature configuration
* Model performance
* Unexpected real-world events

The included confidence intervals are empirical estimates based on validation residuals and should not be interpreted as formal probabilistic guarantees.

---

## 🔮 Future Improvements

Potential extensions include:

* LSTM forecasting
* GRU forecasting
* Transformer-based time-series models
* SARIMA
* Prophet
* Exponential Smoothing
* Weather-aware forecasting
* Temperature-aware forecasting
* Solar generation forecasting
* Multi-building forecasting
* Real-time IoT ingestion
* Automated model retraining
* Model drift monitoring
* Cloud deployment
* User authentication and multi-user workspaces
* PostgreSQL support
* Scheduled forecasting jobs
* Advanced probabilistic forecasting

---

## 🎯 Project Goals

This project demonstrates practical implementation of:

```text
Python
Machine Learning
Time-Series Forecasting
Feature Engineering
Data Preprocessing
Model Evaluation
Anomaly Detection
Flask
REST APIs
Data Visualization
SQLite
Security
Testing
```

It is intended to showcase how a machine-learning model can be transformed into a complete, usable application rather than remaining only as a notebook or standalone training script.

---

## 👨‍💻 Author

**Abaid-ur-Rehman**

Built as a portfolio-ready **Energy Analytics & Machine Learning Forecasting Platform**, combining time-series forecasting, anomaly detection, interactive analytics, model evaluation, and a production-style Flask web application.
