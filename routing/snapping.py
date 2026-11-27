"""
Snap a pin to the nearest ROAD (not the nearest junction), respecting one-way direction, and plan a route from/to
those points on the road.

Why: graph nodes are junctions. A pin 100 m from a long road may be closer to some side lane's junction than to either
end of that road, so "nearest junction" attached pins to the wrong street and the web page then drew a straight line from
the pin to that junction. Here the pin is projected onto the closest road edge; the route starts and ends ON that road, and
nothing is drawn between the pin and the road.

How:
  * find_snaps(): the closest directed edges to the pin (by true distance to the road's shape), within max_m.
    A two-way road is two directed edges, so both directions are candidates; a one-way road only has its legal direction.
  * Leaving the snap point you can only move FORWARD along its edge (to node_after); arriving, you come from
    node_before. So origin candidates enter the graph at node_after and destination candidates leave it at node_before,
    each paying for the partial edge, and ONE turn-aware search (astar_turns) picks the cheapest combination.
  * The search state is (previous node, node), so turning at the first junction costs what it should: the rider is
    already travelling on the snapped edge when the route begins.
  * If both pins sit on the same edge with the destination ahead, the answer is the stretch of that road between them.
"""
import math
from dataclasses import dataclass, field

import numpy as np
import networkx as nx
import osmnx as ox

from core.config import COLLAPSE_MICRO_LOOPS, FREE_FLOW_SPEED_KMH, OFF_ROAD_COST_PER_M, ACCESS_ONLY_REACH_M
from routing.access import allowed_access_edges, gate_access
from routing.algorithms import (
    astar_multi,
    astar_turns,
    build_two_wheeler_penalties,
    calc_route_distance,
    collapse_micro_loops,
    generate_route_maneuvers,
    haversine_m,
    turn_angle_deg,
    length_cost_fn,
    length_cost_floor,
    min_cost_multiplier,
    two_wheeler_cost_fn,
    _dedupe_nodes as _dedupe_node_ids,
    _resolve_blacklist,
)
from routing.graph_qa import INDEX_SPACING_M, edge_class_group


class NoRoadNearby(Exception):
    """No road within the maximum snap distance of a pin."""


@dataclass
class Snap:
    pin: tuple                 # (lat, lng) exactly as given
    point: tuple               # (lat, lng) where the route really starts / ends, on a road
    distance_m: float          # pin -> point
    node_after: int            # node reached by travelling forward from `point`
    node_before: int           # node from which `point` is reached
    after_coords: list         # [[lat, lng], ...] from `point` to node_after (first item is `point`)
    before_coords: list        # [[lat, lng], ...] from node_before to `point` (last item is `point`)
    after_m: float
    before_m: float
    edge: tuple = None         # (u, v, key) of the snapped edge; None for the nearest-junction fallback
    along_m: float = 0.0       # distance from the edge's start (u) to `point`
    length_m: float = 0.0      # geometric length of the edge
    shape: list = field(default_factory=list)   # [(lat, lng), ...] edge shape, oriented u -> v
    access_m: float = 0.0      # extra cost (metres) of reaching this start/end from the pin: only for junction candidates

    def summary(self):
        return {"lat": round(self.point[0], 6), "lng": round(self.point[1], 6), "distance_m": round(self.distance_m, 1)}


# ----------------------------------------------------------------------------------------------- geometry helpers

def _dedupe(points):
    out = []
    for p in points:
        if not out or (p[0], p[1]) != (out[-1][0], out[-1][1]):
            out.append(p)
    return out


def _edge_shape(G, u, v, key):
    """Edge shape as [(lat, lng)] oriented from u to v."""
    data = G[u][v][key]
    ux, uy = G.nodes[u]['x'], G.nodes[u]['y']
    geom = data.get('geometry')
    if geom is not None and hasattr(geom, 'xy'):
        xs, ys = geom.xy
        pts = [(float(la), float(ln)) for ln, la in zip(xs, ys)]
        if haversine_m(pts[-1][0], pts[-1][1], uy, ux) < haversine_m(pts[0][0], pts[0][1], uy, ux):
            pts.reverse()
        return pts
    return [(float(uy), float(ux)), (float(G.nodes[v]['y']), float(G.nodes[v]['x']))]


