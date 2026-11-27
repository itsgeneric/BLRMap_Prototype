import heapq
import itertools
import math
import osmnx as ox
import networkx as nx
from core.config import (
    TWO_WHEELER_ROAD_PENALTIES, MAIN_ROAD_TYPES, INNER_ROAD_BIASED_TYPES,
    FILTER_DISCOUNT_PER_JUNCTION, FILTER_DISCOUNT_FLOOR, MIN_LANES_FOR_FILTERING,
    DEFAULT_ROUTE_SPLIT_FRACTIONS, DETOUR_TOLERANCE,
    MAJOR_TO_MINOR_TRANSITION_PENALTY_M, MINOR_ALLEY_TYPES,
    TURN_PENALTY_SHARP_M, TURN_PENALTY_MODERATE_M, TURN_THRESHOLD_SHARP_DEG, TURN_THRESHOLD_MODERATE_DEG,
    FLYOVER_MAIN_ROAD_MULTIPLIER, FLYOVER_EXCEPTION_ENABLED, JAM_COST_MULTIPLIER,
)

# Default cost multiplier for roundabout edges (a roundabout is slightly cheaper than a plain road).
ROUNDABOUT_MULTIPLIER_DEFAULT = 0.95

# Cost multiplier for any edge touching a node that Google reports as jammed. Always >= 1, so it can
# only ever raise an edge's cost (it never lowers the A* heuristic's lower bound). Phase 6 replaces it.
CONGESTED_NODE_MULTIPLIER = JAM_COST_MULTIPLIER   # core/config.py

# A* correctness notes
# --------------------
# Every edge cost is  length * M + T  where M is a product of multipliers and T >= 0 is an additive
# penalty. The A* heuristic is  h(n) = m * haversine(n, goal)  where m is a lower bound on M for any
# edge (see min_cost_multiplier). That is admissible because
#     edge cost >= m * length >= m * straight-line distance between the edge's endpoints
# and the haversine distance obeys the triangle inequality, so no path can cost less than
# m * haversine(n, goal). It is also consistent for the same reason.
# This needs `length >= straight-line distance` on every edge (true for OSM geometry).
# Turn penalties (astar_turns) are extra NON-NEGATIVE terms, so they cannot make the heuristic inadmissible.
#
# Two search implementations live here on purpose:
#   * astar_on_graph / two_wheeler_astar  node-based networkx A*; kept for the benchmarks and the Phase 5 proofs.
#   * astar_turns                         state-expanded A* over (previous node, node) with turn penalties; this is what
#                                         routing/snapping.py:plan_route (i.e. /route and /dynamic-route) uses.

def haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def _bearing_deg(lat1, lng1, lat2, lng2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lng2 - lng1)
    x = math.sin(dlam) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def _destination_point(lat, lng, bearing_deg, distance_m):
    R = 6371000.0
    phi1, lam1, theta = math.radians(lat), math.radians(lng), math.radians(bearing_deg)
    ang_dist = distance_m / R
    phi2 = math.asin(math.sin(phi1)*math.cos(ang_dist) + math.cos(phi1)*math.sin(ang_dist)*math.cos(theta))
    lam2 = lam1 + math.atan2(math.sin(theta)*math.sin(ang_dist)*math.cos(phi1), math.cos(ang_dist)-math.sin(phi1)*math.sin(phi2))
    return math.degrees(phi2), math.degrees(lam2)

def count_filterable_junctions(graph, route):
    count = 0
    for i, node in enumerate(route):
        if graph.degree(node) < 3 or i == 0: continue
        tag = graph.nodes[node].get('highway', '')
        if isinstance(tag, list): tag = tag[0] if tag else ''
        if tag != 'traffic_signals': continue
        prev = route[i - 1]
        if node not in graph[prev]: continue
        approach_edge = min(graph[prev][node].values(), key=lambda d: float(d.get('length', 1.0)))
        lanes = approach_edge.get('lanes', 1)
        if isinstance(lanes, list): lanes = lanes[0] if lanes else 1
        try: lane_cnt = int(lanes)
        except (TypeError, ValueError): lane_cnt = 1
        if lane_cnt >= MIN_LANES_FOR_FILTERING: count += 1
    return count

