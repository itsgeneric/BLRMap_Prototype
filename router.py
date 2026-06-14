from flask import Flask, render_template, jsonify, request
import os
import requests
from dotenv import load_dotenv
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, LineString
import math
import datetime

app = Flask(__name__)
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# ── Road network ──────────────────────────────────────────────────────────────
import numpy as np

GRAPH_CACHE = "bengaluru_graph.graphml"
if os.path.exists(GRAPH_CACHE):
    print("Loading cached road network...")
    G = ox.load_graphml(GRAPH_CACHE)
else:
    print("Downloading Bengaluru road network... (one-time, ~60s)")
    G = ox.graph_from_place("Bengaluru, Karnataka, India", network_type="drive")
    ox.save_graphml(G, GRAPH_CACHE)
    print("Graph cached.")

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

# ── Auto congestion model ─────────────────────────────────────────────────────
# Simulates real-world congestion patterns on main roads without user input.
# Uses time-of-day + road class to compute a congestion_score per edge,
# which is then used to inflate travel_time for the ML/smart route.

# Known high-congestion corridors in Bengaluru (lat, lng, radius_m, peak_factor)
KNOWN_HOTSPOTS = [
    (12.9716, 77.5946, 1200, 2.5),   # MG Road / Cubbon Park junction
    (12.9784, 77.6408, 900,  2.8),   # Silk Board
    (12.9352, 77.6245, 800,  2.6),   # Electronic City toll
    (13.0012, 77.5855, 700,  2.2),   # Hebbal flyover
    (12.9698, 77.7499, 600,  2.0),   # Whitefield main road
    (12.9279, 77.6271, 700,  2.3),   # Hosur Road
    (13.0358, 77.5970, 650,  2.1),   # Yeshwanthpur circle
    (12.9365, 77.5546, 750,  2.4),   # Bannerghatta Road
    (12.9719, 77.6412, 800,  2.5),   # Indiranagar 100ft road
    (13.0207, 77.6445, 600,  1.9),   # Hennur main road
]

def get_time_factor():
    """Returns a multiplier based on current hour — peak hours = higher congestion."""
    hour = datetime.datetime.now().hour
    if 7 <= hour <= 10:    return 1.8   # morning peak
    elif 17 <= hour <= 20: return 2.0   # evening peak
    elif 11 <= hour <= 16: return 1.2   # midday
    elif 21 <= hour <= 23: return 0.9   # night
    else:                  return 0.7   # late night / early morning

def compute_auto_congestion_score(highway, u_data, v_data):
    """
    ML-inspired edge scoring function.
    Combines road class penalty + proximity to known hotspots + time-of-day.
    Returns a weight multiplier (>1 = congested, penalises main roads).
    """
    if isinstance(highway, list):
        highway = highway[0]

    # Base penalty: main roads get penalised so alternatives look better
    road_class_penalty = {
        "motorway":      4.5,
        "trunk":         4.0,
        "primary":       3.5,
        "secondary":     1.0,   # neutral
        "tertiary":      0.5,   # preferred for two-wheelers
        "residential":   0.4,
        "living_street": 0.35,
        "unclassified":  0.45,
        "service":       0.5,
    }.get(highway, 0.8)

    # Proximity to known hotspots → adds extra penalty
    mid_lat = (u_data["y"] + v_data["y"]) / 2
    mid_lng = (u_data["x"] + v_data["x"]) / 2
    hotspot_bonus = 0.0
    for (h_lat, h_lng, h_rad, h_factor) in KNOWN_HOTSPOTS:
        dist_m = _haversine(mid_lat, mid_lng, h_lat, h_lng)
        if dist_m < h_rad:
            proximity_weight = 1 - (dist_m / h_rad)   # 0→1 as you approach centre
            hotspot_bonus += proximity_weight * (h_factor - 1.0)

    time_factor = get_time_factor()
    # Only amplify hotspot bonus during peak hours
    final = road_class_penalty + (hotspot_bonus * time_factor)
    return max(0.3, final)   # never less than 0.3

def _haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ── Assign weights (vectorised) ───────────────────────────────────────────────
print("Computing ML congestion scores for all edges...")

TW_MULT = {
    "motorway": 5.0, "trunk": 3.0, "primary": 3.0,
    "secondary": 1.0, "tertiary": 0.45, "residential": 0.4,
    "living_street": 0.4, "unclassified": 0.5, "service": 0.5,
}
RCP = {
    "motorway": 4.5, "trunk": 4.0, "primary": 3.5,
    "secondary": 1.0, "tertiary": 0.5, "residential": 0.4,
    "living_street": 0.35, "unclassified": 0.45, "service": 0.5,
}

# Collect all edges in one pass
edge_list = [(u, v, k, d) for u, v, k, d in G.edges(data=True, keys=True)]
N = len(edge_list)

mid_lats = np.empty(N); mid_lngs = np.empty(N)
lengths  = np.empty(N); speeds   = np.empty(N)
tw_mults = np.empty(N); rcps     = np.empty(N)

