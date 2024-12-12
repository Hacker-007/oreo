import pandas as pd


def remove_outliers(df: pd.DataFrame):
    def remove_group_outliers(group):
        lower_bound = group["Sale Amount"].quantile(0.01)
        upper_bound = group["Sale Amount"].quantile(0.99)
        return group[
            (group["Sale Amount"] >= lower_bound)
            & (group["Sale Amount"] <= upper_bound)
        ]

    return df.groupby("Town", group_keys=False).apply(remove_group_outliers)


def reset_dates(df: pd.DataFrame):
    df['Date'] = pd.to_datetime(df['Date'])
    # Set all dates to the first of the month
    df["Date"] = df["Date"].dt.to_period("M").dt.to_timestamp()

    # Filter data after October 2006
    start_date = pd.Timestamp("2006-10-01")
    return df[df["Date"] >= start_date]


def remove_unknowns(df: pd.DataFrame):
    return df.loc[df['Town'] != '***Unknown***']


def impute_missing(df: pd.DataFrame):
    # Group by town and date, calculate mean sale amount
    monthly_avg = df.groupby(["Town", "Date"])["Sale Amount"].mean().reset_index()

    # Create a complete date range
    min_date = monthly_avg["Date"].min()
    max_date = monthly_avg["Date"].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq="MS")

    # Create a DataFrame with all possible town-date combinations
    towns = monthly_avg["Town"].unique()
    town_date_combinations = []
    for town in towns:
        for date in all_dates:
            town_date_combinations.append({"Town": town, "Date": date})

    complete_df = pd.DataFrame(town_date_combinations)

    # Merge with actual data
    monthly_avg = pd.merge(complete_df, monthly_avg, on=["Town", "Date"], how="left")

    # Perform interpolation for each town
    monthly_avg["Sale Amount"] = monthly_avg.groupby("Town")["Sale Amount"].transform(
        lambda x: x.interpolate(method="linear", limit_direction="both")
    )

    # Format the date as YYYY-MM-DD (with day always 01)
    monthly_avg["Date"] = monthly_avg["Date"].dt.strftime("%Y-%m-%d")

    # Round sale amounts to 3 decimal places
    monthly_avg["Sale Amount"] = monthly_avg["Sale Amount"].round(3)

    # Sort by Town and Date
    return monthly_avg.sort_values(["Town", "Date"])


def clean(input_file: str):
    # Read the CSV file with low_memory=False to handle mixed types
    df = pd.read_csv(
        input_file,
        low_memory=False,
    )

    df = remove_outliers(df)
    df = reset_dates(df)
    df = remove_unknowns(df)
    return impute_missing(df)