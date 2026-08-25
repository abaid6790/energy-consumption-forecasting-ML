"""
Generates a synthetic household electric power dataset that mimics the
structure and statistical behavior of the UCI "Individual Household
Electric Power Consumption" dataset (Hebrail & Berard, 2006).

This is NOT the real dataset. It exists so the project runs end-to-end
out of the box. Replace it with the real data by following data/README.md.

Output columns match the UCI file exactly:
Date;Time;Global_active_power;Global_reactive_power;Voltage;Global_intensity;
Sub_metering_1;Sub_metering_2;Sub_metering_3
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

START = datetime(2023, 1, 1, 0, 0, 0)
DAYS = 400  # ~13 months of minute-level data (kept smaller than the real
            # 47-month/2M-row UCI file so it trains quickly on any machine)
N_MINUTES = DAYS * 24 * 60

timestamps = [START + timedelta(minutes=i) for i in range(N_MINUTES)]

hours = np.array([t.hour + t.minute / 60 for t in timestamps])
day_of_year = np.array([t.timetuple().tm_yday for t in timestamps])
weekday = np.array([t.weekday() for t in timestamps])  # 0=Mon

# Base daily pattern: morning + evening peaks, low overnight
daily_pattern = (
    0.5
    + 0.9 * np.exp(-((hours - 8) ** 2) / (2 * 1.5 ** 2))
    + 1.4 * np.exp(-((hours - 19.5) ** 2) / (2 * 2.0 ** 2))
    + 0.3 * np.exp(-((hours - 13) ** 2) / (2 * 1.0 ** 2))
)

# Weekend bump (more daytime usage)
weekend_bump = np.where(weekday >= 5, 0.25, 0.0)

# Seasonal pattern: higher in winter (heating), lower in summer
seasonal = 0.6 * np.cos(2 * np.pi * (day_of_year - 15) / 365.25)

# Slow upward trend across the period (e.g. household growth)
trend = np.linspace(0, 0.15, N_MINUTES)

noise = np.random.normal(0, 0.12, N_MINUTES)

global_active_power = np.clip(
    daily_pattern + weekend_bump + seasonal + trend + noise, 0.05, None
)

# Inject a handful of anomalous spikes (e.g. appliance left running)
n_anomalies = 40
anomaly_idx = np.random.choice(N_MINUTES, n_anomalies, replace=False)
global_active_power[anomaly_idx] += np.random.uniform(3.5, 7.0, n_anomalies)

global_reactive_power = np.clip(
    0.1 * global_active_power + np.random.normal(0, 0.03, N_MINUTES), 0, None
)
voltage = np.random.normal(240, 2.5, N_MINUTES)
global_intensity = np.clip(
    (global_active_power * 1000) / 230 + np.random.normal(0, 0.5, N_MINUTES), 0, None
)

# Sub-metering (kitchen, laundry, water heater/AC) in watt-hours
sub_1 = np.clip(np.random.gamma(1.2, 2.0, N_MINUTES) * (daily_pattern > 1.0), 0, None)
sub_2 = np.clip(np.random.gamma(1.0, 1.5, N_MINUTES) * (daily_pattern > 0.8), 0, None)
sub_3 = np.clip(
    np.random.gamma(2.0, 4.0, N_MINUTES) * (0.4 + 0.6 * (seasonal > 0)), 0, None
)

# Inject missing values (~1.25%, matching the real dataset's documented rate)
missing_mask = np.random.rand(N_MINUTES) < 0.0125

df = pd.DataFrame(
    {
        "Date": [t.strftime("%d/%m/%Y") for t in timestamps],
        "Time": [t.strftime("%H:%M:%S") for t in timestamps],
        "Global_active_power": np.round(global_active_power, 3),
        "Global_reactive_power": np.round(global_reactive_power, 3),
        "Voltage": np.round(voltage, 2),
        "Global_intensity": np.round(global_intensity, 2),
        "Sub_metering_1": np.round(sub_1, 1),
        "Sub_metering_2": np.round(sub_2, 1),
        "Sub_metering_3": np.round(sub_3, 1),
    }
)

for col in df.columns[2:]:
    df[col] = df[col].astype(object)
    df.loc[missing_mask, col] = "?"

out_path = "household_power_consumption.csv"
df.to_csv(out_path, sep=";", index=False)
print(f"Wrote {len(df):,} rows to {out_path}")
