"""
Tests for the restored routing model: turn penalties, the flyover exception, the turn-aware A* (astar_turns) and the
turn-by-turn maneuvers.

Run from the repository root:

    python -m unittest tests.test_turn_routing -v
"""
import math
import random
import unittest
from unittest import mock

import networkx as nx

from core.config import (
    FLYOVER_MAIN_ROAD_MULTIPLIER,
    TURN_PENALTY_MODERATE_M,
    TURN_PENALTY_SHARP_M,
    TWO_WHEELER_ROAD_PENALTIES_HIERARCHY as TWO_WHEELER_ROAD_PENALTIES,
)
from routing.algorithms import (
    CONGESTED_NODE_MULTIPLIER,
    astar_path_turns,
    astar_turns,
    generate_route_maneuvers,
    length_cost_fn,
    turn_penalty_m,
    two_wheeler_edge_cost,
)
from routing.graph_manager import GraphManager
from routing.graph_qa import RoadIndex
from routing.snapping import find_snaps, plan_route
from tests.test_astar_admissibility import SEEDS, FakeBlacklist, FakeGraphManager, Scenario
from tests.test_graph_qa import LAT0, at



# These tests' expected numbers assume the paper's impedance hierarchy; the time model has its own tests (test_time_cost.py).
def setUpModule():
    global _table_patch, _flyover_patch
    _table_patch = mock.patch('routing.algorithms.TWO_WHEELER_ROAD_PENALTIES', TWO_WHEELER_ROAD_PENALTIES)
    _flyover_patch = mock.patch('routing.algorithms.FLYOVER_EXCEPTION_ENABLED', True)     # the paper model includes it
    _table_patch.start()
    _flyover_patch.start()


def tearDownModule():
    _flyover_patch.stop()
    _table_patch.stop()


def named_graph(roads):
    """roads: [(from_xy, to_xy, highway, name)] in metres; every road is two-way. Edge length = straight distance."""
    G = nx.MultiDiGraph()
    ids = {}

    def node(xy):
        if xy not in ids:
            ids[xy] = len(ids)
            lat, lng = at(*xy)
            G.add_node(ids[xy], y=lat, x=lng)
        return ids[xy]

    for a, b, highway, name in roads:
        u, v = node(a), node(b)
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        G.add_edge(u, v, length=length, highway=highway, name=name)
        G.add_edge(v, u, length=length, highway=highway, name=name)
    return G, ids


def manager_for(G):
    gm = GraphManager()
    gm.G = G
    return gm


# ----------------------------------------------------------------------------------------------- penalties

class TurnPenaltyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.G, ids = named_graph([
            ((0, 0), (100, 0), 'residential', 'A'),
            ((100, 0), (200, 0), 'residential', 'A'),       # straight on
            ((100, 0), (200, 50), 'residential', 'B'),      # ~27 degrees
            ((100, 0), (200, 100), 'residential', 'C'),     # 45 degrees
            ((100, 0), (100, 100), 'residential', 'D'),     # 90 degrees
        ])
        cls.ids = ids

    def penalty(self, nxt):
        i = self.ids
        return turn_penalty_m(self.G, i[(0, 0)], i[(100, 0)], i[nxt])

    def test_first_move_has_no_turn_cost(self):
        i = self.ids
        self.assertEqual(turn_penalty_m(self.G, None, i[(100, 0)], i[(100, 100)]), 0.0)

    def test_straight_and_gentle_bends_are_free(self):
        self.assertEqual(self.penalty((200, 0)), 0.0)
        self.assertEqual(self.penalty((200, 50)), 0.0)

    def test_moderate_and_sharp_turns_cost_extra(self):
        self.assertEqual(self.penalty((200, 100)), TURN_PENALTY_MODERATE_M)
        self.assertEqual(self.penalty((100, 100)), TURN_PENALTY_SHARP_M)

    def test_u_turn_is_sharp(self):
        i = self.ids
        self.assertEqual(turn_penalty_m(self.G, i[(0, 0)], i[(100, 0)], i[(0, 0)]), TURN_PENALTY_SHARP_M)


