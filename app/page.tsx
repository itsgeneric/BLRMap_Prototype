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
import { fetchRoute } from '@/lib/api';
import { haversineMeters } from '@/lib/geo';
import { useGPS } from '@/hooks/useGPS';
import { useNavigationEngine } from '@/hooks/useNavigationEngine';

import { ThemeToggle } from '@/components/UI/ThemeToggle';
import { TopSearchBar } from '@/components/Navigation/TopSearchBar';
import { ModeSelector } from '@/components/Navigation/ModeSelector';
import { TurnByTurnBanner } from '@/components/Navigation/TurnByTurnBanner';
import { NavigationFooter } from '@/components/Navigation/NavigationFooter';
import { BottomActionBar } from '@/components/Navigation/BottomActionBar';
import { ToastContainer } from '@/components/UI/Toast';
import { ArrivalModal } from '@/components/Navigation/ArrivalModal';
import { Loader2, Bike } from 'lucide-react';

// Dynamic SSR-disabled MapContainer
const MapContainer = dynamic(
  () => import('@/components/Map/MapContainer').then((mod) => mod.MapContainer),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full bg-slate-950 flex flex-col items-center justify-center text-sky-400 font-mono text-xs gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
        <span>Loading Bengaluru Map Engine...</span>
      </div>
    ),
  }
);

export default function NavigationApp() {
  const [theme, setTheme] = useState<ThemeMode>('dark');
  const [origin, setOrigin] = useState<Point | null>(null);
  const [destination, setDestination] = useState<Point | null>(null);
  const [activeInput, setActiveInput] = useState<'origin' | 'destination'>('origin');
  const [mode, setMode] = useState<RouteMode>('shortest');
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [isFollowingCamera, setIsFollowingCamera] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [tripSummary, setTripSummary] = useState<TripSummary | null>(null);

  const routeAbortControllerRef = useRef<AbortController | null>(null);
  const tripStartTimeRef = useRef<number>(0);

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

  // Single Centralized GPS & Compass Hook
  const {
    gpsPosition: realGpsPosition,
    isLocating,
    getCurrentLocation,
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
    nearestSegmentIndex,
    distanceToManeuverMeters,
    remainingMeters,
    currentManeuver,
    nextManeuver,
    startNavigation,
    stopNavigation,
  } = useNavigationEngine({
    routeData,
    gpsPosition: realGpsPosition,
    voiceEnabled,
    onRerouteNeeded: () => {
      loadRoute();
    },
    onArrival: () => {
      const timeTakenSec = Math.max(1, Math.round((Date.now() - tripStartTimeRef.current) / 1000));
      const distKm = routeData?.distance_km || 0;
      setTripSummary({
        distanceKm: distKm,
        timeTakenSec,
        avgSpeedKmh: distKm > 0 ? distKm / (timeTakenSec / 3600) : 0,
        originName: origin?.name || 'Start Point',
        destinationName: destination?.name || 'Destination',
      });
    },
  });

  // Handle Theme Toggle
  const handleThemeToggle = (newTheme: ThemeMode) => {
    setTheme(newTheme);
    if (typeof document !== 'undefined') {
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
      } else {
        document.documentElement.classList.add('light');
        document.documentElement.classList.remove('dark');
      }
    }
  };

  // Route Fetch Function
  const loadRoute = useCallback(async () => {
    if (!origin || !destination) {
      setRouteData(null);
      return;
    }

    if (routeAbortControllerRef.current) {
      routeAbortControllerRef.current.abort();
    }
    routeAbortControllerRef.current = new AbortController();

    setLoading(true);
    try {
      const res = await fetchRoute(mode, origin, destination, routeAbortControllerRef.current.signal);
      if (res.status === 'success' && res.path && res.path.length > 0) {
        setRouteData(res);
      } else {
        setRouteData(null);
        addToast(res.message || 'No viable route found between these locations.', 'error');
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
  const handleStartNavigation = useCallback(() => {
    if (!routeData?.path) return;
    tripStartTimeRef.current = Date.now();
    startNavigation();
    setIsFollowingCamera(true);
  }, [routeData, startNavigation]);

  // Preview Route Handler (Fits bounds to show full route)
  const handleStartPreview = useCallback(() => {
    setIsFollowingCamera(false);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('fit-route-bounds'));
    }
  }, []);

  const handleEndNavigation = useCallback(() => {
    stopNavigation();
  }, [stopNavigation]);

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
        onClose={() => setTripSummary(null)}
        onNewRoute={() => {
          setTripSummary(null);
          setOrigin(null);
          setDestination(null);
          setRouteData(null);
          setActiveInput('origin');
        }}
      />

      {/* Fullscreen Map Canvas */}
      <MapContainer
        origin={origin}
        destination={destination}
        activeInput={activeInput}
        routePath={routeData?.path || null}
        traveledIndex={nearestSegmentIndex}
        gpsPosition={realGpsPosition}
        theme={theme}
        mode={mode}
        isFollowingCamera={isFollowingCamera}
        isNavigating={isNavigating}
        onSelectOrigin={handleSelectOrigin}
        onSelectDestination={handleSelectDestination}
      />

      {/* Floating Top UI Layer */}
      <div className="absolute top-2 sm:top-4 left-2 right-2 sm:left-4 sm:right-4 z-20 space-y-2 pointer-events-none safe-top">
        {/* Top Header Bar with Brand, Mode Selector, and Theme Toggle */}
        <div className="flex items-center justify-between gap-2 pointer-events-auto max-w-lg mx-auto w-full">
          {/* Brand Logo Pill */}
          <div className="bg-[#0f172a] border border-slate-700/80 px-2 py-1 sm:px-3.5 sm:py-1.5 rounded-xl sm:rounded-2xl flex items-center gap-1 sm:gap-1.5 text-[11px] sm:text-xs font-mono font-bold tracking-widest text-slate-200 shadow-md shrink-0">
            <Bike className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-sky-400" />
            <span>
              BLR<b className="text-lime-400 font-black">NAV</b>
            </span>
          </div>

          {/* Mode Selector (When not actively driving) */}
          {!isNavigating && (
            <ModeSelector mode={mode} onSelectMode={setMode} />
          )}

          {/* Theme Switcher Toggle */}
          <ThemeToggle theme={theme} onToggle={handleThemeToggle} />
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
              currentManeuver={currentManeuver}
              nextManeuver={nextManeuver}
              distanceToManeuverMeters={distanceToManeuverMeters}
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
              currentSpeedMps={realGpsPosition?.speed || 0}
              remainingMeters={remainingMeters || ((routeData?.distance_km || 0) * 1000)}
              isFollowingCamera={isFollowingCamera}
              onRecenter={handleRecenter}
              onEndNavigation={handleEndNavigation}
            />
          </div>
        ) : (
          routeData?.path && (
            <div className="pointer-events-auto">
              <BottomActionBar
                routeData={routeData}
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
      {loading && (
        <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-xs z-50 flex items-center justify-center pointer-events-none">
          <div className="glass-panel-heavy px-5 py-3 sm:px-6 sm:py-4 rounded-3xl flex items-center gap-3 text-sky-400 font-bold text-xs sm:text-sm shadow-2xl border border-slate-700/80">
            <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
            <span>Finding optimal Bangalore route...</span>
          </div>
        </div>
      )}
    </div>
  );
}
