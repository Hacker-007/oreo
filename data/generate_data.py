import pandas as pd
from sklearn.impute import SimpleImputer


def clean_real_estate() -> pd.DataFrame:
    df = pd.read_csv("./Real_Estate_Sales_2001-2021_GL.csv", low_memory=False)

    property_types = ["Single Family", "Two Family", "Three Family", "Four Family"]
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
    return residential_prices


def clean_area_codes(real_estate_df) -> pd.Series:
    area_df = pd.read_csv("./la.area.csv", low_memory=True)

    area_df = area_df[["area_code", "area_text"]]
    area_df = area_df.loc[area_df["area_text"].str.contains(", CT$", regex=True)]
    area_df = area_df.loc[~area_df["area_text"].str.contains("-")]

    # We expect there to be very few area codes that remain, and thus,
    # the below code should be reasonably optimal.
    area_codes = {}
    for code, text in zip(area_df["area_code"], area_df["area_text"]):
        for town in real_estate_df["Town"]:
            if town in text:
                area_codes[town] = code
                break

    df = pd.Series(area_codes, name="Area Code")
    df.index.name = "Town"
    return df


def clean_series(area_codes_df):
    series_df = pd.read_csv("./la.series.csv", low_memory=True)

    series_df = series_df[["series_id", "area_code", "measure_code"]]
    series_df = series_df.loc[series_df["measure_code"] == 4]
    series_df = series_df.rename(
        columns={"series_id": "Series ID", "area_code": "Area Code"}
    )
    df = area_codes_df.merge(series_df[["Series ID", "Area Code"]], on="Area Code")
    return df[["Town", "Series ID"]]


def generate_unemployment_data():
    # real_estate_df = './data/Real Estate.csv'
    # area_codes_df = clean_area_codes(real_estate_df)
    # series_df = clean_series(area_codes_df)
    series_df = pd.read_csv("./Series ID.csv")
    unemployment_df = pd.read_csv("./la.data.13.Connecticut.csv")
    unemployment_df = unemployment_df.rename(
        columns={
            "series_id": "Series ID",
            "year": "Year",
            "period": "Month",
            "value": "Unemployed",
        }
    )

    unemployment_df = unemployment_df.merge(series_df, on="Series ID")
    unemployment_df = unemployment_df.loc[unemployment_df["Month"] != "M13"]
    unemployment_df["Date"] = (
        unemployment_df["Month"] + "/" + unemployment_df["Year"].astype(str)
    )
    unemployment_df["Date"] = pd.to_datetime(unemployment_df["Date"], format="M%m/%Y")
    unemployment_df = unemployment_df[["Date", "Town", "Unemployed"]].set_index("Date")
    return unemployment_df.loc["2006-01-1":]


if __name__ == "__main__":
    df = generate_unemployment_data()
    df.to_csv('./Connecticut Unemployed.csv')
