import os
import ast
import json
import pickle
from pathlib import Path
import osmnx as ox
import networkx as nx
from dataclasses import dataclass
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
import math
from core.config import GRAPH_FILE_PATH, SURFACE_QUALITY_FILE, INNER_ROAD_TYPES, DEFAULT_MAX_SNAPPING_DISTANCE_M
from routing.algorithms import haversine_m


@dataclass
class RoadSnap:
    """A coordinate projected onto the nearest drivable road edge."""
    lat: float            # point on the road
    lng: float
    u: int                # edge u -> v (key) that the point lies on
    v: int
    key: int
    distance_m: float     # distance from the requested coordinate to the road


@dataclass
class SnappedRoute:
    """A drawable route that starts/ends exactly on the snapped road points."""
    coords: list          # [[lat, lng], ...] along road geometry
    nodes: list           # node list; first edge contains the start point, last edge the end point
    keys: list            # parallel-edge key drawn for each nodes[i] -> nodes[i+1]
    start_trim_m: float   # length of the first edge NOT travelled (before the start point)
    end_trim_m: float     # length of the last edge NOT travelled (after the end point)


# ── Small planar helpers (local equirectangular metres; accurate at city scale) ──
def _to_xy(lat, lng, lat0):
    return ((lng) * math.cos(math.radians(lat0)) * 111320.0, lat * 110540.0)


def _project_on_polyline(pts, lat, lng):
    """Return (distance_along_m, total_length_m) of the point's projection on pts."""
    lat0 = pts[0][0]
    px, py = _to_xy(lat, lng, lat0)
    xy = [_to_xy(a, b, lat0) for a, b in pts]
    best_d2, best_along, run = float("inf"), 0.0, 0.0
    for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
        dx, dy = x2 - x1, y2 - y1
        seg = math.hypot(dx, dy)
        t = 0.0 if seg == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (seg * seg)))
        qx, qy = x1 + t * dx, y1 + t * dy
        d2 = (px - qx) ** 2 + (py - qy) ** 2
        if d2 < best_d2:
            best_d2, best_along = d2, run + t * seg
        run += seg
    return best_along, run


def _substring(pts, start_m, end_m):
    """Part of polyline pts between start_m and end_m metres along it (start_m <= end_m)."""
    lat0 = pts[0][0]
    xy = [_to_xy(a, b, lat0) for a, b in pts]
    out, run = [], 0.0

    def interp(i, t):
        return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t,
                pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t]

    for i in range(len(pts) - 1):
        seg = math.hypot(xy[i + 1][0] - xy[i][0], xy[i + 1][1] - xy[i][1])
        s0, s1 = run, run + seg
        if s1 >= start_m and s0 <= end_m and seg > 0:
            a = max(0.0, (start_m - s0) / seg)
            b = min(1.0, (end_m - s0) / seg)
            if not out:
                out.append(interp(i, a))
            out.append(interp(i, b))
        run = s1
    if not out:  # degenerate edge
        out = [list(pts[0]), list(pts[-1])]
    return out


