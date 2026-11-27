// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyPinAction, shortPlaceName } from '../../lib/pinActions.ts';
import { createLatest } from '../../lib/latest.ts';

const PIN = { lat: 12.97, lng: 77.59, name: 'Dropped pin' };
const HOME = { lat: 12.9, lng: 77.5, name: 'My Location' };
const WORK = { lat: 13.0, lng: 77.7, name: 'Office' };

test('Directions with no start chosen: pin becomes the destination and GPS is requested for the start', () => {
  const r = applyPinAction('directions', PIN, { origin: null, destination: null });
  assert.deepEqual(r.destination, PIN);
  assert.equal(r.origin, null);
  assert.equal(r.needGpsOrigin, true);
});

test('Directions with a start already chosen keeps the start and replaces the destination', () => {
  const r = applyPinAction('directions', PIN, { origin: HOME, destination: WORK });
  assert.deepEqual(r.destination, PIN);
  assert.deepEqual(r.origin, HOME);
  assert.equal(r.needGpsOrigin, false);
});

test('Start here makes the pin the start and leaves the destination alone', () => {
  const r = applyPinAction('start_here', PIN, { origin: HOME, destination: WORK });
  assert.deepEqual(r.origin, PIN);
  assert.deepEqual(r.destination, WORK);
  assert.equal(r.needGpsOrigin, false);
});

test('Start here with nothing else chosen: no destination yet and no GPS lookup', () => {
  const r = applyPinAction('start_here', PIN, { origin: null, destination: null });
  assert.deepEqual(r.origin, PIN);
  assert.equal(r.destination, null);
  assert.equal(r.needGpsOrigin, false);
});

test('applyPinAction does not modify its inputs', () => {
  const current = { origin: HOME, destination: WORK };
  applyPinAction('directions', PIN, current);
  assert.deepEqual(current, { origin: HOME, destination: WORK });
});

test('shortPlaceName', () => {
  assert.equal(shortPlaceName('Brigade Road, Ashok Nagar, Bengaluru 560001, India'), 'Brigade Road');
  assert.equal(shortPlaceName('7FQ9+M2 Bengaluru, Karnataka'), 'Dropped pin'); // a plus code is not a name
  assert.equal(shortPlaceName(''), 'Dropped pin');
  assert.equal(shortPlaceName(undefined), 'Dropped pin');
  assert.equal(shortPlaceName(null), 'Dropped pin');
  assert.ok(shortPlaceName('X'.repeat(200)).length <= 60);
});

test('createLatest: only the newest request may update the screen', () => {
  const latest = createLatest();
  const a = latest.begin();
  const b = latest.begin();
  assert.equal(latest.isCurrent(a), false);
  assert.equal(latest.isCurrent(b), true);
});

test('createLatest: invalidate makes everything stale (route cleared while a request was in flight)', () => {
  const latest = createLatest();
  const a = latest.begin();
  latest.invalidate();
  assert.equal(latest.isCurrent(a), false);
  assert.equal(latest.isCurrent(latest.begin()), true);
});

test('spam scenario: answers arriving out of order leave the screen with the newest answer', async () => {
  const latest = createLatest();
  let screen = 'nothing';
  const request = async (name: string, delayMs: number) => {
    const token = latest.begin();
    await new Promise((r) => setTimeout(r, delayMs));
    if (latest.isCurrent(token)) screen = name; // what loadRoute does
  };
  await Promise.all([request('first (slow)', 80), request('second (fast)', 10), request('third (medium)', 40)]);
  assert.equal(screen, 'third (medium)');
});
