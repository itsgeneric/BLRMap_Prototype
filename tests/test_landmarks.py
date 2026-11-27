"""
Tests for routing/landmarks.py: the landmark heuristic must be admissible, consistent and must not change the route found.

Run from the repository root:

    python -m unittest tests.test_landmarks -v
"""
import random
import unittest

import networkx as nx

from routing.algorithms import (
    astar_turns,
    min_cost_multiplier,
    two_wheeler_cost_fn,
)
from routing.landmarks import Landmarks
from tests.test_astar_admissibility import SEEDS, FakeBlacklist, FakeGraphManager, Scenario
from tests.test_turn_routing import rebuilt_total, state_dijkstra_total


def valid_world(seed):
    """A random scenario whose surface/blacklist factors are all >= 1, the condition under which landmarks apply."""
    sc = Scenario(seed)
    rng = random.Random(seed + 7)
    sc.gm = FakeGraphManager(major_nodes=sc.gm.major_nodes, surface={k: max(1.0, v) for k, v in sc.gm.surface_penalties.items()})
    sc.bl = FakeBlacklist({k: max(1.0, v) for k, v in sc.bl.penalties.items()})
    return sc, rng


class LandmarkHeuristicTests(unittest.TestCase):

    def test_bound_is_admissible_and_consistent(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                sc, _ = valid_world(seed)
                cost = sc.cost_fn()                                     # real cost: congestion, incidents, blacklist ...
                lm = Landmarks.build(sc.G, sc.penalties, n_landmarks=4)
                m = min_cost_multiplier(sc.penalties, sc.gm, sc.bl)
                truth = {s: nx.single_source_dijkstra_path_length(sc.G, s, weight=cost) for s in sc.G.nodes}
                for goal in sc.G.nodes:
                    h = lm.heuristic({goal: 0.0}, m, [next(iter(sc.G.nodes))])
                    for s in sc.G.nodes:
                        if goal in truth[s]:
                            self.assertLessEqual(h(s), truth[s][goal] + 1e-6, f"seed={seed} {s}->{goal}")
                    for u, v in {(a, b) for a, b, _ in sc.G.edges(keys=True)}:
                        self.assertLessEqual(h(u), cost(u, v, sc.G[u][v]) + h(v) + 1e-6)

    def test_bound_is_tighter_than_the_plain_one_somewhere(self):
        sc, _ = valid_world(3)
        lm = Landmarks.build(sc.G, sc.penalties, n_landmarks=4)
        m = min_cost_multiplier(sc.penalties, sc.gm, sc.bl)
        goal = list(sc.G.nodes)[-1]
        h = lm.heuristic({goal: 0.0}, m, [list(sc.G.nodes)[0]])
        from routing.algorithms import build_heuristic
        plain = build_heuristic(sc.G, goal, m)
        self.assertTrue(any(h(n) > plain(n) + 1e-6 for n in sc.G.nodes))
        self.assertTrue(all(h(n) >= plain(n) - 1e-6 for n in sc.G.nodes))     # max(), so never looser

    def test_search_result_is_unchanged_with_landmarks(self):
        reachable = 0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                sc, rng = valid_world(seed)
                cost = sc.cost_fn()
                lm = Landmarks.build(sc.G, sc.penalties, n_landmarks=4)
                m = min_cost_multiplier(sc.penalties, sc.gm, sc.bl)
                nodes = list(sc.G.nodes)
                sources = {(None, n): rng.choice([0.0, 30.0]) for n in rng.sample(nodes, 2)}
                targets = {n: rng.choice([0.0, 25.0, 90.0]) for n in rng.sample(nodes, 2)}
                expected = state_dijkstra_total(sc.G, cost, sources, targets)
                try:
                    heuristic = lm.heuristic(targets, m, [k[1] for k in sources])
                    path, total, start = astar_turns(sc.G, sources, targets, cost, m, heuristic=heuristic)
                except nx.NetworkXNoPath:
                    path = None
                if expected is None:
                    self.assertIsNone(path)
                    continue
                reachable += 1
                self.assertAlmostEqual(total, expected, delta=1e-6 * max(1.0, expected))
                self.assertAlmostEqual(rebuilt_total(sc.G, cost, path, start, sources, targets), total,
                                       delta=1e-6 * max(1.0, total))
        self.assertGreater(reachable, 3)


class LandmarkValidityTests(unittest.TestCase):

    def setUp(self):
        self.sc, _ = valid_world(1)
        self.lm = Landmarks.build(self.sc.G, self.sc.penalties, n_landmarks=3)

    def test_valid_for_the_same_table(self):
        self.assertTrue(self.lm.valid_for(self.sc.penalties, self.sc.gm, FakeBlacklist()))

    def test_invalid_for_a_different_cost_table(self):
        other = dict(self.sc.penalties)
        other['primary'] = other['primary'] * 0.5
        self.assertFalse(self.lm.valid_for(other, self.sc.gm, FakeBlacklist()))

    def test_invalid_when_a_surface_factor_is_below_one(self):
        gm = FakeGraphManager(surface={'1_2': 0.8})
        self.assertFalse(self.lm.valid_for(self.sc.penalties, gm, FakeBlacklist()))

    def test_invalid_when_a_blacklist_penalty_is_below_one(self):
        self.assertFalse(self.lm.valid_for(self.sc.penalties, FakeGraphManager(), FakeBlacklist({'1_2': 0.8})))

    def test_blacklist_above_one_is_fine(self):
        self.assertTrue(self.lm.valid_for(self.sc.penalties, FakeGraphManager(), FakeBlacklist({'1_2': 10000.0})))


if __name__ == '__main__':
    unittest.main()
