class VoiceGuidance {
  private synth: SpeechSynthesis | null = null;
  private enabled: boolean = true; // Default ON so rider hears navigation immediately
  private lastSpokenText: string = '';
  private lastSpokenTime: number = 0;
  private spokenMilestones: Set<string> = new Set();

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
    }
  }

  /**
   * Primes speech synthesis on a user touch/click gesture.
   * Required by Android WebView to unlock audio channels.
   */
  public prime() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
      if (!this.enabled || !this.synth) return;
      try {
        this.synth.cancel();
        const u = new SpeechSynthesisUtterance('Navigation started');
        u.volume = 1.0;
        u.rate = 1.05;
        u.lang = 'en-US';
        this.synth.speak(u);
      } catch (e) {
        console.warn('Speech prime warning:', e);
      }
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

  public resetMilestones() {
    this.spokenMilestones.clear();
    this.lastSpokenText = '';
    this.lastSpokenTime = 0;
  }

  /**
   * Speaks turn directions when user has enabled voice navigation.
   * Milestone-based: triggers early prep (≤300m), approach (≤110m), and immediate execution (≤35m).
   */
  public speakManeuver(instruction: string, distanceMeters: number, maneuverIndex: number) {
    if (!this.enabled || !this.synth) return;

    let milestoneBucket: string | null = null;
    let speechText = '';

    if (distanceMeters <= 35) {
      milestoneBucket = `${maneuverIndex}_now`;
      speechText = `${instruction} now`;
    } else if (distanceMeters <= 110) {
      milestoneBucket = `${maneuverIndex}_100m`;
      const roundedMeters = Math.max(40, Math.round(distanceMeters / 10) * 10);
      speechText = `In ${roundedMeters} meters, ${instruction}`;
    } else if (distanceMeters <= 300) {
      milestoneBucket = `${maneuverIndex}_300m`;
      const roundedMeters = Math.max(150, Math.round(distanceMeters / 50) * 50);
      speechText = `In ${roundedMeters} meters, ${instruction}`;
    }

    if (!milestoneBucket || this.spokenMilestones.has(milestoneBucket)) {
      return;
    }

    this.spokenMilestones.add(milestoneBucket);
    this.speak(speechText);
  }

  public speak(text: string) {
    if (!this.enabled || !text) return;
    if (!this.synth && typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
    }
    if (!this.synth) return;

    const now = Date.now();
    if (text === this.lastSpokenText && now - this.lastSpokenTime < 5000) {
      return;
    }

    try {
      this.synth.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05;
      utterance.pitch = 1.0;
      utterance.lang = 'en-US';

      this.lastSpokenText = text;
      this.lastSpokenTime = now;

      this.synth.speak(utterance);
    } catch (e) {
      console.warn('Speech synthesis error:', e);
    }
  }
}

export const voiceGuidance = new VoiceGuidance();
