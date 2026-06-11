# STATIONARITY CHECKING and PARAMETER ESTIMATION 

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

# STL Decomposition
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import adfuller, kpss

for city in monthly_df['City'].unique():

    city_series = (
        monthly_df[monthly_df['City'] == city]
        .set_index('Date')
        ['AQI']
    )

    stl = STL(
        city_series,
        period=12,
        robust=True
    )

    result = stl.fit()

    fig = result.plot()

    fig.set_size_inches(10, 8)

    plt.suptitle(
        f'STL Decomposition - {city}',
        y=1.02
    )

    plt.show()

# ADF Test
print("ADF TEST RESULTS")

for city in monthly_df['City'].unique():

    city_series = (
        monthly_df[monthly_df['City'] == city]
        ['AQI']
    )

    result = adfuller(city_series)

    print(city)

    print(
        "ADF Statistic:",
        round(result[0], 4)
    )

    print(
        "p-value:",
        round(result[1], 4)
    )

    if result[1] < 0.05:
        print("Stationary")
    else:
        print("Non-Stationary")

    print()


# KPSS Test
print("KPSS TEST RESULTS")

for city in monthly_df['City'].unique():

    city_series = (
        monthly_df[monthly_df['City'] == city]
        ['AQI']
    )

    result = kpss(
        city_series,
        regression='c'
    )

    print(city)

    print(
        "KPSS Statistic:",
        round(result[0], 4)
    )

    print(
        "p-value:",
        round(result[1], 4)
    )

    if result[1] < 0.05:
        print("Non-Stationary")
    else:
        print("Stationary")

    print()
    

# ADF on Differenced Series
print("ADF TEST RESULTS on Differenced Series")

for city in ['Delhi','Kolkata','Mumbai']:

    city_series = (
        monthly_df[monthly_df['City']==city]
        .sort_values('Date')
        ['AQI']
    )

    diff_series = city_series.diff().dropna()

    result = adfuller(diff_series)

    print(city)

    print("ADF Statistic:", round(result[0],4))
    print("p-value:", round(result[1],4))

    if result[1] < 0.05:
        print("Stationary")

    else:
        print("Non-Stationary")

    print()
    
# KPSS on Differenced Series
print("KPSS TEST RESULTS on Differenced Series")

for city in ['Delhi','Kolkata','Mumbai']:

    city_series = (
        monthly_df[monthly_df['City']==city]
        .sort_values('Date')
        ['AQI']
    )

    diff_series = city_series.diff().dropna()

    result = kpss(
        diff_series,
        regression='c'
    )

    print(city)

    print("KPSS Statistic:", round(result[0],4))
    print("p-value:", round(result[1],4))

    if result[1] > 0.05:
        print("Stationary")

    else:
        print("Non-Stationary")

    print()

    
# ACF and PACF Plots
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt

for city in monthly_df['City'].unique():

    city_series = (
        monthly_df[monthly_df['City'] == city]
        .sort_values('Date')
        ['AQI']
    )

    if city == 'Bengaluru':
        series_used = city_series

    else:
        series_used = city_series.diff().dropna()

    plt.figure(figsize=(10,4))

    plot_acf(
        series_used,
        lags=24
    )

    plt.title(
        f'ACF - {city}'
    )

    plt.show()

    plt.figure(figsize=(10,4))

    plot_pacf(
        series_used,
        lags=24,
        method='ywm'
    )

    plt.title(
        f'PACF - {city}'
    )

    plt.show()
    
# OCSB test and Canova-Hansen test
print("OCSB test and Canova-Hansen test")
from pmdarima.arima.utils import nsdiffs

for city in monthly_df['City'].unique():
    series = (
        monthly_df[monthly_df['City'] == city]
        .sort_values('Date')
        .set_index('Date')['AQI']
    )
    
    D_ocsb = nsdiffs(series, m=12, test='ocsb')
    D_ch = nsdiffs(series, m=12, test='ch')
    
    print(f"{city} — OCSB: D={D_ocsb}, CH: D={D_ch}")
    
# Grid Search AIC

from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings("ignore")

best_models = []

cities = ['Bengaluru', 'Delhi', 'Kolkata', 'Mumbai']

for city in cities:

    city_series = (
        monthly_df[monthly_df['City'] == city]
        .sort_values('Date')
        .set_index('Date')['AQI']
    )

    train = city_series[:'2023-12-31']

    if city == 'Bengaluru':
        d = 0
        D = 0
        
    elif city == 'Delhi':
        d = 1
        D = 1
              
    else:
        d = 1
        D = 0
      
    city_results = []
    
    for p in [0, 1]:
        for q in [0, 1]:
            for P in [0, 1]:
                for Q in [0, 1]:
                                                            
                        try:

                            model = SARIMAX(
                            train,
                            order=(p, d, q),
                            seasonal_order=(P, D, Q, 12),
                            enforce_stationarity=False,
                            enforce_invertibility=False
                        )

                            fitted = model.fit(disp=False)

                            city_results.append([
                            p,
                            d,
                            q,
                            P,
                            D,
                            Q,
                            fitted.aic
                        ])

                        except:
                            pass

    city_results = pd.DataFrame(
        city_results,
        columns=[
            'p',
            'd',
            'q',
            'P',
            'D',
            'Q',
            'AIC'
        ]
    )

    city_results = city_results.sort_values('AIC')
    
    print(f"\n{'='*50}")
    print(f"TOP 5 MODELS FOR {city}")
    print(f"{'='*50}")

    print(
    city_results.head(5)
    .reset_index(drop=True)
)

    print()

    best = city_results.iloc[0]

    best_models.append([
        city,
        int(best['p']),
        int(best['d']),
        int(best['q']),
        int(best['P']),
        int(best['D']),
        int(best['Q']),
        round(best['AIC'], 2)
    ])

best_models_df = pd.DataFrame(
    best_models,
    columns=[
        'City',
        'p',
        'd',
        'q',
        'P',
        'D',
        'Q',
        'AIC'
    ]
)

print(best_models_df)

best_models_df.to_csv(
    'best_sarima_models.csv',
    index=False
)
