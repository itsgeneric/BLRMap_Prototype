import math
import heapq
import itertools
import time

import osmnx as ox
import networkx as nx

from core.config import (
    DEFAULT_MAX_SNAPPING_DISTANCE_M,
    TWO_WHEELER_ROAD_PENALTIES,
    MAIN_ROAD_TYPES,
    INNER_ROAD_BIASED_TYPES,
    FILTER_DISCOUNT_PER_JUNCTION,
    FILTER_DISCOUNT_FLOOR,
    MIN_LANES_FOR_FILTERING,
    DEFAULT_ROUTE_SPLIT_FRACTIONS,
    DETOUR_TOLERANCE
)


# Lowest possible multiplier any edge can get
# (bridge=0.8, roundabout default=0.95).
# For standard admissible A*, the Euclidean/Haversine distance must be multiplied
# by this floor (h = h_dist * MIN_PENALTY_FLOOR) to guarantee h(n) <= c*(n, goal).
# In aggressive mode, dividing by MIN_PENALTY_FLOOR (h = h_dist / 0.8 = 1.25 * h_dist)
# acts as an overestimating heuristic for faster exploration.
MIN_PENALTY_FLOOR = 0.8


# ============================================================
# TURN PENALTY SETTINGS
# ============================================================

# Penalty is expressed in the same cost units as road length.
# It is applied only to actual direction changes.
TURN_PENALTY_SHARP = 25.0
TURN_PENALTY_MODERATE = 8.0

# Ignore tiny direction changes caused by graph geometry.
TURN_THRESHOLD_MODERATE = 30.0
TURN_THRESHOLD_SHARP = 60.0


def haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000.0

    phi1, phi2 = math.radians(lat1), math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlam / 2) ** 2
    )

    return R * 2 * math.asin(math.sqrt(a))


def _bearing_deg(lat1, lng1, lat2, lng2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lng2 - lng1)

    x = math.sin(dlam) * math.cos(phi2)

    y = (
        math.cos(phi1) * math.sin(phi2)
        - math.sin(phi1)
        * math.cos(phi2)
        * math.cos(dlam)
    )

    return (math.degrees(math.atan2(x, y)) + 360) % 360


def _destination_point(lat, lng, bearing_deg, distance_m):
    R = 6371000.0

    phi1 = math.radians(lat)
    lam1 = math.radians(lng)
    theta = math.radians(bearing_deg)

    ang_dist = distance_m / R

    phi2 = math.asin(
        math.sin(phi1) * math.cos(ang_dist)
        + math.cos(phi1)
        * math.sin(ang_dist)
        * math.cos(theta)
    )

    lam2 = lam1 + math.atan2(
        math.sin(theta)
        * math.sin(ang_dist)
        * math.cos(phi1),
        math.cos(ang_dist)
        - math.sin(phi1) * math.sin(phi2)
    )

    return math.degrees(phi2), math.degrees(lam2)


# ============================================================
# TURN CALCULATION
# ============================================================

def _turn_angle(graph, prev_node, current_node, next_node):
    """
    Calculate the change in direction at current_node.

    Returns:
        0 degrees   -> essentially straight
        90 degrees  -> real turn
        180 degrees -> U-turn
    """

    if prev_node is None:
        return 0.0

    prev_data = graph.nodes[prev_node]
    current_data = graph.nodes[current_node]
    next_data = graph.nodes[next_node]

    incoming = _bearing_deg(
        prev_data["y"],
        prev_data["x"],
        current_data["y"],
        current_data["x"]
    )

    outgoing = _bearing_deg(
        current_data["y"],
        current_data["x"],
        next_data["y"],
        next_data["x"]
    )

    difference = abs(incoming - outgoing)

    return min(difference, 360.0 - difference)


def _turn_penalty(graph, prev_node, current_node, next_node):
    """
    Return an additional cost for making a meaningful turn.
    """

    if prev_node is None:
        return 0.0

    angle = _turn_angle(
        graph,
        prev_node,
        current_node,
        next_node
    )

    if angle >= TURN_THRESHOLD_SHARP:
        return TURN_PENALTY_SHARP

    if angle >= TURN_THRESHOLD_MODERATE:
        return TURN_PENALTY_MODERATE

    return 0.0


# ============================================================
# FILTERING
# ============================================================

