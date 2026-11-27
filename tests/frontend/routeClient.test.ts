// Integration tests: the real route client against a real local HTTP server.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import type { AddressInfo } from 'node:net';
import { requestRoute } from '../../lib/routeClient.ts';

const FROM = { lat: 12.9237, lng: 77.5714 };
const TO = { lat: 12.9756, lng: 77.6066 };

let server: http.Server;
let base = '';
let behaviour: (req: http.IncomingMessage, res: http.ServerResponse) => void = () => {};
const seen: string[] = [];

before(async () => {
  server = http.createServer((req, res) => {
    seen.push(req.url || '');
    behaviour(req, res);
  });
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});

after(async () => {
  server.closeAllConnections?.();
  await new Promise<void>((resolve) => server.close(() => resolve()));
});

const json = (res: http.ServerResponse, status: number, body: unknown) => {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(body));
};
const fast = { baseUrl: '', fetchImpl: fetch, retryDelaysMs: [5, 5] };
const opts = (extra: object = {}) => ({ ...fast, baseUrl: base, ...extra });

test('a good answer comes back unchanged, and the request carries the right path and coordinates', async () => {
  seen.length = 0;
  behaviour = (_req, res) => json(res, 200, { status: 'success', path: [[1, 2], [3, 4]], distance_km: 5.5, duration_s: 600 });
  const r = await requestRoute(opts(), 'dynamic', FROM, TO);
  assert.equal(r.status, 'success');
  assert.equal(r.distance_km, 5.5);
  assert.equal(r.duration_s, 600);
  assert.equal(seen.length, 1);
  const url = new URL(seen[0], base);
  assert.equal(url.pathname, '/dynamic-route');
  assert.equal(url.searchParams.get('from_lat'), '12.9237');
  assert.equal(url.searchParams.get('to_lng'), '77.6066');
});

test('shortest mode uses /route', async () => {
  seen.length = 0;
  behaviour = (_req, res) => json(res, 200, { status: 'success', path: [[1, 2]], distance_km: 1 });
  await requestRoute(opts(), 'shortest', FROM, TO);
  assert.equal(new URL(seen[0], base).pathname, '/route');
});

test('an error the server explains is passed on as it is, with no retry', async () => {
  seen.length = 0;
  behaviour = (_req, res) => json(res, 200, { status: 'error', message: 'No road within 500 m of the start point.' });
  const r = await requestRoute(opts(), 'dynamic', FROM, TO);
  assert.equal(r.status, 'error');
  assert.equal(r.message, 'No road within 500 m of the start point.');
  assert.ok(!r.aborted);
  assert.equal(seen.length, 1);
});

test('an HTTP 500 gives a readable message and is not retried', async () => {
  seen.length = 0;
  behaviour = (_req, res) => {
    res.writeHead(500);
    res.end('boom');
  };
  const r = await requestRoute(opts(), 'dynamic', FROM, TO);
  assert.equal(r.status, 'error');
  assert.match(r.message || '', /500/);
  assert.equal(seen.length, 1, 'a server error is not a network failure: no retry');
});

test('a 422 with a detail field uses the detail text', async () => {
  behaviour = (_req, res) => json(res, 422, { detail: 'from_lat is required' });
  const r = await requestRoute(opts(), 'dynamic', FROM, TO);
  assert.equal(r.message, 'from_lat is required');
});

test('a reply that is not JSON is reported as unreadable, not as a crash', async () => {
  behaviour = (_req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<html>proxy error</html>');
  };
  const r = await requestRoute(opts(), 'dynamic', FROM, TO);
  assert.equal(r.status, 'error');
  assert.match(r.message || '', /unreadable/i);
});

test('network failures are retried and the third attempt can succeed', async () => {
  let calls = 0;
  const flaky: typeof fetch = async (input, init) => {
    calls += 1;
    if (calls < 3) throw new TypeError('Failed to fetch');
    return fetch(input, init);
  };
  behaviour = (_req, res) => json(res, 200, { status: 'success', path: [[1, 2]], distance_km: 2 });
  const r = await requestRoute(opts({ fetchImpl: flaky }), 'dynamic', FROM, TO);
  assert.equal(r.status, 'success');
  assert.equal(calls, 3);
});

