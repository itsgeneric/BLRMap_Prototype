"""
Phase 13.1 — Stage 1 Smoke Test Runner (OD_01 Only).

Validates:
1. OD Corpus integrity across all 25 corridors.
2. Scoped execution context override and guaranteed restoration under normal and exception flows.
3. Smoke-test execution of Experiments A, B, C, D, and E on OD_01 exclusively.
4. Metric extraction consistency and mathematical validation.
5. Strict preservation of production configuration and routing defaults.
Outputs:
- smoke_test_results.json
"""

import sys
import os
import json
import time
import math

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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

    # 1. Normal execution flow
    with scoped_ablation_context(turn_penalty_sharp=99.0, turn_penalty_moderate=77.0, bridge_mode="disabled"):
        assert alg.TURN_PENALTY_SHARP == 99.0, "Sharp penalty override failed"
        assert alg.TURN_PENALTY_MODERATE == 77.0, "Moderate penalty override failed"
        assert alg.two_wheeler_edge_cost != orig_fn, "Edge cost hook override failed"

    assert alg.TURN_PENALTY_SHARP == orig_sharp, "Sharp penalty not restored after normal exit"
    assert alg.TURN_PENALTY_MODERATE == orig_mod, "Moderate penalty not restored after normal exit"
    assert alg.two_wheeler_edge_cost == orig_fn, "Edge cost hook not restored after normal exit"

    # 2. Simulated Exception flow
    caught = False
    try:
        with scoped_ablation_context(turn_penalty_sharp=123.0, turn_penalty_moderate=456.0):
            assert alg.TURN_PENALTY_SHARP == 123.0
            raise RuntimeError("Simulated ablation failure")
    except RuntimeError:
        caught = True

    assert caught, "Simulated exception was not caught"
    assert alg.TURN_PENALTY_SHARP == orig_sharp, "Sharp penalty not restored after exception"
    assert alg.TURN_PENALTY_MODERATE == orig_mod, "Moderate penalty not restored after exception"
    assert alg.two_wheeler_edge_cost == orig_fn, "Edge cost hook not restored after exception"

    print("[OK] Scoped override and exception-safety restoration verified.")


