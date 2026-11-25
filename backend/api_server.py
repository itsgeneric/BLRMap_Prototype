import httpx
import osmnx as ox
import networkx as nx
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional

from routing.graph_manager import graph_manager
from routing.guidance import build_guidance
from routing.app_costs import lane_entry_cost
from routing.algorithms import (
    astar_on_graph,
    two_wheeler_astar,
    build_two_wheeler_penalties,
    calc_route_distance,
    generate_route_maneuvers,
    haversine_m,
    two_wheeler_edge_cost,
)
from services.external_api import search_places, fetch_traffic_data, fetch_route_duration
from database.mongo_client import connect_db, close_db
from database.models import RouteSnapshotIn, JourneyStartPayload, JourneyCompletePayload, ReroutePayload
import database.operations as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    graph_manager.load_graph()
    graph_manager.build_edge_index()
    await connect_db()
    yield
    if graph_manager.G is not None:
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


# ---------------------------------------------------------------------------
# Snapping + drawable geometry shared by the route endpoints
# ---------------------------------------------------------------------------

def _snap_request(from_lat: float, from_lng: float, to_lat: float, to_lng: float,
                  heading: Optional[float] = None):
    """Snap both pins onto the nearest road and pick the graph nodes to route between."""
    try:
        start_snap = graph_manager.snap_to_road(from_lat, from_lng)
        end_snap = graph_manager.snap_to_road(to_lat, to_lng)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    start, end = graph_manager.choose_route_endpoints(start_snap, end_snap, heading=heading)
    return start_snap, end_snap, start, end


def _route_geometry(route, start_snap, end_snap, key_fn=None, destination=None):
    """
    Road-following polyline that starts/ends on the snapped road points, its length
    in km, and turn-by-turn guidance anchored to that polyline.
    """
    snapped = graph_manager.build_snapped_route(route, start_snap, end_snap, key_fn=key_fn)
    maneuvers, _ = build_guidance(graph_manager, snapped, destination=destination)
    coords = snapped.coords
    dist_m = sum(
        haversine_m(a[0], a[1], b[0], b[1]) for a, b in zip(coords, coords[1:])
    )
    return coords, round(dist_m / 1000, 2), maneuvers


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
async def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float,
                   heading: Optional[float] = None):
    start_snap, end_snap, start, end = _snap_request(from_lat, from_lng, to_lat, to_lng, heading)

    try:
        route  = astar_on_graph(graph_manager.G, start, end)
        coords, dist_km, maneuvers = _route_geometry(
            route, start_snap, end_snap, destination=(to_lat, to_lng))

        async with httpx.AsyncClient() as client:
            duration_mins = await fetch_route_duration(client, coords, dist_km=dist_km)

        # ── Save route snapshot to MongoDB ──────────────────────────────
        snapshot = RouteSnapshotIn(
            mode="shortest",
            strategy="direct",
            path=coords,
            distance_km=dist_km,
            estimated_duration_mins=duration_mins,
        )
        journey_id = await db.create_journey_from_route(
            snapshot, from_lat, from_lng, to_lat, to_lng
        )
        # ────────────────────────────────────────────────────────────────

        response = {
            "status": "success",
            "path": coords,
            "distance_km": dist_km,
            "duration_mins": duration_mins,
            "maneuvers": maneuvers,
        }
        if journey_id:
            response["journey_id"] = journey_id
        return response

    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No shortest path found."}


# ---------------------------------------------------------------------------
# /dynamic-route  — Traffic-aware two-wheeler routing
# ---------------------------------------------------------------------------

@app.get("/dynamic-route")
async def dynamic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float,
                       heading: Optional[float] = None):
    start_snap, end_snap, start, end = _snap_request(from_lat, from_lng, to_lat, to_lng, heading)

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
            # Don't leave a main road for a few metres of unnamed alley (see app_costs)
            transition_cost=lane_entry_cost(graph_manager.G),
        )
        # Draw the same parallel edge the two-wheeler cost model picked.
        G = graph_manager.G

        def cheapest_key(a, b):
            return min(G[a][b], key=lambda k: two_wheeler_edge_cost(
                G[a][b][k], graph_manager, penalties, a, b, congested_nodes))

        coords, dist_km, maneuvers = _route_geometry(
            route, start_snap, end_snap, key_fn=cheapest_key, destination=(to_lat, to_lng))
        google_mins = round(duration_s / 60, 1) if duration_s else None

        async with httpx.AsyncClient() as client:
            duration_mins = await fetch_route_duration(client, coords, dist_km=dist_km)

        # ── Save route snapshot to MongoDB ──────────────────────────────
        snapshot = RouteSnapshotIn(
            mode="dynamic",
            strategy="direct",
            path=coords,
            distance_km=dist_km,
            congested_nodes_avoided=len(congested_nodes),
            google_base_duration_mins=google_mins,
            estimated_duration_mins=duration_mins,
        )
        journey_id = await db.create_journey_from_route(
            snapshot, from_lat, from_lng, to_lat, to_lng
        )
        # ────────────────────────────────────────────────────────────────

        response = {
            "status": "success",
            "path": coords,
            "distance_km": dist_km,
            "duration_mins": duration_mins,
            "google_base_duration_mins": google_mins,
            "congested_nodes_avoided": len(congested_nodes),
            "maneuvers": maneuvers,
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


if __name__ == "__main__":
    import uvicorn
    import sys
    reload_flag = "--reload" in sys.argv
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=reload_flag)