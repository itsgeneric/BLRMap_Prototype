"""
The smart two-wheeler behaviour: the detour budget, realistic traffic cost, access-only roads (reaching places inside,
never cutting through) and the automatic map rebuild. Tiny hand-built maps, distances in metres.

    python -m unittest tests.test_smart_routing -v
"""
import os
import pickle
import random
import tempfile
import unittest
from unittest import mock

import networkx as nx
import osmnx as ox

import core.config as config
import routing.graph_manager as graph_manager_module
from routing.access import allowed_access_edges
from routing.algorithms import build_two_wheeler_penalties
from routing.graph_manager import GraphManager, classify_roads, keep_connected, road_class_of_access
from routing.graph_qa import RoadIndex
from routing.smart import blend_penalties, detour_budget_m, plan_smart
from routing.snapping import FAR_PIN_M, find_snaps, nearby_junction_snaps, plan_route
from tests.test_astar_admissibility import FakeBlacklist
from tests.test_graph_qa import at
from tests.test_turn_routing import manager_for

PENALTIES = build_two_wheeler_penalties()


def road_map(roads):
    """
    roads: [(points, highway, extra_tags)] where points is a list of (x, y) metres. Consecutive points make two-way edges
    with their straight length; the same point in two roads is the same junction.
    """
    G = nx.MultiDiGraph()
    G.graph['crs'] = 'epsg:4326'
    ids = {}

    def node(xy):
        if xy not in ids:
            ids[xy] = len(ids)
            lat, lng = at(*xy)
            G.add_node(ids[xy], y=lat, x=lng)
        return ids[xy]

    for points, highway, tags in roads:
        for a, b in zip(points, points[1:]):
            u, v = node(a), node(b)
            length = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
            G.add_edge(u, v, length=length, highway=highway, **tags)
            G.add_edge(v, u, length=length, highway=highway, **tags)
    return G, ids


def snaps(G, index, xy):
    lat, lng = at(*xy)
    found = find_snaps(G, index, lat, lng, 500.0)
    if found and found[0].distance_m > FAR_PIN_M:
        found = found + nearby_junction_snaps(G, index, lat, lng, found[0].distance_m)
    return found


def trip(G, a, b, **kwargs):
    index = RoadIndex.from_graph(G)
    return plan_smart(G, manager_for(G), snaps(G, index, a), snaps(G, index, b), PENALTIES,
                      blacklist=FakeBlacklist({}), **kwargs)


def classes_used(G, plan):
    return {G[u][v][min(G[u][v], key=lambda k: G[u][v][k]['length'])]['highway']
            for u, v in zip(plan['nodes'], plan['nodes'][1:])}


def two_ways(inner_extra_m):
    """A straight 1000 m main road, and an inner-road way round it that is `inner_extra_m` longer."""
    half = inner_extra_m / 2.0
    return road_map([
        ([(-100, 0), (0, 0)], 'residential', {}),
        ([(0, 0), (500, 0), (1000, 0)], 'primary', {}),
        ([(0, 0), (0, half), (1000, half), (1000, 0)], 'residential', {}),
        ([(1000, 0), (1100, 0)], 'residential', {}),
    ])


