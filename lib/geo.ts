import { LatLng } from './types';

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
  const defaultSpeedKmh = 25; // Default average urban 2W speed
  const speedKmh = currentSpeedMps && currentSpeedMps > 1 ? currentSpeedMps * 3.6 : defaultSpeedKmh;
  const hours = (remainingMeters / 1000) / speedKmh;
  const seconds = hours * 3600;
  
  const etaDate = new Date(Date.now() + seconds * 1000);
  return etaDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function findDistanceToPolyline(lat: number, lng: number, polyline: LatLng[]): { distanceMeters: number; nearestSegmentIndex: number } {
  if (!polyline || polyline.length === 0) return { distanceMeters: Infinity, nearestSegmentIndex: -1 };

  let minDistance = Infinity;
  let nearestIdx = 0;

  for (let i = 0; i < polyline.length; i++) {
    const dist = haversineMeters(lat, lng, polyline[i][0], polyline[i][1]);
    if (dist < minDistance) {
      minDistance = dist;
      nearestIdx = i;
    }
  }

  return { distanceMeters: minDistance, nearestSegmentIndex: nearestIdx };
}
