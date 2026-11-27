// The real API client (lib/api.ts) over HTTP against a stand-in that answers exactly like THIS repo's api_server.py:
// path + distance_km, and for the dynamic route Google's live minutes. No travel time and no turn list.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before, after, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';
import { startBackend, guardNetwork, installBrowser, backendBody, sleep, PATH } from './helpers/env.mjs';

let backend: any;
let net: any;
let api: any;
const FROM = { lat: PATH[0][0], lng: PATH[0][1] };
const TO = { lat: PATH[PATH.length - 1][0], lng: PATH[PATH.length - 1][1] };

/** answers of the two endpoints; `traffic` is Google's live minutes on the dynamic answer */
const serve = (shortestKm: number, dynamicKm: number, traffic: number | null) => (url: URL) => ({
  body:
    url.pathname === '/dynamic-route'
      ? backendBody({ distance_km: dynamicKm, google_base_duration_mins: traffic, congested_nodes_avoided: 2 })
      : backendBody({ distance_km: shortestKm }),
});

before(async () => {
  installBrowser();
  backend = await startBackend(serve(6, 7, null));
  process.env.NEXT_PUBLIC_API_BASE = backend.url;
  net = guardNetwork();
  api = await import('../../lib/api.ts');
});
beforeEach(() => {
  backend.requests.length = 0;
  backend.handler = serve(6, 7, null);
});
after(async () => {
  await backend.close();
  net.restore();
});

test('only the four coordinates are sent: the backend accepts nothing else', async () => {
  await api.fetchRoute('shortest', FROM, TO);
  await api.fetchRoute('dynamic', FROM, TO);
  assert.deepEqual(backend.requests.map((r: any) => r.path), ['/route', '/dynamic-route']);
  for (const r of backend.requests) assert.deepEqual(Object.keys(r.query).sort(), ['from_lat', 'from_lng', 'to_lat', 'to_lng']);
});

test("a single route keeps the backend's path and gets the original time: live traffic, else distance at 24 km/h", async () => {
  const plain = await api.fetchRoute('shortest', FROM, TO);
  assert.deepEqual(plain.path, PATH);
  assert.equal(plain.duration_s, 15 * 60); // 6 km at 24 km/h
  backend.handler = serve(6, 7, 21.6);
  assert.equal((await api.fetchRoute('dynamic', FROM, TO)).duration_s, 22 * 60);
});

test('turn instructions are estimated from the shape because the backend sends none', async () => {
  const r = await api.fetchRoute('shortest', FROM, TO);
  assert.deepEqual(r.maneuvers.map((m: any) => m.type), ['depart', 'turn_right', 'arrive']);
});

test('Fastest without live traffic: 22 km/h against 27.5 km/h, as the app always compared them', async () => {
  const both = await api.fetchBothRoutes(FROM, TO); // 6 km -> 16 min, 7 km -> 15 min
  assert.equal(both.shortest.duration_s, 16 * 60);
  assert.equal(both.dynamic.duration_s, 15 * 60);
  assert.equal(both.fastestChoice, 'dynamic');
  assert.equal(both.timeDiffMins, 1);
});

test("Fastest with live traffic: the main-road route takes Google's time", async () => {
  backend.handler = serve(6, 12, 20); // shortest 20 min (traffic), dynamic 12 km at 27.5 = 26 min
  const both = await api.fetchBothRoutes(FROM, TO);
  assert.equal(both.shortest.duration_s, 20 * 60);
  assert.equal(both.dynamic.duration_s, 26 * 60);
  assert.equal(both.fastestChoice, 'shortest');
});

test("a backend that times its routes: its times are used for both, not the app's formulas", async () => {
  backend.handler = (url: URL) => ({
    body: backendBody({
      distance_km: url.pathname === '/dynamic-route' ? 7 : 6,
      duration_s: url.pathname === '/dynamic-route' ? 1500 : 1200,
      google_base_duration_mins: url.pathname === '/dynamic-route' ? 40 : null,
    }),
  });
  const both = await api.fetchBothRoutes(FROM, TO);
  assert.equal(both.shortest.duration_s, 1200);
  assert.equal(both.dynamic.duration_s, 1500);
  assert.equal(both.fastestChoice, 'shortest');
  assert.equal(both.timeDiffMins, 5);
  assert.equal((await api.fetchRoute('dynamic', FROM, TO)).duration_s, 1500);
});

