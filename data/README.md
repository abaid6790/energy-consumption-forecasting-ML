# Dataset

## Source

**Individual Household Electric Power Consumption** (Hebrail & Berard, 2006)

- UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
- Kaggle mirror: https://www.kaggle.com/datasets/uciml/electric-power-consumption-data-set

Minute-level electric power measurements for a single household near Paris,
France, collected between December 2006 and November 2010 (~2.07 million
rows). Licensed CC BY 4.0.

## Structure

The raw file is semicolon-delimited with these columns:

| Column                  | Description                                               |
|--------------------------|-------------------------------------------------------------|
| `Date`                   | `dd/mm/yyyy`                                                 |
| `Time`                   | `hh:mm:ss`                                                   |
| `Global_active_power`    | Household global active power, **kilowatts (kW)** — this is the forecasting target |
| `Global_reactive_power`  | Household global reactive power, kW                         |
| `Voltage`                | Minute-averaged voltage, volts                               |
| `Global_intensity`       | Minute-averaged current intensity, amperes                   |
| `Sub_metering_1`         | Kitchen (watt-hours of active energy)                        |
| `Sub_metering_2`         | Laundry room (watt-hours of active energy)                   |
| `Sub_metering_3`         | Water heater / air conditioner (watt-hours of active energy) |

Missing values are marked `?` (~1.25% of rows).

## Required columns for this application

Internally, everything downstream of `ml/dataset_loader.py` works with a
canonical two-column frame:

```
timestamp             datetime
energy_consumption    float (kW)
```

`Global_active_power` is used as `energy_consumption`. All units are
documented and never silently mixed — if you bring your own dataset with
different units, note that in this file and be consistent.

## How to download the real dataset

1. Download `household_power_consumption.zip` from the UCI or Kaggle link above.
2. Unzip it and place `household_power_consumption.txt` in this `data/` folder.
3. Rename it (or pass `--data`) so it matches what `ml/train.py` expects:

   ```bash
   mv data/household_power_consumption.txt data/household_power_consumption.csv
   python ml/train.py --data data/household_power_consumption.csv --frequency daily
   ```

   The loader (`ml.dataset_loader.load_uci_household_power`) reads it as
   semicolon-delimited regardless of the `.csv` extension, matching the
   original UCI format.

Do **not** commit the raw file to Git — `data/*` is already excluded via
`.gitignore` (this README and the generator script are kept).

## Sample data for immediate testing

Since the full ~2M-row file is large, this repo ships with
`generate_sample_data.py`, which produces a smaller synthetic dataset with
the **identical schema** (same columns, same delimiter, same missing-value
marker) so the whole pipeline can be exercised immediately:

```bash
python data/generate_sample_data.py
```

This writes `data/household_power_consumption.csv`. It is synthetic —
useful for verifying the pipeline works end-to-end, but replace it with the
real UCI/Kaggle file before drawing any real conclusions from the
dashboard's numbers.

## Bringing your own CSV

The `/upload` page and `ml.dataset_loader.load_generic_csv` accept any CSV
with at minimum:

```
timestamp,energy_consumption
2024-01-01,4.82
2024-01-02,5.13
```

Additional columns are ignored for forecasting purposes but won't cause an
error.
