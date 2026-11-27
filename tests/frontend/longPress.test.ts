// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { LongPressDetector } from '../../lib/longPress.ts';

/** a manual clock so the tests need no real waiting */
function fakeClock() {
  let now = 0;
  const timers = new Map<number, { at: number; fn: () => void }>();
  let nextId = 1;
  return {
    setTimer: (fn: () => void, ms: number) => {
      const id = nextId++;
      timers.set(id, { at: now + ms, fn });
      return id;
    },
    clearTimer: (h: unknown) => void timers.delete(h as number),
    advance(ms: number) {
      now += ms;
      for (const [id, t] of [...timers]) {
        if (t.at <= now) {
          timers.delete(id);
          t.fn();
        }
      }
    },
    pending: () => timers.size,
  };
}

function make(holdMs = 500) {
  const clock = fakeClock();
  const fired: { lat: number; lng: number }[] = [];
  const d = new LongPressDetector<{ lat: number; lng: number }>({
    holdMs,
    moveTolerancePx: 10,
    onLongPress: (p) => fired.push(p),
    setTimer: clock.setTimer,
    clearTimer: clock.clearTimer,
  });
  return { d, clock, fired };
}

const P = { lat: 12.97, lng: 77.59 };

test('holding still for the full time fires once with the payload from the moment of touch', () => {
  const { d, clock, fired } = make();
  d.start(100, 100, P);
  clock.advance(499);
  assert.equal(fired.length, 0);
  clock.advance(2);
  assert.deepEqual(fired, [P]);
});

test('it fires only once, however long the hold continues', () => {
  const { d, clock, fired } = make();
  d.start(100, 100, P);
  clock.advance(5000);
  assert.equal(fired.length, 1);
});

test('a quick tap never fires', () => {
  const { d, clock, fired } = make();
  d.start(100, 100, P);
  clock.advance(120);
  d.end();
  clock.advance(5000);
  assert.equal(fired.length, 0);
  assert.equal(clock.pending(), 0);
});

test('spamming taps never fires, and leaves no timers behind', () => {
  const { d, clock, fired } = make();
  for (let i = 0; i < 50; i++) {
    d.start(100 + i, 100, P);
    clock.advance(60);
    d.end();
  }
  clock.advance(5000);
  assert.equal(fired.length, 0);
  assert.equal(clock.pending(), 0);
});

test('moving more than the tolerance (a drag) cancels it', () => {
  const { d, clock, fired } = make();
  d.start(100, 100, P);
  d.move(130, 100);
  clock.advance(1000);
  assert.equal(fired.length, 0);
});

test('small finger tremor within the tolerance does not cancel it', () => {
  const { d, clock, fired } = make();
  d.start(100, 100, P);
  d.move(104, 103);
  d.move(98, 107);
  clock.advance(600);
  assert.equal(fired.length, 1);
});

test('a second touch (pinch) or a zoom cancels it', () => {
  const { d, clock, fired } = make();
  d.start(100, 100, P);
  d.cancel();
  clock.advance(1000);
  assert.equal(fired.length, 0);
});

test('starting again restarts the hold: the first touch cannot fire late', () => {
  const { d, clock, fired } = make();
  d.start(100, 100, { lat: 1, lng: 1 });
  clock.advance(300);
  d.start(200, 200, { lat: 2, lng: 2 });
  clock.advance(300);
  assert.equal(fired.length, 0);
  clock.advance(250);
  assert.deepEqual(fired, [{ lat: 2, lng: 2 }]);
});

test('moves before any touch, and after the hold has fired, are ignored', () => {
  const { d, clock, fired } = make();
  d.move(500, 500);
  d.start(100, 100, P);
  clock.advance(600);
  d.move(900, 900);
  d.end();
  assert.equal(fired.length, 1);
  assert.equal(d.isPending(), false);
});

test('works with the real timers too', async () => {
  const fired: string[] = [];
  const d = new LongPressDetector<string>({ holdMs: 30, onLongPress: (p) => fired.push(p) });
  d.start(0, 0, 'real');
  await new Promise((r) => setTimeout(r, 80));
  assert.deepEqual(fired, ['real']);
});
