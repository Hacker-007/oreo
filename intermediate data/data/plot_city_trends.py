import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Read the data
df = pd.read_csv('/Users/jaydenmcnab/Projects/oreo/monthly_averaged_sales.csv')

# Convert date to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Remove unknown entries
df = df[df['Town'] != '***Unknown***']

# Cities to plot
cities = ['New Haven', 'Hartford', 'Stamford', 'Waterbury']

# Create the plot
plt.figure(figsize=(15, 8))
sns.set_style("whitegrid")

# Plot each city with different colors and markers
colors = ['#2ecc71', '#e74c3c', '#3498db', '#f1c40f']
markers = ['o', 's', '^', 'D']

for city, color, marker in zip(cities, colors, markers):
    city_data = df[df['Town'] == city]
    plt.plot(city_data['Date'], 
             city_data['Sale Amount'],
             label=city,
             color=color,
             marker=marker,
             markersize=4,
             markevery=6,  # Show marker every 6 months
             linewidth=2,
             alpha=0.8)

# Customize the plot
plt.title('Connecticut Real Estate Trends by City (2006-2022)', 
          fontsize=16, 
          pad=20)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Average Sale Amount ($)', fontsize=12)

# Format y-axis to show dollar amounts in thousands
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Add legend
plt.legend(title='Cities', 
          title_fontsize=12, 
          fontsize=10, 
          loc='upper left',
          bbox_to_anchor=(1, 1))

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig('connecticut_city_trends.png', 
            dpi=300, 
            bbox_inches='tight')

# Print some statistics
print("\nAverage Sale Amounts by City:")
print("-" * 50)
for city in cities:
    city_data = df[df['Town'] == city]
    print(f"\n{city}:")
    print(f"Current (2022): ${city_data['Sale Amount'].iloc[-1]:,.2f}")
    print(f"Peak: ${city_data['Sale Amount'].max():,.2f}")
    print(f"Lowest: ${city_data['Sale Amount'].min():,.2f}")
    print(f"Overall Average: ${city_data['Sale Amount'].mean():,.2f}")
