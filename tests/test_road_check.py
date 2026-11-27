"""
The Google road check, against a FAKE Google that only knows certain roads (no network, nothing paid), and the API's
check -> block -> plan again loop with a real blacklist in a temporary file.

    python -m unittest tests.test_road_check -v
"""
import asyncio
import math
import os
import tempfile
import unittest
from unittest import mock

import services.external_api as external_api
from routing.algorithms import haversine_m
from routing.edge_blacklist import EdgeBlacklist
from tests.test_graph_qa import KX, KY, LAT0, LNG0, at
from tests.test_smart_routing import road_map


def xy(lat, lng):
    return (lng - LNG0) * KX, (lat - LAT0) * KY


def nearest_on(segment, p):
    (ax, ay), (bx, by) = segment
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / ((dx * dx + dy * dy) or 1.0)))
    return ax + t * dx, ay + t * dy


class FakeGoogle:
    """Stands in for httpx.AsyncClient. Snaps each point to the nearest road it knows within 50 m, like snapToRoads."""

    def __init__(self, roads, status=200, error=None, misses=()):
        self.roads, self.status, self.error, self.misses = roads, status, error, set(misses)
        self.requests = []

    def __call__(self, **kwargs):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, url, params):
        if self.error:
            raise self.error
        points = [tuple(float(v) for v in p.split(',')) for p in params['path'].split('|')]
        self.requests.append(points)
        snapped = []
        for i, (lat, lng) in enumerate(points):
            here = xy(lat, lng)
            options = [nearest_on(r, here) for r in self.roads]
            best = min(options, key=lambda q: math.dist(q, here), default=None)
            if i in self.misses or best is None or math.dist(best, here) > 50:
                continue
            slat, slng = at(*best)
            snapped.append({'originalIndex': i, 'location': {'latitude': slat, 'longitude': slng}})
        status = self.status

        class Response:
            status_code = status
            text = 'refused'

            def json(self):
                return {'snappedPoints': snapped}
        return Response()


class RoadCheckCase(unittest.TestCase):

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.blacklist = EdgeBlacklist(os.path.join(folder.name, 'blocked.json'))
        external_api._confirmed_roads.clear()
        for p in (mock.patch('routing.edge_blacklist.edge_blacklist', self.blacklist),
                  mock.patch.object(external_api, 'ROADS_KEY', 'test-key'),
                  mock.patch.object(external_api, 'VERIFY_SHADOW_MODE', False),
                  mock.patch('builtins.print')):
            p.start()
            self.addCleanup(p.stop)

    def check(self, google, edges, G):
        with mock.patch.object(external_api.httpx, 'AsyncClient', google):
            return asyncio.run(external_api.snap_and_verify_route(edges, G))


def street(y=0, highway='residential', x0=0, x1=200):
    G, ids = road_map([([(x0, y), (x1, y)], highway, {})])
    return G, (ids[(x0, y)], ids[(x1, y)])


class VerdictTests(RoadCheckCase):

    def test_a_road_google_has_passes_and_nothing_is_blocked(self):
        G, edge = street()
        self.assertEqual(self.check(FakeGoogle([((0, 3), (200, 3))]), [edge], G), ([], 'checked'))
        self.assertEqual(self.blacklist.count(), 0)

    def test_a_road_google_does_not_have_is_blocked_in_both_directions(self):
        G, (u, v) = street()
        bad, status = self.check(FakeGoogle([]), [(u, v)], G)
        self.assertEqual((bad, status), ([(u, v)], 'checked'))
        self.assertGreater(self.blacklist.get_edge_penalty(u, v), 1000)
        self.assertGreater(self.blacklist.get_edge_penalty(v, u), 1000)

    def test_a_lane_beside_a_real_road_is_caught_unless_within_the_tolerance(self):
        G, edge = street()
        self.assertEqual(self.check(FakeGoogle([((0, 40), (200, 40))]), [edge], G)[0], [edge])   # 40 m away
        external_api._confirmed_roads.clear()
        G, edge = street()
        # known limit: closer than the tolerance, it cannot be told apart from normal map offset
        self.assertEqual(self.check(FakeGoogle([((0, 15), (200, 15))]), [edge], G)[0], [])

    def test_one_stray_point_is_not_enough_to_block_a_real_road(self):
        G, edge = street()
        self.assertEqual(self.check(FakeGoogle([((0, 0), (200, 0))], misses={1}), [edge], G)[0], [])

    def test_main_roads_are_not_tested(self):
        G, edge = street(highway='primary')
        google = FakeGoogle([])
        self.assertEqual(self.check(google, [edge], G), ([], 'checked'))
        self.assertEqual(google.requests, [])


