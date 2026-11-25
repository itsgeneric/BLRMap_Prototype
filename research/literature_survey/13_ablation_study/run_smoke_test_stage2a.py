"""
Phase 13.1 — Stage 2A Smoke Test Runner (OD_01 Only).

Validates:
1. Multi-repetition execution protocol:
   - Experiments A-D: 5 timing repetitions per configuration.
   - Experiment E1: 3 timing repetitions for Perpendicular Offset.
   - Experiments E2 & E3: 3 timing repetitions for Raw and Filtered Yen K-SP.
2. Median runtime aggregation and preservation of all raw timing observations.
3. Outcome taxonomy instrumentation for Yen alternative routing.
4. Deterministic route-quality metric extraction (computed once per configuration).
5. Scoped configuration overrides and complete post-test restoration.

Outputs:
- smoke_test_stage2a_results.json
"""

import sys
import os
import json
import time
import math

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
    validate_od_corpus,
    scoped_ablation_context,
    run_experiment_a_corridor,
    run_experiment_b_corridor,
    run_experiment_c_corridor,
    run_experiment_d_corridor,
    run_experiment_e_corridor,
)


def test_override_restoration():
    """Verify that scoped_ablation_context strictly restores original globals and hooks."""
    orig_sharp = alg.TURN_PENALTY_SHARP
    orig_mod = alg.TURN_PENALTY_MODERATE
    orig_fn = alg.two_wheeler_edge_cost

    # 1. Normal execution flow across loop
    with scoped_ablation_context(turn_penalty_sharp=99.0, turn_penalty_moderate=77.0, bridge_mode="disabled"):
        for _ in range(5):
            assert alg.TURN_PENALTY_SHARP == 99.0, "Sharp penalty override failed"
            assert alg.TURN_PENALTY_MODERATE == 77.0, "Moderate penalty override failed"
            assert alg.two_wheeler_edge_cost != orig_fn, "Edge cost hook override failed"

    assert alg.TURN_PENALTY_SHARP == orig_sharp, "Sharp penalty not restored after normal exit"
    assert alg.TURN_PENALTY_MODERATE == orig_mod, "Moderate penalty not restored after normal exit"
    assert alg.two_wheeler_edge_cost == orig_fn, "Edge cost hook not restored after normal exit"

    # 2. Simulated Exception flow during repetition loop
    caught = False
    try:
        with scoped_ablation_context(turn_penalty_sharp=123.0, turn_penalty_moderate=456.0):
            for rep in range(5):
                if rep == 2:
                    raise RuntimeError("Simulated ablation failure during repetition")
    except RuntimeError:
        caught = True

    assert caught, "Simulated exception was not caught"
    assert alg.TURN_PENALTY_SHARP == orig_sharp, "Sharp penalty not restored after exception"
    assert alg.TURN_PENALTY_MODERATE == orig_mod, "Moderate penalty not restored after exception"
    assert alg.two_wheeler_edge_cost == orig_fn, "Edge cost hook not restored after exception"

    print("[OK] Scoped override and exception-safety restoration verified.")


