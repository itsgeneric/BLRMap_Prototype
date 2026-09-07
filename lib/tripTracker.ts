import { Point, TripSummary, JourneyStartPayload, JourneyCompletePayload, ReroutePayload } from './types';

const API_BASE = 'http://127.0.0.1:8000';
const SESSION_STORAGE_KEY = 'blrnav_session_id';

/**
 * Retrieves the anonymous persistent session ID from browser localStorage.
 * Generates and stores a new UUID if one doesn't exist yet.
 * Ensures zero-auth anonymous tracking.
 */
export function getSessionId(): string {
  if (typeof window === 'undefined') {
    return 'server_session';
  }

  try {
    let sid = localStorage.getItem(SESSION_STORAGE_KEY);
    if (!sid) {
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        sid = crypto.randomUUID();
      } else {
        sid = `anon_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
      }
      localStorage.setItem(SESSION_STORAGE_KEY, sid);
    }
    return sid;
  } catch {
    return 'fallback_session';
  }
}

/**
 * Fires when user taps "Start Navigation".
 * Enriches the planned route document in MongoDB with session_id,
 * human-readable origin/destination names, and transitions status to 'navigating'.
 */
export function startTrip(
  journeyId: string | null | undefined,
  origin: Point | null,
  destination: Point | null
): void {
  if (!journeyId || !origin || !destination) return;

  const sessionId = getSessionId();
  const payload: JourneyStartPayload = {
    session_id: sessionId,
    origin: {
      name: origin.name || 'Current Location',
      address: origin.address || undefined,
      lat: origin.lat,
      lng: origin.lng,
    },
    destination: {
      name: destination.name || 'Destination',
      address: destination.address || undefined,
      lat: destination.lat,
      lng: destination.lng,
    },
  };

  fetch(`${API_BASE}/journeys/${journeyId}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).catch((err) => {
    // Non-blocking fire-and-forget: fail gracefully without affecting UX
    console.debug('[TripTracker] startTrip notice:', err);
  });
}

/**
 * Fires when navigation engine confirms arrival at the destination.
 * Saves actual trip duration and average speed into the unified journey document.
 */
export function completeTrip(
  journeyId: string | null | undefined,
  summary: TripSummary
): void {
  if (!journeyId) return;

  const payload: JourneyCompletePayload = {
    actual_duration_secs: Math.max(1, summary.timeTakenSec),
    actual_avg_speed_kmh: Math.max(0, summary.avgSpeedKmh),
  };

  fetch(`${API_BASE}/journeys/${journeyId}/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).catch((err) => {
    console.debug('[TripTracker] completeTrip notice:', err);
  });
}

/**
 * Fires when user deviates off-route during live turn-by-turn navigation.
 * Appends the off-route coordinates and distance to the journey's reroute_events list.
 */
export function reportReroute(
  journeyId: string | null | undefined,
  lat: number,
  lng: number,
  distanceOffRouteM: number,
  timeSinceStartSecs: number
): void {
  if (!journeyId) return;

  const payload: ReroutePayload = {
    lat,
    lng,
    distance_off_route_m: Math.round(distanceOffRouteM),
    time_since_start_secs: Math.max(0, Math.round(timeSinceStartSecs)),
  };

  fetch(`${API_BASE}/journeys/${journeyId}/reroute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).catch((err) => {
    console.debug('[TripTracker] reportReroute notice:', err);
  });
}
