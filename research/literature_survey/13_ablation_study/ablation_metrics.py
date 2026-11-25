"""
Ablation Metrics Module for Phase 13 Ablation Study.

Provides rigorously verified, edge-level metric extractors for:
1. Physical route distance (m, km)
2. Turn analysis (sharp >= 60°, moderate 30°-60°, straight < 30°, total turns, turn penalty cost)
3. Road-class distribution (9 OSM categories and 3 macro-classes: arterial, collector, residential)
4. Bridge / flyover exposure (meters, percentage of route, edge count)
5. Roundabout exposure (meters, percentage of route, edge count)
6. Two-wheeler impedance cost calculation under a specified penalty model
7. Route overlap, Jaccard similarity, and pairwise diversity metrics
"""

from typing import List, Dict, Any, Tuple
import networkx as nx

from routing.algorithms import (
    _turn_angle,
    _turn_penalty,
    TURN_THRESHOLD_SHARP,
    TURN_THRESHOLD_MODERATE,
    haversine_m,
    two_wheeler_edge_cost,
    get_route_edge_lengths,
    calc_shared_edge_length,
    calc_route_overlap,
    calc_jaccard_similarity,
    calc_pairwise_diversity,
    MAIN_ROAD_TYPES,
)

ROAD_CLASS_GROUPS: Dict[str, List[str]] = {
    "motorway": ["motorway", "motorway_link"],
    "trunk": ["trunk", "trunk_link"],
    "primary": ["primary", "primary_link"],
    "secondary": ["secondary", "secondary_link"],
    "tertiary": ["tertiary", "tertiary_link"],
    "residential": ["residential"],
    "living_street": ["living_street"],
    "service": ["service"],
    "unclassified": ["unclassified", "road"],
}


def _get_best_edge_data(G: nx.MultiDiGraph, u: int, v: int) -> Dict[str, Any]:
    """Retrieve the shortest physical edge between directed node pair (u, v)."""
    edge_dict = G.get_edge_data(u, v)
    if not edge_dict:
        return {"length": 1.0, "highway": "unclassified"}
    return min(edge_dict.values(), key=lambda d: float(d.get("length", 1.0)))


def calc_route_distance(G: nx.MultiDiGraph, route: List[int]) -> float:
    """Calculate the exact total physical route distance in meters."""
    if not route or len(route) < 2:
        return 0.0
    total = 0.0
    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        if v in G[u]:
            edge_data = _get_best_edge_data(G, u, v)
            total += float(edge_data.get("length", 1.0))
    return total


def analyze_route_turns(G: nx.MultiDiGraph, route: List[int]) -> Dict[str, Any]:
    """
    Calculate maneuver turn counts and accumulated turn penalty along route.
    Turns are classified into:
    - Sharp: heading change >= 60.0°
    - Moderate: 30.0° <= heading change < 60.0°
    - Straight / gentle: heading change < 30.0°
    - Total turns: Sharp + Moderate
    """
    if not route or len(route) < 3:
        return {
            "total_nodes": len(route) if route else 0,
            "sharp_turns": 0,
            "moderate_turns": 0,
            "straight_or_gentle": 0,
            "total_turns": 0,
            "turn_penalty_cost": 0.0,
        }

    sharp_cnt = 0
    mod_cnt = 0
    straight_cnt = 0
    total_penalty = 0.0

    for i in range(1, len(route) - 1):
        prev_node = route[i - 1]
        curr_node = route[i]
        next_node = route[i + 1]

        angle = _turn_angle(G, prev_node, curr_node, next_node)
        penalty = _turn_penalty(G, prev_node, curr_node, next_node)
        total_penalty += penalty

        if angle >= TURN_THRESHOLD_SHARP:
            sharp_cnt += 1
        elif angle >= TURN_THRESHOLD_MODERATE:
            mod_cnt += 1
        else:
            straight_cnt += 1

    return {
        "total_nodes": len(route),
        "sharp_turns": sharp_cnt,
        "moderate_turns": mod_cnt,
        "straight_or_gentle": straight_cnt,
        "total_turns": sharp_cnt + mod_cnt,
        "turn_penalty_cost": round(total_penalty, 2),
    }