def project_onto_edge(G, edge, lat, lng):
    """Closest point of one directed edge to (lat, lng) as a Snap, or None for a degenerate edge."""
    u, v, key = edge
    shape = _edge_shape(G, u, v, key)
    kx, ky = 111320.0 * math.cos(math.radians(lat)), 110574.0
    pts = [((ln - lng) * kx, (la - lat) * ky) for la, ln in shape]    # the pin is the origin (0, 0)

    best, cum = None, 0.0
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        dx, dy = pts[i + 1][0] - ax, pts[i + 1][1] - ay
        l2 = dx * dx + dy * dy
        seg = math.sqrt(l2)
        if l2 > 0.0:
            t = max(0.0, min(1.0, -(ax * dx + ay * dy) / l2))
            dist = math.hypot(ax + t * dx, ay + t * dy)
            if best is None or dist < best[0]:
                best = (dist, i, t, cum + t * seg)
        cum += seg
    if best is None:
        return None

    dist, i, t, along = best
    a, b = shape[i], shape[i + 1]
    point = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    before = _dedupe(shape[:i + 1] + [point])
    after = _dedupe([point] + shape[i + 1:])
    return Snap(
        pin=(lat, lng), point=point, distance_m=dist,
        node_after=v, node_before=u,
        after_coords=[list(p) for p in after], before_coords=[list(p) for p in before],
        after_m=cum - along, before_m=along,
        edge=(u, v, key), along_m=along, length_m=cum, shape=shape,
    )


def find_snaps(G, index, lat, lng, max_m, tolerance_m=15.0, limit=4):
    """
    The closest road edges to a pin, nearest first: the nearest one plus any other within `tolerance_m` of it (the
    opposite direction of a two-way road, a parallel carriageway). Empty list if no road is within max_m.
    `index` is a routing.graph_qa.RoadIndex (its KD-tree finds candidate edges; distances are then exact).
    """
    x, y = index.proj.forward(lat, lng)
    pt = np.array([[float(x), float(y)]])
    radii = sorted({r for r in (60.0, 150.0, 300.0) if r < max_m} | {float(max_m)})
    snaps = []
    for r in radii:
        hits = index.tree.query_radius(pt, r=r + INDEX_SPACING_M)[0]
        if len(hits) == 0:
            continue
        found = []
        for eid in np.unique(index.edge_ids[hits]):
            s = project_onto_edge(G, index.edges[int(eid)], lat, lng)
            if s is not None and s.distance_m <= max_m:
                found.append(s)
        if found:
            snaps = found
            break
    if not snaps:
        return []
    snaps.sort(key=lambda s: s.distance_m)
    return [s for s in snaps if s.distance_m <= snaps[0].distance_m + tolerance_m][:limit]


def snap_to_node(G, lat, lng):
    """Legacy behaviour (nearest junction), used only while the road index is still being built."""
    n = ox.nearest_nodes(G, lng, lat)
    p = (float(G.nodes[n]['y']), float(G.nodes[n]['x']))
    return Snap(
        pin=(lat, lng), point=p, distance_m=haversine_m(lat, lng, p[0], p[1]),
        node_after=n, node_before=n, after_coords=[list(p)], before_coords=[list(p)], after_m=0.0, before_m=0.0,
    )


FAR_PIN_M = 30.0                 # a pin farther than this from every road is "off the road"
JUNCTION_CANDIDATES = 6
JUNCTION_EXTRA_RADIUS_M = 150.0