def count_filterable_junctions(graph, route):
    count = 0

    for i, node in enumerate(route):

        if graph.degree(node) < 3 or i == 0:
            continue

        tag = graph.nodes[node].get("highway", "")

        if isinstance(tag, list):
            tag = tag[0] if tag else ""

        if tag != "traffic_signals":
            continue

        prev = route[i - 1]

        if node not in graph[prev]:
            continue

        approach_edge = min(
            graph[prev][node].values(),
            key=lambda d: float(d.get("length", 1.0))
        )

        lanes = approach_edge.get("lanes", 1)

        if isinstance(lanes, list):
            lanes = lanes[0] if lanes else 1

        try:
            lane_cnt = int(lanes)
        except (TypeError, ValueError):
            lane_cnt = 1

        if lane_cnt >= MIN_LANES_FOR_FILTERING:
            count += 1

    return count


def apply_filtering_discount(
    traffic_seconds,
    filterable_junction_count
):
    if traffic_seconds is None or filterable_junction_count <= 0:
        return traffic_seconds

    factor = max(
        FILTER_DISCOUNT_FLOOR,
        FILTER_DISCOUNT_PER_JUNCTION
        ** filterable_junction_count
    )

    return traffic_seconds * factor


# ============================================================
# ROAD PENALTIES
# ============================================================

def build_two_wheeler_penalties(
    main_road_penalty=1.0,
    inner_road_multiplier=1.0,
    service_multiplier=1.0,
    roundabout_multiplier=0.95
):
    penalties = dict(TWO_WHEELER_ROAD_PENALTIES)

    for road_type in MAIN_ROAD_TYPES:
        penalties[road_type] = (
            penalties.get(road_type, 1.25)
            * main_road_penalty
        )

    for road_type in INNER_ROAD_BIASED_TYPES:
        penalties[road_type] = (
            penalties.get(road_type, 1.0)
            * inner_road_multiplier
        )

    penalties["service"] = (
        penalties.get("service", 1.0)
        * service_multiplier
    )

    penalties["_roundabout_multiplier"] = roundabout_multiplier

    return penalties


def two_wheeler_edge_cost(
    edge_data,
    graph_mgr,
    penalties=None,
    u=None,
    v=None,
    congested_nodes=None
):
    length = float(edge_data.get("length", 1.0))

    hw = edge_data.get(
        "highway",
        "unclassified"
    )

    if isinstance(hw, list):
        hw = hw[0]

    penalty_map = (
        penalties
        or TWO_WHEELER_ROAD_PENALTIES
    )

    penalty = penalty_map.get(
        hw,
        1.0
    )

    # --------------------------------------------------------
    # Flyover Exception
    # --------------------------------------------------------

    is_bridge = edge_data.get("bridge")

    if isinstance(is_bridge, list):
        is_bridge = is_bridge[0]

    if is_bridge and is_bridge not in [
        "no",
        "false",
        "0"
    ]:

        if hw in MAIN_ROAD_TYPES:
            penalty = 0.8

    # --------------------------------------------------------
    # Dynamic Congestion Penalty
    # --------------------------------------------------------

    if congested_nodes and (
        u in congested_nodes
        or v in congested_nodes
    ):
        penalty *= 25.0

    # --------------------------------------------------------
    # Roundabout
    # --------------------------------------------------------

    if edge_data.get("junction") == "roundabout":

        penalty *= penalty_map.get(
            "_roundabout_multiplier",
            0.95
        )

    # --------------------------------------------------------
    # Surface
    # --------------------------------------------------------

    if (
        u is not None
        and v is not None
        and graph_mgr is not None
    ):
        penalty *= graph_mgr.get_surface_penalty(
            u,
            v
        )

    return length * penalty


# ============================================================
# NORMAL SHORTEST PATH
# ============================================================

