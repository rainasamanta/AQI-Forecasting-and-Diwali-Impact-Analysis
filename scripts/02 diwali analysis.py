# DIWALI EVENT ANALYSIS

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("data/aqi_master_clean.csv")

df['Date'] = pd.to_datetime(
    df['Date'],
    dayfirst=True
)

diwali_windows = {
    2019: ('2019-10-25', '2019-10-29'),
    2020: ('2020-11-12', '2020-11-16'),
    2021: ('2021-11-02', '2021-11-06'),
    2022: ('2022-10-22', '2022-10-26'),
    2023: ('2023-11-10', '2023-11-14'),
    2024: ('2024-10-29', '2024-11-02')
}


# Summary Table
summary_rows = []
event_rows = []

for year, (start, end) in diwali_windows.items():

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    pre_start = start - pd.Timedelta(days=7)
    pre_end = start - pd.Timedelta(days=1)

    post_start = end + pd.Timedelta(days=1)
    post_end = end + pd.Timedelta(days=7)

    for city in df['City'].unique():

        city_df = df[df['City'] == city]

        pre = city_df[
            (city_df['Date'] >= pre_start) &
            (city_df['Date'] <= pre_end)
        ]

        festival = city_df[
            (city_df['Date'] >= start) &
            (city_df['Date'] <= end)
        ]

        post = city_df[
            (city_df['Date'] >= post_start) &
            (city_df['Date'] <= post_end)
        ]

        summary_rows.append({
            'City': city,
            'Year': year,
            'Pre_Mean': pre['AQI'].mean(),
            'Festival_Mean': festival['AQI'].mean(),
            'Post_Mean': post['AQI'].mean()
        })
        
summary_df = pd.DataFrame(summary_rows)
print(summary_df)

# Event Window Plot
for city in df['City'].unique():

    plt.figure(figsize=(10,6))

    for year, (start, end) in diwali_windows.items():

        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        window_start = start - pd.Timedelta(days=7)
        window_end = end + pd.Timedelta(days=7)
       
        temp = df[
            (df['City'] == city) &
            (df['Date'] >= window_start) &
            (df['Date'] <= window_end)
        ].copy()

        temp['Relative_Day'] = range(-9, 10)

        plt.plot(
            temp['Relative_Day'],
            temp['AQI'],
            marker='o',
            label=year
        )

    plt.axvspan(-2, 2, alpha=0.2)

    plt.title(f'Diwali Event Window - {city}')
    plt.xlabel('Relative Day')
    plt.ylabel('AQI')

    plt.legend()

    plt.show()
    
# Impact Score
summary_df['Impact_Score'] = (
    summary_df['Festival_Mean']
    -
    summary_df['Pre_Mean']
)

summary_df.to_csv(
    'diwali_summary.csv',
    index=False
)

# Mann-Whitney U Test for testing Oct-Nov avg AQI vs Diwali AQI
from scipy.stats import mannwhitneyu

results = []

for city in df['City'].unique():

    festival_values = []
    oct_nov_values = []

    city_df = df[df['City'] == city]

    for year, (start, end) in diwali_windows.items():

        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        year_df = city_df[city_df['Date'].dt.year == year]

        festival = year_df[
            (year_df['Date'] >= start) &
            (year_df['Date'] <= end)
        ]['AQI']

        oct_nov = year_df[
            year_df['Date'].dt.month.isin([10, 11])
        ]

        oct_nov = oct_nov[
            ~(
                (oct_nov['Date'] >= start) &
                (oct_nov['Date'] <= end)
            )
        ]['AQI']

        festival_values.extend(festival.tolist())
        oct_nov_values.extend(oct_nov.tolist())

    stat, p = mannwhitneyu(
        festival_values,
        oct_nov_values,
        alternative='greater'
    )

    results.append({
        'City': city,
        'Festival_Mean': np.mean(festival_values),
        'OctNov_Mean': np.mean(oct_nov_values),
        'U_Statistic': stat,
        'P_Value': p
    })

mannwhitney_results = pd.DataFrame(results)
print(mannwhitney_results)

mannwhitney_results.to_csv(
    'diwali_mannwhitney_results.csv',
    index=False
)