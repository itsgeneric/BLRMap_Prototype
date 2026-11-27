'use client';

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { RouteResponse, GPSPosition, TurnManeuver } from '@/lib/types';
import { haversineMeters } from '@/lib/geo';
import { GpsFilter, RouteMatcher, projectOnRoute } from '@/lib/mapMatching';
import { mapManeuvers, upcoming, ManeuverAlong } from '@/lib/navProgress';
import { VoicePlanner } from '@/lib/voicePlan';
import { deriveManeuvers } from '@/lib/deriveManeuvers';
import { voiceGuidance } from '@/lib/speech';

export interface RerouteEventInfo {
  lat: number;
  lng: number;
  distanceOffRouteM: number;
}

/** idle -> following -> approaching (a turn is close) -> off_route -> rerouting -> arrived */
export type NavState = 'idle' | 'following' | 'approaching' | 'off_route' | 'rerouting' | 'arrived';

/** Everything the UI needs, produced once per GPS fix. */
export interface NavProgress {
  displayLat: number; // where to draw the rider marker (on the road while genuinely on the route)
  displayLng: number;
  routeLat: number; // the closest point on the route (the route line is split here)
  routeLng: number;
  segmentIndex: number;
  alongM: number;
  remainingM: number;
  offRouteM: number; // measured from the UNSNAPPED filtered position
  snapped: boolean;
  maneuver: TurnManeuver | null; // the next turn ahead
  nextManeuver: TurnManeuver | null; // the one after it
  distanceToManeuverM: number; // along the route
  currentRoadName: string | null;
}

interface UseNavigationEngineProps {
  routeData: RouteResponse | null;
  gpsPosition: GPSPosition | null;
  voiceEnabled: boolean;
  isRerouting?: boolean;
  onRerouteNeeded?: (info?: RerouteEventInfo) => void;
  onArrival?: (info: { travelledMeters: number }) => void;
}

const OFF_ROUTE_PERSIST_MS = 2000;
const REROUTE_COOLDOWN_MS = 6000;
const REROUTE_RETRY_MS = 15000; // still off route this long after asking: the request failed, ask again
const APPROACHING_M = 200;

