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
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
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
    return [(lat1 + i / n * (lat2 - lat1), lng1 + i / n * (lng2 - lng1)) for i in range(n + 1)]


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


def two_wheeler_astar(graph, start_node, end_node, penalties=None, jammed_nodes=None):
    def heuristic(a, b):
        return haversine_m(graph.nodes[a]['y'], graph.nodes[a]['x'],
                           graph.nodes[b]['y'], graph.nodes[b]['x'])

    def cost(u, v, edge_data):
        if 'length' in edge_data:
            base_cost = two_wheeler_edge_cost(edge_data, penalties=penalties)
        else:
            base_cost = min(two_wheeler_edge_cost(d, penalties=penalties) for d in edge_data.values())

        # Segmented Jam Bypass Logic:
        if jammed_nodes and (u in jammed_nodes or v in jammed_nodes):
            return base_cost * 20.0

        return base_cost

    return nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=cost)


def path_cost(graph, route, cost_fn=two_wheeler_edge_cost, penalties=None, jammed_nodes=None):
    total = 0.0
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        if b in graph[a]:
            base_cost = min(cost_fn(d, penalties=penalties) for d in graph[a][b].values())
            if jammed_nodes and (a in jammed_nodes or b in jammed_nodes):
                base_cost *= 20.0
            total += base_cost
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


DETOUR_TOLERANCE = 1.25


def build_split_route_candidates(graph, from_lat, from_lng, to_lat, to_lng,
                                 split_fractions=DEFAULT_ROUTE_SPLIT_FRACTIONS, penalties=None, jammed_nodes=None):
    direct_start = ox.nearest_nodes(graph, from_lng, from_lat)
    direct_end = ox.nearest_nodes(graph, to_lng, to_lat)

    candidates = []

    # 1. THE CONTROL BASELINE (Pure shortest distance, completely clean)
    try:
        baseline_route = two_wheeler_astar(graph, direct_start, direct_end, penalties={})
        candidates.append({
            'strategy': 'direct_baseline',
            'nodes': baseline_route,
            'cost': path_cost(graph, baseline_route, penalties={}),
        })
    except Exception as exc:
        pass

    # 2. STRATEGY A: ARTERIAL TRAFFIC BYPASS (Crucial for Long Distances)
    # No artificial penalty on main roads/flyovers. It leverages them for cruising speed,
    # but drops down into side-streets strictly where Google maps flags traffic jams.
    try:
        arterial_bypass = two_wheeler_astar(graph, direct_start, direct_end, penalties={}, jammed_nodes=jammed_nodes)
        candidates.append({
            'strategy': 'arterial_traffic_bypass',
            'nodes': arterial_bypass,
            'cost': path_cost(graph, arterial_bypass, penalties={}, jammed_nodes=jammed_nodes),
        })
    except Exception as exc:
        pass

    # 3. STRATEGY B: INNER ROAD SHORTCUT (Penalized + Jam Aware)
    # The original experimental mode that actively prefers residential lanes globally.
    try:
        inner_route = two_wheeler_astar(graph, direct_start, direct_end, penalties=penalties, jammed_nodes=jammed_nodes)
        candidates.append({
            'strategy': 'inner_road_shortcut',
            'nodes': inner_route,
            'cost': path_cost(graph, inner_route, penalties=penalties, jammed_nodes=jammed_nodes),
        })
    except Exception as exc:
        pass

    direct_length = None
    reference_nodes = candidates[0]['nodes'] if candidates else []
    if reference_nodes:
        direct_length = route_length_m(graph, reference_nodes)

    graph_aware_nodes = []
    if reference_nodes:
        graph_aware_nodes = _graph_aware_split_nodes(graph, reference_nodes, split_fractions)

    offset_points = _offset_split_points(from_lat, from_lng, to_lat, to_lng, split_fractions)
    fallback_nodes = [ox.nearest_nodes(graph, lng, lat) for lat, lng in offset_points]
    split_nodes = _dedupe_nodes(graph_aware_nodes + fallback_nodes)

    seen_paths = set()
    for c in candidates:
        if c['nodes']:
            seen_paths.add(tuple(c['nodes']))

    # 4. STRATEGY C: PARALLEL SPLIT TUNNELS (Hybrid Stitched Corridors)
    for split_node in split_nodes:
        split_fraction = None
        if reference_nodes and split_node in reference_nodes:
            split_fraction = round(reference_nodes.index(split_node) / max(1, len(reference_nodes) - 1), 2)

        try:
            # Splits follow the user-defined back-road tuning weights to discover parallel tracks
            first_leg = two_wheeler_astar(graph, direct_start, split_node, penalties=penalties,
                                          jammed_nodes=jammed_nodes)
            second_leg = two_wheeler_astar(graph, split_node, direct_end, penalties=penalties,
                                           jammed_nodes=jammed_nodes)
            stitched = _dedupe_nodes(first_leg + second_leg[1:])

            stitched_key = tuple(stitched)
            if stitched_key in seen_paths:
                continue
            seen_paths.add(stitched_key)

            if direct_length:
                stitched_length = route_length_m(graph, stitched)
                if stitched_length > direct_length * DETOUR_TOLERANCE:
                    continue

            candidates.append({
                'strategy': 'graph_split' if split_fraction is not None else 'line_split',
                'nodes': stitched,
                'split_fraction': split_fraction,
                'split_node': split_node,
                'cost': path_cost(graph, stitched, penalties=penalties, jammed_nodes=jammed_nodes),
            })
        except Exception as exc:
            pass

    return candidates


