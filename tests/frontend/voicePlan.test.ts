// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { VoicePlanner, formatSpokenDistance, stageBands } from '../../lib/voicePlan.ts';

test('formatSpokenDistance', () => {
  assert.equal(formatSpokenDistance(300), '300 metres');
  assert.equal(formatSpokenDistance(120), '100 metres');
  assert.equal(formatSpokenDistance(20), '50 metres');
  assert.equal(formatSpokenDistance(1000), '1 kilometre');
  assert.equal(formatSpokenDistance(1200), '1.2 kilometres');
});

test('bands grow with speed and stay ordered', () => {
  const slow = stageBands(0);
  assert.deepEqual([slow.now, slow.near, slow.prepare], [20, 100, 300]);
  const fast = stageBands(20); // 72 km/h
  assert.ok(fast.now > slow.now && fast.near > slow.near && fast.prepare > slow.prepare);
  assert.ok(fast.now < fast.near && fast.near < fast.prepare);
});

test('a left turn is announced three times: far, near, now', () => {
  const v = new VoicePlanner();
  assert.equal(v.evaluate('r:1', 'turn_left', '7th Cross Road', 450, 0), null);
  assert.equal(v.evaluate('r:1', 'turn_left', '7th Cross Road', 290, 0)?.text, 'In 300 metres, turn left onto 7th Cross Road');
  assert.equal(v.evaluate('r:1', 'turn_left', '7th Cross Road', 95, 0)?.text, 'In 100 metres, turn left');
  const now = v.evaluate('r:1', 'turn_left', '7th Cross Road', 15, 0);
  assert.equal(now?.text, 'Turn left');
  assert.equal(now?.urgent, true);
});

test('the same stage is never repeated', () => {
  const v = new VoicePlanner();
  assert.ok(v.evaluate('r:1', 'turn_right', 'A', 280, 0));
  assert.equal(v.evaluate('r:1', 'turn_right', 'A', 270, 0), null);
  assert.equal(v.evaluate('r:1', 'turn_right', 'A', 200, 0), null);
});

test('if a GPS fix jumps past a band, the current band still speaks and earlier ones are skipped', () => {
  const v = new VoicePlanner();
  assert.equal(v.evaluate('r:1', 'turn_left', 'A', 90, 0)?.stage, 'near'); // first seen already inside "near"
  assert.equal(v.evaluate('r:1', 'turn_left', 'A', 250, 0), null); // the "prepare" band is not announced late
});

test('different maneuvers are tracked independently', () => {
  const v = new VoicePlanner();
  assert.ok(v.evaluate('r:1', 'turn_left', 'A', 290, 0));
  assert.ok(v.evaluate('r:2', 'turn_right', 'B', 290, 0));
});

test('a new route (after a reroute) starts fresh', () => {
  const v = new VoicePlanner();
  assert.ok(v.evaluate('r:1', 'turn_left', 'A', 290, 0));
  v.reset();
  assert.ok(v.evaluate('r:1', 'turn_left', 'A', 290, 0));
});

test('slight turns, u-turns and straight', () => {
  const v = new VoicePlanner();
  assert.equal(v.evaluate('a', 'slight_left', null, 95, 0)?.text, 'In 100 metres, bear left');
  assert.equal(v.evaluate('b', 'u_turn', null, 95, 0)?.text, 'In 100 metres, make a U-turn');
  assert.equal(v.evaluate('c', 'straight', 'Hosur Road', 290, 0)?.text, 'In 300 metres, continue straight onto Hosur Road');
});

test('an unnamed road is not spoken as a name', () => {
  const v = new VoicePlanner();
  assert.equal(v.evaluate('a', 'turn_left', 'Unnamed Road', 290, 0)?.text, 'In 300 metres, turn left');
});

test('arrival: announced ahead of time, and the final "now" is left to the arrival event', () => {
  const v = new VoicePlanner();
  assert.equal(v.evaluate('z', 'arrive', 'X', 290, 0)?.text, 'In 300 metres, you will arrive at your destination');
  assert.equal(v.evaluate('z', 'arrive', 'X', 10, 0), null);
});

test('depart is never spoken', () => {
  const v = new VoicePlanner();
  assert.equal(v.evaluate('d', 'depart', 'Main Road', 10, 0), null);
});

test('a fast rider hears the turn earlier', () => {
  const v = new VoicePlanner();
  assert.equal(v.evaluate('f', 'turn_left', 'A', 36, 15)?.stage, 'now'); // 15 m/s -> "now" band is 37.5 m
  const slow = new VoicePlanner();
  assert.equal(slow.evaluate('f', 'turn_left', 'A', 36, 0)?.stage, 'near'); // standing still: 36 m is only "near"
});