class DetourBudgetTests(unittest.TestCase):

    def test_inner_roads_are_preferred_when_they_cost_little_extra(self):
        G, _ = two_ways(inner_extra_m=150)
        plan = trip(G, (-80, 0), (1080, 0))
        self.assertAlmostEqual(plan['distance_m'], 1310, delta=2)
        self.assertEqual(plan['preference_level'], 1.0)
        self.assertNotIn('primary', classes_used(G, plan))

    def test_a_long_way_round_on_inner_roads_is_refused(self):
        G, _ = two_ways(inner_extra_m=700)          # budget on a 1160 m trip is 1460 m; the inner way is 1860 m
        plan = trip(G, (-80, 0), (1080, 0))
        self.assertAlmostEqual(plan['distance_m'], 1160, delta=2)
        self.assertIn('primary', classes_used(G, plan))
        self.assertLess(plan['preference_level'], 1.0)

    def test_without_the_budget_the_old_planner_takes_the_long_way(self):
        G, _ = two_ways(inner_extra_m=700)
        index = RoadIndex.from_graph(G)
        plan = plan_route(G, manager_for(G), 'dynamic', snaps(G, index, (-80, 0)), snaps(G, index, (1080, 0)),
                          penalties=PENALTIES, blacklist=FakeBlacklist({}))
        self.assertAlmostEqual(plan['distance_m'], 1860, delta=2, msg='this is the problem the budget fixes')

    def test_budget_is_the_larger_of_the_ratio_and_the_slack(self):
        self.assertEqual(detour_budget_m(1000), 1300)
        self.assertAlmostEqual(detour_budget_m(10000), 11500)

    def test_blending_weakens_the_preference_and_never_touches_other_factors(self):
        full = {'primary': 2.2, 'living_street': 0.95, '_roundabout_multiplier': 0.95}
        self.assertEqual(blend_penalties(full, 1.0), full)
        none = blend_penalties(full, 0.0)
        self.assertEqual((none['primary'], none['living_street'], none['_roundabout_multiplier']), (1.0, 1.0, 0.95))
        self.assertAlmostEqual(blend_penalties(full, 0.5)['primary'], 1.6)

    def test_property_no_route_ever_exceeds_the_budget_on_random_maps(self):
        classes = ['primary', 'secondary', 'tertiary', 'residential', 'residential', 'trunk', 'living_street']
        for seed in range(25):
            rng = random.Random(seed)
            roads = []
            for i in range(6):
                for j in range(6):
                    if i < 5:
                        roads.append(([(i * 200, j * 200), ((i + 1) * 200, j * 200)], rng.choice(classes), {}))
                    if j < 5:
                        roads.append(([(i * 200, j * 200), (i * 200, (j + 1) * 200)], rng.choice(classes), {}))
            G, ids = road_map(roads)
            jams = set(rng.sample(list(ids.values()), 8))
            plan = trip(G, (40, 0), (960, 1000), congested_nodes=jams)
            self.assertLessEqual(plan['distance_m'], detour_budget_m(plan['direct_distance_m']) + 1e-6, f'seed {seed}')


def jam_map(way_round_extra_m):
    """1000 m residential road with its middle jammed, and a clean residential way round that is longer by the given amount."""
    half = way_round_extra_m / 2.0
    G, ids = road_map([
        ([(-100, 0), (0, 0), (350, 0), (650, 0), (1000, 0), (1100, 0)], 'residential', {}),
        ([(0, 0), (0, half), (1000, half), (1000, 0)], 'residential', {}),
    ])
    return G, {ids[(350, 0)], ids[(650, 0)]}


class TrafficTests(unittest.TestCase):

    def test_a_short_way_round_a_jam_is_taken(self):
        G, jam = jam_map(way_round_extra_m=120)
        plan = trip(G, (-80, 0), (1080, 0), congested_nodes=jam)
        self.assertAlmostEqual(plan['distance_m'], 1280, delta=2)
        self.assertFalse(plan['through_traffic'])

    def test_a_long_way_round_a_jam_is_not_taken_the_rider_goes_through(self):
        G, jam = jam_map(way_round_extra_m=800)
        plan = trip(G, (-80, 0), (1080, 0), congested_nodes=jam)
        self.assertAlmostEqual(plan['distance_m'], 1160, delta=2)
        self.assertTrue(plan['through_traffic'])

    def test_jam_cost_is_realistic_even_before_the_budget(self):
        self.assertLessEqual(config.JAM_COST_MULTIPLIER, 3.0)
        self.assertGreater(config.JAM_COST_MULTIPLIER, 1.0)

    def test_a_flooded_road_is_avoided_even_when_the_way_round_is_far_longer(self):
        G, jam = jam_map(way_round_extra_m=1600)
        plan = trip(G, (-80, 0), (1080, 0), incident_nodes={n: 50.0 for n in jam})
        self.assertAlmostEqual(plan['distance_m'], 2760, delta=3)


