// The cards, banner, route panel, footer and incident report, rendered with the real component code.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';
import { render, find, findAll, textOf, nameOf } from './helpers/fakes/react.mjs';
import { installBrowser, guardNetwork, startBackend, sleep, until, backendBody } from './helpers/env.mjs';

let C: any = {};
let backend: any;
let net: any;
let formatClock: any;
let completeRoute: any;
let reportAnswer: () => any;
const posts = () => backend.requests.filter((r: any) => r.method === 'POST' && r.path === '/incidents');

before(async () => {
  installBrowser();
  (globalThis as any).document = Object.assign(new EventTarget(), { hidden: false });
  backend = await startBackend(() => reportAnswer());
  process.env.NEXT_PUBLIC_API_BASE = backend.url;
  net = guardNetwork();
  for (const name of ['PlaceSheet', 'ArrivalModal', 'NavigationFooter', 'TurnByTurnBanner', 'BottomActionBar', 'IncidentReportModal']) {
    C[name] = (await import(`../../components/Navigation/${name}.tsx`))[name];
  }
  C.ToastContainer = (await import('../../components/UI/Toast.tsx')).ToastContainer;
  ({ formatClock } = await import('../../lib/eta.ts'));
  ({ completeRoute } = await import('../../lib/routeInfo.ts'));
});
beforeEach(() => {
  backend.requests.length = 0;
  reportAnswer = () => ({ body: { status: 'ok', incident: { id: 'i1', title: 'Crash', type: 'crash', lat: 1, lng: 2 } } });
});
test.after(async () => {
  await backend.close();
  net.restore();
});

const buttons = (tree: any) => findAll(tree, (e: any) => e.type === 'button');
const button = (tree: any, label: RegExp) =>
  buttons(tree).find((b: any) => label.test(textOf(b)) || label.test(b.props['aria-label'] || ''));
const pin = { lat: 12.97012, lng: 77.59034, name: 'MG Road', address: 'MG Road, Bengaluru' };

// ------------------------------------------------------------------ dropped pin
test('PlaceSheet shows nothing without a pin', () => {
  assert.equal(C.PlaceSheet({ pin: null }), null);
});

test('PlaceSheet shows the place; its buttons send the right actions', () => {
  const actions: string[] = [];
  let closed = 0;
  const tree = C.PlaceSheet({ pin, resolving: false, hasOrigin: false, onAction: (a: string) => actions.push(a), onClose: () => closed++ });
  assert.match(textOf(tree), /MG Road.*Directions.*Start here.*current location/s);
  button(tree, /Directions/).props.onClick();
  button(tree, /Start here/).props.onClick();
  button(tree, /Close/).props.onClick();
  assert.deepEqual(actions, ['directions', 'start_here']);
  assert.equal(closed, 1);
});

test('PlaceSheet drops the location note when a start exists, and falls back to coordinates', () => {
  const tree = C.PlaceSheet({ pin: { lat: 12.97012, lng: 77.59034 }, resolving: true, hasOrigin: true });
  assert.doesNotMatch(textOf(tree), /current location/);
  assert.match(textOf(tree), /Dropped pin.*12\.97012, 77\.59034/s);
});

// ------------------------------------------------------------------ arrival and footer
const summary = { destinationName: 'Work', originName: 'Home', distanceKm: 5.25, timeTakenSec: 900, avgSpeedKmh: 21.4 };

test('the arrival card shows the trip and has exactly one button, Done', () => {
  let done = 0;
  const tree = C.ArrivalModal({ summary, onDone: () => done++ });
  assert.equal(buttons(tree).length, 1);
  assert.match(textOf(tree), /You have arrived.*Work.*5\.3 km.*15 min.*21 km\/h.*Done/s);
  buttons(tree)[0].props.onClick();
  assert.equal(done, 1);
  assert.equal(C.ArrivalModal({ summary: null, onDone() {} }), null);
});

const footer = (extra: object = {}) =>
  C.NavigationFooter({
    remainingSeconds: 600, remainingMeters: 3400, arrivalMs: 0, speedKmh: 27, isFollowingCamera: true,
    onRecenter() {}, onEndNavigation() {}, ...extra,
  });

