"""
Phase 13.1 — Stage 2B Full Ablation Study Runner.

Executes the complete experimental study according to:
- phase_13_0_experimental_design.md
- phase_13_0_1_correction_report.md
- phase_13_1_3_final_preflight.md
- phase_13_2A_repetition_validation_report.md

Experiments:
- Experiment A: Turn Awareness and State Expansion (A0, A1, A2) - 25 corridors, 5 reps
- Experiment B: Road-Class Impedance (B0, B1, B2) - 25 corridors, 5 reps
- Experiment C: Turn-Penalty Sensitivity (C0, C1, C2, C3) - 25 corridors, 5 reps
- Experiment D: Bridge & Roundabout 2x2 Factorial (D1, D2, D3, D4) - 25 corridors, 5 reps
- Experiment E1: Perpendicular Offset Alternatives - 25 corridors, 3 reps
- Experiment E2 & E3: Raw and Filtered Yen K-SP (K=4) - 5 selected corridors only, 3 reps

Outputs:
- stage_2b_partial_results.json (checkpoint after each corridor)
- stage_2b_full_ablation_results.json (final complete structured dataset)
"""

import sys
import os
import json
import time
import math
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import routing.algorithms as alg
from routing.graph_manager import graph_manager
from routing.algorithms import build_two_wheeler_penalties

CURR_DIR = os.path.abspath(os.path.dirname(__file__))
if CURR_DIR not in sys.path:
    sys.path.insert(0, CURR_DIR)

from ablation_harness import (
    BENCHMARK_CORRIDORS,
    SELECTED_YEN_CORRIDORS,
    validate_od_corpus,
    scoped_ablation_context,
    run_experiment_a_corridor,
    run_experiment_b_corridor,
    run_experiment_c_corridor,
    run_experiment_d_corridor,
    run_experiment_e_corridor,
)


def verify_execution_safeguards():
    """Verify all pre-execution safeguards required by the approved protocol."""
    print("\n--- Safeguard Verification ---")

    # 1. Corpus size and Yen identifiers
    assert len(BENCHMARK_CORRIDORS) == 25, f"Expected 25 corridors, got {len(BENCHMARK_CORRIDORS)}"
    expected_yen = ["OD_23", "OD_02", "OD_04", "OD_03", "OD_01"]
    assert SELECTED_YEN_CORRIDORS == expected_yen, f"Expected Yen set {expected_yen}, got {SELECTED_YEN_CORRIDORS}"
    print(f"[OK] 25 corridors verified. Selected Yen corridors verified: {SELECTED_YEN_CORRIDORS}")

    # 2. Production defaults check
    assert alg.TURN_PENALTY_SHARP == 25.0, f"Unexpected TURN_PENALTY_SHARP: {alg.TURN_PENALTY_SHARP}"
    assert alg.TURN_PENALTY_MODERATE == 8.0, f"Unexpected TURN_PENALTY_MODERATE: {alg.TURN_PENALTY_MODERATE}"
    print(f"[OK] Production defaults verified (Sharp: 25.0, Moderate: 8.0)")

    # 3. Disk space check (> 1 GB free)
    total, used, free = shutil.disk_usage(CURR_DIR)
    free_gb = free / (1024 ** 3)
    assert free_gb > 1.0, f"Insufficient disk space: {free_gb:.2f} GB available"
    print(f"[OK] Free disk space: {free_gb:.2f} GB")

    # 4. Scoped context manager self-test
    orig_sharp = alg.TURN_PENALTY_SHARP
    orig_mod = alg.TURN_PENALTY_MODERATE
    orig_fn = alg.two_wheeler_edge_cost
    with scoped_ablation_context(turn_penalty_sharp=99.0, turn_penalty_moderate=77.0):
        assert alg.TURN_PENALTY_SHARP == 99.0
        assert alg.TURN_PENALTY_MODERATE == 77.0
    assert alg.TURN_PENALTY_SHARP == orig_sharp
    assert alg.TURN_PENALTY_MODERATE == orig_mod
    assert alg.two_wheeler_edge_cost == orig_fn
    print("[OK] Scoped override and restoration self-test passed.")