def astar_on_graph(
    graph,
    start_node,
    end_node
):
    """
    Shortest Path A* with turn penalties.

    Uses base road length as edge cost, but tracks (previous_node, current_node)
    to penalize unnecessary sharp turns, preventing unrealistic shortcuts
    through private compounds or erratic zig-zag alleys.
    """

    def heuristic(node):
        return haversine_m(
            graph.nodes[node]["y"],
            graph.nodes[node]["x"],
            graph.nodes[end_node]["y"],
            graph.nodes[end_node]["x"]
        )

    start_state = (
        None,
        start_node
    )

    g_score = {
        start_state: 0.0
    }

    came_from = {}
    counter = itertools.count()
    open_set = []

    heapq.heappush(
        open_set,
        (
            heuristic(start_node),
            next(counter),
            start_state
        )
    )

    while open_set:
        _, _, state = heapq.heappop(open_set)
        previous_node, current_node = state
        current_cost = g_score[state]

        if current_node == end_node:
            states = []
            current_state = state
            while True:
                states.append(current_state)
                if current_state == start_state:
                    break
                current_state = came_from[current_state]

            states.reverse()
            route = [s[1] for s in states]
            return _dedupe_nodes(route)

        for next_node in graph.successors(current_node):
            edge_data = graph.get_edge_data(current_node, next_node)
            if edge_data is None:
                continue

            if "length" in edge_data:
                edge_cost = float(edge_data["length"])
            else:
                edge_cost = min(
                    float(d.get("length", 1.0))
                    for d in edge_data.values()
                )

            turn_cost = _turn_penalty(
                graph,
                previous_node,
                current_node,
                next_node
            )

            new_cost = current_cost + edge_cost + turn_cost
            next_state = (current_node, next_node)

            if next_state not in g_score or new_cost < g_score[next_state]:
                g_score[next_state] = new_cost
                came_from[next_state] = state
                priority = new_cost + heuristic(next_node)
                heapq.heappush(
                    open_set,
                    (
                        priority,
                        next(counter),
                        next_state
                    )
                )

    raise nx.NetworkXNoPath(
        f"No path between {start_node} and {end_node}"
    )


# ============================================================
# TWO-WHEELER A*
# ============================================================

