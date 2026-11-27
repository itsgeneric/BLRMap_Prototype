// Layout check in a REAL browser (headless Edge or Chrome) at phone sizes, with no extra packages.
//
//   npm run build            (with NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000)
//   node tests/ui/layout.e2e.mjs [folder-for-screenshots]
//
// It serves out/ itself and runs a stand-in backend on port 8000 (stop your real one first). Every other host is blocked, so
// Google is never called: the map itself stays blank, and only the app's own controls are checked. For each screen it checks
// that every control can really be tapped (nothing on top of it), stays inside the screen, and is not tiny.
import http from 'node:http';
import { spawn } from 'node:child_process';
import { readFileSync, existsSync, writeFileSync, mkdirSync, mkdtempSync, rmSync, statSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const shots = path.resolve(process.argv[2] || path.join(os.tmpdir(), 'blrnav-ui-shots'));
mkdirSync(shots, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ------------------------------------------------------------------ the app and a stand-in backend
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.json': 'application/json' };
const site = http.createServer((req, res) => {
  let file = path.join(root, 'out', decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (existsSync(file) && statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!existsSync(file)) return res.writeHead(404).end();
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  res.end(readFileSync(file));
});

const M = 111195;
const LAT = 12.9716;
const LNG = 77.5946;
const ROUTE = [
  ...[0, 100, 200, 300, 400, 500, 600].map((m) => [LAT + m / M, LNG]),
  ...[100, 200, 300, 400, 500, 600].map((m) => [LAT + 600 / M, LNG + m / (M * Math.cos((LAT * Math.PI) / 180))]),
];
let failRoutes = false;
const backend = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  const send = (status, body) => {
    res.writeHead(status, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*' });
    res.end(JSON.stringify(body));
  };
  if (req.method === 'OPTIONS') return send(200, {});
  if (url.pathname === '/search') {
    return send(200, { results: [{ name: 'Brigade Road', address: 'Brigade Road, Ashok Nagar, Bengaluru 560001', lat: ROUTE.at(-1)[0], lng: ROUTE.at(-1)[1] }] });
  }
  if (url.pathname.startsWith('/incidents')) return send(200, { status: 'ok', count: 0, incidents: [] });
  if (url.pathname.startsWith('/journeys')) return send(200, { status: 'ok' });
  if (failRoutes) {
    return send(500, { message: 'The routing server could not finish this request because the road network is still loading. Please try again in a minute.' });
  }
  send(200, { status: 'success', journey_id: 'j1', path: ROUTE, distance_km: url.pathname === '/dynamic-route' ? 7 : 6 });
});

// ------------------------------------------------------------------ a very small DevTools client
const BROWSERS = [
  process.env.BROWSER_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
].filter((p) => p && existsSync(p));

async function launch() {
  const profile = mkdtempSync(path.join(os.tmpdir(), 'blrnav-browser-'));
  const child = spawn(BROWSERS[0], [
    '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--no-first-run', '--disable-extensions',
    '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1', 'about:blank',
  ]);
  const endpoint = await new Promise((resolve, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error(`browser did not start: ${log.slice(-500)}`)), 20000);
    child.stderr.on('data', (d) => {
      log += d;
      const m = log.match(/DevTools listening on (ws:\S+)/);
      if (m) {
        clearTimeout(timer);
        resolve(m[1]);
      }
    });
  });
  const ws = new WebSocket(endpoint);
  await new Promise((r, j) => ((ws.onopen = r), (ws.onerror = j)));
  let id = 0;
  const waiting = new Map();
  const events = [];
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && waiting.has(msg.id)) {
      const { resolve, reject } = waiting.get(msg.id);
      waiting.delete(msg.id);
      msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
    } else if (msg.method) events.push(msg);
  };
  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      waiting.set(++id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params, sessionId }));
    });
  return {
    send,
    events,
    async close() {
      await send('Browser.close').catch(() => {});
      ws.close();
      child.kill();
      await sleep(500);
      try { rmSync(profile, { recursive: true, force: true }); } catch { /* the browser may still hold a file */ }
    },
  };
}

// ------------------------------------------------------------------ run
const problems = [];
const notes = [];