def nearby_junction_snaps(G, index, lat, lng, nearest_road_m, limit=JUNCTION_CANDIDATES):
    """
    Nearby road JUNCTIONS as alternative start/end points for a pin that is off the road. Snapping only to the nearest road
    segment can lock the route onto a one-way segment and force a long way round; a junction can be left or entered in any
    direction. Each candidate carries its straight-line distance from the pin as `access_m` (a ranking cost: the planner
    picks whichever candidate gives the cheapest whole trip). Nothing is drawn between the pin and the junction.
    """
    x, y = index.proj.forward(lat, lng)
    pt = np.array([[float(x), float(y)]])
    hits = index.tree.query_radius(pt, r=nearest_road_m + JUNCTION_EXTRA_RADIUS_M + INDEX_SPACING_M)[0]
    if len(hits) == 0:
        return []
    nodes = set()
    for eid in np.unique(index.edge_ids[hits]):
        u, v, _ = index.edges[int(eid)]
        nodes.add(u)
        nodes.add(v)
    found = []
    for n in nodes:
        p = (float(G.nodes[n]['y']), float(G.nodes[n]['x']))
        d = haversine_m(lat, lng, p[0], p[1])
        if d <= nearest_road_m + JUNCTION_EXTRA_RADIUS_M:
            found.append(Snap(pin=(lat, lng), point=p, distance_m=d, node_after=n, node_before=n,
                              after_coords=[list(p)], before_coords=[list(p)], after_m=0.0, before_m=0.0,
                              access_m=max(0.0, d - nearest_road_m) * OFF_ROAD_COST_PER_M))
    found.sort(key=lambda s: s.distance_m)
    return found[:limit]


def _sub_polyline(shape, f0, f1):
    """The part of `shape` between fractions f0 <= f1 of its length, as [[lat, lng], ...]."""
    cum = [0.0]
    for p, q in zip(shape, shape[1:]):
        cum.append(cum[-1] + haversine_m(p[0], p[1], q[0], q[1]))
    total = cum[-1] or 1.0

    def at(frac):
        pos = frac * total
        for i in range(len(shape) - 1):
            if cum[i + 1] >= pos:
                span = (cum[i + 1] - cum[i]) or 1.0
                t = (pos - cum[i]) / span
                return (shape[i][0] + t * (shape[i + 1][0] - shape[i][0]), shape[i][1] + t * (shape[i + 1][1] - shape[i][1]))
        return shape[-1]

    inside = [p for p, c in zip(shape, cum) if f0 * total < c < f1 * total]
    return [list(p) for p in _dedupe([at(f0)] + inside + [at(f1)])]


# ----------------------------------------------------------------------------------------------- planned duration

SHARP_TURN_DELAY_S = 5.0     # slowing down and turning at a junction (a turn of 60 degrees or more)
DEFAULT_SPEED_KMH = 16.3     # residential-type speed, used for a road class with no fitted speed


def _speed_mps(edge_attrs):
    return FREE_FLOW_SPEED_KMH.get(edge_class_group(edge_attrs.get('highway')), DEFAULT_SPEED_KMH) / 3.6


def estimate_duration_s(G, nodes, o, d, direct_distance_m=None):
    """
    Planned travel time of a route in seconds: length of every road / its free-flow speed (core/config.py FREE_FLOW_SPEED_KMH,
    fitted from Google's no-traffic times), plus SHARP_TURN_DELAY_S per sharp turn. This is the number the app shows before the
    trip and starts from while navigating; it then adapts to the rider's real pace (lib/eta.ts).
    """
    if not nodes:                                               # both pins on one road segment
        if o.edge and direct_distance_m:
            u, v, key = o.edge
            return direct_distance_m / _speed_mps(G[u][v][key])
        return 0.0

    seconds = 0.0
    if o.edge:
        u, v, key = o.edge
        seconds += o.after_m / _speed_mps(G[u][v][key])
    for a, b in zip(nodes, nodes[1:]):
        best = min(G[a][b].values(), key=lambda e: float(e.get('length', 1.0)))
        seconds += float(best.get('length', 0.0)) / _speed_mps(best)
    if d.edge:
        u, v, key = d.edge
        seconds += d.before_m / _speed_mps(G[u][v][key])

    # the turns include the junction where the rider leaves the road the pin sits on, and the one onto the destination's road
    ext = ([o.node_before] if o.edge else []) + list(nodes) + ([d.node_after] if d.edge else [])
    ext = _dedupe_node_ids(ext)
    sharp = sum(1 for a, b, c in zip(ext, ext[1:], ext[2:]) if turn_angle_deg(G, a, b, c) >= 60.0)
    return seconds + sharp * SHARP_TURN_DELAY_S


# ----------------------------------------------------------------------------------------------- maneuvers

def _edge_length_attr(G, snap):
    u, v, key = snap.edge
    try:
        return float(G[u][v][key].get('length', snap.length_m))
    except (TypeError, ValueError):
        return snap.length_m


