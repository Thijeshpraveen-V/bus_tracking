import json
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# --- UNCHANGED ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bus_stops')
def get_bus_stops():
    try:
        with open('export.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "export.geojson not found"}), 404
    # De-duplication logic
    unique_stops, seen_locations = [], set()
    for feature in data.get('features', []):
        try:
            coords = feature.get('geometry', {}).get('coordinates')
            if not isinstance(coords, list) or len(coords) < 2: continue
            lon, lat = coords[0], coords[1]
            location_key = (round(lat, 3), round(lon, 3))
            if location_key not in seen_locations:
                seen_locations.add(location_key)
                unique_stops.append(feature)
        except Exception: continue
    return jsonify({"type": "FeatureCollection", "features": unique_stops})

# --- NEW: API ROUTE TO GET A SPECIFIC BUS ROUTE ---
@app.route('/api/route/<route_number>')
def get_route_data(route_number):
    """
    Finds and serves the GeoJSON data for a specific bus route.
    """
    # Sanitize the input to prevent directory traversal attacks
    safe_route_number = "".join(c for c in route_number if c.isalnum() or c in ('-', '_')).upper()
    
    filepath = os.path.join('route_data', f'{safe_route_number}.json')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": f"Route data for '{safe_route_number}' not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)