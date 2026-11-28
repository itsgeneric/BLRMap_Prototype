"""
Destinations with no road beside them end on the road Google approaches them from (routing/arrival.py), on a hand-built
walled campus. Google is faked: no network, nothing paid.

    python -m unittest tests.test_google_arrival -v
"""
import asyncio
import unittest
from unittest import mock
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import api_server
import services.external_api as external_api
from routing.arrival import arrival_snaps
from routing.graph_manager import graph_manager
from routing.graph_qa import RoadIndex
from tests.test_graph_qa import LAT0, LNG0, KX, KY, at
from tests.test_smart_routing import road_map


def xy(point):
    return (point[1] - LNG0) * KX, (point[0] - LAT0) * KY


def line(*points):
    return [at(*p) for p in points]


# A campus between two roads. The NORTH road's dead end is only 80 m from the place, but a wall separates them.
# The way in is from the SOUTH road, 200 m below the place. West road joins the two.
#
#   y=280   N ============== (dead end behind the wall)
#           |
#   y=200   |            * the place (300, 200)
#           |
#   y=0     S ============================  entrance road
PLACE = (300, 200)


def campus_map(extra=()):
    return road_map([
        ([(0, 0), (150, 0), (300, 0), (600, 0)], 'residential', {}),
        ([(0, 0), (0, 280)], 'residential', {}),
        ([(0, 280), (150, 280), (300, 280)], 'residential', {}),
        *extra,
    ])


# how Google goes there: east along the south road, then north through the campus gate to the place
GOOGLE = line((20, 0), (300, 0), (300, 120), (300, 200))


def find(G, path=GOOGLE, place=PLACE):
    return arrival_snaps(G, RoadIndex.from_graph(G), path, at(*place))


class ApproachPointTests(unittest.TestCase):

    def test_the_trip_ends_where_google_leaves_the_public_road_not_behind_the_wall(self):
        G, _ = campus_map()
        snaps = find(G)
        x, y = xy(snaps[0].point)
        self.assertAlmostEqual(y, 0, delta=2, msg='on the south (entrance) road')
        self.assertAlmostEqual(x, 300, delta=20)
        self.assertAlmostEqual(snaps[0].distance_m, 200, delta=20, msg='measured from the real pin')

    def test_both_directions_of_a_two_way_road_are_offered(self):
        G, _ = campus_map()
        self.assertEqual({(s.edge[0] < s.edge[1]) for s in find(G)}, {True, False})

    def test_a_road_that_google_only_crosses_is_not_used(self):
        # a lane runs across Google's path inside the campus, at right angles
        G, _ = campus_map(extra=[([(220, 100), (380, 100)], 'residential', {})])
        self.assertAlmostEqual(xy(find(G)[0].point)[1], 0, delta=2)

    def test_access_only_roads_are_not_an_approach(self):
        G, _ = campus_map(extra=[([(300, 0), (300, 120)], 'service', {'access_only': True})])
        self.assertAlmostEqual(xy(find(G)[0].point)[1], 0, delta=2)

    def test_when_google_ends_on_a_public_road_the_trip_ends_there(self):
        G, _ = campus_map()
        path = line((20, 0), (450, 0))
        self.assertAlmostEqual(xy(find(G, path, place=(450, 90))[0].point)[0], 450, delta=3)

    def test_a_public_road_far_from_the_place_is_not_an_arrival(self):
        G, _ = campus_map()
        path = line((20, 0), (300, 0), (300, 900))
        self.assertIsNone(find(G, path, place=(300, 900)))

    def test_no_google_path_means_no_answer(self):
        G, _ = campus_map()
        for path in (None, [], line((20, 0))):
            self.assertIsNone(arrival_snaps(G, RoadIndex.from_graph(G), path, at(*PLACE)))

    def test_a_google_path_nowhere_near_our_roads_gives_no_answer(self):
        G, _ = campus_map()
        self.assertIsNone(find(G, line((250, 120), (300, 160), (300, 200))))


class ApiArrivalTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        G, _ = campus_map()
        for _, _, data in G.edges(data=True):
            data.setdefault('name', 'Road')
        saved = (graph_manager.G, graph_manager.major_nodes, graph_manager.surface_penalties,
                 dict(api_server._road_index_state), dict(api_server._landmark_state))
        cls._saved = saved
        graph_manager.G, graph_manager.major_nodes, graph_manager.surface_penalties = G, set(), {}
        api_server._road_index_state.update(index=RoadIndex.from_graph(G), building=False, error=None)
        api_server._landmark_state.update(lm=None, building=False, error=None)
        cls.client = TestClient(api_server.app)

    @classmethod
    def tearDownClass(cls):
        (graph_manager.G, graph_manager.major_nodes, graph_manager.surface_penalties, roads, landmarks) = cls._saved
        api_server._road_index_state.clear()
        api_server._road_index_state.update(roads)
        api_server._landmark_state.clear()
        api_server._landmark_state.update(landmarks)

    def setUp(self):
        self.google = AsyncMock(return_value=GOOGLE)
        for p in (mock.patch.object(api_server, 'fetch_arrival_path', self.google),
                  mock.patch.object(api_server, 'fetch_traffic_data', AsyncMock(return_value=(None, []))),
                  mock.patch.object(api_server, 'snap_and_verify_route', AsyncMock(return_value=([], 'checked'))),
                  mock.patch.object(api_server.db, 'create_journey_from_route', AsyncMock(return_value=None)),
                  mock.patch.object(api_server.db, 'get_active_incident_penalties', AsyncMock(return_value={}))):
            p.start()
            self.addCleanup(p.stop)

    def ask(self, endpoint, to):
        a, b = at(20, -10), at(*to)
        return self.client.get(endpoint, params={'from_lat': a[0], 'from_lng': a[1], 'to_lat': b[0], 'to_lng': b[1]}).json()

    def test_a_walled_place_is_reached_from_googles_side_in_both_modes(self):
        for endpoint in ('/route', '/dynamic-route'):
            body = self.ask(endpoint, PLACE)
            self.assertEqual((body['status'], body['arrival']), ('success', 'google_approach'), endpoint)
            x, y = xy(body['path'][-1])
            self.assertAlmostEqual(y, 0, delta=3, msg=endpoint)
            self.assertAlmostEqual(body['destination_snap']['distance_m'], 200, delta=20)

    def test_without_this_the_route_ended_behind_the_wall(self):
        with mock.patch.object(api_server, 'ENABLE_GOOGLE_ARRIVAL', False):
            body = self.ask('/route', PLACE)
        self.assertEqual(body['arrival'], 'nearest_road')
        self.assertAlmostEqual(xy(body['path'][-1])[1], 280, delta=3)

    def test_google_is_not_asked_when_a_road_is_beside_the_pin(self):
        body = self.ask('/route', (450, 25))
        self.assertEqual(body['arrival'], 'nearest_road')
        self.google.assert_not_awaited()

    def test_if_google_cannot_help_the_nearest_road_is_still_used(self):
        self.google.return_value = None
        body = self.ask('/route', PLACE)
        self.assertEqual((body['status'], body['arrival']), ('success', 'nearest_road'))

    def test_a_place_with_no_road_within_500_m_is_rescued_by_googles_approach(self):
        place = (300, -560)                                   # south of everything: too far to snap
        self.google.return_value = line((20, 0), (500, 0), (500, -300), (300, -560))
        body = self.ask('/route', place)
        self.assertEqual((body['status'], body['arrival']), ('success', 'google_approach'))

    def test_with_no_road_and_no_google_answer_the_rider_gets_a_clear_message(self):
        self.google.return_value = None
        body = self.ask('/route', (300, -900))
        self.assertEqual(body['status'], 'error')
        self.assertIn('No road within', body['message'])


class FetchArrivalPathTests(unittest.TestCase):
    """The Google request itself, with a fake HTTP client."""

    @staticmethod
    def client(status=200, body=None, error=None):
        class Response:
            status_code = status
            text = 'refused'

            def json(self):
                return body
        fake = mock.Mock()
        fake.post = AsyncMock(side_effect=error, return_value=Response())
        return fake

    def run_fetch(self, client, key='test-key'):
        with mock.patch.object(external_api, 'ROUTES_KEY', key), mock.patch('builtins.print'):
            return asyncio.run(external_api.fetch_arrival_path(client, 12.9, 77.5, 12.98, 77.66))

    def test_returns_googles_line_and_asks_for_two_wheelers(self):
        encoded = '_p~iF~ps|U_ulLnnqC'                                       # the encoding documentation's sample
        client = self.client(body={'routes': [{'polyline': {'encodedPolyline': encoded}}]})
        path = self.run_fetch(client)
        self.assertEqual(len(path), 2)
        self.assertAlmostEqual(path[0][0], 38.5, places=4)
        sent = client.post.await_args.kwargs
        self.assertEqual(sent['json']['travelMode'], 'TWO_WHEELER')
        self.assertEqual(sent['headers']['X-Goog-FieldMask'], 'routes.polyline.encodedPolyline')

    def test_every_google_problem_gives_none(self):
        self.assertIsNone(self.run_fetch(self.client(status=403)))
        self.assertIsNone(self.run_fetch(self.client(body={})))
        self.assertIsNone(self.run_fetch(self.client(error=OSError('offline'))))
        client = self.client()
        self.assertIsNone(self.run_fetch(client, key=None))
        client.post.assert_not_awaited()


if __name__ == '__main__':
    unittest.main()
