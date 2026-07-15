from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import osmnx as ox
import networkx as nx
import os
import httpx
import asyncio
from dotenv import load_dotenv
import math

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
# Routes API (live traffic) uses the Maps key, falls back to the Places key if unset
ROUTES_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or GOOGLE_KEY
ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INNER_ROAD_TYPES = {
    'residential', 'living_street', 'unclassified', 'service',
    'tertiary', 'tertiary_link'
}

TWO_WHEELER_ROAD_PENALTIES = {
    'motorway': 4.0,
    'motorway_link': 3.0,
    'trunk': 3.0,
    'trunk_link': 2.5,
    'primary': 2.2,
    'primary_link': 2.0,
    'secondary': 1.5,
    'secondary_link': 1.4,
    'tertiary': 1.15,
    'tertiary_link': 1.1,
    'residential': 1.0,
    'living_street': 0.95,
    'unclassified': 1.0,
    'service': 0.9,
    'road': 1.1,
}

DEFAULT_ROUTE_SPLIT_FRACTIONS = (0.33, 0.5, 0.67)

MAIN_ROAD_TYPES = {
    'motorway', 'motorway_link', 'trunk', 'trunk_link',
    'primary', 'primary_link', 'secondary', 'secondary_link'
}

INNER_ROAD_BIASED_TYPES = {
    'tertiary', 'tertiary_link', 'residential', 'living_street',
    'unclassified', 'service', 'road'
}

def _is_inner(data):
    hw = data.get('highway', 'unclassified')
    if isinstance(hw, list):
        hw = hw[0]
    return hw in INNER_ROAD_TYPES

def haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def _bearing_deg(lat1, lng1, lat2, lng2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lng2 - lng1)
    x = math.sin(dlam) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def _destination_point(lat, lng, bearing_deg, distance_m):
    R = 6371000.0
    phi1 = math.radians(lat)
    lam1 = math.radians(lng)
    theta = math.radians(bearing_deg)
    ang_dist = distance_m / R
    phi2 = math.asin(
        math.sin(phi1) * math.cos(ang_dist) + math.cos(phi1) * math.sin(ang_dist) * math.cos(theta)
    )
    lam2 = lam1 + math.atan2(
        math.sin(theta) * math.sin(ang_dist) * math.cos(phi1),
        math.cos(ang_dist) - math.sin(phi1) * math.sin(phi2)
    )
    return math.degrees(phi2), math.degrees(lam2)

def interpolate_waypoints(lat1, lng1, lat2, lng2, segment_km):
    total_km = haversine_m(lat1, lng1, lat2, lng2) / 1000
    if total_km <= segment_km:
        return [(lat1, lng1), (lat2, lng2)]
    n = max(1, round(total_km / segment_km))
    return [(lat1 + i/n*(lat2-lat1), lng1 + i/n*(lng2-lng1)) for i in range(n+1)]

def decode_polyline(encoded):
    coords = []
    index = 0
    lat = lng = 0
    while index < len(encoded):
        b = shift = result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        lat += (~(result >> 1) if result & 1 else result >> 1)
        b = shift = result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        lng += (~(result >> 1) if result & 1 else result >> 1)
        coords.append([lat / 1e5, lng / 1e5])
    return coords

def astar_on_graph(graph, start_node, end_node):
    def heuristic(a, b):
        return haversine_m(graph.nodes[a]['y'], graph.nodes[a]['x'],
                           graph.nodes[b]['y'], graph.nodes[b]['x'])
    def cost(u, v, edge_data):
        if 'length' in edge_data:
            return float(edge_data['length'])
        return min(float(d.get('length', 1.0)) for d in edge_data.values())
    return nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=cost)

def _edge_highway_type(edge_data):
    hw = edge_data.get('highway', 'unclassified')
    if isinstance(hw, list):
        hw = hw[0]
    return hw

