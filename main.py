import warnings
import os
import sys

from tqdm import tqdm
import pandas as pd

from pmdarima import auto_arima

import gurobipy as gp
from gurobipy import GRB

warnings.filterwarnings("ignore")


def forecast_unemployment(input_file, output_file):
    """Generate unemployment forecasts using ARIMA models."""
    print("\n1. Forecasting Unemployment...")

    # Read the data
    unemployed_df = pd.read_csv(input_file)
    unemployed_df["Date"] = pd.to_datetime(unemployed_df["Date"])

    # Create future dates
    future_dates = pd.date_range(start="2024-11-01", end="2025-10-01", freq="MS")

    # Store forecasts
    forecasts = []

    # Process each town
    for town in tqdm(unemployed_df["Town"].unique(), desc="Processing towns"):
        town_data = unemployed_df[unemployed_df["Town"] == town].sort_values("Date")

        # Fit ARIMA model
        model = auto_arima(
            town_data["Unemployed"],
            seasonal=True,
            m=12,
            suppress_warnings=True,
            error_action="ignore",
        )

        # Generate forecast
        forecast = model.predict(n_periods=len(future_dates))

        # Create forecast DataFrame
        forecast_df = pd.DataFrame(
            {
                "Town": town,
                "Date": future_dates.strftime("%Y-%m-%d"),
                "Unemployed": forecast.round(),
            }
        )

        forecasts.append(forecast_df)

    # Combine all forecasts
    final_forecasts = pd.concat(forecasts, ignore_index=True)

    # Save forecasts
    final_forecasts.to_csv(output_file, index=False)
    print(f"Unemployment forecasts saved to {output_file}")


def forecast_real_estate(input_file, output_file):
    """Generate real estate price forecasts using ARIMA models."""
    print("\n2. Forecasting Real Estate Prices...")

    # Read the data
    df = pd.read_csv(input_file)
    df["Date"] = pd.to_datetime(df["Date"])

    # Get unique cities, excluding 'Unknown'
    cities = sorted(df["Town"].unique())
    if "Unknown" in cities:
        cities.remove("Unknown")

    # Create future dates
    future_dates = pd.date_range(start="2024-11-01", end="2025-10-01", freq="MS")

    # Store forecasts
    all_forecasts = []

    # Process each city
    for city in tqdm(cities, desc="Processing cities"):
        try:
            city_data = df[df["Town"] == city].sort_values("Date")

            if len(city_data) < 24:  # Skip cities with insufficient data
                print(f"\nSkipping {city} - insufficient data")
                continue

            # Fit ARIMA model
            model = auto_arima(
                city_data["Sale Amount"],
                start_p=0,
                start_q=0,
                max_p=2,
                max_q=2,
                m=12,
                seasonal=True,
                d=1,
                D=1,
                error_action="ignore",
                suppress_warnings=True,
                stepwise=True,
                max_order=4,
            )

            # Generate forecast
            forecast = model.predict(n_periods=len(future_dates))

            # Create forecast DataFrame
            forecast_df = pd.DataFrame(
                {
                    "Town": city,
                    "Date": future_dates.strftime("%Y-%m-%d"),
                    "Sale Amount": forecast,
                }
            )

            all_forecasts.append(forecast_df)

        except Exception as e:
            print(f"\nError processing {city}: {str(e)}")

    # Combine all forecasts
    final_forecasts = pd.concat(all_forecasts, ignore_index=True)

    # Save forecasts
    final_forecasts.to_csv(output_file, index=False)
    print(f"Real estate forecasts saved to {output_file}")


