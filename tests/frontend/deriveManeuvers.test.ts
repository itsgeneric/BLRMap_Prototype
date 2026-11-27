// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deriveManeuvers } from '../../lib/deriveManeuvers.ts';

const LAT0 = 12.97;
const LNG0 = 77.59;
const M_LAT = 1 / 110574;
const M_LNG = 1 / (111320 * Math.cos((LAT0 * Math.PI) / 180));
const at = (eastM: number, northM: number): [number, number] => [LAT0 + northM * M_LAT, LNG0 + eastM * M_LNG];

// points every 10 m along a polyline given by corner points
function walk(corners: [number, number][]): [number, number][] {
  const out: [number, number][] = [];
  for (let k = 0; k < corners.length - 1; k++) {
    const [x0, y0] = corners[k];
    const [x1, y1] = corners[k + 1];
    const n = Math.max(1, Math.round(Math.hypot(x1 - x0, y1 - y0) / 10));
    for (let i = 0; i < n; i++) out.push(at(x0 + ((x1 - x0) * i) / n, y0 + ((y1 - y0) * i) / n));
  }
  out.push(at(...corners[corners.length - 1]));
  return out;
}

const types = (path: [number, number][]) => deriveManeuvers(path).map((m) => m.type);

test('a straight road has only depart and arrive', () => {
  assert.deepEqual(types(walk([[0, 0], [0, 500]])), ['depart', 'arrive']);
});

test('north then west is a left turn; north then east is a right turn', () => {
  assert.deepEqual(types(walk([[0, 0], [0, 300], [-300, 300]])), ['depart', 'turn_left', 'arrive']);
  assert.deepEqual(types(walk([[0, 0], [0, 300], [300, 300]])), ['depart', 'turn_right', 'arrive']);
});

test('the turn is placed at the corner, with the distance to the next maneuver', () => {
  const m = deriveManeuvers(walk([[0, 0], [0, 300], [300, 300]]));
  assert.ok(Math.abs(m[1].lat - at(0, 300)[0]) < 0.00003);
  assert.ok(Math.abs(m[0].distance_m - 300) < 12);
  assert.ok(Math.abs(m[1].distance_m - 300) < 12);
  assert.equal(m[2].distance_m, 0);
});

test('a 50 degree fork is a slight turn', () => {
  const rad = (50 * Math.PI) / 180;
  const t = deriveManeuvers(walk([[0, 0], [0, 300], [300 * Math.sin(rad), 300 + 300 * Math.cos(rad)]]));
  assert.deepEqual(t.map((m) => m.type), ['depart', 'slight_right', 'arrive']);
});

test('a hairpin that doubles straight back is a U-turn', () => {
  assert.deepEqual(types(walk([[0, 0], [0, 300], [6, 0]])), ['depart', 'u_turn', 'arrive']);
});

test('a gentle curve is not reported as a turn', () => {
  const curve: [number, number][] = [];
  for (let i = 0; i <= 40; i++) {
    const a = (i / 40) * (Math.PI / 6); // 30 degrees spread over about 400 m
    curve.push(at(800 * (1 - Math.cos(a)), 800 * Math.sin(a)));
  }
  assert.deepEqual(types(curve), ['depart', 'arrive']);
});

test('an empty or one-point route gives no maneuvers', () => {
  assert.deepEqual(deriveManeuvers([]), []);
  assert.deepEqual(deriveManeuvers([at(0, 0)]), []);
});