def apply_filtering_discount(traffic_seconds, filterable_junction_count):
    if traffic_seconds is None or filterable_junction_count <= 0: return traffic_seconds
    factor = max(FILTER_DISCOUNT_FLOOR, FILTER_DISCOUNT_PER_JUNCTION ** filterable_junction_count)
    return traffic_seconds * factor

def build_two_wheeler_penalties(main_road_penalty=1.0, inner_road_multiplier=1.0, service_multiplier=1.0, roundabout_multiplier=ROUNDABOUT_MULTIPLIER_DEFAULT):
    penalties = dict(TWO_WHEELER_ROAD_PENALTIES)
    for road_type in MAIN_ROAD_TYPES: penalties[road_type] = penalties.get(road_type, 1.25) * main_road_penalty
    for road_type in INNER_ROAD_BIASED_TYPES: penalties[road_type] = penalties.get(road_type, 1.0) * inner_road_multiplier
    penalties['service'] = penalties.get('service', 1.0) * service_multiplier
    penalties['_roundabout_multiplier'] = roundabout_multiplier
    return penalties

def _resolve_blacklist(blacklist=None):
    """Returns the given blacklist, or the process-wide edge_blacklist singleton when None."""
    if blacklist is not None:
        return blacklist
    from routing.edge_blacklist import edge_blacklist
    return edge_blacklist

def two_wheeler_edge_cost(edge_data, graph_mgr, penalties=None, u=None, v=None, congested_nodes=None, incident_nodes=None, blacklist=None):
    """
    cost = length * M + T, in metre-equivalents.
      M = road_class * congestion * incident * roundabout * surface * blacklist   (every factor applies to every edge)
      T = MAJOR_TO_MINOR_TRANSITION_PENALTY_M when a main-road node leads onto a minor road, else 0   (additive, >= 0)
    `blacklist` is optional; None uses the global edge_blacklist singleton.
    """
    length = float(edge_data.get('length', 1.0))
    hw = edge_data.get('highway', 'unclassified')
    if isinstance(hw, list): hw = hw[0]

    penalty_map = penalties or TWO_WHEELER_ROAD_PENALTIES
    penalty = penalty_map.get(hw, 1.0)  # base per-road-type multiplier

    # Flyover exception: a bridge/flyover on a main road beats any ground road (it skips junctions and signals).
    bridge = edge_data.get('bridge')
    if isinstance(bridge, list):
        bridge = bridge[0] if bridge else None
    if FLYOVER_EXCEPTION_ENABLED and bridge and str(bridge).lower() not in ('no', 'false', '0') and hw in MAIN_ROAD_TYPES:
        penalty = min(penalty, FLYOVER_MAIN_ROAD_MULTIPLIER)

    # Dynamic Congestion Penalty (avoid Google Maps traffic jams)
    if congested_nodes and (u in congested_nodes or v in congested_nodes):
        penalty *= CONGESTED_NODE_MULTIPLIER

    # Dynamic Crowd-Reported Incident Penalty (crashes, flooded roads, hazards)
    if incident_nodes and (u is not None or v is not None):
        inc_p = max(incident_nodes.get(u, 1.0), incident_nodes.get(v, 1.0))
        if inc_p > 1.0:
            penalty *= inc_p

    if edge_data.get('junction') == 'roundabout':
        penalty *= penalty_map.get('_roundabout_multiplier', ROUNDABOUT_MULTIPLIER_DEFAULT)

    if u is not None and v is not None and graph_mgr is not None:
        penalty *= graph_mgr.get_surface_penalty(u, v)

    if u is not None and v is not None:
        penalty *= _resolve_blacklist(blacklist).get_edge_penalty(u, v)

    cost = length * penalty

    # Anti-Rat-Running: Penalize transitioning from a major highway into a minor residential alley.
    # Additive, applied AFTER every multiplier (it used to return early and skip roundabout/surface/blacklist).
    if hw in MINOR_ALLEY_TYPES and u is not None and v is not None and graph_mgr is not None:
        if hasattr(graph_mgr, 'major_nodes') and u in graph_mgr.major_nodes and v not in graph_mgr.major_nodes:
            cost += MAJOR_TO_MINOR_TRANSITION_PENALTY_M

    return cost

