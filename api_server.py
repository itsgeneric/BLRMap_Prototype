import sys

# The server prints status lines with symbols. When its output goes to a file or a pipe on Windows (a service, a log redirect,
# a task runner) the default text encoding cannot represent them and printing RAISES, which stopped the server from starting at
# all. Make printing never fail.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import httpx
import osmnx as ox
import networkx as nx
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import threading

from core.config import (
    SNAP_FINAL_POLYLINE, ENABLE_ROAD_VERIFY, ROAD_VERIFY_MAX_ROUNDS, MAX_SNAP_DISTANCE_M,
    ENABLE_GOOGLE_ARRIVAL, ARRIVAL_TRIGGER_M,
)
from routing.graph_manager import graph_manager
from routing.algorithms import build_two_wheeler_penalties
from routing.smart import plan_smart
from routing.arrival import arrival_snaps
from routing.snapping import FAR_PIN_M, NoRoadNearby, find_snaps, nearby_junction_snaps, plan_route, snap_to_node
from routing.edge_blacklist import edge_blacklist
from services.external_api import (
    search_places, fetch_traffic_data, snap_and_verify_route, snap_route_to_roads, fetch_arrival_path,
)
from database.mongo_client import connect_db, close_db
from database.models import (
    RouteSnapshotIn,
    JourneyStartPayload,
    JourneyCompletePayload,
    ReroutePayload,
    IncidentCreate,
    IncidentVerify,
)
import database.operations as db


# Spatial index of every road edge. Used to snap pins to the nearest ROAD (routing/snapping.py) and by the developer
# road-quality tools. Built in a background thread after startup (about a minute); until it is ready, routes fall back
# to the old nearest-junction snapping so the server is usable immediately.
_road_index_state = {"index": None, "building": False, "error": None}


def _build_road_index():
    from routing.graph_qa import RoadIndex
    _road_index_state["building"] = True
    try:
        print("[Index] Building road index in the background...")
        _road_index_state["index"] = RoadIndex.from_graph(
            graph_manager.G, progress=lambda n: print(f"[Index]   indexed {n:,} edges...")
        )
        print(f"[Index] Road index ready: {_road_index_state['index'].size:,} sample points")
    except Exception as exc:
        _road_index_state["error"] = f"{type(exc).__name__}: {exc}"
        print(f"[Index] Road index failed: {_road_index_state['error']}")
    finally:
        _road_index_state["building"] = False


# Landmark bounds that make Dynamic planning several times faster (routing/landmarks.py). Built in the background after the
# road index; until they are ready (or if they cannot be used for a request) the plain, slower heuristic is used.
_landmark_state = {"lm": None, "building": False, "error": None}


def _build_landmarks():
    from routing.landmarks import Landmarks
    _landmark_state["building"] = True
    try:
        print("[Landmarks] Building search landmarks in the background...")
        lm = Landmarks.build(graph_manager.G, build_two_wheeler_penalties())
        _landmark_state["lm"] = lm
        print(f"[Landmarks] Ready: {len(lm.landmark_nodes)} landmarks in {lm.build_seconds:.0f}s")
    except Exception as exc:
        _landmark_state["error"] = f"{type(exc).__name__}: {exc}"
        print(f"[Landmarks] Failed (Dynamic will use the slower heuristic): {_landmark_state['error']}")
    finally:
        _landmark_state["building"] = False


def _snaps_for(lat: float, lng: float, label: str):
    """Candidate road points for a pin. Raises NoRoadNearby when no road is within MAX_SNAP_DISTANCE_M."""
    index = _road_index_state["index"]
    if index is None:
        return [snap_to_node(graph_manager.G, lat, lng)]
    snaps = find_snaps(graph_manager.G, index, lat, lng, MAX_SNAP_DISTANCE_M)
    if not snaps:
        raise NoRoadNearby(f"No road within {MAX_SNAP_DISTANCE_M:.0f} m of the {label} point. Move the pin closer to a road.")
    if snaps[0].distance_m > FAR_PIN_M:
        # Off the road: also offer nearby junctions, so a one-way segment cannot force a long detour (see nearby_junction_snaps).
        snaps = snaps + nearby_junction_snaps(graph_manager.G, index, lat, lng, snaps[0].distance_m)
    return snaps


