import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings("ignore")

# Load data
df = pd.read_csv("data/aqi_master_clean.csv")
df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True)
df = df.sort_values(['City', 'Date'])

metrics_df = pd.read_csv("data/sarima_forecast_metrics.csv")

# Monthly aggregation
monthly_df = (
    df.groupby(
        ['City', pd.Grouper(key='Date', freq='MS')]
    )['AQI']
    .mean()
    .reset_index()
)

# Best models
best_models = {
    'Bengaluru': ((1,0,1),(1,0,1,12)),
    'Delhi':     ((1,1,1),(1,1,0,12)),
    'Kolkata':   ((1,1,1),(1,0,1,12)),
    'Mumbai':    ((0,1,1),(1,0,1,12))
}

# City limitations
limitations = {
    'Kolkata': (
        "Kolkata's model shows borderline residual autocorrelation (Ljung-Box p=0.044), "
        "suggesting mild model misspecification. Point forecasts are reasonable but "
        "confidence intervals may be slightly underestimated."
    ),
    'Mumbai': (
        "Mumbai is the only coastal city in this dataset. Its AQI is influenced by "
        "sea breezes, monsoon patterns, and marine air intrusion - mechanisms that "
        "create irregular, non-seasonal dynamics that SARIMA cannot fully capture. "
        "This explains the higher forecast error and borderline residual autocorrelation (p=0.049)."
    )
}

st.title("SARIMA Forecast")
st.markdown("How well does the model predict 2024-25 air quality for each city?")

st.divider()

# City selector
cities = sorted(best_models.keys())
selected_city = st.selectbox("Select a City", cities)

# Get series
city_series = (
    monthly_df[monthly_df['City'] == selected_city]
    .sort_values('Date')
    .set_index('Date')['AQI']
)

train = city_series[:'2023-12-31']
test = city_series['2024-01-01':]

# Fit model
order, seasonal_order = best_models[selected_city]

model = SARIMAX(
    train,
    order=order,
    seasonal_order=seasonal_order,
    enforce_stationarity=False,
    enforce_invertibility=False
)

with st.spinner("Fitting SARIMA model..."):
    fitted = model.fit(disp=False)

forecast = fitted.get_forecast(steps=len(test))
pred = forecast.predicted_mean
conf_int = forecast.conf_int()

st.divider()

# Forecast plot
st.subheader(f"{selected_city} - Forecast vs Actual")
st.caption(
    "The model is trained on 2019–2023 data. "
    "The shaded region shows the 95% confidence interval for the forecast."
)

fig = go.Figure()

# Training data
fig.add_trace(go.Scatter(
    x=train.index,
    y=train.values,
    name="Training Data",
    line=dict(color="#4C9BE8", width=1.5)
))

# Actual 2024
fig.add_trace(go.Scatter(
    x=test.index,
    y=test.values,
    name="Actual",
    line=dict(color="#00B050", width=2)
))

# Forecast
fig.add_trace(go.Scatter(
    x=pred.index,
    y=pred.values,
    name="Forecast",
    line=dict(color="#E8524C", width=2, dash="dash")
))

# Confidence interval
fig.add_trace(go.Scatter(
    x=list(conf_int.index) + list(conf_int.index[::-1]),
    y=list(conf_int.iloc[:, 0]) + list(conf_int.iloc[:, 1][::-1]),
    fill="toself",
    fillcolor="rgba(232, 82, 76, 0.15)",
    line=dict(color="rgba(255,255,255,0)"),
    name="95% Confidence Interval",
    showlegend=True
))

# Vertical line separating train and test
fig.add_vline(
    x=pd.Timestamp("2024-01-01").timestamp() * 1000,
    line_dash="dot",
    line_color="gray",
    annotation_text="Forecast start",
    annotation_position="top right"
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Monthly Mean AQI",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Metrics
st.subheader("Forecast Accuracy Metrics")

city_metrics = metrics_df[
    metrics_df['City'] == selected_city
].iloc[0]

mae  = city_metrics['MAE']
mape = city_metrics['MAPE']
r2   = city_metrics['R2']
rmse = city_metrics['RMSE']

m1, m2, m3, m4 = st.columns(4)
m1.metric("MAE", f"{mae}")
m2.metric("RMSE", f"{rmse}")
m3.metric("MAPE", f"{mape}%")
m4.metric("R²", f"{r2}")

st.divider()

# Plain English interpretation
st.subheader("What do these numbers mean?")

if r2 >= 0.85:
    quality = "strong"
    quality_color = "success"
elif r2 >= 0.70:
    quality = "moderate"
    quality_color = "warning"
else:
    quality = "weak"
    quality_color = "error"

interpretation = f"""
- The model predicted monthly AQI within **{mae} AQI units** on average (MAE)
- On a percentage basis, predictions were off by **{mape}%** on average (MAPE)
- The model explains **{round(r2*100, 1)}%** of the variation in {selected_city}'s 2024-25 AQI (R²)
- Overall forecast quality: **{quality.upper()}**
"""

if quality_color == "success":
    st.success(interpretation)
elif quality_color == "warning":
    st.warning(interpretation)
else:
    st.error(interpretation)

# Limitation note for Kolkata and Mumbai
if selected_city in limitations:
    st.divider()
    st.subheader("Model Limitation")
    st.info(limitations[selected_city])

st.divider()

# Model specification
st.subheader("Model Specification")
st.caption("The SARIMA model parameters selected via AIC grid search.")

p, d, q = order
P, D, Q, s = seasonal_order

spec_col1, spec_col2 = st.columns(2)

with spec_col1:
    st.markdown(f"""
    **Non-seasonal component**
    - p (AR order): **{p}**
    - d (differencing): **{d}**
    - q (MA order): **{q}**
    """)

with spec_col2:
    st.markdown(f"""
    **Seasonal component** (period = {s} months)
    - P (seasonal AR): **{P}**
    - D (seasonal differencing): **{D}**
    - Q (seasonal MA): **{Q}**
    """)
