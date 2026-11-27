// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mapManeuvers, upcoming } from '../../lib/navProgress.ts';
import type { TurnManeuver } from '../../lib/types.ts';

const m = (type: TurnManeuver['type'], road: string): TurnManeuver => ({
  type,
  instruction: type,
  road_name: road,
  distance_m: 0,
  lat: 0,
  lng: 0,
});

const maneuvers: TurnManeuver[] = [
  m('depart', 'Main Road'),
  m('turn_left', '7th Cross Road'),
  m('turn_right', 'Park Road'),
  m('arrive', 'Park Road'),
];
const alongs = [0, 300, 800, 1200];
const list = mapManeuvers(maneuvers, (() => {
  let i = 0;
  return () => alongs[i++];
})());

test('mapManeuvers keeps maneuvers in route order', () => {
  const seq = [0, 500, 400, 1200]; // the third one projects "before" the second: must not go backwards
  let i = 0;
  const out = mapManeuvers(maneuvers, () => seq[i++]);
  assert.deepEqual(out.map((x) => x.alongM), [0, 500, 500, 1200]);
});

test('at the start the next turn is the first real maneuver, not "depart"', () => {
  const u = upcoming(list, 0, 0);
  assert.equal(u.maneuver?.type, 'turn_left');
  assert.equal(u.distanceM, 300);
  assert.equal(u.next?.type, 'turn_right');
  assert.equal(u.currentRoadName, 'Main Road');
});

test('distance to the turn counts down along the route', () => {
  assert.equal(upcoming(list, 200, 0).distanceM, 100);
  assert.equal(upcoming(list, 295, 0).distanceM, 5);
});

test('a maneuver stays upcoming until the rider is clearly past it, then the next one takes over', () => {
  assert.equal(upcoming(list, 305, 1).maneuver?.type, 'turn_left'); // 5 m past: still shown (GPS noise)
  const after = upcoming(list, 320, 1);
  assert.equal(after.maneuver?.type, 'turn_right');
  assert.equal(after.distanceM, 480);
  assert.equal(after.currentRoadName, '7th Cross Road'); // now driving on the road the left turn led to
});

test('progress never goes backwards: the stored index is a floor', () => {
  assert.equal(upcoming(list, 0, 2).index, 2);
});

test('near the end the destination is the upcoming maneuver', () => {
  const u = upcoming(list, 1100, 2);
  assert.equal(u.maneuver?.type, 'arrive');
  assert.equal(u.distanceM, 100);
  assert.equal(u.next, null);
});

test('an empty route has no maneuver', () => {
  const u = upcoming([], 50, 0);
  assert.equal(u.maneuver, null);
});
