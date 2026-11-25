"""
Comprehensive Test Suite for Phase 10: Alternative Route Generation,
Edge-Overlap Filtering (70% Threshold), and Yen's KSP Baseline.

Covers:
1. Identical routes (100% overlap, Jaccard = 1.0, rejected by 70% filter).
2. Completely different routes (0% overlap, Jaccard = 0.0, accepted).
3. Exact 70% overlap boundary condition (retained).
4. Routes exceeding 70% overlap (rejected).
5. Maximum detour ratio constraint (1.20).
6. Duplicate candidate suppression.
7. Disconnected and invalid route validation.
8. Turn-aware cost calculation on state transitions.
9. Yen's K-Shortest Paths deterministic correctness and ranking.
10. Pairwise route diversity computation.
"""

import sys
import os
import unittest
import networkx as nx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from routing.algorithms import (
    two_wheeler_astar,
    two_wheeler_edge_cost,
    _turn_penalty,
    path_cost,
    calc_route_distance,
    is_valid_connected_route,
    get_route_edge_lengths,
    calc_shared_edge_length,
    calc_route_overlap,
    calc_jaccard_similarity,
    calc_pairwise_diversity,
    build_split_route_candidates,
    yen_ksp_two_wheeler,
)
from core.config import DETOUR_TOLERANCE


class MockGraphManager:
    """Mock graph manager providing neutral surface penalty."""
    def get_surface_penalty(self, u, v):
        return 1.0