test('a server that is really down gives the "can\'t reach" message after the retries', async () => {
  let calls = 0;
  const down: typeof fetch = async () => {
    calls += 1;
    throw new TypeError('Failed to fetch');
  };
  const r = await requestRoute(opts({ fetchImpl: down }), 'dynamic', FROM, TO);
  assert.equal(r.status, 'error');
  assert.match(r.message || '', /can't reach the routing server/i);
  assert.ok(!r.aborted);
  assert.equal(calls, 3, 'one try plus two retries');
});

test('a closed port is reported as unreachable (real connection refused)', async () => {
  const r = await requestRoute({ ...opts(), baseUrl: 'http://127.0.0.1:9' }, 'dynamic', FROM, TO);
  assert.match(r.message || '', /can't reach/i);
});

test('a slow server gives a timeout message, which is different from "unreachable"', async () => {
  behaviour = () => {
    /* never answers */
  };
  const r = await requestRoute(opts({ timeoutMs: 80 }), 'dynamic', FROM, TO);
  assert.equal(r.status, 'error');
  assert.match(r.message || '', /took too long/i);
  assert.ok(!r.aborted);
});

test('a request cancelled by the caller is marked aborted and carries NO error to show', async () => {
  behaviour = () => {
    /* never answers */
  };
  const controller = new AbortController();
  const pending = requestRoute(opts(), 'dynamic', FROM, TO, controller.signal);
  setTimeout(() => controller.abort(), 30);
  const r = await pending;
  assert.equal(r.aborted, true);
  assert.equal(r.status, 'error');
});

test('cancelling before the request starts does not even contact the server', async () => {
  seen.length = 0;
  const controller = new AbortController();
  controller.abort();
  const r = await requestRoute(opts(), 'dynamic', FROM, TO, controller.signal);
  assert.equal(r.aborted, true);
  assert.equal(seen.length, 0);
});

test('cancelling during the retry wait stops the retries', async () => {
  let calls = 0;
  const down: typeof fetch = async () => {
    calls += 1;
    throw new TypeError('Failed to fetch');
  };
  const controller = new AbortController();
  const pending = requestRoute(opts({ fetchImpl: down, retryDelaysMs: [200, 200] }), 'dynamic', FROM, TO, controller.signal);
  setTimeout(() => controller.abort(), 40);
  const r = await pending;
  assert.equal(r.aborted, true);
  assert.equal(calls, 1);
});

test('spamming: twenty rapid requests where each cancels the one before; only the last one answers normally', async () => {
  behaviour = (_req, res) => setTimeout(() => json(res, 200, { status: 'success', path: [[1, 2]], distance_km: 1 }), 40);
  let controller = new AbortController();
  const outcomes: Awaited<ReturnType<typeof requestRoute>>[] = [];
  const all: Promise<void>[] = [];
  for (let i = 0; i < 20; i++) {
    controller.abort();
    controller = new AbortController();
    all.push(requestRoute(opts(), 'dynamic', FROM, TO, controller.signal).then((r) => void outcomes.push(r)));
  }
  await Promise.all(all);
  const aborted = outcomes.filter((o) => o.aborted).length;
  const answered = outcomes.filter((o) => o.status === 'success').length;
  const errorsToShow = outcomes.filter((o) => o.status === 'error' && !o.aborted).length;
  assert.equal(answered, 1);
  assert.equal(aborted, 19);
  assert.equal(errorsToShow, 0, 'a superseded request must never produce an error message');
});
/** answers the headers, then never finishes the body */
const stall = (_req: http.IncomingMessage, res: http.ServerResponse) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.write('{"status":');
};

test('cancelled while the answer is still downloading: aborted, with no error to show', async () => {
  behaviour = stall;
  const controller = new AbortController();
  const pending = requestRoute(opts(), 'shortest', FROM, TO, controller.signal);
  setTimeout(() => controller.abort(), 80);
  const r = await pending;
  assert.equal(r.aborted, true);
});

test('an answer that stalls half way is reported as slow, not as unreadable', async () => {
  behaviour = stall;
  const r = await requestRoute(opts({ timeoutMs: 120 }), 'shortest', FROM, TO);
  assert.match(r.message!, /too long/);
});
