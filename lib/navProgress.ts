/**
 * Where the rider is relative to the turn-by-turn maneuvers (pure functions, testable with `node --test`).
 * Maneuvers come from the backend with a lat/lng each; once per route we convert them to a distance ALONG the route, so later
 * "how far to the next turn" is a subtraction along the road and not a straight line through buildings.
 */
import type { TurnManeuver } from './types';

export interface ManeuverAlong {
  index: number;
  alongM: number;
  maneuver: TurnManeuver;
}

/** project(lat, lng) must return the distance along the route (m) of the closest route point. */
export function mapManeuvers(
  maneuvers: TurnManeuver[],
  project: (lat: number, lng: number) => number
): ManeuverAlong[] {
  let floor = 0;
  return maneuvers.map((maneuver, index) => {
    floor = Math.max(floor, project(maneuver.lat, maneuver.lng)); // never out of order
    return { index, alongM: floor, maneuver };
  });
}

export interface Upcoming {
  index: number;
  distanceM: number;
  maneuver: TurnManeuver | null;
  next: TurnManeuver | null;
  /** the road the rider is on right now (the road of the last maneuver passed) */
  currentRoadName: string | null;
}

const PASSED_MARGIN_M = 12; // a maneuver counts as passed once the rider is this far beyond it

export function upcoming(list: ManeuverAlong[], alongM: number, fromIndex: number): Upcoming {
  if (list.length === 0) return { index: 0, distanceM: 0, maneuver: null, next: null, currentRoadName: null };

  let i = Math.min(Math.max(0, fromIndex), list.length - 1);
  while (i < list.length - 1 && (list[i].maneuver.type === 'depart' || list[i].alongM < alongM - PASSED_MARGIN_M)) i++;

  const road = (m: TurnManeuver | undefined) =>
    m && m.road_name && m.road_name !== 'Unnamed Road' ? m.road_name : null;
  const previous = i > 0 ? list[i - 1].maneuver : list[0].maneuver;

  return {
    index: i,
    distanceM: Math.max(0, list[i].alongM - alongM),
    maneuver: list[i].maneuver,
    next: i + 1 < list.length ? list[i + 1].maneuver : null,
    currentRoadName: road(previous),
  };
}
