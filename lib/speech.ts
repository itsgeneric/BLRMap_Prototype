/**
 * Voice guidance. The WHAT and WHEN of announcements live in lib/voicePlan.ts; this module only speaks.
 *
 *  - In the Android app it uses the phone's own text-to-speech engine through the native plugin
 *    @capacitor-community/text-to-speech. (Android's WebView has no Web Speech engine, so the browser API is silent there.)
 *  - In a desktop browser it uses the Web Speech API (speechSynthesis).
 *
 * When speaking is impossible (no engine, no voice data installed) it tells the UI once through onProblem(), instead of
 * staying silently mute.
 */
import { Capacitor } from '@capacitor/core';

// The plugin reads `window` the moment it is imported, which breaks the server-side prerender of `next build`. So it is loaded
// lazily, only inside the Android app, the first time it is needed.
let ttsModule: Promise<typeof import('@capacitor-community/text-to-speech')> | null = null;
const loadTts = () => (ttsModule ??= import('@capacitor-community/text-to-speech'));
const QUEUE_FLUSH = 0; // QueueStrategy.Flush: interrupt what is being said
const QUEUE_ADD = 1; // QueueStrategy.Add: speak after the current utterance

type ProblemListener = (reason: string) => void;

class VoiceGuidance {
  private native = false;
  private synth: SpeechSynthesis | null = null;
  private enabled = true;
  private voice: SpeechSynthesisVoice | null = null;
  private nativeLang: string | null = null;
  private lastText = '';
  private lastTime = 0;
  private listeners: ProblemListener[] = [];
  private problemReported = false;
  // an urgent prompt waiting for its short delay: stop(), mute and a newer urgent prompt must be able to drop it
  private pending: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    if (typeof window === 'undefined') return;
    try {
      this.native = Capacitor.isNativePlatform();
    } catch {
      this.native = false;
    }
    if (!this.native && 'speechSynthesis' in window && typeof SpeechSynthesisUtterance !== 'undefined') {
      this.synth = window.speechSynthesis;
      this.pickVoice();
      this.synth.addEventListener?.('voiceschanged', () => this.pickVoice());
    }
  }

  private pickVoice() {
    if (!this.synth) return;
    const voices = this.synth.getVoices();
    if (!voices || voices.length === 0) return;
    const by = (prefix: string) => voices.find((v) => v.lang.replace('_', '-').toLowerCase().startsWith(prefix));
    this.voice = by('en-in') || by('en-gb') || by('en-us') || by('en') || null;
  }

  public isSupported(): boolean {
    return this.native || this.synth !== null;
  }

  public setEnabled(enabled: boolean) {
    this.enabled = enabled;
    if (!enabled) this.stop();
  }

  public isEnabled(): boolean {
    return this.enabled;
  }

  /** Be told (once per page load) when speech cannot work on this device. */
  public onProblem(listener: ProblemListener): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  private reportProblem(reason: string) {
    if (this.problemReported) return;
    this.problemReported = true;
    this.listeners.forEach((l) => l(reason));
  }

  /** Call from a tap handler (e.g. "Start"). The browser engine only speaks after a user gesture; the native one needs nothing. */
  public unlock() {
    if (this.native) {
      void this.resolveNativeLanguage().catch(() => undefined);
      return;
    }
    if (!this.synth) {
      this.reportProblem('unsupported');
      return;
    }
    try {
      const u = new SpeechSynthesisUtterance(' ');
      u.volume = 0;
      this.synth.speak(u);
    } catch {
      /* ignore */
    }
  }

  public stop() {
    if (this.pending !== null) {
      clearTimeout(this.pending);
      this.pending = null;
    }
    try {
      if (this.native) void loadTts().then((m) => m.TextToSpeech.stop()).catch(() => undefined);
      else this.synth?.cancel();
    } catch {
      /* ignore */
    }
  }

  /** Indian English if the phone has it, otherwise any English voice, otherwise the engine default. */
  private async resolveNativeLanguage(): Promise<string> {
    if (this.nativeLang) return this.nativeLang;
    const { TextToSpeech } = await loadTts();
    for (const lang of ['en-IN', 'en-GB', 'en-US']) {
      try {
        const { supported } = await TextToSpeech.isLanguageSupported({ lang });
        if (supported) return (this.nativeLang = lang);
      } catch {
        break;
      }
    }
    return (this.nativeLang = 'en-US');
  }

  public speak(text: string, urgent = false) {
    if (!text || !this.enabled) return;
    if (!this.isSupported()) {
      this.reportProblem('unsupported');
      return;
    }
    const now = Date.now();
    if (text === this.lastText && now - this.lastTime < 4000) return; // never repeat the same words back-to-back
    this.lastText = text;
    this.lastTime = now;

    if (this.native) {
      void (async () => {
        try {
          const { TextToSpeech } = await loadTts();
          const lang = await this.resolveNativeLanguage();
          // urgent ("Turn left now", "Rerouting") interrupts what is being said; everything else queues behind it
          await TextToSpeech.speak({
            text,
            lang,
            rate: 1.0,
            pitch: 1.0,
            volume: 1.0,
            queueStrategy: urgent ? QUEUE_FLUSH : QUEUE_ADD,
          });
        } catch (e: any) {
          this.reportProblem(String(e?.message || 'the phone has no text-to-speech voice'));
        }
      })();
      return;
    }

    const say = () => {
      try {
        if (!this.voice) this.pickVoice();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = this.voice?.lang || 'en-IN';
        if (this.voice) u.voice = this.voice;
        u.rate = 1.0;
        u.pitch = 1.0;
        u.volume = 1.0;
        u.onerror = (e) => {
          const reason = (e as SpeechSynthesisErrorEvent).error;
          if (reason && reason !== 'canceled' && reason !== 'interrupted') this.reportProblem(reason);
        };
        if (this.synth!.paused) this.synth!.resume();
        this.synth!.speak(u);
      } catch {
        this.reportProblem('exception');
      }
    };

    if (urgent) {
      // Interrupt what is being said. Chrome drops an utterance spoken in the same tick as cancel(), so wait a moment.
      this.stop();
      this.pending = setTimeout(() => {
        this.pending = null;
        say();
      }, 60);
    } else {
      say();
    }
  }
}

export const voiceGuidance = new VoiceGuidance();
