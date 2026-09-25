'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { RouteResponse, GPSPosition, TurnManeuver } from '@/lib/types';
import {
  haversineMeters,
  findDistanceToPolyline,
  calculateRemainingRouteDistance,
  cleanManeuverText,
} from '@/lib/geo';
import { voiceGuidance } from '@/lib/speech';

export interface RerouteEventInfo {
  lat: number;
  lng: number;
  distanceOffRouteM: number;
}

interface UseNavigationEngineProps {
  routeData: RouteResponse | null;
  gpsPosition: GPSPosition | null;
  voiceEnabled: boolean;
  isRerouting?: boolean; // passed from page.tsx — suppresses double-reroute while request is in flight
  onRerouteNeeded?: (info?: RerouteEventInfo) => void;
  onArrival?: () => void;
}

export function useNavigationEngine({
  routeData,
  gpsPosition,
  voiceEnabled,
  isRerouting = false,
  onRerouteNeeded,
  onArrival,
}: UseNavigationEngineProps) {
  const [isNavigating, setIsNavigating] = useState(false);
  const [currentManeuverIndex, setCurrentManeuverIndex] = useState(0);
  const [nearestSegmentIndex, setNearestSegmentIndex] = useState(0);
  const [distanceToManeuverMeters, setDistanceToManeuverMeters] = useState(0);
  const [remainingMeters, setRemainingMeters] = useState(0);
  const [isOffRoute, setIsOffRoute] = useState(false);
  const [hasArrived, setHasArrived] = useState(false);

  const offRouteSinceRef = useRef<number | null>(null);
  const lastRerouteTimeRef = useRef<number>(0);
  const navigationStartTimeRef = useRef<number>(0);

  // Sync voice preference
  useEffect(() => {
    voiceGuidance.setEnabled(voiceEnabled);
  }, [voiceEnabled]);

  // Reset state when route changes
  useEffect(() => {
    setCurrentManeuverIndex(0);
    setNearestSegmentIndex(0);
    setIsOffRoute(false);
    setHasArrived(false);
    offRouteSinceRef.current = null;
    voiceGuidance.resetMilestones();
  }, [routeData]);

  // Navigation Logic Loop
  useEffect(() => {
    if (!isNavigating || !routeData?.path || routeData.path.length < 2 || !gpsPosition) {
      return;
    }

    const { lat, lng } = gpsPosition;
    const polyline = routeData.path;
    const maneuvers = routeData.maneuvers || [];

    // 1. Check Arrival at destination
    const destPoint = polyline[polyline.length - 1];
    const distToDest = haversineMeters(lat, lng, destPoint[0], destPoint[1]);

    if (distToDest < 35 && !hasArrived) {
      setHasArrived(true);
      setIsNavigating(false);
      if (onArrival) onArrival();
      return;
    }

    // 2. O(1) distance check to polyline
    const { distanceMeters: distToRoute, nearestSegmentIndex: segIdx } = findDistanceToPolyline(
      lat,
      lng,
      polyline,
      nearestSegmentIndex
    );
    setNearestSegmentIndex(segIdx);

    // 3. Calculate remaining route distance
    const remDist = calculateRemainingRouteDistance(lat, lng, polyline, segIdx);
    setRemainingMeters(remDist);

    // 4. Off-Route Detection
    // 80m threshold: GPS accuracy is ±10-30m in urban Bangalore, so 80m is a safe margin.
    // Requires 8 consecutive seconds off-route before triggering (avoids false positives at intersections).
    const now = Date.now();
    if (distToRoute > 80) {
      if (!offRouteSinceRef.current) {
        offRouteSinceRef.current = now;
      } else if (now - offRouteSinceRef.current > 8000) {
        // Don't fire if a reroute is already in flight or cooldown hasn't elapsed
        if (!isOffRoute && !isRerouting && now - lastRerouteTimeRef.current > 20000) {
          setIsOffRoute(true);
          lastRerouteTimeRef.current = now;
          if (onRerouteNeeded) {
            onRerouteNeeded({
              lat,
              lng,
              distanceOffRouteM: distToRoute,
            });
          }
        }
      }
    } else {
      offRouteSinceRef.current = null;
      if (isOffRoute) setIsOffRoute(false);
    }

    // 5. Turn-by-Turn Maneuver Progress & Direction Voice Prompts ONLY
    if (maneuvers.length > 0 && currentManeuverIndex < maneuvers.length) {
      const curM = maneuvers[currentManeuverIndex];
      const distToTurn = haversineMeters(lat, lng, curM.lat, curM.lng);
      setDistanceToManeuverMeters(distToTurn);

      // Only speaks if user enabled voice
      if (voiceEnabled) {
        const cleanInstruction = cleanManeuverText(curM);
        voiceGuidance.speakManeuver(cleanInstruction, distToTurn, currentManeuverIndex);
      }

      // Advance to next maneuver when passed (< 28m)
      if (distToTurn < 28 && currentManeuverIndex < maneuvers.length - 1) {
        setCurrentManeuverIndex((prev) => prev + 1);
      }
    }
  }, [
    isNavigating,
    routeData,
    gpsPosition,
    nearestSegmentIndex,
    currentManeuverIndex,
    isOffRoute,
    hasArrived,
    voiceEnabled,
    onRerouteNeeded,
    onArrival,
  ]);

  const startNavigation = useCallback(() => {
    setIsNavigating(true);
    setHasArrived(false);
    setIsOffRoute(false);
    setCurrentManeuverIndex(0);
    navigationStartTimeRef.current = Date.now();
    voiceGuidance.resetMilestones();
  }, []);

  const stopNavigation = useCallback(() => {
    setIsNavigating(false);
    // Reset traveled index so the grayed polyline disappears immediately
    setNearestSegmentIndex(0);
    setCurrentManeuverIndex(0);
    setRemainingMeters(0);
    setDistanceToManeuverMeters(0);
    offRouteSinceRef.current = null;
  }, []);

  const currentManeuver: TurnManeuver | null =
    routeData?.maneuvers?.[currentManeuverIndex] || null;
  const nextManeuver: TurnManeuver | null =
    routeData?.maneuvers?.[currentManeuverIndex + 1] || null;

  return {
    isNavigating,
    currentManeuverIndex,
    nearestSegmentIndex,
    distanceToManeuverMeters,
    remainingMeters,
    isOffRoute,
    hasArrived,
    currentManeuver,
    nextManeuver,
    startNavigation,
    stopNavigation,
  };
}
