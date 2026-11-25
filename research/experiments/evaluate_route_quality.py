"""
Phase 11: Route Quality Evaluation Script
Evaluates route quality metrics across 25 Bengaluru corridors:
- Physical route distance (m, km)
- Two-wheeler impedance cost
- Detour ratio (distance and cost)
- Road-class composition (% and meters by highway type and macro-categories)
- Turn maneuvers (sharp, moderate, straight) and accumulated turn penalty
- Shared-edge overlap and Jaccard similarity
- Route coordinates for visualization and deep-dive case studies

Outputs:
- research/literature_survey/11_route_quality_evaluation/route_quality_evaluation.json
- research/literature_survey/11_route_quality_evaluation/route_quality_evaluation.csv
"""

import sys
import os
import json
import csv
import time
import osmnx as ox

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from routing.graph_manager import graph_manager
from routing.algorithms import (
    two_wheeler_astar,
    build_two_wheeler_penalties,
    calc_route_distance,
    path_cost,
    calc_route_overlap,
    calc_jaccard_similarity,
    calc_pairwise_diversity,
    build_split_route_candidates,
    yen_ksp_two_wheeler,
    _turn_angle,
    _turn_penalty,
    TURN_THRESHOLD_SHARP,
    TURN_THRESHOLD_MODERATE,
    TURN_PENALTY_SHARP,
    TURN_PENALTY_MODERATE,
)
from core.config import DETOUR_TOLERANCE

OD_PAIRS = [
    {"id": "OD_01", "name": "BNMIT to MG Road", "from_lat": 12.9237, "from_lng": 77.5714, "to_lat": 12.9756, "to_lng": 77.6066},
    {"id": "OD_02", "name": "Koramangala to Indiranagar", "from_lat": 12.9352, "from_lng": 77.6245, "to_lat": 12.9719, "to_lng": 77.6412},
    {"id": "OD_03", "name": "Electronic City to Silk Board", "from_lat": 12.8452, "from_lng": 77.6602, "to_lat": 12.9176, "to_lng": 77.6238},
    {"id": "OD_04", "name": "Whitefield to Marathahalli", "from_lat": 12.9698, "from_lng": 77.7500, "to_lat": 12.9569, "to_lng": 77.7011},
    {"id": "OD_05", "name": "Hebbal to Majestic", "from_lat": 13.0358, "from_lng": 77.5970, "to_lat": 12.9767, "to_lng": 77.5713},
    {"id": "OD_06", "name": "Jayanagar 4th Block to Malleshwaram", "from_lat": 12.9250, "from_lng": 77.5838, "to_lat": 13.0031, "to_lng": 77.5643},
    {"id": "OD_07", "name": "HSR Layout to Bellandur", "from_lat": 12.9121, "from_lng": 77.6446, "to_lat": 12.9304, "to_lng": 77.6784},
    {"id": "OD_08", "name": "Banashankari to Yeshwanthpur", "from_lat": 12.9255, "from_lng": 77.5468, "to_lat": 13.0285, "to_lng": 77.5409},
    {"id": "OD_09", "name": "Rajajinagar to Commercial Street", "from_lat": 12.9915, "from_lng": 77.5523, "to_lat": 12.9822, "to_lng": 77.6083},
    {"id": "OD_10", "name": "BTM Layout to Domlur", "from_lat": 12.9166, "from_lng": 77.6101, "to_lat": 12.9609, "to_lng": 77.6387},
    {"id": "OD_11", "name": "Basavanagudi to Ulsoor", "from_lat": 12.9416, "from_lng": 77.5738, "to_lat": 12.9818, "to_lng": 77.6284},
    {"id": "OD_12", "name": "Frazer Town to Shivajinagar", "from_lat": 12.9982, "from_lng": 77.6145, "to_lat": 12.9856, "to_lng": 77.6006},
    {"id": "OD_13", "name": "JP Nagar 6th Phase to Koramangala", "from_lat": 12.9063, "from_lng": 77.5855, "to_lat": 12.9352, "to_lng": 77.6245},
    {"id": "OD_14", "name": "Vijayanagar to Majestic", "from_lat": 12.9719, "from_lng": 77.5306, "to_lat": 12.9767, "to_lng": 77.5713},
    {"id": "OD_15", "name": "Yelahanka to Hebbal", "from_lat": 13.1007, "from_lng": 77.5963, "to_lat": 13.0358, "to_lng": 77.5970},
    {"id": "OD_16", "name": "Bellandur to Whitefield", "from_lat": 12.9304, "from_lng": 77.6784, "to_lat": 12.9698, "to_lng": 77.7500},
    {"id": "OD_17", "name": "Malleshwaram to Rajajinagar", "from_lat": 13.0031, "from_lng": 77.5643, "to_lat": 12.9915, "to_lng": 77.5523},
    {"id": "OD_18", "name": "Indiranagar to MG Road", "from_lat": 12.9719, "from_lng": 77.6412, "to_lat": 12.9756, "to_lng": 77.6066},
    {"id": "OD_19", "name": "Silk Board to BTM 2nd Stage", "from_lat": 12.9176, "from_lng": 77.6238, "to_lat": 12.9166, "to_lng": 77.6101},
    {"id": "OD_20", "name": "Kengeri to Satellite Bus Station", "from_lat": 12.9081, "from_lng": 77.4852, "to_lat": 12.9536, "to_lng": 77.5432},
    {"id": "OD_21", "name": "RT Nagar to Cantonment", "from_lat": 13.0238, "from_lng": 77.5936, "to_lat": 12.9935, "to_lng": 77.6001},
    {"id": "OD_22", "name": "Marathahalli to HAL Airport Road", "from_lat": 12.9569, "from_lng": 77.7011, "to_lat": 12.9609, "to_lng": 77.6582},
    {"id": "OD_23", "name": "Richmond Town to Brigade Road", "from_lat": 12.9667, "from_lng": 77.6015, "to_lat": 12.9733, "to_lng": 77.6074},
    {"id": "OD_24", "name": "Banaswadi to Kammanahalli", "from_lat": 13.0142, "from_lng": 77.6519, "to_lat": 13.0094, "to_lng": 77.6367},
    {"id": "OD_25", "name": "Padmanabhanagar to Gandhi Bazaar", "from_lat": 12.9180, "from_lng": 77.5576, "to_lat": 12.9463, "to_lng": 77.5694},
]

