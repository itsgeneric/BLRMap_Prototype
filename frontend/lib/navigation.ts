/**
 * Route-geometry helpers for turn-by-turn navigation.
 *
 * Progress is tracked as distance ALONG the route polyline ("along", metres),
 * which is how navigation apps decide which turn is next, how far away it is,
 * and how much of the trip is left. Straight-line distance to a turn is wrong
 * on curving roads, so nothing here uses it for guidance.
 */
import { LatLng, TurnManeuver } from './types';

const R = 6371000;
const toRad = (d: number) => (d * Math.PI) / 180;
const toDeg = (r: number) => (r * 180) / Math.PI;

export function haversine(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const dphi = toRad(lat2 - lat1);
  const dlam = toRad(lng2 - lng1);
  const a =
    Math.sin(dphi / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dlam / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function bearingDeg(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const y = Math.sin(toRad(lng2 - lng1)) * Math.cos(toRad(lat2));
  const x =
    Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) -
    Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(toRad(lng2 - lng1));
  return (toDeg(Math.atan2(y, x)) + 360) % 360;
}

/** Signed smallest difference b - a in degrees, in (-180, 180]. */
export function angleDiff(a: number, b: number): number {
  let d = ((b - a + 540) % 360) - 180;
  if (d === -180) d = 180;
  return d;
}

/** Interpolate between two bearings along the shortest arc. */
export function lerpAngle(a: number, b: number, t: number): number {
  return (a + angleDiff(a, b) * t + 360) % 360;
}

/** Point `meters` from (lat, lng) on the given bearing. */
export function destinationPoint(lat: number, lng: number, bearing: number, meters: number) {
  const d = meters / R;
  const th = toRad(bearing);
  const p1 = toRad(lat);
  const l1 = toRad(lng);
  const p2 = Math.asin(Math.sin(p1) * Math.cos(d) + Math.cos(p1) * Math.sin(d) * Math.cos(th));
  const l2 = l1 + Math.atan2(Math.sin(th) * Math.sin(d) * Math.cos(p1), Math.cos(d) - Math.sin(p1) * Math.sin(p2));
  return { lat: toDeg(p2), lng: toDeg(l2) };
}

// ─────────────────────────────────────────────────────────────────
// Route index & projection
// ─────────────────────────────────────────────────────────────────

export interface RouteIndex {
  path: LatLng[];
  cum: number[]; // cumulative distance at each vertex
  total: number;
}

export function buildRouteIndex(path: LatLng[]): RouteIndex {
  const cum = [0];
  for (let i = 1; i < path.length; i++) {
    cum.push(cum[i - 1] + haversine(path[i - 1][0], path[i - 1][1], path[i][0], path[i][1]));
  }
  return { path, cum, total: cum[cum.length - 1] || 0 };
}

export interface RouteProjection {
  along: number;
  lat: number;
  lng: number;
  distance: number; // metres from the query point to the route
  bearing: number; // route direction at that point
  segIndex: number;
}

function projectOnSegment(idx: RouteIndex, i: number, lat: number, lng: number): RouteProjection {
  const [aLat, aLng] = idx.path[i];
  const [bLat, bLng] = idx.path[i + 1];
  // local planar metres around the segment start
  const kx = Math.cos(toRad(aLat)) * 111320;
  const ky = 110540;
  const bx = (bLng - aLng) * kx;
  const by = (bLat - aLat) * ky;
  const px = (lng - aLng) * kx;
  const py = (lat - aLat) * ky;
  const len2 = bx * bx + by * by;
  const t = len2 === 0 ? 0 : Math.max(0, Math.min(1, (px * bx + py * by) / len2));
  const qLat = aLat + (bLat - aLat) * t;
  const qLng = aLng + (bLng - aLng) * t;
  return {
    along: idx.cum[i] + (idx.cum[i + 1] - idx.cum[i]) * t,
    lat: qLat,
    lng: qLng,
    distance: Math.hypot(px - bx * t, py - by * t),
    bearing: len2 === 0 ? 0 : bearingDeg(aLat, aLng, bLat, bLng),
    segIndex: i,
  };
}

/**
 * Project a GPS fix onto the route. Searches near the previous progress first
 * (so a route that passes the same street twice doesn't jump), then the whole
 * route if the rider isn't near the expected part.
 */
export function projectOnRoute(
  idx: RouteIndex,
  lat: number,
  lng: number,
  hintAlong: number | null = null
): RouteProjection | null {
  const n = idx.path.length;
  if (n < 2) return null;

  const scan = (fromAlong: number, toAlong: number) => {
    let best: RouteProjection | null = null;
    for (let i = 0; i < n - 1; i++) {
      if (idx.cum[i + 1] < fromAlong || idx.cum[i] > toAlong) continue;
      const p = projectOnSegment(idx, i, lat, lng);
      if (!best || p.distance < best.distance) best = p;
    }
    return best;
  };

  if (hintAlong !== null) {
    const local = scan(hintAlong - 40, hintAlong + 400);
    if (local && local.distance < 40) return local;
  }
  return scan(-Infinity, Infinity);
}

/** Position and direction at a given distance along the route. */
export function pointAlong(idx: RouteIndex, along: number) {
  const a = Math.max(0, Math.min(idx.total, along));
  let i = 0;
  while (i < idx.cum.length - 2 && idx.cum[i + 1] < a) i++;
  const seg = idx.cum[i + 1] - idx.cum[i];
  const t = seg > 0 ? (a - idx.cum[i]) / seg : 0;
  const [aLat, aLng] = idx.path[i];
  const [bLat, bLng] = idx.path[i + 1] ?? idx.path[i];
  return {
    lat: aLat + (bLat - aLat) * t,
    lng: aLng + (bLng - aLng) * t,
    bearing: bearingDeg(aLat, aLng, bLat, bLng),
  };
}

/** The part of the route between two along-distances. */
export function sliceRoute(idx: RouteIndex, fromAlong: number, toAlong: number = idx.total): LatLng[] {
  const from = Math.max(0, fromAlong);
  const to = Math.min(idx.total, toAlong);
  if (to <= from || idx.path.length < 2) return [];
  const start = pointAlong(idx, from);
  const end = pointAlong(idx, to);
  const out: LatLng[] = [[start.lat, start.lng]];
  for (let i = 0; i < idx.path.length; i++) {
    if (idx.cum[i] > from && idx.cum[i] < to) out.push(idx.path[i]);
  }
  out.push([end.lat, end.lng]);
  return out;
}

/** along_m for every maneuver (computed client-side if the backend didn't send it). */
export function maneuverAlongs(idx: RouteIndex, maneuvers: TurnManeuver[]): number[] {
  let hint = 0;
  return maneuvers.map((m, i) => {
    if (typeof m.along_m === 'number') return m.along_m;
    if (i === 0) return 0;
    if (i === maneuvers.length - 1) return idx.total;
    const p = projectOnRoute(idx, m.lat, m.lng, hint);
    hint = p ? p.along : hint;
    return hint;
  });
}

// ─────────────────────────────────────────────────────────────────
// Display & voice text
// ─────────────────────────────────────────────────────────────────

/** Distance as shown in the turn banner: "50 m", "350 m", "1.2 km". */
export function formatBannerDistance(m: number): string {
  if (m < 100) return `${Math.max(10, Math.round(m / 10) * 10)} m`;
  if (m < 1000) return `${Math.round(m / 50) * 50} m`;
  if (m < 10000) return `${(Math.round(m / 100) / 10).toFixed(1)} km`;
  return `${Math.round(m / 1000)} km`;
}

/** Remaining trip time: "8 min", "1 hr 5 min". */
export function formatRemainingTime(seconds: number): string {
  const mins = Math.max(1, Math.round(seconds / 60));
  if (mins < 60) return `${mins} min`;
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m ? `${h} hr ${m} min` : `${h} hr`;
}

export function formatRemainingDistance(m: number): string {
  if (m < 1000) return `${Math.round(m / 10) * 10} m`;
  return `${(m / 1000).toFixed(m < 10000 ? 1 : 0)} km`;
}

export function formatClock(date: Date): string {
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

/** Spoken distance, Indian/British English: "300 metres", "1.5 kilometres". */
export function spokenDistance(m: number): string {
  if (m >= 950) {
    const km = Math.round(m / 500) / 2; // nearest half km
    return km === 1 ? '1 kilometre' : `${km} kilometres`;
  }
  const rounded = m >= 300 ? Math.round(m / 100) * 100 : Math.round(m / 50) * 50;
  return `${Math.max(50, rounded)} metres`;
}

const lowerFirst = (s: string) => (s ? s.charAt(0).toLowerCase() + s.slice(1) : s);

/** "In 300 metres, turn left onto 100 Feet Road" */
export function voicePreparePrompt(m: TurnManeuver, distance: number): string {
  return `In ${spokenDistance(distance)}, ${lowerFirst(m.instruction)}`;
}

/** Short form used for "…, then turn right". */
export function shortInstruction(m: TurnManeuver): string {
  switch (m.type) {
    case 'turn_left': return 'turn left';
    case 'turn_right': return 'turn right';
    case 'slight_left': return 'slight left';
    case 'slight_right': return 'slight right';
    case 'sharp_left': return 'sharp left';
    case 'sharp_right': return 'sharp right';
    case 'keep_left': return 'keep left';
    case 'keep_right': return 'keep right';
    case 'u_turn': return 'make a U-turn';
    case 'roundabout': return `take the exit at the roundabout`;
    case 'arrive': return 'you will arrive at your destination';
    default: return 'continue straight';
  }
}

/** Banner headline when a turn has no road name: "Turn left", "Keep right". */
export function maneuverHeadline(m: TurnManeuver): string {
  if (m.type === 'roundabout') return m.road_name || 'Roundabout';
  if (m.type === 'arrive') return 'Destination';
  return m.road_name || m.instruction;
}
