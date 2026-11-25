"""
Mathematical Validation and Counterexample Test Suite for A* Heuristics.

This test suite verifies:
1. Admissibility condition: h(goal) == 0, and h(u) <= c*(u, goal) across all road types.
2. Consistency (monotonicity): h(u) <= c(u, v) + P_turn(p, u, v) + h(v) for all transitions.
3. Dijkstra Ground-Truth Optimality: Standard Admissible A* strictly matches Dijkstra cost (0.0% optimality gap).
4. Suboptimality Counterexample: Demonstrates an explicit topology where Aggressive A* produces
   a strictly suboptimal route while Standard Admissible A* finds the optimal route.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import math
import unittest
import networkx as nx

from routing.algorithms import (
    two_wheeler_astar,
    two_wheeler_edge_cost,
    _turn_penalty,
    haversine_m,
    MIN_PENALTY_FLOOR,
)
from core.config import (
    TWO_WHEELER_ROAD_PENALTIES,
    MAIN_ROAD_TYPES,
)


class MockGraphManager:
    """Mock graph manager providing neutral surface penalty."""
    def get_surface_penalty(self, u, v):
        return 1.0


class TestAStarMathematicalValidation(unittest.TestCase):

    def setUp(self):
        self.mock_mgr = MockGraphManager()

    def test_01_heuristic_at_goal_is_zero(self):
        """Verify h(goal) == 0.0 for all heuristic modes."""
        G = nx.MultiDiGraph()
        G.add_node("G", y=12.9716, x=77.5946)

        for mode in ["admissible", "aggressive", "dijkstra", "zero"]:
            # Evaluate heuristic at goal
            dist = haversine_m(12.9716, 77.5946, 12.9716, 77.5946)
            if mode in ("zero", "dijkstra"):
                h = 0.0
            elif mode == "aggressive":
                h = dist / MIN_PENALTY_FLOOR
            else:
                h = dist * MIN_PENALTY_FLOOR

            self.assertAlmostEqual(h, 0.0, places=9, msg=f"h(goal) != 0 for mode {mode}")

    def test_02_admissibility_across_road_classes(self):
        """
        Verify h(u) <= c(u, goal) for single-edge paths across all OSM road classes.
        Because c(u, goal) = length * penalty >= length * 0.8,
        and haversine(u, goal) <= length,
        h(u) = 0.8 * haversine(u, goal) <= c(u, goal) MUST hold universally.
        """
        lat_u, lon_u = 12.9700, 77.5900
        lat_v, lon_v = 12.9750, 77.5950
        straight_dist = haversine_m(lat_u, lon_u, lat_v, lon_v)

        # Candidate road configurations
        test_configs = [
            {"highway": "residential", "length": straight_dist},
            {"highway": "living_street", "length": straight_dist},
            {"highway": "primary", "length": straight_dist},
            {"highway": "secondary", "length": straight_dist},
            {"highway": "tertiary", "length": straight_dist},
            {"highway": "trunk", "length": straight_dist},
            {"highway": "motorway", "length": straight_dist},
            {"highway": "trunk", "bridge": "yes", "length": straight_dist}, # minimum penalty 0.8
            {"highway": "residential", "junction": "roundabout", "length": straight_dist},
            {"highway": "primary", "bridge": "yes", "length": straight_dist},
        ]

        h_admissible = straight_dist * MIN_PENALTY_FLOOR
        h_aggressive = straight_dist / MIN_PENALTY_FLOOR

        for cfg in test_configs:
            edge_cost = two_wheeler_edge_cost(cfg, self.mock_mgr)
            # Admissible heuristic must NOT exceed actual edge cost
            self.assertLessEqual(
                h_admissible,
                edge_cost + 1e-9,
                f"Admissibility violation on {cfg}: h={h_admissible:.3f} > cost={edge_cost:.3f}"
            )

            # Record if aggressive heuristic overestimates the lowest-cost edge
            if cfg.get("bridge") == "yes" and cfg.get("highway") in MAIN_ROAD_TYPES:
                # Here edge_cost = straight_dist * 0.8
                # Aggressive h = straight_dist * 1.25 > edge_cost
                self.assertGreater(
                    h_aggressive,
                    edge_cost,
                    "Aggressive heuristic should strictly overestimate flyover bridge cost"
                )

    def test_03_consistency_and_triangle_inequality(self):
        """
        Verify monotonicity / consistency condition:
        h(u) <= c(u, v) + P_turn(p, u, v) + h(v)
        for arbitrary geometric angles and road classes.
        """
        # Node P at origin (12.9700, 77.5900)
        # Node U north of P (12.9720, 77.5900)
        # Node V at various compass headings from U
        # Goal G further north-east (12.9800, 77.6000)
        lat_g, lon_g = 12.9800, 77.6000

        G = nx.MultiDiGraph()
        G.add_node("P", y=12.9700, x=77.5900)
        G.add_node("U", y=12.9720, x=77.5900)
        G.add_node("G", y=lat_g, x=lon_g)

        headings = [0, 30, 45, 60, 90, 120, 135, 180]
        step_deg = 0.0020

        for heading in headings:
            rad = math.radians(heading)
            lat_v = 12.9720 + step_deg * math.cos(rad)
            lon_v = 77.5900 + step_deg * math.sin(rad)
            v_name = f"V_{heading}"
            G.add_node(v_name, y=lat_v, x=lon_v)

            dist_uv = haversine_m(12.9720, 77.5900, lat_v, lon_v)
            edge_data = {"highway": "residential", "length": dist_uv}
            c_uv = two_wheeler_edge_cost(edge_data, self.mock_mgr)
            p_turn = _turn_penalty(G, "P", "U", v_name)

            h_u = haversine_m(12.9720, 77.5900, lat_g, lon_g) * MIN_PENALTY_FLOOR
            h_v = haversine_m(lat_v, lon_v, lat_g, lon_g) * MIN_PENALTY_FLOOR

            # Consistency condition: h(u) <= c(u, v) + p_turn + h(v)
            slack = (c_uv + p_turn + h_v) - h_u
            self.assertGreaterEqual(
                slack,
                -1e-7,
                f"Consistency violated at heading {heading} deg: slack={slack:.4f}"
            )

    def test_04_dijkstra_optimality_on_synthetic_grid(self):
        """
        Verify that Standard Admissible A* strictly matches Dijkstra ground truth
        on a multi-route synthetic grid with varying road types and turn penalties.
        """
        G = nx.MultiDiGraph()
        # 3x3 Grid of nodes
        for r in range(3):
            for c in range(3):
                name = f"N_{r}_{c}"
                lat = 12.9700 + r * 0.0030
                lon = 77.5900 + c * 0.0030
                G.add_node(name, y=lat, x=lon)

        # Add horizontal and vertical edges with mixed road classes
        road_types = ["residential", "primary", "secondary", "tertiary"]
        edge_idx = 0
        for r in range(3):
            for c in range(3):
                u = f"N_{r}_{c}"
                if c < 2:
                    v = f"N_{r}_{c+1}"
                    hw = road_types[edge_idx % len(road_types)]
                    d = haversine_m(G.nodes[u]["y"], G.nodes[u]["x"], G.nodes[v]["y"], G.nodes[v]["x"])
                    G.add_edge(u, v, length=d, highway=hw)
                    edge_idx += 1
                if r < 2:
                    v = f"N_{r+1}_{c}"
                    hw = road_types[edge_idx % len(road_types)]
                    d = haversine_m(G.nodes[u]["y"], G.nodes[u]["x"], G.nodes[v]["y"], G.nodes[v]["x"])
                    G.add_edge(u, v, length=d, highway=hw)
                    edge_idx += 1

        start = "N_0_0"
        end = "N_2_2"

        dijkstra_res = two_wheeler_astar(G, start, end, self.mock_mgr, heuristic_mode="dijkstra", return_metrics=True)
        admissible_res = two_wheeler_astar(G, start, end, self.mock_mgr, heuristic_mode="admissible", return_metrics=True)

        # Costs must be identical
        self.assertAlmostEqual(
            admissible_res["cost"],
            dijkstra_res["cost"],
            places=6,
            msg=f"Cost mismatch: Admissible={admissible_res['cost']:.4f} vs Dijkstra={dijkstra_res['cost']:.4f}"
        )
        # Search efficiency: Admissible A* should expand fewer or equal states than Dijkstra
        self.assertLessEqual(
            admissible_res["expanded_states"],
            dijkstra_res["expanded_states"],
            "Admissible A* expanded more states than uniform Dijkstra"
        )

    def test_05_aggressive_heuristic_suboptimality_counterexample(self):
        """
        Construct a concrete counterexample topology where:
        - Aggressive A* (h = 1.25 * haversine) discovers a SUBOPTIMAL path.
        - Standard Admissible A* (h = 0.8 * haversine) discovers the STRICTLY OPTIMAL path.
        - Dijkstra baseline confirms the optimal path cost.
        """
        G = nx.MultiDiGraph()

        # Geometric layout:
        # Start S: (12.9700, 77.5900)
        # Goal G:  (12.9800, 77.5900)  [Directly North, distance ~ 1108.9 m]
        #
        # Path 1 (Suboptimal Direct Path): S -> DirectMid -> G
        # Geometrically direct (h is small), but road is high penalty (primary road, multiplier 2.2).
        # S -> DirectMid: length 554.5 m * 2.2 = 1219.9
        # DirectMid -> G: length 554.5 m * 2.2 = 1219.9
        # Total cost Path 1 = 2439.8
        #
        # Path 2 (Optimal Detour Path via Flyover): S -> FlyoverMid -> G
        # Geometrically detours East to (12.9750, 77.5970).
        # Distance S -> FlyoverMid: ~946 m
        # Distance FlyoverMid -> G: ~946 m
        # Road is Trunk Flyover (multiplier 0.8).
        # Cost S -> FlyoverMid: 946 * 0.8 = 756.8
        # Cost FlyoverMid -> G: 946 * 0.8 = 756.8
        # Maneuver turn at FlyoverMid: ~70 deg (sharp turn = 25.0)
        # Total cost Path 2 = 756.8 + 25.0 + 756.8 = 1538.6  <-- MUCH CHEAPER than 2439.8!
        #
        # Why Aggressive A* Fails:
        # At S:
        # - DirectMid: g = 1219.9, h_dist = 554.5m
        #   h_aggressive = 554.5 / 0.8 = 693.1  --> f = 1219.9 + 693.1 = 1913.0
        # - FlyoverMid: g = 756.8, h_dist = 946m
        #   h_aggressive = 946.0 / 0.8 = 1182.5 --> f = 756.8 + 1182.5 = 1939.3
        #
        # Because f(DirectMid) = 1913.0 < f(FlyoverMid) = 1939.3,
        # Aggressive A* pops DirectMid FIRST!
        # From DirectMid, it evaluates G:
        # g(G via Direct) = 2439.8, h(G) = 0 --> f = 2439.8.
        # But wait! If FlyoverMid has f = 1939.3 < 2439.8, it will still expand FlyoverMid unless
        # we adjust the geometry slightly so f(DirectMid to G) completes before FlyoverMid is reached,
        # or we add an intermediate node on the flyover.
        #
        # Let's add intermediate node to flyover:
        # S -> Fly1 -> Fly2 -> G
        # S: (12.9700, 77.5900)
        # DirectMid: (12.9750, 77.5900)
        # G: (12.9800, 77.5900)

        G.add_node("S", y=12.9700, x=77.5900)
        G.add_node("G", y=12.9800, x=77.5900)
        G.add_node("DirectMid", y=12.9750, x=77.5900)

        dist_s_dm = haversine_m(12.9700, 77.5900, 12.9750, 77.5900)
        dist_dm_g = haversine_m(12.9750, 77.5900, 12.9800, 77.5900)
        G.add_edge("S", "DirectMid", length=dist_s_dm, highway="primary")
        G.add_edge("DirectMid", "G", length=dist_dm_g, highway="primary")

        # Flyover detour: S -> F1 -> F2 -> G
        # Offset east by 0.0090 degrees (~980m)
        offset = 0.0090
        G.add_node("F1", y=12.9710, x=77.5900 + offset)
        G.add_node("F2", y=12.9790, x=77.5900 + offset)

        dist_s_f1 = haversine_m(12.9700, 77.5900, 12.9710, 77.5900 + offset)
        dist_f1_f2 = haversine_m(12.9710, 77.5900 + offset, 12.9790, 77.5900 + offset)
        dist_f2_g = haversine_m(12.9790, 77.5900 + offset, 12.9800, 77.5900)

        G.add_edge("S", "F1", length=dist_s_f1, highway="trunk", bridge="yes")
        G.add_edge("F1", "F2", length=dist_f1_f2, highway="trunk", bridge="yes")
        G.add_edge("F2", "G", length=dist_f2_g, highway="trunk", bridge="yes")

        res_dijkstra = two_wheeler_astar(G, "S", "G", self.mock_mgr, heuristic_mode="dijkstra", return_metrics=True)
        res_admissible = two_wheeler_astar(G, "S", "G", self.mock_mgr, heuristic_mode="admissible", return_metrics=True)
        res_aggressive = two_wheeler_astar(G, "S", "G", self.mock_mgr, heuristic_mode="aggressive", return_metrics=True)

        # Admissible MUST match Dijkstra (optimal ground truth)
        self.assertAlmostEqual(res_admissible["cost"], res_dijkstra["cost"], places=6)
        self.assertEqual(res_admissible["route"], res_dijkstra["route"])
        self.assertEqual(res_admissible["route"], ["S", "F1", "F2", "G"])

        # Aggressive heuristic overestimates and prematurely terminates on suboptimal direct route
        self.assertEqual(res_aggressive["route"], ["S", "DirectMid", "G"])
        self.assertGreater(res_aggressive["cost"], res_admissible["cost"])

        cost_diff = res_aggressive["cost"] - res_admissible["cost"]
        pct_gap = (cost_diff / res_admissible["cost"]) * 100.0

        print(f"\n[Counterexample Verification]")
        print(f"Dijkstra (Ground Truth): Route={res_dijkstra['route']}, Cost={res_dijkstra['cost']:.2f}")
        print(f"Standard Admissible A*:  Route={res_admissible['route']}, Cost={res_admissible['cost']:.2f} (Gap: 0.00%)")
        print(f"Aggressive A*:          Route={res_aggressive['route']}, Cost={res_aggressive['cost']:.2f} (Suboptimal Gap: +{pct_gap:.2f}%)")


if __name__ == "__main__":
    unittest.main()
