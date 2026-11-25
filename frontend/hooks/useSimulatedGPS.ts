'use client';

/**
 * Drive-simulation GPS for testing navigation on a desktop.
 *
 * Enable with the URL parameter ?simulate=1 (or ?simulate=<km/h>, default 30).
 * While navigating, it emits a GPS fix once per second that rides along the
 * current route at roughly that speed, slowing down for turns and adding a few
 * metres of GPS noise, so the camera, progress, voice prompts and arrival logic
 * can be exercised without leaving the desk. It never runs unless the URL asks.
 *
 * Add &detour=<seconds> to leave the route at that time and ride off-route for
 * 15 s, to exercise rerouting.
 */
import { useEffect, useRef, useState } from 'react';
import { GPSPosition, LatLng, TurnManeuver } from '@/lib/types';
import { buildRouteIndex, destinationPoint, maneuverAlongs, pointAlong } from '@/lib/navigation';

export function getSimulationSpeedKmh(): number | null {
  if (typeof window === 'undefined') return null;
  const v = new URLSearchParams(window.location.search).get('simulate');
  if (v === null) return null;
  const n = Number(v);
  return Number.isFinite(n) && n > 1 ? n : 30;
}

function getDetourSeconds(): number | null {
  if (typeof window === 'undefined') return null;
  const v = Number(new URLSearchParams(window.location.search).get('detour'));
  return Number.isFinite(v) && v > 0 ? v : null;
}

export function useSimulatedGPS(
  path: LatLng[] | null | undefined,
  maneuvers: TurnManeuver[] | undefined,
  active: boolean,
  speedKmh: number | null
): GPSPosition | null {
  const [pos, setPos] = useState<GPSPosition | null>(null);
  const alongRef = useRef(0);
  const pathKeyRef = useRef('');
  const startedAtRef = useRef<number | null>(null);
  const detourRef = useRef<{ lat: number; lng: number; bearing: number } | null>(null);

  useEffect(() => {
    if (!active || !speedKmh || !path || path.length < 2) return;
    const idx = buildRouteIndex(path);
    const turns = maneuverAlongs(idx, maneuvers || []).slice(1, -1);

    // A new route (e.g. after a reroute) starts near its beginning.
    const key = `${path[0]}|${path[path.length - 1]}|${path.length}`;
    if (key !== pathKeyRef.current) {
      pathKeyRef.current = key;
      alongRef.current = 0;
    }

    const cruise = speedKmh / 3.6;
    const detourAt = getDetourSeconds();
    if (startedAtRef.current === null) startedAtRef.current = Date.now();

    const tick = () => {
      const elapsed = (Date.now() - (startedAtRef.current ?? Date.now())) / 1000;
      if (detourAt !== null && elapsed >= detourAt && elapsed < detourAt + 15) {
        // Ride straight off at 70° to the route for 15 s
        if (!detourRef.current) {
          const p = pointAlong(idx, alongRef.current);
          detourRef.current = { lat: p.lat, lng: p.lng, bearing: (p.bearing + 70) % 360 };
        }
        const d = detourRef.current;
        const next = destinationPoint(d.lat, d.lng, d.bearing, cruise);
        detourRef.current = { ...d, lat: next.lat, lng: next.lng };
        setPos({ lat: next.lat, lng: next.lng, heading: d.bearing, speed: cruise, accuracy: 5, timestamp: Date.now() });
        return;
      }
      const a = alongRef.current;
      // Slow down within 60 m of a turn, like a real rider
      const nearTurn = turns.some((t) => t - a > -15 && t - a < 60);
      const speed = nearTurn ? Math.min(cruise, 4.5) : cruise * (0.9 + Math.random() * 0.2);
      alongRef.current = Math.min(idx.total, a + speed);
      const p = pointAlong(idx, alongRef.current);
      const noisy = destinationPoint(p.lat, p.lng, Math.random() * 360, Math.random() * 3);
      setPos({
        lat: noisy.lat,
        lng: noisy.lng,
        heading: p.bearing,
        speed,
        accuracy: 5,
        timestamp: Date.now(),
      });
    };
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [active, speedKmh, path, maneuvers]);

  useEffect(() => {
    if (!active) {
      alongRef.current = 0;
      pathKeyRef.current = '';
      startedAtRef.current = null;
      detourRef.current = null;
    }
  }, [active]);

  return active && speedKmh ? pos : null;
}
