/**
 * When and what to say during navigation (pure, testable with `node --test`).
 *
 * Each maneuver is announced in up to three stages: "prepare" (far), "near", "now". A stage is decided from the distance
 * ALONG the route and the rider's speed, so faster riders hear it earlier. A stage fires once. If a GPS fix jumps past a band,
 * the current band still fires, and the earlier ones are marked as done (so nothing is announced late or twice).
 * The first time a maneuver is seen (route start or after a reroute) only the band the rider is already in is spoken.
 */

export type VoiceStage = 'prepare' | 'near' | 'now';

export interface VoiceCue {
  text: string;
  stage: VoiceStage;
  /** "now" cues interrupt whatever is being spoken */
  urgent: boolean;
}

const ORDER: VoiceStage[] = ['prepare', 'near', 'now'];

export function stageBands(speedMps: number) {
  const v = Math.max(0, speedMps || 0);
  const now = Math.max(20, v * 2.5);
  const near = Math.max(100, v * 7, now + 40);
  const prepare = Math.max(300, v * 20, near + 50);
  return { prepare, near, now };
}

export function formatSpokenDistance(meters: number): string {
  if (meters >= 950) {
    const km = Math.round(meters / 100) / 10;
    return km === 1 ? '1 kilometre' : `${km} kilometres`;
  }
  const rounded = Math.max(50, Math.round(meters / 50) * 50);
  return `${rounded} metres`;
}

const ACTION: Record<string, string> = {
  turn_left: 'turn left',
  turn_right: 'turn right',
  slight_left: 'bear left',
  slight_right: 'bear right',
  u_turn: 'make a U-turn',
  straight: 'continue straight',
};

function roadSuffix(roadName: string | null | undefined): string {
  return roadName && roadName !== 'Unnamed Road' ? ` onto ${roadName}` : '';
}

export class VoicePlanner {
  private seen = new Map<string, Set<VoiceStage>>();

  reset(): void {
    this.seen.clear();
  }

  /** `key` must be unique per maneuver of the current route, e.g. `${routeId}:${maneuverIndex}`. */
  evaluate(
    key: string,
    type: string,
    roadName: string | null | undefined,
    distanceM: number,
    speedMps: number
  ): VoiceCue | null {
    if (type === 'depart') return null;
    const bands = stageBands(speedMps);
    const stage: VoiceStage | null =
      distanceM <= bands.now ? 'now' : distanceM <= bands.near ? 'near' : distanceM <= bands.prepare ? 'prepare' : null;
    if (!stage) return null;

    let done = this.seen.get(key);
    if (!done) {
      done = new Set<VoiceStage>();
      this.seen.set(key, done);
    }
    if (done.has(stage)) return null;
    for (const s of ORDER.slice(0, ORDER.indexOf(stage) + 1)) done.add(s); // this band and every earlier one are now done

    if (type === 'arrive') {
      if (stage === 'now') return null; // the arrival itself is announced when the trip completes
      return {
        stage,
        urgent: false,
        text: `In ${formatSpokenDistance(distanceM)}, you will arrive at your destination`,
      };
    }

    const action = ACTION[type] ?? 'continue';
    if (stage === 'now') {
      return { stage, urgent: true, text: action.charAt(0).toUpperCase() + action.slice(1) };
    }
    const where = stage === 'prepare' ? roadSuffix(roadName) : '';
    return { stage, urgent: false, text: `In ${formatSpokenDistance(distanceM)}, ${action}${where}` };
  }
}