def route_nodes_to_coords(graph, route):
    return [[graph.nodes[node]['y'], graph.nodes[node]['x']] for node in route]


def route_length_m(graph, route):
    return calc_route_distance(graph, route)


async def fetch_traffic_probe(client, from_lat, from_lng, to_lat, to_lng):
    if not ROUTES_KEY:
        return []

    body = {
        "origin": {"location": {"latLng": {"latitude": from_lat, "longitude": from_lng}}},
        "destination": {"location": {"latLng": {"latitude": to_lat, "longitude": to_lng}}},
        "travelMode": "TWO_WHEELER",
        "routingPreference": "TRAFFIC_AWARE",
        "extraComputations": ["TRAFFIC_ON_POLYLINE"]
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": ROUTES_KEY,
        "X-Goog-FieldMask": "routes.polyline.encodedPolyline,routes.travelAdvisory.speedReadingIntervals",
    }

    try:
        res = await client.post(ROUTES_API_URL, json=body, headers=headers, timeout=8.0)
        res.raise_for_status()
        data = res.json()
        routes = data.get("routes")
        if not routes:
            return []

        route = routes[0]
        polyline_encoded = route.get("polyline", {}).get("encodedPolyline", "")
        intervals = route.get("travelAdvisory", {}).get("speedReadingIntervals", [])

        if not polyline_encoded or not intervals:
            return []

        full_path = decode_polyline(polyline_encoded)
        jammed_points = []

        for interval in intervals:
            if interval.get("speed") in ["SLOW", "TRAFFIC_JAM"]:
                start = interval.get("startPolylinePointIndex", 0)
                end = interval.get("endPolylinePointIndex", 0)
                jammed_points.extend(full_path[start:end + 1])

        return jammed_points
    except Exception as exc:
        print(f"Traffic probe failed: {type(exc).__name__} - {repr(exc)}")
        return []


async def fetch_traffic_duration(client, from_lat, from_lng, to_lat, to_lng, waypoint=None):
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
        res.raise_for_status()
        data = res.json()
        routes = data.get("routes")
        if not routes:
            return None
        duration_str = routes[0].get("duration", "")
        if not duration_str:
            return None
        return float(duration_str.rstrip("s"))
    except Exception as exc:
        print(f"  Routes API call failed: {type(exc).__name__} - {repr(exc)}")
        return None


