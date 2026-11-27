// Integration tests of the real app screen (app/page.tsx) with its real hooks, API client, navigation engine, map matching,
// arrival time and voice. Faked: React's runtime, the map, the phone (GPS, text-to-speech) and the backend, which is a local
// HTTP server answering exactly like this repo's api_server.py.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before, after, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';
import { render, find, findAll } from './helpers/fakes/react.mjs';
import {
  installBrowser, installClock, startBackend, guardNetwork, until, sleep, backendBody, at, north, east, PATH,
} from './helpers/env.mjs';

let backend: any;
let net: any;
let browser: any;
let clock: any;
let Page: any;
let app: any = null;

const A = { lat: north(0), lng: east(0), name: 'Home' };
const B = { lat: north(600), lng: east(600), name: 'Work' };
const place = (n: number) => ({ lat: 12.95 + n / 1000, lng: 77.6, name: `Place ${n}` });

let routeAnswer: (url: URL) => any;
let incidentAnswer: (method: string, url: URL) => any;
const ok = () => ({ body: backendBody() });

before(async () => {
  clock = installClock();
  backend = await startBackend((url: URL, method: string) => {
    if (url.pathname.startsWith('/incidents')) return incidentAnswer(method, url);
    if (url.pathname.startsWith('/journeys')) return { body: { status: 'ok' } };
    return routeAnswer(url);
  });
  process.env.NEXT_PUBLIC_API_BASE = backend.url;
  (globalThis as any).__native = true; // behave like the Android app, so speech goes to the (fake) phone
  browser = installBrowser();
  (globalThis as any).document = Object.assign(new EventTarget(), { hidden: false });
  net = guardNetwork();
  Page = (await import('../../app/page.tsx')).default;
});

beforeEach(() => {
  backend.requests.length = 0;
  routeAnswer = ok;
  incidentAnswer = () => ({ body: { status: 'ok', count: 0, incidents: [] } });
  browser.gps.fail = false;
  browser.gps.hold = false;
  browser.gps.held.length = 0;
  browser.gps.current = { latitude: A.lat, longitude: A.lng, accuracy: 8, speed: null, heading: null };
  browser.events.length = 0;
  (globalThis as any).__tts = { spoken: [], stops: 0, languages: ['en-IN'], failSpeak: null };
  delete (globalThis as any).google;
  delete (globalThis as any).window.google;
  app = render(Page, {});
});

afterEach(async () => {
  app?.unmount();
  await sleep(20);
});

after(async () => {
  await backend.close();
  net.restore();
  clock.restore();
});

// ------------------------------------------------------------------ reading the screen
const tree = () => app.result();
const el = (name: string) => find(tree(), name);
const props = (name: string) => el(name)?.props ?? null;
const map = () => props('DynamicMap');
const search = () => props('TopSearchBar');
const panel = () => props('BottomActionBar');
const footer = () => props('NavigationFooter');
const banner = () => props('TurnByTurnBanner');
const toasts = () => props('ToastContainer').toasts as { text: string }[];
const hasText = (text: string) => findAll(tree(), (e: any) => e.type === 'span').some((e: any) => e.props.children === text);
const spinner = () => hasText('Finding optimal Bangalore route...');
const spoken = () => (globalThis as any).__tts.spoken.map((s: any) => s.text) as string[];
const routeShown = () => map().routePath;
const settle = () => sleep(450); // debounce (250 ms) plus a local round trip

async function chooseTrip() {
  search().onSelectOrigin(A);
  search().onSelectDestination(B);
  await until(() => panel(), 'the route panel');
}

async function startTrip() {
  await chooseTrip();
  panel().onStartNavigation();
  await until(() => map().isNavigating, 'navigation to start');
}

let gpsTime = 1_000_000;
/** one GPS fix `along` metres down the route, `seconds` after the previous one */
function ride(along: number, { off = 0, seconds = 5, speed = 8, heading = along <= 600 ? 0 : 90 } = {}) {
  clock.advance(seconds * 1000);
  gpsTime += seconds * 1000;
  browser.gps.emit({ ...at(along, off), speed, heading, accuracy: 5 }, gpsTime);
}
function rideTo(from: number, to: number, step = 40, options: any = {}) {
  for (let a = from; a < to; a += step) ride(a, options);
  ride(to, options);
}
/** far enough off the route, long enough, for the app to ask for a new one */
function leaveRoute() {
  for (let i = 0; i < 4; i++) ride(150, { off: 150 + i * 10, heading: 270, seconds: 3 });
}

