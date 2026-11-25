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
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from database.mongo_client import get_col, is_connected
from database.models import (
    RouteSnapshotIn,
    JourneyStartPayload,
    JourneyCompletePayload,
    ReroutePayload,
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
