"""
Tests for routing/graph_qa.py (the road coverage matcher behind the /qa page and graph_qa_benchmark).

Run from the repository root:

    python -m unittest tests.test_graph_qa -v

All graphs are tiny hand-built layouts around 12.97 N, 77.59 E, with distances given in metres.
"""
import math
import unittest

import networkx as nx
import numpy as np

from routing.graph_qa import COVERED, MISSING, RoadIndex, angular_difference, edge_class_group, fill_short_gaps

LAT0, LNG0 = 12.97, 77.59
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 110574.0


def at(dx, dy):
    """(lat, lng) of the point dx metres east and dy metres north of the origin."""
    return (LAT0 + dy / KY, LNG0 + dx / KX)


def build_graph(roads):
    """roads: list of (from_xy, to_xy, highway, two_way). Nodes are created per distinct end point."""
    G = nx.MultiDiGraph()
    ids = {}

    def node(xy):
        if xy not in ids:
            ids[xy] = len(ids)
            lat, lng = at(*xy)
            G.add_node(ids[xy], y=lat, x=lng)
        return ids[xy]

    for a, b, highway, two_way in roads:
        u, v = node(a), node(b)
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        G.add_edge(u, v, length=length, highway=highway)
        if two_way:
            G.add_edge(v, u, length=length, highway=highway)
    return G


def route(*points):
    return [list(at(*p)) for p in points]


class FillShortGapsTests(unittest.TestCase):

    def test_short_gap_is_forgiven_and_long_gap_is_kept(self):
        s = np.array([0, 0, 2, 2, 0, 0], dtype=np.int8)                  # 20 m gap at 10 m spacing
        self.assertTrue((fill_short_gaps(s, 10.0, 30.0) == COVERED).all())
        s = np.array([0, 2, 2, 2, 2, 0], dtype=np.int8)                  # 40 m gap
        self.assertEqual(list(fill_short_gaps(s, 10.0, 30.0)), [0, 2, 2, 2, 2, 0])

    def test_input_is_not_modified(self):
        s = np.array([0, 2, 0], dtype=np.int8)
        fill_short_gaps(s, 10.0, 30.0)
        self.assertEqual(list(s), [0, 2, 0])


class HelperTests(unittest.TestCase):

    def test_angular_difference_wraps_around_north(self):
        self.assertAlmostEqual(float(angular_difference(np.array(350.0), 10.0)), 20.0)
        self.assertAlmostEqual(float(angular_difference(np.array(0.0), 180.0)), 180.0)
        self.assertAlmostEqual(float(angular_difference(np.array(90.0), 90.0)), 0.0)

    def test_road_class_grouping(self):
        self.assertEqual(edge_class_group('primary_link'), 'primary')
        self.assertEqual(edge_class_group(['Residential', 'service']), 'residential')
        self.assertEqual(edge_class_group(None), 'unclassified')


class CoverageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Road 1: 600 m east-west, two-way, primary.   Road 2: 600 m south->north, ONE-WAY, residential, 1 km east.
        cls.index = RoadIndex.from_graph(build_graph([
            ((0, 0), (600, 0), 'primary', True),
            ((1000, -300), (1000, 300), 'residential', False),
        ]))

    def test_following_a_two_way_road_is_covered_in_both_directions(self):
        for pts in ((( 0, 0), (600, 0)), ((600, 0), (0, 0))):
            rep = self.index.match_polyline(route(*pts))
            self.assertGreater(rep['covered_pct'], 98.0)
            self.assertEqual(rep['missing_m'], 0.0)
            self.assertEqual(rep['wrong_direction_m'], 0.0)
            self.assertGreater(rep['class_metres']['primary'], 580.0)

    def test_following_a_one_way_road_with_traffic_is_covered(self):
        rep = self.index.match_polyline(route((1000, -300), (1000, 300)))
        self.assertGreater(rep['covered_pct'], 98.0)
        self.assertGreater(rep['class_metres']['residential'], 580.0)

    def test_driving_against_a_one_way_road_is_reported_as_wrong_direction(self):
        rep = self.index.match_polyline(route((1000, 300), (1000, -300)))
        self.assertGreater(rep['wrong_direction_m'], 560.0)
        self.assertLess(rep['covered_pct'], 5.0)
        self.assertEqual(rep['gaps'][0]['kind'], 'wrong_direction')

    def test_a_route_with_no_road_under_it_is_missing(self):
        rep = self.index.match_polyline(route((0, 500), (600, 500)))
        self.assertGreater(rep['missing_m'], 580.0)
        self.assertLess(rep['covered_pct'], 5.0)
        self.assertEqual(rep['gaps'][0]['kind'], 'missing')

    def test_a_road_crossing_the_route_does_not_count_as_following_it(self):
        # Route runs north along x=300, crossing road 1 at (300, 0): only the crossing point can match.
        rep = self.index.match_polyline(route((300, -200), (300, 200)))
        self.assertGreater(rep['missing_m'], 300.0)

    def test_a_hole_in_the_road_is_reported_but_the_rest_is_covered(self):
        index = RoadIndex.from_graph(build_graph([
            ((0, 0), (200, 0), 'primary', True),
            ((400, 0), (600, 0), 'primary', True),          # 200 m hole between x=200 and x=400
        ]))
        rep = index.match_polyline(route((0, 0), (600, 0)))
        self.assertGreater(rep['missing_m'], 120.0)
        self.assertLess(rep['missing_m'], 200.0)
        self.assertGreater(rep['covered_m'], 380.0)
        self.assertEqual(len(rep['gaps']), 1)

    def test_report_totals_are_consistent(self):
        rep = self.index.match_polyline(route((0, 0), (600, 0), (600, 400)))
        parts = rep['covered_m'] + rep['missing_m'] + rep['wrong_direction_m']
        self.assertAlmostEqual(parts, rep['total_m'], delta=1.0)
        self.assertAlmostEqual(sum(seg['length_m'] for seg in rep['segments']), rep['total_m'], delta=1.0)

    def test_degenerate_input_is_rejected(self):
        with self.assertRaises(ValueError):
            self.index.match_polyline([[LAT0, LNG0]])
        with self.assertRaises(ValueError):
            self.index.match_polyline([[LAT0, LNG0], [LAT0, LNG0]])


class IndexTests(unittest.TestCase):

    def test_stored_edge_shape_is_followed_not_the_straight_chord(self):
        from shapely.geometry import LineString
        G = nx.MultiDiGraph()
        for n, xy in enumerate([(0, 0), (400, 0)]):
            lat, lng = at(*xy)
            G.add_node(n, y=lat, x=lng)
        bend = [at(0, 0), at(200, 150), at(400, 0)]            # a hump, 150 m high in the middle
        shape = LineString([(lng, lat) for lat, lng in bend])
        G.add_edge(0, 1, length=700.0, highway='primary', geometry=shape)
        index = RoadIndex.from_graph(G)
        self.assertGreater(index.match_polyline([list(p) for p in bend])['covered_pct'], 95.0)
        self.assertLess(index.match_polyline(route((0, 0), (400, 0)))['covered_pct'], 30.0)


if __name__ == '__main__':
    unittest.main()
