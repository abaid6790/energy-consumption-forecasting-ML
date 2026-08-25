"""
Trains and compares forecasting models on the household energy dataset,
selects the best model by RMSE, and saves all artifacts to models/.

Usage:
    python ml/train.py
    python ml/train.py --data data/household_power_consumption.csv --frequency daily
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.dataset_loader import load_uci_household_power, validate_canonical
from ml.preprocessing import run_preprocessing_pipeline
from ml.feature_engineering import build_features
from ml.baselines import NaiveForecaster, MovingAverageForecaster
from ml.evaluate import compute_metrics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, "models")


def chronological_split(df: pd.DataFrame, train_frac=0.7, val_frac=0.15):
    n = len(df)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]


def evaluate_baseline(model, full_series: pd.Series, val_idx, test_idx):
    """Baselines predict using the true prior values (context), never future data."""
    val_preds = model.predict(full_series.loc[: val_idx[-1]]).take(
        [full_series.index.get_loc(i) for i in val_idx]
    )
    test_preds = model.predict(full_series.loc[: test_idx[-1]]).take(
        [full_series.index.get_loc(i) for i in test_idx]
    )
    return val_preds, test_preds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        default=os.path.join(ROOT, "data", "household_power_consumption.csv"),
    )
    parser.add_argument("--frequency", default="daily", choices=["hourly", "daily", "weekly", "monthly"])
    args = parser.parse_args()

    t0 = time.time()
    os.makedirs(MODELS_DIR, exist_ok=True)

    print(f"[1/9] Loading dataset from {args.data} ...")
    raw = load_uci_household_power(args.data)
    validate_canonical(raw)
    print(f"      Loaded {len(raw):,} raw rows.")

    print("[2/9] Running preprocessing pipeline (sort, dedupe, missing values, resample) ...")
    prep = run_preprocessing_pipeline(raw, frequency=args.frequency)
    clean = prep["data"]
    print(f"      Resampled to {len(clean):,} {args.frequency} observations. "
          f"Duplicates removed: {prep['duplicates_removed']}. "
          f"Gap periods: {prep['gap_report']['missing_periods']}.")

    print("[3/9] Engineering features (calendar, cyclical, lag, rolling) ...")
    featured, feature_cols = build_features(clean, frequency=args.frequency)
    print(f"      {len(feature_cols)} features across {len(featured)} usable rows.")

    print("[4/9] Creating chronological train/validation/test split (70/15/15) ...")
    train_df, val_df, test_df = chronological_split(featured)
    print(f"      Train={len(train_df)}  Val={len(val_df)}  Test={len(test_df)}")

    X_train, y_train = train_df[feature_cols], train_df["energy_consumption"]
    X_val, y_val = val_df[feature_cols], val_df["energy_consumption"]
    X_test, y_test = test_df[feature_cols], test_df["energy_consumption"]

    results = {}
    trained_models = {}

    print("[5/9] Training baseline models ...")
    full_clean_series = clean.set_index("timestamp")["energy_consumption"]
    train_ts = train_df["timestamp"]
    val_ts = val_df["timestamp"]
    test_ts = test_df["timestamp"]

    naive = NaiveForecaster().fit(full_clean_series.loc[:train_ts.iloc[-1]])
    val_preds = naive.predict(full_clean_series.loc[:val_ts.iloc[-1]]).take(
        [full_clean_series.index.get_loc(t) for t in val_ts]
    )
    test_preds = naive.predict(full_clean_series.loc[:test_ts.iloc[-1]]).take(
        [full_clean_series.index.get_loc(t) for t in test_ts]
    )
    results["Naive"] = {"val": compute_metrics(y_val, val_preds), "test": compute_metrics(y_test, test_preds)}

    ma = MovingAverageForecaster(window=7).fit(full_clean_series.loc[:train_ts.iloc[-1]])
    val_preds = ma.predict(full_clean_series.loc[:val_ts.iloc[-1]]).take(
        [full_clean_series.index.get_loc(t) for t in val_ts]
    )
    test_preds = ma.predict(full_clean_series.loc[:test_ts.iloc[-1]]).take(
        [full_clean_series.index.get_loc(t) for t in test_ts]
    )
    results["Moving Average"] = {"val": compute_metrics(y_val, val_preds), "test": compute_metrics(y_test, test_preds)}

    print("[6/9] Training machine learning models (Linear Regression, Random Forest, XGBoost) ...")

    lr = LinearRegression()
    lr.fit(X_train, y_train)
    results["Linear Regression"] = {
        "val": compute_metrics(y_val, lr.predict(X_val)),
        "test": compute_metrics(y_test, lr.predict(X_test)),
    }
    trained_models["Linear Regression"] = lr

    rf = RandomForestRegressor(
        n_estimators=300, max_depth=12, random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    results["Random Forest"] = {
        "val": compute_metrics(y_val, rf.predict(X_val)),
        "test": compute_metrics(y_test, rf.predict(X_test)),
    }
    trained_models["Random Forest"] = rf

    xgb = XGBRegressor(
        n_estimators=400,
        learning_rate=0.03,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric="rmse",
    )
    xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    results["XGBoost"] = {
        "val": compute_metrics(y_val, xgb.predict(X_val)),
        "test": compute_metrics(y_test, xgb.predict(X_test)),
    }
    trained_models["XGBoost"] = xgb

    print("[7/9] Comparing models on validation RMSE ...")
    comparison_rows = []
    for name, m in results.items():
        comparison_rows.append(
            {"Model": name, **{f"val_{k}": v for k, v in m["val"].items()}}
        )
    comp_df = pd.DataFrame(comparison_rows).sort_values("val_RMSE")
    print(comp_df.to_string(index=False))

    best_name = comp_df.iloc[0]["Model"]
    print(f"\n[8/9] Best model selected: {best_name} (lowest validation RMSE)")

    if best_name in trained_models:
        best_model = trained_models[best_name]
        joblib.dump(best_model, os.path.join(MODELS_DIR, "forecasting_model.pkl"))
    else:
        best_model = None
        print("      (Best model is a baseline; no sklearn model object to persist "
              "-- forecasting will fall back to Moving Average / Naive logic.)")

    joblib.dump(feature_cols, os.path.join(MODELS_DIR, "feature_columns.pkl"))

    # Save a tiny "preprocessing pipeline" descriptor (frequency + lag config)
    # so the Flask app knows how to reproduce features for new data.
    joblib.dump({"frequency": args.frequency}, os.path.join(MODELS_DIR, "preprocessing_pipeline.pkl"))

    print("[9/9] Saving model metadata and evaluation metrics ...")
    metadata = {
        "best_model": best_name,
        "frequency": args.frequency,
        "trained_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "n_train": len(train_df),
        "n_val": len(val_df),
        "n_test": len(test_df),
        "feature_columns": feature_cols,
        "metrics": results,
        "training_duration_sec": round(time.time() - t0, 2),
        "unit": "kW (kilowatts, mean over the resample period)",
    }
    with open(os.path.join(MODELS_DIR, "model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    # Save the cleaned historical series too -- the Flask app loads the model
    # rather than retraining, but it needs history to build lag/rolling
    # features for future forecasts.
    clean.to_csv(os.path.join(MODELS_DIR, "history.csv"), index=False)

    print(f"\nDone in {time.time() - t0:.1f}s. Artifacts saved to {MODELS_DIR}/")


if __name__ == "__main__":
    main()
