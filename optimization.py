import gurobipy as gp
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from gurobipy import GRB

# Sets
date_range = pd.date_range(start='2024-11-01', end='2025-10-01', freq='MS')
months = [date.strftime('%Y-%m-%d') for date in date_range]
month_to_int = {date: i for i, date in enumerate(months, start=1)}
int_to_month = {i: date for i, date in enumerate(months, start=1)}
unemployment_df = pd.read_csv("./Unemployment Forecast/Forecasted Unemployment.csv")
real_estate_df = pd.read_csv("./Real-Estate Forecast/all_cities_forecasts.csv")
cities = set(unemployment_df["Town"]) & set(real_estate_df["Town"])

# Parameters
TOTAL_BUDGET = 25_000_000
MONTHLY_REEMPLOYMENT = 500
PERCENT_HELPED = 0.7

cost = dict()
unemployed = dict()
real_estate_df.set_index(['Town', 'Date'], inplace=True)
unemployment_df.set_index(['Town', 'Date'], inplace=True)
for city in cities:
    for month in months:
        # Commercial costs seeem to be 1.3x residential housing costs
        cost[(city, month)] = 1.3 * real_estate_df.loc[(city, month), 'Sale Amount']
        unemployed[(city, month)] = unemployment_df.loc[(city, month), 'Unemployed']

model = gp.Model("Minimize_Total_Unemployed")

# Variables
p = model.addVars(cities, months, vtype=GRB.INTEGER)
r = model.addVars(cities, months, vtype=GRB.CONTINUOUS)  # Residual unemployment

# Objective: Minimize total residual unemployment across all cities and months
model.setObjective(sum(sum(r[c, m] for m in months) for c in cities), GRB.MINIMIZE)

# Constraints
# Cost constraint: Total cost of centers
model.addConstr(
    sum(sum(cost[c, m] * (p[c, m] - p[c, int_to_month[month_to_int[m] - 1]] if month_to_int[m] > 1 else p[c, m]) for m in months) for c in cities) <= TOTAL_BUDGET
)

# Re-employment centers should be non-decreasing over time
model.addConstrs(p[c, int_to_month[month_to_int[m] + 1]] >= p[c, m] for c in cities for m in months[:-1])

# Residual unemployment is the max of 0 and actual residual unemployment
model.addConstrs(r[c, m] >= unemployed[c, m] - PERCENT_HELPED * MONTHLY_REEMPLOYMENT * p[c, m] - sum(unemployed[c,int_to_month[k]] - r[c,int_to_month[k]] for k in range(1,month_to_int[m])) for c in cities for m in months)
model.addConstrs(r[c, m] >= 0 for c in cities for m in months)

# Non-negativity constraint
model.addConstrs(p[c, m] >= 0 for c in cities for m in months)

model.optimize()

# RESULTS
if model.status == GRB.OPTIMAL:
    print(f"Optimal Objective Value (Total Resiudal Unemployment): {model.objVal}")
    for c in list(cities)[:5]:
        for m in months:
            print(f"City {c}, Month {m}: p = {p[c, m].x}")
else:
    print("No optimal solution found.")

p_values = { (city, month): p[city, month].x for city in cities for month in months }

# Convert the results into a DataFrame for easier plotting
data = []
for city in cities:
    row = []
    for month in months:
        row.append(p_values.get((city, month), 0))  # Default to 0 if not found
    data.append(row)

df = pd.DataFrame(data, columns=list(months), index=list(cities))
df.to_csv(f'Optimal Location - {TOTAL_BUDGET} - {MONTHLY_REEMPLOYMENT}.csv')

# Create a heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(df, annot=False, fmt=".1f", cmap="coolwarm", cbar_kws={'label': 'Re-employment Centers'})
plt.title("Number of Re-employment Centers Across Cities and Months")
plt.xlabel("Month")
plt.ylabel("City")
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.show()