def _plain_length_weight(u, v, d):
    """Edge length in metres. `d` is {key: attrs} for parallel edges (MultiDiGraph) or one attrs dict."""
    if isinstance(d, dict) and 'length' not in d:
        return float(min(ed.get('length', 1.0) for ed in d.values()))
    return float(d.get('length', 1.0))

def collapse_micro_loops(route_nodes, graph, max_detour_m=320.0, cost_fn=None):
    """
    Scans the route for redundant micro-loops / box detours where a route leaves a corridor
    and returns to the same corridor within a short distance (<= max_detour_m).
    Checks both direct 1-hop edges and multi-hop corridor paths.
    If a direct corridor path exists and is shorter or bypasses a box detour, collapses the loop.

    cost_fn: optional weight function (u, v, edge_data) -> cost, the SAME one the A* search used
    (see length_cost_fn / two_wheeler_cost_fn). When given, a replacement is only accepted if it does not
    cost more than the section it replaces, so it can never re-introduce blacklisted/congested edges that
    A* deliberately avoided. max_detour_m is still a physical length limit. When None, plain length is used.
    """
    if not route_nodes or len(route_nodes) < 4:
        return route_nodes

    weight = cost_fn if cost_fn is not None else _plain_length_weight
    # Legacy length-only mode tolerates a replacement up to 2 m longer when it has fewer nodes.
    # With a real cost function a replacement must never cost more.
    tie_slack = 2.0 if cost_fn is None else 0.0

    n = len(route_nodes)
    collapsed = []
    i = 0
    while i < n:
        curr = route_nodes[i]
        collapsed.append(curr)

        # Look ahead up to 15 steps (micro-loops and box detours are typically 3-12 nodes)
        shortcut_found = False
        max_lookahead = min(n, i + 15)
        for j in range(max_lookahead - 1, i + 2, -1):
            target = route_nodes[j]

            # Calculate the detour distance along route_nodes[i:j+1]
            detour_dist = 0.0
            detour_cost = 0.0
            valid_detour = True
            for k in range(i, j):
                a, b = route_nodes[k], route_nodes[k+1]
                if b in graph[a]:
                    detour_dist += float(min(d.get('length', 1.0) for d in graph[a][b].values()))
                    detour_cost += weight(a, b, graph[a][b])
                else:
                    valid_detour = False
                    break

            if not valid_detour or detour_dist > max_detour_m or detour_dist <= 5.0:
                continue

            # 1. Direct 1-hop edge
            if target in graph[curr]:
                direct_cost = weight(curr, target, graph[curr][target])
                if direct_cost < detour_cost:
                    i = j
                    shortcut_found = True
                    break

            # 2. Multi-hop corridor path (e.g. box loop around a block)
            try:
                direct_path = nx.shortest_path(graph, curr, target, weight=weight)
                direct_cost = 0.0
                for idx in range(len(direct_path) - 1):
                    du, dv = direct_path[idx], direct_path[idx+1]
                    direct_cost += weight(du, dv, graph[du][dv])

                # If direct corridor path is cheaper or replaces a multi-turn detour with fewer nodes
                if direct_cost < detour_cost - 5.0 or (direct_cost <= detour_cost + tie_slack and len(direct_path) < (j - i)):
                    collapsed.extend(direct_path[1:-1])
                    i = j
                    shortcut_found = True
                    break
            except Exception:
                continue

        if not shortcut_found:
            i += 1

    if collapsed[-1] != route_nodes[-1]:
        collapsed.append(route_nodes[-1])
    # A route that revisits a node collapses that loop to a zero-cost "path" from the node to itself, which
    # would leave the node listed twice in a row. (A* paths are simple, so this only guards other callers.)
    return _dedupe_nodes(collapsed)

def _require_positive(name, value):
    """A* needs strictly positive multipliers (zero/negative would break both the bound and Dijkstra)."""
    if not value > 0:  # also rejects NaN
        raise ValueError(f"Cost multiplier '{name}' must be > 0 for A* to be valid, got {value!r}")
    return float(value)

