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

if __name__ == "__main__":
    import uvicorn
    print("Starting API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)