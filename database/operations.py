"""
All MongoDB read/write operations for BLRNav.

Unified 'journeys' collection schema
─────────────────────────────────────
{
  _id:           ObjectId
  session_id:    str | null         ← filled when nav starts
  status:        planned | navigating | completed | cancelled | rerouted

  origin:        { name, address, lat, lng }
  destination:   { name, address, lat, lng }

  route: {                          ← snapshot captured at computation time
    mode:                    str
    strategy:                str
    path:                    [[lat,lng], ...]   ← full polyline
    waypoints_count:         int
    distance_km:             float
    congested_nodes_avoided: int
    google_base_duration_mins: float | null
    estimated_duration_mins:   float | null
    computed_at:             datetime
  }

  journey: {                        ← filled progressively during navigation
    started_at:             datetime | null
    completed_at:           datetime | null
    actual_duration_secs:   int  | null
    actual_avg_speed_kmh:   float | null
    reroute_count:          int
  }

  reroute_events: [                 ← appended on each off-route event
    { position: {lat, lng}, distance_off_route_m, time_since_start_secs, occurred_at }
  ]

  context: {
    time_of_day_hour:  int
    day_of_week:       str
    is_peak_hour:      bool
  }

  created_at:  datetime
  updated_at:  datetime
}

'route_decisions' collection schema (learning layer)
──────────────────────────────────────────────────────
{
  _id:         ObjectId
  hour_bucket: int
  grid_lat:    int
  grid_lng:    int
  strategy:    str
  recorded_at: datetime
}
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId
from database.mongo_client import get_col, is_connected
from database.models import (
    RouteSnapshotIn,
    JourneyStartPayload,
    JourneyCompletePayload,
    ReroutePayload,
    IncidentCreate,
    IncidentVerify,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _context(dt: datetime) -> dict:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
    hour = dt.hour
    return {
        "time_of_day_hour": hour,
        "day_of_week": weekdays[dt.weekday()],
        "is_peak_hour": hour in (7, 8, 9, 17, 18, 19, 20),
    }


# ---------------------------------------------------------------------------
# journeys — create (auto-called on every route computation)
# ---------------------------------------------------------------------------

async def create_journey_from_route(
    snapshot: RouteSnapshotIn,
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
) -> Optional[str]:
    """
    Inserts a new journey document the moment a route is computed.
    The route snapshot (including the full polyline) is embedded immediately.
    Place names and session_id are filled later when the user starts navigating.

    Returns the journey_id string, or None if MongoDB is unavailable.
    """
    if not is_connected():
        return None

    now = _now()
    doc = {
        # ── Identity ─────────────────────────────────────────────────────
        "session_id": None,         # filled by /journeys/{id}/start
        "status": "planned",

        # ── Places ───────────────────────────────────────────────────────
        "origin": {
            "name": None,           # filled by /journeys/{id}/start
            "address": None,
            "lat": from_lat,
            "lng": from_lng,
        },
        "destination": {
            "name": None,
            "address": None,
            "lat": to_lat,
            "lng": to_lng,
        },

        # ── Route Snapshot ───────────────────────────────────────────────
        "route": {
            "mode": snapshot.mode,
            "strategy": snapshot.strategy,
            "path": snapshot.path,              # [[lat, lng], ...] full polyline
            "waypoints_count": len(snapshot.path),
            "distance_km": snapshot.distance_km,
            "congested_nodes_avoided": snapshot.congested_nodes_avoided,
            "google_base_duration_mins": snapshot.google_base_duration_mins,
            "estimated_duration_mins": snapshot.estimated_duration_mins,
            "computed_at": now,
        },

        # ── Journey Metrics ──────────────────────────────────────────────
        "journey": {
            "started_at": None,
            "completed_at": None,
            "actual_duration_secs": None,
            "actual_avg_speed_kmh": None,
            "reroute_count": 0,
        },

        # ── Reroute Events (grows as user deviates) ──────────────────────
        "reroute_events": [],

        # ── Time Context ─────────────────────────────────────────────────
        "context": _context(now),
        "created_at": now,
        "updated_at": now,
    }

    col = get_col("journeys")
    result = await col.insert_one(doc)
    return str(result.inserted_id)


# ---------------------------------------------------------------------------
# journeys — enrich (user taps "Start Navigation")
# ---------------------------------------------------------------------------

async def attach_session_and_places(
    journey_id: str,
    data: JourneyStartPayload,
) -> bool:
    """
    Fills in session_id, place names, and marks the journey as navigating.
    Called the moment the user taps "Start Navigation".
    """
    if not is_connected():
        return False

    now = _now()
    col = get_col("journeys")
    result = await col.update_one(
        {"_id": ObjectId(journey_id)},
        {
            "$set": {
                "session_id": data.session_id,
                "status": "navigating",
                "origin.name": data.origin.name,
                "origin.address": data.origin.address,
                "destination.name": data.destination.name,
                "destination.address": data.destination.address,
                "journey.started_at": now,
                "updated_at": now,
            }
        },
    )
    return result.modified_count > 0


# ---------------------------------------------------------------------------
# journeys — complete (user arrives at destination)
# ---------------------------------------------------------------------------

async def complete_journey(
    journey_id: str,
    data: JourneyCompletePayload,
) -> bool:
    if not is_connected():
        return False

    now = _now()
    col = get_col("journeys")
    result = await col.update_one(
        {"_id": ObjectId(journey_id)},
        {
            "$set": {
                "status": "completed",
                "journey.completed_at": now,
                "journey.actual_duration_secs": data.actual_duration_secs,
                "journey.actual_avg_speed_kmh": round(data.actual_avg_speed_kmh, 2),
                "updated_at": now,
            }
        },
    )
    return result.modified_count > 0


# ---------------------------------------------------------------------------
# journeys — reroute (off-route detected during navigation)
# ---------------------------------------------------------------------------

async def log_reroute(
    journey_id: str,
    data: ReroutePayload,
) -> bool:
    if not is_connected():
        return False

    now = _now()
    event = {
        "position": {"lat": data.lat, "lng": data.lng},
        "distance_off_route_m": data.distance_off_route_m,
        "time_since_start_secs": data.time_since_start_secs,
        "occurred_at": now,
    }
    col = get_col("journeys")
    result = await col.update_one(
        {"_id": ObjectId(journey_id)},
        {
            "$push": {"reroute_events": event},
            "$inc": {"journey.reroute_count": 1},
            "$set": {"status": "rerouted", "updated_at": now},
        },
    )
    return result.modified_count > 0


# ---------------------------------------------------------------------------
# route_decisions — learning layer (async MongoDB replacement for SQLite)
# ---------------------------------------------------------------------------

async def log_route_decision_mongo(
    hour_bucket: int,
    grid_lat: int,
    grid_lng: int,
    strategy: str,
) -> None:
    """Async equivalent of learning_layer.log_route_decision()."""
    if not is_connected():
        return
    col = get_col("route_decisions")
    await col.insert_one({
        "hour_bucket": hour_bucket,
        "grid_lat": grid_lat,
        "grid_lng": grid_lng,
        "strategy": strategy,
        "recorded_at": _now(),
    })


async def get_strategy_rates_mongo(
    hour_bucket: int,
    grid_lat: int,
    grid_lng: int,
) -> dict[str, int]:
    """
    Returns { strategy: count } for the given context bucket.
    Async equivalent of learning_layer.strategy_win_rates().
    """
    if not is_connected():
        return {}
    col = get_col("route_decisions")
    pipeline = [
        {"$match": {
            "hour_bucket": hour_bucket,
            "grid_lat": grid_lat,
            "grid_lng": grid_lng,
        }},
        {"$group": {"_id": "$strategy", "count": {"$sum": 1}}},
    ]
    results: dict[str, int] = {}
    async for doc in col.aggregate(pipeline):
        results[doc["_id"]] = doc["count"]
    return results


# ---------------------------------------------------------------------------
# incidents — Crowd-sourced Google Maps-style incident reporting
# ---------------------------------------------------------------------------

INCIDENT_TTLS_MINUTES: Dict[str, int] = {
    "crash": 45,
    "slowdown": 25,
    "flooded": 240,       # 4 hours
    "construction": 1440, # 24 hours
    "lane_closure": 480,  # 8 hours
    "hazard": 90,         # Object on road - 1.5 hours
    "visibility": 120,    # Low visibility - 2 hours
}

INCIDENT_LABELS: Dict[str, str] = {
    "crash": "Crash",
    "slowdown": "Slowdown",
    "construction": "Construction",
    "lane_closure": "Lane closure",
    "hazard": "Object on road",
    "flooded": "Flooded road",
    "visibility": "Low visibility",
}

INCIDENT_PENALTIES: Dict[str, float] = {
    "flooded": 50.0,      # Two-wheelers must avoid flooded roads
    "crash": 15.0,        # Severe bottleneck
    "slowdown": 4.0,      # Congested
    "lane_closure": 2.5,  # Narrow bottleneck
    "construction": 2.0,  # Slow movement
    "hazard": 2.0,        # Object on road
    "visibility": 1.2,    # Low visibility
}


async def create_incident(data: IncidentCreate, nearest_nodes: Optional[List[int]] = None) -> Dict[str, Any]:
    """Saves a new incident report with calculated TTL."""
    if not is_connected():
        return {"status": "error", "message": "Database not connected"}

    now = _now()
    incident_type = data.type.lower()
    ttl_minutes = INCIDENT_TTLS_MINUTES.get(incident_type, 60)
    expires_at = now + timedelta(minutes=ttl_minutes)

    doc = {
        "type": incident_type,
        "title": INCIDENT_LABELS.get(incident_type, incident_type.capitalize()),
        "location": {
            "type": "Point",
            "coordinates": [data.lng, data.lat],  # GeoJSON [longitude, latitude]
        },
        "lat": data.lat,
        "lng": data.lng,
        "heading": data.heading,
        "road_name": data.road_name,
        "reported_by": data.session_id,
        "created_at": now,
        "expires_at": expires_at,
        "status": "active",
        "upvotes": 1,
        "downvotes": 0,
        "affected_nodes": nearest_nodes or [],
    }

    col = get_col("incidents")
    result = await col.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return {"status": "ok", "incident": doc}


async def get_active_incidents(
    min_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lat: Optional[float] = None,
    max_lng: Optional[float] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_m: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Returns active, unexpired incidents within bounding box or near coordinate."""
    if not is_connected():
        return []

    now = _now()
    query: Dict[str, Any] = {
        "status": "active",
        "expires_at": {"$gt": now},
    }

    # Proximity query using $nearSphere
    if lat is not None and lng is not None and radius_m is not None:
        query["location"] = {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat],
                },
                "$maxDistance": radius_m,
            }
        }
    # Bounding box query
    elif min_lat is not None and min_lng is not None and max_lat is not None and max_lng is not None:
        query["location"] = {
            "$geoWithin": {
                "$box": [
                    [min_lng, min_lat],
                    [max_lng, max_lat],
                ]
            }
        }

    col = get_col("incidents")
    incidents = []
    async for doc in col.find(query).limit(100):
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        incidents.append(doc)
    return incidents


