from flask import Flask, render_template, jsonify, request
import os
import requests
from dotenv import load_dotenv
import osmnx as ox
import networkx as nx

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# ── Road network ──────────────────────────────────────────────────────────────
print("Loading Bengaluru road network... (this takes ~30 seconds on first run)")
G = ox.graph_from_place("Bengaluru, Karnataka, India", network_type="drive")

SPEED_MAP = {
    "motorway":      80,
    "trunk":         60,
    "primary":       45,
    "secondary":     35,
    "tertiary":      25,
    "residential":   20,
    "living_street": 15,
    "unclassified":  20,
    "service":       15,
}

def get_speed(highway):
    if isinstance(highway, list):
        highway = highway[0]
    return SPEED_MAP.get(highway, 30)

# Assign travel_time and tw_weight to every edge
for u, v, data in G.edges(data=True):
    highway = data.get("highway", "unclassified")
    speed   = get_speed(highway)
    length  = data.get("length", 0)

    data["travel_time"] = (length / 1000) / speed * 3600

    if isinstance(highway, list):
        highway = highway[0]

    # ── Updated multipliers: cross roads (tertiary) now strongly preferred ──
    if highway in ("residential", "living_street"):
        multiplier = 0.4       # very strongly preferred
    elif highway in ("tertiary", "tertiary_link"):
        multiplier = 0.45      # cross roads — key fix
    elif highway in ("unclassified", "service"):
        multiplier = 0.5
    elif highway in ("secondary", "secondary_link"):
        multiplier = 1.0       # neutral
    elif highway in ("primary", "primary_link", "trunk"):
        multiplier = 3.0       # strongly avoided
    elif highway in ("motorway", "motorway_link"):
        multiplier = 5.0       # avoid entirely
    else:
        multiplier = 0.8

    data["tw_weight"] = data["travel_time"] * multiplier

print("Road network loaded!")


# ── Geocoder: Google Geocoding API ────────────────────────────────────────────
def geocode(place_name):
    """
    Uses Google Geocoding API — handles apartments, landmarks, colleges,
    and any address that Nominatim can't find.
    Falls back with Bengaluru bias if no result.
    """
    # Add Bengaluru context if not already present
    query = place_name
    if "bengaluru" not in place_name.lower() and "bangalore" not in place_name.lower():
        query = place_name + ", Bengaluru, Karnataka, India"

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": query,
        "key": API_KEY,
        "region": "in",
        "bounds": "12.7343,77.3791|13.1726,77.8826"  # Bengaluru bounding box
    }

    resp = requests.get(url, params=params).json()

    if resp.get("status") == "OK" and resp.get("results"):
        loc = resp["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]

    raise ValueError(f'Could not find location: "{place_name}". Try a more specific name.')


# ── Helpers ───────────────────────────────────────────────────────────────────
def route_to_coords(G, route):
    coords = []
    for node in route:
        d = G.nodes[node]
        coords.append([d["y"], d["x"]])  # y=lat, x=lng
    return coords

def calc_route_stats(G, route, weight_key="travel_time"):
    total_length = 0
    total_time   = 0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G.get_edge_data(u, v)
        if isinstance(edge_data, dict) and 0 in edge_data:
            edge_data = edge_data[0]
        total_length += edge_data.get("length", 0)
        total_time   += edge_data.get(weight_key, 0)
    return round(total_length / 1000, 2), round(total_time / 60, 1)


# ── Flask routes ──────────────────────────────────────────────────────────────
@app.route("/")
def home():
    if not API_KEY:
        return "Error: GOOGLE_MAPS_API_KEY is missing from the .env file.", 500
    return render_template("index.html", api_key=API_KEY)


@app.route("/route", methods=["POST"])
def get_routes():
    data        = request.get_json()
    origin_name = data.get("origin", "").strip()
    dest_name   = data.get("destination", "").strip()

    if not origin_name or not dest_name:
        return jsonify({"error": "Origin and destination are required."}), 400

    try:
        orig_lat, orig_lng = geocode(origin_name)
        dest_lat, dest_lng = geocode(dest_name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    orig_node = ox.distance.nearest_nodes(G, orig_lng, orig_lat)
    dest_node = ox.distance.nearest_nodes(G, dest_lng, dest_lat)

    try:
        standard_route     = nx.shortest_path(G, orig_node, dest_node, weight="travel_time")
        std_coords         = route_to_coords(G, standard_route)
        std_dist, std_time = calc_route_stats(G, standard_route, "travel_time")

        tw_route           = nx.shortest_path(G, orig_node, dest_node, weight="tw_weight")
        tw_coords          = route_to_coords(G, tw_route)
        tw_dist, tw_time   = calc_route_stats(G, tw_route, "travel_time")

    except nx.NetworkXNoPath:
        return jsonify({"error": "No path found between these locations."}), 400

    return jsonify({
        "standard": { "coords": std_coords, "distance": std_dist, "time": std_time },
        "shortcut":  { "coords": tw_coords,  "distance": tw_dist,  "time": tw_time  },
        "origin":      { "lat": orig_lat, "lng": orig_lng },
        "destination": { "lat": dest_lat, "lng": dest_lng }
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)