from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import osmnx as ox
import networkx as nx
import os
import httpx
from dotenv import load_dotenv
import math

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

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

    graph_aware_nodes = []
    if candidates and candidates[0]['nodes']:
        graph_aware_nodes = _graph_aware_split_nodes(graph, candidates[0]['nodes'], split_fractions)

    fallback_nodes = []
    for fraction in split_fractions:
        split_lat, split_lng = _line_split_points(from_lat, from_lng, to_lat, to_lng, [fraction])[0]
        fallback_nodes.append(ox.nearest_nodes(graph, split_lng, split_lat))

    split_nodes = _dedupe_nodes(graph_aware_nodes + fallback_nodes)

    for split_node in split_nodes:
        split_fraction = None
        if candidates and candidates[0]['nodes'] and split_node in candidates[0]['nodes']:
            split_fraction = round(candidates[0]['nodes'].index(split_node) / max(1, len(candidates[0]['nodes']) - 1), 2)

        try:
            first_leg = two_wheeler_astar(graph, direct_start, split_node, penalties=penalties)
            second_leg = two_wheeler_astar(graph, split_node, direct_end, penalties=penalties)
            stitched = _dedupe_nodes(first_leg + second_leg[1:])
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
    return [[graph.nodes[node]['y'], graph.nodes[node]['x']] for node in route]

def route_length_m(graph, route):
    return calc_route_distance(graph, route)

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

@app.get("/route")
def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    print(f"Shortest: ({from_lat},{from_lng}) -> ({to_lat},{to_lng})")
    try:
        start = ox.nearest_nodes(G, from_lng, from_lat)
        end   = ox.nearest_nodes(G, to_lng, to_lat)
        route = astar_on_graph(G, start, end)
        coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]
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

        coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in full_route]
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
def two_wheeler_route(
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
        best = next((candidate for candidate in candidates if candidate["nodes"]), candidates[0])

        if not best["nodes"]:
            return {"status": "error", "message": "Could not find a two-wheeler route."}

        coords = route_nodes_to_coords(G, best["nodes"])
        response_candidates = []
        for candidate in candidates:
            candidate_nodes = candidate.get("nodes", [])
            candidate_length = route_length_m(G, candidate_nodes) if candidate_nodes else None
            candidate_weighted_cost = path_cost(G, candidate_nodes, penalties=penalties) if candidate_nodes else None
            response_candidates.append({
                "strategy": candidate["strategy"],
                "cost": round(candidate["cost"], 2) if candidate["cost"] != float("inf") else None,
                "points": len(candidate.get("nodes", [])),
                "split_fraction": candidate.get("split_fraction"),
                "split_node": candidate.get("split_node"),
                "distance_meters": round(candidate_length, 2) if candidate_length is not None else None,
                "distance_km": round(candidate_length / 1000, 2) if candidate_length is not None else None,
                "weighted_cost": round(candidate_weighted_cost, 2) if candidate_weighted_cost is not None else None,
                "error": candidate.get("error"),
            })

        print(f"  Best: {best['strategy']} cost={best['cost']:.2f}")
        route_length = route_length_m(G, best["nodes"])
        route_score = path_cost(G, best["nodes"], penalties=penalties)
        return {
            "status": "success",
            "best_strategy": best["strategy"],
            "path": coords,
            "distance_meters": round(route_length, 2),
            "distance_km": round(route_length / 1000, 2),
            "weighted_cost": round(route_score, 2),
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