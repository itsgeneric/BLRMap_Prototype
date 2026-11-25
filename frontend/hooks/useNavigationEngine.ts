'use client';

/**
 * Turn-by-turn navigation engine.
 *
 * - Progress is distance ALONG the route: the GPS fix is projected onto the route
 *   polyline, and the next instruction is the first one ahead of that point. A turn
 *   point that is never passed within some radius can't freeze guidance.
 * - The rider arrow is snapped onto the road and points along it while on route.
 * - Voice prompts follow navigation-app conventions: an early "In 300 metres, turn
 *   left onto X" (earlier at higher speed), the instruction itself just before the
 *   turn (chained with "then …" when the next turn follows closely), and
 *   "Continue on X for 3 kilometres" after a turn that starts a long stretch.
 * - Off-route for a few seconds (accuracy-aware) asks the app to reroute from the
 *   current position and heading.
 * - Remaining time scales the route's own duration estimate by the distance left,
 *   so the ETA doesn't jump with every change in speed.
 */
import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { RouteResponse, GPSPosition, TurnManeuver, NavPose, NavStatus } from '@/lib/types';
import {
  RouteIndex,
  buildRouteIndex,
  projectOnRoute,
  maneuverAlongs,
  haversine,
  voicePreparePrompt,
  shortInstruction,
  spokenDistance,
} from '@/lib/navigation';
import { voiceGuidance } from '@/lib/speech';

export interface RerouteEventInfo {
  lat: number;
  lng: number;
  heading: number | null;
  distanceOffRouteM: number;
}

interface UseNavigationEngineProps {
  routeData: RouteResponse | null;
  gpsPosition: GPSPosition | null;
  voiceEnabled: boolean;
  destinationName?: string;
  onRerouteNeeded?: (info: RerouteEventInfo) => void;
  onArrival?: () => void;
}

const OFF_ROUTE_BASE_M = 30;        // + GPS accuracy (capped)
const OFF_ROUTE_SECONDS = 4;
const REROUTE_COOLDOWN_MS = 10000;
const REROUTE_GIVE_UP_MS = 15000;   // if no new route arrives, resume and allow another try
const ARRIVE_WITHIN_M = 20;
const DEFAULT_SPEED_MPS = 25 / 3.6; // fallback when the route has no duration