def analyze_route_road_classes(G: nx.MultiDiGraph, route: List[int]) -> Dict[str, Any]:
    """
    Extract the physical length (m) and percentage breakdown across 9 OSM highway
    classes and 3 macro-classes (Arterial, Collector, Residential).
    """
    if not route or len(route) < 2:
        return {
            "total_length_m": 0.0,
            "breakdown_m": {},
            "breakdown_pct": {},
            "macro_m": {"arterial_m": 0.0, "collector_m": 0.0, "residential_m": 0.0, "service_m": 0.0, "other_m": 0.0},
            "macro_pct": {"arterial_pct": 0.0, "collector_pct": 0.0, "residential_pct": 0.0, "service_pct": 0.0, "other_pct": 0.0},
        }

    class_lengths = {cat: 0.0 for cat in ROAD_CLASS_GROUPS}
    class_lengths["other"] = 0.0
    total_length = 0.0

    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        if v not in G[u]:
            continue

        edge_data = _get_best_edge_data(G, u, v)
        length = float(edge_data.get("length", 1.0))
        total_length += length

        hw = edge_data.get("highway", "unclassified")
        if isinstance(hw, list):
            hw = hw[0]

        matched = False
        for cat, tag_list in ROAD_CLASS_GROUPS.items():
            if hw in tag_list:
                class_lengths[cat] += length
                matched = True
                break
        if not matched:
            class_lengths["other"] += length

    denom = total_length if total_length > 0 else 1.0
    breakdown_pct = {k: round((v / denom) * 100.0, 2) for k, v in class_lengths.items()}

    arterial_m = (
        class_lengths["motorway"] + class_lengths["trunk"] + class_lengths["primary"] + class_lengths["secondary"]
    )
    collector_m = class_lengths["tertiary"]
    residential_m = class_lengths["residential"] + class_lengths["living_street"] + class_lengths["unclassified"]
    service_m = class_lengths["service"]
    other_m = class_lengths["other"]

    macro_m = {
        "arterial_m": round(arterial_m, 2),
        "collector_m": round(collector_m, 2),
        "residential_m": round(residential_m, 2),
        "service_m": round(service_m, 2),
        "other_m": round(other_m, 2),
    }

    macro_pct = {
        "arterial_pct": round((arterial_m / denom) * 100.0, 2),
        "collector_pct": round((collector_m / denom) * 100.0, 2),
        "residential_pct": round((residential_m / denom) * 100.0, 2),
        "service_pct": round((service_m / denom) * 100.0, 2),
        "other_pct": round((other_m / denom) * 100.0, 2),
    }

    return {
        "total_length_m": round(total_length, 2),
        "breakdown_m": {k: round(v, 2) for k, v in class_lengths.items()},
        "breakdown_pct": breakdown_pct,
        "macro_m": macro_m,
        "macro_pct": macro_pct,
    }


def analyze_bridge_exposure(G: nx.MultiDiGraph, route: List[int]) -> Dict[str, Any]:
    """
    Calculate the total physical distance and percentage of a route traversing
    elevated flyovers / bridges, partitioned by general bridges and arterial bridges.
    """
    if not route or len(route) < 2:
        return {
            "bridge_length_m": 0.0,
            "bridge_pct": 0.0,
            "bridge_edge_count": 0,
            "arterial_bridge_length_m": 0.0,
            "arterial_bridge_pct": 0.0,
        }

    total_dist = calc_route_distance(G, route)
    denom = total_dist if total_dist > 0 else 1.0

    bridge_length = 0.0
    arterial_bridge_length = 0.0
    bridge_count = 0

    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        if v not in G[u]:
            continue

        edge_data = _get_best_edge_data(G, u, v)
        is_bridge = edge_data.get("bridge")
        if isinstance(is_bridge, list):
            is_bridge = is_bridge[0]

        if is_bridge and str(is_bridge).lower() not in ["no", "false", "0", "none"]:
            length = float(edge_data.get("length", 1.0))
            bridge_length += length
            bridge_count += 1

            hw = edge_data.get("highway", "")
            if isinstance(hw, list):
                hw = hw[0]
            if hw in MAIN_ROAD_TYPES:
                arterial_bridge_length += length

    return {
        "bridge_length_m": round(bridge_length, 2),
        "bridge_pct": round((bridge_length / denom) * 100.0, 2),
        "bridge_edge_count": bridge_count,
        "arterial_bridge_length_m": round(arterial_bridge_length, 2),
        "arterial_bridge_pct": round((arterial_bridge_length / denom) * 100.0, 2),
    }


