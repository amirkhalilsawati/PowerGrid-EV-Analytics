import os
import numpy as np
import pandas as pd

os.makedirs("data", exist_ok=True)

print("=== STEP 1: LOAD & DEDUPLICATE ===")
# excel_path = "ev_charging_dataset.xlsx"
excel_path = os.path.join('data', 'ev_charging_dataset.xlsx')
stations = pd.read_excel(excel_path, sheet_name=0).drop_duplicates(subset=["station_id"], keep="first")
chargers = pd.read_excel(excel_path, sheet_name=1).drop_duplicates(subset=["charger_id"], keep="first")
sessions = pd.read_excel(excel_path, sheet_name=2).drop_duplicates(subset=["session_id"], keep="first")

# Safe median imputation (compatible with Pandas 2.x / 3.x)
for col in ["energy_kwh", "session_duration_minutes", "price_per_kwh", "total_cost"]:
    nulls = sessions[col].isna().sum()
    if nulls > 0:
        sessions[col] = sessions[col].fillna(sessions[col].median())
        print(f"Imputed {nulls} nulls in {col}")

print("\n=== STEP 2: STAR-SCHEMA MERGE ===")
df = sessions.merge(
    chargers[["charger_id", "max_power_kW", "installation_date"]],
    on="charger_id",
    how="left"
).merge(
    stations[["station_id", "station_name", "activation_year", "n_chargers"]],
    on="station_id",
    how="left"
)

print(f"Unmatched chargers: {df['max_power_kW'].isna().sum()} | Unmatched stations: {df['activation_year'].isna().sum()}")

print("\n=== STEP 3: TEMPORAL & PHYSICS FEATURES ===")
df["start_timestamp"] = pd.to_datetime(df["start_timestamp"])
df["end_timestamp"] = pd.to_datetime(df["end_timestamp"])
df["installation_date"] = pd.to_datetime(df["installation_date"])

df["date"] = df["start_timestamp"].dt.date
df["hour_of_day"] = df["start_timestamp"].dt.hour
df["day_of_week"] = df["start_timestamp"].dt.dayofweek
df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
df["month"] = df["start_timestamp"].dt.month
df["year"] = df["start_timestamp"].dt.year

# Useful for Task 05 (Maintenance) & data-audit flags (negative = pre-installation synthetic record)
df["charger_age_days"] = (df["start_timestamp"] - df["installation_date"]).dt.days

# Physics & billing audit features
df["actual_charge_rate_kw"] = df["energy_kwh"] / (df["session_duration_minutes"].replace(0, np.nan) / 60.0)
df["power_efficiency_raw"] = df["actual_charge_rate_kw"] / df["max_power_kW"]
df["power_efficiency_clipped"] = df["power_efficiency_raw"].clip(upper=1.0)
df["cost_check_diff"] = (df["total_cost"] - (df["energy_kwh"] * df["price_per_kwh"])).abs()

# to see exactly where rows or columns are shifting
print("Shape of raw sessions:", sessions.shape)
print("Shape of raw chargers:", chargers.shape)
print("Shape of raw stations:", stations.shape)
print("Shape after merges:", df.shape)
print("Columns present:", df.columns.tolist())


print("\n=== STEP 4: EXPORT BASE TRUTH ===")
df.to_csv("data/base_ev_dataset.csv", index=False)
print(f"Saved data/base_ev_dataset.csv | Shape: {df.shape}")