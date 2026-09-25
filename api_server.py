import httpx
import osmnx as ox
import networkx as nx
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routing.graph_manager import graph_manager
from routing.algorithms import astar_on_graph, two_wheeler_astar, build_two_wheeler_penalties, calc_route_distance
from routing.edge_blacklist import edge_blacklist
from services.external_api import search_places, fetch_traffic_data, snap_and_verify_route
from database.mongo_client import connect_db, close_db
from database.models import RouteSnapshotIn, JourneyStartPayload, JourneyCompletePayload, ReroutePayload
import database.operations as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    graph_manager.load_graph()
    await connect_db()
    yield
    graph_manager.G.clear()
    await close_db()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "online"}


@app.get("/search")
async def search(q: str):
    return await search_places(q)


# ---------------------------------------------------------------------------
# /route  — Shortest path (A*)
# ---------------------------------------------------------------------------

@app.get("/route")
async def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
    end   = ox.nearest_nodes(graph_manager.G, to_lng,  to_lat)

    try:
        route  = astar_on_graph(graph_manager.G, start, end)

        # GMaps verification loop: iteratively eliminate any ghost/private roads
        for _ in range(3):
            flagged = await snap_and_verify_route(route, graph_manager.G)
            if not flagged:
                break
            try:
                route = astar_on_graph(graph_manager.G, start, end)
            except Exception:
                break

        coords = graph_manager.route_nodes_to_coords(route)
        dist   = calc_route_distance(graph_manager.G, route)
        dist_km = round(dist / 1000, 2)

        # ── Save route snapshot to MongoDB ──────────────────────────────
        snapshot = RouteSnapshotIn(
            mode="shortest",
            strategy="direct",
            path=coords,
            distance_km=dist_km,
        )
        journey_id = await db.create_journey_from_route(
            snapshot, from_lat, from_lng, to_lat, to_lng
        )
        # ────────────────────────────────────────────────────────────────

        response = {"status": "success", "path": coords, "distance_km": dist_km}
        if journey_id:
            response["journey_id"] = journey_id
        return response

    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No shortest path found."}


# ---------------------------------------------------------------------------
# /dynamic-route  — Traffic-aware two-wheeler routing
# ---------------------------------------------------------------------------

@app.get("/dynamic-route")
async def dynamic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
    end   = ox.nearest_nodes(graph_manager.G, to_lng,  to_lat)

    async with httpx.AsyncClient() as client:
        duration_s, jam_coords = await fetch_traffic_data(
            client, from_lat, from_lng, to_lat, to_lng
        )

    congested_nodes: set = set()
    if jam_coords:
        for lat, lng in jam_coords:
            congested_nodes.add(ox.nearest_nodes(graph_manager.G, lng, lat))

    penalties = build_two_wheeler_penalties()

    try:
        route = two_wheeler_astar(
            graph_manager.G, start, end, graph_manager,
            penalties=penalties, congested_nodes=congested_nodes,
        )

        # GMaps verification loop: iteratively eliminate any ghost/private roads
        for _ in range(3):
            flagged = await snap_and_verify_route(route, graph_manager.G)
            if not flagged:
                break
            try:
                route = two_wheeler_astar(
                    graph_manager.G, start, end, graph_manager,
                    penalties=penalties, congested_nodes=congested_nodes,
                )
            except Exception:
                break

        coords  = graph_manager.route_nodes_to_coords(route)
        dist    = calc_route_distance(graph_manager.G, route)
        dist_km = round(dist / 1000, 2)
        google_mins = round(duration_s / 60, 1) if duration_s else None

        # ── Save route snapshot to MongoDB ──────────────────────────────
        snapshot = RouteSnapshotIn(
            mode="dynamic",
            strategy="direct",
            path=coords,
            distance_km=dist_km,
            congested_nodes_avoided=len(congested_nodes),
            google_base_duration_mins=google_mins,
        )
        journey_id = await db.create_journey_from_route(
            snapshot, from_lat, from_lng, to_lat, to_lng
        )
        # ────────────────────────────────────────────────────────────────

        response = {
            "status": "success",
            "path": coords,
            "distance_km": dist_km,
            "google_base_duration_mins": google_mins,
            "congested_nodes_avoided": len(congested_nodes),
        }
        if journey_id:
            response["journey_id"] = journey_id
        return response

    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No dynamic path could be found."}



# ---------------------------------------------------------------------------
# Journey lifecycle endpoints
# ---------------------------------------------------------------------------

@app.post("/journeys/{journey_id}/start")
async def journey_start(journey_id: str, payload: JourneyStartPayload):
    """
    Called when the user taps 'Start Navigation'.
    Enriches the journey with session_id and human-readable place names,
    and marks status as 'navigating'.
    """
    ok = await db.attach_session_and_places(journey_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail="Journey not found")
    return {"status": "ok"}


@app.post("/journeys/{journey_id}/complete")
async def journey_complete(journey_id: str, payload: JourneyCompletePayload):
    """
    Called on arrival at the destination.
    Saves actual trip duration and average speed.
    """
    ok = await db.complete_journey(journey_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail="Journey not found")
    return {"status": "ok"}


@app.post("/journeys/{journey_id}/reroute")
async def journey_reroute(journey_id: str, payload: ReroutePayload):
    """
    Called each time the navigation engine detects an off-route condition.
    Appends a reroute_event to the journey document.
    """
    ok = await db.log_reroute(journey_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail="Journey not found")
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Blacklist inspection & reset
# ---------------------------------------------------------------------------

@app.get("/blacklist")
def get_blacklist():
    """Returns the list of Google Maps-verified blacklisted ghost roads."""
    return {
        "status": "ok",
        "count": edge_blacklist.count(),
        "edges": edge_blacklist.records,
    }


@app.post("/blacklist/clear")
def clear_blacklist():
    """Clears the edge blacklist."""
    edge_blacklist.clear()
    return {"status": "ok", "message": "Edge blacklist cleared"}


from pydantic import BaseModel

class BlacklistEdgeRequest(BaseModel):
    u: int | None = None
    v: int | None = None
    lat: float | None = None
    lng: float | None = None
    reason: str = "manual_report"

@app.post("/blacklist/add")
def add_to_blacklist(req: BlacklistEdgeRequest):
    u, v = req.u, req.v
    if (u is None or v is None) and req.lat is not None and req.lng is not None:
        target_node = ox.nearest_nodes(graph_manager.G, req.lng, req.lat)
        neighbors = list(graph_manager.G.neighbors(target_node))
        if neighbors:
            u, v = target_node, neighbors[0]
    if u is not None and v is not None:
        edge_blacklist.mark_edge_bad(u, v, penalty=10000.0, deviation_m=999.0, reason=req.reason)
        return {"status": "ok", "message": f"Blacklisted edge {u}_{v}", "count": edge_blacklist.count()}
    return {"status": "error", "message": "Could not identify edge to blacklist"}


@app.get("/blacklist/reload")
def reload_blacklist():
    """Reloads the edge blacklist from disk."""
    edge_blacklist.load()
    return {"status": "ok", "count": edge_blacklist.count()}


if __name__ == "__main__":
    import uvicorn
    import sys
    reload_flag = "--no-reload" not in sys.argv
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=reload_flag)