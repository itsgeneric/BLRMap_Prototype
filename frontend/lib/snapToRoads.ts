/**
 * Redraw a route on Google's own road geometry (Google Roads API, snapToRoads).
 *
 * Why: routes are computed on the OpenStreetMap road graph, and on many inner roads
 * OSM's centre-line sits 5-15 m from where Google's basemap draws the same road. At
 * street zoom the line then appears to run along the side of the road or through the
 * edge of buildings. The Dynamic route shows this far more than Shortest because it
 * deliberately uses inner roads, while Shortest mostly stays on major roads that OSM
 * maps very accurately.
 *
 * Only the drawn geometry changes: which roads the route takes is still decided by the
 * backend. Each snapped piece is checked against the original route and the original
 * geometry is kept wherever Google's snap disagrees (different road, missing points).
 * If the Roads API is not enabled for the key, the original geometry is used.
 *
 * Disable with NEXT_PUBLIC_SNAP_ROUTES=0.
 */
import { LatLng } from './types';
import { GOOGLE_MAPS_API_KEY } from './mapsKey';
import { buildRouteIndex, projectOnRoute, haversine } from './navigation';

const ENABLED = process.env.NEXT_PUBLIC_SNAP_ROUTES !== '0';
const ROADS_URL = 'https://roads.googleapis.com/v1/snapToRoads';
const MAX_POINTS = 100;          // Roads API limit per request
const OVERLAP = 5;               // points shared by consecutive requests, for continuity
const MIN_SPACING_M = 15;        // drop route vertices closer than this to the last one
const MAX_SPACING_M = 50;        // add points on long straight edges so the snap stays on the road
const MAX_DEVIATION_M = 60;      // OSM inner roads can sit up to ~45 m from Google's; beyond this = other road
const ALONG_SLACK_M = 15;         // a snapped point may sit this far before/after its input point along the route
const BACKTRACK_M = 5;           // ...and may step back this much (GPS-style jitter at junctions)
const MAX_LENGTH_RATIO = 1.3;    // snapped span much longer than ours = it went round a block

let unavailable = false;          // set once the API refuses the key, to stop retrying
const cache = new Map<string, LatLng[]>();

function resample(path: LatLng[]): LatLng[] {
  const out: LatLng[] = [path[0]];
  for (let i = 1; i < path.length; i++) {
    const prev = out[out.length - 1];
    const p = path[i];
    const d = haversine(prev[0], prev[1], p[0], p[1]);
    if (d < MIN_SPACING_M && i !== path.length - 1) continue;
    const extra = Math.floor(d / MAX_SPACING_M);
    for (let k = 1; k <= extra; k++) {
      const t = k / (extra + 1);
      out.push([prev[0] + (p[0] - prev[0]) * t, prev[1] + (p[1] - prev[1]) * t]);
    }
    out.push(p);
  }
  return out;
}

function lengthOf(pts: LatLng[]): number {
  let s = 0;
  for (let i = 1; i < pts.length; i++) s += haversine(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1]);
  return s;
}

interface SnappedPoint {
  location: { latitude: number; longitude: number };
  originalIndex?: number;
}

async function snapChunk(chunk: LatLng[], signal?: AbortSignal): Promise<SnappedPoint[] | null> {
  const path = chunk.map(([a, b]) => `${a.toFixed(6)},${b.toFixed(6)}`).join('|');
  const url = `${ROADS_URL}?interpolate=true&path=${encodeURIComponent(path)}&key=${GOOGLE_MAPS_API_KEY}`;
  const res = await fetch(url, { signal });
  if (!res.ok) {
    if ((res.status === 400 || res.status === 403) && !unavailable) {
      unavailable = true;
      console.warn(
        'Route snapping to Google roads is off: the Roads API refused the request ' +
          `(HTTP ${res.status}). Enable "Roads API" for the Google Maps key to turn it on.`
      );
    }
    return null;
  }
  const data = await res.json();
  return Array.isArray(data.snappedPoints) ? data.snappedPoints : null;
}

/**
 * Turn one request's output into route points. The output is judged span by span
 * (between two consecutive input points): a span is drawn on Google's road when it
 * stays within MAX_DEVIATION_M of our route and isn't much longer than ours (going
 * round a block = Google picked another road); otherwise our own points are used for
 * that span only. Returns the points from input index keepFrom on, and how many spans
 * were replaced.
 */
