import pandas as pd

# Read the CSV file with low_memory=False to handle mixed types
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/data/Real_Estate_Sales_2001-2021_GL 2.csv', low_memory=False)

# Define the residential property types we want to include
residential_types = ['Single Family', 'Two Family', 'Three Family', 'Four Family']

# Create a copy of the filtered data
filtered_df = df[
    # Filter for residential property types
    df['Property Type'].isin(residential_types) &
    # Remove entries with missing dates
    df['Date Recorded'].notna() &
    # Remove unknown towns
    (df['Town'] != '***Unknown***')
].copy()

# Convert date to datetime
filtered_df['Date Recorded'] = pd.to_datetime(filtered_df['Date Recorded'])

# Select only the columns we want
result_df = filtered_df[['Town', 'Date Recorded', 'Sale Amount']]

# Sort by town and date
result_df = result_df.sort_values(['Town', 'Date Recorded'])

# Save to new CSV
output_file = 'residential_sales.csv'
result_df.to_csv(output_file, index=False)

# Print summary statistics
print("\nSummary:")
print(f"Original number of records: {len(df)}")
print(f"Filtered number of records: {len(result_df)}")
print(f"Number of towns: {len(result_df['Town'].unique())}")
print(f"Date range: {result_df['Date Recorded'].min()} to {result_df['Date Recorded'].max()}")
print(f"\nOutput saved to: {output_file}")

# Print sample of the data
print("\nSample of the filtered data:")
print(result_df.head())
