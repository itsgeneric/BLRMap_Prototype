"""
services/route_cache.py
-----------------------
Shared anonymous route cache backed by DECISIONS_DB (SQLite).

All functions open their own connection so they are safe to call from
multiple threads (FastAPI sync endpoints run in a thread-pool, async
endpoints offload via asyncio.to_thread).  No user-identifying data
is ever stored.
"""

import json
import sqlite3
import time
from typing import Optional

from core.config import DECISIONS_DB
from routing.algorithms import haversine_m

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS shared_route_cache (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    from_lat          REAL    NOT NULL,
    from_lng          REAL    NOT NULL,
    to_lat            REAL    NOT NULL,
    to_lng            REAL    NOT NULL,
    path              TEXT    NOT NULL,
    distance_km       REAL    NOT NULL,
    endpoint          TEXT    NOT NULL,
    congestion_current INTEGER NOT NULL DEFAULT 1,
    hit_count         INTEGER NOT NULL DEFAULT 1,
    cached_at         INTEGER NOT NULL
);
"""

_CREATE_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_cache_coords
    ON shared_route_cache(from_lat, from_lng, to_lat, to_lng, endpoint);
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    """Open a connection to DECISIONS_DB with row factory for dict-like access."""
    conn = sqlite3.connect(DECISIONS_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def round_coord(v: float, decimals: int = 3) -> float:
    """Round a coordinate to *decimals* decimal places (~111 m grid at 3 dp)."""
    return round(v, decimals)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_cache() -> None:
    """Create the shared_route_cache table and index if they don't exist.

    Called once at server startup inside the FastAPI lifespan.
    """
    with _connect() as conn:
        conn.execute(_CREATE_TABLE)
        conn.execute(_CREATE_INDEX)
        conn.commit()
    print(f"[route_cache] Initialised shared_route_cache in {DECISIONS_DB}")


def save_route(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
    path: list,
    distance_km: float,
    endpoint: str,
    congestion_current: bool = True,
) -> None:
    """Insert a new cached route or increment hit_count if the
    rounded origin/destination/endpoint key already exists.

    Args:
        from_lat, from_lng: raw (un-rounded) origin coordinates.
        to_lat, to_lng:     raw (un-rounded) destination coordinates.
        path:               list of [lat, lng] pairs (the route polyline).
        distance_km:        total route distance.
        endpoint:           'route' | 'dynamic-route' | 'two-wheeler-route'
        congestion_current: True when the path was computed with live traffic
                            data; False when it comes from the cache.
    """
    r_from_lat = round_coord(from_lat)
    r_from_lng = round_coord(from_lng)
    r_to_lat   = round_coord(to_lat)
    r_to_lng   = round_coord(to_lng)
    path_json  = json.dumps(path)
    now        = int(time.time())
    cong_int   = 1 if congestion_current else 0

    try:
        with _connect() as conn:
            # Try to insert; the UNIQUE index on (from_lat, from_lng, to_lat, to_lng, endpoint)
            # will raise IntegrityError if this trip is already cached.
            try:
                conn.execute(
                    """
                    INSERT INTO shared_route_cache
                        (from_lat, from_lng, to_lat, to_lng, path, distance_km,
                         endpoint, congestion_current, hit_count, cached_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (r_from_lat, r_from_lng, r_to_lat, r_to_lng, path_json,
                     distance_km, endpoint, cong_int, now),
                )
            except sqlite3.IntegrityError:
                # Duplicate — update the path/distance/timestamp and bump hit_count.
                conn.execute(
                    """
                    UPDATE shared_route_cache
                    SET path = ?, distance_km = ?, congestion_current = ?,
                        cached_at = ?, hit_count = hit_count + 1
                    WHERE from_lat = ? AND from_lng = ?
                      AND to_lat   = ? AND to_lng   = ?
                      AND endpoint = ?
                    """,
                    (path_json, distance_km, cong_int, now,
                     r_from_lat, r_from_lng, r_to_lat, r_to_lng, endpoint),
                )
            conn.commit()
    except Exception as exc:
        # Cache writes are best-effort — never let them crash a route response.
        print(f"[route_cache] save_route failed (non-fatal): {exc}")


