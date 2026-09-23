"""
download_graph_full.py
Downloads ALL road types for Greater Bengaluru including inner roads,
residential lanes, service roads, cross-roads etc.

UPDATED: now uses a bounding box instead of "Bengaluru, India" place lookup.
The place lookup only resolves to the BBMP municipal boundary, which
excludes Devanahalli, Electronic City, Attibele, and other outer areas
people actually commute to/from. The bbox below covers:
  north  → past Devanahalli
  south  → past Attibele
  east   → past Seegehalli / Whitefield-KR Puram side
  west   → past Honnaganahatti / Magadi Road side
This roughly follows the proposed Peripheral Ring Road alignment.

Run once — saves to bengaluru_roads_extended.graphml
Takes longer than the original BBMP-only download since the area is
much bigger — don't interrupt it.
"""

import osmnx as ox
import networkx as nx
import pickle
import os
import time

print("=" * 60)
print("  Greater Bengaluru Fresh Live Road Network Downloader")
print("  Date: 22-09-2026")
print("=" * 60)
print()

# ── Step 1: Configure OSMnx for Fresh Download ─────────────
ox.settings.log_console = True
ox.settings.use_cache   = False        # Forces fresh download from OpenStreetMap today

# Configure requests timeout across all osmnx versions (prevents the 180s read timeout error)
for attr in ["requests_timeout", "request_timeout", "timeout"]:
    if hasattr(ox.settings, attr):
        setattr(ox.settings, attr, 600)

if hasattr(ox.settings, "overpass_rate_limit"):
    ox.settings.overpass_rate_limit = True

# Candidate Overpass API endpoints in order of preference
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter"
]

# Greater Bengaluru Bounding Box:
# Covers Airport & Devanahalli (North), Electronic City & Attibele (South),
# Whitefield & Sarjapur (East), Kengeri & NICE Road (West)
# (West, South, East, North)
WEST, SOUTH, EAST, NORTH = 77.44, 12.78, 77.78, 13.22

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data Assets"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_GRAPHML = os.path.join(OUTPUT_DIR, "bengaluru_roads_extended.graphml")
OUTPUT_PKL = os.path.join(OUTPUT_DIR, "bengaluru_graph.pkl")

print(f"Greater Bengaluru Boundary:")
print(f"  North: {NORTH} (Kempegowda Int'l Airport / Devanahalli)")
print(f"  South: {SOUTH} (Electronic City / Jigani / Attibele)")
print(f"  West : {WEST}  (Kengeri / RR Nagar / Magadi Rd)")
print(f"  East : {EAST}  (Whitefield / Kadugodi / Sarjapur)")
print()

G = None
start = time.time()

for endpoint in OVERPASS_ENDPOINTS:
    print(f"Connecting to Overpass server: {endpoint} ...")
    if hasattr(ox.settings, "overpass_url"):
        ox.settings.overpass_url = endpoint
    if hasattr(ox.settings, "overpass_endpoint"):
        ox.settings.overpass_endpoint = endpoint

    try:
        # Strict filter: public drivable roads only
        # Excludes private driveways, parking aisles, gated compound roads,
        # and roads with access=private that cause phantom lines through buildings on Google Maps
        ROAD_FILTER = (
            '["highway"]["area"!~"yes"]'
            '["access"!~"private|no|customers|delivery"]'
            '["highway"!~"abandoned|bridleway|bus_guideway|construction|cycleway|'
            'footway|path|pedestrian|planned|platform|proposed|raceway|razed|steps|track"]'
            '["service"!~"parking_aisle|driveway|emergency_access|alley"]'
        )
        G = ox.graph_from_bbox(
            bbox=(WEST, SOUTH, EAST, NORTH),
            custom_filter=ROAD_FILTER,
            retain_all=False,   # Drop disconnected dead-end layout road fragments
            simplify=True,
        )
        if G is not None and len(G.nodes) > 0:
            print(f"Successfully downloaded from {endpoint}!")
            break
    except Exception as err:
        print(f"Endpoint {endpoint} failed: {err}")
        print("Trying next mirror...")

if G is None or len(G.nodes) == 0:
    print("\nERROR: Failed to download graph from all Overpass endpoints.")
    print("Please check your internet connection or try again in a few minutes.")
    exit(1)

elapsed = round(time.time() - start, 1)
print(f"\nDownloaded fresh map in {elapsed}s")
print(f"Nodes : {len(G.nodes):,}")
print(f"Edges : {len(G.edges):,}")
print()

# Ensure length attribute exists on every road edge
for u, v, k, data in G.edges(data=True, keys=True):
    data['length'] = float(data.get('length', 1.0))

# Calculate dynamic bounds and center
lats = [data['y'] for _, data in G.nodes(data=True)]
lngs = [data['x'] for _, data in G.nodes(data=True)]
bounds = {
    "min_lat": min(lats), "max_lat": max(lats),
    "min_lng": min(lngs), "max_lng": max(lngs)
}
center = {"lat": sum(lats) / len(lats), "lng": sum(lngs) / len(lngs)}

# Save fresh GraphML
print(f"Saving GraphML to {OUTPUT_GRAPHML}...")
ox.save_graphml(G, OUTPUT_GRAPHML)
size_mb = round(os.path.getsize(OUTPUT_GRAPHML) / (1024 * 1024), 1)
print(f"Saved GraphML: {size_mb} MB")

# Save fresh instant-loading PKL
print(f"Saving compiled binary PKL to {OUTPUT_PKL}...")
cache = {'G': G, 'G_inner': G, 'bounds': bounds, 'center': center}
with open(OUTPUT_PKL, 'wb') as f:
    pickle.dump(cache, f)
pkl_size_mb = round(os.path.getsize(OUTPUT_PKL) / (1024 * 1024), 1)
print(f"Saved PKL: {pkl_size_mb} MB (Ready to upload to Azure!)")

print()
print("=" * 60)
print("  ALL DONE! Fresh Bengaluru map is ready in Data Assets.")
print("=" * 60)