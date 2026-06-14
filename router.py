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


# ── Option A: Time-Based Traffic Zones ───────────────────────────────────────
#
# Bengaluru's known congestion corridors with their peak patterns.
# Each entry: { name, lat, lng, radius (m), level by slot }
# Slots: morning_peak (7-10AM), day (10AM-5PM), evening_peak (5-9PM), night (9PM-7AM)
#
BENGALURU_CORRIDORS = [
    # Silk Board junction — worst in the city during peaks
    {
        "name": "Silk Board Junction",
        "lat": 12.9172, "lng": 77.6234, "radius": 700,
        "levels": { "morning_peak": 5, "day": 3, "evening_peak": 5, "night": 1 }
    },
    # Hebbal flyover / ORR north
    {
        "name": "Hebbal Flyover",
        "lat": 13.0358, "lng": 77.5972, "radius": 600,
        "levels": { "morning_peak": 5, "day": 2, "evening_peak": 4, "night": 1 }
    },
    # KR Puram bridge
    {
        "name": "KR Puram Bridge",
        "lat": 12.9969, "lng": 77.6956, "radius": 500,
        "levels": { "morning_peak": 4, "day": 2, "evening_peak": 5, "night": 1 }
    },
    # Marathahalli bridge
    {
        "name": "Marathahalli",
        "lat": 12.9565, "lng": 77.7010, "radius": 600,
        "levels": { "morning_peak": 4, "day": 3, "evening_peak": 5, "night": 1 }
    },
    # Tin Factory / Old Madras Rd
    {
        "name": "Tin Factory",
        "lat": 12.9980, "lng": 77.6570, "radius": 400,
        "levels": { "morning_peak": 4, "day": 2, "evening_peak": 4, "night": 1 }
    },
    # MG Road / Brigade Rd CBD
    {
        "name": "MG Road CBD",
        "lat": 12.9757, "lng": 77.6099, "radius": 500,
        "levels": { "morning_peak": 3, "day": 4, "evening_peak": 5, "night": 1 }
    },
    # Jayadeva flyover / Bannerghatta Rd
    {
        "name": "Jayadeva Flyover",
        "lat": 12.9248, "lng": 77.5975, "radius": 500,
        "levels": { "morning_peak": 3, "day": 2, "evening_peak": 4, "night": 1 }
    },
    # Electronic City toll
    {
        "name": "Electronic City Toll",
        "lat": 12.8456, "lng": 77.6603, "radius": 400,
        "levels": { "morning_peak": 5, "day": 2, "evening_peak": 4, "night": 1 }
    },
    # Whitefield / ITPL junction
    {
        "name": "ITPL Junction",
        "lat": 12.9860, "lng": 77.7356, "radius": 500,
        "levels": { "morning_peak": 5, "day": 3, "evening_peak": 4, "night": 1 }
    },
    # Outer Ring Road — Marathahalli to Silk Board stretch
    {
        "name": "ORR Mid Stretch",
        "lat": 12.9370, "lng": 77.6901, "radius": 700,
        "levels": { "morning_peak": 3, "day": 2, "evening_peak": 4, "night": 1 }
    },
    # Yeshwantpur / Tumkur Rd
    {
        "name": "Yeshwantpur Junction",
        "lat": 13.0211, "lng": 77.5541, "radius": 500,
        "levels": { "morning_peak": 4, "day": 2, "evening_peak": 3, "night": 1 }
    },
]

def get_time_slot(hour: int) -> str:
    """Map 0–23 hour to one of 4 traffic slots."""
    if 7 <= hour < 10:
        return "morning_peak"
    elif 10 <= hour < 17:
        return "day"
    elif 17 <= hour < 21:
        return "evening_peak"
    else:
        return "night"

def build_time_zones(hour: int) -> list:
    """Return a list of zone dicts (same format as manual zones) for a given hour."""
    slot = get_time_slot(hour)
    zones = []
    for corridor in BENGALURU_CORRIDORS:
        level = corridor["levels"][slot]
        if level > 1:   # skip level-1 zones — no meaningful penalty
            zones.append({
                "lat":    corridor["lat"],
                "lng":    corridor["lng"],
                "radius": corridor["radius"],
                "level":  level,
                "name":   corridor["name"],
            })
    return zones


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
CONGESTION_MULTIPLIER = {
    1: 1.5,
    2: 2.5,
    3: 4.0,
    4: 6.0,
    5: 8.0,
}