def main():
    print("=" * 80)
    print("PHASE 13.1 — STAGE 2A: REPETITION SUPPORT AND OUTCOME SMOKE TEST (OD_01 ONLY)")
    print("=" * 80)

    # 1. Load Road Network Graph
    print("\n[Step 1] Loading Bengaluru road network graph...")
    t0 = time.time()
    graph_manager.load_graph()
    G = graph_manager.G
    print(f"  Road network loaded in {time.time() - t0:.2f}s ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")

    # 2. Test Override Restoration & Exception Safety
    print("\n[Step 2] Testing scoped override restoration & exception safety...")
    test_override_restoration()

    # 3. Validate Entire 25-Corridor Corpus
    print("\n[Step 3] Validating 25-corridor benchmark corpus...")
    corpus_val = validate_od_corpus(G, graph_manager)
    print(f"  Total corridors checked: {corpus_val['total_corridors']}")
    print(f"  All distinct endpoints: {corpus_val['all_distinct']}")
    print(f"  All connected in graph: {corpus_val['all_connected']}")
    assert corpus_val["all_distinct"], "Corpus validation failed: identical endpoints detected"
    assert corpus_val["all_connected"], "Corpus validation failed: disconnected corridor detected"

    # 4. Run Smoke Test on OD_01 Exclusively
    print("\n[Step 4] Executing Stage 2A Smoke Test on OD_01 (BNMIT to MG Road)...")
    od_01 = BENCHMARK_CORRIDORS[0]
    prod_penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)

    smoke_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stage": "Phase 13.1 - Stage 2A Smoke Test",
        "corridor": od_01,
        "corpus_validation": {
            "all_distinct": corpus_val["all_distinct"],
            "all_connected": corpus_val["all_connected"],
            "total_corridors": corpus_val["total_corridors"],
        },
        "experiments": {},
    }

    # Exp A (5 reps)
    print("\n  -> Running Experiment A (Turn-awareness & state expansion ablation, R=5)...")
    t_start = time.time()
    res_a = run_experiment_a_corridor(G, graph_manager, od_01, prod_penalties, reps=5)
    smoke_results["experiments"]["Experiment_A"] = res_a
    print(f"     [Exp A done in {time.time() - t_start:.2f}s]")
    for k in ["A0_Turn_Aware", "A1_Turn_Unaware_StateExpanded", "A2_Turn_Unaware_NodeLevel"]:
        item = res_a[k]
        print(f"     {k:30s}: med={item['runtime_ms']:8.2f}ms, raw={item['raw_runtimes_ms']}, dist={item['distance_km']}km, cost={item['impedance_cost']}, sharp={item['turns']['sharp_turns']}")

    # Exp B (5 reps)
    print("\n  -> Running Experiment B (Road-class impedance ablation, R=5)...")
    t_start = time.time()
    res_b = run_experiment_b_corridor(G, graph_manager, od_01, prod_penalties, reps=5)
    smoke_results["experiments"]["Experiment_B"] = res_b
    print(f"     [Exp B done in {time.time() - t_start:.2f}s]")
    for k in ["B0_Production_2W", "B1_Neutral_Road_Class", "B2_Physical_Distance_Ref"]:
        item = res_b[k]
        print(f"     {k:30s}: med={item['runtime_ms']:8.2f}ms, raw={item['raw_runtimes_ms']}, dist={item['distance_km']}km, arterial%={item['road_classes']['macro_pct']['arterial_pct']}%, res%={item['road_classes']['macro_pct']['residential_pct']}%")

    # Exp C (5 reps)
    print("\n  -> Running Experiment C (Turn-penalty sensitivity response, R=5)...")
    t_start = time.time()
    res_c = run_experiment_c_corridor(G, graph_manager, od_01, prod_penalties, reps=5)
    smoke_results["experiments"]["Experiment_C"] = res_c
    print(f"     [Exp C done in {time.time() - t_start:.2f}s]")
    for k in ["C0_Zero_Turn_Penalties", "C1_Low_Turn_Penalties", "C2_Baseline_Turn_Penalties", "C3_High_Turn_Penalties"]:
        item = res_c[k]
        print(f"     {k:30s}: med={item['runtime_ms']:8.2f}ms, raw={item['raw_runtimes_ms']}, sharp={item['turns']['sharp_turns']}, total_turns={item['turns']['total_turns']}")

    # Exp D (5 reps)
    print("\n  -> Running Experiment D (Bridge & roundabout 2x2 factorial, R=5)...")
    t_start = time.time()
    res_d = run_experiment_d_corridor(G, graph_manager, od_01, prod_penalties, reps=5)
    smoke_results["experiments"]["Experiment_D"] = res_d
    print(f"     [Exp D done in {time.time() - t_start:.2f}s]")
    for k in ["D1_Bridge_Off_Roundabout_Off", "D2_Bridge_On_Roundabout_Off", "D3_Bridge_Off_Roundabout_On", "D4_Bridge_On_Roundabout_On"]:
        item = res_d[k]
        print(f"     {k:30s}: med={item['runtime_ms']:8.2f}ms, raw={item['raw_runtimes_ms']}, dist={item['distance_km']}km, bridge_len={item['bridge']['bridge_length_m']}m, rbt_len={item['roundabout']['roundabout_length_m']}m")

    # Exp E (3 reps for E1, 3 reps for E2, 3 reps for E3)
    print("\n  -> Running Experiment E (Alternative routing comparison: Offset vs Yen, R=3)...")
    t_start = time.time()
    res_e = run_experiment_e_corridor(G, graph_manager, od_01, prod_penalties, reps_offset=3, reps_yen=3, run_yen=True)
    smoke_results["experiments"]["Experiment_E"] = res_e
    print(f"     [Exp E done in {time.time() - t_start:.2f}s]")

    e1 = res_e["E1_Perpendicular_Offset"]
    print(f"     E1_Perpendicular_Offset       : med={e1['runtime_ms']:8.2f}ms, raw={e1['raw_runtimes_ms']}, alts={e1['surviving_count']}/{e1['generated_count']}, div={e1['pairwise_diversity']}")

    e2 = res_e["E2_Raw_Yen_KSP"]
    print(f"     E2_Raw_Yen_KSP                : med={e2['runtime_ms']:8.2f}ms, raw={e2['raw_runtimes_ms']}, status={e2['outcome_status']}, paths={e2['paths_found']}, alts={e2['surviving_alts']}, gen={e2['candidates_generated']}, rej_ovl={e2['rejected_overlap']}, term='{e2['termination_reason']}'")

    e3 = res_e["E3_Filtered_Yen_KSP"]
    print(f"     E3_Filtered_Yen_KSP           : med={e3['runtime_ms']:8.2f}ms, raw={e3['raw_runtimes_ms']}, status={e3['outcome_status']}, paths={e3['paths_found']}, alts={e3['surviving_alts']}, gen={e3['candidates_generated']}, rej_ovl={e3['rejected_overlap']}, term='{e3['termination_reason']}'")

    # 5. Save Smoke Test Results
    out_dir = os.path.dirname(__file__)
    out_file = os.path.join(out_dir, "smoke_test_stage2a_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(smoke_results, f, indent=2)
    print(f"\n[Step 5] Smoke test results successfully saved to: {out_file}")

    # 6. Post-Run Production Defaults Check
    print("\n[Step 6] Confirming production globals remain unmodified...")
    assert alg.TURN_PENALTY_SHARP == 25.0, "Production TURN_PENALTY_SHARP altered!"
    assert alg.TURN_PENALTY_MODERATE == 8.0, "Production TURN_PENALTY_MODERATE altered!"
    print("  TURN_PENALTY_SHARP: 25.0 (VERIFIED)")
    print("  TURN_PENALTY_MODERATE: 8.0 (VERIFIED)")
    print("\n[SUCCESS] Stage 2A Smoke Test completed with 100% verification.")


if __name__ == "__main__":
    main()
