/**
 * GPS filtering and route matching (pure functions, no imports, testable with `node --test`).
 *
 * The pipeline keeps four things SEPARATE on purpose:
 *   raw GPS fix  ->  GpsFilter  ->  filtered position  ->  RouteMatcher  ->  matched point on the route
 *                                         |                                        |
 *                       used for OFF-ROUTE detection                 used to DRAW the marker (only when close enough)
 *
 * The marker is drawn on the route only while the filtered position is genuinely close to it; a rider who really leaves the
 * route is NOT hidden by snapping: distanceM is measured from the UNSNAPPED filtered position.
 */

export type LatLngTuple = [number, number];

const KY = 110574; // metres per degree of latitude (Bengaluru)
const MAX_SPEED_MPS = 45; // faster than this between two fixes is a GPS jump, not movement

export function angleDiffDeg(a: number, b: number): number {
  return Math.abs(((a - b + 540) % 360) - 180);
}

// --------------------------------------------------------------------------------------------- filter

export interface GpsFix {
  lat: number;
  lng: number;
  accuracy?: number | null;
  speed?: number | null;
  timestamp: number;
}

export interface FilteredFix {
  lat: number;
  lng: number;
  accuracy: number;
}

/**
 * A small Kalman-style filter in local metres. Each fix is weighted by its reported accuracy (a poor fix moves the estimate
 * little, a good one a lot); the process noise grows with speed so the estimate keeps up with a moving rider. Fixes that would
 * need an impossible speed are rejected (up to 3 in a row, then the filter re-syncs).
 */
export class GpsFilter {
  private lat0 = 0;
  private lng0 = 0;
  private kx = 111320;
  private x = 0;
  private y = 0;
  private p = 0;
  private t = 0;
  private has = false;
  private rejected = 0;

  reset(): void {
    this.has = false;
    this.rejected = 0;
  }

  update(fix: GpsFix): FilteredFix {
    const acc = Math.min(100, Math.max(3, fix.accuracy ?? 15));

    if (!this.has) {
      this.lat0 = fix.lat;
      this.lng0 = fix.lng;
      this.kx = 111320 * Math.cos((fix.lat * Math.PI) / 180);
      this.x = 0;
      this.y = 0;
      this.p = acc * acc;
      this.t = fix.timestamp;
      this.has = true;
      this.rejected = 0;
      return { lat: fix.lat, lng: fix.lng, accuracy: acc };
    }

    const zx = (fix.lng - this.lng0) * this.kx;
    const zy = (fix.lat - this.lat0) * KY;
    const dt = Math.min(10, Math.max(0.05, (fix.timestamp - this.t) / 1000));
    const jump = Math.hypot(zx - this.x, zy - this.y);

    if (jump / dt > MAX_SPEED_MPS && jump > Math.max(40, 3 * acc) && this.rejected < 3) {
      this.rejected += 1;
      return this.estimate();
    }
    this.rejected = 0;

    const speed = Math.max(0.5, fix.speed ?? 0);
    this.p += speed * dt * (speed * dt) + 1;
    const gain = this.p / (this.p + acc * acc);
    this.x += gain * (zx - this.x);
    this.y += gain * (zy - this.y);
    this.p = (1 - gain) * this.p;
    this.t = fix.timestamp;
    return this.estimate();
  }

  private estimate(): FilteredFix {
    return {
      lat: this.lat0 + this.y / KY,
      lng: this.lng0 + this.x / this.kx,
      accuracy: Math.max(3, Math.sqrt(this.p)),
    };
  }
}

// --------------------------------------------------------------------------------------------- route geometry

export interface RouteGeometry {
  x: number[];
  y: number[];
  cum: number[]; // cumulative distance (m) at each vertex
  total: number;
  lat0: number;
  lng0: number;
  kx: number;
}

export function buildRoute(polyline: LatLngTuple[]): RouteGeometry {
  const lat0 = polyline[0][0];
  const lng0 = polyline[0][1];
  const kx = 111320 * Math.cos((lat0 * Math.PI) / 180);
  const x: number[] = [];
  const y: number[] = [];
  const cum: number[] = [];
  let run = 0;
  for (let i = 0; i < polyline.length; i++) {
    x.push((polyline[i][1] - lng0) * kx);
    y.push((polyline[i][0] - lat0) * KY);
    if (i > 0) run += Math.hypot(x[i] - x[i - 1], y[i] - y[i - 1]);
    cum.push(run);
  }
  return { x, y, cum, total: run, lat0, lng0, kx };
}