def build_two_wheeler_penalties(
    main_road_penalty=1.0,
    inner_road_multiplier=1.0,
    service_multiplier=1.0,
    roundabout_multiplier=1.0,
):
    penalties = dict(TWO_WHEELER_ROAD_PENALTIES)
    for road_type in MAIN_ROAD_TYPES:
        penalties[road_type] = penalties.get(road_type, 1.25) * main_road_penalty
    for road_type in INNER_ROAD_BIASED_TYPES:
        penalties[road_type] = penalties.get(road_type, 1.0) * inner_road_multiplier
    penalties['service'] = penalties.get('service', 1.0) * service_multiplier
    penalties['_roundabout_multiplier'] = roundabout_multiplier
    return penalties

def two_wheeler_edge_cost(edge_data, penalties=None):
    length = float(edge_data.get('length', 1.0))
    highway = _edge_highway_type(edge_data)
    penalty_map = penalties or TWO_WHEELER_ROAD_PENALTIES
    penalty = penalty_map.get(highway, 1.25)

    if edge_data.get('junction') == 'roundabout':
        penalty *= penalty_map.get('_roundabout_multiplier', 0.95)

    return length * penalty

def two_wheeler_astar(graph, start_node, end_node, penalties=None):
    def heuristic(a, b):
        return haversine_m(graph.nodes[a]['y'], graph.nodes[a]['x'],
                           graph.nodes[b]['y'], graph.nodes[b]['x'])

    def cost(u, v, edge_data):
        if 'length' in edge_data:
            return two_wheeler_edge_cost(edge_data, penalties=penalties)
        return min(two_wheeler_edge_cost(d, penalties=penalties) for d in edge_data.values())

    return nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=cost)

def path_cost(graph, route, cost_fn=two_wheeler_edge_cost, penalties=None):
    total = 0.0
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        if b in graph[a]:
            total += min(cost_fn(d, penalties=penalties) for d in graph[a][b].values())
    return total

def _dedupe_nodes(nodes):
    deduped = []
    for node in nodes:
        if not deduped or node != deduped[-1]:
            deduped.append(node)
    return deduped

def _line_split_points(from_lat, from_lng, to_lat, to_lng, fractions):
    return [
        (
            from_lat + (to_lat - from_lat) * fraction,
            from_lng + (to_lng - from_lng) * fraction,
        )
        for fraction in fractions
    ]

def _offset_split_points(from_lat, from_lng, to_lat, to_lng, fractions, offsets_m=(150, 300)):
    """
    Generate split candidate points offset perpendicular to the direct line,
    on both sides, at a couple of distances. Plain points on the straight
    line almost always snap to whatever node is already on the optimal
    corridor (Bengaluru's grid is dense), which just reproduces the direct
    route. Offsetting sideways is what actually lands on a parallel inner
    road, giving the algorithm a genuinely different candidate to score.
    """
    bearing = _bearing_deg(from_lat, from_lng, to_lat, to_lng)
    points = []
    for fraction in fractions:
        base_lat, base_lng = _line_split_points(from_lat, from_lng, to_lat, to_lng, [fraction])[0]
        for offset_m in offsets_m:
            for side_bearing in (bearing + 90, bearing - 90):
                pt_lat, pt_lng = _destination_point(base_lat, base_lng, side_bearing, offset_m)
                points.append((pt_lat, pt_lng))
    return points

def _derive_split_fractions(straight_line_km, segment_km):
    if straight_line_km <= segment_km:
        return ()

    segment_km = max(segment_km, 0.5)
    segment_count = max(2, math.ceil(straight_line_km / segment_km))
    return tuple(i / segment_count for i in range(1, segment_count))

def _route_cumulative_lengths(graph, route):
    cumulative = [0.0]
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        if b in graph[a]:
            best = min(graph[a][b].values(), key=lambda d: float(d.get('length', 1.0)))
            cumulative.append(cumulative[-1] + float(best.get('length', 0)))
        else:
            cumulative.append(cumulative[-1])
    return cumulative