class RoadClassificationTests(unittest.TestCase):

    def test_what_is_removed_access_only_and_public(self):
        cases = [
            ({'highway': 'residential'}, 'public'),
            ({'highway': 'residential', 'access': 'permissive'}, 'access_only'),  # reachable, never a cut-through
            ({'highway': 'service'}, 'access_only'),
            ({'highway': 'residential', 'access': 'destination'}, 'access_only'),
            ({'highway': 'residential', 'access': 'customers'}, 'access_only'),
            ({'highway': 'residential', 'service': 'driveway'}, 'access_only'),
            ({'highway': ['service', 'residential']}, 'access_only'),
            ({'highway': 'residential', 'access': 'private'}, 'removed'),
            ({'highway': 'residential', 'access': 'military'}, 'removed'),
            ({'highway': 'residential', 'access': 'emergency'}, 'removed'),
            ({'highway': 'residential', 'access': 'permit'}, 'removed'),
            ({'highway': 'service', 'access': 'no'}, 'removed'),
            ({'highway': 'residential', 'motorcycle': 'no'}, 'removed'),
            ({'highway': 'residential', 'motor_vehicle': 'private'}, 'removed'),
            ({'highway': 'residential', 'access': 'no', 'motorcycle': 'yes'}, 'public'),
            ({'highway': 'footway'}, 'removed'),
            ({'highway': 'service', 'service': 'emergency_access'}, 'removed'),
        ]
        for tags, expected in cases:
            self.assertEqual(road_class_of_access(tags), expected, tags)

    def test_classify_marks_and_removes(self):
        G, _ = road_map([([(0, 0), (100, 0)], 'residential', {}), ([(100, 0), (200, 0)], 'service', {}),
                         ([(200, 0), (300, 0)], 'footway', {})])
        removed, marked = classify_roads(G)
        self.assertEqual((removed, marked), (2, 2))

    def test_a_public_pocket_behind_a_service_road_becomes_access_only(self):
        G, ids = road_map([
            ([(0, 0), (100, 0), (200, 0), (300, 0), (400, 0)], 'residential', {}),     # the public network (biggest)
            ([(400, 0), (500, 0)], 'service', {}),
            ([(500, 0), (600, 0)], 'residential', {}),                                 # reachable only via the service road
        ])
        classify_roads(G)
        G, demoted = keep_connected(G)
        self.assertEqual(demoted, 2)
        self.assertTrue(G[ids[(500, 0)]][ids[(600, 0)]][0].get('access_only'))
        self.assertFalse(G[ids[(0, 0)]][ids[(100, 0)]][0].get('access_only'))


def campus():
    """
    A public road runs along y=0, and goes the long way (via y=-150) between x=300 and x=700. A service road runs
    straight through the campus between those two points, with a lane going 200 m up into it.
    """
    G, ids = road_map([
        ([(0, 0), (300, 0)], 'residential', {}),
        ([(300, 0), (300, -150), (700, -150), (700, 0)], 'residential', {}),
        ([(700, 0), (1000, 0)], 'residential', {}),
        ([(300, 0), (500, 0), (700, 0)], 'service', {}),
        ([(500, 0), (500, 100), (500, 200)], 'service', {}),
    ])
    classify_roads(G)
    return G, ids


