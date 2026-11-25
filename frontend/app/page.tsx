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
} from '@/lib/types';
import { fetchRoute, fetchBothRoutes } from '@/lib/api';
import { haversineMeters } from '@/lib/geo';
import { useGPS } from '@/hooks/useGPS';
import { useNavigationEngine } from '@/hooks/useNavigationEngine';
import { useSimulatedGPS, getSimulationSpeedKmh } from '@/hooks/useSimulatedGPS';
import { startTrip, completeTrip, reportReroute } from '@/lib/tripTracker';

import { TopSearchBar } from '@/components/Navigation/TopSearchBar';
import { ModeSelector } from '@/components/Navigation/ModeSelector';
import { TurnByTurnBanner } from '@/components/Navigation/TurnByTurnBanner';
import { NavigationFooter } from '@/components/Navigation/NavigationFooter';
import { BottomActionBar } from '@/components/Navigation/BottomActionBar';
import { ToastContainer } from '@/components/UI/Toast';
import { ArrivalModal } from '@/components/Navigation/ArrivalModal';
import { Loader2, Bike, Volume2, VolumeX } from 'lucide-react';

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
  const [isFollowingCamera, setIsFollowingCamera] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [tripSummary, setTripSummary] = useState<TripSummary | null>(null);

  const routeAbortControllerRef = useRef<AbortController | null>(null);
  const tripStartTimeRef = useRef<number>(0);
  const activeJourneyIdRef = useRef<string | null>(null);

  // Toast Helpers (Reserved only for genuine errors)
  const addToast = useCallback((text: string, type: ToastMessage['type'] = 'error', duration = 4000) => {
    const id = `${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    setToasts((prev) => [...prev, { id, text, type, duration }]);
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
    gpsPosition: deviceGpsPosition,
    deviceHeading,
    isLocating,
    getCurrentLocation,
  } = useGPS();

  // Drive simulator for desktop testing (only with ?simulate=1 in the URL)
  const [simSpeedKmh] = useState<number | null>(() => getSimulationSpeedKmh());
  const [simActive, setSimActive] = useState(false);
  const simulatedGps = useSimulatedGPS(routeData?.path, routeData?.maneuvers, simActive, simSpeedKmh);
  const realGpsPosition = simActive && simulatedGps ? simulatedGps : deviceGpsPosition;

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
    status: navStatus,
    isNavigating,
    pose: navPose,
    routeIndex,
    currentManeuver,
    nextManeuver,
    currentManeuverAlong,
    distanceToManeuverMeters,
    distanceBetweenManeuvers,
    remainingMeters,
    remainingSeconds,
    startNavigation,
    stopNavigation,
  } = useNavigationEngine({
    routeData,
    gpsPosition: realGpsPosition,
    voiceEnabled,
    destinationName: destination?.name,
    onRerouteNeeded: (info) => {
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
      if (info) loadRoute({ lat: info.lat, lng: info.lng }, info.heading);
    },
    onArrival: () => {
      setSimActive(false);
      const timeTakenSec = Math.max(1, Math.round((Date.now() - tripStartTimeRef.current) / 1000));
      const distKm = routeData?.distance_km || 0;
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

  // Route Fetch Function
  const loadRoute = useCallback(async (startPoint?: { lat: number; lng: number }, heading?: number | null) => {
    if (!origin || !destination) {
      setRouteData(null);
      setShortestRouteData(null);
      setDynamicRouteData(null);
      return;
    }

    if (routeAbortControllerRef.current) {
      routeAbortControllerRef.current.abort();
    }
    routeAbortControllerRef.current = new AbortController();
    // Reset confirmation on every new fetch — show both routes again
    setHasConfirmedRoute(false);

    setLoading(true);
    try {
      if (mode === 'fastest') {
        const both = await fetchBothRoutes(startPoint || origin, destination, routeAbortControllerRef.current.signal, heading);
        setShortestRouteData(both.shortest);
        setDynamicRouteData(both.dynamic);

        const chosenType = both.fastestChoice;
        setSelectedRouteType(chosenType);

        const activeRes = both[chosenType] || both.shortest || both.dynamic;
        if (activeRes && activeRes.path && activeRes.path.length > 0) {
          setRouteData(activeRes);
        } else {
          if (!startPoint) setRouteData(null);
          addToast('Could not calculate fastest route comparison.', 'error');
        }
      } else {
        const res = await fetchRoute(mode, startPoint || origin, destination, routeAbortControllerRef.current.signal, heading);
        if (res.status === 'success' && res.path && res.path.length > 0) {
          setRouteData(res);
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
          if (!startPoint) {
            setRouteData(null);
            setShortestRouteData(null);
            setDynamicRouteData(null);
          }
          addToast(res.message || 'No viable route found between these locations.', 'error');
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        addToast('Failed to calculate route. Check backend connection.', 'error');
      }
    } finally {
      setLoading(false);
    }
  }, [origin, destination, mode, addToast]);

  // Fetch Route whenever origin, destination, or mode updates
  useEffect(() => {
    loadRoute();
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
    setOrigin(loc);
    if (loc && !destination) {
      setActiveInput('destination');
    }
  }, [destination]);

  // Select Destination Handler
  const handleSelectDestination = useCallback((loc: Point | null) => {
    setDestination(loc);
  }, []);

  // Use Current GPS as Origin
  const handleUseGpsOrigin = useCallback(async () => {
    try {
      const pos = await getCurrentLocation();
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
      addToast('Could not acquire GPS position. Ensure location services are enabled.', 'error');
    }
  }, [getCurrentLocation, destination, addToast]);

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
      activeJourneyIdRef.current = targetRoute.journey_id || null;
      if (activeJourneyIdRef.current) {
        startTrip(activeJourneyIdRef.current, origin, destination);
      }
      startNavigation();
      setIsFollowingCamera(true);
      if (simSpeedKmh) setSimActive(true);
    },
    [routeData, shortestRouteData, dynamicRouteData, selectedRouteType, startNavigation, origin, destination, simSpeedKmh]
  );

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

  const handleEndNavigation = useCallback(() => {
    stopNavigation();
    setSimActive(false);
  }, [stopNavigation]);

  const handleOverview = useCallback(() => {
    setIsFollowingCamera(false);
    if (typeof window !== 'undefined') window.dispatchEvent(new CustomEvent('fit-route-bounds'));
  }, []);

  // Keep the screen on while navigating (as navigation apps do)
  useEffect(() => {
    if (!isNavigating || typeof navigator === 'undefined' || !('wakeLock' in navigator)) return;
    let lock: { release: () => Promise<void> } | null = null;
    let cancelled = false;
    const acquire = async () => {
      try {
        lock = await (navigator as any).wakeLock.request('screen');
        if (cancelled) lock?.release();
      } catch {
        /* not allowed (e.g. battery saver) - navigation still works */
      }
    };
    const onVisible = () => {
      if (document.visibilityState === 'visible') acquire();
    };
    acquire();
    document.addEventListener('visibilitychange', onVisible);
    return () => {
      cancelled = true;
      document.removeEventListener('visibilitychange', onVisible);
      lock?.release().catch(() => {});
    };
  }, [isNavigating]);

  const handleRecenter = useCallback(() => {
    setIsFollowingCamera(true);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('recenter-map'));
    }
  }, []);

  return (
    <div className="relative w-screen h-screen h-[100dvh] overflow-hidden flex flex-col font-sans select-none bg-slate-950">
      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Arrival Completion Summary Modal */}
      <ArrivalModal
        summary={tripSummary}
        side={routeData?.maneuvers?.[routeData.maneuvers.length - 1]?.side ?? null}
        onClose={() => setTripSummary(null)}
        onNewRoute={() => {
          setTripSummary(null);
          setOrigin(null);
          setDestination(null);
          setRouteData(null);
          setShortestRouteData(null);
          setDynamicRouteData(null);
          setActiveInput('origin');
        }}
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
        gpsPosition={realGpsPosition}
        navPose={navPose}
        routeIndex={routeIndex}
        maneuverAlong={currentManeuverAlong}
        maneuverType={currentManeuver?.type ?? null}
        distanceToManeuver={distanceToManeuverMeters}
        onUserPan={() => setIsFollowingCamera(false)}
        deviceHeading={deviceHeading}
        theme={theme}
        mode={mode}
        isFollowingCamera={isFollowingCamera}
        isNavigating={isNavigating}
        onSelectOrigin={handleSelectOrigin}
        onSelectDestination={handleSelectDestination}
      />

      {/* Floating Top UI Layer */}
      <div className="absolute top-2 sm:top-4 left-2 right-2 sm:left-4 sm:right-4 z-20 space-y-2 pointer-events-none safe-top">
        {/* Top Header Bar with Brand and Mode Selector */}
        {!isNavigating && (
        <div className="pointer-events-auto max-w-lg mx-auto w-full space-y-1.5 sm:space-y-2">
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
        )}

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
                const temp = origin;
                setOrigin(destination);
                setDestination(temp);
              }}
              onClear={() => {
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
              status={navStatus}
              currentManeuver={currentManeuver}
              nextManeuver={nextManeuver}
              distanceToManeuverMeters={distanceToManeuverMeters}
              distanceBetweenManeuvers={distanceBetweenManeuvers}
            />
          </div>
        )}
        {isNavigating && (
          <div className="pointer-events-auto max-w-lg mx-auto flex justify-end">
            <button
              type="button"
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              title={voiceEnabled ? 'Mute voice guidance' : 'Unmute voice guidance'}
              aria-label={voiceEnabled ? 'Mute voice guidance' : 'Unmute voice guidance'}
              className="w-12 h-12 rounded-full bg-white shadow-lg shadow-black/25 flex items-center justify-center active:scale-95 transition cursor-pointer"
            >
              {voiceEnabled ? (
                <Volume2 className="w-6 h-6 text-[#3c4043]" />
              ) : (
                <VolumeX className="w-6 h-6 text-[#3c4043]" />
              )}
            </button>
          </div>
        )}
      </div>

      {/* Floating Bottom Navigation Controls & Drawer */}
      <div className="pointer-events-none">
        {isNavigating ? (
          <div className="pointer-events-auto">
            <NavigationFooter
              currentSpeedMps={realGpsPosition?.speed ?? null}
              remainingMeters={remainingMeters || ((routeData?.distance_km || 0) * 1000)}
              remainingSeconds={remainingSeconds}
              isFollowingCamera={isFollowingCamera}
              onRecenter={handleRecenter}
              onOverview={handleOverview}
              onEndNavigation={handleEndNavigation}
            />
          </div>
        ) : (
          routeData?.path && (
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

      {/* Loading Spinner Overlay */}
      {loading && !isNavigating && (
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