# 5 In-depth case study corridors
CASE_STUDY_CORRIDORS = {"OD_01", "OD_04", "OD_06", "OD_12", "OD_15"}

ROAD_CLASS_GROUPS = {
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


def analyze_route_road_classes(G, route):
    """Calculate distance (meters) and percentage for each road class in route."""
    if not route or len(route) < 2:
        return {"total_length_m": 0.0, "breakdown_m": {}, "breakdown_pct": {}, "macro_pct": {}}

    class_lengths = {cat: 0.0 for cat in ROAD_CLASS_GROUPS}
    class_lengths["other"] = 0.0
    total_length = 0.0

    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        if v not in G[u]:
            continue

        edge_data = min(G[u][v].values(), key=lambda d: float(d.get("length", 1.0)))
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

    if total_length <= 0:
        total_length = 1.0

    breakdown_pct = {k: round((v / total_length) * 100.0, 2) for k, v in class_lengths.items()}

    # Macro categories
    arterial_m = (
        class_lengths["motorway"] + class_lengths["trunk"] + class_lengths["primary"] + class_lengths["secondary"]
    )
    collector_m = class_lengths["tertiary"]
    residential_m = class_lengths["residential"] + class_lengths["living_street"] + class_lengths["unclassified"]
    service_m = class_lengths["service"]
    other_m = class_lengths["other"]

    macro_pct = {
        "arterial_pct": round((arterial_m / total_length) * 100.0, 2),
        "collector_pct": round((collector_m / total_length) * 100.0, 2),
        "residential_pct": round((residential_m / total_length) * 100.0, 2),
        "service_pct": round((service_m / total_length) * 100.0, 2),
        "other_pct": round((other_m / total_length) * 100.0, 2),
    }

    return {
        "total_length_m": round(total_length, 2),
        "breakdown_m": {k: round(v, 2) for k, v in class_lengths.items()},
        "breakdown_pct": breakdown_pct,
        "macro_pct": macro_pct,
    }


def analyze_route_turns(G, route):
    """Calculate maneuver turn counts and accumulated turn penalty along route."""
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


def extract_route_full_coordinates(G, route):
    """
    Extract complete polyline coordinates including intermediate LineString shape points
    along edges. Preserves exact node order and adds edge curve geometry for visualization.
    """
    if not route:
        return []
    if len(route) == 1:
        return [[round(G.nodes[route[0]]["y"], 6), round(G.nodes[route[0]]["x"], 6)]]

    full_coords = []
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        edge_dict = G.get_edge_data(u, v)
        if edge_dict:
            best_edge = min(edge_dict.values(), key=lambda d: float(d.get("length", 1.0)))
            if "geometry" in best_edge and hasattr(best_edge["geometry"], "coords"):
                pts = list(best_edge["geometry"].coords)
                if full_coords:
                    pts = pts[1:]  # Avoid duplicating the shared vertex
                for p in pts:
                    full_coords.append([round(p[1], 6), round(p[0], 6)])
                continue

        # Fallback to endpoint nodes if no LineString geometry is present
        if not full_coords:
            full_coords.append([round(G.nodes[u]["y"], 6), round(G.nodes[u]["x"], 6)])
        full_coords.append([round(G.nodes[v]["y"], 6), round(G.nodes[v]["x"], 6)])

    return full_coords


def run_route_quality_evaluation():
    print("=" * 80)
    print("PHASE 11: ROUTE QUALITY EVALUATION EXPERIMENT (25 BENGALURU CORRIDORS)")
    print("=" * 80)

    print("Loading Bengaluru road graph...")
    t0 = time.time()
    graph_manager.load_graph()
    G = graph_manager.G
    print(f"Graph loaded in {time.time() - t0:.2f}s ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")

    penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)

    out_dir = os.path.join(PROJECT_ROOT, "research", "literature_survey", "11_route_quality_evaluation")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "route_quality_evaluation.json")
    out_csv = os.path.join(out_dir, "route_quality_evaluation.csv")

    all_corridor_evaluations = []
    csv_rows = []

    for idx, pair in enumerate(OD_PAIRS, 1):
        od_id = pair["id"]
        od_name = pair["name"]
        print(f"\n[{idx}/25] Evaluating {od_id}: {od_name}...")

        s_node = int(ox.nearest_nodes(G, pair["from_lng"], pair["from_lat"]))
        e_node = int(ox.nearest_nodes(G, pair["to_lng"], pair["to_lat"]))

        corridor_data = {
            "id": od_id,
            "name": od_name,
            "start_node": s_node,
            "end_node": e_node,
            "from_coords": [pair["from_lat"], pair["from_lng"]],
            "to_coords": [pair["to_lat"], pair["to_lng"]],
            "is_deep_dive_case_study": bool(od_id in CASE_STUDY_CORRIDORS),
            "primary_route": {},
            "perpendicular_offset_alternatives": [],
            "yen_ksp_alternatives": [],
        }

        # ----------------------------------------------------
        # 1. Primary Route Generation (Standard Admissible A*)
        # ----------------------------------------------------
        t_start_prim = time.perf_counter()
        primary_metrics = two_wheeler_astar(
            G,
            s_node,
            e_node,
            graph_manager,
            penalties=penalties,
            heuristic_mode="admissible",
            return_metrics=True,
        )
        t_prim_ms = (time.perf_counter() - t_start_prim) * 1000.0

        primary_route = primary_metrics["route"]
        prim_dist_m = calc_route_distance(G, primary_route)
        prim_cost = primary_metrics["cost"]
        prim_road_classes = analyze_route_road_classes(G, primary_route)
        prim_turns = analyze_route_turns(G, primary_route)
        prim_coords = extract_route_full_coordinates(G, primary_route)

        corridor_data["primary_route"] = {
            "strategy": "primary_admissible_astar",
            "node_count": len(primary_route),
            "distance_km": round(prim_dist_m / 1000.0, 3),
            "distance_m": round(prim_dist_m, 2),
            "impedance_cost": round(prim_cost, 2),
            "runtime_ms": round(t_prim_ms, 2),
            "road_classes": prim_road_classes,
            "turns": prim_turns,
            "coordinates": prim_coords,
        }

        # CSV row for Primary
        csv_rows.append({
            "corridor_id": od_id,
            "corridor_name": od_name,
            "method": "Primary_Admissible_AStar",
            "route_role": "Primary",
            "strategy": "primary_admissible_astar",
            "distance_km": round(prim_dist_m / 1000.0, 3),
            "impedance_cost": round(prim_cost, 2),
            "detour_ratio_dist": 1.0,
            "detour_ratio_cost": 1.0,
            "overlap_pct": 100.0,
            "jaccard_similarity": 1.0,
            "total_turns": prim_turns["total_turns"],
            "sharp_turns": prim_turns["sharp_turns"],
            "moderate_turns": prim_turns["moderate_turns"],
            "turn_penalty_cost": prim_turns["turn_penalty_cost"],
            "arterial_pct": prim_road_classes["macro_pct"]["arterial_pct"],
            "collector_pct": prim_road_classes["macro_pct"]["collector_pct"],
            "residential_pct": prim_road_classes["macro_pct"]["residential_pct"],
            "service_pct": prim_road_classes["macro_pct"]["service_pct"],
            "motorway_pct": prim_road_classes["breakdown_pct"].get("motorway", 0.0),
            "trunk_pct": prim_road_classes["breakdown_pct"].get("trunk", 0.0),
            "primary_pct": prim_road_classes["breakdown_pct"].get("primary", 0.0),
            "secondary_pct": prim_road_classes["breakdown_pct"].get("secondary", 0.0),
            "tertiary_pct": prim_road_classes["breakdown_pct"].get("tertiary", 0.0),
            "residential_exact_pct": prim_road_classes["breakdown_pct"].get("residential", 0.0),
            "runtime_ms": round(t_prim_ms, 2),
        })

        print(
            f"  Primary: {prim_dist_m/1000.0:.2f}km | Cost: {prim_cost:.1f} | "
            f"Turns: {prim_turns['total_turns']} (Sharp: {prim_turns['sharp_turns']}) | "
            f"Arterial: {prim_road_classes['macro_pct']['arterial_pct']}% | "
            f"Residential: {prim_road_classes['macro_pct']['residential_pct']}%"
        )

        # ----------------------------------------------------
        # 2. Perpendicular-Offset Alternative Route Generation
        # ----------------------------------------------------
        t_start_offset = time.perf_counter()
        offset_diag = build_split_route_candidates(
            G,
            graph_manager,
            pair["from_lat"],
            pair["from_lng"],
            pair["to_lat"],
            pair["to_lng"],
            penalties=penalties,
            max_overlap=0.70,
            max_detour=1.20,
            max_alternatives=3,
            return_diagnostics=True,
        )
        t_offset_ms = (time.perf_counter() - t_start_offset) * 1000.0

        offset_candidates = offset_diag["candidates"]

        for alt_idx, cand in enumerate(offset_candidates[1:], 1):  # Skip index 0 (direct)
            cand_route = cand["nodes"]
            cand_dist_m = calc_route_distance(G, cand_route)
            cand_cost = cand["cost"]
            cand_road_classes = analyze_route_road_classes(G, cand_route)
            cand_turns = analyze_route_turns(G, cand_route)
            cand_overlap = calc_route_overlap(G, primary_route, cand_route)
            cand_jaccard = calc_jaccard_similarity(G, primary_route, cand_route)
            cand_coords = extract_route_full_coordinates(G, cand_route)

            alt_record = {
                "route_index": alt_idx,
                "strategy": cand["strategy"],
                "node_count": len(cand_route),
                "distance_km": round(cand_dist_m / 1000.0, 3),
                "distance_m": round(cand_dist_m, 2),
                "impedance_cost": round(cand_cost, 2),
                "detour_ratio_dist": round(cand_dist_m / prim_dist_m, 4),
                "detour_ratio_cost": round(cand_cost / prim_cost, 4),
                "overlap_ratio_pct": round(cand_overlap * 100.0, 2),
                "jaccard_similarity": round(cand_jaccard, 4),
                "road_classes": cand_road_classes,
                "turns": cand_turns,
                "coordinates": cand_coords,
            }
            corridor_data["perpendicular_offset_alternatives"].append(alt_record)

            csv_rows.append({
                "corridor_id": od_id,
                "corridor_name": od_name,
                "method": "Perpendicular_Offset",
                "route_role": f"Alt_{alt_idx}",
                "strategy": cand["strategy"],
                "distance_km": round(cand_dist_m / 1000.0, 3),
                "impedance_cost": round(cand_cost, 2),
                "detour_ratio_dist": round(cand_dist_m / prim_dist_m, 4),
                "detour_ratio_cost": round(cand_cost / prim_cost, 4),
                "overlap_pct": round(cand_overlap * 100.0, 2),
                "jaccard_similarity": round(cand_jaccard, 4),
                "total_turns": cand_turns["total_turns"],
                "sharp_turns": cand_turns["sharp_turns"],
                "moderate_turns": cand_turns["moderate_turns"],
                "turn_penalty_cost": cand_turns["turn_penalty_cost"],
                "arterial_pct": cand_road_classes["macro_pct"]["arterial_pct"],
                "collector_pct": cand_road_classes["macro_pct"]["collector_pct"],
                "residential_pct": cand_road_classes["macro_pct"]["residential_pct"],
                "service_pct": cand_road_classes["macro_pct"]["service_pct"],
                "motorway_pct": cand_road_classes["breakdown_pct"].get("motorway", 0.0),
                "trunk_pct": cand_road_classes["breakdown_pct"].get("trunk", 0.0),
                "primary_pct": cand_road_classes["breakdown_pct"].get("primary", 0.0),
                "secondary_pct": cand_road_classes["breakdown_pct"].get("secondary", 0.0),
                "tertiary_pct": cand_road_classes["breakdown_pct"].get("tertiary", 0.0),
                "residential_exact_pct": cand_road_classes["breakdown_pct"].get("residential", 0.0),
                "runtime_ms": round(t_offset_ms, 2),
            })

            print(
                f"    Offset Alt {alt_idx}: {cand_dist_m/1000.0:.2f}km | Overlap: {cand_overlap*100.0:.1f}% | "
                f"Detour: {cand_dist_m/prim_dist_m:.3f}x | Turns: {cand_turns['total_turns']} | "
                f"Arterial: {cand_road_classes['macro_pct']['arterial_pct']}% | "
                f"Residential: {cand_road_classes['macro_pct']['residential_pct']}%"
            )

        if not corridor_data["perpendicular_offset_alternatives"]:
            print(f"    Offset: 0 surviving alternatives (all candidates rejected by detour cap or overlap filter)")

        # ----------------------------------------------------
        # 3. Yen's KSP Baseline (For 5 In-Depth Case Study Corridors)
        # ----------------------------------------------------
        if od_id in CASE_STUDY_CORRIDORS:
            print(f"  [Deep-Dive] Executing Yen's KSP (K=4) for {od_id}...")
            t_start_yen = time.perf_counter()
            yen_diag = yen_ksp_two_wheeler(
                G,
                s_node,
                e_node,
                graph_manager,
                penalties=penalties,
                K=4,
                max_detour=1.20,
                apply_overlap_filter=False,
                return_diagnostics=True,
            )
            t_yen_ms = (time.perf_counter() - t_start_yen) * 1000.0

            yen_paths = yen_diag["paths"]
            for y_idx, p in enumerate(yen_paths[1:], 1):  # Skip index 0 (primary)
                p_route = p["nodes"]
                p_dist_m = calc_route_distance(G, p_route)
                p_cost = p["cost"]
                p_road_classes = analyze_route_road_classes(G, p_route)
                p_turns = analyze_route_turns(G, p_route)
                p_overlap = calc_route_overlap(G, primary_route, p_route)
                p_jaccard = calc_jaccard_similarity(G, primary_route, p_route)
                p_coords = extract_route_full_coordinates(G, p_route)

                yen_record = {
                    "route_index": y_idx,
                    "strategy": p["strategy"],
                    "node_count": len(p_route),
                    "distance_km": round(p_dist_m / 1000.0, 3),
                    "distance_m": round(p_dist_m, 2),
                    "impedance_cost": round(p_cost, 2),
                    "detour_ratio_dist": round(p_dist_m / prim_dist_m, 4),
                    "detour_ratio_cost": round(p_cost / prim_cost, 4),
                    "overlap_ratio_pct": round(p_overlap * 100.0, 2),
                    "jaccard_similarity": round(p_jaccard, 4),
                    "survives_70pct_filter": bool(p_overlap <= 0.70),
                    "road_classes": p_road_classes,
                    "turns": p_turns,
                    "coordinates": p_coords,
                }
                corridor_data["yen_ksp_alternatives"].append(yen_record)

                csv_rows.append({
                    "corridor_id": od_id,
                    "corridor_name": od_name,
                    "method": "Yens_KSP",
                    "route_role": f"Alt_{y_idx}",
                    "strategy": p["strategy"],
                    "distance_km": round(p_dist_m / 1000.0, 3),
                    "impedance_cost": round(p_cost, 2),
                    "detour_ratio_dist": round(p_dist_m / prim_dist_m, 4),
                    "detour_ratio_cost": round(p_cost / prim_cost, 4),
                    "overlap_pct": round(p_overlap * 100.0, 2),
                    "jaccard_similarity": round(p_jaccard, 4),
                    "total_turns": p_turns["total_turns"],
                    "sharp_turns": p_turns["sharp_turns"],
                    "moderate_turns": p_turns["moderate_turns"],
                    "turn_penalty_cost": p_turns["turn_penalty_cost"],
                    "arterial_pct": p_road_classes["macro_pct"]["arterial_pct"],
                    "collector_pct": p_road_classes["macro_pct"]["collector_pct"],
                    "residential_pct": p_road_classes["macro_pct"]["residential_pct"],
                    "service_pct": p_road_classes["macro_pct"]["service_pct"],
                    "motorway_pct": p_road_classes["breakdown_pct"].get("motorway", 0.0),
                    "trunk_pct": p_road_classes["breakdown_pct"].get("trunk", 0.0),
                    "primary_pct": p_road_classes["breakdown_pct"].get("primary", 0.0),
                    "secondary_pct": p_road_classes["breakdown_pct"].get("secondary", 0.0),
                    "tertiary_pct": p_road_classes["breakdown_pct"].get("tertiary", 0.0),
                    "residential_exact_pct": p_road_classes["breakdown_pct"].get("residential", 0.0),
                    "runtime_ms": round(t_yen_ms, 2),
                })

                print(
                    f"    Yen Alt {y_idx}: {p_dist_m/1000.0:.2f}km | Overlap: {p_overlap*100.0:.1f}% | "
                    f"Survives <=70%: {p_overlap <= 0.70} | Turns: {p_turns['total_turns']}"
                )

        all_corridor_evaluations.append(corridor_data)

    # Save JSON results
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_corridor_evaluations, f, indent=2)
    print(f"\nSaved detailed evaluation JSON to: {out_json}")

    # Save CSV results
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"Saved detailed evaluation CSV to: {out_csv}")

    print("\n" + "=" * 80)
    print("ROUTE QUALITY EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_route_quality_evaluation()
