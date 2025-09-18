import json
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Serves the main HTML map page."""
    return render_template('index.html')

@app.route('/api/bus_stops')
def get_bus_stops():
    """
    Reads the local GeoJSON file, removes duplicate stops, and returns the clean data.
    THIS IS MORE RELIABLE FOR YOUR PROJECT.
    """
    try:
        # Make sure your GeoJSON file is named 'export.geojson'
        with open('export.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"FATAL: Could not read or parse export.geojson. Error: {e}")
        return jsonify({"type": "FeatureCollection", "features": []})

    unique_stops = []
    seen_locations = set()

    for feature in data.get('features', []):
        try:
            coords = feature.get('geometry', {}).get('coordinates')
            if not isinstance(coords, list) or len(coords) < 2:
                continue
            
            lon, lat = coords[0], coords[1]
            
            # Group stops by proximity (~110 meters)
            precision = 3 
            location_key = (round(lat, precision), round(lon, precision))

            if location_key not in seen_locations:
                seen_locations.add(location_key)
                unique_stops.append(feature)
        except (AttributeError, KeyError, TypeError, IndexError):
            continue
            
    return jsonify({"type": "FeatureCollection", "features": unique_stops})

if __name__ == '__main__':
    app.run(debug=True)