def min_cost_multiplier(penalties=None, graph_mgr=None, blacklist=None):
    """
    Lower bound m on the multiplicative part M of two_wheeler_edge_cost for ANY edge, derived from the
    tables the cost function actually reads (no safety margin):

      road class   min(1.0, smallest value in the penalty table, flyover multiplier if the flyover exception is enabled)
                   1.0 covers highway types not in the table; the (optional) flyover exception can set a main road to 0.8
      congestion   1.0   (the jam multiplier, >= 1, only ever raises the cost)
      incident     1.0   (applied only when > 1)
      roundabout   min(1.0, _roundabout_multiplier)   (applies only to junction=roundabout edges)
      surface      min(1.0, smallest value in graph_mgr.surface_penalties)
      blacklist    min(1.0, smallest value stored in the blacklist)

    m is the product of those lower bounds. The additive anti-rat-running term is >= 0 so it cannot lower it.
    Raises ValueError if any multiplier is <= 0. graph_mgr must expose `surface_penalties` (GraphManager does).
    """
    penalty_map = penalties or TWO_WHEELER_ROAD_PENALTIES
    class_values = [_require_positive(f"road class '{k}'", val)
                    for k, val in penalty_map.items() if not str(k).startswith('_')]
    flyover = _require_positive('flyover multiplier', FLYOVER_MAIN_ROAD_MULTIPLIER)
    class_floor = min([1.0] + class_values + ([flyover] if FLYOVER_EXCEPTION_ENABLED else []))

    roundabout = _require_positive('_roundabout_multiplier',
                                   penalty_map.get('_roundabout_multiplier', ROUNDABOUT_MULTIPLIER_DEFAULT))
    roundabout_floor = min(1.0, roundabout)

    surface_floor = 1.0
    if graph_mgr is not None:
        surface_values = [_require_positive('surface penalty', val) for val in graph_mgr.surface_penalties.values()]
        if surface_values:
            surface_floor = min(1.0, min(surface_values))

    blacklist_floor = min(1.0, _require_positive('blacklist penalty', _resolve_blacklist(blacklist).min_penalty()))

    return class_floor * roundabout_floor * surface_floor * blacklist_floor

def build_heuristic(graph, goal_node, multiplier):
    """
    Returns h(a[, b]) = multiplier * haversine(a, goal_node). The goal is fixed when this is built, so the
    optional second argument (networkx passes the target) is ignored. Admissible and consistent when
    `multiplier` is a valid lower bound (see min_cost_multiplier); the goal's coordinates are read once.
    """
    nodes = graph.nodes
    goal = nodes[goal_node]
    goal_lat, goal_lng = goal['y'], goal['x']
    def heuristic(a, b=None):
        n = nodes[a]
        return multiplier * haversine_m(n['y'], n['x'], goal_lat, goal_lng)
    return heuristic

def length_cost_fn(blacklist=None):
    """Weight function for /route: edge length x blacklist penalty (cheapest of any parallel edges)."""
    bl = _resolve_blacklist(blacklist)
    def cost(u, v, edge_data):
        bl_penalty = bl.get_edge_penalty(u, v)
        if 'length' in edge_data: return float(edge_data['length']) * bl_penalty
        return min(float(d.get('length', 1.0)) for d in edge_data.values()) * bl_penalty
    return cost

def two_wheeler_cost_fn(graph_mgr, penalties=None, congested_nodes=None, incident_nodes=None, blacklist=None):
    """Weight function for /dynamic-route: two_wheeler_edge_cost (cheapest of any parallel edges)."""
    bl = _resolve_blacklist(blacklist)
    def cost(u, v, edge_data):
        if 'length' in edge_data:
            return two_wheeler_edge_cost(edge_data, graph_mgr, penalties, u, v, congested_nodes, incident_nodes, bl)
        return min(two_wheeler_edge_cost(d, graph_mgr, penalties, u, v, congested_nodes, incident_nodes, bl) for d in edge_data.values())
    return cost