def _direct_maneuvers(G, o, d, distance_m):
    """Depart + arrive for a trip that stays on one road segment."""
    u, v, _ = o.edge
    maneuvers = generate_route_maneuvers(G, [u, v])
    maneuvers[0].update(lat=o.point[0], lng=o.point[1], distance_m=round(distance_m, 1))
    maneuvers[-1].update(lat=d.point[0], lng=d.point[1])
    return maneuvers


def _route_maneuvers(G, nodes, o, d):
    """
    Turn-by-turn maneuvers for a planned route. The route is extended by the snapped edge at each end, so the turn at the
    first junction (leaving the road the pin sits on) and at the last one are included; 'depart' and 'arrive' are then
    moved to the snap points on the road, and the distances shortened to the part of those edges actually driven.
    """
    ext = ([o.node_before] if o.edge else []) + list(nodes) + ([d.node_after] if d.edge else [])
    maneuvers = generate_route_maneuvers(G, _dedupe_node_ids(ext))
    if len(maneuvers) < 2:
        return maneuvers
    if o.edge:
        maneuvers[0]['lat'], maneuvers[0]['lng'] = o.point
        driven = maneuvers[0]['distance_m'] - (_edge_length_attr(G, o) - o.after_m)
        maneuvers[0]['distance_m'] = round(max(0.0, driven), 1)
    if d.edge:
        maneuvers[-1]['lat'], maneuvers[-1]['lng'] = d.point
        driven = maneuvers[-2]['distance_m'] - (_edge_length_attr(G, d) - d.before_m)
        maneuvers[-2]['distance_m'] = round(max(0.0, driven), 1)
    return maneuvers


# ----------------------------------------------------------------------------------------------- planning

LANDMARK_MIN_TRIP_M = 3000.0      # shorter trips are already fast with the plain heuristic; landmarks have a fixed ~150 ms cost


def _is_long_trip(G, sources, targets):
    s = G.nodes[next(iter(sources))[1]]
    t = G.nodes[next(iter(targets))]
    return haversine_m(s['y'], s['x'], t['y'], t['x']) >= LANDMARK_MIN_TRIP_M

def _edge_cost(weight, G, snap):
    u, v, key = snap.edge
    return weight(u, v, {key: G[u][v][key]})


def plan_route(G, graph_mgr, mode, origins, destinations, penalties=None, congested_nodes=None,
               incident_nodes=None, blacklist=None, turn_aware=True, landmarks=None):
    """
    Plans the trip. Access-only roads are open within ACCESS_ONLY_REACH_M of the pins; for a place deeper inside a large
    campus or estate, where that finds no way in, the whole connected cluster is opened. See _plan_route for the rest.
    """
    args = (G, graph_mgr, mode, origins, destinations, penalties, congested_nodes, incident_nodes, blacklist,
            turn_aware, landmarks)
    try:
        return _plan_route(*args, reach_m=ACCESS_ONLY_REACH_M)
    except nx.NetworkXNoPath:
        return _plan_route(*args, reach_m=float('inf'))


