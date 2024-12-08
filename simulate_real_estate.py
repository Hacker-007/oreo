import pandas as pd
import numpy as np
from pmdarima import auto_arima
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')

# Read the data
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/data/real_estate_monthly_from_2006.csv')

# Convert Date to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Sort by Town and Date
df = df.sort_values(['Town', 'Date'])

# Get unique towns
towns = df['Town'].unique()

# Create empty lists to store results
forecasted_data = []
model_orders = []  # To store the best ARIMA parameters for each town

# Function to fit auto_arima and get forecast
def fit_and_forecast(data, town_name, periods=36):
    try:
        # Find the best ARIMA model
        model = auto_arima(data,
                          start_p=0, start_q=0, max_p=3, max_q=3, m=12,
                          start_P=0, start_Q=0, max_P=2, max_Q=2,
                          seasonal=True,
                          d=1, D=1, trace=False,
                          error_action='ignore',
                          suppress_warnings=True,
                          stepwise=True)
        
        # Store the model order
        order = model.order
        seasonal_order = model.seasonal_order
        model_orders.append({
            'Town': town_name,
            'Order': order,
            'Seasonal_Order': seasonal_order
        })
        
        # Get forecast
        forecast, conf_int = model.predict(n_periods=periods, return_conf_int=True)
        return forecast, conf_int
    except Exception as e:
        print(f"Error forecasting {town_name}: {str(e)}")
        return np.array([np.nan] * periods), np.array([[np.nan, np.nan]] * periods)

print("Running auto ARIMA simulations for each town...")

# Process each town
for town in tqdm(towns):
    # Get data for this town
    town_data = df[df['Town'] == town].sort_values('Date')
    
    # Fit model and get forecast with confidence intervals
    forecast, conf_int = fit_and_forecast(town_data['Sale Amount'], town)
    
    # Create dates for forecast period
    last_date = town_data['Date'].max()
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                 periods=36, 
                                 freq='MS')
    
    # Add forecasted data to results
    for date, value, (lower, upper) in zip(forecast_dates, forecast, conf_int):
        forecasted_data.append({
            'Town': town,
            'Date': date,
            'Sale Amount': value,
            'Lower_CI': lower,
            'Upper_CI': upper,
            'Projected': True
        })

# Create DataFrame with forecasted data
forecast_df = pd.DataFrame(forecasted_data)

# Create DataFrame with model orders
model_orders_df = pd.DataFrame(model_orders)
model_orders_df.to_csv('arima_model_orders.csv', index=False)

# Combine historical and forecasted data
historical_df = df.copy()
historical_df['Projected'] = False
historical_df['Lower_CI'] = np.nan
historical_df['Upper_CI'] = np.nan

# Combine and sort the data
combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)
combined_df = combined_df.sort_values(['Town', 'Date'])

# Save to CSV
output_file = 'real_estate_with_projections.csv'
combined_df.to_csv(output_file, index=False)

# Print summary statistics
print("\nSummary:")
print(f"Number of towns processed: {len(towns)}")
print(f"Historical data range: {historical_df['Date'].min()} to {historical_df['Date'].max()}")
print(f"Forecast data range: {forecast_df['Date'].min()} to {forecast_df['Date'].max()}")
print(f"\nOutput saved to: {output_file}")
print(f"ARIMA model parameters saved to: arima_model_orders.csv")

# Calculate and print average unemployment by year
print("\nAverage Sale Amount by Month and Year:")
yearly_avg = combined_df.groupby([combined_df['Date'].dt.year, 'Projected'])['Sale Amount'].mean().round(1)
print(yearly_avg)

# Print some example model orders
print("\nExample ARIMA Models (first 5 towns):")
print(model_orders_df.head())
