"""
Phase 12.2 Regression Test Suite:
Validates Controlled Defect Remediation for:
1. Identical Origin-Destination Guard in build_split_route_candidates.
2. Geographic Coordinate and Road Network Snapping Validation.

Covers:
1. Identical origin and destination.
2. Different coordinates snapping to the same node.
3. Valid nearby coordinates.
4. Valid coordinates near the graph boundary.
5. Coordinates approximately 455 km outside Bengaluru (Bay of Bengal).
6. Coordinates inside the bounding box but beyond the permitted snapping radius.
7. Existing valid Bengaluru OD routes.
8. Alternative generation for ordinary non-identical OD pairs.
"""

import sys
import os
import unittest
import math
import osmnx as ox

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from routing.graph_manager import graph_manager
from routing.algorithms import (
    two_wheeler_astar,
    build_two_wheeler_penalties,
    calc_route_distance,
    build_split_route_candidates,
    haversine_m,
)
from core.config import DEFAULT_MAX_SNAPPING_DISTANCE_M


class TestPhase12Remediation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Loading road network for Phase 12.2 regression tests...")
        graph_manager.load_graph()
        cls.G = graph_manager.G
        cls.penalties = build_two_wheeler_penalties()

    # --------------------------------------------------------------------------
    # 1. Identical Origin and Destination
    # --------------------------------------------------------------------------
    def test_01_identical_origin_destination(self):
        """When from == to, build_split_route_candidates returns only direct route, 0 alternatives."""
        lat, lng = 12.9237, 77.5714  # BNMIT
        diag = build_split_route_candidates(
            self.G,
            graph_manager,
            lat, lng,
            lat, lng,
            penalties=self.penalties,
            return_diagnostics=True
        )

        self.assertEqual(len(diag["candidates"]), 1, "Must contain exactly 1 route (direct only)")
        self.assertEqual(diag["surviving_count"], 0, "Surviving alternatives must be 0")
        self.assertEqual(diag["generated_count"], 0, "Generated candidate count must be 0")
        self.assertEqual(len(diag["diverse_alternatives"]), 0, "No alternatives produced")

        direct = diag["direct_route"]
        self.assertEqual(direct["distance"], 0.0, "Zero distance for identical OD")
        self.assertEqual(direct["cost"], 0.0, "Zero cost for identical OD")
        self.assertEqual(len(direct["nodes"]), 1, "Single node path")

    # --------------------------------------------------------------------------
    # 2. Different Coordinates Snapping to Same Node
    # --------------------------------------------------------------------------
    def test_02_different_coords_snapping_to_same_node(self):
        """Coordinates 3m apart snapping to the same node must trigger identical OD guard."""
        lat1, lng1 = 12.923700, 77.571400
        lat2, lng2 = 12.923720, 77.571415

        node1 = graph_manager.validate_coordinate(lat1, lng1)
        node2 = graph_manager.validate_coordinate(lat2, lng2)
        self.assertEqual(node1, node2, "Precondition: points must snap to same node")

        diag = build_split_route_candidates(
            self.G,
            graph_manager,
            lat1, lng1,
            lat2, lng2,
            penalties=self.penalties,
            return_diagnostics=True
        )

        self.assertEqual(len(diag["candidates"]), 1)
        self.assertEqual(diag["surviving_count"], 0)
        self.assertEqual(diag["generated_count"], 0)
        self.assertEqual(diag["direct_route"]["nodes"], [node1])

    # --------------------------------------------------------------------------
    # 3. Valid Nearby Coordinates
    # --------------------------------------------------------------------------
    def test_03_valid_nearby_coordinates(self):
        """Valid coordinates ~500m apart route cleanly without error."""
        lat1, lng1 = 12.9237, 77.5714  # BNMIT
        lat2, lng2 = 12.9270, 77.5740  # ~450m northeast

        n1 = graph_manager.validate_coordinate(lat1, lng1)
        n2 = graph_manager.validate_coordinate(lat2, lng2)
        self.assertNotEqual(n1, n2)

        route = two_wheeler_astar(self.G, n1, n2, graph_manager, penalties=self.penalties)
        self.assertIsInstance(route, list)
        self.assertGreater(len(route), 2)
        dist = calc_route_distance(self.G, route)
        self.assertGreater(dist, 200.0)
        self.assertLess(dist, 1000.0)

    # --------------------------------------------------------------------------
    # 4. Valid Coordinates Near Graph Boundary
    # --------------------------------------------------------------------------
    def test_04_valid_coordinates_near_boundary(self):
        """Valid peri-urban coordinates near the outer perimeter validate and route."""
        # Yelahanka north periphery
        lat_bnd, lng_bnd = 13.1500, 77.5900
        node_bnd = graph_manager.validate_coordinate(lat_bnd, lng_bnd)
        self.assertIsInstance(node_bnd, int)

        # Distance to snapped node must be well within permitted radius
        node_y = self.G.nodes[node_bnd]["y"]
        node_x = self.G.nodes[node_bnd]["x"]
        d_m = haversine_m(lat_bnd, lng_bnd, node_y, node_x)
        self.assertLess(d_m, DEFAULT_MAX_SNAPPING_DISTANCE_M)

    # --------------------------------------------------------------------------
    # 5. Extraterritorial Coordinates ~455 km Outside (Bay of Bengal)
    # --------------------------------------------------------------------------
    def test_05_extraterritorial_coordinates_rejected(self):
        """Coordinates in Bay of Bengal (lat 13.0, lng 82.0) must raise ValueError."""
        oob_lat, oob_lng = 13.0000, 82.0000

        with self.assertRaises(ValueError) as ctx:
            graph_manager.validate_coordinate(oob_lat, oob_lng)

        err_msg = str(ctx.exception)
        self.assertTrue("outside the Bengaluru coverage area" in err_msg or "from nearest road" in err_msg)

        # build_split_route_candidates must also reject cleanly
        with self.assertRaises(ValueError):
            build_split_route_candidates(
                self.G,
                graph_manager,
                oob_lat, oob_lng,
                12.9237, 77.5714,
                penalties=self.penalties
            )

    # --------------------------------------------------------------------------
    # 6. Inside Bounding Box but Beyond Snapping Radius
    # --------------------------------------------------------------------------
    def test_06_inside_bbox_beyond_snapping_radius_rejected(self):
        """Coordinates with distance > max_distance_m must raise ValueError."""
        lat, lng = 12.9237, 77.5714  # BNMIT area
        nearest = ox.nearest_nodes(self.G, lng, lat)
        actual_dist = haversine_m(lat, lng, self.G.nodes[nearest]["y"], self.G.nodes[nearest]["x"])

        # Set a threshold smaller than the actual distance to test distance rejection
        strict_thresh = actual_dist * 0.5
        with self.assertRaises(ValueError) as ctx:
            graph_manager.validate_coordinate(lat, lng, max_distance_m=strict_thresh)

        err_msg = str(ctx.exception)
        self.assertIn("exceeding the maximum allowed snapping threshold", err_msg)

    # --------------------------------------------------------------------------
    # 7. Existing Valid Bengaluru OD Routes
    # --------------------------------------------------------------------------
    def test_07_existing_valid_bengaluru_od_route(self):
        """Standard benchmark OD_01 (BNMIT to MG Road) routes with expected distance."""
        from_lat, from_lng = 12.9237, 77.5714
        to_lat, to_lng = 12.9756, 77.6066

        n_start = graph_manager.validate_coordinate(from_lat, from_lng)
        n_end = graph_manager.validate_coordinate(to_lat, to_lng)

        route = two_wheeler_astar(self.G, n_start, n_end, graph_manager, penalties=self.penalties)
        dist_km = calc_route_distance(self.G, route) / 1000.0

        self.assertGreater(len(route), 100)
        self.assertAlmostEqual(dist_km, 10.065, delta=0.5)

    # --------------------------------------------------------------------------
    # 8. Alternative Generation for Ordinary Non-Identical OD Pairs
    # --------------------------------------------------------------------------
    def test_08_alternative_generation_ordinary_od(self):
        """Ordinary non-identical OD pair produces valid alternatives within detour and overlap caps."""
        from_lat, from_lng = 12.9237, 77.5714
        to_lat, to_lng = 12.9756, 77.6066

        diag = build_split_route_candidates(
            self.G,
            graph_manager,
            from_lat, from_lng,
            to_lat, to_lng,
            penalties=self.penalties,
            return_diagnostics=True
        )

        self.assertGreater(len(diag["candidates"]), 1, "Must produce primary + alternatives")
        self.assertGreater(diag["surviving_count"], 0, "Must have surviving alternatives")

        # Validate that all surviving alternatives satisfy constraints
        for alt in diag["diverse_alternatives"]:
            self.assertLessEqual(alt["detour_ratio"], 1.2001, "Detour ratio must be <= 1.20")
            self.assertLessEqual(alt["overlap_ratio"], 0.7001, "Overlap ratio must be <= 0.70")


if __name__ == "__main__":
    unittest.main()
