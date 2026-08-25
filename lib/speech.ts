class VoiceGuidance {
  private synth: SpeechSynthesis | null = null;
  private enabled: boolean = true;
  private lastSpokenText: string = '';
  private lastSpokenTime: number = 0;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
    }
  }

  public setEnabled(enabled: boolean) {
    this.enabled = enabled;
    if (!enabled && this.synth) {
      this.synth.cancel();
    }
  }

  public isEnabled(): boolean {
    return this.enabled;
  }

  public speak(text: string, force: boolean = false) {
    if (!this.enabled || !this.synth) return;

    const now = Date.now();
    // Don't repeat the exact same instruction within 10 seconds unless forced
    if (!force && text === this.lastSpokenText && now - this.lastSpokenTime < 10000) {
      return;
    }

    this.synth.cancel(); // Stop current speech before speaking new instruction

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';

    this.lastSpokenText = text;
    this.lastSpokenTime = now;

    this.synth.speak(utterance);
  }
}

export const voiceGuidance = new VoiceGuidance();
