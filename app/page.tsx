'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import {
  Point,
  RouteMode,
  RouteResponse,
  GPSPosition,
  ThemeMode,
} from '@/lib/types';
import { fetchRoute } from '@/lib/api';
import {
  haversineMeters,
  calculateBearing,
  findDistanceToPolyline,
} from '@/lib/geo';
import { voiceGuidance } from '@/lib/speech';

import { ThemeToggle } from '@/components/UI/ThemeToggle';
import { TopSearchBar } from '@/components/Navigation/TopSearchBar';
import { ModeSelector } from '@/components/Navigation/ModeSelector';
import { TurnByTurnBanner } from '@/components/Navigation/TurnByTurnBanner';
import { NavigationFooter } from '@/components/Navigation/NavigationFooter';
import { BottomActionBar } from '@/components/Navigation/BottomActionBar';
import { Loader2, Bike } from 'lucide-react';

// Dynamic SSR-disabled import for MapContainer
const MapContainer = dynamic(
  () => import('@/components/Map/MapContainer').then((mod) => mod.MapContainer),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full bg-slate-950 flex items-center justify-center text-sky-400 font-mono text-xs">
        <Loader2 className="w-6 h-6 animate-spin text-sky-400 mr-2" />
        Loading Bangalore Map...
      </div>
    ),
  }
);