class FlyoverExceptionTests(unittest.TestCase):

    def cost(self, edge, **kwargs):
        return two_wheeler_edge_cost(edge, FakeGraphManager(), None, 1, 2, blacklist=FakeBlacklist(), **kwargs)

    def test_flyover_on_a_main_road_is_cheaper_than_the_road(self):
        self.assertAlmostEqual(self.cost({'length': 100.0, 'highway': 'primary', 'bridge': 'yes'}),
                               100.0 * FLYOVER_MAIN_ROAD_MULTIPLIER)
        self.assertAlmostEqual(self.cost({'length': 100.0, 'highway': 'primary', 'bridge': ['yes']}),
                               100.0 * FLYOVER_MAIN_ROAD_MULTIPLIER)

    def test_bridge_no_is_just_a_road(self):
        self.assertAlmostEqual(self.cost({'length': 100.0, 'highway': 'primary', 'bridge': 'no'}),
                               100.0 * TWO_WHEELER_ROAD_PENALTIES['primary'])

    def test_bridge_on_a_minor_road_gets_no_discount(self):
        self.assertAlmostEqual(self.cost({'length': 100.0, 'highway': 'residential', 'bridge': 'yes'}),
                               100.0 * TWO_WHEELER_ROAD_PENALTIES['residential'])

    def test_other_factors_still_apply_to_a_flyover(self):
        cost = self.cost({'length': 100.0, 'highway': 'primary', 'bridge': 'yes'}, congested_nodes={1})
        self.assertAlmostEqual(cost, 100.0 * FLYOVER_MAIN_ROAD_MULTIPLIER * CONGESTED_NODE_MULTIPLIER)

    def test_arterials_cost_more_than_inner_roads(self):
        """The restored hierarchy: this is what steers two-wheelers onto inner roads."""
        arterial = self.cost({'length': 100.0, 'highway': 'primary'})
        inner = self.cost({'length': 100.0, 'highway': 'residential'})
        self.assertGreater(arterial, 2.0 * inner)


# ----------------------------------------------------------------------------------------------- the search

def state_dijkstra_total(G, cost, sources, targets):
    """Ground truth: Dijkstra over explicit (previous, node) states with the same edge and turn costs."""
    S = nx.DiGraph()
    for c in G.nodes:
        for n, edge_data in G[c].items():
            edge = cost(c, n, edge_data)
            for p in [None] + list(G.predecessors(c)):
                S.add_edge((p, c), (c, n), weight=edge + turn_penalty_m(G, p, c, n))
    for state, g0 in sources.items():
        S.add_edge('S', state, weight=g0)
    for node, extra in targets.items():
        for p in [None] + list(G.predecessors(node)):
            S.add_edge((p, node), 'T', weight=extra)
    try:
        return nx.dijkstra_path_length(S, 'S', 'T')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def rebuilt_total(G, cost, nodes, start_state, sources, targets):
    total = sources[start_state]
    prev = start_state[0]
    for a, b in zip(nodes, nodes[1:]):
        total += cost(a, b, G[a][b]) + turn_penalty_m(G, prev, a, b)
        prev = a
    return total + targets[nodes[-1]]


class TurnAwareSearchTests(unittest.TestCase):

    def test_matches_dijkstra_over_states(self):
        """Optimal for every random scenario (flyovers, roundabouts, blacklist, congestion, incidents, turns)."""
        reachable = 0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                with mock.patch('routing.algorithms.MAJOR_TO_MINOR_TRANSITION_PENALTY_M', 45.0):
                    sc = Scenario(seed)
                    cost = sc.cost_fn()
                    rng = random.Random(seed + 900)
                    nodes = list(sc.G.nodes)
                    sources = {}
                    for n in rng.sample(nodes, 2):
                        sources[(rng.choice([None] + list(sc.G.predecessors(n))), n)] = rng.choice([0.0, 30.0, 120.0])
                    targets = {n: rng.choice([0.0, 25.0, 90.0]) for n in rng.sample(nodes, 2)}

                    expected = state_dijkstra_total(sc.G, cost, sources, targets)
                    try:
                        path, total, start = astar_turns(sc.G, sources, targets, cost, sc.multiplier())
                    except nx.NetworkXNoPath:
                        path = None
                    if expected is None:
                        self.assertIsNone(path)
                        continue
                    reachable += 1
                    self.assertIsNotNone(path)
                    self.assertAlmostEqual(total, expected, delta=1e-6 * max(1.0, expected))
                    self.assertIn(start, sources)
                    self.assertEqual(path[0], start[1])
                    self.assertIn(path[-1], targets)
                    self.assertAlmostEqual(rebuilt_total(sc.G, cost, path, start, sources, targets), total,
                                           delta=1e-6 * max(1.0, total))
        self.assertGreater(reachable, 3)

    def test_prefers_one_turn_over_a_staircase_of_equal_length(self):
        # S(0,0) -> T(200,200): the L-shaped route (via P) has 1 turn, the staircase has 3. Both are 400 m.
        G, ids = named_graph([
            ((0, 0), (200, 0), 'residential', 'L1'), ((200, 0), (200, 200), 'residential', 'L2'),
            ((0, 0), (100, 0), 'residential', 'st'), ((100, 0), (100, 100), 'residential', 'st'),
            ((100, 100), (200, 100), 'residential', 'st'), ((200, 100), (200, 200), 'residential', 'st'),
        ])
        route = astar_path_turns(G, ids[(0, 0)], ids[(200, 200)], length_cost_fn(FakeBlacklist()), 1.0)
        self.assertEqual(route, [ids[(0, 0)], ids[(200, 0)], ids[(200, 200)]])

    def test_unreachable_raises(self):
        G, ids = named_graph([((0, 0), (100, 0), 'residential', 'A'), ((500, 0), (600, 0), 'residential', 'B')])
        with self.assertRaises(nx.NetworkXNoPath):
            astar_path_turns(G, ids[(0, 0)], ids[(600, 0)], length_cost_fn(FakeBlacklist()), 1.0)