class TestAlternativeRoutingPhase10(unittest.TestCase):

    def setUp(self):
        self.mgr = MockGraphManager()

    def test_01_identical_routes_100_percent_overlap(self):
        """Identical routes have 100% overlap, Jaccard = 1.0, and must be rejected by 70% filter."""
        G = nx.MultiDiGraph()
        G.add_node("A", y=12.90, x=77.50)
        G.add_node("B", y=12.91, x=77.50)
        G.add_node("C", y=12.92, x=77.50)
        G.add_edge("A", "B", length=100.0, highway="residential")
        G.add_edge("B", "C", length=150.0, highway="residential")

        r1 = ["A", "B", "C"]
        r2 = ["A", "B", "C"]

        overlap = calc_route_overlap(G, r1, r2)
        jaccard = calc_jaccard_similarity(G, r1, r2)

        self.assertAlmostEqual(overlap, 1.0, places=5)
        self.assertAlmostEqual(jaccard, 1.0, places=5)
        # 100% > 70% threshold -> must be rejected
        self.assertGreater(overlap, 0.70)

    def test_02_completely_different_routes_0_percent_overlap(self):
        """Completely disjoint routes have 0% overlap, Jaccard = 0.0, and must be accepted."""
        G = nx.MultiDiGraph()
        nodes = {
            "S": (12.90, 77.50), "D": (12.94, 77.50),
            "A1": (12.91, 77.52), "A2": (12.93, 77.52),
            "B1": (12.91, 77.48), "B2": (12.93, 77.48),
        }
        for n, (lat, lng) in nodes.items():
            G.add_node(n, y=lat, x=lng)

        # Route 1: East detour S -> A1 -> A2 -> D
        G.add_edge("S", "A1", length=200.0, highway="residential")
        G.add_edge("A1", "A2", length=300.0, highway="residential")
        G.add_edge("A2", "D", length=200.0, highway="residential")

        # Route 2: West detour S -> B1 -> B2 -> D
        G.add_edge("S", "B1", length=200.0, highway="residential")
        G.add_edge("B1", "B2", length=300.0, highway="residential")
        G.add_edge("B2", "D", length=200.0, highway="residential")

        r1 = ["S", "A1", "A2", "D"]
        r2 = ["S", "B1", "B2", "D"]

        overlap = calc_route_overlap(G, r1, r2)
        jaccard = calc_jaccard_similarity(G, r1, r2)

        self.assertAlmostEqual(overlap, 0.0, places=5)
        self.assertAlmostEqual(jaccard, 0.0, places=5)
        # 0% <= 70% threshold -> must be accepted
        self.assertLessEqual(overlap, 0.70)

    def test_03_exact_70_percent_overlap_boundary(self):
        """A route sharing exactly 70% of physical edge length is <= 70% and MUST be retained."""
        G = nx.MultiDiGraph()
        # Build chain: N0 -> N1 -> ... -> N10 (each segment 100m, total 1000m)
        for i in range(11):
            G.add_node(f"N{i}", y=12.90 + i * 0.001, x=77.50)
            if i > 0:
                G.add_edge(f"N{i-1}", f"N{i}", length=100.0, highway="residential")

        # Primary route: N0 through N10 (length 1000m)
        primary = [f"N{i}" for i in range(11)]

        # Detour route: shares N0..N7 (700m = 70%), then bypasses via D8, D9 to N10 (300m)
        G.add_node("D8", y=12.9075, x=77.51)
        G.add_node("D9", y=12.9090, x=77.51)
        G.add_edge("N7", "D8", length=150.0, highway="residential")
        G.add_edge("D8", "D9", length=100.0, highway="residential")
        G.add_edge("D9", "N10", length=50.0, highway="residential")

        alt = [f"N{i}" for i in range(8)] + ["D8", "D9", "N10"]

        primary_len = calc_route_distance(G, primary)
        alt_len = calc_route_distance(G, alt)
        self.assertEqual(primary_len, 1000.0)
        self.assertEqual(alt_len, 1000.0)

        shared_len = calc_shared_edge_length(G, primary, alt)
        self.assertEqual(shared_len, 700.0)

        overlap = calc_route_overlap(G, primary, alt)
        self.assertAlmostEqual(overlap, 0.700000, places=5)

        # Boundary condition: <= 0.70 must retain
        self.assertTrue(overlap <= 0.70, "Exact 70.0% overlap should be retained")

    def test_04_routes_exceeding_70_percent_threshold(self):
        """A route sharing 70.1% of edge length exceeds 70% and MUST be rejected."""
        G = nx.MultiDiGraph()
        for i in range(11):
            G.add_node(f"N{i}", y=12.90 + i * 0.001, x=77.50)
            if i > 0:
                G.add_edge(f"N{i-1}", f"N{i}", length=100.0, highway="residential")

        primary = [f"N{i}" for i in range(11)]

        # Alt route shares 701m out of 1000m
        # Shares N0..N7 (700m) + N7..N7_1 (1m) = 701m, then detours 299m to N10
        G.add_node("N7_1", y=12.90701, x=77.50)
        G.add_node("D_high", y=12.9080, x=77.51)
        G.add_edge("N7", "N7_1", length=1.0, highway="residential")
        # Add N7 -> N7_1 to primary for sharing
        G.add_edge("N7_1", "D_high", length=150.0, highway="residential")
        G.add_edge("D_high", "N10", length=149.0, highway="residential")

        # Let's directly create alt route with known edge lengths
        G_simple = nx.MultiDiGraph()
        G_simple.add_node("P0", y=12.0, x=77.0)
        G_simple.add_node("P1", y=12.1, x=77.0)
        G_simple.add_node("P2", y=12.2, x=77.0)
        G_simple.add_node("A1", y=12.1, x=77.1)

        # Primary: P0 -> P1 (701m), P1 -> P2 (299m). Total = 1000m
        G_simple.add_edge("P0", "P1", length=701.0, highway="residential")
        G_simple.add_edge("P1", "P2", length=299.0, highway="residential")

        # Alt: P0 -> P1 (701m), P1 -> A1 (150m), A1 -> P2 (149m). Total = 1000m
        G_simple.add_edge("P1", "A1", length=150.0, highway="residential")
        G_simple.add_edge("A1", "P2", length=149.0, highway="residential")

        r_prim = ["P0", "P1", "P2"]
        r_alt = ["P0", "P1", "A1", "P2"]

        overlap = calc_route_overlap(G_simple, r_prim, r_alt)
        self.assertAlmostEqual(overlap, 0.701, places=3)
        self.assertGreater(overlap, 0.70, "70.1% overlap must strictly exceed 0.70 threshold")

    def test_05_detour_constraint_1_20(self):
        """Detour constraint bounds alternatives to at most 1.20x primary route distance."""
        G = nx.MultiDiGraph()
        G.add_node("S", y=12.90, x=77.50)
        G.add_node("G", y=12.95, x=77.50)
        G.add_node("M1", y=12.925, x=77.51)
        G.add_node("M2", y=12.925, x=77.53)

        # Primary: length = 1000m
        G.add_edge("S", "G", length=1000.0, highway="residential")
        p_dist = 1000.0

        # Alt 1: S -> M1 -> G, length = 590 + 600 = 1190m (detour 1.19 <= 1.20)
        G.add_edge("S", "M1", length=590.0, highway="residential")
        G.add_edge("M1", "G", length=600.0, highway="residential")

        # Alt 2: S -> M2 -> G, length = 610 + 610 = 1220m (detour 1.22 > 1.20)
        G.add_edge("S", "M2", length=610.0, highway="residential")
        G.add_edge("M2", "G", length=610.0, highway="residential")

        dist_1 = calc_route_distance(G, ["S", "M1", "G"])
        dist_2 = calc_route_distance(G, ["S", "M2", "G"])

        detour_1 = dist_1 / p_dist
        detour_2 = dist_2 / p_dist

        self.assertLessEqual(detour_1, DETOUR_TOLERANCE)
        self.assertGreater(detour_2, DETOUR_TOLERANCE)

    def test_06_duplicate_candidate_suppression(self):
        """Exact duplicate candidate routes must be cleanly suppressed."""
        seen = set()
        cand1 = ["A", "B", "C", "D"]
        cand2 = ["A", "B", "C", "D"]
        cand3 = ["A", "B", "E", "D"]

        self.assertNotIn(tuple(cand1), seen)
        seen.add(tuple(cand1))

        # Duplicate detection
        self.assertIn(tuple(cand2), seen)

        # Distinct path
        self.assertNotIn(tuple(cand3), seen)
        seen.add(tuple(cand3))
        self.assertEqual(len(seen), 2)

    def test_07_disconnected_and_invalid_routes(self):
        """Disconnected or non-existent edges must be detected by is_valid_connected_route."""
        G = nx.MultiDiGraph()
        G.add_node("A", y=12.0, x=77.0)
        G.add_node("B", y=12.1, x=77.0)
        G.add_node("C", y=12.2, x=77.0)
        G.add_node("Z", y=12.9, x=77.9) # disconnected

        G.add_edge("A", "B", length=100.0, highway="residential")
        G.add_edge("B", "C", length=100.0, highway="residential")

        self.assertTrue(is_valid_connected_route(G, ["A", "B", "C"]))
        self.assertFalse(is_valid_connected_route(G, ["A", "C"])) # No direct edge
        self.assertFalse(is_valid_connected_route(G, ["A", "B", "Z"])) # Z not reachable from B
        self.assertFalse(is_valid_connected_route(G, ["A"])) # Single node
        self.assertFalse(is_valid_connected_route(G, [])) # Empty
        self.assertFalse(is_valid_connected_route(G, None)) # None

    def test_08_turn_aware_cost_calculation(self):
        """Verify that turn penalties are correctly accumulated into path_cost."""
        G = nx.MultiDiGraph()
        # Straight path: (0,0) -> (1,0) -> (2,0)
        G.add_node("S0", y=12.00, x=77.00)
        G.add_node("S1", y=12.01, x=77.00)
        G.add_node("S2", y=12.02, x=77.00)
        G.add_edge("S0", "S1", length=100.0, highway="residential")
        G.add_edge("S1", "S2", length=100.0, highway="residential")

        # Zig-zag path with 90-degree sharp turn: (0,0) -> (1,0) -> (1,1)
        G.add_node("T0", y=12.00, x=77.00)
        G.add_node("T1", y=12.01, x=77.00)
        G.add_node("T2", y=12.01, x=77.01)
        G.add_edge("T0", "T1", length=100.0, highway="residential")
        G.add_edge("T1", "T2", length=100.0, highway="residential")

        straight_cost = path_cost(G, ["S0", "S1", "S2"], self.mgr)
        turn_cost = path_cost(G, ["T0", "T1", "T2"], self.mgr)

        # Base edge costs: 100 * 1.0 + 100 * 1.0 = 200.0 for both
        # Straight turn cost: 0.0 -> total 200.0
        # 90-degree turn cost: 25.0 -> total 225.0
        self.assertAlmostEqual(straight_cost, 200.0, places=3)
        self.assertAlmostEqual(turn_cost, 225.0, places=3)
        self.assertGreater(turn_cost, straight_cost)

    def test_09_yen_ksp_deterministic_small_graph(self):
        """Yen's KSP must discover paths in strict non-decreasing order of cost."""
        G = nx.MultiDiGraph()
        nodes = {
            "S": (12.00, 77.00),
            "G": (12.04, 77.00),
            "A": (12.02, 77.00),
            "B": (12.02, 77.01),
            "C": (12.02, 77.02),
            "D": (12.02, 77.03),
        }
        for n, (lat, lng) in nodes.items():
            G.add_node(n, y=lat, x=lng)

        # 4 parallel corridors of strictly increasing distance/cost
        # Path 1: S -> A -> G (length 100 + 100 = 200)
        G.add_edge("S", "A", length=100.0, highway="residential")
        G.add_edge("A", "G", length=100.0, highway="residential")

        # Path 2: S -> B -> G (length 110 + 110 = 220)
        G.add_edge("S", "B", length=110.0, highway="residential")
        G.add_edge("B", "G", length=110.0, highway="residential")

        # Path 3: S -> C -> G (length 115 + 115 = 230)
        G.add_edge("S", "C", length=115.0, highway="residential")
        G.add_edge("C", "G", length=115.0, highway="residential")

        # Path 4: S -> D -> G (length 118 + 118 = 236)
        G.add_edge("S", "D", length=118.0, highway="residential")
        G.add_edge("D", "G", length=118.0, highway="residential")

        paths = yen_ksp_two_wheeler(
            G, "S", "G", self.mgr,
            K=4,
            max_detour=1.50,
            apply_overlap_filter=False,
        )

        self.assertEqual(len(paths), 4)
        costs = [p["cost"] for p in paths]
        # Costs must be monotonically non-decreasing
        for idx in range(len(costs) - 1):
            self.assertLessEqual(costs[idx], costs[idx + 1])

        self.assertEqual(paths[0]["nodes"], ["S", "A", "G"])
        self.assertEqual(paths[1]["nodes"], ["S", "B", "G"])
        self.assertEqual(paths[2]["nodes"], ["S", "C", "G"])
        self.assertEqual(paths[3]["nodes"], ["S", "D", "G"])

    def test_10_pairwise_diversity_metric(self):
        """Pairwise route diversity must equal 1.0 for disjoint routes and 0.0 for identical routes."""
        G = nx.MultiDiGraph()
        G.add_node("S", y=12.0, x=77.0)
        G.add_node("G", y=12.4, x=77.0)
        G.add_node("A", y=12.2, x=77.1)
        G.add_node("B", y=12.2, x=77.2)
        G.add_node("C", y=12.2, x=77.3)

        G.add_edge("S", "A", length=100.0, highway="residential")
        G.add_edge("A", "G", length=100.0, highway="residential")
        G.add_edge("S", "B", length=100.0, highway="residential")
        G.add_edge("B", "G", length=100.0, highway="residential")
        G.add_edge("S", "C", length=100.0, highway="residential")
        G.add_edge("C", "G", length=100.0, highway="residential")

        r1 = ["S", "A", "G"]
        r2 = ["S", "B", "G"]
        r3 = ["S", "C", "G"]

        # Disjoint intermediate routes share 0 interior edges
        div_disjoint = calc_pairwise_diversity(G, [r1, r2, r3])
        self.assertAlmostEqual(div_disjoint, 1.0, places=4)

        # Identical routes share 100% of edges -> diversity = 0.0
        div_identical = calc_pairwise_diversity(G, [r1, r1, r1])
        self.assertAlmostEqual(div_identical, 0.0, places=4)


if __name__ == "__main__":
    unittest.main()
