// The real useGPS hook fed by a fake phone. Many Android WebViews report no speed, so it is worked out from movement.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';
import { render } from './helpers/fakes/react.mjs';
import { installBrowser, north, east } from './helpers/env.mjs';

let browser: any;
let useGPS: any;

before(async () => {
  browser = installBrowser();
  ({ useGPS } = await import('../../hooks/useGPS.ts'));
});

/** ride north at `mps` with one fix every `everyMs`; returns the speed after each fix */
function drive(mps: number, { seconds = 12, everyMs = 1000, accuracy = 8, speed = null as number | null, jitterM = 0 } = {}) {
  const hook = render(() => useGPS());
  const out: number[] = [];
  const t0 = 1_000_000;
  let i = 0;
  for (let ms = 0; ms <= seconds * 1000; ms += everyMs, i++) {
    const wobble = jitterM * (i % 2 === 0 ? 1 : -1);
    browser.gps.emit({ latitude: north((mps * ms) / 1000 + wobble), longitude: east(0), accuracy, speed }, t0 + ms);
    out.push(hook.result().gpsPosition.speed);
  }
  hook.unmount();
  return out;
}

const settled = (speeds: number[]) => speeds.slice(Math.floor(speeds.length / 2));

test('the phone\'s own speed is used when it gives one', () => {
  assert.deepEqual(new Set(drive(5, { speed: 7.5 })), new Set([7.5]));
});

for (const [label, mps, accuracy] of [
  ['walking-pace traffic, 5 km/h', 1.4, 8],
  ['slow traffic, 9 km/h', 2.5, 8],
  ['slow traffic with a weak signal, 14 km/h', 4, 20],
  ['city speed, 36 km/h', 10, 8],
] as const) {
  test(`no phone speed, one fix a second: ${label} reads about right and never drops to zero`, () => {
    for (const v of settled(drive(mps, { accuracy, seconds: 20 }))) {
      assert.ok(Math.abs(v - mps) <= mps * 0.25, `expected about ${mps} m/s, got ${v.toFixed(2)}`);
    }
  });
}

test('several fixes a second do not make a moving rider read zero', () => {
  for (const v of settled(drive(6, { everyMs: 250 }))) assert.ok(Math.abs(v - 6) <= 1.5, `got ${v}`);
});

test('standing still with a jittery signal reads zero', () => {
  assert.ok(drive(0, { jitterM: 1.2, seconds: 20 }).every((v) => v === 0));
});

test('after stopping, the speed returns to zero within a few seconds', () => {
  const hook = render(() => useGPS());
  let t = 5_000_000;
  for (let s = 0; s <= 10; s++) browser.gps.emit({ latitude: north(8 * s), longitude: east(0) }, (t += 1000));
  assert.ok(hook.result().gpsPosition.speed > 6);
  for (let s = 0; s < 8; s++) browser.gps.emit({ latitude: north(80), longitude: east(0) }, (t += 1000));
  assert.equal(hook.result().gpsPosition.speed, 0);
  hook.unmount();
});

test('after a long gap (screen off) no wild speed is invented', () => {
  const hook = render(() => useGPS());
  browser.gps.emit({ latitude: north(0), longitude: east(0) }, 9_000_000);
  browser.gps.emit({ latitude: north(3000), longitude: east(0) }, 9_000_000 + 120_000);
  assert.equal(hook.result().gpsPosition.speed, 0);
  hook.unmount();
});

test('the watcher is removed when the screen goes away', () => {
  const before = browser.gps.watchers.size;
  const hook = render(() => useGPS());
  assert.equal(browser.gps.watchers.size, before + 1);
  hook.unmount();
  assert.equal(browser.gps.watchers.size, before);
});
