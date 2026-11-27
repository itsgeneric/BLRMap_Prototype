"""
Tests for routing/snapping.py and astar_multi(): pins are attached to the nearest ROAD (one-way aware), routes start and
end ON a road, and nothing is drawn between a pin and the road.

Run from the repository root:

    python -m unittest tests.test_snapping -v

Layouts are tiny hand-built maps around 12.97 N, 77.59 E; distances are in metres.
"""
import random
import unittest

import networkx as nx

from routing.algorithms import astar_multi
from routing.graph_manager import GraphManager
from routing.graph_qa import RoadIndex
from routing.snapping import FAR_PIN_M, _sub_polyline, find_snaps, nearby_junction_snaps, plan_route
from tests.test_astar_admissibility import SEEDS, FakeBlacklist, Scenario, path_cost
from tests.test_graph_qa import KX, LAT0, LNG0, at, build_graph


def manager_for(G):
    gm = GraphManager()
    gm.G = G
    return gm


def highway_of(G, snap):
    u, v, key = snap.edge
    return G[u][v][key]['highway']


# ----------------------------------------------------------------------------------------------- astar_multi

class AStarMultiTests(unittest.TestCase):

    def test_matches_dijkstra_with_source_and_target_offsets(self):
        """Cheapest (source offset + path + target extra) over every source/target pair, vs Dijkstra with a virtual S and T."""
        reachable = 0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                sc = Scenario(seed)
                rng = random.Random(seed + 500)
                nodes = list(sc.G.nodes)
                sources = {n: rng.choice([0.0, 30.0, 120.0]) for n in rng.sample(nodes, 2)}
                targets = {n: rng.choice([0.0, 25.0, 90.0]) for n in rng.sample(nodes, 2)}
                cost = sc.cost_fn()

                H = sc.G.copy()
                for n, g0 in sources.items():
                    H.add_edge('S', n, vc=g0)
                for n, extra in targets.items():
                    H.add_edge(n, 'T', vc=extra)

                def weight(u, v, d):
                    if u == 'S' or v == 'T':
                        return min(attrs['vc'] for attrs in d.values())
                    return cost(u, v, d)

                try:
                    expected = nx.dijkstra_path_length(H, 'S', 'T', weight=weight)
                except nx.NetworkXNoPath:
                    expected = None
                try:
                    path, total = astar_multi(sc.G, sources, targets, cost, sc.multiplier())
                except nx.NetworkXNoPath:
                    path, total = None, None

                if expected is None:
                    self.assertIsNone(path)
                    continue
                reachable += 1
                self.assertIsNotNone(path)
                self.assertAlmostEqual(total, expected, delta=1e-6 * max(1.0, expected))
                self.assertIn(path[0], sources)
                self.assertIn(path[-1], targets)
                rebuilt = sources[path[0]] + path_cost(sc.G, path, cost) + targets[path[-1]]
                self.assertAlmostEqual(rebuilt, total, delta=1e-6 * max(1.0, total))
        self.assertGreater(reachable, 3)

    def test_start_equal_to_end_is_a_single_node_path(self):
        G = nx.MultiDiGraph()
        G.add_node(1, y=LAT0, x=LNG0)
        path, total = astar_multi(G, {1: 5.0}, {1: 7.0}, lambda u, v, d: 1.0, 1.0)
        self.assertEqual((path, total), ([1], 12.0))

    def test_unreachable_target_raises(self):
        G = nx.MultiDiGraph()
        G.add_node(1, y=LAT0, x=LNG0)
        G.add_node(2, y=LAT0, x=LNG0 + 0.001)
        with self.assertRaises(nx.NetworkXNoPath):
            astar_multi(G, {1: 0.0}, {2: 0.0}, lambda u, v, d: 1.0, 1.0)


# ----------------------------------------------------------------------------------------------- find_snaps

