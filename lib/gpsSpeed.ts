/**
 * Speed worked out from movement, for phones that report none (Android WebView often gives `coords.speed = null`).
 *
 * Distance is measured from an ANCHOR, the last position where the rider had clearly moved, not from the previous fix.
 * At one fix a second a slow rider covers less than the GPS noise between two fixes, so comparing neighbouring fixes
 * reads 0 for anything below walking-to-jogging pace (or far more with a weak signal).
 */
import { haversineMeters } from './geo';

export interface SpeedFix {
  lat: number;
  lng: number;
  /** metres, as reported by the phone */
  accuracy: number;
  timestamp: number;
}

const MAX_GAP_S = 15; // after a longer silence (screen off) the old anchor says nothing about the current speed
const MIN_DT_S = 0.5;

export function createSpeedEstimator() {
  let anchor: SpeedFix | null = null;
  let lastAt = 0;
  let speed = 0;

  return {
    /** metres per second */
    push(fix: SpeedFix): number {
      const gap = (fix.timestamp - lastAt) / 1000;
      lastAt = fix.timestamp;
      if (!anchor || gap > MAX_GAP_S || gap < 0) {
        anchor = fix;
        speed = 0;
        return speed;
      }

      const dt = (fix.timestamp - anchor.timestamp) / 1000;
      const noise = Math.max(3, 0.3 * (fix.accuracy || 10));
      const moved = haversineMeters(anchor.lat, anchor.lng, fix.lat, fix.lng);

      if (moved >= noise && dt >= MIN_DT_S) {
        speed = moved / dt;
        anchor = fix;
      } else if (dt >= Math.min(MAX_GAP_S, Math.max(4, noise / 1.2))) {
        // not out of the noise circle for this long: standing still
        speed = 0;
        anchor = fix;
      }
      return speed; // otherwise too early to tell: keep the last value
    },
  };
}