export function useNavigationEngine({
  routeData,
  gpsPosition,
  voiceEnabled,
  destinationName,
  onRerouteNeeded,
  onArrival,
}: UseNavigationEngineProps) {
  const [status, setStatus] = useState<NavStatus>('idle');
  const [pose, setPose] = useState<NavPose | null>(null);
  const [maneuverIndex, setManeuverIndex] = useState(1);
  const [distanceToManeuverMeters, setDistanceToManeuver] = useState(0);
  const [remainingMeters, setRemainingMeters] = useState(0);

  const statusRef = useRef<NavStatus>('idle');
  const alongRef = useRef<number | null>(null);
  const bearingRef = useRef(0);
  const offRouteSinceRef = useRef<number | null>(null);
  const lastRerouteRef = useRef(0);
  const reroutingSinceRef = useRef(0);
  const spokenRef = useRef<Set<string>>(new Set());
  const lastIndexRef = useRef(1);

  // Latest callbacks without re-running effects
  const onRerouteRef = useRef(onRerouteNeeded);
  const onArrivalRef = useRef(onArrival);
  onRerouteRef.current = onRerouteNeeded;
  onArrivalRef.current = onArrival;

  const setNavStatus = (s: NavStatus) => {
    statusRef.current = s;
    setStatus(s);
  };

  useEffect(() => {
    voiceGuidance.setEnabled(voiceEnabled);
  }, [voiceEnabled]);

  // ── Route geometry, maneuver positions and total duration ─────────────────
  const route = useMemo(() => {
    const path = routeData?.path;
    if (!path || path.length < 2) return null;
    const idx: RouteIndex = buildRouteIndex(path);
    const maneuvers: TurnManeuver[] = routeData?.maneuvers || [];
    const alongs = maneuverAlongs(idx, maneuvers);
    const durationSec =
      routeData?.duration_mins != null ? routeData.duration_mins * 60 : idx.total / DEFAULT_SPEED_MPS;
    const key = `${path[0]}|${path[path.length - 1]}|${path.length}|${Date.now()}`;
    return { idx, maneuvers, alongs, durationSec, key };
  }, [routeData]);

  // ── A new route arrived (first load or reroute) ───────────────────────────
  useEffect(() => {
    alongRef.current = null;
    offRouteSinceRef.current = null;
    lastIndexRef.current = 1;
    setManeuverIndex(1);
    spokenRef.current = new Set();
    if (statusRef.current === 'rerouting') {
      setNavStatus('navigating');
    }
    if (route) setRemainingMeters(route.idx.total);
  }, [route]);

  const say = useCallback((key: string, text: string) => {
    if (spokenRef.current.has(key)) return;
    spokenRef.current.add(key);
    voiceGuidance.speak(text);
  }, []);

  // ── Main loop: one pass per GPS fix ───────────────────────────────────────
  useEffect(() => {
    const st = statusRef.current;
    if ((st !== 'navigating' && st !== 'rerouting') || !route || !gpsPosition) return;

    const { idx, maneuvers, alongs, durationSec } = route;
    const now = Date.now();
    const speed = gpsPosition.speed ?? 0;
    const accuracy = gpsPosition.accuracy ?? 10;

    const proj = projectOnRoute(idx, gpsPosition.lat, gpsPosition.lng, alongRef.current);
    const threshold = OFF_ROUTE_BASE_M + Math.min(accuracy, 40);
    const onRoute = !!proj && proj.distance <= threshold;

    let along = alongRef.current ?? 0;
    let lat = gpsPosition.lat;
    let lng = gpsPosition.lng;
    let bearing = bearingRef.current;

    if (onRoute && proj) {
      along = proj.along;
      lat = proj.lat;
      lng = proj.lng;
      bearing = proj.bearing;
      alongRef.current = along;
      offRouteSinceRef.current = null;
      if (st === 'rerouting') setNavStatus('navigating'); // came back onto the route
    } else {
      if (gpsPosition.heading != null && speed > 1) bearing = gpsPosition.heading;
      // Off route: ask for a new route after a few seconds
      if (offRouteSinceRef.current === null) offRouteSinceRef.current = now;
      const longEnough = now - offRouteSinceRef.current > OFF_ROUTE_SECONDS * 1000;
      if (longEnough && st === 'navigating' && now - lastRerouteRef.current > REROUTE_COOLDOWN_MS) {
        lastRerouteRef.current = now;
        reroutingSinceRef.current = now;
        setNavStatus('rerouting');
        onRerouteRef.current?.({
          lat: gpsPosition.lat,
          lng: gpsPosition.lng,
          heading: speed > 1 ? gpsPosition.heading ?? bearing : null,
          distanceOffRouteM: proj ? proj.distance : 0,
        });
      }
      if (st === 'rerouting' && now - reroutingSinceRef.current > REROUTE_GIVE_UP_MS) {
        setNavStatus('navigating');
      }
    }
    bearingRef.current = bearing;

    const remaining = Math.max(0, idx.total - along);
    setPose({ lat, lng, bearing, along, speedMps: speed, onRoute, timestamp: now });
    setRemainingMeters(remaining);

    // ── Arrival ──
    const end = idx.path[idx.path.length - 1];
    const distToEnd = haversine(gpsPosition.lat, gpsPosition.lng, end[0], end[1]);
    if ((onRoute && remaining < ARRIVE_WITHIN_M) || distToEnd < ARRIVE_WITHIN_M) {
      const arrive = maneuvers[maneuvers.length - 1];
      const side = arrive?.side ? ` Your destination is on the ${arrive.side}.` : '';
      // A map-tapped destination is named by its coordinates: don't read those out
      const named = destinationName && !/^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?$/.test(destinationName.trim());
      const where = named ? `You have arrived at ${destinationName}.` : 'You have arrived.';
      say('arrived', where + side);
      setNavStatus('arrived');
      onArrivalRef.current?.();
      return;
    }

    // ── Which instruction is next ──
    let i = 1;
    while (i < alongs.length - 1 && alongs[i] <= along + 3) i++;
    if (i >= maneuvers.length) i = maneuvers.length - 1;
    setManeuverIndex(i);
    const m = maneuvers[i];
    if (!m) return;
    const d = Math.max(0, alongs[i] - along);
    setDistanceToManeuver(d);

    if (!onRoute) return;

    // ── Voice ──
    const farDist = speed > 16 ? 1000 : speed > 9 ? 500 : 300;
    const nearDist = Math.max(35, speed * 4);
    const legLength = alongs[i] - alongs[i - 1];
    const tag = `${route.key}:${i}`;

    // Passed a turn into a long stretch: "Continue on X for 3 kilometres"
    if (i !== lastIndexRef.current) {
      lastIndexRef.current = i;
      const road = maneuvers[i - 1]?.road_name;
      if (d > 2000) {
        say(`${tag}:cont`, road ? `Continue on ${road} for ${spokenDistance(d)}` : `Continue for ${spokenDistance(d)}`);
      }
    }

    if (m.type === 'arrive') {
      if (d <= farDist && d > 80) say(`${tag}:far`, voicePreparePrompt(m, d));
      return;
    }

    if (d <= farDist && d > nearDist + 60 && legLength > farDist * 0.6) {
      say(`${tag}:far`, voicePreparePrompt(m, d));
    }
    if (d <= nearDist) {
      let text = m.instruction;
      const next = maneuvers[i + 1];
      if (next && next.type !== 'arrive' && alongs[i + 1] - alongs[i] < 120) {
        text += `, then ${shortInstruction(next)}`;
        spokenRef.current.add(`${route.key}:${i + 1}:far`);
      }
      say(`${tag}:near`, text);
    }
  }, [gpsPosition, route, destinationName, say]);

  // ── Controls ──────────────────────────────────────────────────────────────
  const startNavigation = useCallback(() => {
    alongRef.current = null;
    offRouteSinceRef.current = null;
    lastRerouteRef.current = 0;
    lastIndexRef.current = 1;
    spokenRef.current = new Set();
    setManeuverIndex(1);
    setNavStatus('navigating');
    const depart = route?.maneuvers[0];
    if (depart && route) {
      spokenRef.current.add('depart');
      // If the first turn comes almost immediately, say both together (one prompt
      // would otherwise cut off the other): "Head west on X, then turn right onto Y".
      const first = route.maneuvers[1];
      const firstAt = route.alongs[1] ?? Infinity;
      if (first && first.type !== 'arrive' && firstAt < 150) {
        voiceGuidance.speak(`${depart.instruction}, then ${first.instruction.charAt(0).toLowerCase()}${first.instruction.slice(1)}`);
        spokenRef.current.add(`${route.key}:1:far`);
        spokenRef.current.add(`${route.key}:1:near`);
      } else {
        voiceGuidance.speak(depart.instruction);
      }
    }
  }, [route]);

  const stopNavigation = useCallback(() => {
    voiceGuidance.stop();
    setNavStatus('idle');
    setPose(null);
  }, []);

  // ── Derived values for the UI ─────────────────────────────────────────────
  const maneuvers = route?.maneuvers || [];
  const currentManeuver: TurnManeuver | null = maneuvers[maneuverIndex] || null;
  const nextManeuver: TurnManeuver | null = maneuvers[maneuverIndex + 1] || null;
  const distanceBetweenManeuvers =
    route && nextManeuver ? route.alongs[maneuverIndex + 1] - route.alongs[maneuverIndex] : Infinity;
  const currentManeuverAlong = route ? route.alongs[maneuverIndex] ?? null : null;
  const total = route?.idx.total || 0;
  const remainingSeconds = route && total > 0 ? route.durationSec * (remainingMeters / total) : 0;

  return {
    status,
    isNavigating: status === 'navigating' || status === 'rerouting',
    pose,
    routeIndex: route?.idx || null,
    currentManeuver,
    nextManeuver,
    currentManeuverAlong,
    distanceToManeuverMeters,
    distanceBetweenManeuvers,
    remainingMeters,
    remainingSeconds,
    startNavigation,
    stopNavigation,
  };
}
