import os
import json
import pickle
import osmnx as ox
import networkx as nx
from core.config import (
    BASE_DIR, GRAPH_FILE_PATH, GRAPH_PKL_PATH, SURFACE_QUALITY_FILE,
    INNER_ROAD_TYPES, MAIN_ROAD_TYPES,
    RESTRICTED_ACCESS_VALUES, ACCESS_ONLY_VALUES, GRAPH_CLEANUP_VERSION,
)
from routing.algorithms import haversine_m

# Ways a motor vehicle can never use.
NOT_FOR_VEHICLES = {
    'track', 'path', 'footway', 'pedestrian', 'steps', 'cycleway', 'corridor', 'bridleway', 'proposed',
    'construction', 'abandoned', 'platform', 'raceway', 'escape',
}
NEVER_SERVICE = {'emergency_access', 'ground'}
ACCESS_ONLY_SERVICE = {'parking_aisle', 'driveway', 'alley', 'parking', 'drive-through'}


def _tag(data, name):
    value = data.get(name, '')
    if isinstance(value, list):
        value = value[0] if value else ''
    return str(value).lower()


def road_class_of_access(data):
    """'removed', 'access_only' or 'public' for one edge's OpenStreetMap tags."""
    highway = _tag(data, 'highway')
    access, service = _tag(data, 'access'), _tag(data, 'service')
    motor_vehicle, motorcycle = _tag(data, 'motor_vehicle'), _tag(data, 'motorcycle')
    if highway in NOT_FOR_VEHICLES or service in NEVER_SERVICE:
        return 'removed'
    if motorcycle in RESTRICTED_ACCESS_VALUES or motor_vehicle in RESTRICTED_ACCESS_VALUES:
        return 'removed'
    # a tag for motorcycles or motor vehicles is more specific than the general `access` tag
    specific_yes = motorcycle in ('yes', 'permissive') or motor_vehicle in ('yes', 'permissive')
    if access in RESTRICTED_ACCESS_VALUES and not specific_yes:
        return 'removed'
    if (highway == 'service' or service in ACCESS_ONLY_SERVICE or access in ACCESS_ONLY_VALUES
            or motor_vehicle in ACCESS_ONLY_VALUES or motorcycle in ACCESS_ONLY_VALUES):
        return 'access_only'
    return 'public'


def classify_roads(G):
    """Removes what the public cannot drive on and marks access-only edges. Returns (removed, access_only) counts."""
    drop, marked = [], 0
    for u, v, k, data in G.edges(keys=True, data=True):
        kind = road_class_of_access(data)
        if kind == 'removed':
            drop.append((u, v, k))
        elif kind == 'access_only':
            data['access_only'] = True
            marked += 1
    G.remove_edges_from(drop)
    return len(drop), marked


def keep_connected(G):
    """
    The largest strongly connected part of the whole graph. Then, because through traffic may use only PUBLIC roads,
    every public road outside the largest strongly connected PUBLIC network (a pocket you can only reach through
    access-only roads) becomes access-only too: it stays reachable as a destination and never as a way through.
    Returns (graph, number of roads demoted).
    """
    G = G.subgraph(max(nx.strongly_connected_components(G), key=len)).copy()
    public = nx.DiGraph((u, v) for u, v, d in G.edges(data=True) if not d.get('access_only'))
    core = max(nx.strongly_connected_components(public), key=len) if len(public) else set()
    demoted = 0
    for u, v, data in G.edges(data=True):
        if not data.get('access_only') and not (u in core and v in core):
            data['access_only'] = True
            demoted += 1
    return G, demoted