def two_wheeler_astar(
    graph,
    start_node,
    end_node,
    graph_mgr,
    penalties=None,
    congested_nodes=None,
    heuristic_mode="admissible",
    return_metrics=False,
    initial_previous_node=None,
    banned_nodes=None,
    banned_edges=None,
    transition_cost=None
):
    """
    Two-wheeler A* with:

    1. Road-type preferences
    2. Congestion penalties
    3. Surface penalties
    4. Bridge / roundabout handling
    5. Actual maneuver / turn penalties

    The A* state contains:

        (previous_node, current_node)

    This is necessary because turn cost depends on
    the road we arrived from.

    Heuristic modes:
    - 'admissible' (default): h(n) = haversine(n, goal) * MIN_PENALTY_FLOOR
      Admissible and consistent; guarantees shortest path optimality.
    - 'aggressive': h(n) = haversine(n, goal) / MIN_PENALTY_FLOOR
      Legacy overestimating heuristic (1.25 * haversine); faster search, may be suboptimal.
    - 'dijkstra' or 'zero': h(n) = 0.0
      Uniform-cost search baseline without heuristic guidance.

    transition_cost: optional callable (previous_node, current_node, next_node) -> float,
      a non-negative extra cost for moving from edge (previous, current) onto edge
      (current, next). None (default) adds nothing, so results are identical to the
      model without it. Being non-negative, it never breaks heuristic admissibility.
    """

    start_time = time.perf_counter() if return_metrics else 0.0

    def heuristic(node):
        h_dist = haversine_m(
            graph.nodes[node]["y"],
            graph.nodes[node]["x"],
            graph.nodes[end_node]["y"],
            graph.nodes[end_node]["x"]
        )
        if heuristic_mode in ("zero", "dijkstra"):
            return 0.0
        elif heuristic_mode == "aggressive":
            return h_dist / MIN_PENALTY_FLOOR
        elif heuristic_mode == "admissible":
            return h_dist * MIN_PENALTY_FLOOR
        else:
            raise ValueError(
                f"Unknown heuristic_mode: '{heuristic_mode}'. "
                f"Valid modes: 'admissible', 'aggressive', 'dijkstra', 'zero'."
            )

    # State:
    # (previous_node, current_node)

    start_state = (
        initial_previous_node,
        start_node
    )

    g_score = {
        start_state: 0.0
    }

    came_from = {}

    counter = itertools.count()

    open_set = []

    heapq.heappush(
        open_set,
        (
            heuristic(start_node),
            next(counter),
            start_state
        )
    )

    expanded_states = 0
    visited_nodes = set()
    explored_transitions = 0

    while open_set:

        _, _, state = heapq.heappop(
            open_set
        )

        expanded_states += 1
        previous_node, current_node = state
        visited_nodes.add(current_node)

        current_cost = g_score[state]

        # ----------------------------------------------------
        # Destination reached
        # ----------------------------------------------------

        if current_node == end_node:

            states = []
            current_state = state

            while True:

                states.append(
                    current_state
                )

                if current_state == start_state:
                    break

                current_state = came_from[
                    current_state
                ]

            states.reverse()

            route = [
                s[1]
                for s in states
            ]

            deduped_route = _dedupe_nodes(route)

            if return_metrics:
                runtime_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    "route": deduped_route,
                    "cost": current_cost,
                    "expanded_states": expanded_states,
                    "expanded_nodes": len(visited_nodes),
                    "explored_transitions": explored_transitions,
                    "runtime_ms": runtime_ms,
                    "heuristic_mode": heuristic_mode,
                }

            return deduped_route

        # ----------------------------------------------------
        # Explore neighbours
        # ----------------------------------------------------

        for next_node in graph.successors(
            current_node
        ):

            if banned_nodes and next_node in banned_nodes:
                continue

            if banned_edges and (current_node, next_node) in banned_edges:
                continue

            explored_transitions += 1

            edge_data = graph.get_edge_data(
                current_node,
                next_node
            )

            if edge_data is None:
                continue

            # Multi-edge support
            if "length" in edge_data:

                edge_cost = two_wheeler_edge_cost(
                    edge_data,
                    graph_mgr,
                    penalties,
                    current_node,
                    next_node,
                    congested_nodes
                )

            else:

                edge_cost = min(
                    two_wheeler_edge_cost(
                        data,
                        graph_mgr,
                        penalties,
                        current_node,
                        next_node,
                        congested_nodes
                    )
                    for data in edge_data.values()
                )

            # ------------------------------------------------
            # TURN COST
            # ------------------------------------------------

            turn_cost = _turn_penalty(
                graph,
                previous_node,
                current_node,
                next_node
            )

            new_cost = (
                current_cost
                + edge_cost
                + turn_cost
            )

            if transition_cost is not None and previous_node is not None:
                new_cost += transition_cost(previous_node, current_node, next_node)

            next_state = (
                current_node,
                next_node
            )

            if (
                next_state not in g_score
                or new_cost < g_score[next_state]
            ):

                g_score[next_state] = new_cost

                came_from[next_state] = state

                priority = (
                    new_cost
                    + heuristic(next_node)
                )

                heapq.heappush(
                    open_set,
                    (
                        priority,
                        next(counter),
                        next_state
                    )
                )

    raise nx.NetworkXNoPath(
        f"No path between {start_node} and {end_node}"
    )


# ============================================================
# ROUTE DISTANCE
# ============================================================

def calc_route_distance(
    graph,
    route
):
    total = 0.0

    for i in range(len(route) - 1):

        a = route[i]
        b = route[i + 1]

        if b in graph[a]:

            best = min(
                graph[a][b].values(),
                key=lambda d: float(
                    d.get("length", 1.0)
                )
            )

            total += float(
                best.get("length", 0)
            )

    return total


# ============================================================
# ROUTE VALIDATION & DIVERSITY METRICS (PHASE 10)
# ============================================================

def is_valid_connected_route(graph, route):
    """
    Verify that a sequence of nodes forms a continuous, connected path in graph.
    """
    if not route or not isinstance(route, (list, tuple)) or len(route) < 2:
        return False
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        if u not in graph or v not in graph[u]:
            return False
    return True


def get_route_edge_lengths(graph, route, undirected=False):
    """
    Extract the physical length (meters) of each edge traversed in route.
    If undirected=True, returns canonical keys: (min(u, v), max(u, v)).
    If undirected=False, returns directed keys: (u, v).
    """
    if not route or len(route) < 2:
        return {}

    edge_lengths = {}
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        if u not in graph or v not in graph[u]:
            continue
        edge_data = graph[u][v]
        length = min(float(d.get("length", 1.0)) for d in edge_data.values())
        key = (min(u, v), max(u, v)) if undirected else (u, v)
        edge_lengths[key] = length

    return edge_lengths