// ------------------------------------------------------------------ route requests
test('the start screen asks for no route and shows none', async () => {
  await settle();
  assert.equal(backend.routeRequests().length, 0);
  assert.equal(routeShown(), null);
  assert.equal(el('BottomActionBar'), null);
  assert.equal(toasts().length, 0);
});

test('choosing start and destination makes one request with the four coordinates and shows the route', async () => {
  await chooseTrip();
  await settle();
  const requests = backend.routeRequests();
  assert.equal(requests.length, 1);
  assert.equal(requests[0].path, '/route');
  assert.deepEqual(Object.keys(requests[0].query).sort(), ['from_lat', 'from_lng', 'to_lat', 'to_lng']);
  assert.deepEqual(routeShown(), PATH);
  assert.equal(panel().routeData.duration_s, 180); // the original formula: 1.2 km at 24 km/h
  assert.equal(panel().routeData.maneuvers.length, 3);
  assert.equal(spinner(), false);
});

test('spam: ten destination changes in a row make ONE request, for the last one, with no error', async () => {
  search().onSelectOrigin(A);
  for (let n = 1; n <= 10; n++) search().onSelectDestination(place(n));
  await until(() => routeShown(), 'a route');
  await settle();
  assert.equal(backend.routeRequests().length, 1);
  assert.equal(Number(backend.routeRequests()[0].query.to_lat), place(10).lat);
  assert.equal(toasts().length, 0);
  assert.equal(spinner(), false);
});

test('a slow answer that was superseded never shows an error and never replaces the newer route', async () => {
  routeAnswer = (url: URL) =>
    Number(url.searchParams.get('to_lat')) === place(1).lat
      ? { body: backendBody({ distance_km: 111 }), delayMs: 600 }
      : { body: backendBody({ distance_km: 2 }) };
  search().onSelectOrigin(A);
  search().onSelectDestination(place(1));
  await until(() => backend.routeRequests().length === 1, 'the first request');
  search().onSelectDestination(place(2));
  await until(() => panel(), 'the second route');
  await sleep(700);
  assert.equal(panel().routeData.distance_km, 2);
  assert.equal(toasts().length, 0);
  assert.equal(spinner(), false);
});

test('while a NEW route is loading, the old route cannot be started', async () => {
  await chooseTrip();
  routeAnswer = () => ({ body: backendBody(), delayMs: 400 });
  search().onSelectDestination(place(1));
  assert.equal(el('BottomActionBar'), null, 'immediately, before the request is even sent');
  await sleep(350);
  assert.equal(el('BottomActionBar'), null, 'while the request is in flight');
  await until(() => panel(), 'the new route');
});

test('Clear while a request is in flight: no route appears later, no error, no stuck spinner', async () => {
  routeAnswer = () => ({ body: backendBody(), delayMs: 300 });
  search().onSelectOrigin(A);
  search().onSelectDestination(B);
  await until(() => backend.routeRequests().length === 1, 'the request');
  assert.equal(spinner(), true);
  search().onClear();
  await sleep(700);
  assert.equal(routeShown(), null);
  assert.equal(spinner(), false);
  assert.equal(toasts().length, 0);
});

test("a server error is shown once, and the same message is never stacked", async () => {
  routeAnswer = () => ({ status: 500, body: { message: 'Graph is still loading' } });
  search().onSelectOrigin(A);
  search().onSelectDestination(place(1));
  await until(() => toasts().length === 1, 'the error');
  search().onSelectDestination(place(2));
  await until(() => backend.routeRequests().length === 2, 'the second request');
  await sleep(150);
  assert.deepEqual(toasts().map((t) => t.text), ['Graph is still loading']);
  assert.equal(routeShown(), null);
  assert.equal(el('BottomActionBar'), null);
  assert.equal(spinner(), false);
});

