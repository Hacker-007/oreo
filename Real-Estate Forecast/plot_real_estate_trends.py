import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style

sns.set_palette("husl")

# Read the data
df = pd.read_csv('real_estate_monthly_from_2006.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Select major cities
cities = ['New Haven', 'Hartford', 'Stamford', 'Bridgeport', 'Waterbury']

# Create the plot
plt.figure(figsize=(15, 8))

# Plot each city
for city in cities:
    city_data = df[df['Town'] == city]
    
    # Calculate 6-month moving average to smooth the line
    city_data['Moving_Avg'] = city_data['Sale Amount'].rolling(window=6).mean()
    
    plt.plot(city_data['Date'], 
            city_data['Moving_Avg'], 
            label=city, 
            linewidth=2,
            alpha=0.8)

# Customize the plot
plt.title('Connecticut Real Estate Trends in Major Cities\n(6-Month Moving Average)', 
          fontsize=14, pad=20)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Average Sale Amount ($)', fontsize=12)

# Format y-axis to show millions
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Rotate x-axis labels
plt.xticks(rotation=45)

# Add grid
plt.grid(True, alpha=0.3)

# Add legend
plt.legend(title='Cities', bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig('real_estate_trends.png', dpi=300, bbox_inches='tight')
print("Plot saved as 'real_estate_trends.png'")

# Print some statistics
print("\nAverage Sale Amount by City:")
city_stats = df.groupby('Town')['Sale Amount'].agg(['mean', 'min', 'max']).round(2)
for city in cities:
    print(f"\n{city}:")
    print(f"  Average: ${city_stats.loc[city, 'mean']:,.2f}")
    print(f"  Minimum: ${city_stats.loc[city, 'min']:,.2f}")
    print(f"  Maximum: ${city_stats.loc[city, 'max']:,.2f}")