class NeverBlockOnAGoogleProblemTests(RoadCheckCase):

    def assert_unavailable(self, google):
        G, edge = street()
        self.assertEqual(self.check(google, [edge], G), ([], 'unavailable'))
        self.assertEqual(self.blacklist.count(), 0)

    def test_roads_api_not_enabled(self):
        self.assert_unavailable(FakeGoogle([], status=403))

    def test_network_failure(self):
        self.assert_unavailable(FakeGoogle([], error=OSError('no network')))

    def test_no_key(self):
        with mock.patch.object(external_api, 'ROADS_KEY', None):
            self.assert_unavailable(FakeGoogle([]))

    def test_roads_beyond_the_request_limit_are_left_unjudged(self):
        G, ids = road_map([([(x, 0) for x in range(0, 8001, 200)], 'residential', {})])
        edges = [(ids[(x, 0)], ids[(x + 200, 0)]) for x in range(0, 8000, 200)]
        with mock.patch.object(external_api, 'ROAD_VERIFY_MAX_REQUESTS', 1):
            bad, status = self.check(FakeGoogle([((0, 0), (8000, 0))]), edges, G)
        self.assertEqual((bad, status), ([], 'unavailable'))


class SamplingTests(RoadCheckCase):

    def test_points_are_spread_inside_a_straight_road_not_on_its_end(self):
        # the old check took points[len // 2]: on a two-point road that was the road's END, on the next junction
        G, (u, v) = street()
        _, points = external_api._edge_points(G, u, v)
        xs = [xy(*p)[0] for p in points]
        self.assertGreaterEqual(len(xs), 3)
        self.assertTrue(all(10 < x < 190 for x in xs), xs)
        self.assertEqual(xs, sorted(xs), 'in riding order')

    def test_the_other_direction_samples_in_that_riding_order(self):
        G, (u, v) = street()
        xs = [xy(*p)[0] for p in external_api._edge_points(G, v, u)[1]]
        self.assertEqual(xs, sorted(xs, reverse=True))

    def test_requests_hold_at_most_100_points_and_no_long_jumps(self):
        G, ids = road_map([([(x, 0) for x in range(0, 6001, 200)], 'residential', {}),
                           ([(9000, 0), (9200, 0)], 'residential', {})])
        edges = [(ids[(x, 0)], ids[(x + 200, 0)]) for x in range(0, 6000, 200)] + [(ids[(9000, 0)], ids[(9200, 0)])]
        google = FakeGoogle([((0, 0), (9200, 0))])
        self.assertEqual(self.check(google, edges, G), ([], 'checked'))
        self.assertGreater(len(google.requests), 1)
        for batch in google.requests:
            self.assertLessEqual(len(batch), 100)
            self.assertTrue(all(haversine_m(*a, *b) <= 300 for a, b in zip(batch, batch[1:])))

    def test_a_confirmed_road_is_not_paid_for_again(self):
        G, edge = street()
        google = FakeGoogle([((0, 0), (200, 0))])
        self.check(google, [edge], G)
        self.check(google, [edge], G)
        self.assertEqual(len(google.requests), 1)


if __name__ == '__main__':
    unittest.main()