function buildPiece(
  snapped: SnappedPoint[] | null,
  chunk: LatLng[],
  keepFrom: number,
  routeIdx: ReturnType<typeof buildRouteIndex>
): { pts: LatLng[]; replaced: number; spans: number } {
  const original = chunk.slice(keepFrom);
  if (!snapped || snapped.length < 2) return { pts: original, replaced: 0, spans: 0 };

  const anchors: number[] = []; // positions in snapped[] of returned input points, in order
  for (let j = 0; j < snapped.length; j++) {
    const oi = snapped[j].originalIndex;
    if (oi != null && oi >= keepFrom && (!anchors.length || oi > snapped[anchors[anchors.length - 1]].originalIndex!)) {
      anchors.push(j);
    }
  }
  if (anchors.length < 2) return { pts: original, replaced: 0, spans: 0 };

  const loc = (p: SnappedPoint): LatLng => [p.location.latitude, p.location.longitude];
  const project = (p: LatLng) => projectOnRoute(routeIdx, p[0], p[1], null);
  const inAlong = new Map<number, number>();
  const alongOf = (i: number) => {
    if (!inAlong.has(i)) inAlong.set(i, project(chunk[i])?.along ?? 0);
    return inAlong.get(i)!;
  };

  // Google's span from input point ia to ib is used only if it follows our route:
  // close to it, moving forward along it (no U-shaped detours into side streets,
  // no point snapped back up the road), and not much longer than ours.
  const spanOk = (theirs: LatLng[], ia: number, ib: number) => {
    const lo = alongOf(ia) - ALONG_SLACK_M, hi = alongOf(ib) + ALONG_SLACK_M;
    let last = -Infinity;
    for (const p of theirs) {
      const pr = project(p);
      if (!pr || pr.distance > MAX_DEVIATION_M) return false;
      if (pr.along < lo || pr.along > hi || pr.along < last - BACKTRACK_M) return false;
      last = Math.max(last, pr.along);
    }
    return lengthOf(theirs) <= lengthOf(chunk.slice(ia, ib + 1)) * MAX_LENGTH_RATIO + 25;
  };

  // Our points before the first returned input point
  const firstOi = snapped[anchors[0]].originalIndex!;
  const out: LatLng[] = chunk.slice(keepFrom, firstOi);
  const firstAnchor = loc(snapped[anchors[0]]);
  out.push(spanOk([firstAnchor], firstOi, firstOi) ? firstAnchor : chunk[firstOi]);

  let replaced = 0;
  for (let t = 0; t + 1 < anchors.length; t++) {
    const ja = anchors[t], jb = anchors[t + 1];
    const ia = snapped[ja].originalIndex!, ib = snapped[jb].originalIndex!;
    const theirs = snapped.slice(ja, jb + 1).map(loc);
    // The end point must also be good as the start of the next span
    const ok = spanOk(theirs, ia, ib) && spanOk([theirs[theirs.length - 1]], ib, ib);
    if (ok) replaced++;
    out.push(...(ok ? theirs : chunk.slice(ia, ib + 1)).slice(1));
  }
  // Our points after the last returned input point
  out.push(...chunk.slice(snapped[anchors[anchors.length - 1]].originalIndex! + 1));
  return { pts: out, replaced, spans: anchors.length - 1 };
}

export async function snapRouteToGoogleRoads(path: LatLng[], signal?: AbortSignal): Promise<LatLng[]> {
  if (!ENABLED || unavailable || !GOOGLE_MAPS_API_KEY || path.length < 2) return path;
  const cacheKey = `${path[0]}|${path[path.length - 1]}|${path.length}|${lengthOf(path).toFixed(0)}`;
  const hit = cache.get(cacheKey);
  if (hit) return hit;

  const pts = resample(path);
  const routeIdx = buildRouteIndex(path);
  const step = MAX_POINTS - OVERLAP;
  const starts: number[] = [];
  for (let s = 0; s < pts.length - 1; s += step) {
    starts.push(s);
    if (s + MAX_POINTS >= pts.length) break;
  }

  try {
    const results = await Promise.all(
      starts.map((s) => snapChunk(pts.slice(s, s + MAX_POINTS), signal))
    );
    const out: LatLng[] = [];
    let replaced = 0;
    let spans = 0;
    starts.forEach((s, c) => {
      const chunk = pts.slice(s, s + MAX_POINTS);
      const piece = buildPiece(results[c], chunk, c === 0 ? 0 : OVERLAP, routeIdx);
      replaced += piece.replaced;
      spans += piece.spans;
      out.push(...piece.pts);
    });
    console.debug(`Route drawn on Google roads: ${replaced}/${spans} spans (rest kept from OSM)`);
    // Keep the exact start and end the backend chose (on the road, by the pins)
    out[0] = path[0];
    out[out.length - 1] = path[path.length - 1];
    if (replaced === 0) return path;
    cache.set(cacheKey, out);
    return out;
  } catch (err: any) {
    if (err?.name !== 'AbortError') console.warn('Route snapping to Google roads failed:', err);
    return path;
  }
}