def analyze_roundabout_exposure(G: nx.MultiDiGraph, route: List[int]) -> Dict[str, Any]:
    """
    Calculate the total physical distance and percentage of a route traversing
    rotational roundabouts, along with the count of roundabout edges.
    """
    if not route or len(route) < 2:
        return {
            "roundabout_length_m": 0.0,
            "roundabout_pct": 0.0,
            "roundabout_edge_count": 0,
        }

    total_dist = calc_route_distance(G, route)
    denom = total_dist if total_dist > 0 else 1.0

    roundabout_length = 0.0
    roundabout_count = 0

    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        if v not in G[u]:
            continue

        edge_data = _get_best_edge_data(G, u, v)
        if edge_data.get("junction") == "roundabout":
            roundabout_length += float(edge_data.get("length", 1.0))
            roundabout_count += 1

    return {
        "roundabout_length_m": round(roundabout_length, 2),
        "roundabout_pct": round((roundabout_length / denom) * 100.0, 2),
        "roundabout_edge_count": roundabout_count,
    }


def calc_post_hoc_path_cost(
    G: nx.MultiDiGraph,
    route: List[int],
    graph_mgr: Any,
    penalties: Dict[str, float] = None,
    congested_nodes: set = None
) -> float:
    """
    Evaluate the two-wheeler impedance cost of an arbitrary route under standard
    scoring rules: sum(length * penalty) + sum(turn_penalties).
    Used to score B0, B1, and B2 symmetrically on identical units.
    """
    if not route or len(route) < 2:
        return 0.0

    total_cost = 0.0
    for i in range(len(route) - 1):
        a = route[i]
        b = route[i + 1]
        if b not in G[a]:
            continue

        edge_data = _get_best_edge_data(G, a, b)
        edge_cost = two_wheeler_edge_cost(
            edge_data,
            graph_mgr,
            penalties=penalties,
            u=a,
            v=b,
            congested_nodes=congested_nodes
        )
        total_cost += edge_cost

        if i > 0:
            prev = route[i - 1]
            total_cost += _turn_penalty(G, prev, a, b)

    return round(total_cost, 2)


def extract_full_route_metrics(
    G: nx.MultiDiGraph,
    route: List[int],
    graph_mgr: Any,
    scoring_penalties: Dict[str, float] = None
) -> Dict[str, Any]:
    """Aggregate all structural metrics for a given route."""
    if not route:
        return {
            "node_count": 0,
            "distance_m": 0.0,
            "distance_km": 0.0,
            "impedance_cost": float("inf"),
            "turns": analyze_route_turns(G, []),
            "road_classes": analyze_route_road_classes(G, []),
            "bridge": analyze_bridge_exposure(G, []),
            "roundabout": analyze_roundabout_exposure(G, []),
        }

    dist_m = calc_route_distance(G, route)
    cost = calc_post_hoc_path_cost(G, route, graph_mgr, penalties=scoring_penalties)
    turns = analyze_route_turns(G, route)
    road_classes = analyze_route_road_classes(G, route)
    bridge = analyze_bridge_exposure(G, route)
    roundabout = analyze_roundabout_exposure(G, route)

    return {
        "node_count": len(route),
        "distance_m": round(dist_m, 2),
        "distance_km": round(dist_m / 1000.0, 3),
        "impedance_cost": cost,
        "turns": turns,
        "road_classes": road_classes,
        "bridge": bridge,
        "roundabout": roundabout,
    }