def calc_shared_edge_length(graph, route1, route2, undirected=False):
    """
    Calculate the total physical length in meters of edges shared between route1 and route2.
    """
    edges1 = get_route_edge_lengths(graph, route1, undirected=undirected)
    edges2 = get_route_edge_lengths(graph, route2, undirected=undirected)
    shared_keys = set(edges1.keys()) & set(edges2.keys())
    return sum(edges1[k] for k in shared_keys)


def calc_route_overlap(graph, primary_route, alt_route, undirected=False):
    """
    Calculate edge overlap ratio:
    Overlap(P_primary, P_alt) = SharedEdgeLength / AlternativeRouteEdgeLength
    """
    if not alt_route or len(alt_route) < 2:
        return 0.0
    alt_edges = get_route_edge_lengths(graph, alt_route, undirected=undirected)
    alt_len = sum(alt_edges.values())
    if alt_len <= 0.0:
        return 0.0
    shared_len = calc_shared_edge_length(graph, primary_route, alt_route, undirected=undirected)
    return min(1.0, max(0.0, shared_len / alt_len))


def calc_jaccard_similarity(graph, route1, route2, undirected=False):
    """
    Calculate Jaccard edge similarity:
    J(P1, P2) = SharedEdgeLength / UnionEdgeLength
    where UnionEdgeLength = Length(P1) + Length(P2) - SharedEdgeLength.
    """
    if not route1 or not route2 or len(route1) < 2 or len(route2) < 2:
        return 0.0
    edges1 = get_route_edge_lengths(graph, route1, undirected=undirected)
    edges2 = get_route_edge_lengths(graph, route2, undirected=undirected)
    len1 = sum(edges1.values())
    len2 = sum(edges2.values())
    shared_keys = set(edges1.keys()) & set(edges2.keys())
    shared_len = sum(edges1[k] for k in shared_keys)
    union_len = len1 + len2 - shared_len
    if union_len <= 0.0:
        return 1.0 if route1 == route2 else 0.0
    return min(1.0, max(0.0, shared_len / union_len))


def calc_pairwise_diversity(graph, routes, undirected=False):
    """
    Calculate average pairwise route diversity:
    Diversity = 1 - mean(Jaccard(Pi, Pj)) for all distinct pairs (i < j).
    Returns 1.0 if all routes are completely disjoint, 0.0 if identical.
    """
    valid_routes = [r for r in routes if r and len(r) >= 2]
    if len(valid_routes) < 2:
        return 0.0
    pairs = 0
    sim_sum = 0.0
    for i in range(len(valid_routes)):
        for j in range(i + 1, len(valid_routes)):
            sim_sum += calc_jaccard_similarity(graph, valid_routes[i], valid_routes[j], undirected=undirected)
            pairs += 1
    return 1.0 - (sim_sum / pairs) if pairs > 0 else 0.0


# ============================================================
# ROUTE COST
# ============================================================

def path_cost(
    graph,
    route,
    graph_mgr,
    penalties=None,
    congested_nodes=None
):
    total = 0.0

    for i in range(len(route) - 1):

        a = route[i]
        b = route[i + 1]

        if b not in graph[a]:
            continue

        edge_cost = min(
            two_wheeler_edge_cost(
                d,
                graph_mgr,
                penalties=penalties,
                u=a,
                v=b,
                congested_nodes=congested_nodes
            )
            for d in graph[a][b].values()
        )

        total += edge_cost

        # Add actual maneuver cost
        if i > 0:

            previous = route[i - 1]

            total += _turn_penalty(
                graph,
                previous,
                a,
                b
            )

    return total


# ============================================================
# ROUTE NODE HELPERS
# ============================================================

def _dedupe_nodes(nodes):

    deduped = []

    for n in nodes:

        if not deduped or n != deduped[-1]:
            deduped.append(n)

    return deduped


# ============================================================
# SPLIT POINT GENERATION
# ============================================================

def _offset_split_points(
    from_lat,
    from_lng,
    to_lat,
    to_lng,
    fractions,
    offsets_m=(150, 300)
):
    bearing = _bearing_deg(
        from_lat,
        from_lng,
        to_lat,
        to_lng
    )

    points = []

    for fraction in fractions:

        base_lat = (
            from_lat
            + (to_lat - from_lat)
            * fraction
        )

        base_lng = (
            from_lng
            + (to_lng - from_lng)
            * fraction
        )

        for offset_m in offsets_m:

            for side_bearing in (
                bearing + 90,
                bearing - 90
            ):

                points.append(
                    _destination_point(
                        base_lat,
                        base_lng,
                        side_bearing,
                        offset_m
                    )
                )

    return points


