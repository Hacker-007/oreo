import pandas as pd
import numpy as np
from pmdarima import auto_arima
from datetime import datetime
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')

print("Loading data...")
# Read the data
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/Real-Estate Forecast/final_monthly_averages.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Get unique cities, excluding 'Unknown'
cities = sorted(df['Town'].unique())
if 'Unknown' in cities:
    cities.remove('Unknown')

print(f"Processing {len(cities)} cities...")

# Create future dates for prediction
last_date = df['Date'].max()
future_dates = pd.date_range(start=last_date, periods=38, freq='MS')[1:]  # 34 months ahead

# List to store all forecasts
all_forecasts = []

# Process each city with progress bar
for city in tqdm(cities, desc="Forecasting cities"):
    try:
        # Get city data
        city_data = df[df['Town'] == city].sort_values('Date')
        
        if len(city_data) < 24:  # Skip cities with insufficient data
            print(f"\nSkipping {city} - insufficient data")
            continue
            
        # Fit ARIMA model
        model = auto_arima(city_data['Sale Amount'],
                          start_p=0, start_q=0,
                          max_p=2, max_q=2,
                          m=12,
                          start_P=0, start_Q=0,
                          max_P=1, max_Q=1,
                          seasonal=True,
                          d=1, D=1,
                          error_action='ignore',
                          suppress_warnings=True,
                          stepwise=True,
                          max_order=4)
        
        # Generate forecast
        forecast = model.predict(n_periods=37, return_conf_int=True)
        forecast_mean = forecast[0]
        forecast_ci = forecast[1]
        
        # Store forecasts
        forecast_df = pd.DataFrame({
            'Town': city,
            'Date': future_dates,
            'Sale Amount': forecast_mean,
            'Lower_CI': forecast_ci[:, 0],
            'Upper_CI': forecast_ci[:, 1]
        })
        all_forecasts.append(forecast_df)
        
    except Exception as e:
        print(f"\nError processing {city}: {str(e)}")

# Combine all forecasts
print("\nCombining forecasts...")
final_forecasts = pd.concat(all_forecasts)

# Save to CSV
print("Saving forecasts...")
final_forecasts.to_csv('all_cities_forecasts.csv', index=False)

# Print summary statistics
print("\nForecast Summary for July 2025:")
print("-" * 50)
july_2025_forecasts = final_forecasts[final_forecasts['Date'] == '2025-07-01'].sort_values(by='Sale Amount', ascending=False)
print("\nTop 5 Cities by Projected Price:")
for _, row in july_2025_forecasts.head().iterrows():
    print(f"{row['Town']}: ${row['Sale Amount']:,.2f} (Range: ${row['Lower_CI']:,.2f} - ${row['Upper_CI']:,.2f})")

print("\nBottom 5 Cities by Projected Price:")
for _, row in july_2025_forecasts.tail().iterrows():
    print(f"{row['Town']}: ${row['Sale Amount']:,.2f} (Range: ${row['Lower_CI']:,.2f} - ${row['Upper_CI']:,.2f})")

print("\nOutput saved to: all_cities_forecasts.csv")
