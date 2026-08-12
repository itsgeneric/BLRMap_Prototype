import os
import json
import osmnx as ox
import networkx as nx
from core.config import GRAPH_FILE_PATH, SURFACE_QUALITY_FILE, INNER_ROAD_TYPES
from routing.algorithms import haversine_m

class GraphManager:
    def __init__(self):
        self.G = None
        self.G_inner = None
        self.surface_penalties = {}
        self.bounds = {}
        self.center = {}

    def load_surface_penalties(self, path=SURFACE_QUALITY_FILE):
        if not os.path.exists(path):
            self.surface_penalties = {}
            return
        try:
            with open(path) as f:
                raw = json.load(f)
            self.surface_penalties = {k: float(v) for k, v in raw.items()}
        except Exception as exc:
            print(f"Could not load surface quality file: {exc}")
            self.surface_penalties = {}

    def get_surface_penalty(self, u, v) -> float:
        key_fwd = f"{u}_{v}"
        key_rev = f"{v}_{u}"
        return self.surface_penalties.get(key_fwd, self.surface_penalties.get(key_rev, 1.0))

    def load_graph(self):
        print(f"Loading road network from {GRAPH_FILE_PATH}...")
        self.G = ox.load_graphml(GRAPH_FILE_PATH)
        
        for u, v, key, data in self.G.edges(keys=True, data=True):
            data['length'] = float(data.get('length', 1.0))

        # Dynamically calculate map bounds & center point
        lats = [data['y'] for _, data in self.G.nodes(data=True)]
        lngs = [data['x'] for _, data in self.G.nodes(data=True)]
        self.bounds = {
            "min_lat": min(lats), "max_lat": max(lats),
            "min_lng": min(lngs), "max_lng": max(lngs)
        }
        self.center = {"lat": sum(lats) / len(lats), "lng": sum(lngs) / len(lngs)}

        # Filter out invalid long edges
        max_lengths = {'residential': 250, 'living_street': 200, 'service': 200, 'unclassified': 400, 'tertiary': 600}
        edges_to_remove = []
        for u, v, k, data in self.G.edges(keys=True, data=True):
            hw = data.get('highway', '')
            if isinstance(hw, list): hw = hw[0]
            if hw in max_lengths and float(data.get('length', 0)) > max_lengths[hw]:
                edges_to_remove.append((u, v, k))
        self.G.remove_edges_from(edges_to_remove)

        # Retain largest strongly connected component
        largest_cc = max(nx.strongly_connected_components(self.G), key=len)
        self.G = self.G.subgraph(largest_cc).copy()

        # Extract inner roads
        self.G_inner = self.G.edge_subgraph(
            [(u, v, k) for u, v, k, d in self.G.edges(keys=True, data=True) if self._is_inner(d)]
        ).copy()

        self.load_surface_penalties()

    def _is_inner(self, data):
        hw = data.get('highway', 'unclassified')
        if isinstance(hw, list): hw = hw[0]
        return hw in INNER_ROAD_TYPES

    def route_nodes_to_coords(self, route):
        if not route: return []
        coords = [[self.G.nodes[route[0]]['y'], self.G.nodes[route[0]]['x']]]
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            edge_pts = None

            if v in self.G[u]:
                best_edge = min(self.G[u][v].values(), key=lambda d: float(d.get('length', 1.0)))
                geom = best_edge.get('geometry')
                if geom is not None:
                    xs, ys = geom.xy
                    pts = list(zip(ys, xs))
                    u_lat, u_lng = self.G.nodes[u]['y'], self.G.nodes[u]['x']
                    if haversine_m(pts[-1][0], pts[-1][1], u_lat, u_lng) < haversine_m(pts[0][0], pts[0][1], u_lat, u_lng):
                        pts = pts[::-1]
                    edge_pts = [list(p) for p in pts[1:]]

            if edge_pts is None:
                edge_pts = [[self.G.nodes[v]['y'], self.G.nodes[v]['x']]]

            coords.extend(edge_pts)
        return coords

graph_manager = GraphManager()