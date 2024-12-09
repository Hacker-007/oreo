import pandas as pd
import numpy as np

# Read the data
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/intermediate data/data/filtered_residential_sales.csv')

# Create a dictionary to store removed top 1% values for each town
removed_top_values = {}

# Function to process each town
def remove_outliers_and_store(group):
    town_name = group.name
    
    # Calculate percentiles for this town
    lower_bound = group['Sale Amount'].quantile(0.01)
    upper_bound = group['Sale Amount'].quantile(0.99)
    
    # Store removed top values
    removed_top = group[group['Sale Amount'] > upper_bound].copy()
    removed_top = removed_top.sort_values('Sale Amount', ascending=False)
    removed_top_values[town_name] = removed_top
    
    # Return filtered data
    return group[(group['Sale Amount'] >= lower_bound) & 
                (group['Sale Amount'] <= upper_bound)]

# Process each town
df_cleaned = df.groupby('Town', group_keys=False).apply(remove_outliers_and_store)

# Save cleaned data
df_cleaned.to_csv('/Users/jaydenmcnab/Projects/oreo/cleaned_residential_sales.csv', index=False)

# Print summary of removed top values
print("\nTop 1% Sales Removed by Town:")
print("-" * 80)
print(f"{'Town':<30} {'Sale Amount':>15} {'Date':<15}")
print("-" * 80)

for town, removed_df in sorted(removed_top_values.items()):
    if not removed_df.empty:
        # Get the top 5 highest values for each town
        top_5 = removed_df.head(5)
        print(f"\n{town}")
        for _, row in top_5.iterrows():
            print(f"{'':30} ${row['Sale Amount']:>14,.2f} {row['Date']:<15}")

# Print summary statistics
original_count = len(df)
cleaned_count = len(df_cleaned)
removed_count = original_count - cleaned_count

print("\n" + "=" * 80)
print(f"\nSummary Statistics:")
print(f"Original number of entries: {original_count:,}")
print(f"Entries after removing outliers: {cleaned_count:,}")
print(f"Total entries removed: {removed_count:,} ({(removed_count/original_count)*100:.2f}%)")
