"""
Integration tests: the real FastAPI app (routing, snapping, maneuvers, durations, response shape) called over HTTP.

The road map is a tiny synthetic one; only the paid / external services are stubbed (Google Routes, Google Roads verification,
MongoDB). Nothing here touches the network, your .env keys, or edge_blacklist.json.

Run from the repository root:

    python -m unittest tests.test_api_integration -v
"""
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import api_server
import services.external_api as external_api
from core.config import FREE_FLOW_SPEED_KMH
from routing.graph_manager import graph_manager
from routing.graph_qa import RoadIndex
from tests.test_graph_qa import LAT0, LNG0, at
from tests.test_turn_routing import named_graph

# R1 runs west->east, R2 turns north at its end, R3 is a one-way road that only runs south->north far away from both.
ROADS = [
    ((0, 0), (600, 0), 'primary', 'R1 Road'),
    ((600, 0), (600, 600), 'primary', 'R2 Road'),
]
FROM = at(100, -30)          # 30 m off R1
TO = at(630, 300)            # 30 m off R2
FAR = at(300, -1500)         # 1.5 km from any road: beyond MAX_SNAP_DISTANCE_M


def params(a, b):
    return {'from_lat': a[0], 'from_lng': a[1], 'to_lat': b[0], 'to_lng': b[1]}


class ApiIntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        G, _ = named_graph(ROADS)
        G.graph['crs'] = 'epsg:4326'          # the real map carries this; osmnx needs it for nearest-node lookups
        cls._saved = (graph_manager.G, graph_manager.major_nodes, graph_manager.surface_penalties,
                      dict(api_server._road_index_state), dict(api_server._landmark_state))
        graph_manager.G = G
        graph_manager.major_nodes = set()
        graph_manager.surface_penalties = {}
        api_server._road_index_state.update(index=RoadIndex.from_graph(G), building=False, error=None)
        api_server._landmark_state.update(lm=None, building=False, error=None)

        cls.patches = [
            mock.patch.object(api_server, 'fetch_traffic_data', AsyncMock(return_value=(None, []))),
            mock.patch.object(api_server, 'fetch_arrival_path', AsyncMock(return_value=None)),   # a paid Google call
            mock.patch.object(api_server, 'snap_and_verify_route', AsyncMock(return_value=([], 'checked'))),
            mock.patch.object(api_server.db, 'create_journey_from_route', AsyncMock(return_value='journey-1')),
            mock.patch.object(api_server.db, 'get_active_incident_penalties', AsyncMock(return_value={})),
        ]
        cls.mocks = [p.start() for p in cls.patches]
        cls.client = TestClient(api_server.app)  # not used as a context manager: the real graph/DB startup is skipped

    @classmethod
    def tearDownClass(cls):
        for p in cls.patches:
            p.stop()
        (graph_manager.G, graph_manager.major_nodes, graph_manager.surface_penalties,
         road_state, landmark_state) = cls._saved
        api_server._road_index_state.clear()
        api_server._road_index_state.update(road_state)
        api_server._landmark_state.clear()
        api_server._landmark_state.update(landmark_state)

    # ------------------------------------------------------------------ the contract the frontend relies on
    def check_route_contract(self, body):
        self.assertEqual(body['status'], 'success')
        self.assertIsInstance(body['path'], list)
        self.assertGreater(len(body['path']), 1)
        for point in body['path']:
            self.assertEqual(len(point), 2)
            self.assertTrue(all(isinstance(v, float) for v in point))
        self.assertIsInstance(body['distance_km'], float)
        self.assertIsInstance(body['duration_s'], float)
        self.assertGreater(body['duration_s'], 0)
        for key in ('origin_snap', 'destination_snap'):
            self.assertEqual(set(body[key]), {'lat', 'lng', 'distance_m'})
        self.assertEqual(body['journey_id'], 'journey-1')
        m = body['maneuvers']
        self.assertGreaterEqual(len(m), 2)
        self.assertEqual(m[0]['type'], 'depart')
        self.assertEqual(m[-1]['type'], 'arrive')
        for item in m:
            self.assertEqual(set(item), {'type', 'instruction', 'road_name', 'distance_m', 'lat', 'lng'})

    def test_root_is_online(self):
        self.assertEqual(self.client.get('/').json(), {'status': 'online'})

    def test_shortest_route_has_everything_the_app_needs(self):
        body = self.client.get('/route', params=params(FROM, TO)).json()
        self.check_route_contract(body)
        self.assertAlmostEqual(body['distance_km'], 0.8, delta=0.02)          # 500 m along R1 + 300 m up R2
        self.assertEqual([m['type'] for m in body['maneuvers']], ['depart', 'turn_left', 'arrive'])
        self.assertEqual(body['maneuvers'][1]['road_name'], 'R2 Road')

    def test_dynamic_route_has_everything_the_app_needs(self):
        body = self.client.get('/dynamic-route', params=params(FROM, TO)).json()
        self.check_route_contract(body)
        self.assertIn('google_base_duration_mins', body)
        self.assertIsNone(body['google_base_duration_mins'])
        self.assertEqual(body['congested_nodes_avoided'], 0)

    def test_the_route_starts_and_ends_on_a_road_and_never_at_the_pin(self):
        body = self.client.get('/dynamic-route', params=params(FROM, TO)).json()
        first, last = body['path'][0], body['path'][-1]
        self.assertAlmostEqual(first[0], LAT0, places=6)                      # on R1, not 30 m south of it
        self.assertAlmostEqual(last[1], at(600, 0)[1], places=6)              # on R2
        self.assertNotIn(list(FROM), body['path'])
        self.assertNotIn(list(TO), body['path'])
        self.assertAlmostEqual(body['origin_snap']['distance_m'], 30.0, delta=1.5)
        self.assertAlmostEqual(body['destination_snap']['distance_m'], 30.0, delta=1.5)

    def test_planned_duration_matches_the_road_speed_and_the_turn(self):
        body = self.client.get('/route', params=params(FROM, TO)).json()
        expected = 800.0 / (FREE_FLOW_SPEED_KMH['primary'] / 3.6) + 5.0        # 800 m on primary + one sharp turn
        self.assertAlmostEqual(body['duration_s'], expected, delta=3.0)

    def test_live_traffic_is_reported_without_changing_the_road_choice(self):
        jam = [list(at(300, 0))]
        with mock.patch.object(api_server, 'fetch_traffic_data', AsyncMock(return_value=(900.0, jam))):
            body = self.client.get('/dynamic-route', params=params(FROM, TO)).json()
        self.assertEqual(body['status'], 'success')
        self.assertEqual(body['google_base_duration_mins'], 15.0)
        self.assertGreaterEqual(body['congested_nodes_avoided'], 1)

    def test_many_traffic_jam_points_cost_one_lookup_not_one_each(self):
        """Regression: each jam point used to trigger its own whole-city nearest-node lookup (0.7 s each on the real map)."""
        jam = [list(at(x, 5)) for x in range(0, 600, 12)] * 2             # 100 points, half of them duplicates
        real = api_server.ox.nearest_nodes
        calls = []

        def counting(G, X, Y, *args, **kwargs):
            calls.append(len(X) if hasattr(X, '__len__') else 1)
            return real(G, X, Y, *args, **kwargs)

        with mock.patch.object(api_server, 'fetch_traffic_data', AsyncMock(return_value=(600.0, jam))),                 mock.patch.object(api_server.ox, 'nearest_nodes', counting):
            body = self.client.get('/dynamic-route', params=params(FROM, TO)).json()
        self.assertEqual(body['status'], 'success')
        self.assertEqual(len(calls), 1, f'expected ONE batched lookup, got {len(calls)}')
        self.assertEqual(calls[0], 50, 'duplicate jam points are removed before the lookup')

    def test_a_pin_far_from_every_road_gets_a_clear_error_not_a_line_through_buildings(self):
        for endpoint in ('/route', '/dynamic-route'):
            body = self.client.get(endpoint, params=params(FAR, TO)).json()
            self.assertEqual(body['status'], 'error')
            self.assertIn('No road within', body['message'])
            self.assertIn('start', body['message'])
        body = self.client.get('/route', params=params(FROM, FAR)).json()
        self.assertIn('destination', body['message'])

    def test_missing_or_bad_parameters_are_rejected_with_422(self):
        self.assertEqual(self.client.get('/route', params={'from_lat': 1}).status_code, 422)
        bad = params(FROM, TO)
        bad['from_lat'] = 'north'
        self.assertEqual(self.client.get('/dynamic-route', params=bad).status_code, 422)

    def test_both_pins_on_one_road_drive_just_that_stretch(self):
        body = self.client.get('/route', params=params(at(100, -20), at(400, -20))).json()
        self.check_route_contract(body)
        self.assertAlmostEqual(body['distance_km'], 0.3, delta=0.01)
        self.assertEqual([m['type'] for m in body['maneuvers']], ['depart', 'arrive'])

    def test_a_road_google_does_not_have_is_planned_around_and_rechecked(self):
        seen = []

        async def google(edges, graph):
            seen.append(list(edges))
            return ([edges[0]], 'checked') if len(seen) == 1 else ([], 'checked')

        for endpoint in ('/route', '/dynamic-route'):
            seen.clear()
            with mock.patch.object(api_server, 'snap_and_verify_route', google):
                body = self.client.get(endpoint, params=params(FROM, TO)).json()
            self.assertEqual((body['status'], body['road_check']), ('success', 'passed'), endpoint)
            self.assertEqual(len(seen), 2, 'the new route is checked too')
            self.assertTrue(seen[0], 'the part-roads at the ends are included')

    def test_when_no_route_passes_the_answer_says_so(self):
        async def google(edges, graph):
            return [edges[0]], 'checked'

        with mock.patch.object(api_server, 'snap_and_verify_route', google):
            body = self.client.get('/route', params=params(FROM, TO)).json()
        self.assertEqual((body['status'], body['road_check']), ('success', 'failed'))

    def test_a_blocked_road_that_is_the_only_way_is_never_reported_as_passed(self):
        with mock.patch.object(api_server.edge_blacklist, 'get_edge_penalty', return_value=10000.0):
            body = self.client.get('/route', params=params(FROM, TO)).json()
        self.assertEqual(body['road_check'], 'failed')

    def test_unavailable_and_disabled_checks_are_reported_honestly(self):
        with mock.patch.object(api_server, 'snap_and_verify_route', AsyncMock(return_value=([], 'unavailable'))):
            self.assertEqual(self.client.get('/route', params=params(FROM, TO)).json()['road_check'], 'unavailable')
        with mock.patch.object(api_server, 'ENABLE_ROAD_VERIFY', False):
            self.assertEqual(self.client.get('/route', params=params(FROM, TO)).json()['road_check'], 'off')

    def test_there_are_no_developer_endpoints(self):
        for path in ('/qa/status', '/qa/road-coverage', '/qa/compare-models'):
            self.assertEqual(self.client.get(path, params=params(FROM, TO)).status_code, 404, path)

    def test_dynamic_reports_the_detour_it_was_allowed(self):
        body = self.client.get('/dynamic-route', params=params(FROM, TO)).json()
        self.check_route_contract(body)
        budget = max(body['direct_distance_km'] * 1.15, body['direct_distance_km'] + 0.3)
        self.assertLessEqual(body['distance_km'], budget + 0.01)
        self.assertIn(body['preference_level'], (1.0, 0.6, 0.3, 0.0))
        self.assertIs(body['through_traffic'], False)

    def test_the_paid_road_check_is_not_called_unless_enabled(self):
        verify = api_server.snap_and_verify_route
        for enabled, expected in ((False, 0), (True, 2)):
            verify.reset_mock()
            with mock.patch.object(api_server, 'ENABLE_ROAD_VERIFY', enabled):
                self.client.get('/route', params=params(FROM, TO))
                self.client.get('/dynamic-route', params=params(FROM, TO))
            self.assertEqual(verify.call_count, expected, f'enabled={enabled}')

    def test_spamming_the_server_with_parallel_requests_gives_identical_correct_answers(self):
        def call(i):
            endpoint = '/route' if i % 2 else '/dynamic-route'
            return self.client.get(endpoint, params=params(FROM, TO)).json()

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(call, range(40)))
        self.assertTrue(all(r['status'] == 'success' for r in results))
        self.assertEqual({round(r['distance_km'], 3) for r in results}, {round(results[0]['distance_km'], 3)})
        self.assertEqual({tuple(map(tuple, r['path'])) for r in results[::2]}.__len__(), 1)

    def test_the_road_index_not_being_ready_yet_still_gives_a_route(self):
        """Right after server start the index builds in the background; routes must work meanwhile (nearest-junction snapping)."""
        saved = api_server._road_index_state['index']
        api_server._road_index_state['index'] = None
        try:
            body = self.client.get('/route', params=params(at(0, 0), at(600, 600))).json()
        finally:
            api_server._road_index_state['index'] = saved
        self.assertEqual(body['status'], 'success')
        self.assertAlmostEqual(body['distance_km'], 1.2, delta=0.02)

    # ------------------------------------------------------------------ journeys
    def test_journey_endpoints_report_404_for_unknown_journeys(self):
        payload = {'session_id': 's', 'origin': {'name': 'a', 'lat': 1.0, 'lng': 2.0}, 'destination': {'name': 'b', 'lat': 3.0, 'lng': 4.0}}
        with mock.patch.object(api_server.db, 'attach_session_and_places', AsyncMock(return_value=False)):
            self.assertEqual(self.client.post('/journeys/nope/start', json=payload).status_code, 404)
        with mock.patch.object(api_server.db, 'attach_session_and_places', AsyncMock(return_value=True)):
            self.assertEqual(self.client.post('/journeys/abc/start', json=payload).json(), {'status': 'ok'})
        with mock.patch.object(api_server.db, 'complete_journey', AsyncMock(return_value=True)):
            r = self.client.post('/journeys/abc/complete', json={'actual_duration_secs': 600, 'actual_avg_speed_kmh': 21.5})
            self.assertEqual(r.json(), {'status': 'ok'})
        with mock.patch.object(api_server.db, 'log_reroute', AsyncMock(return_value=True)):
            r = self.client.post('/journeys/abc/reroute', json={'lat': 12.9, 'lng': 77.5, 'distance_off_route_m': 60, 'time_since_start_secs': 90})
            self.assertEqual(r.json(), {'status': 'ok'})


class ShadowModeTests(unittest.TestCase):
    """The Roads-API ghost check only LOGS what it would ban, while shadow mode is on (it banned real roads before)."""

    def test_shadow_mode_never_bans_a_road(self):
        with mock.patch('routing.edge_blacklist.edge_blacklist.mark_edge_bad') as ban, \
                mock.patch.object(external_api, 'VERIFY_SHADOW_MODE', True):
            external_api._mark_bad(1, 2, reason='excessive_snap_deviation', deviation_m=300.0)
        ban.assert_not_called()

    def test_with_shadow_mode_off_the_old_banning_returns(self):
        with mock.patch('routing.edge_blacklist.edge_blacklist.mark_edge_bad') as ban, \
                mock.patch.object(external_api, 'VERIFY_SHADOW_MODE', False):
            external_api._mark_bad(1, 2, reason='excessive_snap_deviation', deviation_m=300.0)
        ban.assert_called_once()


if __name__ == '__main__':
    unittest.main()