test("the footer shows speed, time left, the estimator's arrival time and distance", () => {
  const arrivalMs = new Date(2026, 10, 25, 18, 42).getTime();
  const text = textOf(footer({ arrivalMs }));
  assert.match(text, /27km\/h/);
  assert.match(text, /10 min/);
  assert.match(text, /3\.4 km remaining/);
  assert.ok(text.includes(formatClock(arrivalMs)), text);
});

test('before the first estimate the footer shows a dash, not a made-up time', () => {
  assert.match(textOf(footer()), /–/);
  assert.doesNotMatch(textOf(footer()), /10 min/);
});

test('Re-center appears only when the camera is not following; End is always there', () => {
  assert.doesNotMatch(textOf(footer()), /Re-center/);
  let ended = 0;
  const tree = footer({ isFollowingCamera: false, onEndNavigation: () => ended++ });
  assert.match(textOf(tree), /Re-center/);
  button(tree, /End navigation/).props.onClick();
  assert.equal(ended, 1);
});

// ------------------------------------------------------------------ turn banner
const turn = { type: 'turn_right', instruction: 'Turn right', road_name: 'Unnamed Road', distance_m: 100, lat: 0, lng: 0 };
const arrive = { ...turn, type: 'arrive', instruction: 'Arrive at your destination' };
const bannerTree = (extra: object) =>
  C.TurnByTurnBanner({
    currentManeuver: turn, nextManeuver: arrive, distanceToManeuverMeters: 240, navState: 'following',
    voiceEnabled: true, onToggleVoice() {}, ...extra,
  });

test('the banner names the next turn and the distance, with what follows, and never shows "Unnamed Road"', () => {
  const text = textOf(bannerTree({}));
  assert.match(text, /Turn right/);
  assert.match(text, /m/);
  assert.match(text, /Then/);
  assert.doesNotMatch(text, /Unnamed/);
});

test('off route and rerouting replace the old instruction', () => {
  assert.match(textOf(bannerTree({ navState: 'rerouting' })), /Rerouting/);
  const off = textOf(bannerTree({ navState: 'off_route' }));
  assert.match(off, /off route/);
  assert.doesNotMatch(off, /Turn right/);
});

test('the voice button works in every banner state and says what it will do', () => {
  for (const navState of ['following', 'rerouting', 'off_route']) {
    let toggled = 0;
    const tree = bannerTree({ navState, onToggleVoice: () => toggled++ });
    button(tree, /Mute voice guidance/).props.onClick();
    assert.equal(toggled, 1, navState);
  }
  assert.ok(button(bannerTree({ voiceEnabled: false }), /Turn on voice guidance/));
});

// ------------------------------------------------------------------ route panel
const route = (extra: object = {}) => completeRoute(backendBody(extra));
const panel = (extra: object) =>
  render(C.BottomActionBar, {
    routeData: route(), mode: 'shortest', isOriginMyLocation: true,
    onSelectRouteType() {}, onStartNavigation() {}, onStartPreview() {}, ...extra,
  });

test('the route panel shows the original travel time and the estimated steps', () => {
  const view = panel({});
  assert.match(textOf(view.result()), /3 min.*1\.2 km.*3 maneuvers/s);
  button(view.result(), /Steps/).props.onClick();
  assert.match(textOf(view.result()), /Turn right/);
});

test('starting from my location offers Start; from elsewhere it offers a preview', () => {
  let started = 0;
  button(panel({ onStartNavigation: () => started++ }).result(), /Start Navigation/).props.onClick();
  assert.equal(started, 1);
  const elsewhere = panel({ isOriginMyLocation: false }).result();
  assert.ok(button(elsewhere, /Preview Route/));
  assert.equal(button(elsewhere, /Start Navigation/), undefined);
});

