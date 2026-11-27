// Voice in a desktop browser: the Web Speech API.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';
import { sleep } from './helpers/env.mjs';

let voice: any;
const log: string[] = [];
let lastUtterance: any = null;

before(async () => {
  (globalThis as any).__native = false;
  (globalThis as any).SpeechSynthesisUtterance = class {
    text: string; lang = ''; voice: any = null; rate = 1; pitch = 1; volume = 1; onerror: any = null;
    constructor(text: string) { this.text = text; }
  };
  (globalThis as any).window = {
    speechSynthesis: {
      paused: false,
      getVoices: () => [{ lang: 'hi-IN' }, { lang: 'en-US' }, { lang: 'en_IN' }],
      addEventListener() {},
      speak(u: any) { lastUtterance = u; log.push(`speak:${u.text}`); },
      cancel() { log.push('cancel'); },
      resume() {},
    },
  };
  ({ voiceGuidance: voice } = await import('../../lib/speech.ts'));
});

beforeEach(async () => {
  await sleep(90);
  voice.setEnabled(true);
  log.length = 0;
});

test('an urgent prompt cancels the previous one first, and uses the Indian English voice', async () => {
  voice.speak('Turn left', true);
  await sleep(120);
  assert.deepEqual(log, ['cancel', 'speak:Turn left']);
  assert.equal(lastUtterance.voice.lang, 'en_IN');
});

test('an early warning does not cancel what is being said', async () => {
  voice.speak('In 300 metres, turn left');
  await sleep(20);
  assert.deepEqual(log, ['speak:In 300 metres, turn left']);
});

test('two urgent prompts at once: only the newer one is spoken', async () => {
  voice.speak('first', true);
  voice.speak('second', true);
  await sleep(120);
  assert.deepEqual(log.filter((l) => l.startsWith('speak')), ['speak:second']);
});

test('stop() also drops a prompt that has not started yet (ending a trip must be silent)', async () => {
  voice.speak('Turn right', true);
  voice.stop();
  await sleep(120);
  assert.equal(log.some((l) => l.startsWith('speak')), false);
});

test('muting also drops a prompt that has not started yet', async () => {
  voice.speak('Bear left', true);
  voice.setEnabled(false);
  await sleep(120);
  assert.equal(log.some((l) => l.startsWith('speak')), false);
});

test('unlock() speaks a silent utterance from the tap', () => {
  voice.unlock();
  assert.equal(lastUtterance.volume, 0);
});

test('browser errors are reported, but interruption is not a problem', async () => {
  const problems: string[] = [];
  voice.onProblem((r: string) => problems.push(r));
  voice.speak('a');
  await sleep(120);
  lastUtterance.onerror({ error: 'interrupted' });
  assert.deepEqual(problems, []);
  lastUtterance.onerror({ error: 'synthesis-failed' });
  assert.deepEqual(problems, ['synthesis-failed']);
});