class FindSnapsTests(unittest.TestCase):

    def test_pin_attaches_to_the_nearest_road_not_the_nearest_junction(self):
        """Mirrors the reported trip: a side lane's junction is nearer to the pin than either end of the long road."""
        G = build_graph([
            ((0, 0), (600, 0), 'primary', True),          # long road, 104 m north of the pin, junctions 317 m away
            ((400, -30), (480, -30), 'residential', True),  # lane whose junction (400, -30) is 124 m from the pin
        ])
        pin = at(300, -104)
        snaps = find_snaps(G, RoadIndex.from_graph(G), pin[0], pin[1], max_m=500)
        self.assertTrue(snaps)
        self.assertAlmostEqual(snaps[0].distance_m, 104.0, delta=1.5)
        self.assertEqual({highway_of(G, s) for s in snaps}, {'primary'})
        self.assertAlmostEqual(snaps[0].point[0], LAT0, places=6)               # the point is ON the road
        self.assertAlmostEqual(snaps[0].point[1], at(300, 0)[1], places=6)

    def test_two_way_road_offers_both_directions(self):
        G = build_graph([((0, 0), (600, 0), 'primary', True)])
        pin = at(300, -40)
        snaps = find_snaps(G, RoadIndex.from_graph(G), pin[0], pin[1], max_m=500)
        self.assertEqual(len(snaps), 2)
        self.assertEqual({s.node_after for s in snaps}, {0, 1})

    def test_one_way_road_only_allows_its_direction(self):
        G = build_graph([((0, 0), (600, 0), 'primary', False)])        # west -> east only
        pin = at(300, -40)
        snaps = find_snaps(G, RoadIndex.from_graph(G), pin[0], pin[1], max_m=500)
        self.assertEqual(len(snaps), 1)
        s = snaps[0]
        self.assertGreater(G.nodes[s.node_after]['x'], G.nodes[s.node_before]['x'])   # leave eastwards, arrive from the west
        self.assertAlmostEqual(s.along_m + s.after_m, s.length_m, delta=0.01)
        self.assertAlmostEqual(s.along_m, 300.0, delta=1.0)

    def test_no_road_within_max_distance_gives_no_snap(self):
        G = build_graph([((0, 0), (600, 0), 'primary', True)])
        pin = at(300, -800)
        self.assertEqual(find_snaps(G, RoadIndex.from_graph(G), pin[0], pin[1], max_m=500), [])

    def test_sub_polyline_returns_the_requested_stretch(self):
        shape = [at(0, 0), at(100, 0), at(200, 0)]
        part = _sub_polyline(shape, 0.25, 0.75)                 # x = 50 .. 150
        self.assertAlmostEqual(part[0][1], at(50, 0)[1], places=6)
        self.assertAlmostEqual(part[-1][1], at(150, 0)[1], places=6)
        self.assertEqual(len(part), 3)                          # start, the vertex at x=100, end


# ----------------------------------------------------------------------------------------------- plan_route

def crossing_roads():
    """R1: (0,0)-(600,0) and R2: (600,0)-(600,600), both two-way, meeting at the junction (600, 0)."""
    return build_graph([
        ((0, 0), (600, 0), 'primary', True),
        ((600, 0), (600, 600), 'primary', True),
    ])


class PlanRouteTests(unittest.TestCase):

    def plan(self, G, mode, a, b, **kwargs):
        index = RoadIndex.from_graph(G)
        pa, pb = at(*a), at(*b)
        origins = find_snaps(G, index, pa[0], pa[1], 500)
        destinations = find_snaps(G, index, pb[0], pb[1], 500)
        return plan_route(G, manager_for(G), mode, origins, destinations, blacklist=FakeBlacklist(), **kwargs), pa, pb

    def test_route_starts_and_ends_on_the_road_and_no_connector_is_added(self):
        G = crossing_roads()
        for mode in ('shortest', 'dynamic'):
            with self.subTest(mode=mode):
                plan, pin_a, pin_b = self.plan(G, mode, (100, -30), (630, 300))
                coords = plan['coords']
                self.assertAlmostEqual(coords[0][0], LAT0, places=6)                      # starts on R1, not at the pin
                self.assertAlmostEqual(coords[0][1], at(100, 0)[1], places=6)
                self.assertAlmostEqual(coords[-1][1], at(600, 0)[1], places=6)            # ends on R2, not at the pin
                self.assertAlmostEqual(coords[-1][0], at(0, 300)[0], places=6)
                self.assertNotIn(list(pin_a), [list(c) for c in coords])
                self.assertNotIn(list(pin_b), [list(c) for c in coords])
                self.assertAlmostEqual(plan['distance_m'], 800.0, delta=2.0)              # 500 m along R1 + 300 m up R2
                self.assertAlmostEqual(plan['origin_snap']['distance_m'], 30.0, delta=1.0)
                self.assertAlmostEqual(plan['destination_snap']['distance_m'], 30.0, delta=1.0)

    def test_both_pins_on_the_same_road_drive_just_that_stretch(self):
        G = crossing_roads()
        plan, _, _ = self.plan(G, 'dynamic', (100, -30), (400, -30))
        self.assertEqual(plan['nodes'], [])
        self.assertAlmostEqual(plan['distance_m'], 300.0, delta=1.0)
        self.assertAlmostEqual(plan['coords'][0][1], at(100, 0)[1], places=6)
        self.assertAlmostEqual(plan['coords'][-1][1], at(400, 0)[1], places=6)
        for lat, _ in plan['coords']:
            self.assertAlmostEqual(lat, LAT0, places=6)

    def test_one_way_road_cannot_be_driven_backwards(self):
        G = build_graph([((0, 0), (600, 0), 'primary', False)])           # west -> east only
        index = RoadIndex.from_graph(G)
        pa, pb = at(400, -30), at(100, -30)                               # destination is BEHIND the origin
        origins = find_snaps(G, index, pa[0], pa[1], 500)
        destinations = find_snaps(G, index, pb[0], pb[1], 500)
        with self.assertRaises(nx.NetworkXNoPath):
            plan_route(G, manager_for(G), 'shortest', origins, destinations, blacklist=FakeBlacklist())

    def test_destination_ahead_on_a_one_way_road_works(self):
        G = build_graph([((0, 0), (600, 0), 'primary', False)])
        index = RoadIndex.from_graph(G)
        pa, pb = at(100, -30), at(400, -30)
        plan = plan_route(G, manager_for(G), 'shortest',
                          find_snaps(G, index, pa[0], pa[1], 500), find_snaps(G, index, pb[0], pb[1], 500),
                          blacklist=FakeBlacklist())
        self.assertAlmostEqual(plan['distance_m'], 300.0, delta=1.0)