def find_nearest_cached(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
    max_age_days: int = 7,
    tolerance_m: float = 250.0,
) -> Optional[dict]:
    """Return the closest cached route whose origin is within *tolerance_m* of
    (from_lat, from_lng) AND whose destination is within *tolerance_m* of
    (to_lat, to_lng), and which was cached no more than *max_age_days* ago.

    Candidates are pre-filtered with a cheap bounding-box query before the
    exact haversine check, so this stays fast even with many rows.

    Returns a dict with route data, or None on a cache miss.
    """
    cutoff = int(time.time()) - max_age_days * 86400

    # A 1-degree bounding box at Bengaluru's latitude ≈ 111 km — far wider
    # than our tolerance, giving a small candidate set with zero false negatives.
    # tolerance_m / 111_000 converts metres to degrees.
    deg_margin = (tolerance_m / 111_000.0) * 2  # 2× safety margin

    try:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT id, from_lat, from_lng, to_lat, to_lng,
                       path, distance_km, endpoint, congestion_current,
                       hit_count, cached_at
                FROM   shared_route_cache
                WHERE  cached_at >= ?
                  AND  from_lat BETWEEN ? AND ?
                  AND  from_lng BETWEEN ? AND ?
                  AND  to_lat   BETWEEN ? AND ?
                  AND  to_lng   BETWEEN ? AND ?
                ORDER BY hit_count DESC, cached_at DESC
                """,
                (
                    cutoff,
                    from_lat - deg_margin, from_lat + deg_margin,
                    from_lng - deg_margin, from_lng + deg_margin,
                    to_lat   - deg_margin, to_lat   + deg_margin,
                    to_lng   - deg_margin, to_lng   + deg_margin,
                ),
            ).fetchall()
    except Exception as exc:
        print(f"[route_cache] find_nearest_cached query failed: {exc}")
        return None

    best_row  = None
    best_dist = float("inf")

    for row in rows:
        d_from = haversine_m(from_lat, from_lng, row["from_lat"], row["from_lng"])
        d_to   = haversine_m(to_lat,   to_lng,   row["to_lat"],   row["to_lng"])
        combined = d_from + d_to
        if d_from <= tolerance_m and d_to <= tolerance_m and combined < best_dist:
            best_dist = combined
            best_row  = row

    if best_row is None:
        return None

    return {
        "status":             "hit",
        "source":             "shared_cache",
        "congestion_current": False,          # always False — data may be stale
        "endpoint":           best_row["endpoint"],
        "path":               json.loads(best_row["path"]),
        "distance_km":        best_row["distance_km"],
        "hit_count":          best_row["hit_count"],
        "cached_at":          best_row["cached_at"],
    }


def get_popular_near(
    lat: float,
    lng: float,
    radius_m: float = 3000.0,
    limit: int = 20,
) -> list:
    """Return up to *limit* cached routes whose origin lies within *radius_m*
    of (lat, lng), ordered by hit_count DESC then cached_at DESC.

    Used by the frontend to pre-sync routes for the user's current area.
    No age filter is applied here — freshness is the frontend's concern.
    """
    deg_margin = (radius_m / 111_000.0) * 2

    try:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT from_lat, from_lng, to_lat, to_lng,
                       path, distance_km, endpoint,
                       hit_count, cached_at
                FROM   shared_route_cache
                WHERE  from_lat BETWEEN ? AND ?
                  AND  from_lng BETWEEN ? AND ?
                ORDER BY hit_count DESC, cached_at DESC
                LIMIT  ?
                """,
                (
                    lat - deg_margin, lat + deg_margin,
                    lng - deg_margin, lng + deg_margin,
                    limit * 4,   # over-fetch before haversine filter
                ),
            ).fetchall()
    except Exception as exc:
        print(f"[route_cache] get_popular_near query failed: {exc}")
        return []

    results = []
    for row in rows:
        if haversine_m(lat, lng, row["from_lat"], row["from_lng"]) <= radius_m:
            results.append({
                "from_lat":   row["from_lat"],
                "from_lng":   row["from_lng"],
                "to_lat":     row["to_lat"],
                "to_lng":     row["to_lng"],
                "path":       json.loads(row["path"]),
                "distance_km": row["distance_km"],
                "endpoint":   row["endpoint"],
                "hit_count":  row["hit_count"],
                "cached_at":  row["cached_at"],
            })
        if len(results) >= limit:
            break

    return results