async def verify_incident(incident_id: str, vote: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Records a 'Still here?' vote (yes/no) and updates TTL or resolves incident."""
    if not is_connected():
        return {"status": "error", "message": "Database not connected"}

    try:
        oid = ObjectId(incident_id)
    except Exception:
        return {"status": "error", "message": "Invalid incident ID"}

    col = get_col("incidents")
    incident = await col.find_one({"_id": oid})
    if not incident:
        return {"status": "error", "message": "Incident not found"}

    now = _now()
    if vote.lower() == "yes":
        # Extend TTL by 50% of original default TTL
        orig_ttl = INCIDENT_TTLS_MINUTES.get(incident.get("type", ""), 45)
        extension = timedelta(minutes=int(orig_ttl * 0.5))
        curr_exp = incident.get("expires_at", now)
        if hasattr(curr_exp, "tzinfo") and curr_exp.tzinfo is None:
            curr_exp = curr_exp.replace(tzinfo=timezone.utc)
        new_expires_at = max(curr_exp, now) + extension
        await col.update_one(
            {"_id": oid},
            {
                "$inc": {"upvotes": 1},
                "$set": {"expires_at": new_expires_at, "updated_at": now},
            },
        )
        return {"status": "ok", "message": "Incident verified; lifespan extended"}
    elif vote.lower() == "no":
        downvotes = incident.get("downvotes", 0) + 1
        upvotes = incident.get("upvotes", 1)
        # If downvotes exceed upvotes, mark as resolved immediately
        if downvotes > upvotes:
            await col.update_one(
                {"_id": oid},
                {"$inc": {"downvotes": 1}, "$set": {"status": "resolved", "updated_at": now}},
            )
            return {"status": "ok", "message": "Incident marked as cleared"}
        else:
            await col.update_one(
                {"_id": oid},
                {"$inc": {"downvotes": 1}, "$set": {"updated_at": now}},
            )
            return {"status": "ok", "message": "Downvote recorded"}

    return {"status": "error", "message": "Invalid vote value"}


async def get_active_incident_penalties() -> Dict[int, float]:
    """
    Returns a dict mapping { node_id: penalty_multiplier } for all currently active incidents.
    Used by the routing engine to avoid reported hazards and slowdowns.
    """
    if not is_connected():
        return {}

    now = _now()
    col = get_col("incidents")
    penalties: Dict[int, float] = {}

    query = {"status": "active", "expires_at": {"$gt": now}}
    async for doc in col.find(query, {"affected_nodes": 1, "type": 1}):
        incident_type = doc.get("type", "")
        penalty_mult = INCIDENT_PENALTIES.get(incident_type, 2.0)
        for node in doc.get("affected_nodes", []):
            penalties[node] = max(penalties.get(node, 1.0), penalty_mult)

    return penalties

