"""
download_graph_full.py
Downloads ALL road types for Bengaluru including inner roads,
residential lanes, service roads, cross-roads etc.

Run once — saves to bengaluru_roads_full.graphml
Takes 5-15 minutes depending on your internet speed.
"""

import osmnx as ox
import os
import time

print("=" * 55)
print("  Bengaluru Full Road Network Downloader")
print("=" * 55)
print()

# ── Step 1: Configure OSMnx ──────────────────────────────
ox.settings.log_console = True
ox.settings.use_cache   = True   # caches OSM responses so re-runs are faster

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

OUTPUT_FILE = "bengaluru_roads_full.graphml"

# ── Step 3: Download ──────────────────────────────────────
print("Step 1/4 — Connecting to OpenStreetMap...")
print("         This downloads ALL road types including inner roads.")
print()

start = time.time()

try:
    G = ox.graph_from_place(
        "Bengaluru, India",
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
    print("  Update api_server.py to load bengaluru_roads_full.graphml")
    print("=" * 55)

except Exception as e:
    print(f"\n ERROR: {e}")
    print()
    print("  Common causes:")
    print("  - No internet connection")
    print("  - OSM servers temporarily down (try again in a few minutes)")
    print("  - osmnx not installed: pip install osmnx")