for i, (u, v, k, d) in enumerate(edge_list):
    hw = d.get("highway", "unclassified")
    h  = hw[0] if isinstance(hw, list) else hw
    mid_lats[i] = (G.nodes[u]["y"] + G.nodes[v]["y"]) / 2
    mid_lngs[i] = (G.nodes[u]["x"] + G.nodes[v]["x"]) / 2
    lengths[i]  = d.get("length", 0)
    speeds[i]   = get_speed(hw)
    tw_mults[i] = TW_MULT.get(h, 0.8)
    rcps[i]     = RCP.get(h, 0.8)

# Vectorised haversine: edges (N,) vs hotspots (H,)
hs_lats    = np.array([h[0] for h in KNOWN_HOTSPOTS])
hs_lngs    = np.array([h[1] for h in KNOWN_HOTSPOTS])
hs_rads    = np.array([h[2] for h in KNOWN_HOTSPOTS])
hs_factors = np.array([h[3] for h in KNOWN_HOTSPOTS])

R    = 6371000
phi1 = np.radians(mid_lats[:, None]); phi2 = np.radians(hs_lats[None, :])
dphi = np.radians(hs_lats[None, :] - mid_lats[:, None])
dlam = np.radians(hs_lngs[None, :] - mid_lngs[:, None])
a    = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2)**2
dists = R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))          # (N, H)

prox          = np.where(dists < hs_rads, 1 - dists / hs_rads, 0)
hotspot_bonus = (prox * (hs_factors - 1.0)).sum(axis=1)          # (N,)
ml_scores     = np.maximum(0.3, rcps + hotspot_bonus * get_time_factor())

travel_times = (lengths / 1000) / speeds * 3600
tw_weights   = travel_times * tw_mults
ml_weights   = travel_times * ml_scores

for i, (u, v, k, d) in enumerate(edge_list):
    d["travel_time"] = float(travel_times[i])
    d["tw_weight"]   = float(tw_weights[i])
    d["ml_weight"]   = float(ml_weights[i])

print("Road network + ML weights ready!")

# ── Congestion multipliers ────────────────────────────────────────────────────
CONGESTION_MULTIPLIER = {1: 1.5, 2: 2.5, 3: 4.0, 4: 6.0, 5: 8.0}

def apply_congestion(G_temp, zones, resolved_blocked):
    modified = []
    for zone in zones:
        center      = Point(zone["lng"], zone["lat"])
        radius_deg  = zone["radius"] / 111320
        zone_circle = center.buffer(radius_deg)
        multiplier  = CONGESTION_MULTIPLIER.get(int(zone["level"]), 2.5)

        for u, v, key, data in G_temp.edges(data=True, keys=True):
            u_data = G_temp.nodes[u]
            v_data = G_temp.nodes[v]
            edge_line = LineString([(u_data["x"], u_data["y"]), (v_data["x"], v_data["y"])])
            if zone_circle.intersects(edge_line):
                old = (data["travel_time"], data["tw_weight"], data["ml_weight"])
                data["travel_time"] *= multiplier
                data["tw_weight"]   *= multiplier
                data["ml_weight"]   *= multiplier
                modified.append((u, v, key, old))

    for (u, v, key, action) in resolved_blocked:
        if not G_temp.has_edge(u, v, key):
            continue
        data = G_temp[u][v][key]
        old  = (data["travel_time"], data["tw_weight"], data["ml_weight"])
        mult = 99999 if action == "block" else 5
        data["travel_time"] *= mult
        data["tw_weight"]   *= mult
        data["ml_weight"]   *= mult
        modified.append((u, v, key, old))

    return modified

def reset_congestion(G_temp, modified):
    for u, v, key, old in modified:
        if G_temp.has_edge(u, v, key):
            G_temp[u][v][key]["travel_time"] = old[0]
            G_temp[u][v][key]["tw_weight"]   = old[1]
            G_temp[u][v][key]["ml_weight"]   = old[2]

# ── Route helpers ─────────────────────────────────────────────────────────────
def route_to_coords(G, route):
    return [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in route]

def calc_route_stats(G, route, time_key="travel_time"):
    total_length = total_time = 0
    for u, v in zip(route[:-1], route[1:]):
        ed = G.get_edge_data(u, v)
        if isinstance(ed, dict) and 0 in ed:
            ed = ed[0]
        total_length += ed.get("length", 0)
        total_time   += ed.get(time_key, 0)
    return round(total_length / 1000, 2), round(total_time / 60, 1)

def road_type_breakdown(G, route):
    """Returns % of route on main vs side roads for display."""
    main = side = 0
    for u, v in zip(route[:-1], route[1:]):
        ed = G.get_edge_data(u, v)
        if isinstance(ed, dict) and 0 in ed:
            ed = ed[0]
        hw = ed.get("highway", "unclassified")
        if isinstance(hw, list): hw = hw[0]
        l  = ed.get("length", 0)
        if hw in ("motorway", "trunk", "primary", "secondary"):
            main += l
        else:
            side += l
    total = main + side or 1
    return round(main / total * 100), round(side / total * 100)