class GraphManager:
    def __init__(self):
        self.G = None
        self.G_inner = None
        self.surface_penalties = {}
        self.bounds = {}
        self.center = {}
        self.major_nodes = set()

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
        pkl_path = GRAPH_PKL_PATH
        if os.path.exists(pkl_path):
            print(f"Loading compiled road network directly from binary PKL: {pkl_path}...")
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)

            compiled = isinstance(data, dict) and 'major_nodes' in data and 'G_inner' in data
            # A compiled PKL holds the graph AFTER cleanup, so it cannot be re-cleaned with new rules: rebuild from GraphML.
            stale = compiled and data.get('cleanup_version') != GRAPH_CLEANUP_VERSION and os.path.exists(GRAPH_FILE_PATH)
            if stale:
                print("Road-cleanup rules changed since this PKL was built: rebuilding from the GraphML source "
                      "(about a minute, once)...")

            # Fast binary path: If PKL already contains pre-compiled, strongly-connected graph with indexes
            if compiled and not stale:
                self.G = data['G']
                self.G_inner = data.get('G_inner')
                self.major_nodes = data.get('major_nodes', set())
                self.bounds = data.get('bounds', {})
                self.center = data.get('center', {})
                print(f"Fast binary load complete: {len(self.G.nodes):,} nodes, {len(self.G.edges):,} edges (instant boot)")
                self.load_surface_penalties()
                from routing.edge_blacklist import edge_blacklist
                edge_blacklist.load()
                return

            if stale:
                self.G = ox.load_graphml(GRAPH_FILE_PATH)
                print(f"GraphML loaded: {len(self.G.nodes):,} nodes, {len(self.G.edges):,} edges (raw)")
            else:
                self.G = data['G'] if isinstance(data, dict) else data
                print(f"PKL loaded: {len(self.G.nodes):,} nodes, {len(self.G.edges):,} edges (raw)")
        else:
            print(f"Loading full road network directly from GraphML file: {GRAPH_FILE_PATH}...")
            self.G = ox.load_graphml(GRAPH_FILE_PATH)
            print(f"GraphML loaded: {len(self.G.nodes):,} nodes, {len(self.G.edges):,} edges (raw)")

        for u, v, key, data in self.G.edges(keys=True, data=True):
            data['length'] = float(data.get('length', 1.0))

        # ── Sort roads into: removed / access-only / public (see core/config.py and routing/access.py) ──
        removed, access_only = classify_roads(self.G)
        print(f"Removed {removed:,} segments the public cannot drive on; kept {access_only:,} as access-only "
              f"(first or last stretch of a trip only)")

        # ── Keep only what is connected: the largest strongly connected component ──
        self.G, demoted = keep_connected(self.G)
        print(f"After cleanup: {len(self.G.nodes):,} nodes, {len(self.G.edges):,} edges "
              f"({demoted:,} roads reachable only through access-only roads were made access-only too)")
        # ───────────────────────────────────────────────────────────────────

        # Dynamically calculate map bounds & center point
        lats = [data['y'] for _, data in self.G.nodes(data=True)]
        lngs = [data['x'] for _, data in self.G.nodes(data=True)]
        self.bounds = {
            "min_lat": min(lats), "max_lat": max(lats),
            "min_lng": min(lngs), "max_lng": max(lngs)
        }
        self.center = {"lat": sum(lats) / len(lats), "lng": sum(lngs) / len(lngs)}

        self.G_inner = self.G.edge_subgraph(
            [(u, v, k) for u, v, k, d in self.G.edges(keys=True, data=True) if self._is_inner(d)]
        ).copy()

        # ── Index major arterial nodes for anti-rat-running transition penalties ──
        from core.config import MAJOR_HIGHWAY_TYPES
        self.major_nodes = set()
        for u, v, data in self.G.edges(data=True):
            hw = data.get('highway', '')
            if isinstance(hw, list): hw = hw[0] if hw else ''
            if hw in MAJOR_HIGHWAY_TYPES:
                self.major_nodes.add(u)
                self.major_nodes.add(v)
        print(f"Indexed {len(self.major_nodes):,} major corridor nodes for transition penalties")
        # ──────────────────────────────────────────────────────────────────────────

        self.load_surface_penalties()
        from routing.edge_blacklist import edge_blacklist
        edge_blacklist.load()

        # ── Auto-cache fully compiled graph binary for instant boots next time ──
        try:
            print(f"Caching optimized graph binary for instant boots next time to: {pkl_path}...")
            with open(pkl_path, 'wb') as f:
                pickle.dump({
                    'G': self.G,
                    'G_inner': self.G_inner,
                    'major_nodes': self.major_nodes,
                    'bounds': self.bounds,
                    'center': self.center,
                    'version': 2,
                    'cleanup_version': GRAPH_CLEANUP_VERSION,
                }, f, protocol=pickle.HIGHEST_PROTOCOL)
            print("Optimized binary PKL saved successfully.")
        except Exception as exc:
            print(f"Warning: Could not auto-cache optimized graph: {exc}")

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