async function main() {
  if (!BROWSERS.length) throw new Error('no Chrome or Edge found; set BROWSER_PATH');
  if (!existsSync(path.join(root, 'out/index.html'))) throw new Error('run `npm run build` first');
  await new Promise((r, j) => backend.once('error', j).listen(8000, '127.0.0.1', r));
  await new Promise((r) => site.listen(3123, '127.0.0.1', r));
  const browser = await launch();
  try {
    for (const [width, height] of [[360, 640], [390, 844], [1280, 800]]) await journey(browser, width, height);
  } finally {
    await browser.close();
  }
}

async function journey(browser, width, height) {
  const size = `${width}x${height}`;
  failRoutes = false;
  const { browserContextId } = await browser.send('Target.createBrowserContext');
  await browser.send('Browser.grantPermissions', { origin: 'http://127.0.0.1:3123', permissions: ['geolocation'], browserContextId });
  const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank', browserContextId });
  const { sessionId } = await browser.send('Target.attachToTarget', { targetId, flatten: true });
  const cdp = (method, params) => browser.send(method, params, sessionId);
  await cdp('Runtime.enable');
  await cdp('Page.enable');
  await cdp('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 2, mobile: width < 600 });
  await cdp('Emulation.setGeolocationOverride', { latitude: ROUTE[0][0], longitude: ROUTE[0][1], accuracy: 8 });
  browser.events.length = 0;
  await cdp('Page.navigate', { url: 'http://127.0.0.1:3123/' });

  const run = async (expression) => {
    const r = await cdp('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
    return r.result.value;
  };
  const waitFor = async (expression, what, ms = 15000) => {
    const end = Date.now() + ms;
    while (Date.now() < end) {
      if (await run(expression)) return;
      await sleep(150);
    }
    await shot('timeout');
    throw new Error(`${size}: timed out waiting for ${what}`);
  };
  const hasText = (t) => `document.body.innerText.toLowerCase().includes(${JSON.stringify(t.toLowerCase())})`;
  const shot = async (name) => {
    const { data } = await cdp('Page.captureScreenshot', { format: 'png' });
    writeFileSync(path.join(shots, `${size}-${name}.png`), Buffer.from(data, 'base64'));
  };
  /** the centre of the first VISIBLE control whose text, label or placeholder matches */
  const locate = (pattern) =>
    run(`(() => {
      const re = new RegExp(${JSON.stringify(pattern)}, 'i');
      for (const el of document.querySelectorAll('button, input, [role=button]')) {
        const label = [el.innerText, el.getAttribute('aria-label'), el.title, el.placeholder].filter(Boolean).join(' ');
        const r = el.getBoundingClientRect();
        if (r.width && r.height && re.test(label)) return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
      }
      return null;
    })()`);
  /** a REAL tap at the control's position: if something covers it, the tap goes to the cover, as for a user */
  const tap = async (pattern) => {
    const p = await locate(pattern);
    if (!p) throw new Error(`${size}: no visible control matching ${pattern}`);
    for (const type of ['mousePressed', 'mouseReleased']) {
      await cdp('Input.dispatchMouseEvent', { type, x: p.x, y: p.y, button: 'left', clickCount: 1 });
    }
    await sleep(250);
  };

  const check = async (state) => {
    await sleep(700); // let entrance animations finish
    await shot(state);
    const found = await run(`(() => {
      const out = [], small = [];
      const W = innerWidth, H = innerHeight;
      for (const el of document.querySelectorAll('button, input')) {
        const r = el.getBoundingClientRect();
        const style = getComputedStyle(el);
        if (!r.width || !r.height || style.visibility === 'hidden') continue;
        // skip rows scrolled out of view inside a scrolling list
        let box = el.parentElement, hidden = false;
        while (box && box !== document.body) {
          const s = getComputedStyle(box);
          if (/(auto|scroll)/.test(s.overflowY)) { const b = box.getBoundingClientRect(); if (r.bottom > b.bottom + 1 || r.top < b.top - 1) hidden = true; }
          box = box.parentElement;
        }
        if (hidden) continue;
        const name = (el.getAttribute('aria-label') || el.title || el.innerText || el.placeholder || el.className).toString().trim().replace(/\\s+/g, ' ').slice(0, 40);
        if (r.left < -1 || r.right > W + 1 || r.top < -1 || r.bottom > H + 1) { out.push('"' + name + '" is outside the screen'); continue; }
        const top = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
        if (top && top !== el && !el.contains(top) && !top.contains(el)) {
          const cover = (top.closest('button')?.innerText || top.innerText || top.className?.baseVal || top.className || top.tagName).toString().trim().replace(/\\s+/g, ' ').slice(0, 40);
          out.push('"' + name + '" is covered by "' + cover + '"');
        }
        if (Math.min(r.width, r.height) < 28) small.push('"' + name + '" is only ' + Math.round(r.width) + 'x' + Math.round(r.height));
      }
      if (document.documentElement.scrollWidth > W + 1) out.push('the page scrolls sideways');
      return { out, small };
    })()`);
    // the report pop-up is MEANT to sit over the trip screen's own three buttons; anything else covered is a problem
    const behindPopUp = (p) => /report-(sheet|countdown)/.test(state) && /^"(Report incident|Mute voice guidance|End navigation)" is covered/.test(p);
    for (const p of found.out) if (!behindPopUp(p)) problems.push(`${size} ${state}: ${p}`);
    // the map's buttons are placed from this value: it must match what the route panel really covers
    const panel = await run(`(() => {
      const start = [...document.querySelectorAll('button')].find((b) => /Start Navigation|Preview Route/.test(b.innerText));
      const box = start?.closest('div.fixed');
      return box ? { covers: Math.ceil(innerHeight - box.getBoundingClientRect().top), published: parseInt(document.documentElement.style.getPropertyValue('--route-panel-height') || '0', 10) } : null;
    })()`);
    if (panel && Math.abs(panel.covers - panel.published) > 2) {
      problems.push(`${size} ${state}: route panel covers ${panel.covers}px but ${panel.published}px was published for the map buttons`);
    } else if (panel) {
      notes.push(`${size} ${state}: route panel ${panel.covers}px, map buttons placed above it`);
    }
    for (const p of found.small) notes.push(`${size} ${state}: ${p}`);
  };

  const pickDestination = async () => {
    await tap('Where to');
    await cdp('Input.insertText', { text: 'Brigade' });
    await waitFor(hasText('Ashok Nagar'), 'search results');
    await check('2-search-results');
    const p = await run(`(() => {
      const all = [...document.querySelectorAll('*')].filter((e) => e.innerText && e.innerText.includes('Ashok Nagar') && !e.querySelector('input'));
      const r = all.at(-1).getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    })()`);
    for (const type of ['mousePressed', 'mouseReleased']) {
      await cdp('Input.dispatchMouseEvent', { type, x: p.x, y: p.y, button: 'left', clickCount: 1 });
    }
  };

  await waitFor(`!!document.querySelector('input')`, 'the app');
  await check('1-start');
  await pickDestination();
  await waitFor(hasText('maneuvers'), 'the route panel');
  await check('3-route-panel');
  await tap('^\\s*Steps');
  await check('4-route-steps');
  await tap('^\\s*Hide');
  await tap('Fastest');
  await waitFor(hasText('Comparing Routes'), 'the comparison');
  await check('5-compare-routes');
  await tap('Start Navigation \\(Dynamic\\)');
  await waitFor(hasText('remaining'), 'navigation');
  await check('6-navigating');
  await tap('Report|incident');
  await waitFor(hasText('Add a report'), 'the report sheet');
  await check('7-report-sheet');
  await tap('Crash');
  await waitFor(hasText('Reporting crash'), 'the countdown');
  await check('8-report-countdown');
  await tap('Undo');
  await tap('End navigation');
  await waitFor(hasText('Comparing Routes'), 'back to the routes');
  await check('9-after-end');
  failRoutes = true;
  await tap('Shortest');
  await waitFor(hasText('road network is still loading'), 'the error message');
  await check('10-error');

  for (const e of browser.events) {
    if (e.sessionId === sessionId && e.method === 'Runtime.exceptionThrown') {
      problems.push(`${size}: page error: ${e.params.exceptionDetails.exception?.description?.split('\n')[0]}`);
    }
  }
  await browser.send('Target.disposeBrowserContext', { browserContextId });
}

try {
  await main();
} catch (err) {
  problems.push(String(err.message || err));
} finally {
  site.close();
  backend.close();
  backend.closeAllConnections?.();
  site.closeAllConnections?.();
}
console.log(`screenshots: ${shots}`);
if (notes.length) console.log(`\nSmall controls (${notes.length}):\n  ${[...new Set(notes)].join('\n  ')}`);
if (problems.length) {
  console.log(`\nPROBLEMS (${problems.length}):\n  ${problems.join('\n  ')}`);
  process.exit(1);
}
console.log('\nNo layout problems found.');