class PlannedDurationTests(unittest.TestCase):
    """Every route carries a planned duration: road length / free-flow speed per class, plus a delay per sharp turn."""

    def plan(self, G, a, b):
        index = RoadIndex.from_graph(G)
        pa, pb = at(*a), at(*b)
        return plan_route(G, manager_for(G), 'dynamic',
                          find_snaps(G, index, pa[0], pa[1], 500), find_snaps(G, index, pb[0], pb[1], 500),
                          blacklist=FakeBlacklist())

    def test_duration_is_length_over_class_speed_plus_the_turn_delay(self):
        from core.config import FREE_FLOW_SPEED_KMH
        from routing.snapping import SHARP_TURN_DELAY_S
        plan = self.plan(crossing_roads(), (100, -30), (630, 300))     # 500 m + 300 m on primary roads, one left turn
        expected = 800.0 / (FREE_FLOW_SPEED_KMH['primary'] / 3.6) + SHARP_TURN_DELAY_S
        self.assertAlmostEqual(plan['duration_s'], expected, delta=3.0)

    def test_a_trip_on_one_road_has_no_turn_delay(self):
        from core.config import FREE_FLOW_SPEED_KMH
        plan = self.plan(crossing_roads(), (100, -30), (400, -30))     # 300 m straight on one road
        self.assertAlmostEqual(plan['duration_s'], 300.0 / (FREE_FLOW_SPEED_KMH['primary'] / 3.6), delta=2.0)

    def test_faster_roads_give_shorter_durations(self):
        slow = self.plan(build_graph([((0, 0), (600, 0), 'residential', True)]), (100, -20), (500, -20))
        fast = self.plan(build_graph([((0, 0), (600, 0), 'trunk', True)]), (100, -20), (500, -20))
        self.assertLess(fast['duration_s'], slow['duration_s'])


class OffRoadPinTests(unittest.TestCase):
    """A pin off the road also gets nearby junctions as options, so a one-way segment cannot force a long detour."""

    def world(self):
        # X: one-way west->east dead end (0,0)->(500,0).  Y: two-way road down from X's west end to the destination.
        return build_graph([
            ((0, 0), (500, 0), 'primary', False),
            ((0, 0), (0, -300), 'primary', True),
        ])

    def test_far_pin_gets_junction_candidates_and_near_pin_does_not(self):
        G = self.world()
        index = RoadIndex.from_graph(G)
        far, near = at(100, -50), at(100, -3)
        far_road = find_snaps(G, index, far[0], far[1], 500)
        near_road = find_snaps(G, index, near[0], near[1], 500)
        self.assertGreater(far_road[0].distance_m, 40.0)
        self.assertLess(near_road[0].distance_m, FAR_PIN_M)
        self.assertTrue(nearby_junction_snaps(G, index, far[0], far[1], far_road[0].distance_m))
        for snap in nearby_junction_snaps(G, index, far[0], far[1], far_road[0].distance_m):
            self.assertIsNone(snap.edge)
            self.assertGreater(snap.access_m, 0.0)

    def test_junction_candidate_rescues_a_pin_locked_onto_a_dead_end_one_way(self):
        G = self.world()
        index = RoadIndex.from_graph(G)
        a, b = at(100, -50), at(10, -295)
        road_only = find_snaps(G, index, a[0], a[1], 500)
        destinations = find_snaps(G, index, b[0], b[1], 500)
        with self.assertRaises(nx.NetworkXNoPath):                       # edge snapping alone: stuck on the dead end
            plan_route(G, manager_for(G), 'shortest', road_only, destinations, blacklist=FakeBlacklist())
        with_junctions = road_only + nearby_junction_snaps(G, index, a[0], a[1], road_only[0].distance_m)
        plan = plan_route(G, manager_for(G), 'shortest', with_junctions, destinations, blacklist=FakeBlacklist())
        self.assertAlmostEqual(plan['coords'][0][0], LAT0, places=6)      # starts at the junction (0, 0), on the road
        self.assertAlmostEqual(plan['coords'][0][1], LNG0, places=6)
        self.assertAlmostEqual(plan['distance_m'], 295.0, delta=3.0)

    def test_on_road_pin_is_still_locked_to_its_direction(self):
        G = build_graph([((0, 0), (600, 0), 'primary', False)])           # one-way west->east
        index = RoadIndex.from_graph(G)
        a, b = at(400, -10), at(100, -10)                                  # on the road, destination behind
        origins = find_snaps(G, index, a[0], a[1], 500)
        destinations = find_snaps(G, index, b[0], b[1], 500)
        self.assertLess(origins[0].distance_m, FAR_PIN_M)
        with self.assertRaises(nx.NetworkXNoPath):
            plan_route(G, manager_for(G), 'shortest', origins, destinations, blacklist=FakeBlacklist())


if __name__ == '__main__':
    unittest.main()
