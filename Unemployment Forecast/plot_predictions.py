import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
sns.set_palette("husl")

# Read the data
df = pd.read_csv('unemployment_with_projections.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Get unique towns
towns = df['Town'].unique()

# Randomly select 6 towns
np.random.seed(42)  # for reproducibility
selected_towns = np.random.choice(towns, size=6, replace=False)

# Create a 2x3 subplot
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.ravel()

# Plot each selected town
for idx, town in enumerate(selected_towns):
    town_data = df[df['Town'] == town].sort_values('Date')
    
    # Plot historical data
    historical = town_data[~town_data['Projected']]
    projected = town_data[town_data['Projected']]
    
    ax = axes[idx]
    
    # Plot historical data
    ax.plot(historical['Date'], historical['Unemployed'], 
            label='Historical', color='blue', linewidth=2)
    
    # Plot projected data with confidence intervals
    ax.plot(projected['Date'], projected['Unemployed'], 
            label='Forecast', color='red', linewidth=2, linestyle='--')
    
    # Plot confidence intervals
    ax.fill_between(projected['Date'],
                   projected['Lower_CI'],
                   projected['Upper_CI'],
                   color='red', alpha=0.2,
                   label='95% Confidence Interval')
    
    # Customize the plot
    ax.set_title(f'{town}', fontsize=12, pad=10)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Unemployed', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels
    ax.tick_params(axis='x', rotation=45)
    
    # Add legend
    ax.legend()

# Adjust layout
plt.tight_layout()
plt.savefig('unemployment_forecasts.png', dpi=300, bbox_inches='tight')
print("Plot saved as 'unemployment_forecasts.png'")