def length_cost_floor(blacklist=None):
    """
    Heuristic multiplier for the distance-based mode (/route): its cost is length x blacklist penalty, so the bound is
    min(1, smallest blacklist penalty) -- exactly 1.0 (plain haversine) while every penalty is >= 1.
    """
    return min(1.0, _require_positive('blacklist penalty', _resolve_blacklist(blacklist).min_penalty()))

def astar_on_graph(graph, start_node, end_node, blacklist=None):
    # /route stays distance-based.
    bl = _resolve_blacklist(blacklist)
    heuristic = build_heuristic(graph, end_node, length_cost_floor(bl))
    return nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=length_cost_fn(bl))

def two_wheeler_astar(graph, start_node, end_node, graph_mgr, penalties=None, congested_nodes=None, incident_nodes=None, blacklist=None):
    bl = _resolve_blacklist(blacklist)
    heuristic = build_heuristic(graph, end_node, min_cost_multiplier(penalties, graph_mgr, bl))
    cost = two_wheeler_cost_fn(graph_mgr, penalties, congested_nodes, incident_nodes, bl)
    return nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=cost)

def astar_multi(graph, sources, targets, weight, multiplier):
    """
    A* from several possible start nodes to several possible end nodes, each with an extra cost.
      sources: {node: cost already paid when starting there}     e.g. the rest of the road segment the pin sits on
      targets: {node: cost still to pay after arriving there}    e.g. the part of the segment up to the pin
      weight(u, v, edge_dict) -> cost, the same function the single-route searches use
      multiplier: valid lower bound on cost per metre (min_cost_multiplier / length_cost_floor)
    Returns (path, total) with total = source cost + path cost + target cost, minimised over every source/target pair.
    Raises nx.NetworkXNoPath if no target is reachable.

    The heuristic h(n) = min over targets of (multiplier * haversine(n, target) + extra) is admissible and consistent
    for the same reason as the single-target one, so the first goal entry popped is optimal.
    """
    nodes = graph.nodes
    goals = [(nodes[t]['y'], nodes[t]['x'], float(extra)) for t, extra in targets.items()]
    if not goals or not sources:
        raise nx.NetworkXNoPath("no sources or no targets")

    def h(n):
        nd = nodes[n]
        return min(multiplier * haversine_m(nd['y'], nd['x'], gy, gx) + extra for gy, gx, extra in goals)

    counter = itertools.count()
    best_g, parent, closed, heap = {}, {}, set(), []
    for n, g0 in sources.items():
        g0 = float(g0)
        if g0 < best_g.get(n, float('inf')):
            best_g[n], parent[n] = g0, None
            heapq.heappush(heap, (g0 + h(n), next(counter), g0, n, False))

    while heap:
        _, _, g, n, is_goal = heapq.heappop(heap)
        if is_goal:
            path = [n]
            while parent[path[-1]] is not None:
                path.append(parent[path[-1]])
            return path[::-1], g
        if n in closed or g > best_g.get(n, float('inf')):
            continue
        closed.add(n)
        if n in targets:
            total = g + float(targets[n])
            heapq.heappush(heap, (total, next(counter), total, n, True))
        for v, edge_data in graph[n].items():
            if v in closed:
                continue
            ng = g + weight(n, v, edge_data)
            if ng < best_g.get(v, float('inf')):
                best_g[v], parent[v] = ng, n
                heapq.heappush(heap, (ng + h(v), next(counter), ng, v, False))
    raise nx.NetworkXNoPath("no target reachable")

# ----------------------------------------------------------------------------------------------- turn-aware search

def turn_angle_deg(graph, prev_node, current_node, next_node):
    """Change of direction at current_node: 0 = straight on, 90 = a real turn, 180 = U-turn."""
    if prev_node is None:
        return 0.0
    p, c, n = graph.nodes[prev_node], graph.nodes[current_node], graph.nodes[next_node]
    incoming = _bearing_deg(p['y'], p['x'], c['y'], c['x'])
    outgoing = _bearing_deg(c['y'], c['x'], n['y'], n['x'])
    difference = abs(incoming - outgoing)
    return min(difference, 360.0 - difference)

