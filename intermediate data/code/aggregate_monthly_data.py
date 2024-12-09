import pandas as pd
import numpy as np
from datetime import datetime

# Read the cleaned data
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/intermediate data/data/cleaned_residential_sales.csv')

# Remove any unknown or invalid town names
df = df[df['Town'] != '***Unknown***']
df = df[df['Town'].notna()]

# Convert date to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Create month and year columns
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# Group by town, year, and month to get monthly averages
monthly_avg = df.groupby(['Town', 'Year', 'Month'])['Sale Amount'].mean().reset_index()

# Create a complete date range for each town
towns = df['Town'].unique()
years = df['Year'].unique()
months = range(1, 13)

# Create all possible combinations of town, year, and month
all_combinations = []
for town in towns:
    for year in years:
        for month in months:
            all_combinations.append({
                'Town': town,
                'Year': year,
                'Month': month
            })

# Convert to DataFrame
complete_df = pd.DataFrame(all_combinations)

# Merge with actual data
merged_df = pd.merge(complete_df, monthly_avg, 
                    on=['Town', 'Year', 'Month'], 
                    how='left')

# Sort by Town, Year, and Month
merged_df = merged_df.sort_values(['Town', 'Year', 'Month'])

# Function to fill missing values with running average
def fill_with_running_avg(group):
    # Get the first non-NaN value for initialization
    first_valid = group['Sale Amount'].first_valid_index()
    if first_valid is not None:
        first_value = group.loc[first_valid, 'Sale Amount']
        # Fill NaN values before the first valid value with the first valid value
        group.loc[:first_valid, 'Sale Amount'] = first_value
    # Fill remaining NaN values with expanding mean
    group['Sale Amount'] = group['Sale Amount'].fillna(group['Sale Amount'].expanding().mean())
    return group

# Apply running average fill by town
merged_df = merged_df.groupby('Town').apply(fill_with_running_avg).reset_index(drop=True)

# Create the date string in MM/YY format
merged_df['Date'] = merged_df.apply(
    lambda x: f"{x['Month']:02d}/{str(x['Year'])[2:]}", axis=1
)

# Format the final output
final_df = merged_df[['Date', 'Town', 'Sale Amount']].copy()

# Round Sale Amount to 2 decimal places
final_df['Sale Amount'] = final_df['Sale Amount'].round(2)

# Save to CSV
output_path = '/Users/jaydenmcnab/Projects/oreo/monthly_averaged_sales.csv'
final_df.to_csv(output_path, index=False)

# Print some statistics
print("\nData Summary:")
print(f"Number of towns processed: {len(towns)}")
print(f"Date range: {min(years)} to {max(years)}")
print(f"Total number of entries: {len(final_df)}")

# Sample of the data
print("\nSample of the processed data:")
print(final_df.head(10))

print(f"\nOutput saved to: {output_path}")