test('Fastest mode asks both endpoints and picks by the original comparison', async () => {
  routeAnswer = (url: URL) => ({ body: backendBody({ distance_km: url.pathname === '/dynamic-route' ? 7 : 6 }) });
  props('ModeSelector').onSelectMode('fastest');
  search().onSelectOrigin(A);
  for (let n = 1; n <= 5; n++) search().onSelectDestination(place(n));
  await until(() => panel(), 'both routes');
  await settle();
  assert.deepEqual(backend.routeRequests().map((r: any) => r.path).sort(), ['/dynamic-route', '/route']);
  assert.equal(panel().selectedRouteType, 'dynamic'); // 15 min against 16 min
  assert.equal(panel().shortestRouteData.duration_s, 960);
  assert.equal(panel().dynamicRouteData.duration_s, 900);
  assert.equal(toasts().length, 0);
});

test('Fastest mode: starting the other card navigates that route with that card\'s time', async () => {
  routeAnswer = (url: URL) => ({ body: backendBody({ distance_km: url.pathname === '/dynamic-route' ? 7 : 6 }) });
  props('ModeSelector').onSelectMode('fastest');
  await chooseTrip();
  panel().onStartNavigation('shortest');
  await until(() => map().isNavigating, 'start');
  await sleep(30);
  assert.ok(Math.abs(footer().remainingSeconds - 960) < 5, `got ${footer().remainingSeconds}`);
});

// ------------------------------------------------------------------ destination without a start
test("picking a destination with no start uses the rider's location as the start", async () => {
  search().onSelectDestination(B);
  await until(() => routeShown(), 'a route');
  assert.equal(search().origin.name, 'My Location');
  assert.equal(Number(backend.routeRequests()[0].query.from_lat), A.lat);
});

test('a start the rider picks while GPS is still searching is not overwritten by the late GPS answer', async () => {
  browser.gps.hold = true;
  search().onSelectDestination(B);
  search().onSelectOrigin(place(7));
  browser.gps.release();
  await sleep(50);
  assert.equal(search().origin.name, 'Place 7');
});

test('a GPS answer that arrives after Clear does not bring a start point back', async () => {
  browser.gps.hold = true;
  search().onSelectDestination(B);
  search().onClear();
  browser.gps.release();
  await sleep(50);
  assert.equal(search().origin, null);
  assert.equal(search().destination, null);
});

test('when location is denied, the rider is told and nothing is requested', async () => {
  browser.gps.fail = true;
  search().onSelectDestination(B);
  await until(() => toasts().length === 1, 'the location error');
  await settle();
  assert.match(toasts()[0].text, /GPS|location/i);
  assert.equal(backend.routeRequests().length, 0);
});

// ------------------------------------------------------------------ press and hold
const geocodeWith = (answers: (p: any) => Promise<any>) => {
  (globalThis as any).google = { maps: { Geocoder: class { geocode(q: any) { return answers(q.location); } } } };
  (globalThis as any).window.google = (globalThis as any).google;
};

test('press and hold shows a card at once, then fills in the place name, and requests no route', async () => {
  geocodeWith(async () => ({ results: [{ formatted_address: 'MG Road, Ashok Nagar, Bengaluru' }] }));
  map().onLongPress({ lat: B.lat, lng: B.lng });
  assert.equal(props('PlaceSheet').pin.lat, B.lat);
  assert.deepEqual(map().droppedPin, props('PlaceSheet').pin);
  await until(() => props('PlaceSheet').pin.name === 'MG Road', 'the name');
  assert.equal(props('PlaceSheet').resolving, false);
  await settle();
  assert.equal(backend.routeRequests().length, 0);
});

