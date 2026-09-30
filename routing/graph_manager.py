import os
import ast
import json
import pickle
from pathlib import Path
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

    @staticmethod
    def _is_restricted_or_non_motorized(data) -> bool:
        """
        Check if an edge is restricted or non-motorized based on generic OSM tags:
        - access=no/private
        - vehicle=no/private
        - motor_vehicle=no/private
        - motorcar=no/private
        - highway in non-motorized types (footway, path, pedestrian, steps, bridleway, cycleway)
          unless explicit vehicle/motor-vehicle access permits them.
        """
        def get_vals(key):
            val = data.get(key)
            if val is None:
                return set()
            if isinstance(val, list):
                return {str(x).lower().strip() for x in val}
            s = str(val).lower().strip()
            if s.startswith('[') and s.endswith(']'):
                try:
                    parsed = ast.literal_eval(s)
                    if isinstance(parsed, list):
                        return {str(x).lower().strip() for x in parsed}
                except Exception:
                    pass
            return {s}

        access = get_vals('access')
        vehicle = get_vals('vehicle')
        motor_vehicle = get_vals('motor_vehicle')
        motorcar = get_vals('motorcar')
        highway = get_vals('highway')

        perm_vals = {'yes', 'permissive', 'designated'}
        has_motor_perm = bool((motor_vehicle & perm_vals) or (vehicle & perm_vals) or (motorcar & perm_vals))

        # Explicit motor vehicle restrictions
        if motor_vehicle & {'no', 'private'}:
            return True
        if (motorcar & {'no', 'private'}) and not (motor_vehicle & perm_vals):
            return True
        if (vehicle & {'no', 'private'}) and not (motor_vehicle & perm_vals):
            return True
        if (access & {'no', 'private'}) and not has_motor_perm:
            return True

        # Non-motorized highway types unless explicit vehicle access permits them
        non_motorized = {'footway', 'path', 'pedestrian', 'steps', 'bridleway', 'cycleway'}
        if (highway & non_motorized) and not has_motor_perm:
            return True

        return False

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
        graph_path = Path(GRAPH_FILE_PATH)
        if not graph_path.exists():
            raise FileNotFoundError(
                f"GraphML file not found: '{graph_path}'. "
                "This project expects the Bangalore road network file at the repo root or inside "
                "the Data Assets folders. Check the file exists or set GRAPH_FILE_PATH in your environment."
            )

        pkl_path = graph_path.with_name('bengaluru_graph.pkl')
        if pkl_path.exists():
            print(f"Loading pre-compiled road network from {pkl_path} (lightning fast)...")
            with open(pkl_path, 'rb') as f:
                cache = pickle.load(f)
                self.G = cache['G']
                self.G_inner = cache['G_inner']
                self.bounds = cache['bounds']
                self.center = cache['center']

            # Purge any restricted edges if present in cached graph
            cached_restricted = [
                (u, v, k) for u, v, k, data in self.G.edges(keys=True, data=True)
                if self._is_restricted_or_non_motorized(data)
            ]
            if cached_restricted:
                print(f"  Removing {len(cached_restricted):,} restricted/non-motorized edges from cache...")
                self.G.remove_edges_from(cached_restricted)
                largest_cc = max(nx.strongly_connected_components(self.G), key=len)
                self.G = self.G.subgraph(largest_cc).copy()
                self.G_inner = self.G.edge_subgraph(
                    [(u, v, k) for u, v, k, d in self.G.edges(keys=True, data=True) if self._is_inner(d)]
                ).copy()
                with open(pkl_path, 'wb') as f:
                    pickle.dump({
                        'G': self.G,
                        'G_inner': self.G_inner,
                        'bounds': self.bounds,
                        'center': self.center,
                    }, f, protocol=pickle.HIGHEST_PROTOCOL)
                print("  Refreshed graph cache saved.")

            self.load_surface_penalties()
            print("Road network loaded successfully in 2 seconds!")
            return

        print(f"Loading road network from {graph_path}...")
        self.G = ox.load_graphml(str(graph_path))

        # ── Ensure every edge has a length (float) ──────────────────────────
        for u, v, key, data in self.G.edges(keys=True, data=True):
            data['length'] = float(data.get('length', 1.0))

        # ── Fill missing geometry ────────────────────────────────────────────
        # OSMnx omits the `geometry` attribute for straight two-node segments
        # (edges where the road runs in a perfectly straight line and simplify()
        # had nothing to preserve between the two endpoint nodes).
        # We synthesise a two-point LineString from the u/v node coordinates so
        # that route_nodes_to_coords() can always use the geometry path, giving
        # consistent, predictable rendering for every edge in the graph.
        from shapely.geometry import LineString
        filled = 0
        for u, v, key, data in self.G.edges(keys=True, data=True):
            if data.get('geometry') is None:
                u_data = self.G.nodes[u]
                v_data = self.G.nodes[v]
                data['geometry'] = LineString([
                    (u_data['x'], u_data['y']),
                    (v_data['x'], v_data['y']),
                ])
                filled += 1
        if filled:
            print(f"  Filled {filled:,} straight edges with synthetic 2-pt geometry.")

        # Dynamically calculate map bounds & center point
        lats = [data['y'] for _, data in self.G.nodes(data=True)]
        lngs = [data['x'] for _, data in self.G.nodes(data=True)]
        self.bounds = {
            "min_lat": min(lats), "max_lat": max(lats),
            "min_lng": min(lngs), "max_lng": max(lngs)
        }
        self.center = {"lat": sum(lats) / len(lats), "lng": sum(lngs) / len(lngs)}

        # Filter out invalid long edges and restricted/non-motorized edges
        max_lengths = {'residential': 250, 'living_street': 200, 'service': 200, 'unclassified': 400, 'tertiary': 600}
        edges_to_remove = []
        for u, v, k, data in self.G.edges(keys=True, data=True):
            hw = data.get('highway', '')
            if isinstance(hw, list): hw = hw[0]
            if hw in max_lengths and float(data.get('length', 0)) > max_lengths[hw]:
                edges_to_remove.append((u, v, k))
            elif self._is_restricted_or_non_motorized(data):
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

        # ── Cache the processed graph as a pkl for fast future loads ─────────
        print(f"Saving processed graph to {pkl_path} ...")
        with open(pkl_path, 'wb') as f:
            pickle.dump({
                'G':      self.G,
                'G_inner': self.G_inner,
                'bounds': self.bounds,
                'center': self.center,
            }, f, protocol=pickle.HIGHEST_PROTOCOL)
        print("Graph cache saved.")

    def _is_inner(self, data):
        hw = data.get('highway', 'unclassified')
        if isinstance(hw, list): hw = hw[0]
        return hw in INNER_ROAD_TYPES

    def route_nodes_to_coords(self, route):
        """
        Convert a list of OSM node IDs to a list of [lat, lng] coordinates
        that faithfully follow the edge geometries selected by the router.

        Key fixes vs. the previous version
        ------------------------------------
        1. Edge key selection: picks the same minimum-length parallel edge
           that A* implicitly chose (consistent with the router).
        2. Geometry orientation: uses BOTH u→start and v→end proximity so
           that the geometry is correctly oriented even when one endpoint
           happens to be equidistant from two geometry vertices.
        3. Reversed-edge fallback: when best_edge has `reversed=True` and no
           geometry, we look for the same OSM way stored in the opposite
           direction (v→u) in the graph, which may carry the forward geometry.
        """
        if not route:
            return []

        coords = [[self.G.nodes[route[0]]['y'], self.G.nodes[route[0]]['x']]]

        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            edge_pts = None

            if v in self.G[u]:
                # ── pick the same min-length edge key that A* used ──────────
                best_key  = min(self.G[u][v], key=lambda k: float(self.G[u][v][k].get('length', 1.0)))
                best_edge = self.G[u][v][best_key]

                geom = best_edge.get('geometry')

                # ── fallback: if this reversed copy has no geometry,
                #    check whether the forward (v→u) direction stores it ────
                if geom is None and best_edge.get('reversed') is True:
                    if v in self.G and u in self.G[v]:
                        fwd_edge = min(
                            self.G[v][u].values(),
                            key=lambda d: float(d.get('length', 1.0))
                        )
                        geom = fwd_edge.get('geometry')

                if geom is not None:
                    xs, ys = geom.xy
                    pts = list(zip(ys, xs))

                    u_lat, u_lng = self.G.nodes[u]['y'], self.G.nodes[u]['x']
                    v_lat, v_lng = self.G.nodes[v]['y'], self.G.nodes[v]['x']

                    # Score both orientations: lower total misalignment wins
                    d_fwd = (haversine_m(pts[0][0],  pts[0][1],  u_lat, u_lng) +
                             haversine_m(pts[-1][0], pts[-1][1], v_lat, v_lng))
                    d_rev = (haversine_m(pts[-1][0], pts[-1][1], u_lat, u_lng) +
                             haversine_m(pts[0][0],  pts[0][1],  v_lat, v_lng))

                    if d_rev < d_fwd:
                        pts = pts[::-1]

                    edge_pts = [list(p) for p in pts[1:]]

            if edge_pts is None:
                edge_pts = [[self.G.nodes[v]['y'], self.G.nodes[v]['x']]]

            coords.extend(edge_pts)

        return coords

graph_manager = GraphManager()