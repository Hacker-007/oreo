import pandas as pd

def series_values():
    # Keep only unemployment as a measure
    MEASURE = 4
    series_df = pd.read_csv("./data/la.series.csv", low_memory=False)
    area_df = pd.read_csv("./data/la.area.csv", low_memory=False)
    conn_df = pd.read_csv("./data/la.data.13.Connecticut.csv", low_memory=False)
    re_df = pd.read_csv("./data/Real Estate.csv", low_memory=False)
    # Get all towns in Connecticut Real estate data set
    towns = re_df["Town"]
    towns_list = towns.tolist()

    # Create a mask to check if area_text contains "<town>" and ", CT"
    filtered_area_df = area_df[
        area_df["area_text"].apply(lambda x: any(town in x and ", CT" in x for town in towns_list))
    ]

    # Get the area_code values
    associated_area_codes = filtered_area_df["area_code"].unique()

    # Filter the series data for measure_code == 4 and area_code in associated_area_codes
    filtered_series = series_df[
        (series_df['measure_code'] == MEASURE) &
        (series_df['area_code'].isin(associated_area_codes))
    ]
    # Extract unique series_id values
    filtered_series_ids = filtered_series['series_id'].unique()

    print(filtered_series_ids)

series_values()