test('a slow name lookup for an earlier pin neither renames the new pin nor ends its spinner', async () => {
  const waiting: ((v: any) => void)[] = [];
  geocodeWith(() => new Promise((resolve) => waiting.push(resolve)));
  map().onLongPress({ lat: A.lat, lng: A.lng });
  map().onLongPress({ lat: B.lat, lng: B.lng });
  waiting[0]({ results: [{ formatted_address: 'Old Place, Bengaluru' }] });
  await sleep(20);
  assert.equal(props('PlaceSheet').pin.name, 'Dropped pin');
  assert.equal(props('PlaceSheet').resolving, true);
  waiting[1]({ results: [{ formatted_address: 'New Place, Bengaluru' }] });
  await until(() => props('PlaceSheet').pin.name === 'New Place', 'the new name');
  assert.equal(props('PlaceSheet').resolving, false);
});

test('Directions on a pin: route from my location to the pin, card closed', async () => {
  map().onLongPress({ lat: B.lat, lng: B.lng });
  props('PlaceSheet').onAction('directions');
  await until(() => routeShown(), 'a route');
  assert.equal(props('PlaceSheet').pin, null);
  assert.equal(map().droppedPin, null);
  assert.equal(search().origin.name, 'My Location');
  assert.equal(search().destination.lat, B.lat);
  assert.equal(backend.routeRequests().length, 1);
});

test('Start here on a pin keeps the destination and routes from the pin', async () => {
  await chooseTrip();
  backend.requests.length = 0;
  map().onLongPress({ lat: place(3).lat, lng: place(3).lng });
  props('PlaceSheet').onAction('start_here');
  await until(() => backend.routeRequests().length === 1, 'a new request');
  assert.equal(Number(backend.routeRequests()[0].query.from_lat), place(3).lat);
  assert.equal(Number(backend.routeRequests()[0].query.to_lat), B.lat);
});

test('closing the card removes the pin and changes nothing', () => {
  map().onLongPress({ lat: B.lat, lng: B.lng });
  props('PlaceSheet').onClose();
  assert.equal(map().droppedPin, null);
  assert.equal(search().destination, null);
});

// ------------------------------------------------------------------ a whole ride
test('full ride: guidance, voice, speed and arrival time, arrival, Done returns to the start screen', async () => {
  map().onLongPress({ lat: B.lat, lng: B.lng });
  await startTrip();
  assert.equal(el('PlaceSheet'), null, 'no pin card while navigating');
  assert.equal(map().droppedPin, null);
  assert.equal(el('TopSearchBar'), null);
  assert.equal(el('BottomActionBar'), null);
  assert.equal(toasts().length, 0, 'no warning that the server sent no turns');
  await until(() => backend.requests.some((r: any) => r.path === '/journeys/journey-1/start'), 'journey start');

  await sleep(20);
  assert.ok(Math.abs(footer().remainingSeconds - 180) < 5, `planned 3 min, got ${footer().remainingSeconds}`);
  assert.ok(Math.abs(footer().arrivalMs - Date.now() - 180000) < 5000, 'arrival clock = now + 3 min');
  assert.ok(Math.abs(footer().remainingMeters - 1200) < 15);

  rideTo(40, 200);
  assert.ok(footer().speedKmh >= 24 && footer().speedKmh <= 29, `8 m/s is about 29 km/h, got ${footer().speedKmh}`);
  assert.ok(Math.abs(footer().remainingMeters - 1000) < 40, `got ${footer().remainingMeters}`);
  assert.equal(banner().currentManeuver.type, 'turn_right');
  assert.ok(Math.abs(banner().distanceToManeuverMeters - 400) < 45, `got ${banner().distanceToManeuverMeters}`);

  rideTo(240, 590, 20, { seconds: 3 });
  await until(() => spoken().some((s) => /^In \d+ metres, turn right$/.test(s)), 'the early warning');
  await until(() => spoken().includes('Turn right'), 'the instruction at the turn');

  rideTo(620, 1100, 40);
  assert.equal(banner().currentManeuver.type, 'arrive');
  assert.ok(footer().remainingSeconds < 60, `almost there, got ${footer().remainingSeconds}`);

  rideTo(1160, 1198, 20);
  await until(() => props('ArrivalModal').summary, 'the arrival card');
  const summary = props('ArrivalModal').summary;
  assert.equal(summary.destinationName, 'Work');
  assert.ok(summary.distanceKm > 1.0 && summary.distanceKm < 1.3, `distance ${summary.distanceKm}`);
  await until(() => spoken().includes('You have arrived'), 'the arrival message');
  assert.equal(map().isNavigating, false);
  await until(() => backend.requests.some((r: any) => r.path === '/journeys/journey-1/complete'), 'journey complete');

  browser.events.length = 0;
  props('ArrivalModal').onDone();
  await sleep(200);
  assert.equal(props('ArrivalModal').summary, null);
  assert.equal(search().origin, null);
  assert.equal(search().destination, null);
  assert.equal(routeShown(), null);
  assert.equal(el('BottomActionBar'), null);
  assert.equal(el('NavigationFooter'), null);
  assert.ok(browser.events.includes('recenter-map'));
});

