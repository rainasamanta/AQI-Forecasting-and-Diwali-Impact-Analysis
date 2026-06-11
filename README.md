# AQI Forecasting and Diwali Impact Analysis
### An end-to-end time series analysis of Air Quality Index (AQI) data across 4 Indian cities, featuring exploratory analysis, Diwali impact assessment, statistical testing, SARIMA forecasting, and an interactive Streamlit dashboard.

## Cities
Bengaluru | Delhi | Kolkata | Mumbai 

## Study Period
January 2019 – March 2025

## Objectives
- Explore AQI patterns across cities
- Analyze Diwali pollution impact
- Investigate seasonality and trends
- Build SARIMA forecasting models
- Evaluate forecasting performance

## Project Structure
- `scripts/` — Python analysis scripts (run in order 01 → 04)
- `data/` — cleaned data and result CSVs
- `plots/` — all visualisation outputs
- `streamlit_app/` — interactive dashboard
- `report/` — full project report (Word)

## Dashboard
Live app: [your streamlit URL here]

## Analysis Pipeline
1. Data cleaning and EDA
2. Diwali festival event study (Mann-Whitney U test)
3. Stationarity testing and SARIMA parameter estimation
4. SARIMA forecasting and residual diagnostics

## Key Findings
- Delhi and Mumbai show statistically significant Diwali-driven AQI elevation
- SARIMA achieves R²=0.895 for Delhi and R²=0.848 for Bengaluru
- Mumbai's coastal dynamics limit SARIMA forecast accuracy (R²=0.459)