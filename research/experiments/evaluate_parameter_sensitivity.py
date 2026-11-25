"""
Phase 11: Parameter Sensitivity Analysis Script
Evaluates how varying key engineering heuristic parameters affects:
- Primary route physical distance
- Two-wheeler impedance cost
- Road-class distribution (arterial vs. residential vs. collector)
- Maneuver complexity (turn counts and turn penalties)
- Perpendicular-offset alternative route generation, detour, overlap, and diversity

Tested Parameter Variations:
1. Baseline Heuristic (Production Default)
2. Road Hierarchy Multipliers:
   - S1_Neutral_Roads (Main 1.0, Inner 1.0, Service 1.0)
   - S2_Aggressive_Inner (Main 2.5, Inner 0.75, Service 0.8)
   - S3_Extreme_Highway_Aversion (Motorway 6.0, Trunk 5.0, Primary 3.5, Secondary 2.0, Inner 1.0)
3. Turn Penalties:
   - S4_Zero_Turn_Penalty (Sharp 0.0, Moderate 0.0)
   - S5_High_Turn_Penalty (Sharp 60.0, Moderate 25.0)
4. Flyover & Junction Modifiers:
   - S6_Neutral_Bridge_Roundabout (Bridge 1.0, Roundabout 1.0)
   - S7_Flyover_Avoidance (Bridge 1.5, Roundabout 1.2)

Evaluated across 5 structurally diverse Bengaluru corridors:
- OD_01 (Radial to Core: BNMIT to MG Road)
- OD_04 (Pinch-Point IT Corridor: Whitefield to Marathahalli)
- OD_06 (Major Cross-City Corridor: Jayanagar to Malleshwaram)
- OD_12 (Dense Historic Grid: Frazer Town to Shivajinagar)
- OD_15 (Expressway Highway Spine: Yelahanka to Hebbal)

Outputs:
- research/literature_survey/11_route_quality_evaluation/sensitivity_analysis.json
- research/literature_survey/11_route_quality_evaluation/sensitivity_analysis.csv
"""

import sys
import os
import json
import csv
import time
import osmnx as ox

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import routing.algorithms as alg
from routing.graph_manager import graph_manager
from routing.algorithms import (
    two_wheeler_astar,
    build_two_wheeler_penalties,
    calc_route_distance,
    path_cost,
    calc_pairwise_diversity,
    build_split_route_candidates,
    MAIN_ROAD_TYPES,
    TWO_WHEELER_ROAD_PENALTIES,
)
from research.experiments.evaluate_route_quality import (
    analyze_route_road_classes,
    analyze_route_turns,
)

CORRIDORS = [
    {"id": "OD_01", "name": "BNMIT to MG Road", "from_lat": 12.9237, "from_lng": 77.5714, "to_lat": 12.9756, "to_lng": 77.6066},
    {"id": "OD_04", "name": "Whitefield to Marathahalli", "from_lat": 12.9698, "from_lng": 77.7500, "to_lat": 12.9569, "to_lng": 77.7011},
    {"id": "OD_06", "name": "Jayanagar 4th Block to Malleshwaram", "from_lat": 12.9250, "from_lng": 77.5838, "to_lat": 13.0031, "to_lng": 77.5643},
    {"id": "OD_12", "name": "Frazer Town to Shivajinagar", "from_lat": 12.9982, "from_lng": 77.6145, "to_lat": 12.9856, "to_lng": 77.6006},
    {"id": "OD_15", "name": "Yelahanka to Hebbal", "from_lat": 13.1007, "from_lng": 77.5963, "to_lat": 13.0358, "to_lng": 77.5970},
]

