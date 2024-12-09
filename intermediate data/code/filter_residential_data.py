import pandas as pd

# Read the original CSV file
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/original data/Real-Estate Data/Real_Estate_Sales_2001-2021_GL 2.csv', low_memory=False)

# Define residential property types to keep
residential_types = [
    'Single Family', 
    'Two Family', 
    'Three Family', 
    'Four Family', 
    'Residential'
]

# Filter for residential properties (case-insensitive)
df['Property Type'] = df['Property Type'].str.strip()  # Remove any leading/trailing whitespace
mask = df['Property Type'].str.lower().isin([t.lower() for t in residential_types])
filtered_df = df[mask]

# Select only the required columns
# First, let's see what the date column is actually called in the CSV
date_columns = [col for col in df.columns if 'date' in col.lower()]
if 'Date Recorded' in df.columns:
    date_col = 'Date Recorded'
elif len(date_columns) > 0:
    date_col = date_columns[0]
else:
    raise ValueError("Could not find date column in CSV")

# Select and rename columns as needed
result_df = filtered_df[[date_col, 'Town', 'Sale Amount']]
result_df = result_df.rename(columns={date_col: 'Date'})

# Save to new CSV file
output_path = '/Users/jaydenmcnab/Projects/oreo/filtered_residential_sales.csv'
result_df.to_csv(output_path, index=False)

# Print some statistics
print(f"Original number of records: {len(df)}")
print(f"Number of residential records: {len(filtered_df)}")
print(f"Percentage of residential properties: {(len(filtered_df)/len(df))*100:.2f}%")
print(f"\nOutput saved to: {output_path}")
