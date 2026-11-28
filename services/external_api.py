import httpx
from core.config import (
    GOOGLE_KEY, ROUTES_KEY, ROUTES_API_URL,
    ROADS_KEY, ROADS_SNAP_API_URL, VERIFY_SHADOW_MODE,
    ROAD_VERIFY_MAX_DEVIATION_M, ROAD_VERIFY_SPACING_M, ROAD_VERIFY_MAX_REQUESTS
)


def _mark_bad(u, v, **kwargs):
    """
    Ban an edge in the blacklist -- unless the verification runs in SHADOW MODE (the default): then only log what
    WOULD have been banned. The scattered-midpoint check produced snap deviations of 94-645 m (Google snapping the test
    point onto a different road) and banned real roads, so it must not change routing until it is redesigned.
    """
    if VERIFY_SHADOW_MODE:
        print(f"[Verify:shadow] would blacklist {u}-{v}: {kwargs.get('reason')} "
              f"(deviation {kwargs.get('deviation_m')} m) -- NOT banned")
        return
    from routing.edge_blacklist import edge_blacklist
    edge_blacklist.mark_edge_bad(u, v, **kwargs)


def decode_polyline(encoded: str):
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

async def fetch_traffic_data(client: httpx.AsyncClient, from_lat, from_lng, to_lat, to_lng):
    """Fetches the route and extracts specific coordinates of heavy congestion."""
    if not ROUTES_KEY: return None, []
    
    body = {
        "origin": {"location": {"latLng": {"latitude": from_lat, "longitude": from_lng}}},
        "destination": {"location": {"latLng": {"latitude": to_lat, "longitude": to_lng}}},
        "travelMode": "TWO_WHEELER",
        "routingPreference": "TRAFFIC_AWARE",
        "extraComputations": ["TRAFFIC_ON_POLYLINE"]
    }
    
    # We need the polyline, duration, and the speed reading intervals
    headers = {
        "Content-Type": "application/json", 
        "X-Goog-Api-Key": ROUTES_KEY, 
        "X-Goog-FieldMask": "routes.duration,routes.polyline.encodedPolyline,routes.travelAdvisory.speedReadingIntervals"
    }
    
    try:
        res = await client.post(ROUTES_API_URL, json=body, headers=headers, timeout=8.0)
        res.raise_for_status()
        routes = res.json().get("routes")
        if not routes: return None, []
        
        route = routes[0]
        duration = float(route.get("duration", "").rstrip("s"))
        
        # Decode the polyline into a list of [lat, lng]
        encoded_poly = route.get("polyline", {}).get("encodedPolyline", "")
        coords = decode_polyline(encoded_poly)
        
        # Identify Congestion Points
        congestion_coords = []
        intervals = route.get("travelAdvisory", {}).get("speedReadingIntervals", [])
        
        for interval in intervals:
            speed = interval.get("speed")
            # Google maps 'TRAFFIC_JAM' and 'SLOW' to heavy congestion
            if speed in ["TRAFFIC_JAM", "SEVERE"]:
                start_idx = interval.get("startPolylinePointIndex", 0)
                end_idx = interval.get("endPolylinePointIndex", len(coords) - 1)
                # Collect the coordinates where the jam is happening
                congestion_coords.extend(coords[start_idx:end_idx + 1])
                
        return duration, congestion_coords
        
    except Exception as exc:
        print(f"Routes API traffic fetch failed: {type(exc).__name__} - {exc}")
        return None, []
    
