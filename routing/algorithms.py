import math
import heapq
import itertools

import osmnx as ox
import networkx as nx

from core.config import (
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
# Heuristic must divide by this floor to stay admissible for A*.
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
    congested_nodes=None
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
    """

    def heuristic(node):

        return (
            haversine_m(
                graph.nodes[node]["y"],
                graph.nodes[node]["x"],
                graph.nodes[end_node]["y"],
                graph.nodes[end_node]["x"]
            )
            / MIN_PENALTY_FLOOR
        )

    # State:
    # (previous_node, current_node)

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

        _, _, state = heapq.heappop(
            open_set
        )

        previous_node, current_node = state

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

            return _dedupe_nodes(route)

        # ----------------------------------------------------
        # Explore neighbours
        # ----------------------------------------------------

        for next_node in graph.successors(
            current_node
        ):

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
    penalties=None
):

    direct_start = ox.nearest_nodes(
        graph,
        from_lng,
        from_lat
    )

    direct_end = ox.nearest_nodes(
        graph,
        to_lng,
        to_lat
    )

    candidates = []

    # --------------------------------------------------------
    # Direct route
    # --------------------------------------------------------

    try:

        direct_route = two_wheeler_astar(
            graph,
            direct_start,
            direct_end,
            graph_mgr,
            penalties=penalties
        )

        candidates.append({
            "strategy": "direct",
            "nodes": direct_route,
            "cost": path_cost(
                graph,
                direct_route,
                graph_mgr,
                penalties=penalties
            )
        })

    except Exception as exc:

        candidates.append({
            "strategy": "direct",
            "nodes": [],
            "cost": float("inf"),
            "error": str(exc)
        })

    direct_length = (
        calc_route_distance(
            graph,
            candidates[0]["nodes"]
        )
        if candidates[0]["nodes"]
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
            tuple(candidates[0]["nodes"])
        }
        if candidates[0]["nodes"]
        else set()
    )

    # --------------------------------------------------------
    # Build split candidates
    # --------------------------------------------------------

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

            if tuple(stitched) in seen_paths:
                continue

            seen_paths.add(
                tuple(stitched)
            )

            # ------------------------------------------------
            # Detour tolerance
            # ------------------------------------------------

            if (
                calc_route_distance(
                    graph,
                    stitched
                )
                > fallback_cap_length
                * DETOUR_TOLERANCE
            ):
                continue

            candidates.append({
                "strategy": "line_split",
                "nodes": stitched,
                "cost": path_cost(
                    graph,
                    stitched,
                    graph_mgr,
                    penalties=penalties
                )
            })

        except Exception:
            continue

    # --------------------------------------------------------
    # Lowest total cost first
    # --------------------------------------------------------

    candidates.sort(
        key=lambda item: item["cost"]
    )

    return candidates


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
