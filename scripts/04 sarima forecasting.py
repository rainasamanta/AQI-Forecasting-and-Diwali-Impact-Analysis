# FORECASTING

import pandas as pd

df = pd.read_csv("data/aqi_master_clean.csv")

df['Date'] = pd.to_datetime(
    df['Date'],
    dayfirst=True
)
df = df.sort_values(['City', 'Date'])

monthly_df = (
    df.groupby(
        ['City', pd.Grouper(key='Date', freq='MS')]
    )['AQI']
    .mean()
    .reset_index()
)

# SARIMA Forecasting
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.statespace.sarimax import SARIMAX

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

results = []

best_models = {
    'Bengaluru': ((1,0,1),(1,0,1,12)),
    'Delhi': ((1,1,1),(1,1,0,12)),
    'Kolkata': ((1,1,1),(1,0,1,12)),
    'Mumbai': ((0,1,1),(1,0,1,12))
}

for city in best_models.keys():

    city_df = (
        monthly_df[monthly_df['City'] == city]
        .sort_values('Date')
        .set_index('Date')
    )

    series = city_df['AQI']

    train = series[:'2023-12-31']

    test = series['2024-01-01':]

    order, seasonal_order = best_models[city]

    model = SARIMAX(
        train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    fitted = model.fit(disp=False)

    forecast = fitted.get_forecast(
        steps=len(test)
    )

    pred = forecast.predicted_mean

    conf_int = forecast.conf_int()

    mae = mean_absolute_error(
        test,
        pred
    )

    rmse = np.sqrt(
        mean_squared_error(
            test,
            pred
        )
    )

    mape = np.mean(
        np.abs(
            (test - pred) / test
        )
    ) * 100

    r2 = r2_score(
        test,
        pred
    )

    results.append([
        city,
        round(mae,2),
        round(rmse,2),
        round(mape,2),
        round(r2,4)
    ])
    
    plt.figure(figsize=(12,6))

    plt.plot(
        train.index,
        train,
        label='Train'
    )

    plt.plot(
        test.index,
        test,
        label='Actual'
    )

    plt.plot(
        pred.index,
        pred,
        label='Forecast'
    )

    plt.fill_between(
        conf_int.index,
        conf_int.iloc[:,0],
        conf_int.iloc[:,1],
        alpha=0.3
    )

    plt.title(
        f'SARIMA Forecast - {city}'
    )

    plt.xlabel('Date')

    plt.ylabel('AQI')

    plt.legend()

    plt.show()
    
results_df = pd.DataFrame(
    results,
    columns=[
        'City',
        'MAE',
        'RMSE',
        'MAPE',
        'R2'
    ]
)

print(results_df)

results_df.to_csv(
    'sarima_forecast_metrics.csv',
    index=False
)


# Residual Analysis
from statsmodels.stats.diagnostic import acorr_ljungbox

print("\nLJUNG-BOX TEST RESULTS\n")

for city, (order, seasonal_order) in best_models.items():

    train = (
        monthly_df[monthly_df['City'] == city]
        .sort_values('Date')
        .set_index('Date')['AQI']
        [:'2023-12-31']
    )
    
    fitted = SARIMAX(
        train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    ).fit(disp=False)

    residuals = fitted.resid

    plt.figure(figsize=(12,4))
    plt.plot(residuals)
    plt.axhline(y=0, linestyle='--')
    plt.title(f'Residual Time Plot - {city}')
    plt.show()

    p_value = acorr_ljungbox(
        residuals.dropna(),
        lags=[12],
        return_df=True
    )['lb_pvalue'].iloc[0]

    print(city)
    print("p-value:", round(p_value,4))

    if p_value > 0.05:
        print("Residuals are white noise")
    else:
        print("Residual autocorrelation remains")

    print()
    