async def search_places(q: str):
    if not GOOGLE_KEY: return await _search_nominatim(q)
    results = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try Places API (New) first
            auto_url = "https://places.googleapis.com/v1/places:autocomplete"
            auto_body = {
                "input": q,
                "includedRegionCodes": ["in"],
                "locationBias": {
                    "circle": {
                        "center": {"latitude": 12.9716, "longitude": 77.5946},
                        "radius": 50000.0
                    }
                }
            }
            auto_headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": GOOGLE_KEY
            }
            res = await client.post(auto_url, json=auto_body, headers=auto_headers)
            
            if res.status_code == 200:
                suggestions = res.json().get("suggestions", [])[:5]
                for sugg in suggestions:
                    pred = sugg.get("placePrediction", {})
                    place_id = pred.get("placeId")
                    if not place_id:
                        continue
                    
                    det_url = f"https://places.googleapis.com/v1/places/{place_id}"
                    det_headers = {
                        "X-Goog-Api-Key": GOOGLE_KEY,
                        "X-Goog-FieldMask": "id,displayName,formattedAddress,location"
                    }
                    det_res = await client.get(det_url, headers=det_headers)
                    if det_res.status_code == 200:
                        details = det_res.json()
                        loc = details.get("location", {})
                        if "latitude" in loc and "longitude" in loc:
                            disp = details.get("displayName", {})
                            name = disp.get("text") if isinstance(disp, dict) else str(disp)
                            if not name:
                                name = pred.get("text", {}).get("text", "").split(",")[0]
                            results.append({
                                "name": name,
                                "address": details.get("formattedAddress", pred.get("text", {}).get("text", "")),
                                "lat": float(loc["latitude"]),
                                "lng": float(loc["longitude"]),
                            })
                if results:
                    return {"results": results}

            # Fallback to Legacy Places API if Places (New) didn't return
            params = {"input": q, "key": GOOGLE_KEY, "components": "country:in", "radius": 50000, "language": "en"}
            legacy_res = await client.get("https://maps.googleapis.com/maps/api/place/autocomplete/json", params=params)
            for prediction in legacy_res.json().get("predictions", [])[:5]:
                det = await client.get("https://maps.googleapis.com/maps/api/place/details/json", params={
                    "place_id": prediction["place_id"], "key": GOOGLE_KEY, "fields": "name,formatted_address,geometry"
                })
                details = det.json().get("result", {})
                if "geometry" in details:
                    results.append({
                        "name": details.get("name", prediction["structured_formatting"]["main_text"]),
                        "address": details.get("formatted_address", ""),
                        "lat": details["geometry"]["location"]["lat"],
                        "lng": details["geometry"]["location"]["lng"],
                    })
    except Exception as e:
        print(f"Places search failed: {e}")
        return await _search_nominatim(q)
    return {"results": results if results else (await _search_nominatim(q)).get("results", [])}

async def _search_nominatim(q: str):
    params = {"q": f"{q}, Bengaluru", "format": "json", "addressdetails": 1, "limit": 5}
    headers = {"User-Agent": "BLR-Router/2.0"}
    results = []
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=10.0)
            for place in res.json():
                results.append({"name": place.get("display_name", "").split(",")[0], "address": place.get("display_name", ""), "lat": float(place.get("lat", 0)), "lng": float(place.get("lon", 0))})
    except Exception as e:
        print(f"Nominatim error: {e}")
    return {"results": results}