export interface Projection {
  index: number; // segment index (vertex i -> i+1)
  alongM: number;
  distanceM: number;
  lat: number;
  lng: number;
}

function project(route: RouteGeometry, i: number, px: number, py: number): Projection | null {
  const ax = route.x[i];
  const ay = route.y[i];
  const dx = route.x[i + 1] - ax;
  const dy = route.y[i + 1] - ay;
  const l2 = dx * dx + dy * dy;
  if (l2 < 1e-9) return null;
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / l2));
  const qx = ax + t * dx;
  const qy = ay + t * dy;
  return {
    index: i,
    alongM: route.cum[i] + t * Math.sqrt(l2),
    distanceM: Math.hypot(px - qx, py - qy),
    lat: route.lat0 + qy / KY,
    lng: route.lng0 + qx / route.kx,
  };
}

/** Closest point on the whole route to (lat, lng). Used once per route to place maneuvers along it. */
export function projectOnRoute(route: RouteGeometry, lat: number, lng: number): Projection {
  const px = (lng - route.lng0) * route.kx;
  const py = (lat - route.lat0) * KY;
  let best: Projection | null = null;
  for (let i = 0; i < route.x.length - 1; i++) {
    const c = project(route, i, px, py);
    if (c && (!best || c.distanceM < best.distanceM)) best = c;
  }
  return best ?? { index: 0, alongM: 0, distanceM: Infinity, lat: route.lat0, lng: route.lng0 };
}

// --------------------------------------------------------------------------------------------- matcher

export interface MatchResult {
  segmentIndex: number;
  alongM: number;
  /** distance from the UNSNAPPED filtered position to the route: this is what off-route detection must use */
  distanceM: number;
  projLat: number;
  projLng: number;
  snapped: boolean;
  /** where to draw the marker: the point on the route when close enough, otherwise the filtered position itself */
  displayLat: number;
  displayLng: number;
}

/**
 * Projects the filtered position onto the ACTIVE route only (so it can never jump to an unrelated parallel road). It searches a
 * window around the last known segment first (cheap, and keeps progress monotonic); if nothing is close it scans the whole
 * route. Candidates are scored by distance plus a heading mismatch penalty (only when moving), and snapping uses hysteresis so
 * the marker does not flicker on and off the road.
 */
export class RouteMatcher {
  readonly route: RouteGeometry;
  private lastIndex = 0;
  private snapped = false;

  constructor(polyline: LatLngTuple[]) {
    this.route = buildRoute(polyline);
  }

  match(lat: number, lng: number, headingDeg: number | null, speedMps: number, accuracy: number): MatchResult {
    const r = this.route;
    const px = (lng - r.lng0) * r.kx;
    const py = (lat - r.lat0) * KY;
    const useHeading = headingDeg !== null && headingDeg !== undefined && speedMps >= 1.5;
    const last = r.x.length - 2;

    const scan = (from: number, to: number): { c: Projection; score: number } | null => {
      let best: { c: Projection; score: number } | null = null;
      for (let i = Math.max(0, from); i <= Math.min(last, to); i++) {
        const c = project(r, i, px, py);
        if (!c) continue;
        let score = c.distanceM;
        if (useHeading) {
          const bearing = (Math.atan2(r.x[i + 1] - r.x[i], r.y[i + 1] - r.y[i]) * 180) / Math.PI;
          score += (angleDiffDeg(headingDeg as number, (bearing + 360) % 360) / 180) * 30;
        }
        if (!best || score < best.score) best = { c, score };
      }
      return best;
    };

    let found = scan(this.lastIndex - 5, this.lastIndex + 80);
    if (!found || found.c.distanceM > 80) {
      const all = scan(0, last);
      if (all && (!found || all.c.distanceM < found.c.distanceM)) found = all;
    }
    const c: Projection = found
      ? found.c
      : { index: 0, alongM: 0, distanceM: Infinity, lat, lng };

    this.lastIndex = c.index;
    const limit = Math.max(15, 1.5 * accuracy) * (this.snapped ? 1.4 : 1);
    this.snapped = c.distanceM <= limit;

    return {
      segmentIndex: c.index,
      alongM: c.alongM,
      distanceM: c.distanceM,
      projLat: c.lat,
      projLng: c.lng,
      snapped: this.snapped,
      displayLat: this.snapped ? c.lat : lat,
      displayLng: this.snapped ? c.lng : lng,
    };
  }
}