# ----------------------------------------------------------------------------------------------- maneuvers

class ManeuverTests(unittest.TestCase):

    def maneuvers(self, *points, roads):
        G, ids = named_graph(roads)
        return generate_route_maneuvers(G, [ids[p] for p in points]), G, ids

    def test_straight_on_the_same_road_is_depart_and_arrive_only(self):
        m, _, _ = self.maneuvers((0, 0), (100, 0), (200, 0), roads=[
            ((0, 0), (100, 0), 'primary', 'Main Rd'), ((100, 0), (200, 0), 'primary', 'Main Rd')])
        self.assertEqual([x['type'] for x in m], ['depart', 'arrive'])
        self.assertAlmostEqual(m[0]['distance_m'], 200.0, delta=0.5)

    def test_left_turn(self):
        m, _, _ = self.maneuvers((0, 0), (200, 0), (200, 200), roads=[
            ((0, 0), (200, 0), 'primary', 'A Road'), ((200, 0), (200, 200), 'primary', 'B Road')])
        self.assertEqual([x['type'] for x in m], ['depart', 'turn_left', 'arrive'])
        self.assertEqual(m[1]['instruction'], 'Turn left onto B Road')
        self.assertAlmostEqual(m[1]['lat'], at(200, 0)[0], places=6)
        self.assertAlmostEqual(m[0]['distance_m'], 200.0, delta=0.5)
        self.assertAlmostEqual(m[1]['distance_m'], 200.0, delta=0.5)

    def test_right_turn(self):
        m, _, _ = self.maneuvers((0, 0), (200, 0), (200, -200), roads=[
            ((0, 0), (200, 0), 'primary', 'A Road'), ((200, 0), (200, -200), 'primary', 'B Road')])
        self.assertEqual([x['type'] for x in m], ['depart', 'turn_right', 'arrive'])

    def test_gentle_bend_is_a_slight_turn(self):
        m, _, _ = self.maneuvers((0, 0), (200, 0), (400, 100), roads=[
            ((0, 0), (200, 0), 'primary', 'A Road'), ((200, 0), (400, 100), 'primary', 'B Road')])
        self.assertEqual([x['type'] for x in m], ['depart', 'slight_left', 'arrive'])

    def test_u_turn(self):
        m, _, _ = self.maneuvers((0, 0), (200, 0), (0, 0), roads=[((0, 0), (200, 0), 'primary', 'A Road')])
        self.assertIn('u_turn', [x['type'] for x in m])

    def test_trivial_routes(self):
        G, ids = named_graph([((0, 0), (100, 0), 'primary', 'A Road')])
        self.assertEqual(generate_route_maneuvers(G, []), [])
        self.assertEqual([x['type'] for x in generate_route_maneuvers(G, [ids[(0, 0)]])], ['arrive'])


class PlannedRouteManeuverTests(unittest.TestCase):

    def plan(self, a, b, **kwargs):
        G, _ = named_graph([
            ((0, 0), (600, 0), 'primary', 'R1 Road'),
            ((600, 0), (600, 600), 'primary', 'R2 Road'),
        ])
        index = RoadIndex.from_graph(G)
        pa, pb = at(*a), at(*b)
        return plan_route(G, manager_for(G), 'dynamic',
                          find_snaps(G, index, pa[0], pa[1], 500), find_snaps(G, index, pb[0], pb[1], 500),
                          blacklist=FakeBlacklist(), **kwargs)

    def test_depart_turn_arrive_with_distances_from_the_snap_points(self):
        plan = self.plan((100, -30), (630, 300))
        m = plan['maneuvers']
        self.assertEqual([x['type'] for x in m], ['depart', 'turn_left', 'arrive'])
        self.assertEqual(m[1]['road_name'], 'R2 Road')
        self.assertAlmostEqual(m[0]['distance_m'], 500.0, delta=2.0)      # from the point on R1 to the junction
        self.assertAlmostEqual(m[1]['distance_m'], 300.0, delta=2.0)      # up R2 to the destination's point
        self.assertAlmostEqual(m[0]['lat'], LAT0, places=6)               # depart is ON the road, not at the pin
        self.assertAlmostEqual(m[0]['lng'], at(100, 0)[1], places=6)
        self.assertAlmostEqual(m[-1]['lng'], at(600, 0)[1], places=6)
        self.assertAlmostEqual(sum(x['distance_m'] for x in m), plan['distance_m'], delta=3.0)

    def test_same_road_trip_is_depart_and_arrive(self):
        plan = self.plan((100, -30), (400, -30))
        self.assertEqual([x['type'] for x in plan['maneuvers']], ['depart', 'arrive'])
        self.assertAlmostEqual(plan['maneuvers'][0]['distance_m'], 300.0, delta=1.0)

    def test_node_based_search_gives_the_same_trip_on_a_simple_map(self):
        a = self.plan((100, -30), (630, 300))
        b = self.plan((100, -30), (630, 300), turn_aware=False)
        self.assertAlmostEqual(a['distance_m'], b['distance_m'], delta=0.5)


if __name__ == '__main__':
    unittest.main()
