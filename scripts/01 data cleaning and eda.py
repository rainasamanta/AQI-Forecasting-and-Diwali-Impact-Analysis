# DATA CLEANING & INITIAL DATA AUDIT

import pandas as pd

df = pd.read_csv("data/aqi_master_updated.csv")

# View first few rows
print(df.head())
# Check dimensions
print(df.shape)
# View column names
print(df.columns)
# Check data types and missing values
print(df.info())

# Convert Date column to datetime format
df['Date'] = pd.to_datetime(
    df['Date'],
    dayfirst=True
)

# Create columns for month and year
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year

# Find earliest and latest dates
print(df['Date'].min())
print(df['Date'].max())

# List all cities
print(df['City'].nunique())
print(df['City'].unique())

# Missing values per column
missing = df.isnull().sum()
print(missing)

# Count duplicate rows
duplicates = df.duplicated().sum()
print(duplicates)

# Remove duplicates if present
if duplicates > 0:
    df = df.drop_duplicates()

def compute_bucket(aqi):
    if aqi <= 50:    return 'Good'
    elif aqi <= 100: return 'Satisfactory'
    elif aqi <= 200: return 'Moderate'
    elif aqi <= 300: return 'Poor'
    elif aqi <= 400: return 'Very Poor'
    else:            return 'Severe'
 
df['AQI_Bucket'] = df['AQI'].apply(compute_bucket)

# SAVE CLEANED DATASET
df.to_csv(
    "aqi_master_clean.csv",
    index=False
)


# EXPLORATORY DATA ANALYSIS

# Summary statistics for each city's AQI values
summary_stats = df.groupby('City')['AQI'].describe()
print(summary_stats)

summary_stats.to_csv(
    'summary_stats.csv',
    index=True
)

import matplotlib.pyplot as plt
import seaborn as sns

# PLOT 1: Compare AQI distributions across cities

plt.figure(figsize=(8,5))

sns.boxplot(
    data=df,
    x='City',
    y='AQI'
)

plt.title('AQI Distribution by City')
plt.xlabel('City')
plt.ylabel('AQI')

plt.show()

# PLOT 2: Daily AQI across all years

plt.figure(figsize=(14,6))

for city in df['City'].unique():

    city_data = df[df['City'] == city]

    plt.plot(
        city_data['Date'],
        city_data['AQI'],
        label=city,
        alpha=0.7
    )

plt.title('Daily AQI Across Cities')
plt.xlabel('Date')
plt.ylabel('AQI')
plt.legend()

plt.show()

# PLOT 3: Smoothed AQI trend

plt.figure(figsize=(14,6))

for city in df['City'].unique():

    city_data = df[df['City'] == city].copy()
    city_data = city_data.sort_values('Date')

    city_data['MA30'] = (
        city_data['AQI']
        .rolling(window=30)
        .mean()
    )

    plt.plot(
        city_data['Date'],
        city_data['MA30'],
        label=city
    )

plt.title('30-Day Rolling Average AQI')
plt.xlabel('Date')
plt.ylabel('AQI')
plt.legend()

plt.show()

# PLOT 4: Monthly Average AQI by City

# Average AQI by city and month
monthly_avg = (
    df.groupby(['City', 'Month'])['AQI']
      .mean()
      .reset_index()
)

plt.figure(figsize=(10,6))

sns.lineplot(
    data=monthly_avg,
    x='Month',
    y='AQI',
    hue='City',
    marker='o'
)

plt.title('Monthly Average AQI by City')
plt.xlabel('Month')
plt.ylabel('Average AQI')
plt.xticks(range(1,13))

plt.legend(title='City')

plt.show()

# PLOT 5: Annual Average AQI Trend

# Annual average AQI by city and year
annual_avg = (
    df.groupby(['City','Year'])['AQI']
      .mean()
      .reset_index()
)

plt.figure(figsize=(10,6))

sns.lineplot(
    data=annual_avg,
    x='Year',
    y='AQI',
    hue='City',
    marker='o'
)

plt.title('Annual Average AQI Trend')
plt.xlabel('Year')
plt.ylabel('Average AQI')

plt.show()