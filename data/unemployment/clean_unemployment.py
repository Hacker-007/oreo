import pandas as pd


def clean_area_codes(towns) -> pd.Series:
    area_df = pd.read_csv("./data/unemployment/la.area.csv", low_memory=True)

    area_df = area_df[["area_code", "area_text"]]
    area_df = area_df.loc[area_df["area_text"].str.contains(", CT$", regex=True)]
    area_df = area_df.loc[~area_df["area_text"].str.contains("-")]

    # We expect there to be very few area codes that remain, and thus,
    # the below code should be reasonably optimal.
    area_codes = {}
    for code, text in zip(area_df["area_code"], area_df["area_text"]):
        for town in towns:
            if town in text:
                area_codes[town] = code
                break

    df = pd.Series(area_codes, name="Area Code")
    df.index.name = "Town"
    return df


def clean_series(area_codes_df: pd.DataFrame):
    series_df = pd.read_csv("./data/unemployment/la.series.csv", low_memory=True)

    series_df = series_df[["series_id", "area_code", "measure_code"]]
    series_df = series_df.loc[series_df["measure_code"] == 4]
    series_df = series_df.rename(
        columns={"series_id": "Series ID", "area_code": "Area Code"}
    )

    df = area_codes_df.merge(series_df[["Series ID", "Area Code"]], on="Area Code")
    return df[["Town", "Series ID"]]


def clean(towns: list[str]):
    area_codes_df = clean_area_codes(towns)
    series_df = clean_series(area_codes_df.reset_index())
    unemployment_df = pd.read_csv("./data/unemployment/la.data.13.Connecticut.csv")
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
    unemployment_df = (
        unemployment_df[["Date", "Town", "Unemployed"]]
        .sort_values(["Town", "Date"])
        .set_index("Date")
    )

    unemployment_df = unemployment_df.loc["2006-01-1":]
    return unemployment_df

