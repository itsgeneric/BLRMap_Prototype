import os
import sys
import networkx as nx
import osmnx as ox

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.join(_REPO_ROOT, "backend"))

from routing.graph_manager import graph_manager
from routing.algorithms import (
    two_wheeler_astar,
    build_two_wheeler_penalties,
    calc_route_distance,
    build_split_route_candidates,
    haversine_m
)

graph_manager.load_graph()
G = graph_manager.G

print("Total nodes:", G.number_of_nodes())
print("Total edges:", G.number_of_edges())

# 1. Find one-way edges
oneway_edges = [
    (u, v, d) for u, v, d in G.edges(data=True)
    if d.get("oneway") in (True, "True", 1, "yes")
    and not G.has_edge(v, u)
]
print(f"Found {len(oneway_edges):,} strictly one-way edges (no reverse edge)")
if oneway_edges:
    u_ow, v_ow, d_ow = oneway_edges[100]
    print(f"Sample one-way: {u_ow} -> {v_ow}, highway={d_ow.get('highway')}, name={d_ow.get('name')}, length={d_ow.get('length')}")

# 2. Find dead-end leaf nodes (in-degree 1, out-degree 1 to same neighbor)
dead_end_nodes = [
    n for n in G.nodes()
    if G.out_degree(n) == 1 and G.in_degree(n) == 1
    and list(G.successors(n))[0] == list(G.predecessors(n))[0]
]
print(f"Found {len(dead_end_nodes):,} cul-de-sac / dead-end leaf nodes")
if dead_end_nodes:
    de_node = dead_end_nodes[100]
    de_parent = list(G.successors(de_node))[0]
    print(f"Sample dead-end leaf: node {de_node} connected only to parent {de_parent}")

# 3. Find ultra-short edge (< 50m)
short_edges = [
    (u, v, d) for u, v, d in G.edges(data=True)
    if 10.0 < float(d.get("length", 100)) < 45.0
]
print(f"Found {len(short_edges):,} short edges (10m - 45m)")
if short_edges:
    u_sh, v_sh, d_sh = short_edges[100]
    print(f"Sample short edge: {u_sh} -> {v_sh}, length={d_sh.get('length'):.2f}m")

# 4. Find long-distance pair (> 35 km)
# Bounding box of G
lats = [d['y'] for _, d in G.nodes(data=True)]
lngs = [d['x'] for _, d in G.nodes(data=True)]
min_lat, max_lat = min(lats), max(lats)
min_lng, max_lng = min(lngs), max(lngs)
print(f"Graph bounds: lat [{min_lat:.4f}, {max_lat:.4f}], lng [{min_lng:.4f}, {max_lng:.4f}]")

# Top north-west vs bottom south-east nodes
north_node = ox.nearest_nodes(G, (min_lng + max_lng)/2, max_lat - 0.01)
south_node = ox.nearest_nodes(G, (min_lng + max_lng)/2, min_lat + 0.01)
north_lat, north_lng = G.nodes[north_node]['y'], G.nodes[north_node]['x']
south_lat, south_lng = G.nodes[south_node]['y'], G.nodes[south_node]['x']
span_dist = haversine_m(north_lat, north_lng, south_lat, south_lng)
print(f"North node: {north_node} ({north_lat:.4f}, {north_lng:.4f})")
print(f"South node: {south_node} ({south_lat:.4f}, {south_lng:.4f})")
print(f"Span haversine distance: {span_dist/1000.0:.2f} km")

# 5. Test identical OD on two_wheeler_astar and build_split_route_candidates
penalties = build_two_wheeler_penalties()
test_node = list(G.nodes())[500]
test_lat, test_lng = G.nodes[test_node]['y'], G.nodes[test_node]['x']
r_identical = two_wheeler_astar(G, test_node, test_node, graph_manager, penalties=penalties)
print("Identical OD route:", r_identical, "Distance:", calc_route_distance(G, r_identical))

try:
    cands = build_split_route_candidates(G, test_lat, test_lng, test_lat, test_lng, graph_manager, penalties=penalties, return_diagnostics=True)
    print("Identical OD candidates count:", len(cands['candidates']), "Surviving:", cands['surviving_count'])
except Exception as e:
    print("Identical OD candidates raised:", type(e).__name__, str(e))

# 6. Test out-of-bounds nearest_nodes
oob_lat, oob_lng = 13.0, 82.0 # Bay of Bengal (~450 km east)
snapped = ox.nearest_nodes(G, oob_lng, oob_lat)
snap_lat, snap_lng = G.nodes[snapped]['y'], G.nodes[snapped]['x']
snap_err = haversine_m(oob_lat, oob_lng, snap_lat, snap_lng)
print(f"Out of bounds ({oob_lat}, {oob_lng}) snapped to node {snapped} ({snap_lat:.4f}, {snap_lng:.4f}) with error {snap_err/1000.0:.1f} km!")
