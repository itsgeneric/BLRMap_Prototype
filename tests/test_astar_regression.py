"""
Regression Test Suite for A* Heuristic Correction.

Validates that:
1. Legacy / default calling signatures in router.py, api_server.py, and build_split_route_candidates
   remain 100% backwards-compatible.
2. Route reconstruction, node deduplication, coordinate conversion, maneuver generation, and split-route
   candidate generation execute without regression.
3. Explicit parameter selection (admissible, aggressive, dijkstra) and metric returns function as specified.
"""

import sys
import os
import unittest
import osmnx as ox

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from routing.graph_manager import graph_manager
from routing.algorithms import (
    two_wheeler_astar,
    build_two_wheeler_penalties,
    calc_route_distance,
    generate_route_maneuvers,
    build_split_route_candidates,
)


class TestAStarRegression(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the graph once for class tests
        graph_manager.load_graph()
        cls.G = graph_manager.G

        # Standard test pair: BNMIT to MG Road
        cls.start_node = ox.nearest_nodes(cls.G, 77.5714, 12.9237)
        cls.end_node = ox.nearest_nodes(cls.G, 77.6066, 12.9756)
        cls.penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)

    def test_01_default_signature_backward_compatibility(self):
        """Calling two_wheeler_astar with legacy signature returns a list of nodes."""
        route = two_wheeler_astar(
            self.G,
            self.start_node,
            self.end_node,
            graph_manager,
            penalties=self.penalties,
        )

        self.assertIsInstance(route, list, "Expected route to be a list of node IDs")
        self.assertGreater(len(route), 10, "Expected a realistic multi-node route")
        self.assertEqual(route[0], self.start_node, "First node must be start_node")
        self.assertEqual(route[-1], self.end_node, "Last node must be end_node")

    def test_02_distance_and_coordinate_pipeline(self):
        """Calc distance and coordinate conversion must succeed on route output."""
        route = two_wheeler_astar(
            self.G,
            self.start_node,
            self.end_node,
            graph_manager,
            penalties=self.penalties,
        )
        dist_m = calc_route_distance(self.G, route)
        self.assertGreater(dist_m, 5000.0, "Route distance should exceed 5km")
        self.assertLess(dist_m, 20000.0, "Route distance should be under 20km")

        coords = graph_manager.route_nodes_to_coords(route)
        self.assertGreaterEqual(len(coords), len(route), "Coordinate count should be >= node count (geometry interpolation)")
        for lat, lng in coords:
            self.assertTrue(12.8 <= lat <= 13.2, f"Latitude {lat} out of Bengaluru bounds")
            self.assertTrue(77.4 <= lng <= 77.8, f"Longitude {lng} out of Bengaluru bounds")

    def test_03_maneuver_generation(self):
        """Maneuver generation must succeed on route."""
        route = two_wheeler_astar(
            self.G,
            self.start_node,
            self.end_node,
            graph_manager,
            penalties=self.penalties,
        )
        maneuvers = generate_route_maneuvers(self.G, route)
        self.assertIsInstance(maneuvers, list)
        self.assertGreater(len(maneuvers), 0, "Route should generate maneuver instructions")

    def test_04_split_route_candidates(self):
        """build_split_route_candidates should function correctly using corrected A* internally."""
        candidates = build_split_route_candidates(
            self.G,
            graph_manager,
            12.9237,
            77.5714,
            12.9756,
            77.6066,
            penalties=self.penalties,
        )
        self.assertIsInstance(candidates, list)
        self.assertGreater(len(candidates), 0, "Expected at least one candidate route")
        direct = candidates[0]
        self.assertEqual(direct["strategy"], "direct")
        self.assertIn("nodes", direct)
        self.assertIn("cost", direct)

    def test_05_explicit_heuristic_modes_and_metrics(self):
        """Verify return_metrics=True returns dict with all expected fields."""
        for mode in ["admissible", "aggressive", "dijkstra"]:
            res = two_wheeler_astar(
                self.G,
                self.start_node,
                self.end_node,
                graph_manager,
                penalties=self.penalties,
                heuristic_mode=mode,
                return_metrics=True,
            )
            self.assertIsInstance(res, dict)
            for key in ["route", "cost", "expanded_states", "expanded_nodes", "explored_transitions", "runtime_ms", "heuristic_mode"]:
                self.assertIn(key, res, f"Missing key '{key}' in metrics dict")
            self.assertEqual(res["heuristic_mode"], mode)
            self.assertGreater(res["cost"], 0.0)
            self.assertGreater(res["expanded_states"], 0)
            self.assertGreater(res["runtime_ms"], 0.0)

    def test_06_invalid_heuristic_mode_raises(self):
        """Passing an unknown heuristic mode raises ValueError."""
        with self.assertRaises(ValueError):
            two_wheeler_astar(
                self.G,
                self.start_node,
                self.end_node,
                graph_manager,
                penalties=self.penalties,
                heuristic_mode="non_existent_mode",
            )


if __name__ == "__main__":
    unittest.main()
