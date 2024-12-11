import pandas as pd
from PIL import Image
import numpy as np
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import ssl
import certifi
import urllib3
import imageio
from datetime import datetime
import io
from matplotlib.patheffects import withStroke, Stroke

# Disable SSL verification warnings
urllib3.disable_warnings()

# Connecticut bounding box coordinates
CT_BOUNDS = {
    'min_lat': 41.0,
    'max_lat': 42.1,
    'min_lon': -73.7,
    'max_lon': -71.9
}

# Manual coordinates for all Connecticut towns
MANUAL_COORDS = {
    'Avon': (41.8098209, -72.8606541),
    'Hartford': (41.7627144, -72.6743129),
    'New Haven': (41.3082138, -72.9250518),
    'Stamford': (41.0534302, -73.5387341),
    'Waterbury': (41.5581525, -73.0514965),
    'Bridgeport': (41.1670412, -73.2048348),
    'New Britain': (41.6612104, -72.7795419),
    'West Hartford': (41.7620842, -72.7420151),
    'Greenwich': (41.0211238, -73.6284692),
    'Hamden': (41.3959752, -72.8967573),
    'Bristol': (41.6717648, -72.9492703),
    'Meriden': (41.5381535, -72.8070468),
    'Manchester': (41.7759301, -72.5215087),
    'West Haven': (41.2705384, -72.9469711),
    'Fairfield': (41.1408363, -73.2613349),
    'Stratford': (41.1845415, -73.1331563),
    'East Hartford': (41.7634219, -72.6128514),
    'Milford': (41.2306979, -73.0514965),
    'Norwalk': (41.1175966, -73.4083773),
    'Danbury': (41.3948177, -73.4539719),
    'New London': (41.3557106, -72.0995573),
    'Westport': (41.1414728, -73.3578783),
    'Middletown': (41.5623209, -72.6506672),
    'Southington': (41.5964835, -72.8776054),
    'Enfield': (41.9959743, -72.5498352),
    'Torrington': (41.8003181, -73.1211853),
    'Vernon': (41.8659407, -72.4745941),
    'Shelton': (41.3164856, -73.0931625),
    'Trumbull': (41.2428431, -73.2006912),
    'Glastonbury': (41.6934261, -72.5498352),
    'Norwich': (41.5242649, -72.0759116),
    'Windsor': (41.8525969, -72.6437378),
    'Newington': (41.6972893, -72.7298355),
    'Cheshire': (41.4989751, -72.9011993),
    'East Haven': (41.2742557, -72.8684235),
    'Branford': (41.2798565, -72.8137207),
    'Rocky Hill': (41.6612104, -72.6609039),
    'Wallingford': (41.4570329, -72.8234482),
    'Naugatuck': (41.4889984, -73.0514965),
    'Southbury': (41.4789505, -73.2173538),
    'Farmington': (41.7198202, -72.8317642),
    'Newtown': (41.4089642, -73.3037567),
    'South Windsor': (41.8489685, -72.5712585),
    'Ridgefield': (41.2812061, -73.4981766),
    'Simsbury': (41.8756635, -72.8159332),
    'Windham': (41.7023438, -72.1656799),
    'North Haven': (41.3906612, -72.8595734),
    'Watertown': (41.6081409, -73.1211853),
    'Guilford': (41.2889862, -72.6812363),
    'New Canaan': (41.1468266, -73.4942818),
    'Bloomfield': (41.8556709, -72.7306747),
    'Windsor Locks': (41.9253807, -72.6437378),
    'Plainville': (41.6717648, -72.8584747),
    'Seymour': (41.3964844, -73.0759644),
    'Wolcott': (41.6037350, -72.9864502),
    'Berlin': (41.6214847, -72.7456665),
    'Darien': (41.0776412, -73.4678574),
    'East Hampton': (41.5734482, -72.5020599),
    'Wethersfield': (41.7112274, -72.6576233),
    'Monroe': (41.3325958, -73.2073517),
    'Bethel': (41.3712234, -73.4145355),
    'Madison': (41.2795792, -72.5987244),
    'Plainfield': (41.6753922, -71.9214935),
    'Montville': (41.4478683, -72.1442566),
    'Wilton': (41.1956520, -73.4378815),
    'Clinton': (41.2789917, -72.5284576),
    'Ansonia': (41.3434238, -73.0787354),
    'Oxford': (41.4337139, -73.1167297),
    'Groton': (41.3498402, -72.0789719),
    'Stonington': (41.3348083, -71.9067383),
    'Killingly': (41.8136978, -71.8867493),
    'Suffield': (41.9825935, -72.6298523),
    'Cromwell': (41.5945396, -72.6456451),
    'East Lyme': (41.3573074, -72.2319031),
    'Waterford': (41.3542786, -72.1625900),
    'Derby': (41.3206787, -73.0892944),
    'Weston': (41.2014847, -73.3806915),
    'New Fairfield': (41.4645691, -73.4859467),
    'Brooklyn': (41.7881470, -71.9478607),
    'Stafford': (41.9553680, -72.3014832),
    'North Branford': (41.3337250, -72.7745438),
    'Winchester': (41.9214859, -73.0609894),
    'Ellington': (41.9067307, -72.4617767),
    'Griswold': (41.5859375, -71.9923096),
    'Granby': (41.9503784, -72.7920532),
    'Ledyard': (41.4423141, -72.0156555),
    'Portland': (41.5720520, -72.6384430),
    'Thompson': (41.9342384, -71.9034576),
    'Somers': (41.9848061, -72.4464874),
    'East Windsor': (41.9178581, -72.6109543),
    'Canton': (41.8542328, -72.8934326),
    'Old Saybrook': (41.2956657, -72.3764648),
    'Coventry': (41.7692947, -72.3069763),
    'Tolland': (41.8714600, -72.3681641),
    'Woodbridge': (41.3520508, -73.0156555),
    'Bethany': (41.4256592, -72.9953613),
    'Essex': (41.3534546, -72.4142456),
    'Deep River': (41.3767776, -72.4409485),
    'Chester': (41.4034424, -72.4464874),
    'Old Lyme': (41.3159409, -72.3292542),
    'Middlebury': (41.5289917, -73.1278992),
    'Durham': (41.4706650, -72.6812363),
    'Haddam': (41.4748230, -72.5109863),
    'Woodbury': (41.5445557, -73.2073517),
    'East Haddam': (41.5006638, -72.4312592),
    'Prospect': (41.5089722, -72.9772949),
    'Putnam': (41.9145508, -71.9089966),
    'Litchfield': (41.7470551, -73.1889648),
    'Colchester': (41.5753784, -72.3320313),
    'Hebron': (41.6567688, -72.3681641),
    'Lebanon': (41.6342773, -72.2152710),
    'Sherman': (41.5781555, -73.4970703),
    'Marlborough': (41.6309509, -72.4617767),
    'Westbrook': (41.2889862, -72.4464874),
    'Killingworth': (41.3770599, -72.5665283),
    'Burlington': (41.7720718, -72.9494934),
    'Harwinton': (41.7692947, -73.0609894),
    'Salisbury': (41.9831238, -73.4203796),
    'Kent': (41.7248459, -73.4776001),
    'Sharon': (41.8800659, -73.4776001),
    'Washington': (41.6428680, -73.3098755),
    'Roxbury': (41.5489922, -73.2989502),
    'Morris': (41.6867523, -73.2656860),
    'Warren': (41.7331543, -73.3429565),
    'Cornwall': (41.8453407, -73.3262939),
    'Goshen': (41.8397865, -73.2323608),
    'Norfolk': (41.9706421, -73.1945038),
    'Canaan': (42.0261765, -73.3318329),
    'North Canaan': (42.0205917, -73.3373718),
    'Colebrook': (41.9936829, -73.0842743),
    'Bozrah': (41.5534363, -72.1553802),
    'Franklin': (41.6084442, -72.1553802),
    'Sprague': (41.6195412, -72.0734406),
    'Salem': (41.4923019, -72.2819519),
    'Voluntown': (41.5789795, -71.8700867),
    'Sterling': (41.7042465, -71.8228760),
    'Eastford': (41.8981285, -72.0956802),
    'Ashford': (41.8923073, -72.1539993),
    'Pomfret': (41.8981285, -72.0178986),
    'Hampton': (41.7864990, -72.0595551),
    'Chaplin': (41.7981567, -72.1289825),
    'Scotland': (41.6981697, -72.0817566),
    'Canterbury': (41.6981697, -71.9761658),
    'Plainfield': (41.6753922, -71.9214935),
    'Union': (41.9923019, -72.1650696),
    'Andover': (41.7370338, -72.3709412),
    'Columbia': (41.7145538, -72.3014832),
    'Bolton': (41.7631683, -72.4340820),
    'Willington': (41.8842239, -72.2652893),
    'Mansfield': (41.7881470, -72.2291565)
}

def get_town_coordinates(town_name):
    """Get the coordinates for a given town in Connecticut."""
    if town_name in MANUAL_COORDS:
        return MANUAL_COORDS[town_name]
        
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

if __name__ == "__main__":
    create_animation('Optimal Location - 50000000 - 250.csv')
