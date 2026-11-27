"""
Phase 5 tests: A* heuristic correctness and cost consistency (standard-library unittest only).

Run from the repository root:

    python -m unittest discover -s tests -t . -v

Optional check of the real Bengaluru graph (loads the ~130 MB pickle, slow):

    set BLR_REAL_GRAPH=1            (PowerShell: $env:BLR_REAL_GRAPH = "1")
    python -m unittest tests.test_astar_admissibility.RealGraphLengthTests -v

The proofs use small seeded random graphs and compare A* against plain Dijkstra that uses the SAME
cost function. Fake blacklist / graph-manager objects are injected, so the real edge_blacklist.json
and the real graph are never touched.
"""
import os
import pickle
import random
import unittest
from unittest import mock

import networkx as nx

from core.config import GRAPH_PKL_PATH, TWO_WHEELER_ROAD_PENALTIES_HIERARCHY as TWO_WHEELER_ROAD_PENALTIES
from core.config import FLYOVER_MAIN_ROAD_MULTIPLIER
from routing.algorithms import (
    ROUNDABOUT_MULTIPLIER_DEFAULT,
    astar_on_graph,
    build_heuristic,
    build_two_wheeler_penalties,
    collapse_micro_loops,
    haversine_m,
    length_cost_fn,
    min_cost_multiplier,
    two_wheeler_astar,
    two_wheeler_cost_fn,
    two_wheeler_edge_cost,
)


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

HIGHWAYS = [
    'motorway', 'motorway_link', 'trunk', 'primary', 'secondary', 'tertiary', 'tertiary_link',
    'residential', 'living_street', 'unclassified', 'service', 'road',
    'busway',  # deliberately NOT in the penalty table -> exercises the 1.0 default
]


# ---------------------------------------------------------------------------
# Test doubles (same interface as the real EdgeBlacklist / GraphManager)
# ---------------------------------------------------------------------------

class FakeBlacklist:
    def __init__(self, penalties=None):
        self.penalties = dict(penalties or {})

    def get_edge_penalty(self, u, v):
        if f"{u}_{v}" in self.penalties:
            return self.penalties[f"{u}_{v}"]
        if f"{v}_{u}" in self.penalties:
            return self.penalties[f"{v}_{u}"]
        return 1.0

    def min_penalty(self):
        return min(self.penalties.values()) if self.penalties else 1.0


class FakeGraphManager:
    def __init__(self, major_nodes=(), surface=None):
        self.major_nodes = set(major_nodes)
        self.surface_penalties = dict(surface or {})

    def get_surface_penalty(self, u, v):
        return self.surface_penalties.get(f"{u}_{v}", self.surface_penalties.get(f"{v}_{u}", 1.0))


# ---------------------------------------------------------------------------
# Random scenario generator
# ---------------------------------------------------------------------------

def _chord(G, u, v):
    a, b = G.nodes[u], G.nodes[v]
    return haversine_m(a['y'], a['x'], b['y'], b['x'])


def make_graph(rng, n=24, box_deg=0.04, neighbours=3):
    """Random directed multigraph. Every edge length is >= the straight-line distance (as in real OSM data)."""
    G = nx.MultiDiGraph()
    for i in range(n):
        G.add_node(i, y=12.90 + rng.random() * box_deg, x=77.55 + rng.random() * box_deg)

    def add_edge(u, v):
        stretch = rng.choice([0.0, rng.random() * 0.5])  # 0.0 -> length == chord exactly (tightest case)
        attrs = {'length': _chord(G, u, v) * (1.0 + stretch), 'highway': rng.choice(HIGHWAYS)}
        if rng.random() < 0.15:
            attrs['junction'] = 'roundabout'
        if rng.random() < 0.12:
            attrs['bridge'] = 'yes'                      # flyover exception applies on main roads
        G.add_edge(u, v, **attrs)

    for u in range(n):
        nearest = sorted((v for v in range(n) if v != u), key=lambda v: _chord(G, u, v))[:neighbours]
        for v in nearest:
            if rng.random() < 0.9:
                add_edge(u, v)
            if rng.random() < 0.9:
                add_edge(v, u)
    return G


def edge_pairs(G):
    return sorted({(u, v) for u, v, _ in G.edges(keys=True)})