# ── Geocoder ──────────────────────────────────────────────────────────────────
def geocode(place_name):
    query = place_name
    if "bengaluru" not in place_name.lower() and "bangalore" not in place_name.lower():
        query = place_name + ", Bengaluru, Karnataka, India"
    url    = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": query, "key": API_KEY, "region": "in",
              "bounds": "12.7343,77.3791|13.1726,77.8826"}
    resp = requests.get(url, params=params).json()
    if resp.get("status") == "OK" and resp.get("results"):
        loc = resp["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    raise ValueError(f'Could not find location: "{place_name}".')

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
    zones         = data.get("zones", [])
    blocked_edges = data.get("blocked_edges", [])
    vehicle       = data.get("vehicle", "scooter")
    realtime      = data.get("realtime", False)

    if not origin_name or not dest_name:
        return jsonify({"error": "Origin and destination are required."}), 400

    try:
        orig_lat, orig_lng = geocode(origin_name)
        dest_lat, dest_lng = geocode(dest_name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    orig_node = ox.distance.nearest_nodes(G, orig_lng, orig_lat)
    dest_node = ox.distance.nearest_nodes(G, dest_lng, dest_lat)

    resolved_blocked = []
    for be in blocked_edges:
        try:
            u, v, key = ox.distance.nearest_edges(G, be["lng"], be["lat"])
            resolved_blocked.append((u, v, key, be.get("action", "slow")))
        except Exception as e:
            print(f"[WARN] Could not resolve edge: {e}")

    modified = apply_congestion(G, zones, resolved_blocked)

    # Real-time: temporarily boost congestion on main roads using current time factor
    rt_modified = []
    if realtime:
        boost = min(get_time_factor() * 1.6, 3.5)
        for u, v, k, d in G.edges(data=True, keys=True):
            hw = d.get("highway", "unclassified")
            h  = hw[0] if isinstance(hw, list) else hw
            if h in ("motorway", "trunk", "primary"):
                old = (d["travel_time"], d["tw_weight"], d["ml_weight"])
                d["travel_time"] *= boost
                d["tw_weight"]   *= boost
                d["ml_weight"]   *= boost * 1.3
                rt_modified.append((u, v, k, old))

    try:
        # Route 1: standard (car — fastest via main roads)
        std_route          = nx.shortest_path(G, orig_node, dest_node, weight="travel_time")
        std_coords         = route_to_coords(G, std_route)
        std_dist, std_time = calc_route_stats(G, std_route, "travel_time")
        std_main, std_side = road_type_breakdown(G, std_route)

        # Route 2: two-wheeler shortcut (prefers side streets)
        tw_route           = nx.shortest_path(G, orig_node, dest_node, weight="tw_weight")
        tw_coords          = route_to_coords(G, tw_route)
        tw_dist, tw_time   = calc_route_stats(G, tw_route, "travel_time")
        tw_main, tw_side   = road_type_breakdown(G, tw_route)

        # Route 3: ML smart (avoids hotspots + time-of-day congestion)
        ml_route           = nx.shortest_path(G, orig_node, dest_node, weight="ml_weight")
        ml_coords          = route_to_coords(G, ml_route)
        ml_dist, ml_time   = calc_route_stats(G, ml_route, "travel_time")
        ml_main, ml_side   = road_type_breakdown(G, ml_route)

        reset_congestion(G, modified)
        reset_congestion(G, rt_modified)

        # Recommend route based on vehicle
        VEHICLE_ROUTE = {
            "scooter": "shortcut",
            "car":     "standard",
            "auto":    "standard",
            "cycle":   "ml",
        }
        recommended = VEHICLE_ROUTE.get(vehicle, "standard")

        return jsonify({
            "standard": {
                "coords": std_coords, "distance": std_dist, "time": std_time,
                "main_pct": std_main, "side_pct": std_side
            },
            "shortcut": {
                "coords": tw_coords,  "distance": tw_dist,  "time": tw_time,
                "main_pct": tw_main,  "side_pct": tw_side
            },
            "ml": {
                "coords": ml_coords,  "distance": ml_dist,  "time": ml_time,
                "main_pct": ml_main,  "side_pct": ml_side
            },
            "recommended": recommended,
            "vehicle":     vehicle,
            "realtime":    realtime,
            "origin":      {"lat": orig_lat, "lng": orig_lng},
            "destination": {"lat": dest_lat, "lng": dest_lng},
            "time_factor": round(get_time_factor(), 2)
        })

    except nx.NetworkXNoPath:
        reset_congestion(G, modified)
        reset_congestion(G, rt_modified)
        return jsonify({"error": "No path found between these locations."}), 400
    except Exception as e:
        reset_congestion(G, modified)
        reset_congestion(G, rt_modified)
        print(f"[ERROR] {e}")
        return jsonify({"error": "Routing failed. Try again."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)