def turn_penalty_m(graph, prev_node, current_node, next_node):
    """Extra cost (metres) for a meaningful change of direction; 0 for straight-on or the first move."""
    if prev_node is None:
        return 0.0
    angle = turn_angle_deg(graph, prev_node, current_node, next_node)
    if angle >= TURN_THRESHOLD_SHARP_DEG:
        return TURN_PENALTY_SHARP_M
    if angle >= TURN_THRESHOLD_MODERATE_DEG:
        return TURN_PENALTY_MODERATE_M
    return 0.0

def astar_turns(graph, sources, targets, weight, multiplier, turn_cost=None, heuristic=None):
    """
    Turn-aware A*: the search state is (previous node, node), so a turn costs what it should (the cost of turning at a
    node depends on the road you arrived on). Several start states and several end nodes are allowed, each with an
    extra cost, exactly like astar_multi.
      sources: {(previous_node_or_None, node): cost already paid when starting there}
      targets: {node: cost still to pay after arriving there}
      weight(u, v, edge_dict) -> cost;  multiplier: valid lower bound on cost per metre.
      heuristic: optional node -> lower bound of (cost to the cheapest target + that target's extra), e.g. from
                 routing/landmarks.py. It MUST be admissible and consistent; when None the multiplier * haversine bound is used.
    Returns (nodes, total, start_state). Raises nx.NetworkXNoPath if no target is reachable.

    Turn costs are >= 0, so the heuristic from astar_multi (min over targets of multiplier * haversine + extra) stays
    admissible and consistent in the state space.
    """
    turn_cost = turn_cost or turn_penalty_m
    nodes = graph.nodes
    goals = [(nodes[t]['y'], nodes[t]['x'], float(extra)) for t, extra in targets.items()]
    if not goals or not sources:
        raise nx.NetworkXNoPath("no sources or no targets")

    if heuristic is not None:
        h = heuristic
    else:
        def h(n):
            nd = nodes[n]
            return min(multiplier * haversine_m(nd['y'], nd['x'], gy, gx) + extra for gy, gx, extra in goals)

    counter = itertools.count()
    best_g, parent, closed, heap = {}, {}, set(), []
    for state, g0 in sources.items():
        g0 = float(g0)
        if g0 < best_g.get(state, float('inf')):
            best_g[state], parent[state] = g0, None
            heapq.heappush(heap, (g0 + h(state[1]), next(counter), g0, state, False))

    while heap:
        _, _, g, state, is_goal = heapq.heappop(heap)
        if is_goal:
            states = [state]
            while parent[states[-1]] is not None:
                states.append(parent[states[-1]])
            states.reverse()
            return _dedupe_nodes([s[1] for s in states]), g, states[0]
        if state in closed or g > best_g.get(state, float('inf')):
            continue
        closed.add(state)
        prev, cur = state
        if cur in targets:
            total = g + float(targets[cur])
            heapq.heappush(heap, (total, next(counter), total, state, True))
        for nxt, edge_data in graph[cur].items():
            next_state = (cur, nxt)
            if next_state in closed:
                continue
            ng = g + weight(cur, nxt, edge_data) + turn_cost(graph, prev, cur, nxt)
            if ng < best_g.get(next_state, float('inf')):
                best_g[next_state], parent[next_state] = ng, state
                heapq.heappush(heap, (ng + h(nxt), next(counter), ng, next_state, False))
    raise nx.NetworkXNoPath("no target reachable")

def astar_path_turns(graph, start_node, end_node, weight, multiplier):
    """Single start / single end convenience wrapper around astar_turns; returns the node list."""
    nodes, _, _ = astar_turns(graph, {(None, start_node): 0.0}, {end_node: 0.0}, weight, multiplier)
    return nodes

def calc_route_distance(graph, route):
    total = 0.0
    for i in range(len(route) - 1):
        a, b = route[i], route[i+1]
        if b in graph[a]:
            best = min(graph[a][b].values(), key=lambda d: float(d.get('length', 1.0)))
            total += float(best.get('length', 0))
    return total

def path_cost(graph, route, graph_mgr, penalties=None):
    total = 0.0
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        if b in graph[a]:
            total += min(two_wheeler_edge_cost(d, graph_mgr, penalties=penalties, u=a, v=b) for d in graph[a][b].values())
    return total