test('comparison cards show each time and which route saves how much', () => {
  const chosen: string[] = [];
  const shortestRouteData = { ...route({ distance_km: 6 }), duration_s: 960 };
  const dynamicRouteData = { ...route({ distance_km: 7 }), duration_s: 900 };
  const tree = panel({
    mode: 'fastest', routeData: dynamicRouteData, shortestRouteData, dynamicRouteData, selectedRouteType: 'dynamic',
    onStartNavigation: (t: string) => chosen.push(t),
  }).result();
  assert.match(textOf(tree), /Dynamic saves 1 min/);
  assert.match(textOf(tree), /16 min.*6\.0 km.*15 min.*7\.0 km/s);
  button(tree, /Start Navigation \(Shortest\)/).props.onClick();
  button(tree, /Start Navigation \(Dynamic\)/).props.onClick();
  assert.deepEqual(chosen, ['shortest', 'dynamic']);
});

test('the panel renders nothing without a route', () => {
  assert.equal(panel({ routeData: null }).result(), null);
});

// ------------------------------------------------------------------ incident report
function report(t: any, extra: object = {}) {
  t.mock.timers.enable({ apis: ['setInterval'] });
  const calls = { reported: 0, failed: 0 };
  const view = render(C.IncidentReportModal, {
    isNavigating: true, currentLat: 12.9, currentLng: 77.5, currentHeading: 90,
    onIncidentReported: () => calls.reported++, onReportFailed: () => calls.failed++, ...extra,
  });
  const open = () => find(view.result(), (e: any) => e.type === 'button').props.onClick();
  const choose = (label: RegExp) => button(view.result(), label).props.onClick();
  const tick = (seconds: number) => {
    for (let i = 0; i < seconds; i++) t.mock.timers.tick(1000);
  };
  return { view, calls, open, choose, tick };
}

test('the report button exists only during a trip', () => {
  assert.equal(render(C.IncidentReportModal, { isNavigating: false }).result(), null);
});

test('a report is sent exactly once when the countdown ends', async (t) => {
  const r = report(t);
  r.open();
  r.choose(/Crash/);
  r.tick(4);
  await sleep(30);
  assert.equal(posts().length, 0);
  r.tick(3);
  await until(() => r.calls.reported === 1, 'the report to be confirmed');
  await sleep(150);
  assert.equal(posts().length, 1);
  assert.equal(JSON.parse(posts()[0].body).type, 'crash');
  assert.deepEqual(r.calls, { reported: 1, failed: 0 });
});

test('Undo sends nothing', async (t) => {
  const r = report(t);
  r.open();
  r.choose(/Crash/);
  r.tick(2);
  button(r.view.result(), /Undo/).props.onClick();
  r.tick(10);
  await sleep(50);
  assert.equal(posts().length, 0);
});

test('Done sends at once, and only once', async (t) => {
  const r = report(t);
  r.open();
  r.choose(/Crash/);
  button(r.view.result(), /Done/).props.onClick();
  r.tick(10);
  await until(() => posts().length >= 1, 'the report');
  await sleep(150);
  assert.equal(posts().length, 1);
});

test('the rider is told when the server refuses the report', async (t) => {
  reportAnswer = () => ({ status: 503, body: { status: 'error', message: 'database off' } });
  const r = report(t);
  r.open();
  r.choose(/Crash/);
  r.tick(5);
  await until(() => r.calls.failed === 1, 'the failure to be reported');
  assert.deepEqual(r.calls, { reported: 0, failed: 1 });
});

test('the rider is told when there is no position to report', async (t) => {
  const r = report(t, { currentLat: undefined, currentLng: undefined });
  r.open();
  r.choose(/Crash/);
  r.tick(5);
  await sleep(30);
  assert.equal(posts().length, 0);
  assert.equal(r.calls.failed, 1);
});

// ------------------------------------------------------------------ messages
test('long messages wrap instead of being cut off, and can be dismissed', () => {
  const dismissed: string[] = [];
  const text = 'The routing server took too long to answer. Try again.';
  const tree = C.ToastContainer({ toasts: [{ id: '1', type: 'error', text }], onDismiss: (id: string) => dismissed.push(id) });
  const span = find(tree, (e: any) => e.type === 'span' && textOf(e) === text);
  assert.doesNotMatch(span.props.className, /truncate/);
  buttons(tree)[0].props.onClick();
  assert.deepEqual(dismissed, ['1']);
});
