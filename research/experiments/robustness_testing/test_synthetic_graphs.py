"""
Synthetic Graph Test Suite for Phase 12.

Executes isolated, controlled experiments against 6 synthetic graph fixtures:
1. One-way road without reverse path.
2. Disconnected graph components.
3. Multiple parallel corridors with cost ranking.
4. Dead-end road / cul-de-sac handling.
5. Detour tolerance enforcement (detour > 1.20).
6. Shared edge overlap filtering (overlap > 70%).
"""

import sys
import os
import unittest
import networkx as nx

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.join(_REPO_ROOT, "backend"))

from routing.algorithms import (
    two_wheeler_astar,
    two_wheeler_edge_cost,
    path_cost,
    calc_route_distance,
    calc_route_overlap,
    calc_jaccard_similarity,
    is_valid_connected_route,
    build_two_wheeler_penalties,
)
from core.config import DETOUR_TOLERANCE
from research.experiments.robustness_testing.synthetic_fixtures import (
    MockGraphManager,
    create_oneway_no_reverse_graph,
    create_disconnected_graph,
    create_parallel_routes_graph,
    create_dead_end_graph,
    create_detour_exceeded_graph,
    create_overlap_exceeded_graph,
)


class TestSyntheticGraphs(unittest.TestCase):

    def setUp(self):
        self.mgr = MockGraphManager()
        self.penalties = build_two_wheeler_penalties(main_road_penalty=1.0, inner_road_multiplier=1.0)

    # --------------------------------------------------------------------------
    # Test 1: One-way Road with No Legal Reverse Path
    # --------------------------------------------------------------------------
    def test_01_oneway_no_reverse(self):
        """Forward path succeeds along one-way chain; reverse paths raise NetworkXNoPath."""
        G = create_oneway_no_reverse_graph()

        # Forward search: A -> D
        fwd_route = two_wheeler_astar(G, "A", "D", self.mgr, penalties=self.penalties)
        self.assertEqual(fwd_route, ["A", "B", "C", "D"])
        self.assertAlmostEqual(calc_route_distance(G, fwd_route), 300.0, places=2)
        self.assertTrue(is_valid_connected_route(G, fwd_route))

        # Reverse search: D -> A (must fail)
        with self.assertRaises(nx.NetworkXNoPath):
            two_wheeler_astar(G, "D", "A", self.mgr, penalties=self.penalties)

        # Intermediate reverse: C -> B (must fail)
        with self.assertRaises(nx.NetworkXNoPath):
            two_wheeler_astar(G, "C", "B", self.mgr, penalties=self.penalties)

        # Intermediate forward: B -> D (succeeds)
        mid_route = two_wheeler_astar(G, "B", "D", self.mgr, penalties=self.penalties)
        self.assertEqual(mid_route, ["B", "C", "D"])

    # --------------------------------------------------------------------------
    # Test 2: Disconnected Graph Components
    # --------------------------------------------------------------------------
    def test_02_disconnected_components(self):
        """Intra-component searches succeed; cross-component searches raise NetworkXNoPath."""
        G = create_disconnected_graph()

        # Intra-component C1: A -> C
        r_c1 = two_wheeler_astar(G, "A", "C", self.mgr, penalties=self.penalties)
        self.assertEqual(r_c1, ["A", "B", "C"])

        # Intra-component C2: X -> Z
        r_c2 = two_wheeler_astar(G, "X", "Z", self.mgr, penalties=self.penalties)
        self.assertEqual(r_c2, ["X", "Y", "Z"])

        # Cross-component: A -> Z (must fail)
        with self.assertRaises(nx.NetworkXNoPath):
            two_wheeler_astar(G, "A", "Z", self.mgr, penalties=self.penalties)

        # Cross-component reverse: Z -> A (must fail)
        with self.assertRaises(nx.NetworkXNoPath):
            two_wheeler_astar(G, "Z", "A", self.mgr, penalties=self.penalties)

    # --------------------------------------------------------------------------
    # Test 3: Multiple Parallel Corridors
    # --------------------------------------------------------------------------
    def test_03_parallel_routes_ranking(self):
        """Verifies deterministic cost ranking among 4 parallel corridors."""
        G = create_parallel_routes_graph()

        # Config A: Pure uniform road penalties (all road types = 1.0)
        # Arterial is 400m straight with 0 turns -> cost 400.0.
        # Residential is 420m + 2 turns -> cost 436.0.
        uniform_penalties = {
            "primary": 1.0, "residential": 1.0, "tertiary": 1.0, "service": 1.0
        }
        route_uniform = two_wheeler_astar(G, "S", "D", self.mgr, penalties=uniform_penalties)
        self.assertEqual(route_uniform, ["S", "M1", "M2", "D"])
        self.assertEqual(path_cost(G, route_uniform, self.mgr, penalties=uniform_penalties), 400.0)

        # Config B: Standard Two-Wheeler road penalties (Primary = 2.2, Residential = 1.0)
        # Arterial: 400m * 2.2 = 880.0 cost
        # Residential: 420m * 1.0 = 420.0 + 16.0 turn penalty = 436.0 cost
        route_2w = two_wheeler_astar(G, "S", "D", self.mgr, penalties=self.penalties)
        self.assertEqual(route_2w, ["S", "R1", "R2", "D"])
        self.assertEqual(path_cost(G, route_2w, self.mgr, penalties=self.penalties), 436.0)

    # --------------------------------------------------------------------------
    # Test 4: Dead-End Road / Cul-de-Sac Handling
    # --------------------------------------------------------------------------
    def test_04_dead_end_handling(self):
        """Verifies dead-end entry when destination inside, avoidance when destination beyond."""
        # 4a. Bidirectional dead-end
        G = create_dead_end_graph(trapped_oneway=False)

        # Destination inside dead-end (F)
        r_to_dead = two_wheeler_astar(G, "A", "F", self.mgr, penalties=self.penalties)
        self.assertEqual(r_to_dead, ["A", "B", "E", "F"])

        # Destination beyond dead-end (D) -> must NOT enter dead-end
        r_through = two_wheeler_astar(G, "A", "D", self.mgr, penalties=self.penalties)
        self.assertEqual(r_through, ["A", "B", "C", "D"])
        self.assertNotIn("E", r_through)
        self.assertNotIn("F", r_through)

        # Origin inside dead-end (F -> D) -> must navigate out
        r_from_dead = two_wheeler_astar(G, "F", "D", self.mgr, penalties=self.penalties)
        self.assertEqual(r_from_dead, ["F", "E", "B", "C", "D"])

        # 4b. Trapped one-way dead-end (B -> E -> F oneway)
        G_trap = create_dead_end_graph(trapped_oneway=True)
        # A -> F succeeds
        r_trap_in = two_wheeler_astar(G_trap, "A", "F", self.mgr, penalties=self.penalties)
        self.assertEqual(r_trap_in, ["A", "B", "E", "F"])

        # F -> D fails (no egress edge exists)
        with self.assertRaises(nx.NetworkXNoPath):
            two_wheeler_astar(G_trap, "F", "D", self.mgr, penalties=self.penalties)

    # --------------------------------------------------------------------------
    # Test 5: Detour Tolerance Enforcement
    # --------------------------------------------------------------------------
    def test_05_detour_exceeded_filtering(self):
        """Verifies that alternative with detour ratio > 1.20 is rejected."""
        G = create_detour_exceeded_graph()

        r_primary = ["S", "P1", "D"]
        r_alt = ["S", "A1", "A2", "D"]

        d_primary = calc_route_distance(G, r_primary)
        d_alt = calc_route_distance(G, r_alt)
        detour_ratio = d_alt / d_primary

        self.assertAlmostEqual(d_primary, 100.0, places=2)
        self.assertAlmostEqual(d_alt, 135.0, places=2)
        self.assertAlmostEqual(detour_ratio, 1.35, places=2)

        # Under default DETOUR_TOLERANCE (1.20), detour ratio 1.35 exceeds threshold
        self.assertGreater(detour_ratio, DETOUR_TOLERANCE)

    # --------------------------------------------------------------------------
    # Test 6: Shared Edge Overlap Filtering
    # --------------------------------------------------------------------------
    def test_06_overlap_exceeded_filtering(self):
        """Verifies that alternative with edge overlap > 70% is rejected."""
        G = create_overlap_exceeded_graph()

        r_primary = ["S", "N1", "N2", "N3", "N4", "D"]
        r_alt = ["S", "N1", "N2", "ALT", "N4", "D"]

        d_primary = calc_route_distance(G, r_primary)
        d_alt = calc_route_distance(G, r_alt)
        overlap = calc_route_overlap(G, r_primary, r_alt)

        self.assertAlmostEqual(d_primary, 1000.0, places=2)
        self.assertAlmostEqual(d_alt, 820.0, places=2)
        # Shared edges: (S,N1)=200, (N1,N2)=200, (N4,D)=200 -> 600m
        # Overlap = 600 / 820 = 73.17%
        self.assertAlmostEqual(overlap, 600.0 / 820.0, places=4)
        self.assertGreater(overlap, 0.70)


if __name__ == "__main__":
    unittest.main()