# ============================================================
# SPLIT ROUTE CANDIDATES
# ============================================================

def build_split_route_candidates(
    graph,
    graph_mgr,
    from_lat,
    from_lng,
    to_lat,
    to_lng,
    split_fractions=DEFAULT_ROUTE_SPLIT_FRACTIONS,
    penalties=None,
    max_overlap=0.70,
    max_detour=DETOUR_TOLERANCE,
    max_alternatives=3,
    undirected=False,
    return_diagnostics=False,
    max_snapping_distance=DEFAULT_MAX_SNAPPING_DISTANCE_M
):
    """
    Generate alternative route candidates using perpendicular offsets and 2-leg A* stitching.
    
    Applies the Phase 10 diversity filtering pipeline:
    1. Exact duplicate sequence suppression.
    2. Maximum detour constraint (detour_ratio <= max_detour, default 1.20).
    3. Edge overlap filtering (overlap <= max_overlap, default 0.70).
    4. Connectivity and validity checks.
    5. Jaccard similarity and diversity computation.
    """

    if graph_mgr is not None and hasattr(graph_mgr, "validate_coordinate"):
        direct_start = graph_mgr.validate_coordinate(from_lat, from_lng, max_snapping_distance)
        direct_end = graph_mgr.validate_coordinate(to_lat, to_lng, max_snapping_distance)
    else:
        direct_start = ox.nearest_nodes(graph, from_lng, from_lat)
        direct_end = ox.nearest_nodes(graph, to_lng, to_lat)

    # --------------------------------------------------------
    # Identical OD Guard: If start and end snap to identical node,
    # return direct zero-distance route immediately with 0 alternatives.
    # --------------------------------------------------------
    if direct_start == direct_end:
        primary_entry = {
            "strategy": "direct",
            "nodes": [direct_start],
            "cost": 0.0,
            "distance": 0.0,
            "detour_ratio": 1.0,
            "overlap_ratio": 1.0,
            "jaccard_similarity": 1.0,
        }
        if return_diagnostics:
            return {
                "candidates": [primary_entry],
                "direct_route": primary_entry,
                "diverse_alternatives": [],
                "generated_count": 0,
                "rejected_candidates": [],
                "surviving_count": 0,
            }
        return [primary_entry]

    candidates = []

    # --------------------------------------------------------
    # Direct route (Primary)
    # --------------------------------------------------------

    try:
        direct_route = two_wheeler_astar(
            graph,
            direct_start,
            direct_end,
            graph_mgr,
            penalties=penalties
        )
        direct_dist = calc_route_distance(graph, direct_route)
        direct_cost = path_cost(
            graph,
            direct_route,
            graph_mgr,
            penalties=penalties
        )

        candidates.append({
            "strategy": "direct",
            "nodes": direct_route,
            "cost": direct_cost,
            "distance": direct_dist,
            "detour_ratio": 1.0,
            "overlap_ratio": 1.0,
            "jaccard_similarity": 1.0,
        })

    except Exception as exc:
        candidates.append({
            "strategy": "direct",
            "nodes": [],
            "cost": float("inf"),
            "distance": 0.0,
            "detour_ratio": 1.0,
            "overlap_ratio": 1.0,
            "jaccard_similarity": 1.0,
            "error": str(exc)
        })

    primary_nodes = candidates[0]["nodes"]
    direct_length = (
        candidates[0]["distance"]
        if primary_nodes
        else None
    )

    # --------------------------------------------------------
    # Detour cap
    # --------------------------------------------------------

    fallback_cap_length = (
        direct_length
        if direct_length
        else haversine_m(
            from_lat,
            from_lng,
            to_lat,
            to_lng
        )
    )

    # --------------------------------------------------------
    # Generate split points
    # --------------------------------------------------------

    offset_points = _offset_split_points(
        from_lat,
        from_lng,
        to_lat,
        to_lng,
        split_fractions
    )

    split_nodes = _dedupe_nodes([
        ox.nearest_nodes(
            graph,
            lng,
            lat
        )
        for lat, lng in offset_points
    ])

    seen_paths = (
        {
            tuple(primary_nodes)
        }
        if primary_nodes
        else set()
    )

    # --------------------------------------------------------
    # Build split candidates & filter
    # --------------------------------------------------------

    diverse_alternatives = []
    rejected_candidates = []
    generated_count = 0

    for split_node in split_nodes:

        try:
            first_leg = two_wheeler_astar(
                graph,
                direct_start,
                split_node,
                graph_mgr,
                penalties=penalties
            )

            second_leg = two_wheeler_astar(
                graph,
                split_node,
                direct_end,
                graph_mgr,
                penalties=penalties
            )

            stitched = _dedupe_nodes(
                first_leg
                + second_leg[1:]
            )

            generated_count += 1

            # 1. Connectivity validation
            if not is_valid_connected_route(graph, stitched):
                rejected_candidates.append({
                    "nodes": stitched,
                    "reason": "disconnected_or_invalid"
                })
                continue

            # 2. Duplicate suppression
            if tuple(stitched) in seen_paths:
                rejected_candidates.append({
                    "nodes": stitched,
                    "reason": "exact_duplicate"
                })
                continue

            seen_paths.add(tuple(stitched))

            # 3. Detour tolerance
            cand_dist = calc_route_distance(graph, stitched)
            detour_ratio = cand_dist / fallback_cap_length if fallback_cap_length > 0 else 1.0

            if detour_ratio > max_detour:
                rejected_candidates.append({
                    "nodes": stitched,
                    "reason": "detour_exceeded",
                    "detour_ratio": detour_ratio,
                    "distance": cand_dist
                })
                continue

            # 4. Edge overlap filtering (<= 70%)
            if primary_nodes:
                overlap = calc_route_overlap(graph, primary_nodes, stitched, undirected=undirected)
                jaccard = calc_jaccard_similarity(graph, primary_nodes, stitched, undirected=undirected)
            else:
                overlap = 0.0
                jaccard = 0.0

            if overlap > max_overlap:
                rejected_candidates.append({
                    "nodes": stitched,
                    "reason": "overlap_exceeded",
                    "overlap_ratio": overlap,
                    "distance": cand_dist
                })
                continue

            cand_cost = path_cost(
                graph,
                stitched,
                graph_mgr,
                penalties=penalties
            )

            diverse_alternatives.append({
                "strategy": "line_split",
                "nodes": stitched,
                "cost": cand_cost,
                "distance": cand_dist,
                "detour_ratio": detour_ratio,
                "overlap_ratio": overlap,
                "jaccard_similarity": jaccard,
            })

        except Exception as exc:
            rejected_candidates.append({
                "nodes": [],
                "reason": f"search_failed: {exc}"
            })
            continue

    # --------------------------------------------------------
    # Lowest total cost first for alternatives
    # --------------------------------------------------------

    diverse_alternatives.sort(
        key=lambda item: item["cost"]
    )

    if max_alternatives is not None:
        diverse_alternatives = diverse_alternatives[:max_alternatives]

    final_candidates = [candidates[0]] + diverse_alternatives

    if return_diagnostics:
        return {
            "candidates": final_candidates,
            "direct_route": candidates[0],
            "diverse_alternatives": diverse_alternatives,
            "generated_count": generated_count,
            "rejected_candidates": rejected_candidates,
            "surviving_count": len(diverse_alternatives),
        }

    return final_candidates


