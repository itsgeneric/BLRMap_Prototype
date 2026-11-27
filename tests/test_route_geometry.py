"""
Step 2.2 tests: the displayed route line is now GraphManager.route_nodes_to_coords() and nothing else
(the Roads-API re-snap is off by default), so its behaviour is pinned down here on tiny graphs.

Run from the repository root:

    python -m unittest tests.test_route_geometry -v
"""
import unittest

import networkx as nx
from shapely.geometry import LineString

from routing.graph_manager import GraphManager

# Node positions (lat, lng). Edge shapes are shapely LineStrings in (x=lng, y=lat) order, as in OSMnx.
A = (12.900, 77.600)
B = (12.910, 77.600)
C = (12.910, 77.610)
BEND_AB = (12.905, 77.605)          # a bend between A and B


def make_manager(edges):
    """edges: list of (u, v, attrs). Nodes 0=A, 1=B, 2=C."""
    G = nx.MultiDiGraph()
    for node, (lat, lng) in enumerate([A, B, C]):
        G.add_node(node, y=lat, x=lng)
    for u, v, attrs in edges:
        G.add_edge(u, v, **attrs)
    gm = GraphManager()
    gm.G = G
    return gm


def shape(*latlngs):
    return LineString([(lng, lat) for lat, lng in latlngs])


class RouteGeometryTests(unittest.TestCase):

    def test_follows_the_stored_edge_shape(self):
        gm = make_manager([(0, 1, {'length': 1500.0, 'geometry': shape(A, BEND_AB, B)})])
        self.assertEqual(gm.route_nodes_to_coords([0, 1]), [list(A), list(BEND_AB), list(B)])

    def test_reverses_a_shape_stored_in_the_opposite_direction(self):
        gm = make_manager([(0, 1, {'length': 1500.0, 'geometry': shape(B, BEND_AB, A)})])
        self.assertEqual(gm.route_nodes_to_coords([0, 1]), [list(A), list(BEND_AB), list(B)])

    def test_edge_without_shape_is_a_straight_segment_to_the_next_node(self):
        gm = make_manager([(0, 1, {'length': 1100.0})])
        self.assertEqual(gm.route_nodes_to_coords([0, 1]), [list(A), list(B)])

    def test_consecutive_edges_join_without_gaps_or_duplicates(self):
        gm = make_manager([
            (0, 1, {'length': 1500.0, 'geometry': shape(A, BEND_AB, B)}),
            (1, 2, {'length': 1100.0}),
        ])
        coords = gm.route_nodes_to_coords([0, 1, 2])
        self.assertEqual(coords, [list(A), list(BEND_AB), list(B), list(C)])
        self.assertEqual(len(coords), len({tuple(p) for p in coords}), "no point should be repeated")

    def test_parallel_edges_use_the_shorter_one(self):
        gm = make_manager([
            (0, 1, {'length': 5000.0, 'geometry': shape(A, (12.95, 77.65), B)}),   # long way round
            (0, 1, {'length': 1500.0, 'geometry': shape(A, BEND_AB, B)}),          # shorter
        ])
        self.assertEqual(gm.route_nodes_to_coords([0, 1]), [list(A), list(BEND_AB), list(B)])

    def test_trivial_routes(self):
        gm = make_manager([(0, 1, {'length': 1100.0})])
        self.assertEqual(gm.route_nodes_to_coords([]), [])
        self.assertEqual(gm.route_nodes_to_coords([0]), [list(A)])


if __name__ == '__main__':
    unittest.main()
