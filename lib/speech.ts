class VoiceGuidance {
  private synth: SpeechSynthesis | null = null;
  private enabled: boolean = false; // Default OFF
  private lastSpokenText: string = '';
  private lastSpokenTime: number = 0;
  private spokenMilestones: Set<string> = new Set();

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

  public resetMilestones() {
    this.spokenMilestones.clear();
    this.lastSpokenText = '';
    this.lastSpokenTime = 0;
  }

  /**
   * Speaks ONLY turn directions when user has explicitly unmuted/enabled the speaker.
   */
  public speakManeuver(instruction: string, distanceMeters: number, maneuverIndex: number) {
    if (!this.enabled || !this.synth) return;

    let milestoneBucket: string | null = null;
    let spokenDistance = '';

    if (distanceMeters <= 35) {
      milestoneBucket = `${maneuverIndex}_now`;
      spokenDistance = 'Now';
    } else if (distanceMeters <= 120 && distanceMeters > 70) {
      milestoneBucket = `${maneuverIndex}_100m`;
      spokenDistance = `In 100 meters`;
    } else if (distanceMeters <= 300 && distanceMeters > 220) {
      milestoneBucket = `${maneuverIndex}_250m`;
      spokenDistance = `In 250 meters`;
    }

    if (!milestoneBucket || this.spokenMilestones.has(milestoneBucket)) {
      return;
    }

    this.spokenMilestones.add(milestoneBucket);
    const speechText = spokenDistance === 'Now' ? `${instruction} now` : `${spokenDistance}, ${instruction}`;
    this.speak(speechText);
  }

  public speak(text: string) {
    if (!this.enabled || !this.synth || !text) return;

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
