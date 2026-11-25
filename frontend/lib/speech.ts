/**
 * Spoken navigation prompts (Web Speech API).
 *
 * Prefers an Indian-English voice, falling back to any English voice. Each new
 * prompt interrupts the previous one, as in navigation apps, so a late prompt
 * never queues up behind an earlier one.
 */
class VoiceGuidance {
  private synth: SpeechSynthesis | null = null;
  private enabled = true;
  private voice: SpeechSynthesisVoice | null = null;
  private lastText = '';
  private lastTime = 0;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
      this.pickVoice();
      this.synth.addEventListener?.('voiceschanged', () => this.pickVoice());
    }
  }

  private pickVoice() {
    if (!this.synth) return;
    const voices = this.synth.getVoices();
    this.voice =
      voices.find((v) => v.lang === 'en-IN') ||
      voices.find((v) => v.lang?.startsWith('en-IN')) ||
      voices.find((v) => v.lang === 'en-GB') ||
      voices.find((v) => v.lang?.startsWith('en')) ||
      null;
  }

  public setEnabled(enabled: boolean) {
    this.enabled = enabled;
    if (!enabled) this.stop();
  }

  public isEnabled(): boolean {
    return this.enabled;
  }

  public stop() {
    this.synth?.cancel();
  }

  /** Speak a prompt now, interrupting anything still being spoken. */
  public speak(text: string) {
    if (!this.enabled || !this.synth || !text) return;
    const now = Date.now();
    if (text === this.lastText && now - this.lastTime < 4000) return;
    try {
      this.synth.cancel();
      const u = new SpeechSynthesisUtterance(text);
      if (this.voice) u.voice = this.voice;
      u.lang = this.voice?.lang || 'en-IN';
      u.rate = 1.0;
      u.pitch = 1.0;
      this.lastText = text;
      this.lastTime = now;
      this.synth.speak(u);
    } catch (e) {
      console.warn('Speech synthesis error:', e);
    }
  }

  /** Kept for older callers; prompts are now scheduled by the navigation engine. */
  public resetMilestones() {
    this.lastText = '';
    this.lastTime = 0;
  }
}

export const voiceGuidance = new VoiceGuidance();
