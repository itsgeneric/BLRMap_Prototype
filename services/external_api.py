import httpx
from core.config import GOOGLE_KEY, ROUTES_KEY, ROUTES_API_URL

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