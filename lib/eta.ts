/**
 * Trip timing: the ONE place that decides how long a route takes and when the rider arrives (pure, testable with `node --test`).
 *
 *  - Before the trip: the route's planned duration (the backend sums length / free-flow speed per road class, plus turn delays).
 *  - During the trip: the plan is blended with the rider's ACTUAL pace so far (distance travelled / time elapsed, which already
 *    includes traffic lights and slow stretches). The longer the rider has been going, the more the real pace counts.
 *  - The result is smoothed, so the arrival time does not jump around with every GPS fix, and it counts down every second
 *    between fixes, like Google Maps.
 */

/** Typical Bengaluru two-wheeler average (about 23 km/h) used only when a route has no planned duration. */
export const FALLBACK_SPEED_MPS = 6.5;

const MAX_RIDE_MPS = 35; // about 126 km/h

/** Planned minutes of a route: the server's duration when present, otherwise a distance-based guess at `fallbackKmh`. */
export function routeMinutes(
  route: { duration_s?: number | null; distance_km?: number | null } | null | undefined,
  fallbackKmh = 23
): number {
  if (!route) return Infinity;
  if (route.duration_s && route.duration_s > 0) return Math.max(1, Math.round(route.duration_s / 60));
  const km = route.distance_km || 0;
  return Math.max(1, Math.round((km / fallbackKmh) * 60));
}

/** "10:42 AM" in the phone's own clock format. */
export function formatClock(epochMs: number): string {
  return new Date(epochMs).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

/** "3 min", "1 h 05 min". Rounds UP to the minute (Google never shows "0 min" while you are still driving). */
export function formatRemaining(seconds: number): string {
  if (seconds < 45) return '< 1 min';
  const mins = Math.max(1, Math.round(seconds / 60));
  if (mins < 60) return `${mins} min`;
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m === 0 ? `${h} h` : `${h} h ${String(m).padStart(2, '0')} min`;
}

// --------------------------------------------------------------------------------------------- speedometer

/**
 * Smooths the GPS speed for display. It rises quickly and falls a little slower (like a real speedometer), and anything below
 * 1.5 km/h reads 0 so standing still at a signal does not flicker between 0 and 2 km/h.
 */
export class SpeedSmoother {
  private v = 0;

  reset(): void {
    this.v = 0;
  }

  /** speedMps: metres per second (null/undefined = unknown, treated as unchanged). Returns km/h as a whole number. */
  push(speedMps: number | null | undefined): number {
    if (speedMps !== null && speedMps !== undefined && Number.isFinite(speedMps) && speedMps >= 0) {
      const alpha = speedMps > this.v ? 0.5 : 0.3;
      this.v += alpha * (speedMps - this.v);
      if (this.v * 3.6 < 1.5 && speedMps * 3.6 < 1.5) this.v = 0;
    }
    return Math.round(this.v * 3.6);
  }
}

// --------------------------------------------------------------------------------------------- ETA

export interface EtaResult {
  remainingS: number;
  arrivalMs: number;
  /** the pace the estimate currently assumes, m/s */
  paceMps: number;
}

export class EtaEstimator {
  private startMs = 0;
  private totalM = 0;
  private plannedMps = FALLBACK_SPEED_MPS;
  private doneBeforeM = 0; // distance covered on earlier routes of this trip (after reroutes)
  private lastRemainingM = 0;
  private lastAtMs = 0;
  private skippedM = 0; // distance jumped over: a start part-way along the route, or a gap in the signal
  private shown: { remainingS: number; atMs: number } | null = null;

  /** A trip begins (the rider taps Start). */
  startTrip(nowMs: number): void {
    this.startMs = nowMs;
    this.totalM = 0; // forget the previous trip's route, or setRoute() would count it as already travelled
    this.doneBeforeM = 0;
    this.lastRemainingM = 0;
    this.lastAtMs = nowMs;
    this.skippedM = 0;
    this.shown = null;
  }

  /** The active route is set, or replaced after a reroute: distance travelled so far on this trip is kept. */
  setRoute(totalM: number, plannedDurationS: number | null | undefined): void {
    if (this.totalM > 0 && this.lastRemainingM >= 0) {
      this.doneBeforeM += Math.max(0, this.totalM - this.lastRemainingM);
    }
    this.totalM = Math.max(0, totalM);
    this.lastRemainingM = this.totalM;
    this.plannedMps =
      plannedDurationS && plannedDurationS > 0 && totalM > 0
        ? Math.min(25, Math.max(0.5, totalM / plannedDurationS))
        : FALLBACK_SPEED_MPS;
  }

  update(remainingM: number, nowMs: number): EtaResult {
    const remaining = Math.max(0, remainingM);
    // More progress than any two-wheeler could make since the last update was not ridden. Without this, starting part-way
    // along a route looked like riding that far in no time, and the arrival time came out far too early.
    const drop = this.lastRemainingM - remaining;
    const possible = (MAX_RIDE_MPS * Math.max(0, nowMs - this.lastAtMs)) / 1000 + 100;
    if (drop > possible) this.skippedM += drop;
    this.lastRemainingM = remaining;
    this.lastAtMs = nowMs;

    const travelled = Math.max(0, this.doneBeforeM + Math.max(0, this.totalM - remaining) - this.skippedM);
    const elapsedS = Math.max(0, (nowMs - this.startMs) / 1000);

    // The rider's real pace counts only once there is enough to measure, and more the further they have gone.
    const observed = elapsedS >= 30 && travelled >= 150 ? Math.min(22, Math.max(1.5, travelled / elapsedS)) : null;
    const weight = observed === null ? 0 : Math.min(0.75, travelled / 2000);
    const pace = (1 - weight) * this.plannedMps + weight * (observed ?? this.plannedMps);

    const raw = remaining / pace;
    let remainingS = raw;
    if (this.shown) {
      // continue the countdown from the last shown value, then move 25% of the way to the fresh estimate
      const expected = Math.max(0, this.shown.remainingS - (nowMs - this.shown.atMs) / 1000);
      remainingS = expected + 0.25 * (raw - expected);
    }
    if (remaining < 30) remainingS = Math.min(remainingS, 15);
    remainingS = Math.max(0, remainingS);

    this.shown = { remainingS, atMs: nowMs };
    return { remainingS, arrivalMs: nowMs + remainingS * 1000, paceMps: pace };
  }

  /** Seconds left RIGHT NOW (counts down between GPS fixes, so the display ticks every second). */
  remainingAt(nowMs: number): number {
    if (!this.shown) return 0;
    return Math.max(0, this.shown.remainingS - (nowMs - this.shown.atMs) / 1000);
  }
}