class Scenario:
    """A random graph plus random penalties, surface data, blacklist, congestion and incidents."""

    def __init__(self, seed, n=24, box_deg=0.04):
        rng = random.Random(seed)
        self.rng = rng
        self.G = make_graph(rng, n=n, box_deg=box_deg)
        nodes = list(self.G.nodes)
        pairs = edge_pairs(self.G)

        self.penalties = build_two_wheeler_penalties(
            main_road_penalty=rng.choice([1.0, 1.5]),
            inner_road_multiplier=rng.choice([1.0, 0.9, 0.7]),   # < 1 pushes the class floor below 1
            service_multiplier=rng.choice([1.0, 0.8]),
            roundabout_multiplier=rng.choice([0.95, 0.85]),
        )
        surface = {f"{u}_{v}": rng.choice([0.8, 1.0, 2.0, 3.0]) for u, v in rng.sample(pairs, 6)}
        self.gm = FakeGraphManager(
            major_nodes=rng.sample(nodes, int(n * 0.4)),
            surface=surface,
        )
        # Includes values BELOW 1 so the bound has to cope with a "discount" entry.
        self.bl = FakeBlacklist({f"{u}_{v}": rng.choice([0.8, 2.0, 10000.0]) for u, v in rng.sample(pairs, 6)})
        self.congested = set(rng.sample(nodes, 3))
        self.incidents = {node: rng.choice([1.2, 2.0, 15.0, 50.0]) for node in rng.sample(nodes, 3)}

    def cost_fn(self):
        return two_wheeler_cost_fn(self.gm, self.penalties, self.congested, self.incidents, self.bl)

    def multiplier(self):
        return min_cost_multiplier(self.penalties, self.gm, self.bl)


def true_costs(G, cost):
    """Exact cheapest cost between every reachable ordered pair, by Dijkstra on the same cost function."""
    return {s: nx.single_source_dijkstra_path_length(G, s, weight=cost) for s in G.nodes}


def path_cost(G, path, cost):
    return sum(cost(a, b, G[a][b]) for a, b in zip(path, path[1:]))


SEEDS = range(12)


# ---------------------------------------------------------------------------
# Heuristic / A* proofs
# ---------------------------------------------------------------------------

