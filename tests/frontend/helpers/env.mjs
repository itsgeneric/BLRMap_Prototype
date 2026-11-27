// Fake browser + phone, a stand-in backend (real HTTP), and a guard that blocks every request leaving the machine.
import http from 'node:http';

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** wait until `check()` is truthy (for debounced / network-driven updates) */
export async function until(check, what = 'condition', timeoutMs = 3000) {
  const end = performance.now() + timeoutMs;
  for (;;) {
    const value = check();
    if (value) return value;
    if (performance.now() > end) throw new Error(`timed out waiting for ${what}`);
    await sleep(10);
  }
}

/** Date.now() that a test can move forward */
export function installClock() {
  const real = Date.now.bind(Date);
  let offset = 0;
  Date.now = () => real() + offset;
  return { advance: (ms) => (offset += ms), restore: () => (Date.now = real) };
}

export function installBrowser({ search = '' } = {}) {
  const target = new EventTarget();
  const events = [];
  const store = new Map();
  const localStorage = {
    getItem: (k) => store.get(k) ?? null,
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
  };
  const window = {
    location: { search },
    localStorage,
    addEventListener: target.addEventListener.bind(target),
    removeEventListener: target.removeEventListener.bind(target),
    dispatchEvent(e) {
      events.push(e.type);
      return target.dispatchEvent(e);
    },
  };

  const gps = {
    watchers: new Map(),
    nextId: 1,
    /** what getCurrentPosition answers; set `hold` to answer later through release() */
    current: { latitude: 12.9, longitude: 77.5, accuracy: 8, speed: null, heading: null },
    fail: false,
    hold: false,
    held: [],
    emit(coords, timestamp = Date.now()) {
      const pos = { coords: { accuracy: 8, speed: null, heading: null, ...coords }, timestamp };
      for (const ok of this.watchers.values()) ok(pos);
    },
    release() {
      this.held.splice(0).forEach((fn) => fn());
    },
  };
  const geolocation = {
    watchPosition(ok) {
      const id = gps.nextId++;
      gps.watchers.set(id, ok);
      return id;
    },
    clearWatch: (id) => gps.watchers.delete(id),
    getCurrentPosition(ok, fail) {
      const answer = () =>
        gps.fail ? fail({ code: 1, message: 'denied' }) : ok({ coords: { ...gps.current }, timestamp: Date.now() });
      if (gps.hold) gps.held.push(answer);
      else setTimeout(answer, 0);
    },
  };

  const define = (name, value) => Object.defineProperty(globalThis, name, { value, configurable: true, writable: true });
  define('window', window);
  define('localStorage', localStorage);
  define('navigator', { geolocation, vibrate: () => true });
  return { window, gps, events, listen: (type, fn) => target.addEventListener(type, fn) };
}

/**
 * Stand-in for the Python backend, speaking the response shape in frontend/lib/types.ts.
 * `handler(url)` returns { status?, body?, delayMs? }.
 */
export async function startBackend(handler) {
  const requests = [];
  const sockets = new Set();
  const api = { requests, handler };
  const server = http.createServer((req, res) => {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', async () => {
      const url = new URL(req.url, 'http://x');
      requests.push({ method: req.method, path: url.pathname, query: Object.fromEntries(url.searchParams), body: raw });
      if (req.method === 'OPTIONS') return res.writeHead(204).end();
      const answer = (await api.handler(url, req.method)) || { body: { status: 'success' } };
      if (answer.delayMs) await sleep(answer.delayMs);
      if (res.destroyed) return;
      res.writeHead(answer.status || 200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(answer.body));
    });
  });
  server.on('connection', (s) => {
    sockets.add(s);
    s.on('close', () => sockets.delete(s));
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  api.url = `http://127.0.0.1:${server.address().port}`;
  api.routeRequests = () => requests.filter((r) => r.path === '/route' || r.path === '/dynamic-route');
  api.close = () =>
    new Promise((r) => {
      sockets.forEach((s) => s.destroy());
      server.close(() => r());
    });
  return api;
}

/** Only 127.0.0.1 may be reached for real. Anything else goes to `external`, or fails the test. */
export function guardNetwork(external) {
  const real = globalThis.fetch;
  const blocked = [];
  globalThis.fetch = (input, init) => {
    const url = new URL(typeof input === 'string' ? input : input.url);
    if (url.hostname === '127.0.0.1') return real(input, init);
    if (external) return external(url, init);
    blocked.push(url.href);
    return Promise.reject(new Error(`test blocked an external request: ${url.hostname}`));
  };
  return { blocked, restore: () => (globalThis.fetch = real) };
}

// ---------------------------------------------------------------- a route with one right turn
// 600 m north along one road, then 600 m east along another.
export const M_PER_DEG_LAT = 111195;
const LAT0 = 12.9;
const LNG0 = 77.5;
const mPerDegLng = M_PER_DEG_LAT * Math.cos((LAT0 * Math.PI) / 180);
export const north = (m) => LAT0 + m / M_PER_DEG_LAT;
export const east = (m) => LNG0 + m / mPerDegLng;
export const PATH = [
  ...[0, 100, 200, 300, 400, 500, 600].map((m) => [north(m), east(0)]),
  ...[100, 200, 300, 400, 500, 600].map((m) => [north(600), east(m)]),
];
export const MANEUVERS = [
  { type: 'depart', instruction: 'Head north on First Road', road_name: 'First Road', distance_m: 600, lat: north(0), lng: east(0) },
  { type: 'turn_right', instruction: 'Turn right onto Second Road', road_name: 'Second Road', distance_m: 600, lat: north(600), lng: east(0) },
  { type: 'arrive', instruction: 'You will arrive at your destination', road_name: '', distance_m: 0, lat: north(600), lng: east(600), side: 'left' },
];
export const routeBody = (extra = {}) => ({
  status: 'success',
  journey_id: 'journey-1',
  path: PATH,
  distance_km: 1.2,
  duration_mins: 4,
  maneuvers: MANEUVERS,
  ...extra,
});
/** a position `along` metres down the route, optionally pushed `offM` metres west */
export function at(along, offM = 0) {
  if (along <= 600) return { latitude: north(along), longitude: east(-offM) };
  return { latitude: north(600 + offM), longitude: east(along - 600) };
}

/** exactly what this repo's backend answers: no travel time, no turn list */
export const backendBody = (extra = {}) => ({
  status: 'success',
  journey_id: 'journey-1',
  path: PATH,
  distance_km: 1.2,
  ...extra,
});