def calc_route_distance(graph, route):
    total = 0.0
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        if b in graph[a]:
            best = min(graph[a][b].values(), key=lambda d: float(d.get('length', 1.0)))
            total += float(best.get('length', 0))
    return total


# ── Load graphs ───────────────────────────────────────────
print("Loading Bengaluru road network...")
G = ox.load_graphml("bengaluru_roads_full.graphml")
for u, v, key, data in G.edges(keys=True, data=True):
    data['length'] = float(data.get('length', 1.0))

MAX_EDGE_LENGTH = {'residential': 250, 'living_street': 200, 'service': 200, 'unclassified': 400, 'tertiary': 600}
edges_to_remove = []
for u, v, k, data in G.edges(keys=True, data=True):
    hw = data.get('highway', '')
    if isinstance(hw, list): hw = hw[0]
    max_len = MAX_EDGE_LENGTH.get(hw)
    if max_len and float(data.get('length', 0)) > max_len:
        edges_to_remove.append((u, v, k))
G.remove_edges_from(edges_to_remove)

largest_cc_nodes = max(nx.strongly_connected_components(G), key=len)
G = G.subgraph(largest_cc_nodes).copy()

G_inner = G.edge_subgraph(
    [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if _is_inner(d)]
).copy()


# ── Endpoints ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Bengaluru Router API"}


@app.get("/search")
async def search_places(q: str):
    if not GOOGLE_KEY:
        return await _search_nominatim(q)
    params = {"input": q, "key": GOOGLE_KEY, "components": "country:in", "location": "12.9716,77.5946", "radius": 50000,
              "language": "en"}
    async with httpx.AsyncClient() as client:
        res = await client.get("https://maps.googleapis.com/maps/api/place/autocomplete/json", params=params)
        data = res.json()

    results = []
    for prediction in data.get("predictions", [])[:5]:
        async with httpx.AsyncClient() as c2:
            det = await c2.get("https://maps.googleapis.com/maps/api/place/details/json",
                               params={"place_id": prediction["place_id"], "key": GOOGLE_KEY,
                                       "fields": "name,formatted_address,geometry"})
            details = det.json().get("result", {})
        if "geometry" in details:
            results.append({
                "name": details.get("name", prediction["structured_formatting"]["main_text"]),
                "address": details.get("formatted_address", ""),
                "lat": details["geometry"]["location"]["lat"],
                "lng": details["geometry"]["location"]["lng"],
            })
    return {"results": results}


async def _search_nominatim(q: str):
    search_query = q.strip()
    if "bengaluru" not in search_query.lower() and "bangalore" not in search_query.lower():
        search_query = f"{search_query}, Bengaluru"
    params = {"q": search_query, "format": "json", "addressdetails": 1, "limit": 5, "viewbox": "77.4,13.1,77.8,12.8",
              "bounded": 0}
    headers = {"User-Agent": "BLR-Router/1.0"}
    results = []
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers,
                                   timeout=10.0)
            data = res.json()
        for place in data:
            results.append(
                {"name": place.get("display_name", "").split(",")[0], "address": place.get("display_name", ""),
                 "lat": float(place.get("lat", 0)), "lng": float(place.get("lon", 0))})
    except Exception as e:
        print(f"Nominatim error: {e}")
    return {"results": results}