CONFIGURATIONS = [
    {
        "config_id": "C0_Baseline",
        "description": "Production Default Heuristics (Main 1.5, Inner 0.9, Bridge 0.8, Sharp 25, Mod 8)",
        "penalties_kwargs": {"main_road_penalty": 1.5, "inner_road_multiplier": 0.9, "service_multiplier": 0.9, "roundabout_multiplier": 0.95},
        "custom_road_penalties": None,
        "bridge_multiplier": 0.8,
        "turn_sharp": 25.0,
        "turn_moderate": 8.0,
    },
    {
        "config_id": "C1_Neutral_Roads",
        "description": "Pure Distance Neutrality (Main 1.0, Inner 1.0, Service 1.0)",
        "penalties_kwargs": {"main_road_penalty": 1.0, "inner_road_multiplier": 1.0, "service_multiplier": 1.0, "roundabout_multiplier": 1.0},
        "custom_road_penalties": None,
        "bridge_multiplier": 1.0,
        "turn_sharp": 25.0,
        "turn_moderate": 8.0,
    },
    {
        "config_id": "C2_Aggressive_Inner",
        "description": "High Arterial Avoidance (Main 2.5, Inner 0.75, Service 0.8)",
        "penalties_kwargs": {"main_road_penalty": 2.5, "inner_road_multiplier": 0.75, "service_multiplier": 0.8, "roundabout_multiplier": 0.95},
        "custom_road_penalties": None,
        "bridge_multiplier": 0.8,
        "turn_sharp": 25.0,
        "turn_moderate": 8.0,
    },
    {
        "config_id": "C3_Extreme_Highway_Aversion",
        "description": "Severe Highway Penalization (Motorway 6.0, Trunk 5.0, Primary 3.5, Secondary 2.0)",
        "penalties_kwargs": {"main_road_penalty": 1.5, "inner_road_multiplier": 0.9, "service_multiplier": 0.9, "roundabout_multiplier": 0.95},
        "custom_road_penalties": {
            "motorway": 6.0, "motorway_link": 5.0, "trunk": 5.0, "trunk_link": 4.0,
            "primary": 3.5, "primary_link": 3.0, "secondary": 2.0, "secondary_link": 1.8,
            "tertiary": 1.15, "tertiary_link": 1.1, "residential": 1.0, "living_street": 0.95,
            "unclassified": 1.0, "service": 0.9, "road": 1.1,
        },
        "bridge_multiplier": 0.8,
        "turn_sharp": 25.0,
        "turn_moderate": 8.0,
    },
    {
        "config_id": "C4_Zero_Turn_Penalty",
        "description": "Zero Turn Penalties (Sharp 0.0, Moderate 0.0 - Unrestricted Turns)",
        "penalties_kwargs": {"main_road_penalty": 1.5, "inner_road_multiplier": 0.9, "service_multiplier": 0.9, "roundabout_multiplier": 0.95},
        "custom_road_penalties": None,
        "bridge_multiplier": 0.8,
        "turn_sharp": 0.0,
        "turn_moderate": 0.0,
    },
    {
        "config_id": "C5_High_Turn_Penalty",
        "description": "Heavy Turn Suppression (Sharp 60.0, Moderate 25.0 - Strict Corridor Straightness)",
        "penalties_kwargs": {"main_road_penalty": 1.5, "inner_road_multiplier": 0.9, "service_multiplier": 0.9, "roundabout_multiplier": 0.95},
        "custom_road_penalties": None,
        "bridge_multiplier": 0.8,
        "turn_sharp": 60.0,
        "turn_moderate": 25.0,
    },
    {
        "config_id": "C6_Neutral_Bridge_Roundabout",
        "description": "Neutral Grade & Junction Modifiers (Bridge 1.0, Roundabout 1.0 - No Flyover Discount)",
        "penalties_kwargs": {"main_road_penalty": 1.5, "inner_road_multiplier": 0.9, "service_multiplier": 0.9, "roundabout_multiplier": 1.0},
        "custom_road_penalties": None,
        "bridge_multiplier": 1.0,
        "turn_sharp": 25.0,
        "turn_moderate": 8.0,
    },
    {
        "config_id": "C7_Flyover_Avoidance",
        "description": "Flyover Disincentive (Bridge 1.5, Roundabout 1.2 - Two-Wheeler Flyover Avoidance)",
        "penalties_kwargs": {"main_road_penalty": 1.5, "inner_road_multiplier": 0.9, "service_multiplier": 0.9, "roundabout_multiplier": 1.2},
        "custom_road_penalties": None,
        "bridge_multiplier": 1.5,
        "turn_sharp": 25.0,
        "turn_moderate": 8.0,
    },
]