def optimize_locations(
    unemployment_file,
    real_estate_file,
    budget,
    monthly_reemployment,
    percent_helped,
    output_file,
):
    """Optimize reemployment center locations using Gurobi."""
    print("\n3. Optimizing Center Locations...")

    # Read forecast data
    unemployment_df = pd.read_csv(unemployment_file)
    real_estate_df = pd.read_csv(real_estate_file)

    # Get common cities and date range
    cities = set(unemployment_df["Town"]) & set(real_estate_df["Town"])
    date_range = pd.date_range(start="2024-11-01", end="2025-10-01", freq="MS")
    months = [date.strftime("%Y-%m-%d") for date in date_range]

    # Setup month mappings
    month_to_int = {date: i for i, date in enumerate(months, start=1)}
    int_to_month = {i: date for i, date in enumerate(months, start=1)}

    # Prepare data
    cost = dict()
    unemployed = dict()

    real_estate_df.set_index(["Town", "Date"], inplace=True)
    unemployment_df.set_index(["Town", "Date"], inplace=True)

    for city in cities:
        for month in months:
            cost[(city, month)] = 1.3 * real_estate_df.loc[(city, month), "Sale Amount"]
            unemployed[(city, month)] = unemployment_df.loc[(city, month), "Unemployed"]

    # Create and solve optimization model
    model = gp.Model("Minimize_Total_Unemployed")

    # Variables
    p = model.addVars(cities, months, vtype=GRB.INTEGER)
    r = model.addVars(cities, months, vtype=GRB.CONTINUOUS)

    # Objective
    model.setObjective(sum(sum(r[c, m] for m in months) for c in cities), GRB.MINIMIZE)

    # Budget Constraint
    model.addConstr(
        sum(
            sum(
                cost[c, m]
                * (
                    p[c, m] - p[c, int_to_month[month_to_int[m] - 1]]
                    if month_to_int[m] > 1
                    else p[c, m]
                )
                for m in months
            )
            for c in cities
        )
        <= budget
    )

    # Center Persistence Constraint
    model.addConstrs(
        p[c, int_to_month[month_to_int[m] + 1]] >= p[c, m]
        for c in cities
        for m in months[:-1]
    )

    # Residual Unemployed Individuals Constraint
    model.addConstrs(
        r[c, m]
        >= unemployed[c, m]
        - percent_helped * monthly_reemployment * p[c, m]
        - sum(
            unemployed[c, int_to_month[k]] - r[c, int_to_month[k]]
            for k in range(1, month_to_int[m])
        )
        for c in cities
        for m in months
    )

    # Solve
    model.optimize()

    # Extract and save results
    if model.status == GRB.OPTIMAL:
        results = []
        for month in months:
            month_results = {"Unnamed: 0": month}
            for city in cities:
                month_results[city] = p[city, month].X
            results.append(month_results)

        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False)
        print(f"Optimization results saved to {output_file}")
    else:
        print("Optimization failed to find a solution")


def create_visualization(input_file):
    """Create animated visualization of results."""
    print("\n4. Creating Visualization...")
    import map_towns

    map_towns.create_animation(input_file)
    print("Animation created as centers_animation.gif")


def main():
    # Parameters
    TOTAL_BUDGET = 25_000_000
    MONTHLY_REEMPLOYMENT = 500
    PERCENT_HELPED = 0.7

    # File paths
    UNEMPLOYMENT_INPUT = "./Unemployment Forecast/Connecticut Unemployed.csv"
    REAL_ESTATE_INPUT = "./Real-Estate Forecast/final_monthly_averages.csv"
    UNEMPLOYMENT_FORECAST = "./Unemployment Forecast/Forecasted Unemployment.csv"
    REAL_ESTATE_FORECAST = "./Real-Estate Forecast/all_cities_forecasts.csv"
    OPTIMIZATION_OUTPUT = (
        f"Optimal Location - {TOTAL_BUDGET} - {MONTHLY_REEMPLOYMENT}.csv"
    )

    # Check if input files exist
    for file in [UNEMPLOYMENT_INPUT, REAL_ESTATE_INPUT]:
        if not os.path.exists(file):
            print(f"Error: Input file {file} not found")
            sys.exit(1)

    # Run pipeline
    forecast_unemployment(UNEMPLOYMENT_INPUT, UNEMPLOYMENT_FORECAST)
    forecast_real_estate(REAL_ESTATE_INPUT, REAL_ESTATE_FORECAST)
    optimize_locations(
        UNEMPLOYMENT_FORECAST,
        REAL_ESTATE_FORECAST,
        TOTAL_BUDGET,
        MONTHLY_REEMPLOYMENT,
        PERCENT_HELPED,
        OPTIMIZATION_OUTPUT,
    )
    create_visualization(OPTIMIZATION_OUTPUT)

    print("\nPipeline complete! Check centers_animation.gif for the visualization.")


if __name__ == "__main__":
    main()