async def snap_route_to_roads(coords: list) -> list:
    """
    Snaps a list of [lat, lng] route coordinates to actual road centerlines
    using the Google Roads API with interpolate=true.

    With interpolation enabled, the Roads API fills in all intermediate road
    geometry between the supplied sample points, so the returned coordinates
    literally lie on road centerlines — no more phantom lines through buildings.

    The Roads API allows max 100 points per request with interpolation.
    We evenly sample up to 100 waypoints from the full coordinate list.

    Returns the snapped+interpolated coordinate list, or the original list
    if the API is unavailable or returns an error.
    """
    if not ROADS_KEY or not coords or len(coords) < 2:
        return coords

    # Sample up to 100 evenly-spaced points (Roads API limit with interpolate=true)
    MAX_SNAP_POINTS = 100
    if len(coords) <= MAX_SNAP_POINTS:
        sampled = coords
    else:
        step = (len(coords) - 1) / (MAX_SNAP_POINTS - 1)
        sampled = [coords[round(i * step)] for i in range(MAX_SNAP_POINTS - 1)] + [coords[-1]]

    path_str = "|".join(f"{lat:.6f},{lng:.6f}" for lat, lng in sampled)
    params = {
        "path": path_str,
        "interpolate": "true",
        "key": ROADS_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(ROADS_SNAP_API_URL, params=params)

        if res.status_code != 200:
            print(f"[SnapToRoads] Snap failed: HTTP {res.status_code} - {res.text[:200]}")
            return coords

        data = res.json()
        snapped_points = data.get("snappedPoints", [])
        if not snapped_points:
            return coords

        snapped_coords = [
            [sp["location"]["latitude"], sp["location"]["longitude"]]
            for sp in snapped_points
            if "location" in sp
        ]

        if len(snapped_coords) < 2:
            return coords

        print(f"[SnapToRoads] Snapped route: {len(coords)} -> {len(snapped_coords)} points (road-hugging)")
        return snapped_coords

    except Exception as exc:
        print(f"[SnapToRoads] snap_route_to_roads failed: {type(exc).__name__} - {exc}")
        return coords


# ---------------------------------------------------------------------------
# Road check: is every smaller road on the route a road that Google Maps has?
# ---------------------------------------------------------------------------

# Through roads of these classes are not tested.
MAJOR_HIGHWAYS = {
    'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link',
    'tertiary', 'tertiary_link'
}
MAX_POINT_GAP_M = 300.0             # the Roads API expects a continuous trail: start a new request after a longer jump
_confirmed_roads: set = set()       # (u, v) Google has confirmed while this server runs: not paid for twice


def _edge_points(graph, u, v):
    """(highway, [(lat, lng), ...] test points spread ALONG the road from u to v)."""
    from routing.algorithms import haversine_m
    edge = min(graph[u][v].values(), key=lambda d: float(d.get('length', 1.0)))
    highway = edge.get('highway', 'unclassified')
    if isinstance(highway, list):
        highway = highway[0] if highway else 'unclassified'

    start = (float(graph.nodes[u]['y']), float(graph.nodes[u]['x']))
    end = (float(graph.nodes[v]['y']), float(graph.nodes[v]['x']))
    geometry = edge.get('geometry')
    if geometry is not None and hasattr(geometry, 'xy'):
        xs, ys = geometry.xy
        shape = [(float(la), float(ln)) for ln, la in zip(xs, ys)]
        if haversine_m(*shape[0], *end) < haversine_m(*shape[0], *start):
            shape.reverse()
    else:
        shape = [start, end]

    lengths = [haversine_m(*p, *q) for p, q in zip(shape, shape[1:])]
    total = sum(lengths)
    count = max(3, int(total // ROAD_VERIFY_SPACING_M))
    points = []
    for i in range(1, count + 1):
        target, walked = total * i / (count + 1), 0.0       # inside the road, never on a junction
        for (p, q), length in zip(zip(shape, shape[1:]), lengths):
            if walked + length >= target and length > 0:
                t = (target - walked) / length
                points.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
                break
            walked += length
    return str(highway).lower(), points


def _batches(samples):
    """Splits the trail into requests of at most 100 points with no long jump inside one."""
    from routing.algorithms import haversine_m
    batch = []
    for sample in samples:
        if batch and (len(batch) == 100 or haversine_m(*batch[-1][1], *sample[1]) > MAX_POINT_GAP_M):
            yield batch
            batch = []
        batch.append(sample)
    if batch:
        yield batch


async def snap_and_verify_route(edges: list, graph, threshold_m: float = ROAD_VERIFY_MAX_DEVIATION_M):
    """
    Checks the route's smaller roads against Google's road network (Roads API, snapToRoads).

    edges: [(u, v), ...] in the order they are ridden.
    Returns (bad_edges, status). A road is bad when MOST of its test points are not on any Google road, or lie more than
    threshold_m from the road Google matches them to; each is blocked in both directions. status is
        'checked'      every road was tested (bad_edges may be non-empty)
        'unavailable'  Google could not be asked about some roads (no key, refused, network): nothing is assumed about them
    An error from Google never blocks a road.
    """
    from routing.algorithms import haversine_m

    if not ROADS_KEY:
        print("[RoadCheck] No Google key: roads are NOT being checked.")
        return [], 'unavailable'

    samples = []                                            # (edge, point)
    highways = {}
    for u, v in edges:
        if (u, v) in _confirmed_roads or v not in graph[u]:
            continue
        highway, points = _edge_points(graph, u, v)
        if highway in MAJOR_HIGHWAYS:
            continue
        highways[(u, v)] = highway
        samples.extend(((u, v), p) for p in points)
    if not samples:
        return [], 'checked'

    results: dict = {}                                      # edge -> [(point on a Google road?, deviation)]
    incomplete: set = set()
    batches = list(_batches(samples))
    for batch in batches[ROAD_VERIFY_MAX_REQUESTS:]:
        incomplete.update(edge for edge, _ in batch)

    async with httpx.AsyncClient(timeout=10.0) as client:
        for batch in batches[:ROAD_VERIFY_MAX_REQUESTS]:
            params = {
                "path": "|".join(f"{lat:.6f},{lng:.6f}" for _, (lat, lng) in batch),
                "interpolate": "false",
                "key": ROADS_KEY,
            }
            try:
                res = await client.get(ROADS_SNAP_API_URL, params=params)
                if res.status_code != 200:
                    print(f"[RoadCheck] Google refused the check (HTTP {res.status_code}): {res.text[:200]}\n"
                          "[RoadCheck] Is the 'Roads API' enabled for the key?")
                    incomplete.update(edge for edge, _ in batch)
                    continue
                snapped = {}
                for point in res.json().get("snappedPoints", []):
                    index = point.get("originalIndex")
                    if index is not None:
                        location = point.get("location", {})
                        snapped.setdefault(index, (location.get("latitude"), location.get("longitude")))
            except Exception as exc:
                print(f"[RoadCheck] Check failed: {type(exc).__name__} - {exc}")
                incomplete.update(edge for edge, _ in batch)
                continue
            for index, (edge, (lat, lng)) in enumerate(batch):
                match = snapped.get(index)
                deviation = haversine_m(lat, lng, match[0], match[1]) if match else None
                results.setdefault(edge, []).append((deviation is not None and deviation <= threshold_m, deviation))

    bad = []
    for edge, checks in results.items():
        if edge in incomplete:                              # only part of it was answered: no verdict
            continue
        failed = [deviation for ok, deviation in checks if not ok]
        if 2 * len(failed) <= len(checks):                  # one stray point is not evidence
            _confirmed_roads.add(edge)
            continue
        measured = [d for d in failed if d is not None]
        u, v = edge
        bad.append(edge)
        _mark_bad(
            u, v,
            deviation_m=max(measured) if measured else 999.0,
            reason="not_on_google_maps",
            metadata={"highway": highways[edge], "points_failed": len(failed), "points_tested": len(checks)},
        )

    if bad:
        print(f"[RoadCheck] {len(bad)} road(s) on this route are not on Google Maps")
    if VERIFY_SHADOW_MODE:
        bad = []                                            # shadow mode: report only, never re-route
    return bad, 'unavailable' if incomplete else 'checked'


async def fetch_arrival_path(client: httpx.AsyncClient, from_lat, from_lng, to_lat, to_lng):
    """
    Google's two-wheeler route to the destination, as [(lat, lng), ...], used only to find which road a place is
    approached from (routing/arrival.py). None when Google cannot be asked or has no route: never an error.
    """
    if not ROUTES_KEY:
        return None
    body = {
        "origin": {"location": {"latLng": {"latitude": from_lat, "longitude": from_lng}}},
        "destination": {"location": {"latLng": {"latitude": to_lat, "longitude": to_lng}}},
        "travelMode": "TWO_WHEELER",
        "routingPreference": "TRAFFIC_UNAWARE",
        "polylineQuality": "HIGH_QUALITY",
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": ROUTES_KEY,
        "X-Goog-FieldMask": "routes.polyline.encodedPolyline",
    }
    try:
        res = await client.post(ROUTES_API_URL, json=body, headers=headers, timeout=10.0)
        if res.status_code != 200:
            print(f"[Arrival] Google Routes API HTTP {res.status_code}: {res.text[:200]}")
            return None
        routes = res.json().get("routes") or []
        encoded = routes[0].get("polyline", {}).get("encodedPolyline", "") if routes else ""
        return [(point[0], point[1]) for point in decode_polyline(encoded)] or None
    except Exception as exc:
        print(f"[Arrival] Google request failed: {type(exc).__name__} - {exc}")
        return None
