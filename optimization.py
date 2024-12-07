import gurobipy as gp
from gurobipy import GRB

# Sets
months = list(range(1, 3))
cities = ['city1', 'city2', 'city3']

# Parameters
cost = {('city1', 1): 5000, ('city1', 2): 600,  # Cost of opening re-employment centers
        ('city2', 1): 400, ('city2', 2): 500,
        ('city3', 1): 700, ('city3', 2): 800}  # Extend for all cities/months

unemployed = {('city1', 1): 5000, ('city1', 2): 6000,  # Unemployed individuals
      ('city2', 1): 3000, ('city2', 2): 4000,
      ('city3', 1): 7000, ('city3', 2): 8000}  # Extend for all cities/months

budget = 10  # Total budget

model = gp.Model("Minimize_Total_Unemployed")

# Variables
p = model.addVars(cities, months, vtype=GRB.INTEGER)
r = model.addVars(cities, months, vtype=GRB.CONTINUOUS)  # Residual unemployment

# Objective: Minimize total residual unemployment across all cities and months
model.setObjective(sum(sum(r[c, m] for m in months) for c in cities), GRB.MINIMIZE)

# Constraints
# Cost constraint: Total cost of centers
model.addConstr(
    sum(sum(cost[c, m] * (p[c, m] - p[c, m - 1] if m > 1 else p[c, m]) for m in months) for c in cities) <= budget
)

# Re-employment centers should be non-decreasing over time
model.addConstrs(p[c, m + 1] >= p[c, m] for c in cities for m in months[:-1])

# Residual unemployment is the max of 0 and actual residual unemployment
model.addConstrs(r[c, m] >= unemployed[c, m] - 4000 * p[c, m] for c in cities for m in months)
model.addConstrs(r[c, m] >= 0 for c in cities for m in months)

# Non-negativity constraint
model.addConstrs(p[c, m] >= 0 for c in cities for m in months)

model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    print(f"Optimal Objective Value (Total Resiudal Unemployment): {model.objVal}")
    for c in cities:
        for m in months:
            print(f"City {c}, Month {m}: p = {p[c, m].x}")
else:
    print("No optimal solution found.")