// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { EtaEstimator, SpeedSmoother, formatRemaining, routeMinutes, FALLBACK_SPEED_MPS } from '../../lib/eta.ts';

test('routeMinutes prefers the server duration, otherwise guesses from distance', () => {
  assert.equal(routeMinutes({ duration_s: 600, distance_km: 3 }), 10);
  assert.equal(routeMinutes({ distance_km: 10 }, 20), 30);
  assert.equal(routeMinutes({ distance_km: 0.1 }), 1);
  assert.equal(routeMinutes(null), Infinity);
});

test('formatRemaining', () => {
  assert.equal(formatRemaining(20), '< 1 min');
  assert.equal(formatRemaining(60), '1 min');
  assert.equal(formatRemaining(14 * 60 + 20), '14 min');
  assert.equal(formatRemaining(3600), '1 h');
  assert.equal(formatRemaining(3600 + 5 * 60), '1 h 05 min');
});

test('SpeedSmoother: rises toward the real speed, falls back to a true 0 at a standstill', () => {
  const s = new SpeedSmoother();
  let kmh = 0;
  for (let i = 0; i < 10; i++) kmh = s.push(10); // 10 m/s = 36 km/h
  assert.ok(kmh >= 35 && kmh <= 36, `got ${kmh}`);
  for (let i = 0; i < 30; i++) kmh = s.push(0);
  assert.equal(kmh, 0);
});

test('SpeedSmoother: GPS noise at a standstill reads 0, an unknown speed keeps the last value', () => {
  const s = new SpeedSmoother();
  assert.equal(s.push(0.2), 0);
  assert.equal(s.push(0.3), 0);
  for (let i = 0; i < 10; i++) s.push(8);
  const before = s.push(8);
  assert.equal(s.push(null), before);
});

test('ETA at the start is the planned duration', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(6000, 1200); // 6 km planned in 20 min = 5 m/s
  const r = e.update(6000, 0);
  assert.ok(Math.abs(r.remainingS - 1200) < 1);
  assert.equal(r.arrivalMs, r.remainingS * 1000);
});

test('ETA moves toward the real pace: a rider slower than planned gets a later arrival', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(10000, 1200); // planned 8.3 m/s
  e.update(10000, 0);
  // after 10 minutes only 2 km covered (3.3 m/s): well below plan
  let r = e.update(8000, 600_000);
  for (let t = 601; t <= 660; t++) r = e.update(8000 - (t - 600) * 3.3, t * 1000);
  const plannedRemaining = (8000 - 60 * 3.3) / (10000 / 1200);
  assert.ok(r.remainingS > plannedRemaining * 1.3, `remaining ${r.remainingS.toFixed(0)}s vs plan-only ${plannedRemaining.toFixed(0)}s`);
});

test('ETA moves toward the real pace: a faster rider gets an earlier arrival', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(10000, 1800); // planned 5.6 m/s
  e.update(10000, 0);
  let r = e.update(10000, 1000);
  for (let t = 1; t <= 300; t++) r = e.update(10000 - t * 9, t * 1000); // 9 m/s for five minutes
  const plannedRemaining = (10000 - 300 * 9) / (10000 / 1800);
  assert.ok(r.remainingS < plannedRemaining * 0.85);
});

test('ETA does not jump around on one noisy fix', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(5000, 900);
  let r = e.update(5000, 0);
  for (let t = 1; t <= 60; t++) r = e.update(5000 - t * 5.5, t * 1000);
  const steady = r.remainingS;
  const jumpy = e.update(5000 - 61 * 5.5 + 400, 61_000); // a GPS fix that suddenly puts the rider 400 m back
  assert.ok(Math.abs(jumpy.remainingS - steady) < 0.35 * steady + 60);
});

test('remainingAt counts down second by second between fixes', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(3000, 600);
  const r = e.update(3000, 0);
  assert.ok(Math.abs(e.remainingAt(10_000) - (r.remainingS - 10)) < 0.01);
  assert.equal(e.remainingAt(10_000_000), 0);
});

test('after a reroute the distance already travelled still counts toward the rider\'s pace', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(5000, 900);
  e.update(5000, 0);
  e.update(3000, 400_000); // 2 km covered in 400 s
  e.setRoute(2500, 600); // rerouted from the current position
  const r = e.update(2500, 400_000);
  assert.ok(r.paceMps > 0 && r.remainingS > 0);
  assert.ok(Math.abs(r.paceMps - 2500 / 600) > 0.05, 'the real pace of the first 2 km must influence the estimate');
});

test('near the destination the remaining time is short', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(2000, 400);
  e.update(2000, 0);
  const r = e.update(20, 380_000);
  assert.ok(r.remainingS <= 15);
});

test('with no planned duration the fallback pace is used', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(6500, null);
  const r = e.update(6500, 0);
  assert.ok(Math.abs(r.remainingS - 6500 / FALLBACK_SPEED_MPS) < 1);
});
test('a second trip starts clean: nothing from the first trip counts as travelled', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(8000, 1600);
  e.update(100, 1_600_000); // first trip ridden almost to the end
  e.startTrip(2_000_000);
  e.setRoute(6000, 1200);
  e.update(6000, 2_000_000);
  // 60 s in, 300 m covered (5 m/s, exactly the plan): the estimate must still match the plan
  const r = e.update(5700, 2_060_000);
  assert.ok(Math.abs(r.paceMps - 5) < 0.1, `pace ${r.paceMps}`);
});

test('starting part-way along a route does not count the skipped part as ridden', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(6000, 1200); // planned 5 m/s
  e.update(6000, 0);
  e.update(2000, 1000); // the first fix is already 4 km along
  let r = e.update(2000, 1000);
  for (let t = 2; t <= 90; t++) r = e.update(2000 - (t - 1) * 5, t * 1000);
  assert.ok(Math.abs(r.paceMps - 5) < 0.3, `pace ${r.paceMps}`);
});

test('real fast riding is still counted', () => {
  const e = new EtaEstimator();
  e.startTrip(0);
  e.setRoute(20000, 4000); // planned 5 m/s
  let r = e.update(20000, 0);
  for (let t = 10; t <= 300; t += 10) r = e.update(20000 - t * 15, t * 1000); // 54 km/h
  assert.ok(r.paceMps > 9, `pace ${r.paceMps}`);
});