def main():
    start_wall_time = time.time()
    start_time_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    print("=" * 80)
    print("PHASE 13.1 — STAGE 2B: FULL ABLATION STUDY EXECUTION (25 CORRIDORS)")
    print(f"Start time: {start_time_iso}")
    print("=" * 80)

    # 1. Pre-execution Safeguards
    verify_execution_safeguards()

    # 2. Load Graph
    print("\n[Step 1] Loading Bengaluru road network graph...")
    t0 = time.time()
    graph_manager.load_graph()
    G = graph_manager.G
    print(f"  Graph loaded in {time.time() - t0:.2f}s ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")

    # 3. Validate Entire 25-Corridor Corpus
    print("\n[Step 2] Validating corpus connectivity and endpoint distinctness...")
    val_res = validate_od_corpus(G, graph_manager)
    assert val_res["all_distinct"], "Corpus validation failed: identical endpoints detected"
    assert val_res["all_connected"], "Corpus validation failed: disconnected corridor detected"
    print(f"  All {val_res['total_corridors']} corridors are connected and resolve to distinct endpoints.")

    # 4. Prepare Results Structure and Production Penalties
    prod_penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)

    out_file_final = os.path.join(CURR_DIR, "stage_2b_full_ablation_results.json")
    out_file_partial = os.path.join(CURR_DIR, "stage_2b_partial_results.json")

    results_data = {
        "metadata": {
            "title": "Phase 13.1 Stage 2B Full Ablation Study Results",
            "start_time": start_time_iso,
            "completion_time": None,
            "elapsed_seconds": None,
            "total_corridors": 25,
            "yen_selected_corridors": SELECTED_YEN_CORRIDORS,
            "repetition_protocol": {
                "exp_a": 5,
                "exp_b": 5,
                "exp_c": 5,
                "exp_d": 5,
                "exp_e1": 3,
                "exp_e2_yen": 3,
                "exp_e3_yen": 3,
            },
            "production_parameters": {
                "TURN_PENALTY_SHARP": 25.0,
                "TURN_PENALTY_MODERATE": 8.0,
                "main_road_penalty": 1.5,
                "inner_road_multiplier": 0.9,
                "bridge_discount_main_roads": 0.8,
                "roundabout_multiplier": 0.95,
                "max_detour": 1.20,
                "max_overlap": 0.70,
            }
        },
        "corpus_validation": val_res,
        "corridors": {}
    }

    # 5. Execute 25 Corridors
    print("\n[Step 3] Executing Ablation Benchmarks across all 25 corridors...")
    total_corridors = len(BENCHMARK_CORRIDORS)

    for idx, corridor in enumerate(BENCHMARK_CORRIDORS, 1):
        c_id = corridor["id"]
        c_name = corridor["name"]
        c_dist = corridor["dist_cat"]
        is_yen = c_id in SELECTED_YEN_CORRIDORS

        t_corr_start = time.time()
        print(f"\n[{idx:02d}/{total_corridors:02d}] Corridor {c_id}: {c_name} ({c_dist}) | Yen: {'YES' if is_yen else 'NO'}")
        print(f"       From: ({corridor['from_lat']}, {corridor['from_lng']}) -> Snapped: {corridor['start_node']}")
        print(f"       To:   ({corridor['to_lat']}, {corridor['to_lng']}) -> Snapped: {corridor['end_node']}")

        corridor_record = {
            "corridor_info": corridor,
            "is_yen_selected": is_yen,
            "start_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "experiments": {},
            "exceptions": []
        }

        # --- Experiment A (5 reps) ---
        try:
            t_sub = time.time()
            exp_a_res = run_experiment_a_corridor(G, graph_manager, corridor, prod_penalties, reps=5)
            corridor_record["experiments"]["Experiment_A"] = exp_a_res
            print(f"       Exp A (Turn-Awareness) completed in {time.time() - t_sub:.2f}s "
                  f"[A0 med={exp_a_res['A0_Turn_Aware']['runtime_ms']}ms, "
                  f"A1 med={exp_a_res['A1_Turn_Unaware_StateExpanded']['runtime_ms']}ms, "
                  f"A2 med={exp_a_res['A2_Turn_Unaware_NodeLevel']['runtime_ms']}ms]")
        except Exception as exc:
            print(f"       [ERROR] Exp A failed: {exc}")
            corridor_record["exceptions"].append({"experiment": "Exp_A", "error": str(exc)})

        # --- Experiment B (5 reps) ---
        try:
            t_sub = time.time()
            exp_b_res = run_experiment_b_corridor(G, graph_manager, corridor, prod_penalties, reps=5)
            corridor_record["experiments"]["Experiment_B"] = exp_b_res
            print(f"       Exp B (Road-Class) completed in {time.time() - t_sub:.2f}s "
                  f"[B0 med={exp_b_res['B0_Production_2W']['runtime_ms']}ms, "
                  f"B1 med={exp_b_res['B1_Neutral_Road_Class']['runtime_ms']}ms, "
                  f"B2 med={exp_b_res['B2_Physical_Distance_Ref']['runtime_ms']}ms]")
        except Exception as exc:
            print(f"       [ERROR] Exp B failed: {exc}")
            corridor_record["exceptions"].append({"experiment": "Exp_B", "error": str(exc)})

        # --- Experiment C (5 reps) ---
        try:
            t_sub = time.time()
            exp_c_res = run_experiment_c_corridor(G, graph_manager, corridor, prod_penalties, reps=5)
            corridor_record["experiments"]["Experiment_C"] = exp_c_res
            print(f"       Exp C (Turn Sensitivity) completed in {time.time() - t_sub:.2f}s "
                  f"[C0 med={exp_c_res['C0_Zero_Turn_Penalties']['runtime_ms']}ms, "
                  f"C2 med={exp_c_res['C2_Baseline_Turn_Penalties']['runtime_ms']}ms, "
                  f"C3 med={exp_c_res['C3_High_Turn_Penalties']['runtime_ms']}ms]")
        except Exception as exc:
            print(f"       [ERROR] Exp C failed: {exc}")
            corridor_record["exceptions"].append({"experiment": "Exp_C", "error": str(exc)})

        # --- Experiment D (5 reps) ---
        try:
            t_sub = time.time()
            exp_d_res = run_experiment_d_corridor(G, graph_manager, corridor, prod_penalties, reps=5)
            corridor_record["experiments"]["Experiment_D"] = exp_d_res
            print(f"       Exp D (Bridge/Roundabout) completed in {time.time() - t_sub:.2f}s "
                  f"[D1 med={exp_d_res['D1_Bridge_Off_Roundabout_Off']['runtime_ms']}ms, "
                  f"D4 med={exp_d_res['D4_Bridge_On_Roundabout_On']['runtime_ms']}ms]")
        except Exception as exc:
            print(f"       [ERROR] Exp D failed: {exc}")
            corridor_record["exceptions"].append({"experiment": "Exp_D", "error": str(exc)})

        # --- Experiment E (3 reps E1, 3 reps E2 & E3 if selected) ---
        try:
            t_sub = time.time()
            exp_e_res = run_experiment_e_corridor(
                G, graph_manager, corridor, prod_penalties,
                reps_offset=3, reps_yen=3, run_yen=is_yen
            )
            corridor_record["experiments"]["Experiment_E"] = exp_e_res
            e1 = exp_e_res["E1_Perpendicular_Offset"]
            print(f"       Exp E (Alternatives) completed in {time.time() - t_sub:.2f}s "
                  f"[E1 Offset med={e1['runtime_ms']}ms, alts={e1['surviving_count']}/{e1['generated_count']}, div={e1['pairwise_diversity']}]")
            if is_yen:
                e2 = exp_e_res["E2_Raw_Yen_KSP"]
                e3 = exp_e_res["E3_Filtered_Yen_KSP"]
                print(f"         E2 Raw Yen med={e2['runtime_ms']}ms, status={e2['outcome_status']}, alts={e2['surviving_alts']}, div={e2['pairwise_diversity']}")
                print(f"         E3 Filtered Yen med={e3['runtime_ms']}ms, status={e3['outcome_status']}, alts={e3['surviving_alts']}, div={e3['pairwise_diversity']}, rej_ovl={e3['rejected_overlap']}")
        except Exception as exc:
            print(f"       [ERROR] Exp E failed: {exc}")
            corridor_record["exceptions"].append({"experiment": "Exp_E", "error": str(exc)})

        corr_elapsed = time.time() - t_corr_start
        corridor_record["end_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        corridor_record["elapsed_seconds"] = round(corr_elapsed, 2)
        print(f"       --> Corridor {c_id} completed in {corr_elapsed:.2f}s ({corr_elapsed / 60.0:.2f} min)")

        # Save to memory and checkpoint to disk
        results_data["corridors"][c_id] = corridor_record
        with open(out_file_partial, "w", encoding="utf-8") as f:
            json.dump(results_data, f, indent=2)

    # 6. Post-Run Production Defaults and Invariant Verification
    print("\n[Step 4] Post-run integrity verification...")
    assert alg.TURN_PENALTY_SHARP == 25.0, "Integrity failure: TURN_PENALTY_SHARP was altered!"
    assert alg.TURN_PENALTY_MODERATE == 8.0, "Integrity failure: TURN_PENALTY_MODERATE was altered!"
    assert len(results_data["corridors"]) == 25, f"Expected 25 corridors in output, got {len(results_data['corridors'])}"

    total_elapsed = time.time() - start_wall_time
    completion_time_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    results_data["metadata"]["completion_time"] = completion_time_iso
    results_data["metadata"]["elapsed_seconds"] = round(total_elapsed, 2)

    # 7. Write Final Complete Structured Dataset
    with open(out_file_final, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

    print(f"\n" + "=" * 80)
    print("PHASE 13.1 — STAGE 2B FULL ABLATION STUDY COMPLETE")
    print(f"Total elapsed time: {total_elapsed:.2f}s ({total_elapsed / 60.0:.2f} minutes / {total_elapsed / 3600.0:.2f} hours)")
    print(f"Final results saved to: {out_file_final}")
    print(f"Checkpoint results saved to: {out_file_partial}")
    print("=" * 80)


if __name__ == "__main__":
    main()