class AStarAdmissibilityTests(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch('routing.algorithms.MAJOR_TO_MINOR_TRANSITION_PENALTY_M', 45.0)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_heuristic_is_admissible(self):
        """h(n, goal) <= the true cheapest remaining cost, for every node and goal (checked against Dijkstra)."""
        checked = 0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                sc = Scenario(seed)
                cost, m = sc.cost_fn(), sc.multiplier()
                self.assertGreater(m, 0.0)
                truth = true_costs(sc.G, cost)
                for goal in sc.G.nodes:
                    h = build_heuristic(sc.G, goal, m)
                    for s in sc.G.nodes:
                        if goal in truth[s]:
                            self.assertLessEqual(
                                h(s), truth[s][goal] * (1 + 1e-12) + 1e-9,
                                f"seed={seed} {s}->{goal}: h={h(s)} > true={truth[s][goal]}",
                            )
                            checked += 1
        self.assertGreater(checked, 1000)  # make sure the loop really exercised many pairs

    def test_heuristic_is_consistent(self):
        """h(u) <= cost(u, v) + h(v) for every edge and every goal."""
        for seed in SEEDS:
            with self.subTest(seed=seed):
                sc = Scenario(seed)
                cost, m = sc.cost_fn(), sc.multiplier()
                for goal in sc.G.nodes:
                    h = build_heuristic(sc.G, goal, m)
                    for u, v in edge_pairs(sc.G):
                        self.assertLessEqual(
                            h(u), cost(u, v, sc.G[u][v]) + h(v) + 1e-9,
                            f"seed={seed} edge {u}->{v} goal {goal}",
                        )

    def test_two_wheeler_astar_matches_dijkstra(self):
        """The A* path costs exactly what Dijkstra says is cheapest, for every reachable pair."""
        pairs_checked = 0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                sc = Scenario(seed)
                cost = sc.cost_fn()
                truth = true_costs(sc.G, cost)
                for s in sc.G.nodes:
                    for g, best in truth[s].items():
                        if s == g:
                            continue
                        path = two_wheeler_astar(
                            sc.G, s, g, sc.gm, penalties=sc.penalties,
                            congested_nodes=sc.congested, incident_nodes=sc.incidents, blacklist=sc.bl,
                        )
                        self.assertEqual((path[0], path[-1]), (s, g))
                        self.assertAlmostEqual(path_cost(sc.G, path, cost), best, delta=1e-6 * max(1.0, best),
                                               msg=f"seed={seed} {s}->{g}")
                        pairs_checked += 1
        self.assertGreater(pairs_checked, 1000)

    def test_route_mode_astar_matches_dijkstra_with_blacklist(self):
        """/route (distance x blacklist) stays optimal, including a blacklist entry below 1.0."""
        for seed in SEEDS:
            with self.subTest(seed=seed):
                sc = Scenario(seed)
                cost = length_cost_fn(sc.bl)
                truth = true_costs(sc.G, cost)
                for s in sc.G.nodes:
                    for g, best in truth[s].items():
                        if s == g:
                            continue
                        path = astar_on_graph(sc.G, s, g, blacklist=sc.bl)
                        self.assertAlmostEqual(path_cost(sc.G, path, cost), best, delta=1e-6 * max(1.0, best),
                                               msg=f"seed={seed} {s}->{g}")

    def test_legacy_division_heuristic_was_inadmissible(self):
        """Documents the bug: the old h = haversine / 0.85 overestimates; the new bound does not."""
        G = nx.MultiDiGraph()
        for i, lat in enumerate([12.90, 12.91, 12.92]):      # three points on one meridian
            G.add_node(i, y=lat, x=77.60)
        for a, b in [(0, 1), (1, 2), (1, 0), (2, 1)]:
            G.add_edge(a, b, length=_chord(G, a, b), highway='residential')   # residential multiplier is 1.0

        gm, bl = FakeGraphManager(), FakeBlacklist()
        cost = two_wheeler_cost_fn(gm, None, None, None, bl)
        true = path_cost(G, [0, 1, 2], cost)
        straight = _chord(G, 0, 2)

        legacy_h = straight / 0.85
        self.assertGreater(legacy_h, true * 1.1, "legacy heuristic should overestimate by ~17.6%")

        new_h = build_heuristic(G, 2, min_cost_multiplier(None, gm, bl))(0)
        self.assertLessEqual(new_h, true)
        self.assertEqual(two_wheeler_astar(G, 0, 2, gm, blacklist=bl), [0, 1, 2])


class MultiplierBoundTests(unittest.TestCase):

    def test_default_bound_is_a_roundabout_on_a_flyover(self):
        m = min_cost_multiplier(build_two_wheeler_penalties(), FakeGraphManager(), FakeBlacklist())
        # cheapest possible edge: a main-road flyover (0.8, cheaper than service 0.9) that is also a roundabout (0.95)
        self.assertAlmostEqual(m, FLYOVER_MAIN_ROAD_MULTIPLIER * ROUNDABOUT_MULTIPLIER_DEFAULT)   # 0.76

    def test_bound_follows_the_penalty_table(self):
        pen = build_two_wheeler_penalties(inner_road_multiplier=0.7)      # service 0.9 * 0.7 = 0.63 now undercuts the flyover 0.8
        m = min_cost_multiplier(pen, FakeGraphManager(), FakeBlacklist())
        cheapest = min([1.0, FLYOVER_MAIN_ROAD_MULTIPLIER] + [v for k, v in pen.items() if not k.startswith('_')])
        self.assertAlmostEqual(cheapest, 0.9 * 0.7)
        self.assertAlmostEqual(m, cheapest * ROUNDABOUT_MULTIPLIER_DEFAULT)

    def test_bound_includes_surface_and_blacklist_discounts(self):
        gm = FakeGraphManager(surface={'1_2': 0.5})
        bl = FakeBlacklist({'3_4': 0.8})
        m = min_cost_multiplier(build_two_wheeler_penalties(), gm, bl)
        self.assertAlmostEqual(m, FLYOVER_MAIN_ROAD_MULTIPLIER * ROUNDABOUT_MULTIPLIER_DEFAULT * 0.5 * 0.8)

    def test_bound_ignores_penalties_that_only_raise_cost(self):
        bl = FakeBlacklist({'1_2': 10000.0})
        m = min_cost_multiplier(build_two_wheeler_penalties(), FakeGraphManager(surface={'1_2': 3.0}), bl)
        self.assertAlmostEqual(m, FLYOVER_MAIN_ROAD_MULTIPLIER * ROUNDABOUT_MULTIPLIER_DEFAULT)

    def test_non_positive_multiplier_is_rejected(self):
        with self.assertRaises(ValueError):
            min_cost_multiplier({'primary': 0.0}, FakeGraphManager(), FakeBlacklist())
        with self.assertRaises(ValueError):
            min_cost_multiplier(build_two_wheeler_penalties(), FakeGraphManager(surface={'1_2': -1.0}), FakeBlacklist())
        with self.assertRaises(ValueError):
            min_cost_multiplier(build_two_wheeler_penalties(), FakeGraphManager(), FakeBlacklist({'1_2': 0.0}))


class EdgeCostConsistencyTests(unittest.TestCase):

    @mock.patch('routing.algorithms.MAJOR_TO_MINOR_TRANSITION_PENALTY_M', 45.0)
    def test_blacklist_still_applies_on_major_to_minor_edge(self):
        """Regression: the old early `return` skipped the blacklist on major -> minor edges."""
        edge = {'length': 100.0, 'highway': 'residential'}
        gm = FakeGraphManager(major_nodes={1})
        bl = FakeBlacklist({'1_2': 10.0})
        cost = two_wheeler_edge_cost(edge, gm, None, 1, 2, blacklist=bl)
        expected = 100.0 * TWO_WHEELER_ROAD_PENALTIES['residential'] * 10.0 + 45.0
        self.assertAlmostEqual(cost, expected)

    @mock.patch('routing.algorithms.MAJOR_TO_MINOR_TRANSITION_PENALTY_M', 45.0)
    def test_roundabout_and_surface_still_apply_on_major_to_minor_edge(self):
        edge = {'length': 100.0, 'highway': 'residential', 'junction': 'roundabout'}
        gm = FakeGraphManager(major_nodes={1}, surface={'1_2': 2.0})
        cost = two_wheeler_edge_cost(edge, gm, None, 1, 2, blacklist=FakeBlacklist())
        expected = 100.0 * TWO_WHEELER_ROAD_PENALTIES['residential'] * ROUNDABOUT_MULTIPLIER_DEFAULT * 2.0 \
            + 45.0
        self.assertAlmostEqual(cost, expected)

    @mock.patch('routing.algorithms.MAJOR_TO_MINOR_TRANSITION_PENALTY_M', 45.0)
    def test_transition_penalty_only_for_major_to_minor(self):
        edge = {'length': 100.0, 'highway': 'residential'}
        base = 100.0 * TWO_WHEELER_ROAD_PENALTIES['residential']
        bl = FakeBlacklist()
        self.assertAlmostEqual(two_wheeler_edge_cost(edge, FakeGraphManager(major_nodes={1}), None, 1, 2, blacklist=bl),
                               base + 45.0)
        self.assertAlmostEqual(two_wheeler_edge_cost(edge, FakeGraphManager(major_nodes={1, 2}), None, 1, 2, blacklist=bl), base)
        self.assertAlmostEqual(two_wheeler_edge_cost(edge, FakeGraphManager(major_nodes={9}), None, 1, 2, blacklist=bl), base)

    def test_every_edge_cost_is_positive(self):
        for seed in SEEDS:
            sc = Scenario(seed)
            cost = sc.cost_fn()
            for u, v in edge_pairs(sc.G):
                self.assertGreater(cost(u, v, sc.G[u][v]), 0.0)


# ---------------------------------------------------------------------------
# collapse_micro_loops
# ---------------------------------------------------------------------------

def box_loop_graph():
    """Chain 0->1->2->3->4 (70 m each, 280 m total) plus a direct 0->4 edge of 100 m."""
    G = nx.MultiDiGraph()
    for i in range(5):
        G.add_node(i, y=12.9, x=77.6)
    for a in range(4):
        G.add_edge(a, a + 1, length=70.0, highway='primary')
    G.add_edge(0, 4, length=100.0, highway='primary')
    return G


class CollapseMicroLoopsTests(unittest.TestCase):

    def test_legacy_length_mode_takes_the_shortcut(self):
        self.assertEqual(collapse_micro_loops([0, 1, 2, 3, 4], box_loop_graph()), [0, 4])

    def test_cost_mode_takes_the_shortcut_when_it_is_cheaper(self):
        G = box_loop_graph()
        out = collapse_micro_loops([0, 1, 2, 3, 4], G, cost_fn=length_cost_fn(FakeBlacklist()))
        self.assertEqual(out, [0, 4])

    def test_cost_mode_refuses_a_blacklisted_shortcut(self):
        """The old length-only code would re-introduce the blacklisted 0->4 edge A* just avoided."""
        G = box_loop_graph()
        bl = FakeBlacklist({'0_4': 10000.0})
        self.assertEqual(collapse_micro_loops([0, 1, 2, 3, 4], G), [0, 4])                       # legacy: ignores blacklist
        self.assertEqual(collapse_micro_loops([0, 1, 2, 3, 4], G, cost_fn=length_cost_fn(bl)), [0, 1, 2, 3, 4])

    def test_loop_back_to_same_node_does_not_duplicate_it(self):
        """A route that returns to a node it already visited must not list that node twice in a row."""
        G = nx.MultiDiGraph()
        for i in range(3):
            G.add_node(i, y=12.9, x=77.6)
        for a, b in [(0, 1), (1, 2), (2, 0)]:
            G.add_edge(a, b, length=70.0, highway='primary')
        for cost_fn in (None, length_cost_fn(FakeBlacklist())):
            self.assertEqual(collapse_micro_loops([0, 1, 2, 0], G, cost_fn=cost_fn), [0])

    def test_collapse_never_increases_cost_and_stays_a_valid_path(self):
        for seed in range(15):
            with self.subTest(seed=seed):
                sc = Scenario(seed, n=18, box_deg=0.002)       # compact graph so loops fit inside max_detour_m
                cost = sc.cost_fn()
                rng = random.Random(1000 + seed)
                for _ in range(25):
                    node = rng.choice(list(sc.G.nodes))
                    walk = [node]
                    for _ in range(8):
                        successors = list(sc.G.successors(walk[-1]))
                        if not successors:
                            break
                        walk.append(rng.choice(successors))
                    if len(walk) < 4:
                        continue
                    out = collapse_micro_loops(walk, sc.G, cost_fn=cost)
                    self.assertEqual((out[0], out[-1]), (walk[0], walk[-1]))
                    for a, b in zip(out, out[1:]):
                        self.assertIn(b, sc.G[a], f"collapsed route uses missing edge {a}->{b}")
                    self.assertLessEqual(path_cost(sc.G, out, cost), path_cost(sc.G, walk, cost) + 1e-9)


# ---------------------------------------------------------------------------
# Optional: the real graph must satisfy the assumption "length >= straight-line distance"
# ---------------------------------------------------------------------------

@unittest.skipUnless(
    os.environ.get('BLR_REAL_GRAPH') == '1' and os.path.exists(GRAPH_PKL_PATH),
    'set BLR_REAL_GRAPH=1 (and have Data Assets/bengaluru_graph.pkl) to check the real graph',
)
class RealGraphLengthTests(unittest.TestCase):

    def test_no_edge_is_shorter_than_its_chord(self):
        """
        The admissibility proof needs length >= haversine(u, v) on every edge. A 1 cm allowance covers the
        rounding OSMnx applies to stored lengths; it is a data tolerance, not a heuristic margin.
        """
        with open(GRAPH_PKL_PATH, 'rb') as f:
            data = pickle.load(f)
        G = data['G'] if isinstance(data, dict) else data
        violations, total = [], 0
        for u, v, d in G.edges(data=True):
            total += 1
            length = float(d.get('length', 1.0))
            chord = _chord(G, u, v)
            if length < chord - 0.01:
                violations.append((u, v, round(length, 3), round(chord, 3), d.get('highway')))
        print(f"\n[real graph] {total:,} edges checked, {len(violations):,} shorter than their chord")
        self.assertEqual(violations, [], f"first violations (u, v, length, chord, highway): {violations[:10]}")


if __name__ == '__main__':
    unittest.main()
