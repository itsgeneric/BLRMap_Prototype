import httpx
import osmnx as ox
import networkx as nx
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routing.graph_manager import graph_manager
from routing.algorithms import (
    astar_on_graph, two_wheeler_astar, build_two_wheeler_penalties,
    calc_route_distance, extract_maneuvers_from_route, build_split_route_candidates
)
from services.external_api import search_places, fetch_traffic_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    graph_manager.load_graph()
    yield
    if graph_manager.G:
        graph_manager.G.clear()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {
        "status": "online",
        "bounds": graph_manager.bounds,
        "center": graph_manager.center
    }

@app.get("/search")
async def search(q: str):
    return await search_places(q)

@app.get("/route")
def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
    end = ox.nearest_nodes(graph_manager.G, to_lng, to_lat)
    
    try:
        route = astar_on_graph(graph_manager.G, start, end)
        coords = graph_manager.route_nodes_to_coords(route)
        dist = calc_route_distance(graph_manager.G, route)
        maneuvers = extract_maneuvers_from_route(graph_manager.G, route)
        return {
            "status": "success", 
            "path": coords, 
            "distance_km": round(dist/1000, 2),
            "maneuvers": maneuvers
        }
    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No shortest path found."}

@app.get("/dynamic-route")
async def dynamic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    try:
        start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
        end = ox.nearest_nodes(graph_manager.G, to_lng, to_lat)
        
        jam_coords = []
        duration_s = None
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                duration_s, jam_coords = await fetch_traffic_data(client, from_lat, from_lng, to_lat, to_lng)
        except Exception as e:
            print(f"Traffic data fetch warning: {e}")
            jam_coords = []
            duration_s = None
        
        congested_nodes = set()
        if jam_coords:
            for lat, lng in jam_coords:
                try:
                    congested_nodes.add(ox.nearest_nodes(graph_manager.G, lng, lat))
                except Exception:
                    pass
                
        penalties = build_two_wheeler_penalties()
        
        try:
            route = two_wheeler_astar(graph_manager.G, start, end, graph_manager, penalties=penalties, congested_nodes=congested_nodes)
        except (nx.NetworkXNoPath, Exception):
            # Fallback to standard A* if penalties blocked all paths
            route = astar_on_graph(graph_manager.G, start, end)

        coords = graph_manager.route_nodes_to_coords(route)
        dist = calc_route_distance(graph_manager.G, route)
        maneuvers = extract_maneuvers_from_route(graph_manager.G, route)
        
        return {
            "status": "success", 
            "path": coords, 
            "distance_km": round(dist/1000, 2),
            "google_base_duration_mins": round(duration_s / 60, 1) if duration_s else None,
            "congested_nodes_avoided": len(congested_nodes),
            "maneuvers": maneuvers
        }
    except Exception as exc:
        print(f"Route calculation error: {exc}")
        return {"status": "error", "message": f"Could not calculate path: {str(exc)}"}


@app.get("/two-wheeler-route")
async def two_wheeler_route(
    from_lat: float, from_lng: float, to_lat: float, to_lng: float,
    main_road_penalty: float = 1.35, inner_road_multiplier: float = 0.95,
    service_multiplier: float = 1.2, segment_km: float = 3.0
):
    penalties = build_two_wheeler_penalties(
        main_road_penalty=main_road_penalty,
        inner_road_multiplier=inner_road_multiplier,
        service_multiplier=service_multiplier
    )
    candidates = build_split_route_candidates(
        graph_manager.G, graph_manager, from_lat, from_lng, to_lat, to_lng, penalties=penalties
    )
    
    if not candidates or not candidates[0].get('nodes'):
        return {"status": "error", "message": "No valid 2W route candidate found."}
        
    best = candidates[0]
    coords = graph_manager.route_nodes_to_coords(best['nodes'])
    dist = calc_route_distance(graph_manager.G, best['nodes'])
    maneuvers = extract_maneuvers_from_route(graph_manager.G, best['nodes'])
    
    return {
        "status": "success",
        "path": coords,
        "distance_km": round(dist/1000, 2),
        "weighted_cost": round(best['cost'], 2),
        "best_strategy": best['strategy'],
        "candidate_routes": [
            {
                "strategy": c['strategy'],
                "distance_km": round(calc_route_distance(graph_manager.G, c['nodes'])/1000, 2) if c.get('nodes') else None,
                "weighted_cost": round(c['cost'], 2) if c.get('cost') is not None else None
            } for c in candidates if c.get('nodes')
        ],
        "maneuvers": maneuvers
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)