def _graph_aware_split_nodes(graph, route, split_fractions):
    if len(route) < 3:
        return []

    cumulative = _route_cumulative_lengths(graph, route)
    total = cumulative[-1]
    if total <= 0:
        return []

    candidate_nodes = []
    for fraction in split_fractions:
        target = total * fraction
        closest_index = min(range(len(cumulative)), key=lambda i: abs(cumulative[i] - target))
        window_start = max(0, closest_index - 2)
        window_end = min(len(route), closest_index + 3)
        window = route[window_start:window_end]

        junction_nodes = [node for node in window if graph.degree(node) >= 3]
        ordered_window = list(dict.fromkeys(junction_nodes + [route[closest_index]] + window))
        candidate_nodes.extend(ordered_window[:3])

    return _dedupe_nodes(candidate_nodes)

DETOUR_TOLERANCE = 1.20  # reject split candidates more than 20% longer than direct

def build_split_route_candidates(graph, from_lat, from_lng, to_lat, to_lng, split_fractions=DEFAULT_ROUTE_SPLIT_FRACTIONS, penalties=None):
    direct_start = ox.nearest_nodes(graph, from_lng, from_lat)
    direct_end = ox.nearest_nodes(graph, to_lng, to_lat)

    candidates = []

    try:
        direct_route = two_wheeler_astar(graph, direct_start, direct_end, penalties=penalties)
        candidates.append({
            'strategy': 'direct',
            'nodes': direct_route,
            'cost': path_cost(graph, direct_route, penalties=penalties),
        })
    except Exception as exc:
        candidates.append({
            'strategy': 'direct',
            'nodes': [],
            'cost': float('inf'),
            'error': str(exc),
        })

    # distance baseline for sanity-checking split candidates
    direct_length = None
    if candidates and candidates[0]['nodes']:
        direct_length = route_length_m(graph, candidates[0]['nodes'])

    graph_aware_nodes = []
    if candidates and candidates[0]['nodes']:
        graph_aware_nodes = _graph_aware_split_nodes(graph, candidates[0]['nodes'], split_fractions)

    # Offset points (parallel inner roads) are what actually produce a
    # genuinely different candidate — see _offset_split_points().
    offset_points = _offset_split_points(from_lat, from_lng, to_lat, to_lng, split_fractions)
    fallback_nodes = [ox.nearest_nodes(graph, lng, lat) for lat, lng in offset_points]

    split_nodes = _dedupe_nodes(graph_aware_nodes + fallback_nodes)

    seen_paths = set()
    if candidates and candidates[0]['nodes']:
        seen_paths.add(tuple(candidates[0]['nodes']))

    for split_node in split_nodes:
        split_fraction = None
        if candidates and candidates[0]['nodes'] and split_node in candidates[0]['nodes']:
            split_fraction = round(candidates[0]['nodes'].index(split_node) / max(1, len(candidates[0]['nodes']) - 1), 2)

        try:
            first_leg = two_wheeler_astar(graph, direct_start, split_node, penalties=penalties)
            second_leg = two_wheeler_astar(graph, split_node, direct_end, penalties=penalties)
            stitched = _dedupe_nodes(first_leg + second_leg[1:])

            # Skip candidates that turned out identical (or near-identical)
            # to the direct route or to another candidate already found —
            # these are redundant, not real alternatives, and just burn
            # extra traffic-API calls without giving the user any real choice.
            stitched_key = tuple(stitched)
            if stitched_key in seen_paths:
                continue
            seen_paths.add(stitched_key)

            # NEW: reject geometrically bad stitches (zigzags / pointless detours)
            if direct_length:
                stitched_length = route_length_m(graph, stitched)
                if stitched_length > direct_length * DETOUR_TOLERANCE:
                    continue

            candidates.append({
                'strategy': 'graph_split' if split_fraction is not None else 'line_split',
                'nodes': stitched,
                'split_fraction': split_fraction,
                'split_node': split_node,
                'cost': path_cost(graph, stitched, penalties=penalties),
            })
        except Exception as exc:
            candidates.append({
                'strategy': 'graph_split' if split_fraction is not None else 'line_split',
                'nodes': [],
                'split_fraction': split_fraction,
                'split_node': split_node,
                'cost': float('inf'),
                'error': str(exc),
            })

    candidates.sort(key=lambda item: item['cost'])
    return candidates

