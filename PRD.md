# ⚡ Energy Consumption Forecasting System

## Product Requirements Document (PRD)

**Version:** 1.0.0
**Status:** Completed / Portfolio Release
**Product Type:** Machine Learning + Energy Analytics Platform
**Primary Stack:** Python, Flask, Pandas, Scikit-learn, XGBoost, Plotly, SQLite

---

## 1. Product Overview

The **Energy Consumption Forecasting System** is a web-based machine learning platform designed to analyze historical household electricity consumption and generate future energy forecasts.

The platform combines:

* Time-series data processing
* Feature engineering
* Machine learning forecasting
* Model comparison
* Energy analytics
* Anomaly detection
* Interactive visualization
* CSV dataset uploads
* Forecast history
* REST APIs
* Model performance monitoring

The primary objective is to transform raw electricity-consumption data into actionable forecasts and understandable energy insights through an accessible web interface.

---

## 2. Problem Statement

Historical energy-consumption datasets often contain:

* Missing values
* Duplicate records
* Irregular timestamps
* Different sampling frequencies
* Seasonal patterns
* Daily and weekly consumption cycles
* Unexpected consumption spikes

Analyzing this data manually is time-consuming and makes it difficult to generate reliable future forecasts.

Many machine-learning forecasting projects stop at model training and do not provide a complete application for interacting with the trained model.

This project addresses that gap by providing an end-to-end system that:

1. Processes raw energy data.
2. Engineers time-series features.
3. Compares multiple forecasting approaches.
4. Automatically selects the best model.
5. Generates future forecasts.
6. Detects unusual consumption behavior.
7. Visualizes historical and predicted energy usage.
8. Provides API access to the forecasting system.

---

## 3. Product Vision

Build a practical and extensible energy forecasting platform that demonstrates how machine learning can be integrated into a complete real-world analytics application.

The system should be:

* Accurate
* Transparent
* Secure
* Easy to use
* Reproducible
* Extensible
* Portfolio-ready

---

## 4. Goals

### Primary Goals

* Build a complete time-series forecasting pipeline.
* Prevent data leakage during feature engineering and evaluation.
* Compare multiple forecasting models.
* Automatically select the best-performing model.
* Provide configurable future forecasting.
* Provide meaningful energy-consumption analytics.
* Detect historical anomalies.
* Provide an interactive web dashboard.
* Support user-provided CSV datasets.
* Expose forecasting functionality through REST APIs.
* Store historical forecasting runs.
* Follow basic application-security practices.

### Secondary Goals

* Make the project easy to run locally.
* Provide a synthetic dataset for immediate testing.
* Maintain a modular architecture.
* Make it easy to add additional forecasting models.
* Provide automated tests.

---

## 5. Non-Goals

The following are outside the scope of the initial release:

* Utility-grade electricity forecasting
* Real-time electricity-grid control
* Automated energy purchasing
* Electricity billing
* Hardware control
* Smart-meter device management
* Medical or safety-critical decision making
* Guaranteed forecast accuracy
* Fully automated production-scale cloud infrastructure

---

## 6. Target Users

### 6.1 Data Science Students

Students can use the platform to understand:

* Time-series forecasting
* Feature engineering
* Model comparison
* Evaluation
* Anomaly detection

### 6.2 Machine Learning Developers

Developers can use the architecture as a foundation for extending forecasting models and APIs.

### 6.3 Energy Analysts

Analysts can explore:

* Consumption patterns
* Trends
* Peak usage
* Anomalies
* Forecasted demand

### 6.4 Portfolio Reviewers

Recruiters and technical reviewers can evaluate the complete machine-learning application architecture.

---

## 7. User Stories

### Dataset Management

> As a user, I want to upload an energy-consumption CSV so that I can analyze my own dataset.

> As a user, I want invalid datasets to be rejected with clear errors so that I know what needs to be fixed.

### Forecasting

> As a user, I want to select a forecasting horizon so that I can generate predictions for different future periods.

> As a user, I want the system to automatically select the best-performing model so that I do not need to manually choose one.

### Analytics

> As a user, I want to understand when energy consumption is highest so that I can identify usage patterns.

### Anomaly Detection

> As a user, I want to identify unusual consumption periods so that I can investigate unexpected energy behavior.

### Model Evaluation

> As a user, I want to compare model performance so that I can understand which forecasting approach performs best.

### Forecast History

> As a user, I want previous forecasting runs to be stored so that I can review them later.

---

# 8. Functional Requirements