@app.get("/route")
def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    try:
        start = ox.nearest_nodes(G, from_lng, from_lat)
        end = ox.nearest_nodes(G, to_lng, to_lat)
        route = astar_on_graph(G, start, end)
        coords = route_nodes_to_coords(G, route)
        dist = calc_route_distance(G, route)
        return {"status": "success", "path": coords, "distance_km": round(dist / 1000, 2)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/two-wheeler-route")
async def two_wheeler_route(
        from_lat: float, from_lng: float, to_lat: float, to_lng: float,
        main_road_penalty: float = 1.0, inner_road_multiplier: float = 1.0,
        service_multiplier: float = 1.0, roundabout_multiplier: float = 0.95,
        segment_km: float = 3.0,
):
    print(f"Executing segmented route profiling...")
    try:
        penalties = build_two_wheeler_penalties(main_road_penalty, inner_road_multiplier, service_multiplier,
                                                roundabout_multiplier)
        straight_line_km = haversine_m(from_lat, from_lng, to_lat, to_lng) / 1000
        split_fractions = _derive_split_fractions(straight_line_km, segment_km)

        # PROBE PHASE
        jammed_nodes = set()
        async with httpx.AsyncClient() as client:
            jammed_coords = await fetch_traffic_probe(client, from_lat, from_lng, to_lat, to_lng)
        if jammed_coords:
            lngs, lats = [p[1] for p in jammed_coords], [p[0] for p in jammed_coords]
            jammed_nodes.update(ox.nearest_nodes(G, lngs, lats))
            print(f"  Dynamic Mapping: Labeled {len(jammed_nodes)} bottlenecks in graph.")

        # CANDIDATE PIPELINE
        candidates = build_split_route_candidates(G, from_lat, from_lng, to_lat, to_lng, split_fractions, penalties,
                                                  jammed_nodes)
        scoreable = [c for c in candidates if c["nodes"]]
        if not scoreable:
            return {"status": "error", "message": "Failed to generate any structural routes."}

        # LIVE TRAFFIC SCORING WITH TRACE LOCKING
        async with httpx.AsyncClient() as client:
            semaphore = asyncio.Semaphore(5)

            async def sem_fetch(*args, **kwargs):
                async with semaphore: return await fetch_traffic_duration(*args, **kwargs)

            tasks = []
            for candidate in scoreable:
                nodes = candidate["nodes"]
                # LOCK TRAJECTORY: Always pass a physical midpoint node to force Google to score
                # our custom local vector profile instead of falling back to default route logic.
                if len(nodes) > 4:
                    mid_node = nodes[len(nodes) // 2]
                    waypoint = (G.nodes[mid_node]['y'], G.nodes[mid_node]['x'])
                else:
                    waypoint = None
                tasks.append(sem_fetch(client, from_lat, from_lng, to_lat, to_lng, waypoint=waypoint))

            traffic_seconds_list = await asyncio.gather(*tasks)

        for candidate, secs in zip(scoreable, traffic_seconds_list):
            candidate["traffic_seconds"] = secs

        timed_candidates = [c for c in scoreable if c["traffic_seconds"] is not None]
        if timed_candidates:
            timed_candidates.sort(key=lambda c: c["traffic_seconds"])
            best = timed_candidates[0]
            selection_method = "live_traffic"
        else:
            scoreable.sort(key=lambda c: c["cost"])
            best = scoreable[0]
            selection_method = "static_cost_fallback"

        coords = route_nodes_to_coords(G, best["nodes"])
        response_candidates = []
        for candidate in candidates:
            c_nodes = candidate.get("nodes", [])
            c_len = route_length_m(G, c_nodes) if c_nodes else None
            t_secs = candidate.get("traffic_seconds")
            response_candidates.append({
                "strategy": candidate["strategy"],
                "distance_km": round(c_len / 1000, 2) if c_len is not None else None,
                "traffic_minutes": round(t_secs / 60, 1) if t_secs is not None else None,
            })

        print(f"  Selected Profile: {best['strategy']} via {selection_method}")
        route_length = route_length_m(G, best["nodes"])
        return {
            "status": "success",
            "best_strategy": best["strategy"],
            "selection_method": selection_method,
            "path": coords,
            "distance_km": round(route_length / 1000, 2),
            "traffic_minutes": round(best.get("traffic_seconds", 0) / 60, 1) if best.get("traffic_seconds") else None,
            "candidate_routes": response_candidates,
        }
    except Exception as e:
        import traceback;
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)