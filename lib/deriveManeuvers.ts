/**
 * Fallback turn-by-turn: derive maneuvers from the SHAPE of the route when the server did not send any (for example when the
 * phone talks to an older backend). Pure function, testable with `node --test`.
 *
 * It looks at how much the direction changes over a 30 m window before and after each point and reports clear turns
 * ("Turn left", "Bear right", "Make a U-turn"). It cannot know road names, and a sharply curving road can look like a turn, so
 * the real maneuvers from the server (which know the junctions and street names) are always preferred.
 */
import type { TurnManeuver } from './types';

type LatLngTuple = [number, number];

const KY = 110574;
const WINDOW_M = 30;
const MIN_TURN_DEG = 40; // smaller changes are bends in the road, not turns
const MERGE_WITHIN_M = 40; // one real junction produces several neighbouring candidates: keep the sharpest

export function deriveManeuvers(path: LatLngTuple[]): TurnManeuver[] {
  if (!path || path.length < 2) return [];

  const lat0 = path[0][0];
  const lng0 = path[0][1];
  const kx = 111320 * Math.cos((lat0 * Math.PI) / 180);
  const x = path.map((p) => (p[1] - lng0) * kx);
  const y = path.map((p) => (p[0] - lat0) * KY);
  const cum: number[] = [0];
  for (let i = 1; i < path.length; i++) cum.push(cum[i - 1] + Math.hypot(x[i] - x[i - 1], y[i] - y[i - 1]));
  const total = cum[cum.length - 1];

  const pointAt = (c: number): [number, number] => {
    const target = Math.min(total, Math.max(0, c));
    let lo = 0;
    let hi = cum.length - 1;
    while (lo < hi - 1) {
      const mid = (lo + hi) >> 1;
      if (cum[mid] <= target) lo = mid;
      else hi = mid;
    }
    const span = cum[hi] - cum[lo] || 1;
    const t = (target - cum[lo]) / span;
    return [x[lo] + t * (x[hi] - x[lo]), y[lo] + t * (y[hi] - y[lo])];
  };
  const bearing = (a: [number, number], b: [number, number]) =>
    (Math.atan2(b[0] - a[0], b[1] - a[1]) * 180) / Math.PI;

  // candidates: signed direction change (positive = clockwise = a right turn) at every vertex with room on both sides
  const candidates: { along: number; delta: number; index: number }[] = [];
  for (let i = 1; i < path.length - 1; i++) {
    const c = cum[i];
    if (c < WINDOW_M || c > total - WINDOW_M) continue;
    const here = pointAt(c);
    const incoming = bearing(pointAt(c - WINDOW_M), here);
    const outgoing = bearing(here, pointAt(c + WINDOW_M));
    const delta = ((outgoing - incoming + 540) % 360) - 180;
    if (Math.abs(delta) >= MIN_TURN_DEG) candidates.push({ along: c, delta, index: i });
  }

  // keep only the sharpest candidate of each cluster
  const turns: typeof candidates = [];
  for (const cand of candidates) {
    const last = turns[turns.length - 1];
    if (last && cand.along - last.along < MERGE_WITHIN_M) {
      if (Math.abs(cand.delta) > Math.abs(last.delta)) turns[turns.length - 1] = cand;
    } else {
      turns.push(cand);
    }
  }

  const at = (i: number) => ({ lat: path[i][0], lng: path[i][1] });
  const make = (type: TurnManeuver['type'], instruction: string, along: number, i: number): TurnManeuver => ({
    type,
    instruction,
    road_name: 'Unnamed Road',
    distance_m: 0,
    ...at(i),
    // distance_m is filled in below as the distance to the next maneuver
    ...{ _along: along },
  } as TurnManeuver & { _along: number });

  const list: (TurnManeuver & { _along: number })[] = [make('depart', 'Start of route', 0, 0) as any];
  for (const t of turns) {
    const right = t.delta > 0;
    const size = Math.abs(t.delta);
    let type: TurnManeuver['type'];
    let text: string;
    if (size >= 140) {
      type = 'u_turn';
      text = 'Make a U-turn';
    } else if (size >= 60) {
      type = right ? 'turn_right' : 'turn_left';
      text = right ? 'Turn right' : 'Turn left';
    } else {
      type = right ? 'slight_right' : 'slight_left';
      text = right ? 'Bear right' : 'Bear left';
    }
    list.push(make(type, text, t.along, t.index) as any);
  }
  list.push(make('arrive', 'Arrive at your destination', total, path.length - 1) as any);

  return list.map((m, k) => {
    const next = list[k + 1];
    const { _along, ...rest } = m as any;
    return { ...rest, distance_m: next ? Math.round((next._along - _along) * 10) / 10 : 0 } as TurnManeuver;
  });
}
