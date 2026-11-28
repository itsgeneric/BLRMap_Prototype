'use client';

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import dynamic from 'next/dynamic';
import {
  Point,
  RouteMode,
  RouteResponse,
  ThemeMode,
  ToastMessage,
  TripSummary,
  RoadIncident,
} from '@/lib/types';
import { fetchRoute, fetchBothRoutes, fetchActiveIncidents, reverseGeocode } from '@/lib/api';
import { createLatest } from '@/lib/latest';
import { applyPinAction, PinAction } from '@/lib/pinActions';
import { haversineMeters, pathLengthMeters } from '@/lib/geo';
import { useGPS } from '@/hooks/useGPS';
import { useNavigationEngine } from '@/hooks/useNavigationEngine';
import { useTripEta } from '@/hooks/useTripEta';
import { voiceGuidance } from '@/lib/speech';
import { startTrip, completeTrip, reportReroute } from '@/lib/tripTracker';

import { TopSearchBar } from '@/components/Navigation/TopSearchBar';
import { ModeSelector } from '@/components/Navigation/ModeSelector';
import { TurnByTurnBanner } from '@/components/Navigation/TurnByTurnBanner';
import { NavigationFooter } from '@/components/Navigation/NavigationFooter';
import { BottomActionBar } from '@/components/Navigation/BottomActionBar';
import { ToastContainer } from '@/components/UI/Toast';
import { ArrivalModal } from '@/components/Navigation/ArrivalModal';
import { IncidentReportModal } from '@/components/Navigation/IncidentReportModal';
import { PlaceSheet } from '@/components/Navigation/PlaceSheet';
import { Loader2, Bike } from 'lucide-react';

// Dynamic SSR-disabled GoogleMapContainer
const MapContainer = dynamic(
  () => import('@/components/Map/GoogleMapContainer').then((mod) => mod.GoogleMapContainer),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full bg-slate-950 flex flex-col items-center justify-center text-sky-400 font-mono text-xs gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
        <span>Loading Bengaluru Google Maps Engine...</span>
      </div>
    ),
  }
);

const ROUTE_DEBOUNCE_MS = 250;

/** Identifies what a route was calculated for, so an old route is never offered for a new choice. */
const tripKey = (from: Point | null, to: Point | null, mode: RouteMode) =>
  from && to ? `${from.lat},${from.lng}|${to.lat},${to.lng}|${mode}` : '';

