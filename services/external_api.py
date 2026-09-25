import httpx
from core.config import (
    GOOGLE_KEY, ROUTES_KEY, ROUTES_API_URL,
    ROADS_KEY, ROADS_SNAP_API_URL, SNAP_DEVIATION_THRESHOLD_M
)

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
    params = {"input": q, "key": GOOGLE_KEY, "components": "country:in", "radius": 50000, "language": "en"}
    results = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get("https://maps.googleapis.com/maps/api/place/autocomplete/json", params=params)
            for prediction in res.json().get("predictions", [])[:5]:
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
    return {"results": results}

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


async def snap_and_verify_route(route_nodes: list, graph, threshold_m: float = SNAP_DEVIATION_THRESHOLD_M):
    """
    Sends route coordinates to Google Roads Snap to Roads API.
    Identifies any edges along the route where:
      1) The snapped road point is > threshold_m away from the original edge midpoint, or
      2) Google cannot snap the point to any road nearby.
    Marks those bad edges in edge_blacklist to avoid routing through them in the future.
    """
    if not ROADS_KEY or not route_nodes or len(route_nodes) < 2:
        return []

    from routing.algorithms import haversine_m
    from routing.edge_blacklist import edge_blacklist

    # Major road categories that are guaranteed to be public thoroughfares on Google Maps
    MAJOR_HIGHWAYS = {
        'motorway', 'motorway_link', 'trunk', 'trunk_link',
        'primary', 'primary_link', 'secondary', 'secondary_link',
        'tertiary', 'tertiary_link'
    }

    candidate_edges = []
    for i in range(len(route_nodes) - 1):
        u = route_nodes[i]
        v = route_nodes[i + 1]

        # Skip if already blacklisted
        if edge_blacklist.get_edge_penalty(u, v) > 1.0:
            continue

        if v not in graph[u]:
            continue

        best_edge = min(graph[u][v].values(), key=lambda d: float(d.get('length', 1.0)))
        hw = best_edge.get('highway', 'unclassified')
        if isinstance(hw, list):
            hw = hw[0] if hw else 'unclassified'
        hw_str = str(hw).lower()

        if hw_str in MAJOR_HIGHWAYS:
            continue

        # Extract representative midpoint
        geom = best_edge.get('geometry')
        if geom is not None and hasattr(geom, 'xy'):
            xs, ys = geom.xy
            pts = list(zip(ys, xs))
            mid_pt = pts[len(pts) // 2]
            mid_lat, mid_lng = float(mid_pt[0]), float(mid_pt[1])
        else:
            mid_lat = (float(graph.nodes[u]['y']) + float(graph.nodes[v]['y'])) / 2.0
            mid_lng = (float(graph.nodes[u]['x']) + float(graph.nodes[v]['x'])) / 2.0

        candidate_edges.append((u, v, mid_lat, mid_lng, hw_str))

    if not candidate_edges:
        return []

    flagged_edges = []
    chunk_size = 100
    # Process candidates in chunks of up to 100 points
    for chunk_start in range(0, min(len(candidate_edges), 300), chunk_size):
        sampled_edges = candidate_edges[chunk_start:chunk_start + chunk_size]
        path_str = "|".join(f"{lat:.6f},{lng:.6f}" for _, _, lat, lng, _ in sampled_edges)
        params = {
            "path": path_str,
            "interpolate": "false",
            "key": ROADS_KEY,
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(ROADS_SNAP_API_URL, params=params)

            if res.status_code != 200:
                print(f"[SnapToRoads] API warning: HTTP {res.status_code} - {res.text[:200]}")
                continue

            data = res.json()
            snapped_points = data.get("snappedPoints", [])

            # Map originalIndex -> (lat, lng, place_id)
            snapped_by_index = {}
            for sp in snapped_points:
                orig_idx = sp.get("originalIndex")
                if orig_idx is not None:
                    loc = sp.get("location", {})
                    snapped_by_index[orig_idx] = (
                        loc.get("latitude"),
                        loc.get("longitude"),
                        sp.get("placeId")
                    )

            for idx, (u, v, orig_lat, orig_lng, hw) in enumerate(sampled_edges):
                if idx not in snapped_by_index:
                    # Point could not be snapped to any road in Google Maps
                    edge_blacklist.mark_edge_bad(
                        u, v,
                        deviation_m=999.0,
                        reason="no_gmaps_road_found",
                        metadata={"highway": hw, "lat": orig_lat, "lng": orig_lng}
                    )
                    flagged_edges.append((u, v, 999.0, "no_snap"))
                else:
                    snapped_lat, snapped_lng, place_id = snapped_by_index[idx]
                    if snapped_lat is not None and snapped_lng is not None:
                        dev_m = haversine_m(orig_lat, orig_lng, snapped_lat, snapped_lng)
                        if dev_m > threshold_m:
                            edge_blacklist.mark_edge_bad(
                                u, v,
                                deviation_m=dev_m,
                                reason="excessive_snap_deviation",
                                metadata={
                                    "highway": hw,
                                    "orig_lat": orig_lat, "orig_lng": orig_lng,
                                    "snapped_lat": snapped_lat, "snapped_lng": snapped_lng,
                                    "place_id": place_id
                                }
                            )
                            flagged_edges.append((u, v, dev_m, "deviation_exceeded"))

        except Exception as exc:
            print(f"[SnapToRoads] Route verification failed: {type(exc).__name__} - {exc}")

    if flagged_edges:
        print(f"[SnapToRoads] Flagged {len(flagged_edges)} non-existent/private edges (> {threshold_m}m deviation). Total blacklisted: {edge_blacklist.count()}")

    return flagged_edges