def apply_congestion(G_temp, zones, resolved_blocked):
    modified = []

    # Zone-based congestion
    for zone in zones:
        center      = Point(zone["lng"], zone["lat"])
        radius_deg  = zone["radius"] / 111320
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

    # Click-to-block/slow edges
    for (u, v, key, action) in resolved_blocked:
        if not G_temp.has_edge(u, v, key):
            continue
        data   = G_temp[u][v][key]
        old_tt = data["travel_time"]
        old_tw = data["tw_weight"]

        if action == "block":
            data["travel_time"] = old_tt * 99999
            data["tw_weight"]   = old_tw * 99999
        else:
            data["travel_time"] = old_tt * 5
            data["tw_weight"]   = old_tw * 5

        modified.append((u, v, key, old_tt, old_tw))

    return modified


def reset_congestion(G_temp, modified):
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


@app.route("/time-zones", methods=["GET"])
def time_zones():
    """
    Returns the auto-generated congestion zones for a given hour.
    Frontend calls this to show zone circles on the map for Option A.
    Query param: hour (0–23)
    """
    try:
        hour = int(request.args.get("hour", 8))
        hour = max(0, min(23, hour))
    except (TypeError, ValueError):
        hour = 8

    slot  = get_time_slot(hour)
    zones = build_time_zones(hour)

    return jsonify({
        "hour":  hour,
        "slot":  slot,
        "zones": zones
    })


@app.route("/route", methods=["POST"])
def get_routes():
    data          = request.get_json()
    origin_name   = data.get("origin", "").strip()
    dest_name     = data.get("destination", "").strip()
    manual_zones  = data.get("zones", [])
    blocked_edges = data.get("blocked_edges", [])

    # ── Option A: time-based zones ────────────────────────────────────────
    traffic_mode = data.get("traffic_mode", "manual")   # "manual" | "time_based"
    time_hour    = data.get("time_hour", None)           # 0–23 int, sent when mode=time_based

    if traffic_mode == "time_based" and time_hour is not None:
        try:
            hour = int(time_hour)
        except (TypeError, ValueError):
            hour = 8
        auto_zones = build_time_zones(hour)
        print(f"[Option A] Time slot: {get_time_slot(hour)} — {len(auto_zones)} auto zones applied")
    else:
        auto_zones = []

    # Merge manual + auto zones
    all_zones = manual_zones + auto_zones

    print(f"[DEBUG] total zones={len(all_zones)} (manual={len(manual_zones)}, auto={len(auto_zones)})")
    print(f"[DEBUG] blocked_edges={blocked_edges}")

    if not origin_name or not dest_name:
        return jsonify({"error": "Origin and destination are required."}), 400

    try:
        orig_lat, orig_lng = geocode(origin_name)
        dest_lat, dest_lng = geocode(dest_name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    orig_node = ox.distance.nearest_nodes(G, orig_lng, orig_lat)
    dest_node = ox.distance.nearest_nodes(G, dest_lng, dest_lat)

    # Resolve blocked edges
    resolved_blocked = []
    for be in blocked_edges:
        try:
            u, v, key = ox.distance.nearest_edges(G, be["lng"], be["lat"])
            resolved_blocked.append((u, v, key, be.get("action", "slow")))
        except Exception as e:
            print(f"[DEBUG] Could not resolve edge: {e}")

    # Apply congestion
    modified = apply_congestion(G, all_zones, resolved_blocked)
    print(f"[DEBUG] Modified {len(modified)} edges")

    try:
        standard_route     = nx.shortest_path(G, orig_node, dest_node, weight="travel_time")
        std_coords         = route_to_coords(G, standard_route)
        std_dist, std_time = calc_route_stats(G, standard_route, "travel_time")

        tw_route           = nx.shortest_path(G, orig_node, dest_node, weight="tw_weight")
        tw_coords          = route_to_coords(G, tw_route)
        tw_dist, tw_time   = calc_route_stats(G, tw_route, "travel_time")

        reset_congestion(G, modified)

        return jsonify({
            "standard": { "coords": std_coords, "distance": std_dist, "time": std_time },
            "shortcut":  { "coords": tw_coords,  "distance": tw_dist,  "time": tw_time  },
            "origin":      { "lat": orig_lat, "lng": orig_lng },
            "destination": { "lat": dest_lat, "lng": dest_lng },
            "active_zones": [
                { "lat": z["lat"], "lng": z["lng"], "radius": z["radius"],
                  "level": z["level"], "name": z.get("name", "") }
                for z in all_zones
            ]
        })

    except nx.NetworkXNoPath:
        reset_congestion(G, modified)
        return jsonify({"error": "No path found between these locations."}), 400
    except Exception as e:
        reset_congestion(G, modified)
        print(f"[ERROR] Routing failed: {e}")
        return jsonify({"error": "Routing failed. Try again."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)