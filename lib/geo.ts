import { LatLng, TurnManeuver } from './types';

export function haversineMeters(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371000;
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const dphi = ((lat2 - lat1) * Math.PI) / 180;
  const dlam = ((lng2 - lng1) * Math.PI) / 180;

  const a =
    Math.sin(dphi / 2) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(dlam / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function calculateBearing(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const dlam = ((lng2 - lng1) * Math.PI) / 180;

  const y = Math.sin(dlam) * Math.cos(phi2);
  const x = Math.cos(phi1) * Math.sin(phi2) - Math.sin(phi1) * Math.cos(phi2) * Math.cos(dlam);
  const brng = (Math.atan2(y, x) * 180) / Math.PI;
  return (brng + 360) % 360;
}

export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }
  return `${(meters / 1000).toFixed(1)} km`;
}

export function formatDuration(seconds: number): string {
  const mins = Math.round(seconds / 60);
  if (mins < 1) return '< 1 min';
  if (mins < 60) {
    return `${mins} min`;
  }
  const hours = Math.floor(mins / 60);
  const remMins = mins % 60;
  return `${hours} hr ${remMins} min`;
}

export function formatSpeed(mps: number | null): string {
  if (mps === null || mps < 0.5) return '0 km/h';
  const kmh = Math.round(mps * 3.6);
  return `${kmh} km/h`;
}

export function calculateETA(remainingMeters: number, currentSpeedMps: number | null): string {
  const defaultSpeedKmh = 25; // Urban 2W average
  const speedKmh = currentSpeedMps && currentSpeedMps > 1.5 ? currentSpeedMps * 3.6 : defaultSpeedKmh;
  const hours = (remainingMeters / 1000) / speedKmh;
  const seconds = Math.max(30, hours * 3600);
  
  const etaDate = new Date(Date.now() + seconds * 1000);
  return etaDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Strips out 'Unnamed', technical tags, and road names, returning clean, pure user instructions (e.g. "Turn left", "Turn right").
 */
export function cleanManeuverText(maneuver: TurnManeuver | null): string {
  if (!maneuver) return '';

  switch (maneuver.type) {
    case 'turn_left':
      return 'Turn left';
    case 'slight_left':
      return 'Bear left';
    case 'turn_right':
      return 'Turn right';
    case 'slight_right':
      return 'Bear right';
    case 'u_turn':
      return 'Make a U-turn';
    case 'arrive':
      return 'Arrive at destination';
    case 'depart':
      return 'Head straight on route';
    case 'straight':
    default:
      return 'Continue straight';
  }
}

/**
 * Calculates point-to-line-segment perpendicular or vertex distance in meters.
 */
export function pointToSegmentDistanceMeters(
  px: number, py: number,
  x1: number, y1: number,
  x2: number, y2: number
): number {
  const dx = x2 - x1;
  const dy = y2 - y1;
  if (dx === 0 && dy === 0) {
    return haversineMeters(px, py, x1, y1);
  }

  const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)));
  const projLat = x1 + t * dx;
  const projLng = y1 + t * dy;

  return haversineMeters(px, py, projLat, projLng);
}

/**
 * Optimized O(1) amortized polyline distance check with spatial windowing.
 */
export function findDistanceToPolyline(
  lat: number,
  lng: number,
  polyline: LatLng[],
  lastKnownIndex: number = 0,
  windowSize: number = 25
): { distanceMeters: number; nearestSegmentIndex: number } {
  if (!polyline || polyline.length === 0) {
    return { distanceMeters: Infinity, nearestSegmentIndex: -1 };
  }

  if (polyline.length === 1) {
    return {
      distanceMeters: haversineMeters(lat, lng, polyline[0][0], polyline[0][1]),
      nearestSegmentIndex: 0,
    };
  }

  const startIndex = Math.max(0, lastKnownIndex - 5);
  const endIndex = Math.min(polyline.length - 1, lastKnownIndex + windowSize);

  let minDistance = Infinity;
  let nearestIdx = lastKnownIndex;

  for (let i = startIndex; i < endIndex; i++) {
    const p1 = polyline[i];
    const p2 = polyline[i + 1];
    const dist = pointToSegmentDistanceMeters(lat, lng, p1[0], p1[1], p2[0], p2[1]);
    if (dist < minDistance) {
      minDistance = dist;
      nearestIdx = i;
    }
  }

  if (minDistance < 60) {
    return { distanceMeters: minDistance, nearestSegmentIndex: nearestIdx };
  }

  minDistance = Infinity;
  nearestIdx = 0;
  for (let i = 0; i < polyline.length - 1; i++) {
    const p1 = polyline[i];
    const p2 = polyline[i + 1];
    const dist = pointToSegmentDistanceMeters(lat, lng, p1[0], p1[1], p2[0], p2[1]);
    if (dist < minDistance) {
      minDistance = dist;
      nearestIdx = i;
    }
  }

  return { distanceMeters: minDistance, nearestSegmentIndex: nearestIdx };
}

/**
 * Calculates remaining route distance in meters from the current segment index to destination.
 */
export function calculateRemainingRouteDistance(
  currentLat: number,
  currentLng: number,
  polyline: LatLng[],
  currentSegmentIndex: number
): number {
  if (!polyline || polyline.length === 0) return 0;
  if (currentSegmentIndex >= polyline.length - 1) {
    return haversineMeters(currentLat, currentLng, polyline[polyline.length - 1][0], polyline[polyline.length - 1][1]);
  }

  let total = haversineMeters(currentLat, currentLng, polyline[currentSegmentIndex + 1][0], polyline[currentSegmentIndex + 1][1]);

  for (let i = currentSegmentIndex + 1; i < polyline.length - 1; i++) {
    total += haversineMeters(polyline[i][0], polyline[i][1], polyline[i + 1][0], polyline[i + 1][1]);
  }

  return total;
}
