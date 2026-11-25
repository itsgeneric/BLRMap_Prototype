"""
Phase 10 Benchmark: Comparative Diversity Evaluation of Perpendicular-Offset
Alternative Route Generation vs. Yen's K-Shortest Paths (KSP) Baseline.

Evaluates 25 diverse origin-destination corridors across Bengaluru under identical conditions:
- Same Bengaluru road network (bengaluru_graph.pkl).
- Same snapped origin and destination nodes.
- Same two-wheeler edge impedance and turn penalties.
- Same detour tolerance cap (1.20x).
- Same 70% edge overlap threshold.
- Up to 3 alternative routes per corridor (K=4 total).

Outputs:
- research/literature_survey/10_alternative_routing/alternative_routing_raw.json
- research/literature_survey/10_alternative_routing/alternative_routing_raw.csv
"""

import sys
import os
import json
import csv
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
    path_cost,
    calc_route_overlap,
    calc_jaccard_similarity,
    calc_pairwise_diversity,
    build_split_route_candidates,
    yen_ksp_two_wheeler,
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


def run_phase_10_experiment():
    print("=" * 80)
    print("PHASE 10: ALTERNATIVE ROUTING COMPARISON (OFFSET vs. YEN'S KSP)")
    print("=" * 80)

    print("Loading Bengaluru road graph...")
    t0 = time.time()
    graph_manager.load_graph()
    G = graph_manager.G
    print(f"Graph loaded in {time.time() - t0:.2f}s (Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()})")

    penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)

    out_dir = os.path.join("research", "literature_survey", "10_alternative_routing")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "alternative_routing_raw.json")
    out_csv = os.path.join(out_dir, "alternative_routing_raw.csv")

    all_corridor_results = []
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
            "perpendicular_offset": {},
            "yen_ksp": {},
        }

        # ----------------------------------------------------
        # 1. Perpendicular Offset Routing (with 70% Overlap Filter)
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
        offset_routes = [c["nodes"] for c in offset_candidates if c["nodes"]]
        offset_diversity = calc_pairwise_diversity(G, offset_routes)

        corridor_data["perpendicular_offset"] = {
            "runtime_ms": round(t_offset_ms, 2),
            "candidates_generated": offset_diag["generated_count"],
            "candidates_rejected": len(offset_diag["rejected_candidates"]),
            "valid_alternatives_count": offset_diag["surviving_count"],
            "pairwise_diversity": round(offset_diversity, 4),
            "routes": [],
        }

        for r_idx, c in enumerate(offset_candidates):
            r_info = {
                "route_index": r_idx,
                "strategy": c["strategy"],
                "node_count": len(c["nodes"]),
                "distance_km": round(c["distance"] / 1000.0, 3),
                "cost": round(c["cost"], 2),
                "detour_ratio": round(c["detour_ratio"], 4),
                "overlap_ratio_pct": round(c["overlap_ratio"] * 100.0, 2),
                "jaccard_similarity": round(c["jaccard_similarity"], 4),
            }
            corridor_data["perpendicular_offset"]["routes"].append(r_info)

            # CSV record
            csv_rows.append({
                "corridor_id": od_id,
                "corridor_name": od_name,
                "method": "Perpendicular_Offset",
                "route_type": "Primary" if r_idx == 0 else f"Alt_{r_idx}",
                "strategy": c["strategy"],
                "node_count": len(c["nodes"]),
                "distance_km": round(c["distance"] / 1000.0, 3),
                "cost": round(c["cost"], 2),
                "detour_ratio": round(c["detour_ratio"], 4),
                "overlap_pct": round(c["overlap_ratio"] * 100.0, 2),
                "jaccard_similarity": round(c["jaccard_similarity"], 4),
                "runtime_ms": round(t_offset_ms, 2),
                "candidates_generated": offset_diag["generated_count"],
                "candidates_rejected": len(offset_diag["rejected_candidates"]),
                "surviving_alternatives": offset_diag["surviving_count"],
                "pairwise_diversity": round(offset_diversity, 4),
            })

        print(
            f"  [Offset] Time: {t_offset_ms:6.1f}ms | Generated: {offset_diag['generated_count']:2d} | "
            f"Rejected: {len(offset_diag['rejected_candidates']):2d} | Surviving Alts: {offset_diag['surviving_count']} | "
            f"Diversity: {offset_diversity:.3f}"
        )

        # ----------------------------------------------------
        # 2. Yen's KSP Baseline (Turn-Aware State-Expanded)
        # ----------------------------------------------------
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
        yen_routes = [p["nodes"] for p in yen_paths if p["nodes"]]
        yen_diversity = calc_pairwise_diversity(G, yen_routes)

        # Check how many Yen alternatives survive the 70% filter
        yen_surviving_alts = [
            p for idx, p in enumerate(yen_paths)
            if idx > 0 and p["overlap_ratio"] <= 0.70
        ]

        corridor_data["yen_ksp"] = {
            "runtime_ms": round(t_yen_ms, 2),
            "candidates_generated": yen_diag["candidates_generated"],
            "candidates_rejected_detour": yen_diag["rejected_detour"],
            "candidates_rejected_duplicates": yen_diag["rejected_duplicates"],
            "total_paths_found": len(yen_paths),
            "surviving_under_70pct_filter": len(yen_surviving_alts),
            "pairwise_diversity": round(yen_diversity, 4),
            "routes": [],
        }

        for r_idx, p in enumerate(yen_paths):
            r_info = {
                "route_index": r_idx,
                "strategy": p["strategy"],
                "node_count": len(p["nodes"]),
                "distance_km": round(p["distance"] / 1000.0, 3),
                "cost": round(p["cost"], 2),
                "detour_ratio": round(p["detour_ratio"], 4),
                "overlap_ratio_pct": round(p["overlap_ratio"] * 100.0, 2),
                "jaccard_similarity": round(p["jaccard_similarity"], 4),
                "survives_70pct_filter": bool(r_idx == 0 or p["overlap_ratio"] <= 0.70),
            }
            corridor_data["yen_ksp"]["routes"].append(r_info)

            # CSV record
            csv_rows.append({
                "corridor_id": od_id,
                "corridor_name": od_name,
                "method": "Yens_KSP_Raw",
                "route_type": "Primary" if r_idx == 0 else f"Alt_{r_idx}",
                "strategy": p["strategy"],
                "node_count": len(p["nodes"]),
                "distance_km": round(p["distance"] / 1000.0, 3),
                "cost": round(p["cost"], 2),
                "detour_ratio": round(p["detour_ratio"], 4),
                "overlap_pct": round(p["overlap_ratio"] * 100.0, 2),
                "jaccard_similarity": round(p["jaccard_similarity"], 4),
                "runtime_ms": round(t_yen_ms, 2),
                "candidates_generated": yen_diag["candidates_generated"],
                "candidates_rejected": yen_diag["rejected_detour"] + yen_diag["rejected_duplicates"],
                "surviving_alternatives": len(yen_surviving_alts),
                "pairwise_diversity": round(yen_diversity, 4),
            })

        print(
            f"  [Yen KSP] Time: {t_yen_ms:6.1f}ms | Generated: {yen_diag['candidates_generated']:2d} | "
            f"Paths Found: {len(yen_paths)} | Surviving <=70%: {len(yen_surviving_alts)} | "
            f"Diversity: {yen_diversity:.3f}"
        )

        all_corridor_results.append(corridor_data)

    # Save raw JSON
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_corridor_results, f, indent=2)
    print(f"\nSaved raw JSON results to {out_json}")

    # Save raw CSV
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"Saved raw CSV results to {out_csv}")

    # --------------------------------------------------------
    # Aggregate Comparative Summary Statistics
    # --------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 10 EXPERIMENTAL SUMMARY ACROSS 25 BENGALURU CORRIDORS")
    print("=" * 80)

    # Offset metrics
    offset_alts_counts = [c["perpendicular_offset"]["valid_alternatives_count"] for c in all_corridor_results]
    offset_runtimes = [c["perpendicular_offset"]["runtime_ms"] for c in all_corridor_results]
    offset_diversities = [c["perpendicular_offset"]["pairwise_diversity"] for c in all_corridor_results]

    # Collect alternative routes (r_idx > 0)
    offset_alt_overlaps = []
    offset_alt_jaccards = []
    offset_alt_detours = []
    for c in all_corridor_results:
        for r in c["perpendicular_offset"]["routes"][1:]:
            offset_alt_overlaps.append(r["overlap_ratio_pct"])
            offset_alt_jaccards.append(r["jaccard_similarity"])
            offset_alt_detours.append(r["detour_ratio"])

    # Yen metrics
    yen_paths_counts = [len(c["yen_ksp"]["routes"]) - 1 for c in all_corridor_results]
    yen_surviving_counts = [c["yen_ksp"]["surviving_under_70pct_filter"] for c in all_corridor_results]
    yen_runtimes = [c["yen_ksp"]["runtime_ms"] for c in all_corridor_results]
    yen_diversities = [c["yen_ksp"]["pairwise_diversity"] for c in all_corridor_results]

    yen_alt_overlaps = []
    yen_alt_jaccards = []
    yen_alt_detours = []
    for c in all_corridor_results:
        for r in c["yen_ksp"]["routes"][1:]:
            yen_alt_overlaps.append(r["overlap_ratio_pct"])
            yen_alt_jaccards.append(r["jaccard_similarity"])
            yen_alt_detours.append(r["detour_ratio"])

    print("\n--- PERPENDICULAR OFFSET ALTERNATIVE ROUTING (WITH 70% FILTER) ---")
    print(f"Total Valid Alternatives Generated: {sum(offset_alts_counts)} (Mean: {sum(offset_alts_counts)/25:.2f} per corridor)")
    print(f"Corridors with >= 1 Valid Alternative: {sum(1 for cnt in offset_alts_counts if cnt > 0)} / 25 ({sum(1 for cnt in offset_alts_counts if cnt > 0)/25*100:.1f}%)")
    print(f"Mean Execution Runtime:             {sum(offset_runtimes)/25:.2f} ms")
    if offset_alt_overlaps:
        print(f"Mean Shared Edge Overlap:           {sum(offset_alt_overlaps)/len(offset_alt_overlaps):.2f}%")
        print(f"Mean Jaccard Edge Similarity:       {sum(offset_alt_jaccards)/len(offset_alt_jaccards):.4f}")
        print(f"Mean Detour Ratio:                  {sum(offset_alt_detours)/len(offset_alt_detours):.3f}")
    print(f"Mean Pairwise Route Diversity:      {sum(offset_diversities)/25:.4f}")

    print("\n--- YEN'S K-SHORTEST PATHS BASELINE (RAW KSP, K=4) ---")
    print(f"Total Raw Alternatives Generated:   {sum(yen_paths_counts)} (Mean: {sum(yen_paths_counts)/25:.2f} per corridor)")
    print(f"Total Alternatives Surviving <=70%: {sum(yen_surviving_counts)} (Mean: {sum(yen_surviving_counts)/25:.2f} per corridor)")
    print(f"Corridors with >= 1 Surviving Alt:  {sum(1 for cnt in yen_surviving_counts if cnt > 0)} / 25 ({sum(1 for cnt in yen_surviving_counts if cnt > 0)/25*100:.1f}%)")
    print(f"Mean Execution Runtime:             {sum(yen_runtimes)/25:.2f} ms")
    if yen_alt_overlaps:
        print(f"Mean Shared Edge Overlap:           {sum(yen_alt_overlaps)/len(yen_alt_overlaps):.2f}%")
        print(f"Mean Jaccard Edge Similarity:       {sum(yen_alt_jaccards)/len(yen_alt_jaccards):.4f}")
        print(f"Mean Detour Ratio:                  {sum(yen_alt_detours)/len(yen_alt_detours):.3f}")
    print(f"Mean Pairwise Route Diversity:      {sum(yen_diversities)/25:.4f}")

    print("\n" + "=" * 80)
    print("BENCHMARK EXECUTION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_phase_10_experiment()
