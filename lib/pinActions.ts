/**
 * What the "dropped pin" card buttons do (pure, testable with `node --test`).
 *   Directions  -> the pin becomes the destination. With no start chosen yet, the rider's own location is used.
 *   Start here  -> the pin becomes the start; the destination stays as it was.
 */
import type { Point } from './types';

export type PinAction = 'directions' | 'start_here';

export interface TripEnds {
  origin: Point | null;
  destination: Point | null;
}

export interface PinActionResult extends TripEnds {
  /** true when the caller should fill the start in from the device's GPS */
  needGpsOrigin: boolean;
}

export function applyPinAction(action: PinAction, pin: Point, current: TripEnds): PinActionResult {
  if (action === 'directions') {
    return { origin: current.origin, destination: pin, needGpsOrigin: current.origin === null };
  }
  return { origin: pin, destination: current.destination, needGpsOrigin: false };
}

/** "Brigade Road, Ashok Nagar, Bengaluru 560001, India" -> "Brigade Road". Falls back to "Dropped pin". */
export function shortPlaceName(formattedAddress: string | null | undefined): string {
  const first = (formattedAddress || '').split(',')[0].trim();
  // Plus-code style first parts ("7FQ9+M2") are not useful names
  // Plus-code addresses ("7FQ9+M2 Bengaluru", "7FQ9+M2") are location codes, not names
  if (!first || /^[0-9A-Z]{4,8}\+[0-9A-Z]{2,3}(\s|$)/.test(first)) return 'Dropped pin';
  return first.length > 60 ? `${first.slice(0, 57)}...` : first;
}