export default function NavigationApp() {
  const [theme, setTheme] = useState<ThemeMode>('dark');
  const [origin, setOrigin] = useState<Point | null>(null);
  const [destination, setDestination] = useState<Point | null>(null);
  const [mode, setMode] = useState<RouteMode>('shortest');
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Navigation State
  const [isNavigating, setIsNavigating] = useState(false);
  const [gpsPosition, setGpsPosition] = useState<GPSPosition | null>(null);
  const [isFollowingCamera, setIsFollowingCamera] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [currentManeuverIndex, setCurrentManeuverIndex] = useState(0);

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

  // Real Hardware GPS Watcher
  useEffect(() => {
    if (typeof window === 'undefined' || !('geolocation' in navigator)) return;

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        setGpsPosition({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          heading: pos.coords.heading || 0,
          speed: pos.coords.speed || 0,
          accuracy: pos.coords.accuracy,
          timestamp: pos.timestamp,
        });
      },
      (err) => console.warn('Geolocation warning:', err.message),
      { enableHighAccuracy: true, maximumAge: 1000, timeout: 5000 }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

  // Fetch Route when origin, destination, or mode changes
  useEffect(() => {
    if (!origin || !destination) {
      setRouteData(null);
      return;
    }

    let isMounted = true;
    const loadRoute = async () => {
      setLoading(true);
      try {
        const res = await fetchRoute(mode, origin, destination);
        if (isMounted) {
          setRouteData(res);
          setCurrentManeuverIndex(0);
        }
      } catch (err) {
        console.error('Failed to load route:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadRoute();
    return () => { isMounted = false; };
  }, [origin, destination, mode]);

  // Navigation Logic (Off-route detection, Maneuver updates, Voice Prompts)
  useEffect(() => {
    if (!isNavigating || !routeData?.maneuvers || !gpsPosition) return;

    const maneuvers = routeData.maneuvers;
    if (currentManeuverIndex >= maneuvers.length) return;

    const currentM = maneuvers[currentManeuverIndex];
    const distToTurn = haversineMeters(gpsPosition.lat, gpsPosition.lng, currentM.lat, currentM.lng);

    // Speak turn instruction when within 120m
    if (distToTurn < 120) {
      voiceGuidance.speak(`In ${Math.round(distToTurn)} meters, ${currentM.instruction}`);
    }

    // Advance to next maneuver when passed
    if (distToTurn < 25 && currentManeuverIndex < maneuvers.length - 1) {
      setCurrentManeuverIndex((prev) => prev + 1);
    }

    // Off-route detection (> 45m from polyline)
    if (routeData.path) {
      const { distanceMeters } = findDistanceToPolyline(gpsPosition.lat, gpsPosition.lng, routeData.path);
      if (distanceMeters > 45) {
        voiceGuidance.speak('Recalculating route');
      }
    }
  }, [isNavigating, gpsPosition, routeData, currentManeuverIndex]);

  // Handle map click to place origin / destination
  const handleMapClick = useCallback((latlng: [number, number]) => {
    if (!origin) {
      setOrigin({ lat: latlng[0], lng: latlng[1], name: `${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}` });
    } else if (!destination) {
      setDestination({ lat: latlng[0], lng: latlng[1], name: `${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}` });
    }
  }, [origin, destination]);

  const handleStartNavigation = useCallback(() => {
    if (!routeData?.path) return;
    setIsNavigating(true);
    setIsFollowingCamera(true);
    voiceGuidance.setEnabled(voiceEnabled);
    voiceGuidance.speak('Starting navigation');
  }, [routeData, voiceEnabled]);

  const handleStartPreview = useCallback(() => {
    setIsNavigating(false);
    setIsFollowingCamera(false);
    voiceGuidance.speak('Previewing route');
  }, []);

  const handleEndNavigation = useCallback(() => {
    setIsNavigating(false);
    voiceGuidance.speak('Navigation ended');
  }, []);

  // Check if Origin is "My Location"
  const isOriginMyLocation = useMemo(() => {
    return (
      origin?.name?.toLowerCase().includes('my location') ||
      origin?.address?.toLowerCase().includes('my location') ||
      false
    );
  }, [origin]);

  const currentManeuver = routeData?.maneuvers?.[currentManeuverIndex] || null;
  const nextManeuver = routeData?.maneuvers?.[currentManeuverIndex + 1] || null;
  const distToNextManeuver = (currentManeuver && gpsPosition)
    ? haversineMeters(gpsPosition.lat, gpsPosition.lng, currentManeuver.lat, currentManeuver.lng)
    : (currentManeuver?.distance_m || 0);

  return (
    <div className="relative w-screen h-screen h-[100dvh] overflow-hidden flex flex-col font-sans select-none">
      {/* Fullscreen Map Canvas */}
      <MapContainer
        origin={origin}
        destination={destination}
        routePath={routeData?.path || null}
        gpsPosition={gpsPosition}
        theme={theme}
        mode={mode}
        isFollowingCamera={isFollowingCamera}
        isNavigating={isNavigating}
        onMapClick={handleMapClick}
      />

      {/* Floating Top UI Layer (Safe-Area Aware) */}
      <div className="absolute top-2 sm:top-4 left-2 right-2 sm:left-4 sm:right-4 z-20 space-y-2 pointer-events-none safe-top">
        {/* Top Header Bar with Brand, Mode Selector, and Theme Toggle */}
        <div className="flex items-center justify-between gap-2 pointer-events-auto max-w-lg mx-auto w-full">
          {/* Brand Logo Pill */}
          <div className="glass-panel px-3 py-2 sm:px-4 sm:py-2.5 rounded-2xl flex items-center gap-1.5 sm:gap-2 text-xs font-mono font-bold tracking-widest text-slate-200 shadow-lg shrink-0">
            <Bike className="w-4 h-4 text-sky-400" />
            <span>BLR<b className="text-lime-400 font-black">NAV</b></span>
          </div>

          {/* Mode Selector (When not actively driving/navigating) */}
          {!isNavigating && (
            <ModeSelector
              mode={mode}
              onSelectMode={setMode}
            />
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
              onSelectOrigin={setOrigin}
              onSelectDestination={setDestination}
              onSwap={() => {
                const temp = origin;
                setOrigin(destination);
                setDestination(temp);
              }}
              onClear={() => {
                setOrigin(null);
                setDestination(null);
                setRouteData(null);
                setIsNavigating(false);
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
              distanceToManeuverMeters={distToNextManeuver}
              voiceEnabled={voiceEnabled}
              onToggleVoice={() => {
                const nextVoice = !voiceEnabled;
                setVoiceEnabled(nextVoice);
                voiceGuidance.setEnabled(nextVoice);
              }}
            />
          </div>
        )}
      </div>

      {/* Floating Bottom Navigation Controls & Drawer */}
      <div className="pointer-events-none">
        {/* Navigation Footer during active GPS tracking */}
        {isNavigating ? (
          <div className="pointer-events-auto">
            <NavigationFooter
              currentSpeedMps={gpsPosition?.speed || 0}
              remainingMeters={(routeData?.distance_km || 0) * 1000}
              isFollowingCamera={isFollowingCamera}
              onRecenter={() => setIsFollowingCamera(true)}
              onEndNavigation={handleEndNavigation}
            />
          </div>
        ) : (
          /* Route Overview Bottom Sheet Card */
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
        <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-sm z-50 flex items-center justify-center pointer-events-none">
          <div className="glass-panel-heavy px-5 py-3 sm:px-6 sm:py-4 rounded-3xl flex items-center gap-3 text-sky-400 font-bold text-xs sm:text-sm shadow-2xl border border-slate-700/80">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Calculating fastest route...</span>
          </div>
        </div>
      )}
    </div>
  );
}
