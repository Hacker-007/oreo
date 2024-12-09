import pandas as pd
from PIL import Image
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import matplotlib.pyplot as plt
import ssl
import certifi
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings()

# Connecticut bounding box coordinates
CT_BOUNDS = {
    'min_lat': 41.0,
    'max_lat': 42.1,
    'min_lon': -73.9,
    'max_lon': -71.7
}

def get_town_coordinates(town_name):
    """Get the coordinates for a given town in Connecticut."""
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    geolocator = Nominatim(user_agent="ct_town_mapper", ssl_context=ctx)
    try:
        location = geolocator.geocode(f"{town_name}, Connecticut, USA")
        if location:
            return (location.latitude, location.longitude)
        return None
    except GeocoderTimedOut:
        print(f"Timeout for {town_name}")
        return None

def convert_coords_to_pixels(lat, lon, img_width, img_height):
    """Convert geographic coordinates to image pixels."""
    x = (lon - CT_BOUNDS['min_lon']) / (CT_BOUNDS['max_lon'] - CT_BOUNDS['min_lon']) * img_width
    y = (CT_BOUNDS['max_lat'] - lat) / (CT_BOUNDS['max_lat'] - CT_BOUNDS['min_lat']) * img_height
    return int(x), int(y)

def plot_town_on_map(town_name, output_file="marked_map.png"):
    """Plot a town on the Connecticut map."""
    # Get coordinates for the town
    coordinates = get_town_coordinates(town_name)
    
    if not coordinates:
        print(f"Could not find coordinates for {town_name}")
        return
    
    # Load the map image
    img = Image.open('/Users/jaydenmcnab/Projects/oreo/photos/Connecticut Map.gif')
    img = img.convert('RGBA')  # Convert to RGBA for transparency
    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Display the image
    ax.imshow(img)
    
    # Convert coordinates to pixels
    x, y = convert_coords_to_pixels(coordinates[0], coordinates[1], img.width, img.height)
    
    # Plot the point
    ax.plot(x, y, 'ro', markersize=3)
    
    # Remove axes
    ax.axis('off')
    
    # Save the plot
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0, dpi=300)
    plt.close()
    
    print(f"Map saved as {output_file}")
    print(f"Coordinates for {town_name}: {coordinates}")
    print(f"Pixel position: ({x}, {y})")

if __name__ == "__main__":
    # Test with Hartford
    plot_town_on_map("Avon")