## FR-01 — Dataset Loading

The system must:

* Load supported CSV datasets.
* Validate dataset structure.
* Parse timestamps.
* Sort records chronologically.
* Detect duplicates.
* Handle missing values.
* Detect data gaps.

---

## FR-02 — Dataset Validation

Uploaded datasets must be validated for:

* File type
* File size
* Required columns
* Timestamp validity
* Data types
* Minimum row count
* Chronological consistency

Invalid files must be rejected safely.

---

## FR-03 — Data Resampling

The system must support configurable time frequencies.

Examples:

```text
Hourly
Daily
Weekly
Monthly
```

Resampling must preserve chronological ordering.

---

## FR-04 — Feature Engineering

The system must generate appropriate temporal features including:

### Calendar

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

### Cyclical

```text
sin_hour
cos_hour
sin_day
cos_day
sin_month
cos_month
```

### Historical

```text
Lag features
Rolling mean
Rolling standard deviation
```

Feature generation must not use future observations.

---

## FR-05 — Model Training

The system must support:

* Naive forecasting
* Moving Average
* Linear Regression
* Random Forest
* XGBoost

Models must be trained using chronological data.

---

## FR-06 — Model Selection

The system must compare model performance using validation data.

The default selection criterion is:

```text
Lowest Validation RMSE
```

The winning model must be selected dynamically.

No model may be permanently hardcoded as the winner.

---

## FR-07 — Model Evaluation

The system must calculate:

```text
MAE
MSE
RMSE
MAPE
R²
```

Final test evaluation must be performed on data that was not used for model selection.

---

## FR-08 — Forecast Generation

The system must allow users to generate forecasts using:

```text
7 periods
14 periods
30 periods
60 periods
90 periods
```

Forecast results must include:

* Timestamp
* Predicted consumption
* Confidence interval when available

---

## FR-09 — Analytics

The system must provide:

* Current consumption
* Average consumption
* Peak consumption
* Hourly patterns
* Day-of-week patterns
* Weekly trends
* Monthly trends
* Rule-based insights

---

## FR-10 — Anomaly Detection

The system must support:

```text
Rolling Z-Score
IQR
Isolation Forest
```

Users must be able to visualize detected anomalies.

---

## FR-11 — Forecast History

The system must store previous forecasting runs.

Stored information may include:

* Run ID
* Timestamp
* Forecast frequency
* Forecast horizon
* Selected model
* Forecast results
* Model metadata

---

## FR-12 — REST API

The system must provide API endpoints for:

```text
Dashboard
Forecasting
Forecast Downloads
Analytics
Anomalies
Model Metadata
Forecast History
Dataset Upload
```

---

# 9. Non-Functional Requirements

## Performance

The application should:

* Load dashboards efficiently.
* Avoid retraining models during application startup.
* Reuse saved trained models.
* Process supported datasets within reasonable local-development time.

## Reliability

The system should:

* Handle malformed uploads safely.
* Return controlled API errors.
* Avoid exposing internal stack traces.
* Continue operating when optional confidence information is unavailable.

## Security

The system should:

* Protect form submissions with CSRF.
* Validate uploaded files.
* Enforce upload limits.
* Prevent directory traversal.
* Keep secrets outside source code.
* Avoid executing uploaded content.

## Maintainability

The codebase should be organized into:

```text
Application
Machine Learning
Data
Models
Tests
```

Each major responsibility should remain modular.

---

# 10. System Architecture

```text
                  ┌──────────────────────┐
                  │      User / Client   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Flask Dashboard   │
                  │   + REST API Layer   │
                  └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌──────────────┐
       │ Analytics  │ │ Forecasting│ │   Anomaly    │
       │  Service   │ │  Service   │ │   Detection  │
       └──────┬─────┘ └──────┬─────┘ └──────────────┘
              │              │
              └───────┬──────┘
                      ▼
              ┌───────────────┐
              │ Saved ML Model│
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Data Pipeline │
              │ Clean / Resample
              │ / Features    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Energy Dataset│
              └───────────────┘

                      │
                      ▼
              ┌───────────────┐
              │ SQLite History│
              └───────────────┘
```

---

# 11. Technology Requirements

| Layer                | Technology                    |
| -------------------- | ----------------------------- |
| Programming Language | Python                        |
| Web Framework        | Flask                         |
| Data Processing      | Pandas, NumPy                 |
| Machine Learning     | Scikit-learn                  |
| Gradient Boosting    | XGBoost                       |
| Visualization        | Plotly                        |
| Database             | SQLite                        |
| Templates            | Jinja2                        |
| Frontend             | HTML, CSS, Vanilla JavaScript |
| Testing              | Pytest                        |