def make_scoped_edge_cost(bridge_mult, roundabout_mult):
    def custom_edge_cost(edge_data, graph_mgr, penalties=None, u=None, v=None, congested_nodes=None):
        length = float(edge_data.get("length", 1.0))
        hw = edge_data.get("highway", "unclassified")
        if isinstance(hw, list):
            hw = hw[0]
        penalty_map = penalties or TWO_WHEELER_ROAD_PENALTIES
        penalty = penalty_map.get(hw, 1.0)

        # Flyover handling
        is_bridge = edge_data.get("bridge")
        if isinstance(is_bridge, list):
            is_bridge = is_bridge[0]
        if is_bridge and is_bridge not in ["no", "false", "0"]:
            if hw in MAIN_ROAD_TYPES:
                penalty = bridge_mult

        if congested_nodes and (u in congested_nodes or v in congested_nodes):
            penalty *= 25.0

        if edge_data.get("junction") == "roundabout":
            penalty *= roundabout_mult

        if u is not None and v is not None and graph_mgr is not None:
            penalty *= graph_mgr.get_surface_penalty(u, v)

        return length * penalty

    return custom_edge_cost


def run_parameter_sensitivity_experiment():
    print("=" * 80)
    print("PHASE 11: PARAMETER SENSITIVITY ANALYSIS EXPERIMENT")
    print("=" * 80)

    print("Loading Bengaluru road graph...")
    t0 = time.time()
    graph_manager.load_graph()
    G = graph_manager.G
    print(f"Graph loaded in {time.time() - t0:.2f}s ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")

    out_dir = os.path.join(PROJECT_ROOT, "research", "literature_survey", "11_route_quality_evaluation")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "sensitivity_analysis.json")
    out_csv = os.path.join(out_dir, "sensitivity_analysis.csv")

    orig_sharp = alg.TURN_PENALTY_SHARP
    orig_moderate = alg.TURN_PENALTY_MODERATE
    orig_edge_cost_fn = alg.two_wheeler_edge_cost

    all_sensitivity_results = []
    csv_rows = []

    for cfg in CONFIGURATIONS:
        cfg_id = cfg["config_id"]
        cfg_desc = cfg["description"]
        print(f"\nEvaluating Configuration: {cfg_id} — {cfg_desc}")

        # Build penalty dictionary
        if cfg["custom_road_penalties"]:
            penalties = dict(cfg["custom_road_penalties"])
            penalties["_roundabout_multiplier"] = cfg["penalties_kwargs"].get("roundabout_multiplier", 0.95)
        else:
            penalties = build_two_wheeler_penalties(**cfg["penalties_kwargs"])

        bridge_mult = cfg["bridge_multiplier"]
        roundabout_mult = cfg["penalties_kwargs"].get("roundabout_multiplier", 0.95)

        # Setup scoped execution environment
        alg.TURN_PENALTY_SHARP = cfg["turn_sharp"]
        alg.TURN_PENALTY_MODERATE = cfg["turn_moderate"]
        alg.two_wheeler_edge_cost = make_scoped_edge_cost(bridge_mult, roundabout_mult)

        cfg_corridor_results = []

        try:
            for pair in CORRIDORS:
                od_id = pair["id"]
                od_name = pair["name"]

                s_node = int(ox.nearest_nodes(G, pair["from_lng"], pair["from_lat"]))
                e_node = int(ox.nearest_nodes(G, pair["to_lng"], pair["to_lat"]))

                # 1. Primary Route under this configuration
                t_start = time.perf_counter()
                prim_res = two_wheeler_astar(
                    G, s_node, e_node, graph_manager,
                    penalties=penalties,
                    heuristic_mode="admissible",
                    return_metrics=True
                )
                t_prim_ms = (time.perf_counter() - t_start) * 1000.0

                prim_route = prim_res["route"]
                prim_dist_m = calc_route_distance(G, prim_route)
                prim_cost = prim_res["cost"]
                prim_road_classes = analyze_route_road_classes(G, prim_route)
                prim_turns = analyze_route_turns(G, prim_route)

                # 2. Alternative Route Generation under this configuration
                t_alt_start = time.perf_counter()
                offset_diag = build_split_route_candidates(
                    G, graph_manager,
                    pair["from_lat"], pair["from_lng"],
                    pair["to_lat"], pair["to_lng"],
                    penalties=penalties,
                    max_overlap=0.70,
                    max_detour=1.20,
                    max_alternatives=3,
                    return_diagnostics=True
                )
                t_alt_ms = (time.perf_counter() - t_alt_start) * 1000.0

                offset_cands = offset_diag["candidates"]
                valid_alts = offset_diag["surviving_count"]
                alt_routes = [c["nodes"] for c in offset_cands if c["nodes"]]
                pairwise_div = calc_pairwise_diversity(G, alt_routes)

                alt_overlaps = []
                alt_detours = []
                for cand in offset_cands[1:]:
                    alt_overlaps.append(cand["overlap_ratio"])
                    alt_detours.append(cand["detour_ratio"])

                mean_overlap_pct = (sum(alt_overlaps) / len(alt_overlaps) * 100.0) if alt_overlaps else 0.0
                mean_detour_ratio = (sum(alt_detours) / len(alt_detours)) if alt_detours else 1.0

                record = {
                    "config_id": cfg_id,
                    "description": cfg_desc,
                    "corridor_id": od_id,
                    "corridor_name": od_name,
                    "distance_km": round(prim_dist_m / 1000.0, 3),
                    "impedance_cost": round(prim_cost, 2),
                    "total_turns": prim_turns["total_turns"],
                    "sharp_turns": prim_turns["sharp_turns"],
                    "moderate_turns": prim_turns["moderate_turns"],
                    "turn_penalty_cost": prim_turns["turn_penalty_cost"],
                    "arterial_pct": prim_road_classes["macro_pct"]["arterial_pct"],
                    "collector_pct": prim_road_classes["macro_pct"]["collector_pct"],
                    "residential_pct": prim_road_classes["macro_pct"]["residential_pct"],
                    "candidates_generated": offset_diag["generated_count"],
                    "surviving_alternatives": valid_alts,
                    "mean_alt_overlap_pct": round(mean_overlap_pct, 2),
                    "mean_alt_detour_ratio": round(mean_detour_ratio, 4),
                    "pairwise_diversity": round(pairwise_div, 4),
                    "primary_runtime_ms": round(t_prim_ms, 2),
                    "offset_runtime_ms": round(t_alt_ms, 2),
                }

                cfg_corridor_results.append(record)
                csv_rows.append(record)

                print(
                    f"  {od_id} ({od_name[:20]}): Dist={prim_dist_m/1000.0:.2f}km, Cost={prim_cost:.1f}, "
                    f"Turns={prim_turns['total_turns']}, Arterial={prim_road_classes['macro_pct']['arterial_pct']}%, "
                    f"Res={prim_road_classes['macro_pct']['residential_pct']}%, Alts={valid_alts}, Div={pairwise_div:.3f}"
                )

        finally:
            # Strictly restore original algorithmic configuration
            alg.TURN_PENALTY_SHARP = orig_sharp
            alg.TURN_PENALTY_MODERATE = orig_moderate
            alg.two_wheeler_edge_cost = orig_edge_cost_fn

        all_sensitivity_results.append({
            "config_id": cfg_id,
            "description": cfg_desc,
            "corridors": cfg_corridor_results,
        })

    # Save JSON results
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_sensitivity_results, f, indent=2)
    print(f"\nSaved sensitivity JSON to: {out_json}")

    # Save CSV results
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"Saved sensitivity CSV to: {out_csv}")

    print("\n" + "=" * 80)
    print("PARAMETER SENSITIVITY EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_parameter_sensitivity_experiment()
