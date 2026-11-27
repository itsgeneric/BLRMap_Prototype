"""
Tests for the time-based cost model (DYNAMIC_COST_MODEL="time"): cost = length / free-flow speed, so distance still counts
but faster roads are worth a longer drive.

Run from the repository root:

    python -m unittest tests.test_time_cost -v
"""
import math
import unittest

import networkx as nx

from core.config import (
    FREE_FLOW_SPEED_KMH,
    REFERENCE_SPEED_KMH,
    TWO_WHEELER_ROAD_PENALTIES_HIERARCHY,
    TWO_WHEELER_ROAD_PENALTIES_TIME,
)
from routing.algorithms import (
    astar_path_turns,
    build_two_wheeler_penalties,
    min_cost_multiplier,
    two_wheeler_cost_fn,
    two_wheeler_edge_cost,
)
from tests.test_astar_admissibility import FakeBlacklist, FakeGraphManager
from tests.test_turn_routing import named_graph


def time_penalties():
    return dict(TWO_WHEELER_ROAD_PENALTIES_TIME) | {'_roundabout_multiplier': 0.95}


class TimeTableTests(unittest.TestCase):

    def test_multiplier_is_reference_speed_over_speed(self):
        for road_class, speed in FREE_FLOW_SPEED_KMH.items():
            self.assertAlmostEqual(TWO_WHEELER_ROAD_PENALTIES_TIME[road_class], REFERENCE_SPEED_KMH / speed, places=3)

    def test_every_class_has_a_positive_speed_and_both_tables_cover_the_same_classes(self):
        self.assertTrue(all(v > 0 for v in FREE_FLOW_SPEED_KMH.values()))
        self.assertEqual(set(TWO_WHEELER_ROAD_PENALTIES_TIME), set(TWO_WHEELER_ROAD_PENALTIES_HIERARCHY))

    def test_faster_roads_cost_less_per_metre(self):
        t = TWO_WHEELER_ROAD_PENALTIES_TIME
        self.assertLess(t['motorway'], t['trunk'])
        self.assertLess(t['trunk'], t['primary'])
        self.assertLess(t['primary'], t['residential'])

    def test_links_take_their_parent_class(self):
        t = TWO_WHEELER_ROAD_PENALTIES_TIME
        for parent in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary'):
            self.assertEqual(t[parent], t[parent + '_link'])


class TimeModelRoutingTests(unittest.TestCase):

    def edge_cost(self, highway, length=100.0):
        return two_wheeler_edge_cost({'length': length, 'highway': highway}, FakeGraphManager(), time_penalties(), 1, 2,
                                     blacklist=FakeBlacklist())

    def test_edge_cost_is_proportional_to_travel_time(self):
        for road_class in ('trunk', 'primary', 'residential'):
            seconds = 100.0 / (FREE_FLOW_SPEED_KMH[road_class] / 3.6)
            self.assertAlmostEqual(self.edge_cost(road_class) / seconds,
                                   REFERENCE_SPEED_KMH / 3.6, places=2)

    def test_flyover_bonus_is_off_by_default(self):
        """A flyover on a main road must cost the same as the plain road unless FLYOVER_EXCEPTION is switched on."""
        from unittest import mock
        with mock.patch('routing.algorithms.FLYOVER_EXCEPTION_ENABLED', False):
            plain = self.edge_cost('primary')
            bridge = two_wheeler_edge_cost({'length': 100.0, 'highway': 'primary', 'bridge': 'yes'}, FakeGraphManager(),
                                           time_penalties(), 1, 2, blacklist=FakeBlacklist())
        self.assertEqual(plain, bridge)

    def test_flyover_never_makes_a_fast_road_more_expensive(self):
        plain = self.edge_cost('trunk')
        flyover = two_wheeler_edge_cost({'length': 100.0, 'highway': 'trunk', 'bridge': 'yes'}, FakeGraphManager(),
                                        time_penalties(), 1, 2, blacklist=FakeBlacklist())
        self.assertLessEqual(flyover, plain)

    def test_heuristic_bound_is_valid_for_the_time_table(self):
        m = min_cost_multiplier(time_penalties(), FakeGraphManager(), FakeBlacklist())
        self.assertAlmostEqual(m, TWO_WHEELER_ROAD_PENALTIES_TIME['motorway'] * 0.95)      # motorway roundabout
        for value in TWO_WHEELER_ROAD_PENALTIES_TIME.values():
            self.assertGreaterEqual(value, m / 0.95 - 1e-9)

    def test_longer_route_on_a_faster_road_beats_a_shorter_slow_one(self):
        # A -> B directly on a residential road (1000 m, 16.3 km/h = 221 s) or round via a trunk road
        # (2 x 510 m = 1020 m, 28.2 km/h = 130 s): the slightly longer trunk route is much quicker.
        G, ids = named_graph([
            ((0, 0), (1000, 0), 'residential', 'Lane'),
            ((0, 0), (500, 100), 'trunk', 'Ring Road'), ((500, 100), (1000, 0), 'trunk', 'Ring Road'),
        ])
        weight = two_wheeler_cost_fn(FakeGraphManager(), time_penalties(), None, None, FakeBlacklist())
        route = astar_path_turns(G, ids[(0, 0)], ids[(1000, 0)], weight,
                                 min_cost_multiplier(time_penalties(), FakeGraphManager(), FakeBlacklist()))
        self.assertEqual(len(route), 3, "should take the faster, slightly longer trunk detour")

    def test_the_hierarchy_model_would_not_take_the_same_detour(self):
        """Documents the difference: with trunk x3.0 the paper model refuses the faster road."""
        G, ids = named_graph([
            ((0, 0), (1000, 0), 'residential', 'Lane'),
            ((0, 0), (500, 100), 'trunk', 'Ring Road'), ((500, 100), (1000, 0), 'trunk', 'Ring Road'),
        ])
        penalties = build_two_wheeler_penalties() | TWO_WHEELER_ROAD_PENALTIES_HIERARCHY
        weight = two_wheeler_cost_fn(FakeGraphManager(), penalties, None, None, FakeBlacklist())
        route = astar_path_turns(G, ids[(0, 0)], ids[(1000, 0)], weight,
                                 min_cost_multiplier(penalties, FakeGraphManager(), FakeBlacklist()))
        self.assertEqual(len(route), 2)

    def test_slow_road_wins_when_it_is_much_shorter(self):
        # 300 m residential vs a 1400 m trunk loop: distance still matters.
        G, ids = named_graph([
            ((0, 0), (300, 0), 'residential', 'Lane'),
            ((0, 0), (700, 100), 'trunk', 'Ring Road'), ((700, 100), (300, 0), 'trunk', 'Ring Road'),
        ])
        weight = two_wheeler_cost_fn(FakeGraphManager(), time_penalties(), None, None, FakeBlacklist())
        route = astar_path_turns(G, ids[(0, 0)], ids[(300, 0)], weight,
                                 min_cost_multiplier(time_penalties(), FakeGraphManager(), FakeBlacklist()))
        self.assertEqual(len(route), 2)


if __name__ == '__main__':
    unittest.main()