async def _checked_route(make_plan):
    """
    Plans, checks the route's roads with Google, and plans again around any road Google does not have.
    Returns (plan, road_check):
        'passed'       every road on this very route was accepted
        'failed'       it still uses a road Google does not have (no way found round it)
        'unavailable'  Google could not be asked
        'off'          the check is disabled
    """
    plan = make_plan()
    if not ENABLE_ROAD_VERIFY:
        return plan, "off"
    for attempt in range(ROAD_VERIFY_MAX_ROUNDS):
        bad, status = await snap_and_verify_route(plan["ridden_edges"], graph_manager.G)
        if not bad:
            if any(edge_blacklist.get_edge_penalty(u, v) > 1.0 for u, v in plan["ridden_edges"]):
                return plan, "failed"          # a blocked road is the only way
            return plan, "passed" if status == "checked" else "unavailable"
        if attempt == ROAD_VERIFY_MAX_ROUNDS - 1:
            break
        try:
            plan = make_plan()
        except nx.NetworkXNoPath:
            break
    return plan, "failed"


async def _destination_snaps(from_lat, from_lng, to_lat, to_lng):
    """
    Where the trip ends. Returns (candidates, arrival):
        'nearest_road'     the road nearest the pin
        'google_approach'  no road is beside the pin, so the trip ends on the road Google approaches it from
    Raises NoRoadNearby when neither finds a road.
    """
    try:
        snaps, no_road = _snaps_for(to_lat, to_lng, "destination"), None
    except NoRoadNearby as exc:
        snaps, no_road = [], exc

    index = _road_index_state["index"]
    if ENABLE_GOOGLE_ARRIVAL and index is not None and (not snaps or snaps[0].distance_m > ARRIVAL_TRIGGER_M):
        async with httpx.AsyncClient() as client:
            google_path = await fetch_arrival_path(client, from_lat, from_lng, to_lat, to_lng)
        approach = arrival_snaps(graph_manager.G, index, google_path, (to_lat, to_lng)) if google_path else None
        if approach:
            return approach, "google_approach"

    if no_road:
        raise no_road
    return snaps, "nearest_road"


