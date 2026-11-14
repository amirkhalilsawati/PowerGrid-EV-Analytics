# PowerGrid-EV-Analytics
# Task 01: EV Charging Demand Forecasting

## Objective
Predict future hourly charging demand (kWh and session counts) using historical session patterns from 2022–2024 to optimize grid capacity, staffing, and energy procurement.

## Approach & Methodology
* **Primary Track (Innovator):** Meta Prophet with automated weekly/daily seasonality and UK holiday regressors, coupled with interactive Plotly visualisations.
* **Shadow Track (Statistician / ML):** SARIMA and XGBoost baseline incorporating lag features (`lag_1`, `lag_24`) and temporal encodings.

## Key Deliverables Included
* Cleaned time-series demand dataset.
* Forecasting models & evaluation metrics (RMSE, MAPE).
* Interactive forecast plot (`task_01_forecast_plot.html`).
* Side-by-side model performance comparison table.

## Model Comparison Summary
| Model | RMSE (kWh) | MAPE (%) | Training Complexity | Key Trade-off |
| :--- | :--- | :--- | :--- | :--- |
| **Meta Prophet (Innovator)** | *[Insert Value]* | *[Insert Value]* | Low / Fast | Handles seasonality natively; less sensitive to extreme spikes. |
| **XGBoost (Shadow ML)** | *[Insert Value]* | *[Insert Value]* | Medium | Captures non-linear feature interactions; requires careful lag engineering. |