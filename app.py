import requests
import random
import math
import json
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from shapely.geometry import shape, Point

app = Flask(__name__)

# Load Montana Counties for Spatial Counting
try:
    with open('static/montana_counties.geojson') as f:
        COUNTY_DATA = json.load(f)
except Exception as e:
    print(f"Error loading counties: {e}")
    COUNTY_DATA = {"features": []}

# IoT Simulation: Herd with unique IDs
CATTLE_HERD = [
    {"id": f"Tag_{100+i}", "lat": 46.8 + random.uniform(-0.5, 0.5), "lon": -110.3 + random.uniform(-0.5, 0.5)}
    for i in range(35)
]

INFO = {
    "name": "Ali Bazrafkan",
    "phone": "701-729-9088",
    "specialty": "GeoAI & Precision Ranching"
}

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)

@app.route('/')
def index():
    return render_template('index.html', info=INFO)

@app.route('/get_cattle')
def get_cattle():
    county_counts = {}
    for cow in CATTLE_HERD:
        cow['lat'] += random.uniform(-0.002, 0.002)
        cow['lon'] += random.uniform(-0.002, 0.002)
        p = Point(cow['lon'], cow['lat'])
        cow['current_county'] = "Unknown" 
        for feature in COUNTY_DATA.get('features', []):
            poly = shape(feature['geometry'])
            if poly.contains(p):
                name = feature['properties']['name']
                county_counts[name] = county_counts.get(name, 0) + 1
                cow['current_county'] = name
                break

    # NEW: Risk Assessment Logic for warnings
    alerts = []
    for county, count in county_counts.items():
        if count > 10: # Threshold for density warning
            alerts.append({
                "county": county,
                "reason": f"High Density: {count} head detected. Check forage levels."
            })

    return jsonify({
        "cattle": CATTLE_HERD,
        "counts": county_counts,
        "alerts": alerts
    })

@app.route('/analyze_ranch', methods=['POST'])
def analyze_ranch():
    try:
        data = request.json
        lat, lon = data['lat'], data['lon']
        url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": lat, "longitude": lon, "current": "soil_moisture_0_to_1cm", "timezone": "auto"}
        res = requests.get(url, params=params).json()
        
        return jsonify({
            "ndvi": round(random.uniform(0.1, 0.9), 2),
            "soil_moisture": res['current']['soil_moisture_0_to_1cm'],
            "dist_water": 0.45,
            "recommendation": "Maintain",
            "water_loc": {"lat": lat + 0.005, "lon": lon + 0.005}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)