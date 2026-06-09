from flask import Flask, render_template, jsonify, request
import os
import requests
from dotenv import load_dotenv
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, LineString
import copy

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

    if highway in ("residential", "living_street"):
        multiplier = 0.4
    elif highway in ("tertiary", "tertiary_link"):
        multiplier = 0.45
    elif highway in ("unclassified", "service"):
        multiplier = 0.5
    elif highway in ("secondary", "secondary_link"):
        multiplier = 1.0
    elif highway in ("primary", "primary_link", "trunk"):
        multiplier = 3.0
    elif highway in ("motorway", "motorway_link"):
        multiplier = 5.0
    else:
        multiplier = 0.8

    data["tw_weight"] = data["travel_time"] * multiplier

print("Road network loaded!")


# ── Google Geocoder ───────────────────────────────────────────────────────────
def geocode(place_name):
    query = place_name
    if "bengaluru" not in place_name.lower() and "bangalore" not in place_name.lower():
        query = place_name + ", Bengaluru, Karnataka, India"

    url    = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": query,
        "key":     API_KEY,
        "region":  "in",
        "bounds":  "12.7343,77.3791|13.1726,77.8826"
    }
    resp = requests.get(url, params=params).json()
    if resp.get("status") == "OK" and resp.get("results"):
        loc = resp["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    raise ValueError(f'Could not find location: "{place_name}".')


# ── Congestion helpers ────────────────────────────────────────────────────────

# Congestion level → travel time multiplier
CONGESTION_MULTIPLIER = {
    1: 1.5,
    2: 2.5,
    3: 4.0,
    4: 6.0,
    5: 8.0,
}

def apply_congestion(G_temp, zones, blocked_edges):
    """
    Mutates G_temp edges in-place based on:
      zones        — list of {lat, lng, radius (m), level 1-5}
      blocked_edges — list of {lat, lng, action: 'block'|'slow'}
    Returns set of edges that were modified (for reset).
    """
    modified = []

    # ── Zone-based congestion ─────────────────────────────────────────────
    for zone in zones:
        center     = Point(zone["lng"], zone["lat"])   # shapely Point (lng, lat)
        radius_deg = zone["radius"] / 111320           # metres → degrees (approx)
        zone_circle = center.buffer(radius_deg)
        multiplier  = CONGESTION_MULTIPLIER.get(int(zone["level"]), 2.5)

        for u, v, key, data in G_temp.edges(data=True, keys=True):
            u_data = G_temp.nodes[u]
            v_data = G_temp.nodes[v]
            edge_line = LineString([
                (u_data["x"], u_data["y"]),
                (v_data["x"], v_data["y"])
            ])
            if zone_circle.intersects(edge_line):
                old_tt = data["travel_time"]
                old_tw = data["tw_weight"]
                data["travel_time"] = old_tt * multiplier
                data["tw_weight"]   = old_tw * multiplier
                modified.append((u, v, key, old_tt, old_tw))

    # ── Click-to-block/slow edges ─────────────────────────────────────────
    for be in blocked_edges:
        click_point = Point(be["lng"], be["lat"])
        action      = be.get("action", "slow")

        # Find nearest edge to click point
        nearest_u, nearest_v, nearest_key = None, None, None
        min_dist = float("inf")

        for u, v, key, data in G_temp.edges(data=True, keys=True):
            u_data = G_temp.nodes[u]
            v_data = G_temp.nodes[v]
            edge_line = LineString([
                (u_data["x"], u_data["y"]),
                (v_data["x"], v_data["y"])
            ])
            dist = click_point.distance(edge_line)
            if dist < min_dist:
                min_dist     = dist
                nearest_u    = u
                nearest_v    = v
                nearest_key  = key

        if nearest_u is not None:
            data = G_temp[nearest_u][nearest_v][nearest_key]
            old_tt = data["travel_time"]
            old_tw = data["tw_weight"]

            if action == "block":
                # Effectively infinite cost
                data["travel_time"] = old_tt * 99999
                data["tw_weight"]   = old_tw * 99999
            else:
                # Slow — 5x penalty
                data["travel_time"] = old_tt * 5
                data["tw_weight"]   = old_tw * 5

            modified.append((nearest_u, nearest_v, nearest_key, old_tt, old_tw))

    return modified


def reset_congestion(G_temp, modified):
    """Restore original weights after routing."""
    for u, v, key, old_tt, old_tw in modified:
        if G_temp.has_edge(u, v, key):
            G_temp[u][v][key]["travel_time"] = old_tt
            G_temp[u][v][key]["tw_weight"]   = old_tw


# ── Route helpers ─────────────────────────────────────────────────────────────
def route_to_coords(G, route):
    return [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in route]

def calc_route_stats(G, route, weight_key="travel_time"):
    total_length = total_time = 0
    for u, v in zip(route[:-1], route[1:]):
        ed = G.get_edge_data(u, v)
        if isinstance(ed, dict) and 0 in ed:
            ed = ed[0]
        total_length += ed.get("length", 0)
        total_time   += ed.get(weight_key, 0)
    return round(total_length / 1000, 2), round(total_time / 60, 1)


# ── Flask routes ──────────────────────────────────────────────────────────────
@app.route("/")
def home():
    if not API_KEY:
        return "Error: GOOGLE_MAPS_API_KEY is missing.", 500
    return render_template("index.html", api_key=API_KEY)


@app.route("/route", methods=["POST"])
def get_routes():
    data          = request.get_json()
    origin_name   = data.get("origin", "").strip()
    dest_name     = data.get("destination", "").strip()
    zones         = data.get("zones", [])          # list of zone objects
    blocked_edges = data.get("blocked_edges", [])  # list of blocked road objects

    if not origin_name or not dest_name:
        return jsonify({"error": "Origin and destination are required."}), 400

    try:
        orig_lat, orig_lng = geocode(origin_name)
        dest_lat, dest_lng = geocode(dest_name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    orig_node = ox.distance.nearest_nodes(G, orig_lng, orig_lat)
    dest_node = ox.distance.nearest_nodes(G, dest_lng, dest_lat)

    # Apply congestion to shared graph, route, then reset immediately
    modified = apply_congestion(G, zones, blocked_edges)

    try:
        standard_route     = nx.shortest_path(G, orig_node, dest_node, weight="travel_time")
        std_coords         = route_to_coords(G, standard_route)
        std_dist, std_time = calc_route_stats(G, standard_route, "travel_time")

        tw_route           = nx.shortest_path(G, orig_node, dest_node, weight="tw_weight")
        tw_coords          = route_to_coords(G, tw_route)
        tw_dist, tw_time   = calc_route_stats(G, tw_route, "travel_time")

    except nx.NetworkXNoPath:
        reset_congestion(G, modified)
        return jsonify({"error": "No path found between these locations."}), 400
    finally:
        reset_congestion(G, modified)

    return jsonify({
        "standard": { "coords": std_coords, "distance": std_dist, "time": std_time },
        "shortcut":  { "coords": tw_coords,  "distance": tw_dist,  "time": tw_time  },
        "origin":      { "lat": orig_lat, "lng": orig_lng },
        "destination": { "lat": dest_lat, "lng": dest_lng }
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)