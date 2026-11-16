# 01_data_prep/02_daily_aggregation.py
import pandas as pd
import numpy as np
import os
from itertools import product

print("=== STEP 1: LOAD BASE TRUTH ===")
# excel_path = os.path.join('data', 'base_ev_dataset.csv')
df = pd.read_csv('data/base_ev_dataset.csv')
df['date'] = pd.to_datetime(df['date'])

print("=== STEP 2: DAILY AGGREGATION PER STATION ===")
daily_agg = df.groupby(['date', 'station_id', 'station_region']).agg(
    total_energy_kwh=('energy_kwh', 'sum'),
    total_sessions=('session_id', 'count'),
    total_revenue=('total_cost', 'sum'),
    avg_price=('price_per_kwh', 'mean')
).reset_index()

print("=== STEP 3: GET STATION CAPACITY ===")
station_capacity = df.groupby('station_id').agg(
    max_capacity_kw=('max_power_kW', lambda x: x.max() * df.loc[x.index, 'n_chargers'].iloc[0])
).reset_index()

print("=== STEP 4: CREATE GAP-FREE CALENDAR GRID ===")
all_dates = pd.date_range(start=daily_agg['date'].min(), end=daily_agg['date'].max(), freq='D')
all_stations = daily_agg['station_id'].unique()

full_grid = pd.DataFrame(list(product(all_dates, all_stations)), columns=['date', 'station_id'])
daily_demand = full_grid.merge(daily_agg, on=['date', 'station_id'], how='left')

daily_demand['total_energy_kwh'] = daily_demand['total_energy_kwh'].fillna(0)
daily_demand['total_sessions'] = daily_demand['total_sessions'].fillna(0)
daily_demand['total_revenue'] = daily_demand['total_revenue'].fillna(0)

daily_demand['station_region'] = daily_demand.groupby('station_id')['station_region'].ffill().bfill()
daily_demand['avg_price'] = daily_demand.groupby('station_id')['avg_price'].ffill().bfill()

daily_demand = daily_demand.merge(station_capacity, on='station_id', how='left')
daily_demand['utilisation_rate'] = (daily_demand['total_energy_kwh'] / (daily_demand['max_capacity_kw'] * 24)).clip(upper=1.0)

os.makedirs('data', exist_ok=True)
daily_demand.to_csv('data/daily_demand.csv', index=False)
print(f"✅ Gap-free station daily demand grid saved! Shape: {daily_demand.shape}")