@asynccontextmanager
async def lifespan(app: FastAPI):
    graph_manager.load_graph()
    threading.Thread(target=_build_road_index, daemon=True).start()
    threading.Thread(target=_build_landmarks, daemon=True).start()
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
    # Pins are attached to the nearest ROAD (one-way aware). The returned path starts and ends ON a road: nothing is
    # drawn between a pin and the road (origin_snap / destination_snap report how far each pin was from it).
    try:
        origins = _snaps_for(from_lat, from_lng, "start")
        destinations, arrival = await _destination_snaps(from_lat, from_lng, to_lat, to_lng)
    except NoRoadNearby as exc:
        return {"status": "error", "message": str(exc)}

    try:
        plan, road_check = await _checked_route(
            lambda: plan_route(graph_manager.G, graph_manager, "shortest", origins, destinations))

        coords = plan["coords"]
        dist_km = round(plan["distance_m"] / 1000, 2)

        # Displayed line = our own graph geometry. Roads-API re-snapping is opt-in (SNAP_FINAL_POLYLINE).
        if SNAP_FINAL_POLYLINE:
            coords = await snap_route_to_roads(coords)
        # ────────────────────────────────────────────────────────────────

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

        response = {
            "status": "success", "path": coords, "distance_km": dist_km, "road_check": road_check, "arrival": arrival,
            "duration_s": plan["duration_s"],
            "origin_snap": plan["origin_snap"], "destination_snap": plan["destination_snap"],
            "maneuvers": plan["maneuvers"],
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
async def dynamic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    try:
        origins = _snaps_for(from_lat, from_lng, "start")
        destinations, arrival = await _destination_snaps(from_lat, from_lng, to_lat, to_lng)
    except NoRoadNearby as exc:
        return {"status": "error", "message": str(exc)}

    async with httpx.AsyncClient() as client:
        duration_s, jam_coords = await fetch_traffic_data(
            client, from_lat, from_lng, to_lat, to_lng
        )

    congested_nodes: set = set()
    if jam_coords:
        # ONE batched lookup for all jam points. A call per point rebuilt the lookup over the whole city each time (about 0.7 s
        # each), so a route with 60 jam points took 40+ s and the app gave up with "failed to fetch directions".
        unique = sorted({(round(lat, 5), round(lng, 5)) for lat, lng in jam_coords})
        found = ox.nearest_nodes(graph_manager.G, [lng for _, lng in unique], [lat for lat, _ in unique])
        congested_nodes.update(int(n) for n in found)

    # Fetch live crowd-sourced incidents (accidents, floods, hazards) for dynamic avoidance
    incident_penalties = await db.get_active_incident_penalties()

    penalties = build_two_wheeler_penalties()

    try:
        plan_args = dict(penalties=penalties, congested_nodes=congested_nodes, incident_nodes=incident_penalties,
                         landmarks=_landmark_state["lm"])
        # inner roads first, within a detour budget; through traffic when the way round is too long (routing/smart.py)
        plan, road_check = await _checked_route(
            lambda: plan_smart(graph_manager.G, graph_manager, origins, destinations, **plan_args))

        coords  = plan["coords"]
        dist_km = round(plan["distance_m"] / 1000, 2)
        google_mins = round(duration_s / 60, 1) if duration_s else None

        # Displayed line = our own graph geometry. Roads-API re-snapping is opt-in (SNAP_FINAL_POLYLINE).
        if SNAP_FINAL_POLYLINE:
            coords = await snap_route_to_roads(coords)
        # ────────────────────────────────────────────────────────────────

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
            "duration_s": plan["duration_s"],
            "google_base_duration_mins": google_mins,
            "congested_nodes_avoided": len(congested_nodes),
            "road_check": road_check,
            "arrival": arrival,
            "direct_distance_km": round(plan["direct_distance_m"] / 1000, 2),
            "preference_level": plan["preference_level"],
            "through_traffic": plan["through_traffic"],
            "origin_snap": plan["origin_snap"],
            "destination_snap": plan["destination_snap"],
            "maneuvers": plan["maneuvers"],
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


# ---------------------------------------------------------------------------
# Crowd-Sourced Incident Reporting Endpoints (Google Maps style)
# ---------------------------------------------------------------------------

@app.post("/incidents")
async def report_incident(payload: IncidentCreate):
    """
    Rider reports a live incident (crash, slowdown, flooded road, construction, etc.).
    Associates the report with nearest road network nodes and stores in MongoDB with TTL.
    """
    affected_nodes = []
    try:
        if graph_manager.G is not None and len(graph_manager.G) > 0:
            target_node = ox.nearest_nodes(graph_manager.G, payload.lng, payload.lat)
            affected_nodes.append(int(target_node))
            if target_node in graph_manager.G:
                for neighbor in graph_manager.G.neighbors(target_node):
                    affected_nodes.append(int(neighbor))
    except Exception as exc:
        print(f"⚠️ Could not map incident to graph nodes: {exc}")

    result = await db.create_incident(payload, nearest_nodes=affected_nodes)
    return result


@app.get("/incidents")
async def get_active_incidents(
    min_lat: float | None = None,
    min_lng: float | None = None,
    max_lat: float | None = None,
    max_lng: float | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_m: float | None = None,
):
    """
    Returns active, unexpired incidents for rendering on the map.
    Can filter by bounding box (viewport) or proximity radius.
    """
    incidents = await db.get_active_incidents(
        min_lat=min_lat,
        min_lng=min_lng,
        max_lat=max_lat,
        max_lng=max_lng,
        lat=lat,
        lng=lng,
        radius_m=radius_m,
    )
    return {"status": "ok", "count": len(incidents), "incidents": incidents}


@app.post("/incidents/{incident_id}/verify")
async def verify_incident_endpoint(incident_id: str, payload: IncidentVerify):
    """
    Handles 'Still here?' rider feedback (vote: 'yes' extends TTL, 'no' can resolve early).
    """
    result = await db.verify_incident(
        incident_id=incident_id,
        vote=payload.vote,
        session_id=payload.session_id,
    )
    return result


@app.get("/incidents/penalties")
async def get_incident_penalties():
    """Returns currently active routing penalties caused by incidents."""
    penalties = await db.get_active_incident_penalties()
    return {"status": "ok", "affected_nodes_count": len(penalties), "penalties": penalties}


if __name__ == "__main__":
    import uvicorn
    import sys
    reload_flag = "--no-reload" not in sys.argv
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=reload_flag)