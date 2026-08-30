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
import os
import time

print("=" * 55)
print("  Greater Bengaluru Full Road Network Downloader")
print("=" * 55)
print()

# ── Step 1: Configure OSMnx ──────────────────────────────
ox.settings.log_console = True
ox.settings.use_cache   = True

# ADD THESE TWO LINES:
ox.settings.timeout = 600             # Increase server timeout to 10 minutes
ox.settings.max_query_area_size = 5e7 # Force chunks to be 50 sq km (default is 2500 sq km)
# ox.settings.overpass_endpoint = "https://overpass-api.de/api"             # 1. Default (Germany - usually busiest)
# ox.settings.overpass_endpoint = "https://z.overpass-api.de/api"           # 2. Main Fallback (Germany)
# ox.settings.overpass_endpoint = "https://lz4.overpass-api.de/api"         # 3. Secondary Fallback (Germany)
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api"       # 4. Kumi Systems (Taiwan - very fast)
# ox.settings.overpass_endpoint = "https://overpass.openstreetmap.fr/api"   # 5. OSM France
# ox.settings.overpass_endpoint = "https://overpass.openstreetmap.ru/api"   # 6. OSM Russia
# ── Step 2: Define what roads to include ─────────────────
# This includes EVERY road type:
# motorway, trunk, primary    → big highways
# secondary, tertiary         → medium roads
# residential, living_street  → inner roads, layouts
# unclassified                → unnamed roads, cross-roads
# service                     → service lanes, parking access
# road                        → generic/unknown roads
ROAD_FILTER = (
    '["highway"~"motorway|trunk|primary|secondary|tertiary'
    '|residential|living_street|unclassified|service|road"]'
)

# ── Bounding box (replaces the old "Bengaluru, India" place lookup) ──
# Covers Devanahalli (N), Attibele (S), Seegehalli (E), Honnaganahatti (W)
# with a small buffer on each side so roads AT these towns are included,
# not just cut off at the edge.
NORTH, SOUTH, EAST, WEST = 13.28, 12.74, 77.80, 77.38

OUTPUT_FILE = "bengaluru_roads_extended.graphml"

# ── Step 3: Download ──────────────────────────────────────
print("Step 1/4 — Connecting to OpenStreetMap...")
print("         This downloads ALL road types including inner roads,")
print(f"         across bbox N={NORTH} S={SOUTH} E={EAST} W={WEST}")
print()

start = time.time()

try:
    G = ox.graph_from_bbox(
        bbox=(WEST, SOUTH, EAST, NORTH),
        custom_filter=ROAD_FILTER,
        retain_all=False,   # keep only the largest connected component
        simplify=True,      # merge straight road segments (smaller file)
    )

    elapsed = round(time.time() - start, 1)
    print(f"\nStep 2/4 — Downloaded in {elapsed}s")
    print(f"          Nodes : {len(G.nodes):,}")
    print(f"          Edges : {len(G.edges):,}")
    print()

    # ── Step 4: Set all edge weights to length only ───────
    print("Step 3/4 — Setting edge weights to length only...")
    print("          (no highway bias — all roads treated equally)")

    for u, v, k, data in G.edges(data=True, keys=True):
        # weight = physical length in metres, nothing else
        if 'length' not in data:
            data['length'] = 1.0   # fallback for edges with no length

    print("          Done.")
    print()

    # ── Step 5: Save ──────────────────────────────────────
    print(f"Step 4/4 — Saving to {OUTPUT_FILE}...")
    ox.save_graphml(G, OUTPUT_FILE)

    size_mb = round(os.path.getsize(OUTPUT_FILE) / 1024 / 1024, 1)
    print(f"          Saved. File size: {size_mb} MB")
    print()
    print("=" * 55)
    print("  Done! Graph saved.")
    print(f"  File : {OUTPUT_FILE}")
    print(f"  Nodes: {len(G.nodes):,}  |  Edges: {len(G.edges):,}")
    print()
    print("  Next step:")
    print("  Point api_server.py's ox.load_graphml(...) at")
    print(f"  {OUTPUT_FILE} to test coverage before replacing")
    print("  your current bengaluru_roads_full.graphml")
    print("=" * 55)

except Exception as e:
    print(f"\n ERROR: {e}")
    print()
    print("  Common causes:")
    print("  - No internet connection")
    print("  - OSM servers temporarily down (try again in a few minutes)")
    print("  - osmnx not installed: pip install osmnx")
    print("  - bbox parameter order changed between osmnx versions —")
    print("    check that graph_from_bbox expects (west, south, east, north)")
    print("    for your installed osmnx version")