def _dedupe_nodes(nodes):
    deduped = []
    for n in nodes:
        if not deduped or n != deduped[-1]: deduped.append(n)
    return deduped

def _offset_split_points(from_lat, from_lng, to_lat, to_lng, fractions, offsets_m=(150, 300)):
    bearing = _bearing_deg(from_lat, from_lng, to_lat, to_lng)
    points = []
    for fraction in fractions:
        base_lat = from_lat + (to_lat - from_lat) * fraction
        base_lng = from_lng + (to_lng - from_lng) * fraction
        for offset_m in offsets_m:
            for side_bearing in (bearing + 90, bearing - 90):
                points.append(_destination_point(base_lat, base_lng, side_bearing, offset_m))
    return points

def build_split_route_candidates(graph, graph_mgr, from_lat, from_lng, to_lat, to_lng, split_fractions=DEFAULT_ROUTE_SPLIT_FRACTIONS, penalties=None):
    direct_start = ox.nearest_nodes(graph, from_lng, from_lat)
    direct_end = ox.nearest_nodes(graph, to_lng, to_lat)
    candidates = []

    try:
        direct_route = two_wheeler_astar(graph, direct_start, direct_end, graph_mgr, penalties=penalties)
        candidates.append({'strategy': 'direct', 'nodes': direct_route, 'cost': path_cost(graph, direct_route, graph_mgr, penalties=penalties)})
    except Exception as exc:
        candidates.append({'strategy': 'direct', 'nodes': [], 'cost': float('inf'), 'error': str(exc)})

    direct_length = calc_route_distance(graph, candidates[0]['nodes']) if candidates[0]['nodes'] else None
    # FIX: if direct route failed, fall back to straight-line distance so the
    # detour cap still applies instead of silently disabling it.
    fallback_cap_length = direct_length if direct_length else haversine_m(from_lat, from_lng, to_lat, to_lng)

    offset_points = _offset_split_points(from_lat, from_lng, to_lat, to_lng, split_fractions)
    split_nodes = _dedupe_nodes([ox.nearest_nodes(graph, lng, lat) for lat, lng in offset_points])

    seen_paths = {tuple(candidates[0]['nodes'])} if candidates[0]['nodes'] else set()

    for split_node in split_nodes:
        try:
            first_leg = two_wheeler_astar(graph, direct_start, split_node, graph_mgr, penalties=penalties)
            second_leg = two_wheeler_astar(graph, split_node, direct_end, graph_mgr, penalties=penalties)
            stitched = _dedupe_nodes(first_leg + second_leg[1:])

            if tuple(stitched) in seen_paths: continue
            seen_paths.add(tuple(stitched))

            if calc_route_distance(graph, stitched) > fallback_cap_length * DETOUR_TOLERANCE:
                continue

            candidates.append({
                'strategy': 'line_split',
                'nodes': stitched,
                'cost': path_cost(graph, stitched, graph_mgr, penalties=penalties)
            })
        except Exception:
            continue

    candidates.sort(key=lambda item: item['cost'])
    return candidates


# ----------------------------------------------------------------------------------------------- maneuvers

