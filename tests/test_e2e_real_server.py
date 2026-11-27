"""
End-to-end tests against a RUNNING backend with the real Bengaluru map. Skipped unless BLR_E2E_URL is set, so the normal test run
never needs a server.

To run them without spending any Google quota, start the server with the paid keys blanked (nothing external is then called):

    PowerShell:
        $env:GOOGLE_PLACES_API_KEY=""; $env:GOOGLE_MAPS_API_KEY=""; $env:GOOGLE_ROADS_API_KEY=""; $env:MONGODB_URI=""
        python -m uvicorn api_server:app --port 8765
    (wait for "[Index] Road index ready" and "[Landmarks] Ready")
    then:
        $env:BLR_E2E_URL="http://127.0.0.1:8765"
        python -m unittest tests.test_e2e_real_server -v
"""
import os
import statistics
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

import httpx

BASE = os.environ.get('BLR_E2E_URL', '').rstrip('/')

TRIPS = {
    # name: (from, to, expected distance range in km for the CURRENT cost model, maximum share of highways)
    'BNMIT -> MG Road': ((12.9237, 77.5714), (12.9756, 77.6066), (7.5, 11.5)),
    'Indiranagar -> Koramangala': ((12.9784, 77.6408), (12.9352, 77.6245), (5.5, 10.0)),
    'Koramangala -> Whitefield': ((12.9352, 77.6245), (12.9863, 77.7346), (17.0, 22.0)),
    'MG Road -> Vidhana Soudha': ((12.9756, 77.6066), (12.9796, 77.5909), (1.8, 3.2)),
    'Cubbon Park B -> A (reported)': ((12.97039, 77.59527), (12.98376, 77.59697), (2.2, 3.4)),
    'AGS Layout -> Electronic City (reported)': ((12.912765, 77.534049), (12.8452, 77.6602), (19.5, 21.5)),
}


def query(a, b):
    return {'from_lat': a[0], 'from_lng': a[1], 'to_lat': b[0], 'to_lng': b[1]}


@unittest.skipUnless(BASE, 'set BLR_E2E_URL to run the end-to-end tests against a running server')
class RealServerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.http = httpx.Client(base_url=BASE, timeout=60.0)
        if cls.http.get('/').json().get('status') != 'online':
            raise unittest.SkipTest('the server is not ready')

    @classmethod
    def tearDownClass(cls):
        cls.http.close()

    def get(self, endpoint, a, b):
        t = time.perf_counter()
        r = self.http.get(endpoint, params=query(a, b))
        return r, time.perf_counter() - t

    def test_every_trip_returns_a_complete_route_in_both_modes(self):
        for name, (a, b, (lo, hi)) in TRIPS.items():
            for endpoint in ('/route', '/dynamic-route'):
                with self.subTest(trip=name, endpoint=endpoint):
                    r, _ = self.get(endpoint, a, b)
                    self.assertEqual(r.status_code, 200)
                    body = r.json()
                    self.assertEqual(body['status'], 'success', body)
                    self.assertGreater(len(body['path']), 10)
                    self.assertGreater(body['duration_s'], 0)
                    self.assertEqual(body['maneuvers'][0]['type'], 'depart')
                    self.assertEqual(body['maneuvers'][-1]['type'], 'arrive')
                    self.assertIn('origin_snap', body)
                    if endpoint == '/dynamic-route':
                        self.assertGreaterEqual(body['distance_km'], lo, f'{name}: suspiciously short')
                        self.assertLessEqual(body['distance_km'], hi, f'{name}: suspiciously long (a detour or highway?)')

    def test_planned_duration_is_consistent_with_distance(self):
        """Between 4 and 40 km/h average for every trip: catches a broken speed table or a unit mix-up."""
        for name, (a, b, _) in TRIPS.items():
            body = self.get('/dynamic-route', a, b)[0].json()
            kmh = body['distance_km'] / (body['duration_s'] / 3600)
            self.assertTrue(4 <= kmh <= 40, f'{name}: {kmh:.1f} km/h')

    def test_dynamic_planning_is_fast_enough_for_a_phone(self):
        """Regression for the 6 s planning time and for the 25 s app time-out ("failed to fetch directions")."""
        self.get('/dynamic-route', *TRIPS['BNMIT -> MG Road'][:2])        # warm up
        times = []
        for name, (a, b, _) in TRIPS.items():
            r, seconds = self.get('/dynamic-route', a, b)
            self.assertEqual(r.json()['status'], 'success')
            times.append(seconds)
        self.assertLess(max(times), 8.0, f'slowest trip took {max(times):.1f}s')
        self.assertLess(statistics.median(times), 3.0, f'median {statistics.median(times):.1f}s')

    def test_a_point_in_the_middle_of_nowhere_is_a_clear_error(self):
        r, _ = self.get('/dynamic-route', (12.9237, 77.5714), (12.60, 77.20))      # far outside the map
        body = r.json()
        self.assertEqual(body['status'], 'error')
        self.assertIn('No road within', body['message'])

    def test_a_burst_of_parallel_requests_all_succeed_with_the_same_answer(self):
        a, b, _ = TRIPS['MG Road -> Vidhana Soudha']
        with ThreadPoolExecutor(max_workers=10) as pool:
            replies = list(pool.map(lambda i: self.http.get('/dynamic-route' if i % 2 else '/route', params=query(a, b)), range(30)))
        self.assertTrue(all(r.status_code == 200 and r.json()['status'] == 'success' for r in replies))
        dynamic = {round(r.json()['distance_km'], 2) for i, r in enumerate(replies) if i % 2}
        self.assertEqual(len(dynamic), 1, f'the same request must give the same route, got {dynamic}')

    def test_aborting_requests_does_not_hurt_the_server(self):
        """The app cancels a request when a newer one replaces it. The server must shrug that off."""
        a, b, _ = TRIPS['Koramangala -> Whitefield']
        for _ in range(8):
            try:
                httpx.get(BASE + '/dynamic-route', params=query(a, b), timeout=0.05)
            except httpx.TimeoutException:
                pass
        r, _ = self.get('/route', *TRIPS['MG Road -> Vidhana Soudha'][:2])
        self.assertEqual(r.json()['status'], 'success')

    def test_the_highway_regression_trip_stays_on_inner_roads(self):
        """AGS Layout -> Electronic City used to take 22.7 km including 13 km of flyovers; inner roads are 20.8 km."""
        a, b, _ = TRIPS['AGS Layout -> Electronic City (reported)']
        body = self.get('/dynamic-route', a, b)[0].json()
        self.assertLess(body['distance_km'], 21.5)


if __name__ == '__main__':
    unittest.main()
