import math
import osmnx as ox
import networkx as nx
from core.config import (
    TWO_WHEELER_ROAD_PENALTIES, MAIN_ROAD_TYPES, INNER_ROAD_BIASED_TYPES,
    FILTER_DISCOUNT_PER_JUNCTION, FILTER_DISCOUNT_FLOOR, MIN_LANES_FOR_FILTERING,
    DEFAULT_ROUTE_SPLIT_FRACTIONS, DETOUR_TOLERANCE
)

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

def build_two_wheeler_penalties(main_road_penalty=1.0, inner_road_multiplier=1.0, service_multiplier=1.0, roundabout_multiplier=0.95):
    penalties = dict(TWO_WHEELER_ROAD_PENALTIES)
    for road_type in MAIN_ROAD_TYPES: penalties[road_type] = penalties.get(road_type, 1.25) * main_road_penalty
    for road_type in INNER_ROAD_BIASED_TYPES: penalties[road_type] = penalties.get(road_type, 1.0) * inner_road_multiplier
    penalties['service'] = penalties.get('service', 1.0) * service_multiplier
    penalties['_roundabout_multiplier'] = roundabout_multiplier
    return penalties

def two_wheeler_edge_cost(edge_data, graph_mgr, penalties=None, u=None, v=None, congested_nodes=None):
    length = float(edge_data.get('length', 1.0))
    hw = edge_data.get('highway', 'unclassified')
    if isinstance(hw, list): hw = hw[0]
    
    penalty_map = penalties or TWO_WHEELER_ROAD_PENALTIES
    penalty = penalty_map.get(hw, 1.0) # Lowered base main road penalty to let traffic data take control

    # Flyover Exception
    is_bridge = edge_data.get('bridge')
    if isinstance(is_bridge, list): is_bridge = is_bridge[0]
    if is_bridge and is_bridge not in ['no', 'false', '0']:
        if hw in MAIN_ROAD_TYPES:
            penalty = 0.8  # Slight reward for taking elevated bypasses

    # Dynamic Congestion Penalty
    if congested_nodes and (u in congested_nodes or v in congested_nodes):
        penalty *= 25.0  

    if edge_data.get('junction') == 'roundabout':
        penalty *= penalty_map.get('_roundabout_multiplier', 0.95)

    if u is not None and v is not None and graph_mgr is not None:
        penalty *= graph_mgr.get_surface_penalty(u, v)

    return length * penalty

def astar_on_graph(graph, start_node, end_node):
    def heuristic(a, b): return haversine_m(graph.nodes[a]['y'], graph.nodes[a]['x'], graph.nodes[b]['y'], graph.nodes[b]['x'])
    def cost(u, v, edge_data):
        if 'length' in edge_data: return float(edge_data['length'])
        return min(float(d.get('length', 1.0)) for d in edge_data.values())
    return nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=cost)

def two_wheeler_astar(graph, start_node, end_node, graph_mgr, penalties=None, congested_nodes=None):
    def heuristic(a, b): return haversine_m(graph.nodes[a]['y'], graph.nodes[a]['x'], graph.nodes[b]['y'], graph.nodes[b]['x'])
    def cost(u, v, edge_data):
        if 'length' in edge_data: return two_wheeler_edge_cost(edge_data, graph_mgr, penalties, u, v, congested_nodes)
        return min(two_wheeler_edge_cost(d, graph_mgr, penalties, u, v, congested_nodes) for d in edge_data.values())
    return nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=cost)

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

def _derive_split_fractions(straight_line_km, segment_km):
    if straight_line_km <= segment_km: return ()
    segment_km = max(segment_km, 0.5)
    segment_count = max(2, math.ceil(straight_line_km / segment_km))
    return tuple(i / segment_count for i in range(1, segment_count))

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

            if direct_length and calc_route_distance(graph, stitched) > direct_length * DETOUR_TOLERANCE:
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

def extract_maneuvers_from_route(graph, route_nodes):
    """Extracts turn-by-turn navigation maneuvers from a list of route node IDs."""
    if not route_nodes or len(route_nodes) < 2:
        return []

    def get_edge_data(u, v):
        if v in graph[u]:
            return min(graph[u][v].values(), key=lambda d: float(d.get('length', 1.0)))
        return {}

    def get_road_name(edge_data):
        name = edge_data.get('name')
        if isinstance(name, list): name = name[0] if name else None
        if not name:
            hw = edge_data.get('highway', 'road')
            if isinstance(hw, list): hw = hw[0]
            name = f"Unnamed ({hw.replace('_', ' ').title()})"
        return name

    steps = []
    # 1. Start maneuver
    first_u, first_v = route_nodes[0], route_nodes[1]
    first_edge = get_edge_data(first_u, first_v)
    first_name = get_road_name(first_edge)
    start_lat = graph.nodes[first_u]['y']
    start_lng = graph.nodes[first_u]['x']
    
    steps.append({
        "type": "depart",
        "instruction": f"Head on {first_name}",
        "road_name": first_name,
        "distance_m": float(first_edge.get('length', 0)),
        "lat": start_lat,
        "lng": start_lng
    })

    current_distance = float(first_edge.get('length', 0))

    for i in range(1, len(route_nodes) - 1):
        u = route_nodes[i - 1]
        v = route_nodes[i]
        w = route_nodes[i + 1]

        edge1 = get_edge_data(u, v)
        edge2 = get_edge_data(v, w)

        lat1, lng1 = graph.nodes[u]['y'], graph.nodes[u]['x']
        lat2, lng2 = graph.nodes[v]['y'], graph.nodes[v]['x']
        lat3, lng3 = graph.nodes[w]['y'], graph.nodes[w]['x']

        b1 = _bearing_deg(lat1, lng1, lat2, lng2)
        b2 = _bearing_deg(lat2, lng2, lat3, lng3)
        angle = (b2 - b1 + 180) % 360 - 180

        road1 = get_road_name(edge1)
        road2 = get_road_name(edge2)
        seg_len = float(edge2.get('length', 0))

        # Only emit a maneuver if road name changes or turn angle is significant (> 25 deg)
        is_name_change = (road1 != road2 and not road2.startswith("Unnamed"))
        is_sharp_turn = abs(angle) > 28.0

        if is_name_change or is_sharp_turn:
            if angle < -135 or angle > 135:
                m_type = "u_turn"
                verb = "Make a U-turn"
            elif angle < -45:
                m_type = "turn_left"
                verb = "Turn left"
            elif angle < -20:
                m_type = "slight_left"
                verb = "Bear left"
            elif angle > 45:
                m_type = "turn_right"
                verb = "Turn right"
            elif angle > 20:
                m_type = "slight_right"
                verb = "Bear right"
            else:
                m_type = "straight"
                verb = "Continue straight"

            instruction = f"{verb} onto {road2}"
            steps.append({
                "type": m_type,
                "instruction": instruction,
                "road_name": road2,
                "distance_m": round(seg_len, 1),
                "lat": lat2,
                "lng": lng2
            })
        else:
            if steps:
                steps[-1]["distance_m"] = round(steps[-1]["distance_m"] + seg_len, 1)

    # Destination maneuver
    last_node = route_nodes[-1]
    steps.append({
        "type": "arrive",
        "instruction": "Arrive at destination",
        "road_name": "Destination",
        "distance_m": 0,
        "lat": graph.nodes[last_node]['y'],
        "lng": graph.nodes[last_node]['x']
    })

    return steps