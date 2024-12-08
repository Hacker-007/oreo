import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

def clean_real_estate() -> pd.DataFrame:
    df = pd.read_csv("./Real_Estate_Sales_2001-2021_GL 2.csv", low_memory=False)

    property_types = ["Residential","Single Family", "Two Family", "Three Family", "Four Family"]
    real_estate_columns = [
        "Date Recorded",
        "Town",
        "Sale Amount",
    ]
    residential_prices = df.loc[df["Property Type"].isin(property_types)][
        real_estate_columns
    ]
    residential_prices.dropna(inplace=True)
    residential_prices = residential_prices.loc[
        residential_prices["Town"] != "***Unknown***"
    ]
    
    # Multiply all sale amounts by 1.3
    residential_prices['Sale Amount'] = residential_prices['Sale Amount'] * 1.3
    
    # Convert Date Recorded to datetime
    residential_prices['Date Recorded'] = pd.to_datetime(residential_prices['Date Recorded'])
    
    # Create Year and Month columns
    residential_prices['Year'] = residential_prices['Date Recorded'].dt.year
    residential_prices['Month'] = residential_prices['Date Recorded'].dt.month
    
    # Group by Town, Year, Month and calculate mean sale amount
    monthly_avg = residential_prices.groupby(['Town', 'Year', 'Month'])['Sale Amount'].mean().reset_index()
    
    # Create a complete date range for each town
    towns = monthly_avg['Town'].unique()
    years = range(2006, monthly_avg['Year'].max() + 1)  # Start from 2006
    months = range(1, 13)
    
    # Create a complete grid of all possible town-year-month combinations
    complete_grid = pd.DataFrame([
        (town, year, month)
        for town in towns
        for year in years
        for month in months
    ], columns=['Town', 'Year', 'Month'])
    
    # Merge with actual data
    complete_data = pd.merge(
        complete_grid,
        monthly_avg,
        on=['Town', 'Year', 'Month'],
        how='left'
    )
    
    # Impute missing values by town mean
    imputer = SimpleImputer(strategy='mean')
    
    # Impute for each town separately
    for town in towns:
        town_mask = complete_data['Town'] == town
        complete_data.loc[town_mask, 'Sale Amount'] = imputer.fit_transform(
            complete_data.loc[town_mask, ['Sale Amount']]
        )
    
    # Create proper datetime index
    complete_data['Date'] = pd.to_datetime(
        complete_data[['Year', 'Month']].assign(Day=1)
    )
    
    # Filter for dates from October 2006 onwards
    complete_data = complete_data[
        complete_data['Date'] >= pd.Timestamp('2006-10-01')
    ]
    
    # Drop separate Year and Month columns and sort
    result = complete_data.drop(['Year', 'Month'], axis=1)
    result = result.sort_values(['Town', 'Date'])
    
    # Save to new CSV
    output_file = 'real_estate_monthly_from_2006.csv'
    result.to_csv(output_file, index=False)
    
    return result

if __name__ == "__main__":
    # Test the function
    result_df = clean_real_estate()
    print("\nSample of processed data:")
    print(result_df.head())
    print("\nShape of data:", result_df.shape)
    print("\nNumber of towns:", len(result_df['Town'].unique()))
    print("\nDate range:", result_df['Date'].min(), "to", result_df['Date'].max())
    print("\nOutput saved to: real_estate_monthly_from_2006.csv")
