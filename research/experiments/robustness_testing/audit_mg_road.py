import os
import sys
import osmnx as ox
import networkx as nx

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.join(_REPO_ROOT, "backend"))

from routing.graph_manager import graph_manager
from routing.algorithms import two_wheeler_astar, build_two_wheeler_penalties, calc_route_distance, haversine_m

graph_manager.load_graph()
G = graph_manager.G
pen = build_two_wheeler_penalties()

mg_lat, mg_lng = 12.9756, 77.6066
mg_dest_lat, mg_dest_lng = 12.9770, 77.6075
n_start = ox.nearest_nodes(G, mg_lng, mg_lat)
n_end = ox.nearest_nodes(G, mg_dest_lng, mg_dest_lat)

s_lat, s_lng = G.nodes[n_start]["y"], G.nodes[n_start]["x"]
e_lat, e_lng = G.nodes[n_end]["y"], G.nodes[n_end]["x"]
euc_dist = haversine_m(s_lat, s_lng, e_lat, e_lng)

print(f"Start node: {n_start} ({s_lat:.5f}, {s_lng:.5f})")
print(f"End node:   {n_end} ({e_lat:.5f}, {e_lng:.5f})")
print(f"Euclidean / Haversine distance: {euc_dist:.1f} m")

# 1. Two-wheeler A* route
route_2w = two_wheeler_astar(G, n_start, n_end, graph_manager, penalties=pen)
dist_2w = calc_route_distance(G, route_2w)
print(f"Two-wheeler A* route: {len(route_2w)} nodes, {dist_2w:.1f} m")

# 2. Pure shortest physical distance in G (Dijkstra on length)
shortest_route = nx.shortest_path(G, n_start, n_end, weight="length")
dist_shortest = calc_route_distance(G, shortest_route)
print(f"Absolute shortest physical path in G: {len(shortest_route)} nodes, {dist_shortest:.1f} m")

# 3. Print breakdown of edges on the path
print("\nEdge details along the route:")
street_names = []
for i in range(len(route_2w) - 1):
    u, v = route_2w[i], route_2w[i+1]
    edge_dict = G[u][v]
    best_edge = min(edge_dict.values(), key=lambda d: float(d.get("length", 1.0)))
    name = best_edge.get("name", "Unnamed")
    if isinstance(name, list): name = name[0]
    hw = best_edge.get("highway", "unknown")
    if isinstance(hw, list): hw = hw[0]
    oneway = best_edge.get("oneway", False)
    length = float(best_edge.get("length", 0.0))
    if not street_names or street_names[-1][0] != name:
        street_names.append((name, hw, oneway, length))
    else:
        street_names[-1] = (name, hw, oneway, street_names[-1][3] + length)

for name, hw, oneway, length in street_names:
    print(f"  Street: {name:30s} | Class: {hw:15s} | One-way: {str(oneway):5s} | Length: {length:.1f}m")
