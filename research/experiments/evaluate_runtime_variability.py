"""
Phase 11: Algorithmic Runtime and Variability Evaluation Script
Repeats runtime measurements across the benchmark corridors for:
1. Uniform-cost Dijkstra baseline
2. Standard Admissible A*
3. Aggressive A*
4. Perpendicular-Offset Alternative Routing
5. Yen's KSP Baseline

Evaluates:
- Mean runtime (ms)
- Standard deviation (ms)
- Median runtime (ms)
- Minimum and Maximum runtime (ms)
- Coefficient of variation (CV)
- Relative speedups vs Dijkstra and Yen's KSP

Outputs:
- research/literature_survey/11_route_quality_evaluation/runtime_evaluation.json
- research/literature_survey/11_route_quality_evaluation/runtime_evaluation.csv
"""

import sys
import os
import json
import csv
import time
import statistics
import osmnx as ox

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
    build_split_route_candidates,
    yen_ksp_two_wheeler,
)

# 10 Core corridors covering Short (<3km), Medium (4-9km), and Long (>10km) urban trips
BENCHMARK_CORRIDORS = [
    {"id": "OD_01", "name": "BNMIT to MG Road", "dist_cat": "Long (10.1 km)", "from_lat": 12.9237, "from_lng": 77.5714, "to_lat": 12.9756, "to_lng": 77.6066},
    {"id": "OD_02", "name": "Koramangala to Indiranagar", "dist_cat": "Medium (6.4 km)", "from_lat": 12.9352, "from_lng": 77.6245, "to_lat": 12.9719, "to_lng": 77.6412},
    {"id": "OD_03", "name": "Electronic City to Silk Board", "dist_cat": "Long (9.5 km)", "from_lat": 12.8452, "from_lng": 77.6602, "to_lat": 12.9176, "to_lng": 77.6238},
    {"id": "OD_04", "name": "Whitefield to Marathahalli", "dist_cat": "Medium (8.8 km)", "from_lat": 12.9698, "from_lng": 77.7500, "to_lat": 12.9569, "to_lng": 77.7011},
    {"id": "OD_05", "name": "Hebbal to Majestic", "dist_cat": "Long (9.9 km)", "from_lat": 13.0358, "from_lng": 77.5970, "to_lat": 12.9767, "to_lng": 77.5713},
    {"id": "OD_07", "name": "HSR Layout to Bellandur", "dist_cat": "Medium (5.8 km)", "from_lat": 12.9121, "from_lng": 77.6446, "to_lat": 12.9304, "to_lng": 77.6784},
    {"id": "OD_09", "name": "Rajajinagar to Commercial Street", "dist_cat": "Medium (8.3 km)", "from_lat": 12.9915, "from_lng": 77.5523, "to_lat": 12.9822, "to_lng": 77.6083},
    {"id": "OD_10", "name": "BTM Layout to Domlur", "dist_cat": "Medium (7.8 km)", "from_lat": 12.9166, "from_lng": 77.6101, "to_lat": 12.9609, "to_lng": 77.6387},
    {"id": "OD_12", "name": "Frazer Town to Shivajinagar", "dist_cat": "Short (2.7 km)", "from_lat": 12.9982, "from_lng": 77.6145, "to_lat": 12.9856, "to_lng": 77.6006},
    {"id": "OD_15", "name": "Yelahanka to Hebbal", "dist_cat": "Medium (8.7 km)", "from_lat": 13.1007, "from_lng": 77.5963, "to_lat": 13.0358, "to_lng": 77.5970},
]

NUM_REPETITIONS_FAST = 5
NUM_REPETITIONS_YEN = 3