class GraphManager:
    def __init__(self):
        self.G = None
        self.G_inner = None
        self.surface_penalties = {}
        self.bounds = {}
        self.center = {}
        self._edge_tree = None
        self._edge_ids = None

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
        service = get_vals('service')

        perm_vals = {'yes', 'permissive', 'designated'}
        has_motor_perm = bool((motor_vehicle & perm_vals) or (vehicle & perm_vals) or (motorcar & perm_vals))

        # Access values that close a road to the general public: cantonment/military
        # land, customer-only lots, bus-only lanes, permit roads, etc. Routing through
        # these draws routes across compounds that the public basemap shows as buildings.
        closed_access = {'no', 'private', 'military', 'customers', 'bus', 'psv',
                         'permit', 'delivery', 'agricultural', 'forestry', 'emergency'}

        # Explicit motor vehicle restrictions
        if motor_vehicle & {'no', 'private'}:
            return True
        if (motorcar & {'no', 'private'}) and not (motor_vehicle & perm_vals):
            return True
        if (vehicle & {'no', 'private'}) and not (motor_vehicle & perm_vals):
            return True
        if (access & closed_access) and not has_motor_perm:
            return True

        # Service ways that lead into private plots rather than connecting streets:
        # driveways, parking-lot aisles, drive-throughs and emergency-only lanes.
        if service & {'driveway', 'parking_aisle', 'drive-through', 'emergency_access'}:
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

    def validate_coordinate(
        self,
        lat: float,
        lng: float,
        max_distance_m: float = DEFAULT_MAX_SNAPPING_DISTANCE_M
    ) -> int:
        """
        Validate that input coordinates lie within the supported road network coverage.

        Performs:
        1. Type and value checking (numeric, non-NaN, non-inf, valid lat/lng range).
        2. Bounding box check against self.bounds with safety margin.
        3. Road network coverage check: ensures distance to nearest graph node
           does not exceed max_distance_m.

        Returns:
            int: The nearest valid graph node ID.
        Raises:
            TypeError: If coordinates are non-numeric.
            ValueError: If coordinates are invalid, out of bounds, or too far from road network.
        """
        if not (isinstance(lat, (int, float)) and isinstance(lng, (int, float))):
            raise TypeError(f"Coordinates must be numeric floats. Received lat={type(lat).__name__}, lng={type(lng).__name__}")
        if math.isnan(lat) or math.isnan(lng) or math.isinf(lat) or math.isinf(lng):
            raise ValueError(f"Invalid coordinate values: lat={lat}, lng={lng}")
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
            raise ValueError(f"Coordinates out of geographic range: lat={lat}, lng={lng}")

        if self.G is None or len(self.G) == 0:
            raise RuntimeError("Road network graph is not loaded. Call load_graph() first.")

        # 1. Bounding-box verification with buffer (~0.05 deg ≈ 5.5 km)
        buffer = 0.05
        b = self.bounds
        if b:
            if not (b["min_lat"] - buffer <= lat <= b["max_lat"] + buffer and
                    b["min_lng"] - buffer <= lng <= b["max_lng"] + buffer):
                raise ValueError(
                    f"Coordinates ({lat:.4f}, {lng:.4f}) lie outside the Bengaluru coverage area "
                    f"[lat: {b['min_lat']:.2f}..{b['max_lat']:.2f}, lng: {b['min_lng']:.2f}..{b['max_lng']:.2f}]."
                )

        # 2. Road network proximity validation
        nearest_node = ox.nearest_nodes(self.G, lng, lat)
        node_data = self.G.nodes[nearest_node]
        dist_m = haversine_m(lat, lng, node_data["y"], node_data["x"])

        if dist_m > max_distance_m:
            raise ValueError(
                f"Coordinate ({lat:.4f}, {lng:.4f}) is {dist_m:.1f}m from nearest road node, "
                f"exceeding the maximum allowed snapping threshold of {max_distance_m:.1f}m."
            )

        return nearest_node

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

    def route_nodes_to_coords(self, route, key_fn=None):
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
            coords.extend(self.edge_points(route[i], route[i + 1], key_fn=key_fn)[1:])

        return coords

    def edge_points(self, u, v, key=None, key_fn=None):
        """
        Oriented [[lat, lng], ...] points of edge u -> v, from u to v inclusive.

        The parallel edge drawn is `key` if given, else key_fn(u, v) if given,
        else the minimum-length edge (the one astar_on_graph uses).
        """
        u_lat, u_lng = self.G.nodes[u]['y'], self.G.nodes[u]['x']
        v_lat, v_lng = self.G.nodes[v]['y'], self.G.nodes[v]['x']

        if v not in self.G[u]:
            return [[u_lat, u_lng], [v_lat, v_lng]]

        if key is None or key not in self.G[u][v]:
            key = key_fn(u, v) if key_fn else min(
                self.G[u][v], key=lambda k: float(self.G[u][v][k].get('length', 1.0)))
        best_edge = self.G[u][v][key]

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

        if geom is None:
            return [[u_lat, u_lng], [v_lat, v_lng]]

        xs, ys = geom.xy
        pts = list(zip(ys, xs))

        # Score both orientations: lower total misalignment wins
        d_fwd = (haversine_m(pts[0][0],  pts[0][1],  u_lat, u_lng) +
                 haversine_m(pts[-1][0], pts[-1][1], v_lat, v_lng))
        d_rev = (haversine_m(pts[-1][0], pts[-1][1], u_lat, u_lng) +
                 haversine_m(pts[0][0],  pts[0][1],  v_lat, v_lng))

        if d_rev < d_fwd:
            pts = pts[::-1]

        return [[u_lat, u_lng]] + [list(p) for p in pts[1:]]

    # ------------------------------------------------------------------
    # Snapping to the nearest ROAD (edge), not the nearest junction (node)
    # ------------------------------------------------------------------

    def build_edge_index(self):
        """Spatial index over every edge geometry. Call once after load_graph()."""
        ids, geoms = [], []
        for u, v, k, d in self.G.edges(keys=True, data=True):
            g = d.get('geometry')
            if g is None:
                g = LineString([(self.G.nodes[u]['x'], self.G.nodes[u]['y']),
                                (self.G.nodes[v]['x'], self.G.nodes[v]['y'])])
            ids.append((u, v, k))
            geoms.append(g)
        self._edge_ids = ids
        self._edge_tree = STRtree(geoms)

    def snap_to_road(self, lat, lng, max_distance_m=DEFAULT_MAX_SNAPPING_DISTANCE_M) -> RoadSnap:
        """
        Project a coordinate onto the nearest drivable road segment.

        Applies the same coordinate checks as validate_coordinate(), but measures the
        distance to the road itself, so a pin beside a long straight road is not
        snapped to a junction on a different street.
        """
        self._check_coordinate(lat, lng)
        if self._edge_tree is None:
            self.build_edge_index()

        pt = Point(lng, lat)
        nearest = self._edge_tree.query_nearest(pt, return_distance=True)
        d_deg = float(nearest[1][0])
        # Degree distances are slightly anisotropic: re-rank close candidates in metres.
        cand_idx = self._edge_tree.query(pt.buffer(d_deg * 1.1 + 1e-7))

        best = None
        for i in cand_idx:
            u, v, k = self._edge_ids[int(i)]
            pts = self.edge_points(u, v, key=k)
            along, _ = _project_on_polyline(pts, lat, lng)
            q = _substring(pts, along, along)[0]
            dist = haversine_m(lat, lng, q[0], q[1])
            if best is None or dist < best.distance_m:
                best = RoadSnap(lat=q[0], lng=q[1], u=u, v=v, key=k, distance_m=dist)

        if best.distance_m > max_distance_m:
            raise ValueError(
                f"Coordinate ({lat:.4f}, {lng:.4f}) is {best.distance_m:.1f}m from the nearest road, "
                f"exceeding the maximum allowed snapping threshold of {max_distance_m:.1f}m."
            )
        return best

    def _snap_options(self, snap: RoadSnap, at_start: bool):
        """
        Graph nodes a trip can leave from (start) or arrive through (end) for a point
        on edge u->v, as (node, other_endpoint, metres_on_partial_edge). One-way
        edges only allow travel u -> v.
        """
        pts = self.edge_points(snap.u, snap.v, key=snap.key)
        along, total = _project_on_polyline(pts, snap.lat, snap.lng)
        two_way = self._reverse_passes_through(snap)
        if at_start:
            opts = [(snap.v, snap.u, total - along)]          # ride forward to v
            if two_way:
                opts.append((snap.u, snap.v, along))          # ride back to u
        else:
            opts = [(snap.u, snap.v, along)]                  # arrive from u
            if two_way:
                opts.append((snap.v, snap.u, total - along))  # arrive from v
        return opts

    def _key_through(self, a, b, snap):
        """Key of the a->b edge passing closest to the snapped point, and that distance."""
        def miss(k):
            pts = self.edge_points(a, b, key=k)
            along, _ = _project_on_polyline(pts, snap.lat, snap.lng)
            q = _substring(pts, along, along)[0]
            return haversine_m(q[0], q[1], snap.lat, snap.lng)
        return min(self.G[a][b], key=miss) if b in self.G[a] else None

    def _reverse_passes_through(self, snap, tolerance_m=2.0):
        """True if the SAME road is also travellable v -> u (not just some parallel road)."""
        if not self.G.has_edge(snap.v, snap.u):
            return False
        k = self._key_through(snap.v, snap.u, snap)
        pts = self.edge_points(snap.v, snap.u, key=k)
        along, _ = _project_on_polyline(pts, snap.lat, snap.lng)
        q = _substring(pts, along, along)[0]
        return haversine_m(q[0], q[1], snap.lat, snap.lng) <= tolerance_m

    def _travel_bearing(self, snap: RoadSnap, towards_node):
        """Compass bearing of travel along the snapped edge when riding towards `towards_node`."""
        pts = self.edge_points(snap.u, snap.v, key=snap.key)
        along, total = _project_on_polyline(pts, snap.lat, snap.lng)
        a = _substring(pts, max(0.0, along - 8.0), max(0.0, along - 8.0))[0]
        b = _substring(pts, min(total, along + 8.0), min(total, along + 8.0))[0]
        y = math.sin(math.radians(b[1] - a[1])) * math.cos(math.radians(b[0]))
        x = (math.cos(math.radians(a[0])) * math.sin(math.radians(b[0]))
             - math.sin(math.radians(a[0])) * math.cos(math.radians(b[0])) * math.cos(math.radians(b[1] - a[1])))
        forward = math.degrees(math.atan2(y, x)) % 360       # direction u -> v
        return forward if towards_node == snap.v else (forward + 180.0) % 360

    def choose_route_endpoints(self, start: RoadSnap, end: RoadSnap, heading=None):
        """
        Graph nodes to route between: the nearest legal end of each snapped edge.

        If `heading` (degrees, direction the rider is moving) is given, the start
        prefers continuing forward along the road rather than turning back, as a
        navigation app does when rerouting a moving rider.
        """
        s_opts = self._snap_options(start, True)
        if heading is not None and len(s_opts) > 1:
            def off(o):
                d = abs(self._travel_bearing(start, o[0]) - heading) % 360
                return min(d, 360 - d)
            forward = [o for o in s_opts if off(o) <= 90]
            if forward:
                s_opts = forward
        s_opts = self._avoid_dead_ends(s_opts)
        s = min(s_opts, key=lambda o: o[2])[0]
        e_opts = self._avoid_dead_ends(self._snap_options(end, False))
        e = min(e_opts, key=lambda o: o[2])[0]
        return s, e

    def _avoid_dead_ends(self, opts):
        """
        Drop an option whose node is a dead end (its only connection is back along the
        snapped road). Leaving or arriving through it would force a U-turn.
        """
        def dead_end(node, other):
            return all(w == other for w in self.G.successors(node))
        live = [o for o in opts if not dead_end(o[0], o[1])]
        return live or opts

    def build_snapped_route(self, route, start: RoadSnap, end: RoadSnap, key_fn=None):
        """
        Turn a node route between choose_route_endpoints() nodes into a drawable path
        that begins exactly at the start road point and ends at the end road point,
        following road geometry the whole way (no straight jumps, no back-tracking).

        Returns a SnappedRoute.
        """
        # Same road segment and the destination is ahead in a legal direction:
        # the trip never needs to reach a junction.
        if {start.u, start.v} == {end.u, end.v}:
            pts = self.edge_points(start.u, start.v, key=start.key)
            a, total = _project_on_polyline(pts, start.lat, start.lng)
            b, _ = _project_on_polyline(pts, end.lat, end.lng)
            if b >= a:
                return SnappedRoute(_substring(pts, a, b), [start.u, start.v], [start.key], a, total - b)
            if self._reverse_passes_through(start):
                rk = self._key_through(start.v, start.u, start)
                rev = self.edge_points(start.v, start.u, key=rk)
                ra, rt = _project_on_polyline(rev, start.lat, start.lng)
                rb, _ = _project_on_polyline(rev, end.lat, end.lng)
                if rb >= ra:
                    return SnappedRoute(_substring(rev, ra, rb), [start.v, start.u], [rk], ra, rt - rb)

        s_opts = {n: o for n, o, _ in self._snap_options(start, True)}
        e_opts = {n: o for n, o, _ in self._snap_options(end, False)}
        s_other = s_opts.get(route[0])
        e_other = e_opts.get(route[-1])

        nodes = list(route)
        # Start: if the route immediately runs back along the snapped edge, start
        # partway along that edge instead of riding to its end and U-turning.
        if not (len(nodes) >= 2 and nodes[1] == s_other) and s_other is not None:
            nodes = [s_other] + nodes
        # End: same idea for the last edge.
        if not (len(nodes) >= 2 and nodes[-2] == e_other) and e_other is not None:
            nodes = nodes + [e_other]

        def key_for(a, b, snap):
            # On the snapped road segment, draw the parallel edge that actually passes
            # through the snapped point (two different roads can join the same pair of
            # junctions, e.g. a loop around a block), in whichever direction it's ridden.
            if {a, b} != {snap.u, snap.v}:
                return None
            return self._key_through(a, b, snap)

        def resolve(a, b, key):
            if key is not None:
                return key
            return key_fn(a, b) if key_fn else min(
                self.G[a][b], key=lambda k: float(self.G[a][b][k].get('length', 1.0)))

        keys = [resolve(a, b, None) for a, b in zip(nodes, nodes[1:])]
        keys[0] = resolve(nodes[0], nodes[1], key_for(nodes[0], nodes[1], start))
        keys[-1] = resolve(nodes[-2], nodes[-1], key_for(nodes[-2], nodes[-1], end))

        first = self.edge_points(nodes[0], nodes[1], key=keys[0])
        last = self.edge_points(nodes[-2], nodes[-1], key=keys[-1])
        a, first_total = _project_on_polyline(first, start.lat, start.lng)
        b, last_total = _project_on_polyline(last, end.lat, end.lng)

        if len(nodes) == 2:
            if b < a:  # cannot happen for a legal single-edge trip; draw the whole edge
                a, b = 0.0, first_total
            return SnappedRoute(_substring(first, a, b), nodes, keys, a, first_total - b)

        coords = _substring(first, a, first_total)
        for i in range(1, len(nodes) - 2):
            coords.extend(self.edge_points(nodes[i], nodes[i + 1], key=keys[i])[1:])
        coords.extend(_substring(last, 0.0, b)[1:])
        return SnappedRoute(coords, nodes, keys, a, last_total - b)

    def _check_coordinate(self, lat, lng):
        if not (isinstance(lat, (int, float)) and isinstance(lng, (int, float))):
            raise TypeError(f"Coordinates must be numeric floats. Received lat={type(lat).__name__}, lng={type(lng).__name__}")
        if math.isnan(lat) or math.isnan(lng) or math.isinf(lat) or math.isinf(lng):
            raise ValueError(f"Invalid coordinate values: lat={lat}, lng={lng}")
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
            raise ValueError(f"Coordinates out of geographic range: lat={lat}, lng={lng}")
        if self.G is None or len(self.G) == 0:
            raise RuntimeError("Road network graph is not loaded. Call load_graph() first.")
        buffer = 0.05
        b = self.bounds
        if b and not (b["min_lat"] - buffer <= lat <= b["max_lat"] + buffer and
                      b["min_lng"] - buffer <= lng <= b["max_lng"] + buffer):
            raise ValueError(
                f"Coordinates ({lat:.4f}, {lng:.4f}) lie outside the Bengaluru coverage area "
                f"[lat: {b['min_lat']:.2f}..{b['max_lat']:.2f}, lng: {b['min_lng']:.2f}..{b['max_lng']:.2f}]."
            )

graph_manager = GraphManager()