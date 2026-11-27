// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { GpsFilter, RouteMatcher, buildRoute, projectOnRoute, angleDiffDeg } from '../../lib/mapMatching.ts';
import type { LatLngTuple } from '../../lib/mapMatching.ts';

const LAT0 = 12.97;
const LNG0 = 77.59;
const M_LAT = 1 / 110574; // degrees per metre north
const M_LNG = 1 / (111320 * Math.cos((LAT0 * Math.PI) / 180)); // degrees per metre east

const at = (eastM: number, northM: number): LatLngTuple => [LAT0 + northM * M_LAT, LNG0 + eastM * M_LNG];

// a straight route going north: 1000 m, a vertex every 20 m
const straight: LatLngTuple[] = Array.from({ length: 51 }, (_, i) => at(0, i * 20));

function distM(a: [number, number], b: [number, number]): number {
  return Math.hypot((a[1] - b[1]) / M_LNG, (a[0] - b[0]) / M_LAT);
}

// small deterministic pseudo random generator, so the tests never flake
function rng(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296 - 0.5;
  };
}

test('angleDiffDeg wraps around north', () => {
  assert.equal(angleDiffDeg(350, 10), 20);
  assert.equal(angleDiffDeg(0, 180), 180);
  assert.equal(angleDiffDeg(90, 90), 0);
});

test('GpsFilter: noisy stationary GPS is steadier than the raw fixes', () => {
  const rand = rng(1);
  const filter = new GpsFilter();
  let rawErr = 0;
  let filtErr = 0;
  let n = 0;
  for (let i = 0; i < 60; i++) {
    const p = at(rand() * 24, rand() * 24); // +-12 m noise around the true point (0, 0)
    const f = filter.update({ lat: p[0], lng: p[1], accuracy: 12, speed: 0, timestamp: 1000 * i });
    if (i >= 10) {
      rawErr += distM(p, at(0, 0));
      filtErr += distM([f.lat, f.lng], at(0, 0));
      n++;
    }
  }
  assert.ok(filtErr / n < 0.6 * (rawErr / n), `filtered ${(filtErr / n).toFixed(1)} m vs raw ${(rawErr / n).toFixed(1)} m`);
});

test('GpsFilter: a 500 m jump in one second is rejected, not followed', () => {
  const filter = new GpsFilter();
  for (let i = 0; i < 10; i++) filter.update({ lat: at(0, 0)[0], lng: at(0, 0)[1], accuracy: 8, speed: 0, timestamp: 1000 * i });
  const jumped = at(500, 0);
  const f = filter.update({ lat: jumped[0], lng: jumped[1], accuracy: 8, speed: 0, timestamp: 10000 });
  assert.ok(distM([f.lat, f.lng], at(0, 0)) < 20);
});

test('GpsFilter: genuine fast movement is tracked', () => {
  const filter = new GpsFilter();
  let last = { lat: 0, lng: 0 };
  for (let i = 0; i < 30; i++) {
    const p = at(0, i * 14); // 14 m/s, about 50 km/h
    last = filter.update({ lat: p[0], lng: p[1], accuracy: 6, speed: 14, timestamp: 1000 * i });
  }
  assert.ok(distM([last.lat, last.lng], at(0, 29 * 14)) < 15);
});

test('RouteMatcher: a point 8 m off the road snaps onto it', () => {
  const m = new RouteMatcher(straight);
  const r = m.match(...at(8, 300), null, 0, 10);
  assert.ok(r.snapped);
  assert.ok(Math.abs(r.distanceM - 8) < 0.5);
  assert.ok(Math.abs(r.alongM - 300) < 1);
  assert.ok(Math.abs((r.displayLng - LNG0) / M_LNG) < 0.1, 'the marker is drawn ON the road');
});

test('RouteMatcher: 40 m off is NOT snapped, and the off-route distance is the real one', () => {
  const m = new RouteMatcher(straight);
  const r = m.match(...at(40, 300), null, 0, 10);
  assert.ok(!r.snapped);
  assert.ok(Math.abs(r.distanceM - 40) < 0.5);
  assert.ok(Math.abs((r.displayLng - at(40, 300)[1]) / M_LNG) < 0.1, 'the marker stays where the rider really is');
});

test('RouteMatcher: snapping the marker never hides the true distance from the route', () => {
  const m = new RouteMatcher(straight);
  const r = m.match(...at(14, 300), null, 0, 10); // snapped (limit 15 m) ...
  assert.ok(r.snapped);
  assert.ok(Math.abs(r.distanceM - 14) < 0.5); // ... but off-route detection still sees 14 m, not 0
});

test('RouteMatcher: hysteresis keeps an already snapped marker snapped a little further out', () => {
  const m = new RouteMatcher(straight);
  assert.ok(!m.match(...at(20, 100), null, 0, 10).snapped); // 20 m > 15 m limit: not snapped
  assert.ok(m.match(...at(10, 120), null, 0, 10).snapped); // 10 m: snapped
  assert.ok(m.match(...at(19, 140), null, 0, 10).snapped); // 19 m, within the 1.4x hysteresis limit (21 m): stays snapped
  assert.ok(!m.match(...at(30, 160), null, 0, 10).snapped); // 30 m: let go
});

test('RouteMatcher: while moving, heading picks the correct one of two parallel legs', () => {
  // north 200 m, across 30 m, then back south 200 m on a parallel leg
  const uTurn: LatLngTuple[] = [
    ...Array.from({ length: 11 }, (_, i) => at(0, i * 20)),
    at(30, 200),
    ...Array.from({ length: 11 }, (_, i) => at(30, 200 - i * 20)),
  ];
  const m = new RouteMatcher(uTurn);
  // 16 m from leg 1 (north-bound) and 14 m from leg 2 (south-bound); the rider is heading NORTH
  const r = m.match(...at(16, 100), 0, 8, 10);
  assert.ok(r.segmentIndex < 10, `matched segment ${r.segmentIndex}: should be the north-bound leg`);
});

test('RouteMatcher: progress along the route is monotonic while riding along it', () => {
  const m = new RouteMatcher(straight);
  let prev = -1;
  for (let along = 0; along <= 900; along += 15) {
    const r = m.match(...at(3, along), 0, 8, 8);
    assert.ok(r.alongM >= prev - 0.5);
    assert.ok(Math.abs(r.alongM - along) < 1);
    prev = r.alongM;
  }
});

test('projectOnRoute and buildRoute: total length and projection', () => {
  const route = buildRoute(straight);
  assert.ok(Math.abs(route.total - 1000) < 1);
  const p = projectOnRoute(route, ...at(12, 450));
  assert.ok(Math.abs(p.alongM - 450) < 1);
  assert.ok(Math.abs(p.distanceM - 12) < 0.5);
});
