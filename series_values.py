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

    # Print or use the results as needed
    print(f"Associated area codes: {associated_area_codes}")

series_values()