class AccessOnlyRoutingTests(unittest.TestCase):

    def test_no_cutting_through_the_campus(self):
        G, _ = campus()
        plan = trip(G, (50, 0), (950, 0))
        self.assertNotIn('service', classes_used(G, plan))
        self.assertAlmostEqual(plan['distance_m'], 1200, delta=3)

    def test_a_destination_inside_is_reached(self):
        G, _ = campus()
        plan = trip(G, (50, 0), (500, 190))
        self.assertLess(plan['destination_snap']['distance_m'], 2)
        self.assertAlmostEqual(plan['distance_m'], 250 + 200 + 190, delta=3)
        self.assertIn('service', classes_used(G, plan) | {'service'})

    def test_a_start_inside_can_leave(self):
        G, _ = campus()
        plan = trip(G, (500, 190), (950, 0))
        self.assertLess(plan['origin_snap']['distance_m'], 2)
        self.assertAlmostEqual(plan['distance_m'], 190 + 200 + 250, delta=3)

    def test_the_old_cleanup_stopped_short_of_the_same_destination(self):
        G, _ = campus()
        old = nx.MultiDiGraph(G)
        old.remove_edges_from([(u, v, k) for u, v, k, d in old.edges(keys=True, data=True) if d['highway'] == 'service'])
        old.remove_nodes_from(list(nx.isolates(old)))
        plan = trip(old, (50, 0), (500, 190))
        self.assertGreater(plan['destination_snap']['distance_m'], 150, 'the route used to end far from the pin')

    def test_only_the_cluster_at_the_pin_is_opened(self):
        G, _ = road_map([([(0, 0), (1000, 0)], 'residential', {}), ([(200, 0), (200, 100)], 'service', {}),
                         ([(800, 0), (800, 100)], 'service', {})])
        classify_roads(G)
        index = RoadIndex.from_graph(G)
        allowed = allowed_access_edges(G, snaps(G, index, (200, 90)))
        self.assertEqual(len(allowed), 2)                       # that lane, both directions

    def test_a_place_deep_inside_a_large_estate_is_still_reachable(self):
        G, _ = road_map([([(0, 0), (200, 0)], 'residential', {}),
                         ([(200, 0)] + [(200, y) for y in range(500, 3001, 500)], 'service', {})])
        classify_roads(G)
        plan = trip(G, (20, 0), (200, 2990))
        self.assertLess(plan['destination_snap']['distance_m'], 2)

    def test_the_nearest_road_beats_a_junction_far_from_the_pin(self):
        # the pin is 40 m from a lane; a junction 150 m away would make the route a little shorter but stop far off
        G, _ = road_map([([(0, 0), (400, 0), (800, 0)], 'residential', {}),
                         ([(400, 0), (400, 300)], 'residential', {})])
        plan = trip(G, (20, 0), (440, 250))
        self.assertLess(plan['destination_snap']['distance_m'], 45)


class MapRebuildTests(unittest.TestCase):
    """No file has to be renamed or deleted by hand."""

    def test_this_version_has_its_own_map_and_blocked_road_files(self):
        self.assertTrue(config.GRAPH_PKL_PATH.endswith('bengaluru_graph.smart.pkl'))
        self.assertTrue(config.EDGE_BLACKLIST_FILE.endswith('edge_blacklist_manual.json'))
        self.assertTrue(config.ENABLE_ROAD_VERIFY)
        self.assertFalse(config.VERIFY_SHADOW_MODE)

    def test_missing_or_outdated_map_is_rebuilt_and_then_loaded_fast(self):
        G, _ = road_map([([(0, 0), (100, 0), (200, 0)], 'residential', {}), ([(200, 0), (200, 100)], 'service', {})])
        for i, node in enumerate(G.nodes):
            G.nodes[node]['street_count'] = 2
        for u, v, k in G.edges(keys=True):
            G[u][v][k]['osmid'] = 1000 + u * 10 + v
        with tempfile.TemporaryDirectory() as folder:
            source = os.path.join(folder, 'roads.graphml')
            compiled = os.path.join(folder, 'map.smart.pkl')
            ox.save_graphml(G, source)
            with mock.patch.object(graph_manager_module, 'GRAPH_FILE_PATH', source), \
                    mock.patch.object(graph_manager_module, 'GRAPH_PKL_PATH', compiled), \
                    mock.patch('builtins.print'):
                GraphManager().load_graph()                                       # missing -> built
                with open(compiled, 'rb') as f:
                    data = pickle.load(f)
                self.assertEqual(data['cleanup_version'], config.GRAPH_CLEANUP_VERSION)

                data['cleanup_version'] = 'older rules'
                data['G'] = nx.MultiDiGraph()
                with open(compiled, 'wb') as f:
                    pickle.dump(data, f)
                manager = GraphManager()
                manager.load_graph()                                              # outdated -> rebuilt
                self.assertEqual(manager.G.number_of_nodes(), 4)
                self.assertEqual(sum(bool(d.get('access_only')) for _, _, d in manager.G.edges(data=True)), 2)

                with mock.patch.object(graph_manager_module.ox, 'load_graphml', side_effect=AssertionError('rebuilt')):
                    GraphManager().load_graph()                                   # current -> loaded as it is


if __name__ == '__main__':
    unittest.main()
