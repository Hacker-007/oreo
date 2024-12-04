import pandas as pd
import os

def clean_data(input_file_path: str, output_file_path: str):
    df = pd.read_csv(input_file_path, low_memory=False)
    commercial = df.loc[df['Property Type'] == 'Commercial'][['List Year', 'Town', 'Assessed Value', 'Sale Amount']]
    commercial = commercial.dropna()
    commercial.to_csv(output_file_path, index=False)
    print(commercial.count())

def main():
    input_csv = './data/Real_Estate_Sales_2001-2021_GL.csv'
    output_csv = './data/Real Estate.csv'
    if os.path.exists(input_csv):
        clean_data(output_csv)

if __name__ == '__main__':
    main()