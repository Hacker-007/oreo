import gurobipy as gp
import pandas as pd
from gurobipy import GRB

# Sets
date_range = pd.date_range(start='2024-11-01', end='2025-10-01', freq='MS')
months = [date.strftime('%Y-%m-%d') for date in date_range]
month_to_int = {date: i for i, date in enumerate(months, start=1)}
int_to_month = {i: date for i, date in enumerate(months, start=1)}
unemployment_df = pd.read_csv("./Unemployment Forecast/Forecasted Unemployment.csv")
real_estate_df = pd.read_csv("./Real-Estate Forecast/forecasted_real_estate.csv")
cities = set(unemployment_df["Town"]) & set(real_estate_df["Town"])

# Parameters
cost = dict()
unemployed = dict()
real_estate_df.set_index(['Town', 'Date'], inplace=True)
unemployment_df.set_index(['Town', 'Date'], inplace=True)
for city in cities:
    for month in months:
        cost[(city, month)] = real_estate_df.loc[(city, month), 'Sale Amount']
        unemployed[(city, month)] = unemployment_df.loc[(city, month), 'Unemployed']

budget = 1000  # Total budget

model = gp.Model("Minimize_Total_Unemployed")

# Variables
p = model.addVars(cities, months, vtype=GRB.INTEGER)
r = model.addVars(cities, months, vtype=GRB.CONTINUOUS)  # Residual unemployment

# Objective: Minimize total residual unemployment across all cities and months
model.setObjective(sum(sum(r[c, m] for m in months) for c in cities), GRB.MINIMIZE)

# Constraints
# Cost constraint: Total cost of centers
model.addConstr(
    sum(sum(cost[c, m] * (p[c, m] - p[c, int_to_month[month_to_int[m] - 1]] if month_to_int[m] > 1 else p[c, m]) for m in months) for c in cities) <= budget
)

# Re-employment centers should be non-decreasing over time
model.addConstrs(p[c, int_to_month[month_to_int[m] + 1]] >= p[c, m] for c in cities for m in months[:-1])

# Residual unemployment is the max of 0 and actual residual unemployment
model.addConstrs(r[c, m] >= unemployed[c, m] - 4000 * p[c, m] for c in cities for m in months)
model.addConstrs(r[c, m] >= 0 for c in cities for m in months)

# Non-negativity constraint
model.addConstrs(p[c, m] >= 0 for c in cities for m in months)

model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    print(f"Optimal Objective Value (Total Resiudal Unemployment): {model.objVal}")
    for c in list(cities)[:5]:
        for m in months:
            print(f"City {c}, Month {m}: p = {p[c, m].x}")
else:
    print("No optimal solution found.")