def generate_route_maneuvers(graph, route):
    """
    Turns a node route into turn-by-turn maneuvers (restored from the version that worked):
      depart, turn_left, slight_left, straight, slight_right, turn_right, u_turn, arrive
    Each maneuver is {type, instruction, road_name, distance_m, lat, lng}: the point where it happens, and the distance
    from there to the next maneuver. A 'straight' maneuver is only emitted where the road name changes.
    """
    if not route:
        return []

    if len(route) == 1:
        node_data = graph.nodes[route[0]]
        return [{
            "type": "arrive",
            "instruction": "Arrive at destination",
            "road_name": "Destination",
            "distance_m": 0.0,
            "lat": float(node_data["y"]),
            "lng": float(node_data["x"]),
        }]

    def get_edge_data(u, v):
        if v in graph[u]:
            best_key = min(graph[u][v], key=lambda k: float(graph[u][v][k].get("length", 1.0)))
            return graph[u][v][best_key]
        return {}

    def get_road_name(edge_data):
        name = edge_data.get("name")
        if not name or name == "None":
            return "Unnamed Road"
        if isinstance(name, list):
            return str(name[0]) if name else "Unnamed Road"
        return str(name)

    def get_edge_length(edge_data):
        try:
            return float(edge_data.get("length", 0.0))
        except (ValueError, TypeError):
            return 0.0

    def format_instruction(maneuver_type, road_name):
        has_name = road_name and road_name != "Unnamed Road"
        if maneuver_type == 'depart':
            return f"Depart on {road_name}" if has_name else "Depart on route"
        elif maneuver_type == 'turn_left':
            return f"Turn left onto {road_name}" if has_name else "Turn left"
        elif maneuver_type == 'slight_left':
            return f"Bear left onto {road_name}" if has_name else "Bear left"
        elif maneuver_type == 'straight':
            return f"Continue straight onto {road_name}" if has_name else "Continue straight"
        elif maneuver_type == 'slight_right':
            return f"Bear right onto {road_name}" if has_name else "Bear right"
        elif maneuver_type == 'turn_right':
            return f"Turn right onto {road_name}" if has_name else "Turn right"
        elif maneuver_type == 'u_turn':
            return f"Make a U-turn onto {road_name}" if has_name else "Make a U-turn"
        elif maneuver_type == 'arrive':
            return f"Arrive at destination on {road_name}" if has_name else "Arrive at destination"
        return "Continue"

    num_steps = len(route) - 1
    steps = []
    for i in range(num_steps):
        u, v = route[i], route[i + 1]
        ed = get_edge_data(u, v)
        steps.append({"u": u, "v": v, "length": get_edge_length(ed), "road_name": get_road_name(ed)})

    start_node = route[0]
    first_road = steps[0]["road_name"]
    maneuvers = [{
        "type": "depart",
        "instruction": format_instruction("depart", first_road),
        "road_name": first_road,
        "distance_m": 0.0,
        "lat": float(graph.nodes[start_node]["y"]),
        "lng": float(graph.nodes[start_node]["x"]),
    }]

    for i in range(num_steps):
        if i > 0:
            prev_node, curr_node, next_node = route[i - 1], route[i], route[i + 1]
            angle = turn_angle_deg(graph, prev_node, curr_node, next_node)

            prev_data, curr_data, next_data = graph.nodes[prev_node], graph.nodes[curr_node], graph.nodes[next_node]
            incoming = _bearing_deg(prev_data["y"], prev_data["x"], curr_data["y"], curr_data["x"])
            outgoing = _bearing_deg(curr_data["y"], curr_data["x"], next_data["y"], next_data["x"])
            signed_diff = (outgoing - incoming + 180.0) % 360.0 - 180.0

            prev_road = steps[i - 1]["road_name"]
            next_road = steps[i]["road_name"]

            if angle >= 140.0:
                m_type = 'u_turn'
            elif angle >= 45.0:
                m_type = 'turn_right' if signed_diff > 0 else 'turn_left'
            elif angle >= 20.0:
                m_type = 'slight_right' if signed_diff > 0 else 'slight_left'
            else:
                m_type = 'straight'

            is_turn = m_type != 'straight'
            is_new_road = (m_type == 'straight' and prev_road != next_road and next_road != "Unnamed Road")

            if is_turn or is_new_road:
                maneuvers.append({
                    "type": m_type,
                    "instruction": format_instruction(m_type, next_road),
                    "road_name": next_road,
                    "distance_m": 0.0,
                    "lat": float(curr_data["y"]),
                    "lng": float(curr_data["x"]),
                })

        maneuvers[-1]["distance_m"] += steps[i]["length"]

    dest_data = graph.nodes[route[-1]]
    last_road = steps[-1]["road_name"]
    maneuvers.append({
        "type": "arrive",
        "instruction": format_instruction("arrive", last_road),
        "road_name": last_road,
        "distance_m": 0.0,
        "lat": float(dest_data["y"]),
        "lng": float(dest_data["x"]),
    })

    for m in maneuvers:
        m["distance_m"] = round(m["distance_m"], 1)

    return maneuvers