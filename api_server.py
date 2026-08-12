import httpx
import osmnx as ox
import networkx as nx
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routing.graph_manager import graph_manager
from routing.algorithms import astar_on_graph, two_wheeler_astar, build_two_wheeler_penalties, calc_route_distance
from services.external_api import search_places, fetch_traffic_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    graph_manager.load_graph()
    yield
    graph_manager.G.clear()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"status": "online"}

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
        return {"status": "success", "path": coords, "distance_km": round(dist/1000, 2)}
    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No shortest path found."}

@app.get("/dynamic-route")
async def dynamic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
    end = ox.nearest_nodes(graph_manager.G, to_lng, to_lat)
    
    # 1. Ask Google where the jams are
    async with httpx.AsyncClient() as client:
        duration_s, jam_coords = await fetch_traffic_data(client, from_lat, from_lng, to_lat, to_lng)
    
    # 2. Snap jam coordinates to your local graph nodes
    congested_nodes = set()
    if jam_coords:
        for lat, lng in jam_coords:
            congested_nodes.add(ox.nearest_nodes(graph_manager.G, lng, lat))
            
    penalties = build_two_wheeler_penalties()
    
    # 3. Route around the jams
    try:
        route = two_wheeler_astar(graph_manager.G, start, end, graph_manager, penalties=penalties, congested_nodes=congested_nodes)
        coords = graph_manager.route_nodes_to_coords(route)
        dist = calc_route_distance(graph_manager.G, route)
        
        return {
            "status": "success", 
            "path": coords, 
            "distance_km": round(dist/1000, 2),
            "google_base_duration_mins": round(duration_s / 60, 1) if duration_s else None,
            "congested_nodes_avoided": len(congested_nodes)
        }
    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No dynamic path could be found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)