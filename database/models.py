"""
Pydantic v2 models for BLRNav's unified MongoDB schema.

All collections share a consistent field naming convention.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class PlaceInfo(BaseModel):
    name: str
    address: str = ""
    lat: float
    lng: float


# ---------------------------------------------------------------------------
# Route snapshot — captured at computation time inside the backend
# ---------------------------------------------------------------------------

class RouteSnapshotIn(BaseModel):
    """
    Passed internally when a route is computed.
    The `path` field is the full polyline already produced by graph_manager.
    """
    mode: str                                           # shortest | dynamic | fastest
    strategy: str = "direct"                            # direct | line_split
    path: List[List[float]]                             # [[lat, lng], ...]
    distance_km: float
    congested_nodes_avoided: int = 0
    google_base_duration_mins: Optional[float] = None
    estimated_duration_mins: Optional[float] = None


# ---------------------------------------------------------------------------
# Journey lifecycle payloads (received from the frontend)
# ---------------------------------------------------------------------------

class JourneyStartPayload(BaseModel):
    """
    Sent by the frontend when the user taps "Start Navigation".
    Enriches the journey document with session_id and human-readable place names.
    """
    session_id: str
    origin: PlaceInfo
    destination: PlaceInfo


class JourneyCompletePayload(BaseModel):
    """Sent on arrival. Captures actual trip performance."""
    actual_duration_secs: int
    actual_avg_speed_kmh: float


class ReroutePayload(BaseModel):
    """Sent each time the navigation engine detects an off-route condition."""
    lat: float
    lng: float
    distance_off_route_m: float = 0.0
    time_since_start_secs: int = 0
