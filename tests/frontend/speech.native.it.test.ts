// Voice inside the Android app: it must go to the phone's text-to-speech plugin.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';
import { sleep } from './helpers/env.mjs';

let voice: any;
const tts = () => (globalThis as any).__tts;
const problems: string[] = [];

before(async () => {
  (globalThis as any).__native = true;
  (globalThis as any).window = {};
  (globalThis as any).__tts = { spoken: [], stops: 0, languages: ['en-GB', 'en-US'], failSpeak: null };
  ({ voiceGuidance: voice } = await import('../../lib/speech.ts'));
  voice.onProblem((r: string) => problems.push(r));
});

beforeEach(() => {
  tts().spoken.length = 0;
  tts().failSpeak = null;
  voice.setEnabled(true);
});

test('it is supported although the WebView has no browser speech engine', () => {
  assert.equal(voice.isSupported(), true);
});

test('an urgent prompt reaches the phone in an available English voice and interrupts the previous one', async () => {
  voice.unlock();
  voice.speak('Turn left', true);
  await sleep(30);
  assert.equal(tts().spoken.length, 1);
  assert.equal(tts().spoken[0].text, 'Turn left');
  assert.equal(tts().spoken[0].lang, 'en-GB', 'en-IN is not installed on this fake phone');
  assert.equal(tts().spoken[0].queueStrategy, 0);
});

test('an early warning waits its turn instead of cutting off what is being said', async () => {
  voice.speak('In 300 metres, turn left');
  await sleep(30);
  assert.equal(tts().spoken[0].queueStrategy, 1);
});

test('the same words are not repeated back to back, different words are spoken', async () => {
  voice.speak('Bear left');
  voice.speak('Bear left');
  voice.speak('Bear right');
  await sleep(30);
  assert.deepEqual(tts().spoken.map((s: any) => s.text), ['Bear left', 'Bear right']);
});

test('muted: nothing is spoken, and muting stops speech in progress', async () => {
  const stops = tts().stops;
  voice.setEnabled(false);
  voice.speak('Make a U-turn');
  await sleep(30);
  assert.equal(tts().spoken.length, 0);
  assert.ok(tts().stops > stops);
});

test('empty text is ignored', async () => {
  voice.speak('');
  await sleep(20);
  assert.equal(tts().spoken.length, 0);
});

test('a phone without voice data reports the problem once and does not crash', async () => {
  tts().failSpeak = 'This language is not supported.';
  voice.speak('one');
  voice.speak('two');
  await sleep(30);
  assert.deepEqual(problems, ['This language is not supported.']);
});