def route_nodes_to_coords(graph, route):
    """
    Build the coordinate path for the frontend, following each edge's real
    road geometry (when OSM provides it) instead of drawing a straight line
    from node to node — straight node-to-node lines are what was causing
    the drawn route to cut across buildings on curved/long roads.
    """
    if not route:
        return []
    coords = [[graph.nodes[route[0]]['y'], graph.nodes[route[0]]['x']]]
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        if b not in graph[a]:
            coords.append([graph.nodes[b]['y'], graph.nodes[b]['x']])
            continue
        edge_data = min(graph[a][b].values(), key=lambda d: float(d.get('length', 1.0)))
        geom = edge_data.get('geometry')
        if geom is not None and hasattr(geom, 'coords'):
            pts = [[lat, lng] for lng, lat in geom.coords]
            # geometry may run start->end or end->start depending on OSM way direction
            start_pt = [graph.nodes[a]['y'], graph.nodes[a]['x']]
            if pts and haversine_m(pts[0][0], pts[0][1], start_pt[0], start_pt[1]) > \
                       haversine_m(pts[-1][0], pts[-1][1], start_pt[0], start_pt[1]):
                pts = pts[::-1]
            coords.extend(pts[1:] if pts and pts[0] == coords[-1] else pts)
        else:
            coords.append([graph.nodes[b]['y'], graph.nodes[b]['x']])
    return coords

def route_length_m(graph, route):
    return calc_route_distance(graph, route)

async def fetch_traffic_duration(client, from_lat, from_lng, to_lat, to_lng, waypoint=None):
    """
    Ask Google Routes API for the REAL, live, traffic-aware travel time
    (TWO_WHEELER mode) for a given path. If `waypoint` is given, the route is
    forced through that point — this is how we get a real duration for one
    of our own split/inner-road candidates instead of only the direct route.
    Returns seconds (float) or None if the call fails / key missing.
    """
    if not ROUTES_KEY:
        return None

    body = {
        "origin": {"location": {"latLng": {"latitude": from_lat, "longitude": from_lng}}},
        "destination": {"location": {"latLng": {"latitude": to_lat, "longitude": to_lng}}},
        "travelMode": "TWO_WHEELER",
        "routingPreference": "TRAFFIC_AWARE",
    }
    if waypoint is not None:
        wp_lat, wp_lng = waypoint
        body["intermediates"] = [{"location": {"latLng": {"latitude": wp_lat, "longitude": wp_lng}}}]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": ROUTES_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
    }
    try:
        res = await client.post(ROUTES_API_URL, json=body, headers=headers, timeout=8.0)
        data = res.json()
        routes = data.get("routes")
        if not routes:
            print(f"  Routes API returned no route: {data}")
            return None
        duration_str = routes[0].get("duration", "")
        if not duration_str:
            return None
        return float(duration_str.rstrip("s"))
    except Exception as exc:
        print(f"  Routes API call failed: {exc}")
        return None

def calc_route_distance(graph, route):
    total = 0.0
    for i in range(len(route) - 1):
        a, b = route[i], route[i+1]
        if b in graph[a]:
            best = min(graph[a][b].values(), key=lambda d: float(d.get('length', 1.0)))
            total += float(best.get('length', 0))
    return total

# ── Load graphs ───────────────────────────────────────────
print("Loading Bengaluru road network...")
G = ox.load_graphml("bengaluru_roads_full.graphml")
for u, v, key, data in G.edges(keys=True, data=True):
    data['length'] = float(data.get('length', 1.0))
print(f"Loaded graph with {len(G.nodes):,} nodes and {len(G.edges):,} edges")

# Remove suspiciously long inner road edges (likely OSM errors / phantom roads)
MAX_EDGE_LENGTH = {
    'residential':   250,
    'living_street': 200,
    'service':       200,
    'unclassified':  400,
    'tertiary':      600,
}
edges_to_remove = []
for u, v, k, data in G.edges(keys=True, data=True):
    hw = data.get('highway', '')
    if isinstance(hw, list):
        hw = hw[0]
    max_len = MAX_EDGE_LENGTH.get(hw)
    if max_len and float(data.get('length', 0)) > max_len:
        edges_to_remove.append((u, v, k))
