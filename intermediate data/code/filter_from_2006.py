import pandas as pd

# Read the CSV file
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/Real-Estate Forecast/monthly_averaged_sales.csv')

# Convert date string to datetime for easier filtering
df['Date'] = pd.to_datetime(df['Date'].apply(lambda x: f"20{x.split('/')[1]}-{x.split('/')[0]}-01"))

# Filter data from October 2006 onwards
cutoff_date = pd.to_datetime('2006-10-01')
df_filtered = df[df['Date'] >= cutoff_date]

# Convert dates back to MM/YY format
df_filtered['Date'] = df_filtered['Date'].dt.strftime('%m/%y')

# Save the filtered data
output_path = '/Users/jaydenmcnab/Projects/oreo/Real-Estate Forecast/monthly_averaged_sales_filtered.csv'
df_filtered.to_csv(output_path, index=False)

# Print statistics
print(f"Original number of records: {len(df)}")
print(f"Records after filtering: {len(df_filtered)}")
print(f"Date range: {df_filtered['Date'].iloc[0]} to {df_filtered['Date'].iloc[-1]}")
print(f"\nOutput saved to: {output_path}")