# ============================================================
# YEN'S K-SHORTEST PATHS BASELINE (PHASE 10)
# ============================================================

def yen_ksp_two_wheeler(
    graph,
    start_node,
    end_node,
    graph_mgr,
    penalties=None,
    K=4,
    max_detour=DETOUR_TOLERANCE,
    max_overlap=0.70,
    apply_overlap_filter=False,
    undirected=False,
    return_diagnostics=False
):
    """
    Yen's K-Shortest Paths baseline with turn-aware state-expanded routing.

    Both Yen's KSP and Perpendicular Offset use:
    - Identical graph representation and edge-cost function.
    - Identical turn penalties (_turn_penalty).
    - Identical route-cost calculation (path_cost).
    - Identical detour tolerance (max_detour = 1.20).
    """
    start_time = time.perf_counter()

    primary = two_wheeler_astar(
        graph,
        start_node,
        end_node,
        graph_mgr,
        penalties=penalties
    )
    primary_cost = path_cost(graph, primary, graph_mgr, penalties=penalties)
    primary_dist = calc_route_distance(graph, primary)

    A = [{
        "strategy": "yen_ksp_0",
        "nodes": primary,
        "cost": primary_cost,
        "distance": primary_dist,
        "detour_ratio": 1.0,
        "overlap_ratio": 1.0,
        "jaccard_similarity": 1.0,
    }]

    B = []
    seen_in_B = {tuple(primary)}
    max_dist = primary_dist * max_detour

    generated_count = 0
    rejected_detour = 0
    rejected_overlap = 0
    rejected_duplicates = 0

    for k in range(1, K):
        prev_path = A[k - 1]["nodes"]

        for i in range(len(prev_path) - 1):
            spur_node = prev_path[i]
            root_path = prev_path[:i + 1]
            initial_prev = root_path[-2] if len(root_path) >= 2 else None

            banned_edges = set()
            for path_entry in A:
                p_nodes = path_entry["nodes"]
                if len(p_nodes) > i + 1 and p_nodes[:i + 1] == root_path:
                    banned_edges.add((p_nodes[i], p_nodes[i + 1]))

            banned_nodes = set(root_path[:-1])

            try:
                spur_path = two_wheeler_astar(
                    graph,
                    spur_node,
                    end_node,
                    graph_mgr,
                    penalties=penalties,
                    initial_previous_node=initial_prev,
                    banned_nodes=banned_nodes,
                    banned_edges=banned_edges,
                )

                cand_nodes = _dedupe_nodes(root_path[:-1] + spur_path)
                tup = tuple(cand_nodes)
                generated_count += 1

                if tup in seen_in_B:
                    rejected_duplicates += 1
                    continue
                seen_in_B.add(tup)

                cand_dist = calc_route_distance(graph, cand_nodes)
                detour_ratio = cand_dist / primary_dist if primary_dist > 0 else 1.0

                if detour_ratio > max_detour:
                    rejected_detour += 1
                    continue

                overlap = calc_route_overlap(graph, primary, cand_nodes, undirected=undirected)
                if apply_overlap_filter and overlap > max_overlap:
                    rejected_overlap += 1
                    continue

                cand_cost = path_cost(graph, cand_nodes, graph_mgr, penalties=penalties)
                jaccard = calc_jaccard_similarity(graph, primary, cand_nodes, undirected=undirected)

                heapq.heappush(B, (cand_cost, cand_dist, cand_nodes, overlap, jaccard, detour_ratio))

            except nx.NetworkXNoPath:
                continue

        if not B:
            break

        next_cost, next_dist, next_nodes, next_overlap, next_jaccard, next_detour = heapq.heappop(B)
        A.append({
            "strategy": f"yen_ksp_{k}",
            "nodes": next_nodes,
            "cost": next_cost,
            "distance": next_dist,
            "detour_ratio": next_detour,
            "overlap_ratio": next_overlap,
            "jaccard_similarity": next_jaccard,
        })

    runtime_ms = (time.perf_counter() - start_time) * 1000.0

    if return_diagnostics:
        return {
            "paths": A,
            "candidates_generated": generated_count,
            "rejected_duplicates": rejected_duplicates,
            "rejected_detour": rejected_detour,
            "rejected_overlap": rejected_overlap,
            "runtime_ms": runtime_ms,
        }

    return A


# ============================================================
# MANEUVER GENERATION
# ============================================================

def generate_route_maneuvers(graph, route):
    """
    Convert a sequence of routed OSM node IDs into a list of TurnManeuver objects:
    - depart, turn_left, slight_left, straight, slight_right, turn_right, u_turn, arrive
    Each maneuver object contains:
    - type: str
    - instruction: str
    - road_name: str
    - distance_m: float
    - lat: float
    - lng: float
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
        steps.append({
            "u": u,
            "v": v,
            "length": get_edge_length(ed),
            "road_name": get_road_name(ed),
        })

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
            prev_node = route[i - 1]
            curr_node = route[i]
            next_node = route[i + 1]

            angle = _turn_angle(graph, prev_node, curr_node, next_node)

            prev_data = graph.nodes[prev_node]
            curr_data = graph.nodes[curr_node]
            next_data = graph.nodes[next_node]

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

    dest_node = route[-1]
    dest_data = graph.nodes[dest_node]
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