test('when the drawn route is shorter than the reported distance, progress still follows the drawn route', async () => {
  routeAnswer = () => ({ body: backendBody({ distance_km: 1.8 }) }); // the line on screen is 1.2 km
  await startTrip();
  await sleep(20);
  assert.ok(Math.abs(footer().remainingMeters - 1200) < 15, `before the first fix: ${footer().remainingMeters}`);
  // 1.8 km at 24 km/h = 4.5, shown as 5 min
  assert.ok(Math.abs(footer().remainingSeconds - 300) < 5, `got ${footer().remainingSeconds}`);
  ride(10, { seconds: 1 });
  assert.ok(Math.abs(footer().remainingSeconds - 297) < 6, `no jump on the first fix: ${footer().remainingSeconds}`);
});

test('a second trip gets a fresh arrival time and distance', async () => {
  await startTrip();
  rideTo(100, 1100, 100, { seconds: 12 });
  rideTo(1160, 1198, 20);
  await until(() => props('ArrivalModal').summary, 'arrival');
  props('ArrivalModal').onDone();
  await sleep(100);
  ride(0, { speed: 0 }); // the next trip begins where this route starts
  await startTrip();
  await sleep(20);
  assert.ok(Math.abs(footer().remainingSeconds - 180) < 5, `got ${footer().remainingSeconds}`);
  assert.ok(Math.abs(footer().remainingMeters - 1200) < 15, `got ${footer().remainingMeters}`);
});

test('ending a trip part way stops speech, and starting again shows the whole distance', async () => {
  await startTrip();
  rideTo(100, 900, 200, { seconds: 15 });
  footer().onEndNavigation();
  await until(() => !map().isNavigating, 'navigation to end');
  assert.ok((globalThis as any).__tts.stops > 0);
  clock.advance(60000);
  ride(0, { speed: 0 }); // back at the start
  panel().onStartNavigation();
  await until(() => map().isNavigating, 'a new start');
  await sleep(20);
  assert.ok(Math.abs(footer().remainingMeters - 1200) < 15, `got ${footer().remainingMeters}`);
  assert.ok(Math.abs(footer().remainingSeconds - 180) < 5, `got ${footer().remainingSeconds}`);
});

// ------------------------------------------------------------------ rerouting
test('leaving the route reroutes from where the rider is and says so', async () => {
  await startTrip();
  ride(50);
  ride(100);
  backend.requests.length = 0;
  leaveRoute();
  await until(() => backend.routeRequests().length === 1, 'a reroute request');
  assert.ok(Math.abs(Number(backend.routeRequests()[0].query.from_lng) - at(150, 170).longitude) < 0.0008);
  await until(() => spoken().includes('New route found'), 'the new route');
  assert.ok(spoken().includes('Rerouting'));
  assert.equal(map().isNavigating, true);
  assert.equal(toasts().length, 0);
});

test('a failed reroute keeps the route, and tries again while the rider stays off it', async () => {
  await startTrip();
  ride(50);
  backend.requests.length = 0;
  routeAnswer = () => ({ status: 500, body: { message: 'busy' } });
  leaveRoute();
  await until(() => toasts().length === 1, 'the warning');
  assert.deepEqual(routeShown(), PATH);
  assert.equal(map().isNavigating, true);
  routeAnswer = ok;
  clock.advance(20000);
  leaveRoute();
  await until(() => backend.routeRequests().length === 2, 'a second attempt');
});