test('a tie keeps the shortest route', async () => {
  backend.handler = serve(5.5, 6.875, null); // 15 min each
  assert.equal((await api.fetchBothRoutes(FROM, TO)).fastestChoice, 'shortest');
});

test('if one endpoint fails the other is still offered', async () => {
  backend.handler = (url: URL) =>
    url.pathname === '/dynamic-route' ? { status: 500, body: 'Internal Server Error' } : { body: backendBody() };
  const both = await api.fetchBothRoutes(FROM, TO);
  assert.equal(both.dynamic, null);
  assert.equal(both.shortest.status, 'success');
  assert.equal(both.fastestChoice, 'shortest');
});

test('a validation error (a list in "detail") becomes a readable message, never [object Object]', async () => {
  backend.handler = () => ({ status: 422, body: { detail: [{ loc: ['query', 'to_lat'], msg: 'field required' }] } });
  const r = await api.fetchRoute('shortest', FROM, TO);
  assert.equal(r.status, 'error');
  assert.equal(r.message, 'The routing server returned an error (422).');
});

test("the backend's own \"no path\" message is passed on", async () => {
  backend.handler = () => ({ body: { status: 'error', message: 'No shortest path found.' } });
  assert.equal((await api.fetchRoute('shortest', FROM, TO)).message, 'No shortest path found.');
});

test('both routes cancelled: marked aborted', async () => {
  const controller = new AbortController();
  backend.handler = () => ({ body: backendBody(), delayMs: 200 });
  const pending = api.fetchBothRoutes(FROM, TO, controller.signal);
  await sleep(30);
  controller.abort();
  assert.equal((await pending).aborted, true);
});

test("incidents: list, report and vote use the backend's endpoints", async () => {
  const incident = { id: 'i1', type: 'crash', title: 'Crash', lat: FROM.lat, lng: FROM.lng };
  backend.handler = (_url: URL, method: string) =>
    method === 'GET'
      ? { body: { status: 'ok', count: 1, incidents: [incident] } }
      : { body: { status: 'ok', incident } };
  assert.equal((await api.fetchActiveIncidents()).length, 1);
  assert.equal((await api.reportIncident('crash', FROM.lat, FROM.lng, 90, 'MG Road')).status, 'ok');
  await api.verifyIncident('i1', 'yes');
  assert.deepEqual(
    backend.requests.filter((r: any) => r.method !== 'OPTIONS').map((r: any) => `${r.method} ${r.path}`),
    ['GET /incidents', 'POST /incidents', 'POST /incidents/i1/verify']
  );
});

test('reverseGeocode: no geocoder, an empty answer, a failure and a real answer', async () => {
  const w = (globalThis as any).window;
  assert.deepEqual(await api.reverseGeocode(12.9, 77.5), { name: 'Dropped pin', address: '12.90000, 77.50000' });
  const use = (geocode: () => Promise<any>) => (w.google = { maps: { Geocoder: class { geocode = geocode; } } });
  use(async () => ({ results: [] }));
  assert.equal((await api.reverseGeocode(12.9, 77.5)).name, 'Dropped pin');
  use(async () => { throw new Error('OVER_QUERY_LIMIT'); });
  assert.equal((await api.reverseGeocode(12.9, 77.5)).name, 'Dropped pin');
  use(async () => ({ results: [{ formatted_address: 'Brigade Road, Bengaluru' }] }));
  assert.deepEqual(await api.reverseGeocode(12.9, 77.5), { name: 'Brigade Road', address: 'Brigade Road, Bengaluru' });
  delete w.google;
});

test('no request left the machine', () => assert.deepEqual(net.blocked, []));