G.remove_edges_from(edges_to_remove)
print(f"Removed {len(edges_to_remove)} suspicious long edges")

# Keep only the largest strongly connected component. Routing into a node that
# sits in a small disconnected pocket is exactly what caused routes to "get
# stuck" and never reach the destination, especially heading south where
# OSM data has gaps/one-way mismatches that split the graph.
before_nodes, before_edges = len(G.nodes), len(G.edges)
largest_cc_nodes = max(nx.strongly_connected_components(G), key=len)
G = G.subgraph(largest_cc_nodes).copy()
print(f"Kept largest connected component: {len(G.nodes):,}/{before_nodes:,} nodes, "
      f"{len(G.edges):,}/{before_edges:,} edges")

print("Building inner road subgraph...")
G_inner = G.edge_subgraph(
    [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if _is_inner(d)]
).copy()
print(f"Inner road subgraph: {len(G_inner.nodes):,} nodes, {len(G_inner.edges):,} edges")

# ── Endpoints ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Bengaluru Router API"}

@app.get("/search")
async def search_places(q: str):
    # Use Nominatim (free, no API key) when Google key is not available
    if not GOOGLE_KEY:
        return await _search_nominatim(q)

    params = {
        "input": q, "key": GOOGLE_KEY,
        "components": "country:in",
        "location": "12.9716,77.5946",
        "radius": 50000, "language": "en"
    }
    async with httpx.AsyncClient() as client:
        res  = await client.get("https://maps.googleapis.com/maps/api/place/autocomplete/json", params=params)
        data = res.json()

    results = []
    for prediction in data.get("predictions", [])[:5]:
        async with httpx.AsyncClient() as c2:
            det = await c2.get("https://maps.googleapis.com/maps/api/place/details/json", params={
                "place_id": prediction["place_id"], "key": GOOGLE_KEY,
                "fields": "name,formatted_address,geometry"
            })
            details = det.json().get("result", {})
        if "geometry" in details:
            results.append({
                "name":    details.get("name", prediction["structured_formatting"]["main_text"]),
                "address": details.get("formatted_address", ""),
                "lat":     details["geometry"]["location"]["lat"],
                "lng":     details["geometry"]["location"]["lng"],
            })
    return {"results": results}

async def _search_nominatim(q: str):
    """Fallback search using OpenStreetMap Nominatim (no API key needed)."""
    search_query = q.strip()
    # Append Bengaluru if not already mentioned to bias results locally
    q_lower = search_query.lower()
    if "bengaluru" not in q_lower and "bangalore" not in q_lower and "blr" not in q_lower:
        search_query = f"{search_query}, Bengaluru"

    params = {
        "q": search_query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "viewbox": "77.4,13.1,77.8,12.8",  # Bengaluru bounding box
        "bounded": 0,  # prefer but don't restrict to viewbox
    }
    headers = {"User-Agent": "BLR-Router/1.0"}
    results = []
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params=params, headers=headers, timeout=10.0,
            )
            data = res.json()

        for place in data:
            lat = float(place.get("lat", 0))
            lng = float(place.get("lon", 0))
            name = place.get("display_name", "").split(",")[0]
            address = place.get("display_name", "")
            results.append({
                "name": name,
                "address": address,
                "lat": lat,
                "lng": lng,
            })
    except Exception as e:
        print(f"Nominatim search error: {e}")

    return {"results": results}