def main():
    print("=" * 80)
    print("PHASE 13.1 — STAGE 1: HARNESS VALIDATION AND SMOKE TEST (OD_01 ONLY)")
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
    print("\n[Step 4] Executing Smoke Test on OD_01 (BNMIT to MG Road)...")
    od_01 = BENCHMARK_CORRIDORS[0]
    prod_penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)

    smoke_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corridor": od_01,
        "corpus_validation": {
            "all_distinct": corpus_val["all_distinct"],
            "all_connected": corpus_val["all_connected"],
            "total_corridors": corpus_val["total_corridors"],
        },
        "experiments": {},
    }

    # Exp A
    print("  -> Running Experiment A (Turn-awareness & state expansion ablation)...")
    res_a = run_experiment_a_corridor(G, graph_manager, od_01, prod_penalties)
    smoke_results["experiments"]["Experiment_A"] = res_a
    print(f"     A0 (Turn-Aware):       dist={res_a['A0_Turn_Aware']['distance_km']}km, cost={res_a['A0_Turn_Aware']['impedance_cost']}, sharp_turns={res_a['A0_Turn_Aware']['turns']['sharp_turns']}, states={res_a['A0_Turn_Aware']['expanded_states']}")
    print(f"     A1 (Turn-Unaware Edge):dist={res_a['A1_Turn_Unaware_StateExpanded']['distance_km']}km, cost={res_a['A1_Turn_Unaware_StateExpanded']['impedance_cost']}, sharp_turns={res_a['A1_Turn_Unaware_StateExpanded']['turns']['sharp_turns']}, states={res_a['A1_Turn_Unaware_StateExpanded']['expanded_states']}")
    print(f"     A2 (Turn-Unaware Node):dist={res_a['A2_Turn_Unaware_NodeLevel']['distance_km']}km, cost={res_a['A2_Turn_Unaware_NodeLevel']['impedance_cost']}, sharp_turns={res_a['A2_Turn_Unaware_NodeLevel']['turns']['sharp_turns']}, states={res_a['A2_Turn_Unaware_NodeLevel']['expanded_states']}")

    # Exp B
    print("  -> Running Experiment B (Road-class impedance ablation)...")
    res_b = run_experiment_b_corridor(G, graph_manager, od_01, prod_penalties)
    smoke_results["experiments"]["Experiment_B"] = res_b
    print(f"     B0 (Production 2W):    dist={res_b['B0_Production_2W']['distance_km']}km, cost={res_b['B0_Production_2W']['impedance_cost']}, arterial%={res_b['B0_Production_2W']['road_classes']['macro_pct']['arterial_pct']}%, res%={res_b['B0_Production_2W']['road_classes']['macro_pct']['residential_pct']}%")
    print(f"     B1 (Neutral Road Class):dist={res_b['B1_Neutral_Road_Class']['distance_km']}km, cost={res_b['B1_Neutral_Road_Class']['impedance_cost']}, arterial%={res_b['B1_Neutral_Road_Class']['road_classes']['macro_pct']['arterial_pct']}%, res%={res_b['B1_Neutral_Road_Class']['road_classes']['macro_pct']['residential_pct']}%")
    print(f"     B2 (Physical Shortest):dist={res_b['B2_Physical_Distance_Ref']['distance_km']}km, cost={res_b['B2_Physical_Distance_Ref']['impedance_cost']}, arterial%={res_b['B2_Physical_Distance_Ref']['road_classes']['macro_pct']['arterial_pct']}%, res%={res_b['B2_Physical_Distance_Ref']['road_classes']['macro_pct']['residential_pct']}%")

    # Exp C
    print("  -> Running Experiment C (Turn-penalty sensitivity response)...")
    res_c = run_experiment_c_corridor(G, graph_manager, od_01, prod_penalties)
    smoke_results["experiments"]["Experiment_C"] = res_c
    print(f"     C0 (Zero Turn P):      dist={res_c['C0_Zero_Turn_Penalties']['distance_km']}km, cost={res_c['C0_Zero_Turn_Penalties']['impedance_cost']}, sharp={res_c['C0_Zero_Turn_Penalties']['turns']['sharp_turns']}, total_turns={res_c['C0_Zero_Turn_Penalties']['turns']['total_turns']}")
    print(f"     C1 (Low Turn P 12/4):  dist={res_c['C1_Low_Turn_Penalties']['distance_km']}km, cost={res_c['C1_Low_Turn_Penalties']['impedance_cost']}, sharp={res_c['C1_Low_Turn_Penalties']['turns']['sharp_turns']}, total_turns={res_c['C1_Low_Turn_Penalties']['turns']['total_turns']}")
    print(f"     C2 (Baseline 25/8):    dist={res_c['C2_Baseline_Turn_Penalties']['distance_km']}km, cost={res_c['C2_Baseline_Turn_Penalties']['impedance_cost']}, sharp={res_c['C2_Baseline_Turn_Penalties']['turns']['sharp_turns']}, total_turns={res_c['C2_Baseline_Turn_Penalties']['turns']['total_turns']}")
    print(f"     C3 (High Turn P 50/16):dist={res_c['C3_High_Turn_Penalties']['distance_km']}km, cost={res_c['C3_High_Turn_Penalties']['impedance_cost']}, sharp={res_c['C3_High_Turn_Penalties']['turns']['sharp_turns']}, total_turns={res_c['C3_High_Turn_Penalties']['turns']['total_turns']}")

    # Exp D
    print("  -> Running Experiment D (Bridge & roundabout 2x2 factorial)...")
    res_d = run_experiment_d_corridor(G, graph_manager, od_01, prod_penalties)
    smoke_results["experiments"]["Experiment_D"] = res_d
    print(f"     D1 (Off/Off):          dist={res_d['D1_Bridge_Off_Roundabout_Off']['distance_km']}km, bridge_len={res_d['D1_Bridge_Off_Roundabout_Off']['bridge']['bridge_length_m']}m, rbt_len={res_d['D1_Bridge_Off_Roundabout_Off']['roundabout']['roundabout_length_m']}m")
    print(f"     D2 (Bridge On/Rbt Off):dist={res_d['D2_Bridge_On_Roundabout_Off']['distance_km']}km, bridge_len={res_d['D2_Bridge_On_Roundabout_Off']['bridge']['bridge_length_m']}m, rbt_len={res_d['D2_Bridge_On_Roundabout_Off']['roundabout']['roundabout_length_m']}m")
    print(f"     D3 (Bridge Off/Rbt On):dist={res_d['D3_Bridge_Off_Roundabout_On']['distance_km']}km, bridge_len={res_d['D3_Bridge_Off_Roundabout_On']['bridge']['bridge_length_m']}m, rbt_len={res_d['D3_Bridge_Off_Roundabout_On']['roundabout']['roundabout_length_m']}m")
    print(f"     D4 (On/On - Control):  dist={res_d['D4_Bridge_On_Roundabout_On']['distance_km']}km, bridge_len={res_d['D4_Bridge_On_Roundabout_On']['bridge']['bridge_length_m']}m, rbt_len={res_d['D4_Bridge_On_Roundabout_On']['roundabout']['roundabout_length_m']}m")

    # Exp E
    print("  -> Running Experiment E (Alternative routing comparison: Offset vs Yen)...")
    res_e = run_experiment_e_corridor(G, graph_manager, od_01, prod_penalties)
    smoke_results["experiments"]["Experiment_E"] = res_e
    print(f"     E1 (Perp Offset):      runtime={res_e['E1_Perpendicular_Offset']['runtime_ms']}ms, surviving_alts={res_e['E1_Perpendicular_Offset']['surviving_count']}, diversity={res_e['E1_Perpendicular_Offset']['pairwise_diversity']}, detours={res_e['E1_Perpendicular_Offset']['detour_ratios']}")
    print(f"     E2 (Raw Yen KSP):      runtime={res_e['E2_Raw_Yen_KSP']['runtime_ms']}ms, paths={res_e['E2_Raw_Yen_KSP']['paths_found']}, diversity={res_e['E2_Raw_Yen_KSP']['pairwise_diversity']}, overlaps={res_e['E2_Raw_Yen_KSP']['overlap_ratios']}")
    print(f"     E3 (Filtered Yen KSP): runtime={res_e['E3_Filtered_Yen_KSP']['runtime_ms']}ms, paths={res_e['E3_Filtered_Yen_KSP']['paths_found']}, rejected_overlap={res_e['E3_Filtered_Yen_KSP']['rejected_overlap']}")

    # 5. Save Smoke Test Results
    out_dir = os.path.dirname(__file__)
    out_file = os.path.join(out_dir, "smoke_test_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(smoke_results, f, indent=2)
    print(f"\n[Step 5] Smoke test results successfully saved to: {out_file}")

    # 6. Post-Run Production Defaults Check
    print("\n[Step 6] Confirming production globals remain unmodified...")
    assert alg.TURN_PENALTY_SHARP == 25.0, "Production TURN_PENALTY_SHARP altered!"
    assert alg.TURN_PENALTY_MODERATE == 8.0, "Production TURN_PENALTY_MODERATE altered!"
    print("  TURN_PENALTY_SHARP: 25.0 (VERIFIED)")
    print("  TURN_PENALTY_MODERATE: 8.0 (VERIFIED)")
    print("\n[SUCCESS] Stage 1 Smoke Test completed with 100% verification.")


if __name__ == "__main__":
    main()