export function useNavigationEngine({
  routeData,
  gpsPosition,
  voiceEnabled,
  isRerouting = false,
  onRerouteNeeded,
  onArrival,
}: UseNavigationEngineProps) {
  const [isNavigating, setIsNavigating] = useState(false);
  const [progress, setProgress] = useState<NavProgress | null>(null);
  const [isOffRoute, setIsOffRoute] = useState(false);
  const [hasArrived, setHasArrived] = useState(false);

  const filterRef = useRef(new GpsFilter());
  const matcherRef = useRef<RouteMatcher | null>(null);
  const maneuversRef = useRef<ManeuverAlong[]>([]);
  const maneuverIdxRef = useRef(0);
  const plannerRef = useRef(new VoicePlanner());
  const routeIdRef = useRef(0);
  const offRouteSinceRef = useRef<number | null>(null);
  const lastRerouteRef = useRef(0);
  const prevAlongRef = useRef<number | null>(null);
  const travelledRef = useRef(0);
  const arrivedRef = useRef(false);
  const offRouteRef = useRef(false);

  // Latest callbacks/flags, read inside the per-fix effect without re-running it.
  const live = useRef({ onRerouteNeeded, onArrival, isRerouting, voiceEnabled });
  live.current = { onRerouteNeeded, onArrival, isRerouting, voiceEnabled };

  useEffect(() => {
    voiceGuidance.setEnabled(voiceEnabled);
  }, [voiceEnabled]);

  // A new route (first route, or after a reroute): rebuild the matcher and place the maneuvers along it.
  useEffect(() => {
    const path = routeData?.path;
    if (path && path.length >= 2) {
      const matcher = new RouteMatcher(path);
      matcherRef.current = matcher;
      // Prefer the server's maneuvers (they know junctions and street names). If it sent none (an older backend), derive the
      // turns from the route's shape so the banner and the voice still work.
      const serverManeuvers = routeData?.maneuvers ?? [];
      const maneuvers = serverManeuvers.length > 1 ? serverManeuvers : deriveManeuvers(path);
      maneuversRef.current = mapManeuvers(maneuvers, (lat, lng) => projectOnRoute(matcher.route, lat, lng).alongM);
    } else {
      matcherRef.current = null;
      maneuversRef.current = [];
    }
    routeIdRef.current += 1;
    maneuverIdxRef.current = 0;
    plannerRef.current.reset();
    offRouteSinceRef.current = null;
    prevAlongRef.current = null;
    arrivedRef.current = false;
    offRouteRef.current = false;
    setProgress(null);
    setIsOffRoute(false);
    setHasArrived(false);
  }, [routeData]);

  // One pass per GPS fix: filter -> match -> off-route / arrival / next maneuver / voice.
  useEffect(() => {
    const matcher = matcherRef.current;
    const path = routeData?.path;
    if (!isNavigating || !matcher || !path || path.length < 2 || !gpsPosition || arrivedRef.current) return;
    const cb = live.current;

    const speed = gpsPosition.speed ?? 0;
    const f = filterRef.current.update({
      lat: gpsPosition.lat,
      lng: gpsPosition.lng,
      accuracy: gpsPosition.accuracy,
      speed,
      timestamp: gpsPosition.timestamp,
    });
    const heading = speed > 1.5 ? gpsPosition.heading : null;
    const m = matcher.match(f.lat, f.lng, heading, speed, f.accuracy);
    const total = matcher.route.total;
    const remaining = Math.max(0, total - m.alongM);

    // distance actually travelled (for the trip summary), counted along the route so GPS jitter adds nothing
    if (prevAlongRef.current !== null) {
      const delta = m.alongM - prevAlongRef.current;
      if (delta > 0 && delta < 300) travelledRef.current += delta;
    }
    prevAlongRef.current = Math.max(prevAlongRef.current ?? 0, m.alongM);

    // ── arrival
    const dest = path[path.length - 1];
    const distToDest = haversineMeters(f.lat, f.lng, dest[0], dest[1]);
    if (distToDest < Math.max(30, f.accuracy) || (m.snapped && remaining < 20)) {
      arrivedRef.current = true;
      setHasArrived(true);
      setIsNavigating(false);
      setIsOffRoute(false);
      cb.onArrival?.({ travelledMeters: travelledRef.current });
      return;
    }

    // ── off-route: judged on the UNSNAPPED filtered position, with a threshold that grows with GPS inaccuracy
    const now = Date.now();
    const threshold = Math.max(30, 2 * f.accuracy);
    if (m.distanceM > threshold) {
      if (offRouteSinceRef.current === null) {
        offRouteSinceRef.current = now;
      } else if (
        now - offRouteSinceRef.current > OFF_ROUTE_PERSIST_MS &&
        (!offRouteRef.current || now - lastRerouteRef.current > REROUTE_RETRY_MS) &&
        !cb.isRerouting &&
        now - lastRerouteRef.current > REROUTE_COOLDOWN_MS
      ) {
        offRouteRef.current = true;
        lastRerouteRef.current = now;
        setIsOffRoute(true);
        if (typeof navigator !== 'undefined' && 'vibrate' in navigator) navigator.vibrate([40, 60, 40]);
        if (cb.voiceEnabled) voiceGuidance.speak('Rerouting', true);
        cb.onRerouteNeeded?.({ lat: f.lat, lng: f.lng, distanceOffRouteM: m.distanceM });
      }
    } else {
      offRouteSinceRef.current = null;
      if (offRouteRef.current) {
        offRouteRef.current = false;
        setIsOffRoute(false);
      }
    }

    // ── next maneuver, measured along the route
    const up = upcoming(maneuversRef.current, m.alongM, maneuverIdxRef.current);
    maneuverIdxRef.current = up.index;

    // ── voice: quiet while off route / rerouting (the new route will start its own announcements)
    if (cb.voiceEnabled && up.maneuver && !offRouteRef.current && !cb.isRerouting) {
      const cue = plannerRef.current.evaluate(
        `${routeIdRef.current}:${up.index}`,
        up.maneuver.type,
        up.maneuver.road_name,
        up.distanceM,
        speed
      );
      if (cue) voiceGuidance.speak(cue.text, cue.urgent);
    }

    setProgress({
      displayLat: m.displayLat,
      displayLng: m.displayLng,
      routeLat: m.projLat,
      routeLng: m.projLng,
      segmentIndex: m.segmentIndex,
      alongM: m.alongM,
      remainingM: remaining,
      offRouteM: m.distanceM,
      snapped: m.snapped,
      maneuver: up.maneuver,
      nextManeuver: up.next,
      distanceToManeuverM: up.distanceM,
      currentRoadName: up.currentRoadName,
    });
  }, [gpsPosition, isNavigating, routeData]);

  const startNavigation = useCallback(() => {
    filterRef.current = new GpsFilter();
    plannerRef.current.reset();
    maneuverIdxRef.current = 0;
    offRouteSinceRef.current = null;
    prevAlongRef.current = null;
    travelledRef.current = 0;
    arrivedRef.current = false;
    offRouteRef.current = false;
    lastRerouteRef.current = 0;
    setProgress(null);
    setHasArrived(false);
    setIsOffRoute(false);
    setIsNavigating(true);
  }, []);

  const stopNavigation = useCallback(() => {
    voiceGuidance.stop();
    setIsNavigating(false);
    setProgress(null);
    setIsOffRoute(false);
    offRouteSinceRef.current = null;
    offRouteRef.current = false;
  }, []);

  const navState: NavState = useMemo(() => {
    if (hasArrived) return 'arrived';
    if (!isNavigating) return 'idle';
    if (isRerouting) return 'rerouting';
    if (isOffRoute) return 'off_route';
    if (progress && progress.distanceToManeuverM <= APPROACHING_M) return 'approaching';
    return 'following';
  }, [hasArrived, isNavigating, isRerouting, isOffRoute, progress]);

  return {
    isNavigating,
    navState,
    progress,
    nearestSegmentIndex: progress?.segmentIndex ?? 0,
    distanceToManeuverMeters: progress?.distanceToManeuverM ?? 0,
    remainingMeters: progress?.remainingM ?? 0,
    isOffRoute,
    hasArrived,
    currentManeuver: progress?.maneuver ?? null,
    nextManeuver: progress?.nextManeuver ?? null,
    currentRoadName: progress?.currentRoadName ?? null,
    startNavigation,
    stopNavigation,
  };
}