@app.get("/route")
def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    print(f"Shortest: ({from_lat},{from_lng}) -> ({to_lat},{to_lng})")
    try:
        start = ox.nearest_nodes(G, from_lng, from_lat)
        end   = ox.nearest_nodes(G, to_lng, to_lat)
        route = astar_on_graph(G, start, end)
        coords = route_nodes_to_coords(G, route)
        dist = calc_route_distance(G, route)
        print(f"  Done: {dist/1000:.2f}km")
        return {"status": "success", "path": coords,
                "distance_meters": round(dist, 2), "distance_km": round(dist/1000, 2)}
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/inner-route")
def get_inner_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float, segment_km: float = 1.0):
    print(f"Inner route: ({from_lat},{from_lng}) -> ({to_lat},{to_lng}), seg={segment_km}km")
    try:
        waypoints = interpolate_waypoints(from_lat, from_lng, to_lat, to_lng, segment_km)
        print(f"  {len(waypoints)} waypoints")

        nodes = [ox.nearest_nodes(G_inner, lng, lat) for lat, lng in waypoints]

        deduped = [nodes[0]]
        for n in nodes[1:]:
            if n != deduped[-1]:
                deduped.append(n)
        nodes = deduped
        print(f"  {len(nodes)} unique inner nodes")

        full_route = []
        total_dist = 0.0

        for i in range(len(nodes) - 1):
            u, v = nodes[i], nodes[i+1]
            try:
                seg = astar_on_graph(G_inner, u, v)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                print(f"  No inner path {u}->{v}, falling back to full graph")
                try:
                    seg = astar_on_graph(G, u, v)
                except Exception:
                    print(f"  Skipping segment")
                    continue

            if full_route and seg[0] == full_route[-1]:
                seg = seg[1:]
            full_route.extend(seg)

            for j in range(len(seg) - 1):
                a, b = seg[j], seg[j+1]
                use = G_inner if (a in G_inner and b in G_inner[a]) else G
                if b in use[a]:
                    best = min(use[a][b].values(), key=lambda d: float(d.get('length', 1.0)))
                    total_dist += float(best.get('length', 0))

        if len(full_route) < 2:
            return {"status": "error", "message": "Could not find inner road path."}

        coords = route_nodes_to_coords(G, full_route)
        print(f"  Done: {len(coords)} pts, {total_dist/1000:.2f}km")
        return {
            "status": "success", "path": coords,
            "distance_meters": round(total_dist, 2),
            "distance_km": round(total_dist/1000, 2),
            "waypoints_used": len(nodes),
            "segment_km": segment_km,
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/traffic-route")
async def traffic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    print(f"Traffic route: ({from_lat},{from_lng}) -> ({to_lat},{to_lng})")
    params = {
        "origin": f"{from_lat},{from_lng}",
        "destination": f"{to_lat},{to_lng}",
        "departure_time": "now",
        "alternatives": "true",
        "mode": "driving",
        "key": GOOGLE_KEY,
    }
    async with httpx.AsyncClient() as client:
        res  = await client.get("https://maps.googleapis.com/maps/api/directions/json", params=params)
        data = res.json()

    if data.get("status") != "OK":
        return {"status": "error", "message": data.get("status")}

    routes = []
    for r in data["routes"]:
        leg = r["legs"][0]
        routes.append({
            "path":               decode_polyline(r["overview_polyline"]["points"]),
            "distance_text":      leg["distance"]["text"],
            "distance_m":         leg["distance"]["value"],
            "duration_text":      leg["duration"]["text"],
            "duration_traffic":   leg.get("duration_in_traffic", {}).get("text", leg["duration"]["text"]),
            "duration_traffic_s": leg.get("duration_in_traffic", {}).get("value", leg["duration"]["value"]),
            "summary":            r.get("summary", ""),
        })

    routes.sort(key=lambda x: x["duration_traffic_s"])
    return {"status": "success", "routes": routes, "fastest": routes[0]}

@app.get("/two-wheeler-route")
async def two_wheeler_route(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
    main_road_penalty: float = 1.0,
    inner_road_multiplier: float = 1.0,
    service_multiplier: float = 1.0,
    roundabout_multiplier: float = 0.95,
    segment_km: float = 3.0,
):
    print(f"Two-wheeler route: ({from_lat},{from_lng}) -> ({to_lat},{to_lng})")
    try:
        penalties = build_two_wheeler_penalties(
            main_road_penalty=main_road_penalty,
            inner_road_multiplier=inner_road_multiplier,
            service_multiplier=service_multiplier,
            roundabout_multiplier=roundabout_multiplier,
        )
        straight_line_km = haversine_m(from_lat, from_lng, to_lat, to_lng) / 1000
        split_fractions = _derive_split_fractions(straight_line_km, segment_km)
        candidates = build_split_route_candidates(G, from_lat, from_lng, to_lat, to_lng, split_fractions=split_fractions, penalties=penalties)

        scoreable = [c for c in candidates if c["nodes"]]
        if not scoreable:
            return {"status": "error", "message": "Could not find a two-wheeler route."}

        # ── Live traffic scoring ──────────────────────────────
        # Your penalty/split logic above already generated and filtered the
        # candidates. Now, instead of picking the winner by static weighted
        # cost, ask Google for the REAL current traffic-aware duration of
        # each surviving candidate and pick whichever is actually fastest
        # right now. Static cost is only used as a fallback if the API
        # is unreachable.
        async with httpx.AsyncClient() as client:
            tasks = []
            for candidate in scoreable:
                nodes = candidate["nodes"]
                if candidate["strategy"] == "direct":
                    waypoint = None
                else:
                    mid_node = nodes[len(nodes) // 2]
                    waypoint = (G.nodes[mid_node]['y'], G.nodes[mid_node]['x'])
                tasks.append(fetch_traffic_duration(client, from_lat, from_lng, to_lat, to_lng, waypoint=waypoint))
            traffic_seconds_list = await asyncio.gather(*tasks)

        for candidate, secs in zip(scoreable, traffic_seconds_list):
            candidate["traffic_seconds"] = secs

        timed_candidates = [c for c in scoreable if c["traffic_seconds"] is not None]
        if timed_candidates:
            timed_candidates.sort(key=lambda c: c["traffic_seconds"])
            best = timed_candidates[0]
            selection_method = "live_traffic"
        else:
            print("  Live traffic unavailable for all candidates, falling back to static cost")
            scoreable.sort(key=lambda c: c["cost"])
            best = scoreable[0]
            selection_method = "static_cost_fallback"

        coords = route_nodes_to_coords(G, best["nodes"])
        response_candidates = []
        for candidate in candidates:
            candidate_nodes = candidate.get("nodes", [])
            candidate_length = route_length_m(G, candidate_nodes) if candidate_nodes else None
            candidate_weighted_cost = path_cost(G, candidate_nodes, penalties=penalties) if candidate_nodes else None
            traffic_secs = candidate.get("traffic_seconds")
            response_candidates.append({
                "strategy": candidate["strategy"],
                "cost": round(candidate["cost"], 2) if candidate["cost"] != float("inf") else None,
                "points": len(candidate.get("nodes", [])),
                "split_fraction": candidate.get("split_fraction"),
                "split_node": candidate.get("split_node"),
                "distance_meters": round(candidate_length, 2) if candidate_length is not None else None,
                "distance_km": round(candidate_length / 1000, 2) if candidate_length is not None else None,
                "weighted_cost": round(candidate_weighted_cost, 2) if candidate_weighted_cost is not None else None,
                "traffic_seconds": round(traffic_secs, 1) if traffic_secs is not None else None,
                "traffic_minutes": round(traffic_secs / 60, 1) if traffic_secs is not None else None,
                "error": candidate.get("error"),
            })

        print(f"  Best: {best['strategy']} via={selection_method} "
              f"traffic_s={best.get('traffic_seconds')} cost={best['cost']:.2f}")
        route_length = route_length_m(G, best["nodes"])
        route_score = path_cost(G, best["nodes"], penalties=penalties)
        best_traffic_seconds = best.get("traffic_seconds")
        return {
            "status": "success",
            "best_strategy": best["strategy"],
            "selection_method": selection_method,
            "path": coords,
            "distance_meters": round(route_length, 2),
            "distance_km": round(route_length / 1000, 2),
            "weighted_cost": round(route_score, 2),
            "traffic_seconds": round(best_traffic_seconds, 1) if best_traffic_seconds is not None else None,
            "traffic_minutes": round(best_traffic_seconds / 60, 1) if best_traffic_seconds is not None else None,
            "penalties": {
                "main_road_penalty": main_road_penalty,
                "inner_road_multiplier": inner_road_multiplier,
                "service_multiplier": service_multiplier,
                "roundabout_multiplier": roundabout_multiplier,
                "segment_km": segment_km,
            },
            "candidate_routes": response_candidates,
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Starting API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)