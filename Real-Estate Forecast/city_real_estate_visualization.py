import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns

# Set the style for better visualization
plt.style.use('bmh')

# Read the data
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/data/real_estate_with_projections.csv')

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# List of cities to analyze
cities = ['New Haven', 'Hartford', 'Stamford', 'Waterbury']

# Create a figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Connecticut Real Estate Trends and Projections\nby City', fontsize=16, y=1.02)

# Flatten axes for easier iteration
axes = axes.flatten()

# Colors for historical and projected data
historical_color = '#2ecc71'
projected_color = '#e74c3c'

for idx, city in enumerate(cities):
    city_data = df[df['Town'] == city]
    
    # Separate historical and projected data
    historical = city_data[~city_data['Projected']]
    projected = city_data[city_data['Projected']]
    
    # Plot historical data
    axes[idx].plot(historical['Date'], historical['Sale Amount'], 
                  color=historical_color, label='Historical', linewidth=2)
    
    # Plot projected data with confidence intervals
    axes[idx].plot(projected['Date'], projected['Sale Amount'],
                  color=projected_color, label='Projected', linewidth=2)
    
    # Add confidence intervals for projected data
    axes[idx].fill_between(projected['Date'],
                          projected['Lower_CI'],
                          projected['Upper_CI'],
                          color=projected_color,
                          alpha=0.2)
    
    # Customize each subplot
    axes[idx].set_title(city, fontsize=12, pad=10)
    axes[idx].set_xlabel('Year', fontsize=10)
    axes[idx].set_ylabel('Sale Amount ($)', fontsize=10)
    axes[idx].legend()
    axes[idx].grid(True, alpha=0.3)
    
    # Rotate x-axis labels for better readability
    axes[idx].tick_params(axis='x', rotation=45)
    
    # Format y-axis to show amounts in thousands
    axes[idx].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot
plt.savefig('connecticut_real_estate_trends.png', dpi=300, bbox_inches='tight')