test('End during a reroute: the late answer is ignored, nothing is announced, no error appears', async () => {
  await startTrip();
  ride(50);
  const rerouted = [[north(150), east(-170)], [north(600), east(-170)], [north(600), east(600)]];
  routeAnswer = () => ({ body: backendBody({ path: rerouted }), delayMs: 300 });
  backend.requests.length = 0;
  leaveRoute();
  await until(() => backend.routeRequests().length === 1, 'a reroute request');
  routeAnswer = ok;
  footer().onEndNavigation();
  await sleep(900);
  assert.equal(map().isNavigating, false);
  assert.deepEqual(routeShown(), PATH, 'the screen shows the planned trip, not the abandoned reroute');
  assert.equal(spoken().includes('New route found'), false);
  assert.equal(toasts().length, 0);
});

test('End after a reroute: the screen goes back to the route from the chosen start', async () => {
  await startTrip();
  ride(50);
  const rerouted = [[north(150), east(-170)], [north(600), east(-170)], [north(600), east(600)]];
  routeAnswer = () => ({ body: backendBody({ path: rerouted }) });
  leaveRoute();
  await until(() => routeShown()?.length === 3, 'the new route');
  routeAnswer = ok;
  backend.requests.length = 0;
  footer().onEndNavigation();
  await until(() => routeShown()?.length === PATH.length && panel(), 'the planned route again');
  assert.equal(Number(backend.routeRequests()[0].query.from_lat), A.lat);
});

test('when the route cannot get close to a pin, the rider is told how far it stops', async () => {
  routeAnswer = () => ({
    body: backendBody({ origin_snap: { lat: A.lat, lng: A.lng, distance_m: 12 }, destination_snap: { lat: B.lat, lng: B.lng, distance_m: 140 } }),
  });
  await chooseTrip();
  assert.deepEqual(toasts().map((t) => t.text), ['The route ends 140 m from your destination: no public road goes closer.']);
});

test("street names and turns sent by the backend are shown as sent", async () => {
  const maneuvers = [
    { type: 'depart', instruction: 'Depart on First Road', road_name: 'First Road', distance_m: 600, lat: PATH[0][0], lng: PATH[0][1] },
    { type: 'turn_right', instruction: 'Turn right onto 7th Cross', road_name: '7th Cross', distance_m: 600, lat: north(600), lng: east(0) },
    { type: 'arrive', instruction: 'Arrive at destination', road_name: '', distance_m: 0, lat: north(600), lng: east(600) },
  ];
  routeAnswer = () => ({ body: backendBody({ maneuvers, duration_s: 420 }) });
  await startTrip();
  ride(100);
  await sleep(20);
  assert.equal(banner().currentManeuver.road_name, '7th Cross');
  assert.ok(Math.abs(footer().remainingSeconds - 420) < 40, `got ${footer().remainingSeconds}`);
});

// ------------------------------------------------------------------ voice and incidents
test('muting from the banner: nothing more is spoken', async () => {
  await startTrip();
  ride(50);
  banner().onToggleVoice();
  const count = spoken().length;
  rideTo(240, 590, 20, { seconds: 3 });
  await sleep(120);
  assert.equal(spoken().length, count);
});

test('a phone that cannot speak tells the rider once', async () => {
  (globalThis as any).__tts.failSpeak = 'no voice data';
  await startTrip();
  rideTo(240, 590, 20, { seconds: 3 });
  await until(() => toasts().some((t) => /Voice guidance/.test(t.text)), 'the warning');
  await sleep(100);
  assert.equal(toasts().length, 1);
});

test('incidents from the server reach the map, and a failed report is shown to the rider', async () => {
  incidentAnswer = () => ({
    body: { status: 'ok', incidents: [{ id: 'i1', type: 'crash', title: 'Crash', lat: A.lat, lng: A.lng }] },
  });
  app.unmount();
  app = render(Page, {});
  await until(() => map().activeIncidents.length === 1, 'the incident');
  await startTrip();
  props('IncidentReportModal').onReportFailed();
  assert.ok(toasts().some((t) => /report/i.test(t.text)));
});

test('no request in these journeys left the machine', () => {
  assert.deepEqual(net.blocked, []);
});
