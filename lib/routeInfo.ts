/**
 * Fills in what the screens need but the backend does not send, so every screen reads the same fields (pure, testable).
 *
 * The current backend sends its own travel time and turn instructions with street names, and those are always used. An
 * older backend sends neither (only the path, the distance and, for dynamic, Google's live time):
 *  - Travel time: the app's ORIGINAL formulas, unchanged, applied here once. The route cards, the "Fastest" choice and the
 *    arrival time all read the result, so they cannot disagree.
 *  - Turn instructions: estimated from the shape of the route (lib/deriveManeuvers.ts). They have no street names.
 * Anything a server does send is kept as it is.
 */
import type { RouteResponse } from './types';
import { deriveManeuvers } from './deriveManeuvers';

/** The original speeds, km/h */
export const SINGLE_ROUTE_KMH = 24;
export const COMPARE_SHORTEST_KMH = 22;
export const COMPARE_DYNAMIC_KMH = 27.5;

const fromDistance = (distanceKm: number | undefined, kmh: number) =>
  Math.max(2, Math.round(((distanceKm || 0) / kmh) * 60));

const fromTraffic = (mins: number) => Math.max(1, Math.round(mins));

/** One route on its own: Google's live time when the response has it, otherwise distance at 24 km/h. */
export function singleRouteMinutes(route: RouteResponse): number {
  return route.google_base_duration_mins
    ? fromTraffic(route.google_base_duration_mins)
    : fromDistance(route.distance_km, SINGLE_ROUTE_KMH);
}

/**
 * "Fastest" mode: the shortest route (main roads) takes Google's live time when known, otherwise distance at 22 km/h; the
 * dynamic route (two-wheeler inner roads) takes distance at 27.5 km/h.
 */
export function comparisonMinutes(
  shortest: RouteResponse | null,
  dynamic: RouteResponse | null
): { shortest: number; dynamic: number } {
  const traffic = dynamic?.google_base_duration_mins;
  return {
    shortest: !shortest
      ? Infinity
      : traffic
        ? fromTraffic(traffic)
        : fromDistance(shortest.distance_km, COMPARE_SHORTEST_KMH),
    dynamic: dynamic ? fromDistance(dynamic.distance_km, COMPARE_DYNAMIC_KMH) : Infinity,
  };
}

/** A successful answer with travel time and turn list filled in. Other answers are returned untouched. */
export function completeRoute(res: RouteResponse): RouteResponse {
  if (res.status !== 'success' || !res.path || res.path.length < 2) return res;
  const hasTurns = !!res.maneuvers && res.maneuvers.length > 1;
  return {
    ...res,
    duration_s: res.duration_s ?? singleRouteMinutes(res) * 60,
    time_from_app: res.duration_s == null,
    maneuvers: hasTurns ? res.maneuvers : deriveManeuvers(res.path),
  };
}