def _plan_route(G, graph_mgr, mode, origins, destinations, penalties, congested_nodes, incident_nodes, blacklist,
                turn_aware, landmarks, reach_m):
    """
    mode: 'shortest' (distance x blacklist) or 'dynamic' (two-wheeler cost model). Both add turn penalties.
    origins / destinations: lists of Snap (from find_snaps or snap_to_node).
    turn_aware=False uses the old node-based search (only for comparing cost models).
    landmarks: optional routing.landmarks.Landmarks; used for 'dynamic' when valid_for() says its bounds still hold
    (same cost table, no surface/blacklist factor below 1), which makes the search several times faster.
    Returns {nodes, coords, distance_m, origin_snap, destination_snap, maneuvers}; raises nx.NetworkXNoPath if unreachable.
    `coords` starts at the origin's point ON the road and ends at the destination's point ON the road.
    """
    bl = _resolve_blacklist(blacklist)
    if mode == 'shortest':
        weight, multiplier = length_cost_fn(bl), length_cost_floor(bl)
    else:
        penalties = penalties or build_two_wheeler_penalties()
        weight = two_wheeler_cost_fn(graph_mgr, penalties, congested_nodes, incident_nodes, bl)
        multiplier = min_cost_multiplier(penalties, graph_mgr, bl)

    # access-only roads (service lanes, destination-only streets) are open only for this trip's own first / last stretch
    weight = gate_access(weight, allowed_access_edges(G, list(origins) + list(destinations), reach_m))

    def start_key(o):
        if not turn_aware:
            return o.node_after
        return (o.node_before, o.node_after) if o.edge else (None, o.node_after)

    sources, targets, src_snap, dst_snap = {}, {}, {}, {}
    for o in origins:
        cost = (_edge_cost(weight, G, o) * (o.after_m / o.length_m) if o.edge and o.length_m > 0 else 0.0) + o.access_m
        key = start_key(o)
        if cost < sources.get(key, float('inf')):
            sources[key], src_snap[key] = cost, o
    for d in destinations:
        cost = (_edge_cost(weight, G, d) * (d.before_m / d.length_m) if d.edge and d.length_m > 0 else 0.0) + d.access_m
        if cost < targets.get(d.node_before, float('inf')):
            targets[d.node_before], dst_snap[d.node_before] = cost, d

    # Both pins on the same edge with the destination further along: just drive that stretch.
    direct = None
    for o in origins:
        for d in destinations:
            if o.edge and o.edge == d.edge and d.along_m > o.along_m and o.length_m > 0:
                cost = _edge_cost(weight, G, o) * (d.along_m - o.along_m) / o.length_m
                if direct is None or cost < direct[0]:
                    direct = (cost, o, d)

    result = None
    try:
        if turn_aware:
            heuristic = None
            if (mode != 'shortest' and landmarks is not None and _is_long_trip(G, sources, targets)
                    and landmarks.valid_for(penalties, graph_mgr, bl)):
                heuristic = landmarks.heuristic(targets, multiplier, [k[1] for k in sources])
            nodes, total, start = astar_turns(G, sources, targets, weight, multiplier, heuristic=heuristic)
            result = (nodes, total, src_snap[start])
        else:
            nodes, total = astar_multi(G, sources, targets, weight, multiplier)
            result = (nodes, total, src_snap[nodes[0]])
    except nx.NetworkXNoPath:
        if direct is None:
            raise

    if result is not None and result[1] == float('inf'):
        result = None
    if result is None and direct is None:
        raise nx.NetworkXNoPath("no route without cutting through access-only roads")

    if direct is not None and (result is None or direct[0] <= result[1]):
        _, o, d = direct
        coords = _sub_polyline(o.shape, o.along_m / o.length_m, d.along_m / o.length_m)
        distance_m = d.along_m - o.along_m
        return {"nodes": [], "coords": coords, "distance_m": distance_m, "ridden_edges": [(o.edge[0], o.edge[1])],
                "duration_s": round(estimate_duration_s(G, [], o, d, distance_m), 1),
                "origin_snap": o.summary(), "destination_snap": d.summary(),
                "maneuvers": _direct_maneuvers(G, o, d, distance_m)}

    nodes, _, o = result
    d = dst_snap[nodes[-1]]
    if COLLAPSE_MICRO_LOOPS and len(nodes) >= 4:
        nodes = collapse_micro_loops(nodes, G, cost_fn=weight)
    body = graph_mgr.route_nodes_to_coords(nodes)
    coords = o.after_coords + body[1:] + d.before_coords[1:]
    distance_m = o.after_m + calc_route_distance(G, nodes) + d.before_m
    # every road ridden, in order, including the part-roads at both ends (used by the Google road check)
    ridden = [(o.node_before, o.node_after)] if o.edge and o.after_m > 1 else []
    ridden += list(zip(nodes, nodes[1:]))
    if d.edge and d.before_m > 1:
        ridden.append((d.node_before, d.node_after))
    return {"nodes": nodes, "coords": coords, "distance_m": distance_m, "ridden_edges": ridden,
            "duration_s": round(estimate_duration_s(G, nodes, o, d), 1),
            "origin_snap": o.summary(), "destination_snap": d.summary(),
            "maneuvers": _route_maneuvers(G, nodes, o, d)}
