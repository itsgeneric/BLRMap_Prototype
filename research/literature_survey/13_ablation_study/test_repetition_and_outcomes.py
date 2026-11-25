"""
Unit and Validation Tests for Stage 2A Repetition Support and Outcome Classification.

Tests:
1. Correct repetition counts (R=5 for A-D, R=3 for E).
2. Median aggregation mathematical accuracy.
3. Preservation of individual timing observations in raw_runtimes_ms.
4. Scoped override configuration restoration after normal loops and exceptions.
5. Correct Yen outcome taxonomy classification across all 4 normal states + error state:
   - ZERO_GENERATED
   - ALL_REJECTED_OVERLAP
   - PARTIAL_ALTERNATIVES
   - SUCCESS_FULL
   - ERROR_EXCEPTION
6. Consistent output schema compliance.
"""

import sys
import os
import time
import statistics
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CURR_DIR = os.path.abspath(os.path.dirname(__file__))
if CURR_DIR not in sys.path:
    sys.path.insert(0, CURR_DIR)

import routing.algorithms as alg
from ablation_harness import (
    scoped_ablation_context,
    classify_yen_outcome,
    SELECTED_YEN_CORRIDORS,
)


class TestRepetitionAndOutcomes(unittest.TestCase):

    def test_median_aggregation_and_preservation(self):
        """Verify median calculation across odd and even timing repetitions and raw list preservation."""
        # Odd repetition count (R = 5)
        raw_5 = [12.4, 15.1, 11.8, 14.2, 12.0]
        med_5 = round(float(statistics.median(raw_5)), 2)
        self.assertEqual(med_5, 12.4)
        self.assertEqual(len(raw_5), 5)

        # Even repetition count (R = 4)
        raw_4 = [10.0, 20.0, 30.0, 40.0]
        med_4 = round(float(statistics.median(raw_4)), 2)
        self.assertEqual(med_4, 25.0)

        # Repetition count (R = 3)
        raw_3 = [254.38, 251.20, 258.90]
        med_3 = round(float(statistics.median(raw_3)), 2)
        self.assertEqual(med_3, 254.38)
        self.assertEqual(len(raw_3), 3)

    def test_scoped_override_restoration_under_repetitions_and_exceptions(self):
        """Verify that scoped_ablation_context restores original globals after repetition loops and exceptions."""
        orig_sharp = alg.TURN_PENALTY_SHARP
        orig_mod = alg.TURN_PENALTY_MODERATE
        orig_fn = alg.two_wheeler_edge_cost

        # 1. Normal repetition loop
        with scoped_ablation_context(turn_penalty_sharp=99.0, turn_penalty_moderate=77.0, bridge_mode="disabled"):
            for rep in range(5):
                self.assertEqual(alg.TURN_PENALTY_SHARP, 99.0)
                self.assertEqual(alg.TURN_PENALTY_MODERATE, 77.0)
                self.assertNotEqual(alg.two_wheeler_edge_cost, orig_fn)

        self.assertEqual(alg.TURN_PENALTY_SHARP, orig_sharp)
        self.assertEqual(alg.TURN_PENALTY_MODERATE, orig_mod)
        self.assertEqual(alg.two_wheeler_edge_cost, orig_fn)

        # 2. Exception raised during repetition loop
        with self.assertRaises(RuntimeError):
            with scoped_ablation_context(turn_penalty_sharp=111.0, turn_penalty_moderate=222.0):
                for rep in range(5):
                    if rep == 2:
                        raise RuntimeError("Simulated failure during rep 2")

        self.assertEqual(alg.TURN_PENALTY_SHARP, orig_sharp)
        self.assertEqual(alg.TURN_PENALTY_MODERATE, orig_mod)
        self.assertEqual(alg.two_wheeler_edge_cost, orig_fn)

    def test_outcome_classification_zero_generated(self):
        """Case 1: No candidate spur paths generated from any spur node."""
        diag = {
            "paths": [{"nodes": [1, 2, 3]}],
            "candidates_generated": 0,
            "rejected_duplicates": 0,
            "rejected_detour": 0,
            "rejected_overlap": 0,
        }
        res = classify_yen_outcome(diag, K=4, apply_overlap_filter=False)
        self.assertEqual(res["outcome_status"], "ZERO_GENERATED")
        self.assertEqual(res["paths_found"], 1)
        self.assertEqual(res["surviving_alts"], 0)
        self.assertEqual(res["candidates_generated"], 0)
        self.assertTrue(res["queue_exhausted"])
        self.assertFalse(res["k_achieved"])
        self.assertIn("No candidate spur paths", res["termination_reason"])

    def test_outcome_classification_all_rejected_overlap(self):
        """Case 2: Candidates generated but all rejected by overlap filter (E3 only)."""
        diag = {
            "paths": [{"nodes": [1, 2, 3]}],
            "candidates_generated": 25,
            "rejected_duplicates": 2,
            "rejected_detour": 3,
            "rejected_overlap": 20,
        }
        res = classify_yen_outcome(diag, K=4, apply_overlap_filter=True)
        self.assertEqual(res["outcome_status"], "ALL_REJECTED_OVERLAP")
        self.assertEqual(res["paths_found"], 1)
        self.assertEqual(res["surviving_alts"], 0)
        self.assertEqual(res["candidates_generated"], 25)
        self.assertEqual(res["rejected_overlap"], 20)
        self.assertTrue(res["queue_exhausted"])
        self.assertFalse(res["k_achieved"])
        self.assertIn("exceeded max_overlap", res["termination_reason"])

    def test_outcome_classification_partial_alternatives(self):
        """Case 3: Fewer than K-1 alternatives found after candidate queue exhaustion."""
        diag = {
            "paths": [{"nodes": [1, 2, 3]}, {"nodes": [1, 4, 3]}],  # 1 alt found
            "candidates_generated": 100,
            "rejected_duplicates": 10,
            "rejected_detour": 20,
            "rejected_overlap": 69,
        }
        res = classify_yen_outcome(diag, K=4, apply_overlap_filter=True)
        self.assertEqual(res["outcome_status"], "PARTIAL_ALTERNATIVES")
        self.assertEqual(res["paths_found"], 2)
        self.assertEqual(res["surviving_alts"], 1)
        self.assertEqual(res["candidates_generated"], 100)
        self.assertTrue(res["queue_exhausted"])
        self.assertFalse(res["k_achieved"])
        self.assertIn("Candidate queue B exhausted", res["termination_reason"])

    def test_outcome_classification_success_full(self):
        """Case 4: Exactly K-1 = 3 distinct alternatives found satisfying all bounds."""
        diag = {
            "paths": [
                {"nodes": [1, 2, 3]},
                {"nodes": [1, 4, 3]},
                {"nodes": [1, 5, 3]},
                {"nodes": [1, 6, 3]},
            ],
            "candidates_generated": 85,
            "rejected_duplicates": 5,
            "rejected_detour": 10,
            "rejected_overlap": 66,
        }
        res = classify_yen_outcome(diag, K=4, apply_overlap_filter=True)
        self.assertEqual(res["outcome_status"], "SUCCESS_FULL")
        self.assertEqual(res["paths_found"], 4)
        self.assertEqual(res["surviving_alts"], 3)
        self.assertEqual(res["candidates_generated"], 85)
        self.assertFalse(res["queue_exhausted"])
        self.assertTrue(res["k_achieved"])
        self.assertIn("Successfully generated all", res["termination_reason"])

    def test_outcome_classification_error_exception(self):
        """Case 5: Unhandled error or exception captured during search."""
        diag = {
            "exception": "TimeoutError: Search exceeded wall-clock limit of 600s",
            "paths": [],
            "candidates_generated": 12,
        }
        res = classify_yen_outcome(diag, K=4, apply_overlap_filter=True)
        self.assertEqual(res["outcome_status"], "ERROR_EXCEPTION")
        self.assertEqual(res["paths_found"], 0)
        self.assertEqual(res["surviving_alts"], 0)
        self.assertFalse(res["k_achieved"])
        self.assertIn("TimeoutError", res["termination_reason"])

    def test_selected_yen_corridors_set(self):
        """Verify the five representative Yen corridors match the approved selection."""
        expected = ["OD_23", "OD_02", "OD_04", "OD_03", "OD_01"]
        self.assertEqual(SELECTED_YEN_CORRIDORS, expected)

    def test_repetition_count_enforcement_and_schema_exp_a(self):
        """Verify reps parameter enforces exact search iterations and consistent schema in Exp A."""
        from unittest.mock import patch, MagicMock
        from ablation_harness import run_experiment_a_corridor

        mock_route_res = {"route": [1, 2], "expanded_states": 42}
        mock_metrics = {
            "distance_km": 1.5,
            "route_distance_m": 1500.0,
            "impedance_cost": 2250.0,
            "turns": {"sharp_turns": 1, "moderate_turns": 2, "total_turns": 3},
            "road_classes": {"macro_pct": {"arterial_pct": 50.0, "residential_pct": 50.0}}
        }

        with patch("ablation_harness.two_wheeler_astar", return_value=mock_route_res) as mock_2w, \
             patch("ablation_harness.node_level_astar", return_value=mock_route_res) as mock_nl, \
             patch("ablation_harness.extract_full_route_metrics", side_effect=[
                 dict(mock_metrics), dict(mock_metrics), dict(mock_metrics)
             ]) as mock_ext:

            res = run_experiment_a_corridor(
                G=MagicMock(),
                graph_mgr=MagicMock(),
                corridor={"start_node": 1, "end_node": 2},
                scoring_penalties={},
                reps=5
            )

            # Verification of call counts: 5 for A0, 5 for A1 -> 10 two_wheeler_astar calls
            self.assertEqual(mock_2w.call_count, 10)
            # 5 calls for A2 -> 5 node_level_astar calls
            self.assertEqual(mock_nl.call_count, 5)
            # Deterministic metric calculation called only once per config (3 total)
            self.assertEqual(mock_ext.call_count, 3)

            # Verify repetition enforcement and schema for each config
            for key in ["A0_Turn_Aware", "A1_Turn_Unaware_StateExpanded", "A2_Turn_Unaware_NodeLevel"]:
                self.assertIn(key, res)
                cfg = res[key]
                self.assertIn("raw_runtimes_ms", cfg)
                self.assertEqual(len(cfg["raw_runtimes_ms"]), 5)
                self.assertIn("runtime_ms", cfg)
                self.assertEqual(cfg["runtime_ms"], round(float(statistics.median(cfg["raw_runtimes_ms"])), 2))
                self.assertIn("route_distance_m", cfg)
                self.assertIn("impedance_cost", cfg)
                self.assertIn("turns", cfg)

    def test_repetition_count_enforcement_and_schema_exp_e(self):
        """Verify reps parameter enforces exact search iterations, outcome schema, and Yen skipping."""
        from unittest.mock import patch, MagicMock
        from ablation_harness import run_experiment_e_corridor

        mock_offset_diag = {
            "surviving_count": 2,
            "generated_count": 4,
            "candidates": [
                {"nodes": [1, 2], "detour_ratio": 1.05, "overlap_ratio": 0.50},
                {"nodes": [1, 3, 2], "detour_ratio": 1.10, "overlap_ratio": 0.35}
            ]
        }
        mock_yen_diag = {
            "paths": [
                {"nodes": [1, 2], "detour_ratio": 1.0, "overlap_ratio": 1.0},
                {"nodes": [1, 3, 2], "detour_ratio": 1.08, "overlap_ratio": 0.60},
                {"nodes": [1, 4, 2], "detour_ratio": 1.12, "overlap_ratio": 0.45},
                {"nodes": [1, 5, 2], "detour_ratio": 1.15, "overlap_ratio": 0.40},
            ],
            "candidates_generated": 30,
            "rejected_overlap": 5,
        }

        with patch("ablation_harness.build_split_route_candidates", return_value=mock_offset_diag) as mock_offset, \
             patch("ablation_harness.yen_ksp_two_wheeler", return_value=mock_yen_diag) as mock_yen, \
             patch("ablation_harness.calc_pairwise_diversity", return_value=0.45):

            # 1. Selected Yen Corridor (OD_01)
            corridor_sel = {
                "id": "OD_01", "start_node": 1, "end_node": 2,
                "from_lat": 12.9237, "from_lng": 77.5714,
                "to_lat": 12.9756, "to_lng": 77.6066
            }
            res_sel = run_experiment_e_corridor(
                G=MagicMock(),
                graph_mgr=MagicMock(),
                corridor=corridor_sel,
                production_penalties={},
                reps_offset=3,
                reps_yen=3,
                run_yen=None  # Should auto-enable because OD_01 in SELECTED_YEN_CORRIDORS
            )

            # E1 ran 3 times
            self.assertEqual(mock_offset.call_count, 3)
            self.assertEqual(len(res_sel["E1_Perpendicular_Offset"]["raw_runtimes_ms"]), 3)
            self.assertEqual(
                res_sel["E1_Perpendicular_Offset"]["runtime_ms"],
                round(float(statistics.median(res_sel["E1_Perpendicular_Offset"]["raw_runtimes_ms"])), 2)
            )

            # E2 and E3 ran 3 times each -> 6 yen calls
            self.assertEqual(mock_yen.call_count, 6)
            for ykey in ["E2_Raw_Yen_KSP", "E3_Filtered_Yen_KSP"]:
                yres = res_sel[ykey]
                self.assertEqual(len(yres["raw_runtimes_ms"]), 3)
                self.assertEqual(yres["runtime_ms"], round(float(statistics.median(yres["raw_runtimes_ms"])), 2))
                # Validate outcome taxonomy schema fields
                self.assertEqual(yres["outcome_status"], "SUCCESS_FULL")
                self.assertEqual(yres["paths_found"], 4)
                self.assertEqual(yres["surviving_alts"], 3)
                self.assertEqual(yres["candidates_generated"], 30)
                self.assertIn("rejected_overlap", yres)
                self.assertFalse(yres["queue_exhausted"])
                self.assertTrue(yres["k_achieved"])
                self.assertIn("termination_reason", yres)

            # 2. Unselected Yen Corridor (e.g., OD_05)
            mock_offset.reset_mock()
            mock_yen.reset_mock()

            corridor_unsel = {
                "id": "OD_05", "start_node": 1, "end_node": 2,
                "from_lat": 13.0358, "from_lng": 77.5970,
                "to_lat": 12.9767, "to_lng": 77.5713
            }
            res_unsel = run_experiment_e_corridor(
                G=MagicMock(),
                graph_mgr=MagicMock(),
                corridor=corridor_unsel,
                production_penalties={},
                reps_offset=3,
                reps_yen=3,
                run_yen=None  # Should auto-disable because OD_05 NOT in SELECTED_YEN_CORRIDORS
            )

            self.assertEqual(mock_offset.call_count, 3)
            self.assertEqual(mock_yen.call_count, 0)
            self.assertEqual(res_unsel["E2_Raw_Yen_KSP"]["outcome_status"], "SKIPPED_UNSELECTED")
            self.assertEqual(res_unsel["E3_Filtered_Yen_KSP"]["outcome_status"], "SKIPPED_UNSELECTED")
            self.assertIsNone(res_unsel["E2_Raw_Yen_KSP"]["runtime_ms"])
            self.assertEqual(res_unsel["E2_Raw_Yen_KSP"]["raw_runtimes_ms"], [])


if __name__ == "__main__":
    unittest.main()