def calc_stats(run_times):
    if not run_times:
        return {"mean": 0.0, "std": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "cv_pct": 0.0}
    mean_val = statistics.mean(run_times)
    std_val = statistics.stdev(run_times) if len(run_times) > 1 else 0.0
    med_val = statistics.median(run_times)
    min_val = min(run_times)
    max_val = max(run_times)
    cv_pct = (std_val / mean_val * 100.0) if mean_val > 0 else 0.0
    return {
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "median": round(med_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "cv_pct": round(cv_pct, 2),
    }


def run_runtime_variability_experiment():
    print("=" * 80)
    print("PHASE 11: RUNTIME AND VARIABILITY EVALUATION EXPERIMENT")
    print("=" * 80)

    print("Loading Bengaluru road graph...")
    t0 = time.time()
    graph_manager.load_graph()
    G = graph_manager.G
    print(f"Graph loaded in {time.time() - t0:.2f}s ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")

    penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)

    out_dir = os.path.join(PROJECT_ROOT, "research", "literature_survey", "11_route_quality_evaluation")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "runtime_evaluation.json")
    out_csv = os.path.join(out_dir, "runtime_evaluation.csv")

    results_by_corridor = []
    csv_rows = []

    for idx, pair in enumerate(BENCHMARK_CORRIDORS, 1):
        od_id = pair["id"]
        od_name = pair["name"]
        dist_cat = pair["dist_cat"]
        print(f"\n[{idx}/{len(BENCHMARK_CORRIDORS)}] Benchmarking {od_id}: {od_name} ({dist_cat})...")

        s_node = int(ox.nearest_nodes(G, pair["from_lng"], pair["from_lat"]))
        e_node = int(ox.nearest_nodes(G, pair["to_lng"], pair["to_lat"]))

        corridor_benchmark = {
            "id": od_id,
            "name": od_name,
            "distance_category": dist_cat,
            "algorithms": {},
        }

        # ----------------------------------------------------
        # 1. Dijkstra Baseline
        # ----------------------------------------------------
        dijkstra_runs = []
        for r in range(NUM_REPETITIONS_FAST):
            t_s = time.perf_counter()
            two_wheeler_astar(G, s_node, e_node, graph_manager, penalties=penalties, heuristic_mode="dijkstra")
            dijkstra_runs.append((time.perf_counter() - t_s) * 1000.0)
        corridor_benchmark["algorithms"]["Dijkstra"] = {"runs_ms": dijkstra_runs, "stats": calc_stats(dijkstra_runs)}

        # ----------------------------------------------------
        # 2. Standard Admissible A*
        # ----------------------------------------------------
        admissible_runs = []
        for r in range(NUM_REPETITIONS_FAST):
            t_s = time.perf_counter()
            two_wheeler_astar(G, s_node, e_node, graph_manager, penalties=penalties, heuristic_mode="admissible")
            admissible_runs.append((time.perf_counter() - t_s) * 1000.0)
        corridor_benchmark["algorithms"]["Admissible_AStar"] = {"runs_ms": admissible_runs, "stats": calc_stats(admissible_runs)}

        # ----------------------------------------------------
        # 3. Aggressive A*
        # ----------------------------------------------------
        aggressive_runs = []
        for r in range(NUM_REPETITIONS_FAST):
            t_s = time.perf_counter()
            two_wheeler_astar(G, s_node, e_node, graph_manager, penalties=penalties, heuristic_mode="aggressive")
            aggressive_runs.append((time.perf_counter() - t_s) * 1000.0)
        corridor_benchmark["algorithms"]["Aggressive_AStar"] = {"runs_ms": aggressive_runs, "stats": calc_stats(aggressive_runs)}

        # ----------------------------------------------------
        # 4. Perpendicular Offset Routing
        # ----------------------------------------------------
        offset_runs = []
        for r in range(NUM_REPETITIONS_FAST):
            t_s = time.perf_counter()
            build_split_route_candidates(
                G, graph_manager,
                pair["from_lat"], pair["from_lng"],
                pair["to_lat"], pair["to_lng"],
                penalties=penalties,
                max_overlap=0.70,
                max_detour=1.20,
                max_alternatives=3,
            )
            offset_runs.append((time.perf_counter() - t_s) * 1000.0)
        corridor_benchmark["algorithms"]["Perpendicular_Offset"] = {"runs_ms": offset_runs, "stats": calc_stats(offset_runs)}

        # ----------------------------------------------------
        # 5. Yen's KSP Baseline (K=4)
        # ----------------------------------------------------
        yen_runs = []
        for r in range(NUM_REPETITIONS_YEN):
            t_s = time.perf_counter()
            yen_ksp_two_wheeler(
                G, s_node, e_node, graph_manager,
                penalties=penalties,
                K=4,
                max_detour=1.20,
                apply_overlap_filter=False,
            )
            yen_runs.append((time.perf_counter() - t_s) * 1000.0)
        corridor_benchmark["algorithms"]["Yens_KSP"] = {"runs_ms": yen_runs, "stats": calc_stats(yen_runs)}

        # Print corridor summary
        d_mean = corridor_benchmark["algorithms"]["Dijkstra"]["stats"]["mean"]
        a_mean = corridor_benchmark["algorithms"]["Admissible_AStar"]["stats"]["mean"]
        ag_mean = corridor_benchmark["algorithms"]["Aggressive_AStar"]["stats"]["mean"]
        off_mean = corridor_benchmark["algorithms"]["Perpendicular_Offset"]["stats"]["mean"]
        yen_mean = corridor_benchmark["algorithms"]["Yens_KSP"]["stats"]["mean"]

        print(
            f"  Dijkstra: {d_mean:.1f}ms (std: {corridor_benchmark['algorithms']['Dijkstra']['stats']['std']:.1f}) | "
            f"Admissible: {a_mean:.1f}ms (speedup: {d_mean/a_mean:.2f}x) | "
            f"Aggressive: {ag_mean:.1f}ms | "
            f"Offset: {off_mean:.1f}ms | Yen: {yen_mean:.1f}ms (speedup vs Yen: {yen_mean/off_mean:.2f}x)"
        )

        for alg_name, data in corridor_benchmark["algorithms"].items():
            st = data["stats"]
            csv_rows.append({
                "corridor_id": od_id,
                "corridor_name": od_name,
                "distance_category": dist_cat,
                "algorithm": alg_name,
                "repetitions": len(data["runs_ms"]),
                "mean_ms": st["mean"],
                "std_ms": st["std"],
                "median_ms": st["median"],
                "min_ms": st["min"],
                "max_ms": st["max"],
                "cv_pct": st["cv_pct"],
                "speedup_vs_dijkstra": round(d_mean / st["mean"], 2) if st["mean"] > 0 else 0.0,
            })

        results_by_corridor.append(corridor_benchmark)

    # Save JSON results
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results_by_corridor, f, indent=2)
    print(f"\nSaved runtime JSON to: {out_json}")

    # Save CSV results
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"Saved runtime CSV to: {out_csv}")

    print("\n" + "=" * 80)
    print("RUNTIME EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_runtime_variability_experiment()