---

# 12. Dashboard Requirements

The dashboard must contain:

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

The interface should provide:

* Responsive layouts
* Interactive charts
* Clear metric cards
* Tables for detailed results
* User-friendly error messages
* Download functionality

---

# 13. API Requirements

| Endpoint                 | Method | Purpose                 |
| ------------------------ | ------ | ----------------------- |
| `/api/dashboard`         | GET    | Dashboard statistics    |
| `/api/forecast`          | POST   | Generate forecast       |
| `/api/forecast/download` | GET    | Download forecast       |
| `/api/analytics`         | GET    | Energy analytics        |
| `/api/anomalies`         | GET    | Detect anomalies        |
| `/api/history`           | GET    | Forecast history        |
| `/api/history/<id>`      | GET    | Individual forecast run |
| `/api/model`             | GET    | Model metadata          |
| `/api/upload`            | POST   | Dataset upload          |

---

# 14. Data Requirements

### Required Dataset Characteristics

The dataset should contain:

* A timestamp column
* At least one electricity-consumption measurement
* Sufficient chronological observations
* Valid numeric consumption values

The reference dataset is:

**UCI Individual Household Electric Power Consumption**

---

# 15. Security Requirements

The application must:

* Validate uploads server-side.
* Restrict upload sizes.
* Sanitize filenames.
* Prevent path traversal.
* Protect form endpoints with CSRF.
* Store secrets in environment variables.
* Avoid exposing stack traces.
* Avoid executing uploaded files.
* Use parameterized database queries.

---

# 16. Testing Requirements

The project should include automated tests for:

* Dataset loading
* Data validation
* Feature generation
* Leakage prevention
* Model training
* Model evaluation
* Forecast generation
* Anomaly detection
* API endpoints
* File validation

Test command:

```bash
pytest -v
```

---

# 17. Acceptance Criteria

The project is considered complete when:

* [x] Dataset can be loaded successfully.
* [x] Data cleaning works correctly.
* [x] Missing values are handled.
* [x] Data is resampled correctly.
* [x] Temporal features are generated.
* [x] No future leakage occurs.
* [x] Five forecasting approaches can be compared.
* [x] Best model is selected automatically.
* [x] Forecasts can be generated.
* [x] Forecasts can be downloaded.
* [x] Analytics are displayed.
* [x] Anomalies can be detected.
* [x] Forecast history is stored.
* [x] Model performance can be reviewed.
* [x] CSV uploads are validated.
* [x] REST APIs are available.
* [x] Basic security controls are implemented.
* [x] Automated tests are available.
* [x] Application runs through Flask without retraining on startup.

---

# 18. Future Roadmap

### Phase 2

* LSTM
* GRU
* Transformer models
* SARIMA
* Prophet
* Exponential Smoothing

### Phase 3

* Weather-aware forecasting
* Temperature integration
* Solar-generation forecasting
* Multi-household forecasting

### Phase 4

* Real-time IoT ingestion
* Automated retraining
* Model drift detection
* Scheduled forecasting

### Phase 5

* User authentication
* Multi-user workspaces
* PostgreSQL
* Cloud deployment
* Production monitoring

---

# 19. Success Metrics

Project success can be measured through:

### Model Quality

* Validation RMSE
* Test RMSE
* MAE
* R²

### Application Quality

* Successful forecast generation
* Successful CSV validation
* API reliability
* Test coverage
* Error-handling reliability

### User Experience

* Easy dataset upload
* Clear forecasting workflow
* Understandable visualizations
* Accessible model comparison

---

# 20. Project Constraints

The initial release is intended for:

* Local development
* Demonstration
* Education
* Portfolio presentation
* Experimental forecasting

It is not intended to control physical infrastructure or make critical grid-management decisions.

---

# 21. Final Product Definition

The completed product is an end-to-end machine-learning application that transforms historical electricity-consumption data into:

```text
Clean Data
     ↓
Engineered Features
     ↓
Forecasting Models
     ↓
Model Comparison
     ↓
Best Model
     ↓
Future Forecast
     ↓
Analytics + Anomalies
     ↓
Interactive Dashboard + API
```

The project demonstrates the complete lifecycle of a practical machine-learning application—from raw data ingestion to model deployment and user-facing analytics.