export default function NavigationApp() {
  const [theme] = useState<ThemeMode>('light');
  const [origin, setOrigin] = useState<Point | null>(null);
  const [destination, setDestination] = useState<Point | null>(null);
  const [activeInput, setActiveInput] = useState<'origin' | 'destination'>('origin');
  const [mode, setMode] = useState<RouteMode>('shortest');
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [shortestRouteData, setShortestRouteData] = useState<RouteResponse | null>(null);
  const [dynamicRouteData, setDynamicRouteData] = useState<RouteResponse | null>(null);
  const [selectedRouteType, setSelectedRouteType] = useState<'shortest' | 'dynamic'>('shortest');
  const [loading, setLoading] = useState(false);
  const [routeFor, setRouteFor] = useState(''); // tripKey() of the route on screen
  const [isRerouting, setIsRerouting] = useState(false);
  const [isFollowingCamera, setIsFollowingCamera] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [tripSummary, setTripSummary] = useState<TripSummary | null>(null);
  const [activeIncidents, setActiveIncidents] = useState<RoadIncident[]>([]);

  const routeAbortControllerRef = useRef<AbortController | null>(null);
  // "Latest request wins": only the newest route request may change the screen (see lib/latest.ts)
  const latestRoute = useRef(createLatest());
  // The place dropped by press-and-hold, waiting for the rider to choose Directions / Start here
  const [droppedPin, setDroppedPin] = useState<Point | null>(null);
  const [pinResolving, setPinResolving] = useState(false);
  // A slow GPS or place-name answer must not overwrite what the rider has done in the meantime
  const latestGpsOrigin = useRef(createLatest());
  const latestPinName = useRef(createLatest());
  const tripStartTimeRef = useRef<number>(0);
  const activeJourneyIdRef = useRef<string | null>(null);
  const reroutedRef = useRef(false); // this trip replaced the planned route (or is trying to)
  const cancelRerouteRef = useRef<(() => void) | null>(null);
  // Stable ref so onRerouteNeeded can call rerouteFromPosition even before it's defined
  const rerouteFromPositionRef = useRef<((lat: number, lng: number) => void) | null>(null);

  // Live crowd-reported incidents fetching & periodic refresh
  const refreshIncidents = useCallback(async () => {
    try {
      const list = await fetchActiveIncidents();
      setActiveIncidents(list);
    } catch (err) {
      console.error('Failed to refresh incidents:', err);
    }
  }, []);

  useEffect(() => {
    refreshIncidents();
    const interval = setInterval(() => {
      if (typeof document === 'undefined' || !document.hidden) refreshIncidents(); // 30s live poll, only while visible
    }, 30000);
    return () => clearInterval(interval);
  }, [refreshIncidents]);

  // Toast Helpers (Reserved only for genuine errors)
  const addToast = useCallback((text: string, type: ToastMessage['type'] = 'error', duration = 4000) => {
    const id = `${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    setToasts((prev) => (prev.some((t) => t.text === text) ? prev : [...prev, { id, text, type, duration }]));
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // hasConfirmedRoute: user has explicitly clicked a route card in compare mode
  // When true, the alternate ghost polyline is hidden from the map.
  const [hasConfirmedRoute, setHasConfirmedRoute] = useState(false);

  // Single Centralized GPS & Compass Hook
  const {
    gpsPosition: realGpsPosition,
    deviceHeading,
    isLocating,
    getCurrentLocation,
    requestCompassPermission,
  } = useGPS();

  // Check if Origin is user's current live location
  const isOriginMyLocation = useMemo(() => {
    if (!origin) return false;
    const name = (origin.name || '').toLowerCase();
    const addr = (origin.address || '').toLowerCase();
    if (
      name.includes('my location') ||
      addr.includes('my location') ||
      name.includes('current location') ||
      addr.includes('current location')
    ) {
      return true;
    }
    // Check if within 80m of current GPS fix
    if (realGpsPosition && realGpsPosition.lat && realGpsPosition.lng) {
      const dist = haversineMeters(origin.lat, origin.lng, realGpsPosition.lat, realGpsPosition.lng);
      if (dist < 80) return true;
    }
    return false;
  }, [origin, realGpsPosition]);

  // Turn-by-Turn Navigation Engine Hook
  const {
    isNavigating,
    navState,
    progress,
    nearestSegmentIndex,
    distanceToManeuverMeters,
    remainingMeters,
    currentManeuver,
    nextManeuver,
    currentRoadName,
    startNavigation,
    stopNavigation,
  } = useNavigationEngine({
    routeData,
    gpsPosition: realGpsPosition,
    voiceEnabled,
    isRerouting,
    onRerouteNeeded: (info) => {
      // Log the off-route event to the backend for analytics
      if (info && activeJourneyIdRef.current) {
        const timeSinceStart = tripStartTimeRef.current > 0
          ? Math.round((Date.now() - tripStartTimeRef.current) / 1000)
          : 0;
        reportReroute(
          activeJourneyIdRef.current,
          info.lat,
          info.lng,
          info.distanceOffRouteM,
          timeSinceStart
        );
      }
      // Reroute FROM the current GPS position, not from the original origin
      if (info && destination) {
        rerouteFromPositionRef.current?.(info.lat, info.lng);
      }
    },
    onArrival: ({ travelledMeters }) => {
      if (reroutedRef.current) cancelRerouteRef.current?.();
      const timeTakenSec = Math.max(1, Math.round((Date.now() - tripStartTimeRef.current) / 1000));
      // distance actually travelled (counted along the route, so rerouting and GPS jitter do not distort it)
      const distKm = travelledMeters > 50 ? travelledMeters / 1000 : routeData?.distance_km || 0;
      if (voiceEnabled) voiceGuidance.speak('You have arrived', true);
      const summary: TripSummary = {
        distanceKm: distKm,
        timeTakenSec,
        avgSpeedKmh: distKm > 0 ? distKm / (timeTakenSec / 3600) : 0,
        originName: origin?.name || 'Start Point',
        destinationName: destination?.name || 'Destination',
      };
      setTripSummary(summary);
      if (activeJourneyIdRef.current) {
        completeTrip(activeJourneyIdRef.current, summary);
      }
    },
  });

  // Remaining time, arrival time and speedometer: one model for all of them (lib/eta.ts).
  // progress is measured along the drawn line, so the total must be that line's length too
  const routeTotalM = useMemo(() => pathLengthMeters(routeData?.path), [routeData?.path]);
  const trip = useTripEta({
    isNavigating,
    totalM: routeTotalM,
    plannedDurationS: routeData?.duration_s ?? null,
    remainingM: remainingMeters || routeTotalM,
    gpsPosition: realGpsPosition,
  });

  // The route starts and ends on the nearest road. When that is far from a pin, say so instead of leaving the rider to
  // wonder why the line stops short.
  const notifySnap = useCallback(
    (res: RouteResponse) => {
      const parts: string[] = [];
      const start = res.origin_snap?.distance_m ?? 0;
      const end = res.destination_snap?.distance_m ?? 0;
      if (start > 75) parts.push(`The route starts ${Math.round(start)} m from your start point`);
      const googleApproach = res.arrival === 'google_approach';
      if (end > 75 && !googleApproach) parts.push(`The route ends ${Math.round(end)} m from your destination`);
      if (parts.length > 0) addToast(`${parts.join('. ')}: no road in our map goes closer.`, 'info', 6000);
      if (googleApproach) {
        addToast(
          `No road goes right to your destination. The route ends where Google Maps approaches it, about ${Math.round(end)} m away.`,
          'info',
          8000
        );
      }
      if (res.road_check === 'failed') {
        addToast('Part of this route uses a road that Google Maps does not have. Check it before you ride.', 'warning', 8000);
      } else if (res.road_check === 'unavailable') {
        addToast('The roads on this route could not be checked with Google.', 'warning', 6000);
      }
    },
    [addToast]
  );

  // Route Fetch Function (for initial + mode change loads).
  // Answers of superseded requests are dropped: they never show an error, never clear the route, never touch the spinner.
  const loadRoute = useCallback(async () => {
    if (routeAbortControllerRef.current) {
      routeAbortControllerRef.current.abort();
    }

    if (!origin || !destination) {
      latestRoute.current.invalidate();
      setLoading(false);
      setRouteData(null);
      setShortestRouteData(null);
      setDynamicRouteData(null);
      return;
    }

    const controller = new AbortController();
    routeAbortControllerRef.current = controller;
    const token = latestRoute.current.begin();
    // Reset confirmation on every new fetch: show both routes again
    setHasConfirmedRoute(false);

    setLoading(true);
    try {
      if (mode === 'fastest') {
        const both = await fetchBothRoutes(origin, destination, controller.signal);
        if (!latestRoute.current.isCurrent(token) || both.aborted) return;
        setShortestRouteData(both.shortest);
        setDynamicRouteData(both.dynamic);

        const chosenType = both.fastestChoice;
        setSelectedRouteType(chosenType);

        const activeRes = both[chosenType] || both.shortest || both.dynamic;
        if (activeRes && activeRes.path && activeRes.path.length > 0) {
          setRouteData(activeRes);
          notifySnap(activeRes);
          setRouteFor(tripKey(origin, destination, mode));
        } else {
          setRouteData(null);
          addToast('Could not calculate fastest route comparison.', 'error');
        }
      } else {
        const res = await fetchRoute(mode, origin, destination, controller.signal);
        if (!latestRoute.current.isCurrent(token) || res.aborted) return;
        if (res.status === 'success' && res.path && res.path.length > 0) {
          setRouteData(res);
          notifySnap(res);
          setRouteFor(tripKey(origin, destination, mode));
          if (mode === 'shortest') {
            setShortestRouteData(res);
            setDynamicRouteData(null);
            setSelectedRouteType('shortest');
          } else {
            setDynamicRouteData(res);
            setShortestRouteData(null);
            setSelectedRouteType('dynamic');
          }
        } else {
          setRouteData(null);
          setShortestRouteData(null);
          setDynamicRouteData(null);
          addToast(res.message || 'No viable route found between these locations.', 'error');
        }
      }
    } catch (err: any) {
      if (!latestRoute.current.isCurrent(token) || err?.name === 'AbortError') return;
      addToast('Failed to calculate route. Check backend connection.', 'error');
    } finally {
      if (latestRoute.current.isCurrent(token)) setLoading(false);
    }
  }, [origin, destination, mode, addToast, notifySnap]);

  /**
   * Reroute from an arbitrary GPS position to the destination.
   * Called ONLY by the navigation engine when the user goes off-route.
   * Uses the current GPS coordinates as the new origin — NOT the original start point.
   */
  const rerouteFromPosition = useCallback(async (fromLat: number, fromLng: number) => {
    if (!destination) return;

    // Abort any in-flight route request; its answer (if it still arrives) must not overwrite the new route
    if (routeAbortControllerRef.current) {
      routeAbortControllerRef.current.abort();
    }
    const token = latestRoute.current.begin();
    routeAbortControllerRef.current = new AbortController();
    reroutedRef.current = true;

    setIsRerouting(true);

    const rerouteOrigin: Point = {
      lat: fromLat,
      lng: fromLng,
      name: 'Current Position',
      address: 'GPS Reroute Point',
    };

    // Use the same mode as the active route (prefer 'shortest' or 'dynamic', not 'fastest')
    const rerouteMode: RouteMode = mode === 'fastest' ? selectedRouteType : mode;

    try {
      const res = await fetchRoute(
        rerouteMode,
        rerouteOrigin,
        destination,
        routeAbortControllerRef.current.signal
      );
      if (res.aborted || !latestRoute.current.isCurrent(token)) return;

      if (res.status === 'success' && res.path && res.path.length > 0) {
        // Replace active routeData with the new rerouted path.
        // Keep origin/destination state unchanged so UI labels stay correct.
        setRouteData(res);
        if (rerouteMode === 'dynamic') {
          setDynamicRouteData(res);
        } else {
          setShortestRouteData(res);
        }
        if (voiceEnabled) voiceGuidance.speak('New route found');
      } else {
        addToast('Could not reroute from your position. Stay on course.', 'warning');
      }
    } catch (err: any) {
      if (err.name !== 'AbortError' && latestRoute.current.isCurrent(token)) {
        addToast('Rerouting failed. Check backend connection.', 'error');
      }
    } finally {
      setIsRerouting(false);
    }
  }, [destination, mode, selectedRouteType, addToast]);

  // Keep the ref always pointing to the latest version of rerouteFromPosition
  // so the navigation engine can call it via a stable ref without stale closures
  rerouteFromPositionRef.current = rerouteFromPosition;

  // Fetch the route whenever origin, destination or mode changes. Debounced, so several quick changes make ONE request.
  useEffect(() => {
    const timer = setTimeout(() => {
      void loadRoute();
    }, ROUTE_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [loadRoute]);

  // Route Type Switcher (Shortest vs Dynamic)
  // Also marks the selection as confirmed — removes alternate ghost line.
  const handleSelectRouteType = useCallback(
    (type: 'shortest' | 'dynamic', confirmed = false) => {
      setSelectedRouteType(type);
      if (confirmed) setHasConfirmedRoute(true);
      const target = type === 'dynamic' ? dynamicRouteData : shortestRouteData;
      if (target) {
        setRouteData(target);
      }
    },
    [shortestRouteData, dynamicRouteData]
  );

  // Select Origin Handler
  const handleSelectOrigin = useCallback((loc: Point | null) => {
    latestGpsOrigin.current.invalidate();
    setOrigin(loc);
    if (loc && !destination) {
      setActiveInput('destination');
    }
  }, [destination]);

  // Use Current GPS as Origin
  const handleUseGpsOrigin = useCallback(async () => {
    const token = latestGpsOrigin.current.begin();
    try {
      const pos = await getCurrentLocation();
      if (!latestGpsOrigin.current.isCurrent(token)) return;
      setOrigin({
        lat: pos.lat,
        lng: pos.lng,
        name: 'My Location',
        address: 'Current GPS Location',
      });
      if (!destination) {
        setActiveInput('destination');
      }
    } catch (err: any) {
      if (!latestGpsOrigin.current.isCurrent(token)) return;
      addToast('Could not acquire GPS position. Ensure location services are enabled.', 'error');
    }
  }, [getCurrentLocation, destination, addToast]);

  // Select Destination Handler: with no start chosen yet, start from the rider's own location
  const handleSelectDestination = useCallback(
    (loc: Point | null) => {
      setDestination(loc);
      if (loc && !origin) void handleUseGpsOrigin();
    },
    [origin, handleUseGpsOrigin]
  );

  // Press-and-hold on the map: drop a pin and show the card (name looked up in the background)
  const handleLongPress = useCallback((position: { lat: number; lng: number }) => {
    const fallback: Point = {
      lat: position.lat,
      lng: position.lng,
      name: 'Dropped pin',
      address: `${position.lat.toFixed(5)}, ${position.lng.toFixed(5)}`,
    };
    setDroppedPin(fallback);
    setPinResolving(true);
    const token = latestPinName.current.begin();
    reverseGeocode(position.lat, position.lng).then((place) => {
      if (!latestPinName.current.isCurrent(token)) return; // the rider has pressed somewhere else since
      // only if the same pin is still showing (the rider may have pressed somewhere else meanwhile)
      setDroppedPin((current) =>
        current && current.lat === position.lat && current.lng === position.lng
          ? { ...current, name: place.name, address: place.address }
          : current
      );
      setPinResolving(false);
    });
  }, []);

  const handlePinAction = useCallback(
    (action: PinAction) => {
      if (!droppedPin) return;
      const next = applyPinAction(action, droppedPin, { origin, destination });
      setDroppedPin(null);
      latestGpsOrigin.current.invalidate();
      setOrigin(next.origin);
      setDestination(next.destination);
      if (next.needGpsOrigin) void handleUseGpsOrigin();
      else if (next.origin && !next.destination) setActiveInput('destination');
    },
    [droppedPin, origin, destination, handleUseGpsOrigin]
  );

  // Start Navigation Handlers
  const handleStartNavigation = useCallback(
    (chosenRoute?: 'shortest' | 'dynamic') => {
      const typeToUse = chosenRoute || selectedRouteType;
      const targetRoute =
        typeToUse === 'dynamic'
          ? dynamicRouteData || routeData
          : shortestRouteData || routeData;

      if (!targetRoute?.path) return;
      setSelectedRouteType(typeToUse);
      setRouteData(targetRoute);
      tripStartTimeRef.current = Date.now();
      reroutedRef.current = false;
      activeJourneyIdRef.current = targetRoute.journey_id || null;
      if (activeJourneyIdRef.current) {
        startTrip(activeJourneyIdRef.current, origin, destination);
      }
      setDroppedPin(null);
      requestCompassPermission();
      voiceGuidance.unlock(); // phones only allow speech after a tap: this is that tap
      startNavigation();
      setIsFollowingCamera(true);
    },
    [routeData, shortestRouteData, dynamicRouteData, selectedRouteType, startNavigation, requestCompassPermission, addToast, origin, destination]
  );

  // If the device cannot speak (no speech engine / no voice installed), say so once instead of staying silently mute.
  useEffect(() => {
    return voiceGuidance.onProblem((reason) => {
      addToast(
        reason === 'unsupported'
          ? "Voice guidance isn't available on this device"
          : `Voice guidance couldn't start (${reason}). Check the phone's text-to-speech settings`,
        'warning',
        6000
      );
    });
  }, [addToast]);

  // Preview Route Handler (Fits bounds to show full route)
  const handleStartPreview = useCallback((chosenRoute?: 'shortest' | 'dynamic') => {
    if (chosenRoute) {
      handleSelectRouteType(chosenRoute);
    }
    setIsFollowingCamera(false);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('fit-route-bounds'));
    }
  }, [handleSelectRouteType]);

  /** Drop a reroute that is still on its way: its answer must not arrive after the trip is over. */
  const cancelPendingReroute = useCallback(() => {
    routeAbortControllerRef.current?.abort();
    latestRoute.current.invalidate();
    setIsRerouting(false);
    setLoading(false);
  }, []);
  cancelRerouteRef.current = cancelPendingReroute;

  const handleEndNavigation = useCallback(() => {
    stopNavigation();
    if (reroutedRef.current) {
      // back to browsing: show the planned trip again, not the piece that started where the rider left the route
      reroutedRef.current = false;
      cancelPendingReroute();
      setRouteFor('');
      void loadRoute();
    }
  }, [stopNavigation, cancelPendingReroute, loadRoute]);

  const handleRecenter = useCallback(() => {
    setIsFollowingCamera(true);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('recenter-map'));
    }
  }, []);

  // After a finished trip: clear everything and go back to the normal starting map, centred on the rider.
  // (The selected route mode is kept; it is a preference, not trip state.)
  const resetToStart = useCallback(() => {
    stopNavigation();
    latestGpsOrigin.current.invalidate();
    setDroppedPin(null);
    setTripSummary(null);
    setOrigin(null);
    setDestination(null);
    setRouteData(null);
    setShortestRouteData(null);
    setDynamicRouteData(null);
    setHasConfirmedRoute(false);
    setActiveInput('origin');
    activeJourneyIdRef.current = null;
    tripStartTimeRef.current = 0;
    setIsFollowingCamera(true);
    if (typeof window !== 'undefined') {
      // after React has applied the cleared state, so the map recentres as "browsing" (flat, north-up), not "navigating"
      setTimeout(() => window.dispatchEvent(new CustomEvent('recenter-map')), 120);
    }
  }, [stopNavigation]);

  // Listen for user panning/dragging the map to unlink camera follow
  useEffect(() => {
    const handleCameraUnlink = () => setIsFollowingCamera(false);
    window.addEventListener('camera-unlinked', handleCameraUnlink);
    return () => window.removeEventListener('camera-unlinked', handleCameraUnlink);
  }, []);

  return (
    <div className="relative w-screen h-screen h-[100dvh] overflow-hidden flex flex-col font-sans select-none bg-slate-950">
      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Arrival Completion Summary Modal */}
      <ArrivalModal summary={tripSummary} onDone={resetToStart} />

      {/* Card for a pin dropped by press-and-hold */}
      {!isNavigating && (
        <PlaceSheet
          pin={droppedPin}
          resolving={pinResolving}
          hasOrigin={!!origin}
          onAction={handlePinAction}
          onClose={() => setDroppedPin(null)}
        />
      )}

      {/* Google Maps-style Incident Reporting Button & Modal */}
      <IncidentReportModal
        isNavigating={isNavigating}
        currentLat={realGpsPosition?.lat ?? origin?.lat ?? routeData?.path?.[0]?.[0]}
        currentLng={realGpsPosition?.lng ?? origin?.lng ?? routeData?.path?.[0]?.[1]}
        currentHeading={deviceHeading || realGpsPosition?.heading}
        currentRoadName={currentRoadName ?? currentManeuver?.road_name}
        activeIncidents={activeIncidents}
        onIncidentReported={(newInc) => {
          setActiveIncidents((prev) => [newInc, ...prev.filter((i) => i.id !== newInc.id)]);
          addToast(`Reported: ${newInc.title}`, 'success', 3000);
        }}
        onIncidentUpdated={refreshIncidents}
        onReportFailed={() => addToast('Your report could not be sent. Check your connection and try again.', 'warning', 5000)}
      />

      {/* Fullscreen Map Canvas */}
      <MapContainer
        origin={origin}
        destination={destination}
        activeInput={activeInput}
        routePath={routeData?.path || null}
        alternateRoutePath={
          // Only show the ghost alternate route while both routes are loaded
          // AND the user has NOT yet confirmed/selected one of them.
          // Once user taps a route card => hasConfirmedRoute=true => ghost disappears.
          mode === 'fastest' && shortestRouteData && dynamicRouteData && !hasConfirmedRoute
            ? selectedRouteType === 'dynamic'
              ? shortestRouteData?.path
              : dynamicRouteData?.path
            : null
        }
        selectedRouteType={selectedRouteType}
        onSelectRouteType={handleSelectRouteType}
        traveledIndex={nearestSegmentIndex}
        displayPosition={progress ? { lat: progress.displayLat, lng: progress.displayLng } : null}
        routePoint={progress ? { lat: progress.routeLat, lng: progress.routeLng } : null}
        gpsPosition={realGpsPosition}
        deviceHeading={deviceHeading}
        theme={theme}
        mode={mode}
        isFollowingCamera={isFollowingCamera}
        isNavigating={isNavigating}
        activeIncidents={activeIncidents}
        droppedPin={droppedPin}
        onLongPress={handleLongPress}
        onRecenter={handleRecenter}
        onCameraUnlink={() => setIsFollowingCamera(false)}
      />

      {/* Floating Top UI Layer */}
      <div className="absolute top-2 sm:top-4 left-2 right-2 sm:left-4 sm:right-4 z-20 space-y-2 pointer-events-none safe-top">
        {/* Top Header Bar with Brand and Mode Selector (hidden while riding: the room goes to the turn banner) */}
        <div className={`${isNavigating ? 'hidden ' : ''}pointer-events-auto max-w-lg mx-auto w-full space-y-1.5 sm:space-y-2`}>
          {/* Header Row */}
          <div className="flex items-center justify-between gap-2 sm:gap-3">
            {/* Brand Logo Pill */}
            <div className="bg-[#0f172a]/95 backdrop-blur-md border border-slate-700/80 px-2.5 py-1.5 sm:px-2.5 sm:py-1 rounded-xl sm:rounded-xl flex items-center gap-1.5 text-[11px] sm:text-[11px] font-mono font-bold tracking-widest text-slate-200 shadow-md shrink-0">
              <Bike className="w-3.5 h-3.5 sm:w-3.5 sm:h-3.5 text-sky-400" />
              <span>
                BLR<b className="text-lime-400 font-black">NAV</b>
              </span>
            </div>

            {/* Desktop Mode Selector */}
            {!isNavigating && (
              <div className="hidden sm:flex flex-1 justify-end">
                <ModeSelector mode={mode} onSelectMode={setMode} />
              </div>
            )}
          </div>

          {/* Mobile Mode Selector (Centered responsive tabs) */}
          {!isNavigating && (
            <div className="flex sm:hidden justify-center w-full">
              <ModeSelector mode={mode} onSelectMode={setMode} />
            </div>
          )}
        </div>

        {/* Search Bar Input (When not navigating) */}
        {!isNavigating && (
          <div className="pointer-events-auto">
            <TopSearchBar
              origin={origin}
              destination={destination}
              activeInput={activeInput}
              setActiveInput={setActiveInput}
              onSelectOrigin={handleSelectOrigin}
              onSelectDestination={handleSelectDestination}
              onUseGpsOrigin={handleUseGpsOrigin}
              gpsLoading={isLocating}
              onSwap={() => {
                latestGpsOrigin.current.invalidate();
                const temp = origin;
                setOrigin(destination);
                setDestination(temp);
              }}
              onClear={() => {
                latestGpsOrigin.current.invalidate();
                setDroppedPin(null);
                setOrigin(null);
                setDestination(null);
                setRouteData(null);
                setActiveInput('origin');
                handleEndNavigation();
              }}
              isNavigating={isNavigating}
            />
          </div>
        )}

        {/* Turn-by-Turn Navigation Header Banner */}
        {isNavigating && (
          <div className="pointer-events-auto">
            <TurnByTurnBanner
              currentManeuver={currentManeuver}
              nextManeuver={nextManeuver}
              distanceToManeuverMeters={distanceToManeuverMeters}
              currentRoadName={currentRoadName}
              navState={isRerouting ? 'rerouting' : navState}
              voiceEnabled={voiceEnabled}
              onToggleVoice={() => setVoiceEnabled(!voiceEnabled)}
            />
          </div>
        )}
      </div>

      {/* Floating Bottom Navigation Controls & Drawer */}
      <div className="pointer-events-none">
        {isNavigating ? (
          <div className="pointer-events-auto">
            <NavigationFooter
              remainingSeconds={trip.remainingS}
              arrivalMs={trip.arrivalMs}
              speedKmh={trip.speedKmh}
              remainingMeters={remainingMeters || routeTotalM}
              isFollowingCamera={isFollowingCamera}
              onRecenter={handleRecenter}
              onEndNavigation={handleEndNavigation}
            />
          </div>
        ) : (
          routeData?.path && routeFor === tripKey(origin, destination, mode) && (
            <div className="pointer-events-auto">
              <BottomActionBar
                routeData={routeData}
                shortestRouteData={shortestRouteData}
                dynamicRouteData={dynamicRouteData}
                selectedRouteType={selectedRouteType}
                onSelectRouteType={(type) => handleSelectRouteType(type, true)}
                mode={mode}
                isOriginMyLocation={isOriginMyLocation}
                onStartNavigation={handleStartNavigation}
                onStartPreview={handleStartPreview}
              />
            </div>
          )
        )}
      </div>

      {/* Rerouting Banner — shown briefly while new route is being calculated */}
      {isRerouting && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 pointer-events-none">
          <div className="glass-panel-heavy px-5 py-3 rounded-2xl flex items-center gap-3 text-amber-400 font-bold text-xs shadow-2xl border border-amber-500/40 animate-in fade-in zoom-in-95 duration-200">
            <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
            <span>Rerouting from your position...</span>
          </div>
        </div>
      )}

      {/* Loading Spinner Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-xs z-50 flex items-center justify-center pointer-events-none">
          <div className="glass-panel-heavy px-5 py-3 sm:px-5 sm:py-3 rounded-2xl sm:rounded-2xl flex items-center gap-2.5 sm:gap-3 text-sky-400 font-bold text-xs sm:text-xs shadow-2xl border border-slate-700/80">
            <Loader2 className="w-4 h-4 sm:w-4 sm:h-4 animate-spin text-sky-400" />
            <span>Finding optimal Bangalore route...</span>
          </div>
        </div>
      )}
    </div>
  );
}
