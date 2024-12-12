import io

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import imageio
from PIL import Image

def create_bar_frame(towns_data, date, previous_data=None):
    """Create a single frame for the bar chart animation."""
    # Get all towns that have a center at any point
    all_active_towns = sorted(towns_data.index[towns_data > 0].tolist())
    
    # Create figure with larger size for better readability
    plt.figure(figsize=(15, 10))
    
    # Prepare data for plotting
    values = [towns_data.get(town, 0) for town in all_active_towns]
    
    # Create horizontal bar chart
    bars = plt.barh(all_active_towns, values)
    
    # Color the bars based on changes
    if previous_data is not None:
        for idx, (town, bar) in enumerate(zip(all_active_towns, bars)):
            current_value = towns_data.get(town, 0)
            previous_value = previous_data.get(town, 0)
            
            if current_value > previous_value:
                # New or increased centers - bright red with glow effect
                bar.set_color('#ff0000')  # Bright red
                plt.axhspan(idx - 0.4, idx + 0.4, color='red', alpha=0.2)  # Glow effect
            else:
                # Normal bars - blue
                bar.set_color('#1f77b4')
    else:
        # First frame - all bars blue
        for bar in bars:
            bar.set_color('#1f77b4')
    
    # Customize the appearance
    plt.title(f'Reemployment Centers by Town - {date.strftime("%B %Y")}', pad=20, fontsize=16)
    plt.xlabel('Number of Centers', fontsize=14)
    plt.ylabel('Town', fontsize=14)
    
    # Add value labels on the bars
    for bar in bars:
        width = bar.get_width()
        if width > 0:  # Only show labels for non-zero values
            plt.text(width, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center', fontsize=12)
    
    # Adjust layout and style
    plt.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    
    # Save to a temporary buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    
    # Read image from buffer
    image = np.array(Image.open(buf))
    
    plt.close()
    buf.close()
    
    return image

def create_animation(data_file, output_file='centers_animation.gif'):
    """Create an animation showing the progression of reemployment centers."""
    # Read the data
    df = pd.read_csv(data_file)
    df.set_index('Unnamed: 0', inplace=True)
    
    # Convert column names to datetime
    df.columns = pd.to_datetime(df.columns)
    
    # Create frames
    frames = []
    previous_data = None
    
    for date in df.columns:
        print(f"Processing {date.strftime('%B %Y')}...")
        towns_data = df[date]
        frame = create_bar_frame(towns_data, date, previous_data)
        frames.append(frame)
        previous_data = towns_data
    
    # Save as GIF
    print(f"Saving animation to {output_file}...")
    imageio.mimsave(output_file, frames, duration=2000, loop=0)  # loop=0 means infinite loop
    print("Animation complete!")