import pandas as pd
import os

PROPERTY_TYPES = ['Single Family', 'Two Family', 'Three Family', 'Four Family']
REAL_ESTATE_COLUMNS = ['List Year', 'Property Type', 'Town', 'Assessed Value', 'Sale Amount']

def clean_data(input_file_path: str, output_file_path: str):
    df = pd.read_csv(input_file_path, low_memory=False)
    residential_prices = df.loc[df['Property Type'].isin(PROPERTY_TYPES)][REAL_ESTATE_COLUMNS]
    residential_prices.dropna(inplace=True)
    residential_prices.to_csv(output_file_path, index=False)
    residential_prices = residential_prices.loc[residential_prices['Town'] != '***Unknown***']
    print(residential_prices.count())

def main():
    input_csv = './data/Real_Estate_Sales_2001-2021_GL.csv'
    output_csv = './data/Real Estate.csv'
    if os.path.exists(input_csv):
        clean_data(input_csv, output_csv)

if __name__ == '__main__':
    main()