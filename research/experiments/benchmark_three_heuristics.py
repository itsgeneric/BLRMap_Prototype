"""
Three-Way Heuristic Comparison Benchmark on the Bengaluru Road Network.

Compares:
1. Uniform-cost Dijkstra baseline (h = 0.0)
2. Standard Admissible A* (h = 0.8 * haversine)
3. Legacy Aggressive A* (h = 1.25 * haversine)

Evaluates:
- Route Cost
- Physical Distance (km)
- Expanded States
- Visited Nodes
- Explored Edge Transitions
- Search Runtime (ms)
- Optimality Gap (%) vs. Dijkstra Ground Truth
- Search State Reduction (%) vs. Dijkstra
"""

import sys
import os
import json
import time
import osmnx as ox

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.join(_REPO_ROOT, "backend"))

from routing.graph_manager import graph_manager
from routing.algorithms import (
    two_wheeler_astar,
    build_two_wheeler_penalties,
    calc_route_distance,
)

OD_PAIRS = [
    {
        "id": "OD_01",
        "name": "BNMIT to MG Road",
        "from_lat": 12.9237, "from_lng": 77.5714,
        "to_lat": 12.9756, "to_lng": 77.6066,
    },
    {
        "id": "OD_02",
        "name": "Koramangala to Indiranagar",
        "from_lat": 12.9352, "from_lng": 77.6245,
        "to_lat": 12.9719, "to_lng": 77.6412,
    },
    {
        "id": "OD_03",
        "name": "Electronic City to Silk Board",
        "from_lat": 12.8452, "from_lng": 77.6602,
        "to_lat": 12.9176, "to_lng": 77.6238,
    },
    {
        "id": "OD_04",
        "name": "Whitefield to Marathahalli",
        "from_lat": 12.9698, "from_lng": 77.7500,
        "to_lat": 12.9569, "to_lng": 77.7011,
    },
    {
        "id": "OD_05",
        "name": "Hebbal to Majestic",
        "from_lat": 13.0358, "from_lng": 77.5970,
        "to_lat": 12.9767, "to_lng": 77.5713,
    },
    {
        "id": "OD_06",
        "name": "Jayanagar 4th Block to Malleshwaram",
        "from_lat": 12.9250, "from_lng": 77.5838,
        "to_lat": 13.0031, "to_lng": 77.5643,
    },
    {
        "id": "OD_07",
        "name": "HSR Layout to Bellandur",
        "from_lat": 12.9121, "from_lng": 77.6446,
        "to_lat": 12.9304, "to_lng": 77.6784,
    },
    {
        "id": "OD_08",
        "name": "Banashankari to Yeshwanthpur",
        "from_lat": 12.9255, "from_lng": 77.5468,
        "to_lat": 13.0285, "to_lng": 77.5409,
    },
    {
        "id": "OD_09",
        "name": "Rajajinagar to Commercial Street",
        "from_lat": 12.9915, "from_lng": 77.5523,
        "to_lat": 12.9822, "to_lng": 77.6083,
    },
    {
        "id": "OD_10",
        "name": "BTM Layout to Domlur",
        "from_lat": 12.9166, "from_lng": 77.6101,
        "to_lat": 12.9609, "to_lng": 77.6387,
    },
]


def run_benchmark():
    print("=" * 80)
    print("STARTING 3-WAY HEURISTIC BENCHMARK ON BENGALURU GRAPH")
    print("=" * 80)
    print("Loading graph...")
    t0 = time.time()
    graph_manager.load_graph()
    G = graph_manager.G
    print(f"Graph loaded in {time.time() - t0:.2f}s (Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()})")

    penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)
    modes = ["dijkstra", "admissible", "aggressive"]

    all_results = []

    for pair in OD_PAIRS:
        od_id = pair["id"]
        od_name = pair["name"]
        print(f"\nProcessing {od_id}: {od_name}...")

        start_node = ox.nearest_nodes(G, pair["from_lng"], pair["from_lat"])
        end_node = ox.nearest_nodes(G, pair["to_lng"], pair["to_lat"])

        pair_result = {
            "id": od_id,
            "name": od_name,
            "start_node": int(start_node),
            "end_node": int(end_node),
            "modes": {},
        }

        dijkstra_cost = None

        for mode in modes:
            res = two_wheeler_astar(
                G,
                start_node,
                end_node,
                graph_manager,
                penalties=penalties,
                heuristic_mode=mode,
                return_metrics=True,
            )
            route = res["route"]
            cost = res["cost"]
            dist_km = calc_route_distance(G, route) / 1000.0

            if mode == "dijkstra":
                dijkstra_cost = cost
                opt_gap = 0.0
            else:
                opt_gap = ((cost - dijkstra_cost) / dijkstra_cost) * 100.0

            mode_data = {
                "route_len_nodes": len(route),
                "distance_km": round(dist_km, 3),
                "cost": round(cost, 2),
                "expanded_states": res["expanded_states"],
                "expanded_nodes": res["expanded_nodes"],
                "explored_transitions": res["explored_transitions"],
                "runtime_ms": round(res["runtime_ms"], 2),
                "optimality_gap_pct": round(opt_gap, 4),
            }
            pair_result["modes"][mode] = mode_data

            print(
                f"  [{mode:10s}] Cost: {cost:8.2f} | Dist: {dist_km:5.2f}km | "
                f"States: {res['expanded_states']:6d} | Runtime: {res['runtime_ms']:6.2f}ms | "
                f"Opt Gap: {opt_gap:6.3f}%"
            )

        all_results.append(pair_result)

    # Save raw benchmark output to json
    out_dir = os.path.join("research", "literature_survey", "09_astar_correction")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "heuristic_benchmark_raw.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved raw benchmark data to {out_json}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY STATISTICS ACROSS 10 OD CORRIDORS")
    print("=" * 80)
    for mode in modes:
        avg_cost = sum(r["modes"][mode]["cost"] for r in all_results) / len(all_results)
        avg_dist = sum(r["modes"][mode]["distance_km"] for r in all_results) / len(all_results)
        avg_states = sum(r["modes"][mode]["expanded_states"] for r in all_results) / len(all_results)
        avg_time = sum(r["modes"][mode]["runtime_ms"] for r in all_results) / len(all_results)
        max_gap = max(r["modes"][mode]["optimality_gap_pct"] for r in all_results)
        avg_gap = sum(r["modes"][mode]["optimality_gap_pct"] for r in all_results) / len(all_results)

        dijkstra_states = sum(r["modes"]["dijkstra"]["expanded_states"] for r in all_results) / len(all_results)
        reduction = ((dijkstra_states - avg_states) / dijkstra_states) * 100.0

        print(f"Mode: {mode.upper()}")
        print(f"  Avg Cost:            {avg_cost:10.2f}")
        print(f"  Avg Distance:        {avg_dist:10.2f} km")
        print(f"  Avg Expanded States: {avg_states:10.1f} ({reduction:+.1f}% vs Dijkstra)")
        print(f"  Avg Runtime:         {avg_time:10.2f} ms")
        print(f"  Avg Optimality Gap:  {avg_gap:10.4f}%")
        print(f"  Max Optimality Gap:  {max_gap:10.4f}%")
        print("-" * 50)


if __name__ == "__main__":
    run_benchmark()
