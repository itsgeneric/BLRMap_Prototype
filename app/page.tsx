'use client';

import React, { useState, useEffect } from 'react';
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
import { SimulatedGpsControl } from '@/components/Navigation/SimulatedGpsControl';
import { Navigation, Loader2, Bike } from 'lucide-react';

// Dynamic SSR-disabled import for MapContainer
const MapContainer = dynamic(
  () => import('@/components/Map/MapContainer').then((mod) => mod.MapContainer),
  { ssr: false }
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

  // Simulation State
  const [isSimulating, setIsSimulating] = useState(false);
  const [simIndex, setSimIndex] = useState(0);
  const [simSpeedKmh, setSimSpeedKmh] = useState(35);

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
        if (!isSimulating) {
          setGpsPosition({
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
            heading: pos.coords.heading || 0,
            speed: pos.coords.speed || 0,
            accuracy: pos.coords.accuracy,
            timestamp: pos.timestamp,
          });
        }
      },
      (err) => console.warn('Geolocation warning:', err.message),
      { enableHighAccuracy: true, maximumAge: 1000, timeout: 5000 }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, [isSimulating]);

  // Fetch Route when origin, destination, or mode changes
  useEffect(() => {
    if (!origin || !destination) {
      setRouteData(null);
      return;
    }

    const loadRoute = async () => {
      setLoading(true);
      const res = await fetchRoute(mode, origin, destination);
      setRouteData(res);
      setLoading(false);
      setCurrentManeuverIndex(0);
      setSimIndex(0);
    };

    loadRoute();
  }, [origin, destination, mode]);

  // Simulated GPS Driver Loop
  useEffect(() => {
    if (!isSimulating || !routeData?.path || routeData.path.length < 2) return;

    const intervalMs = 200;

    const timer = setInterval(() => {
      setSimIndex((prevIdx) => {
        const path = routeData.path!;
        if (prevIdx >= path.length - 1) {
          setIsSimulating(false);
          voiceGuidance.speak('You have arrived at your destination');
          return prevIdx;
        }

        const nextIdx = prevIdx + 1;
        const currentPt = path[prevIdx];
        const nextPt = path[nextIdx];
        const heading = calculateBearing(currentPt[0], currentPt[1], nextPt[0], nextPt[1]);

        setGpsPosition({
          lat: currentPt[0],
          lng: currentPt[1],
          heading: heading,
          speed: (simSpeedKmh * 1000) / 3600,
          accuracy: 5,
          timestamp: Date.now(),
        });

        return nextIdx;
      });
    }, intervalMs);

    return () => clearInterval(timer);
  }, [isSimulating, routeData, simSpeedKmh]);

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
  const handleMapClick = (latlng: [number, number]) => {
    if (!origin) {
      setOrigin({ lat: latlng[0], lng: latlng[1], name: `${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}` });
    } else if (!destination) {
      setDestination({ lat: latlng[0], lng: latlng[1], name: `${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}` });
    }
  };

  const handleStartNavigation = () => {
    if (!routeData?.path) return;
    setIsNavigating(true);
    setIsFollowingCamera(true);
    voiceGuidance.setEnabled(voiceEnabled);
    voiceGuidance.speak('Starting navigation');
  };

  const handleEndNavigation = () => {
    setIsNavigating(false);
    setIsSimulating(false);
    voiceGuidance.speak('Navigation ended');
  };

  const currentManeuver = routeData?.maneuvers?.[currentManeuverIndex] || null;
  const nextManeuver = routeData?.maneuvers?.[currentManeuverIndex + 1] || null;
  const distToNextManeuver = (currentManeuver && gpsPosition)
    ? haversineMeters(gpsPosition.lat, gpsPosition.lng, currentManeuver.lat, currentManeuver.lng)
    : (currentManeuver?.distance_m || 0);

  return (
    <div className="relative w-screen h-screen overflow-hidden flex flex-col font-sans">
      {/* Fullscreen Map Canvas */}
      <MapContainer
        origin={origin}
        destination={destination}
        routePath={routeData?.path || null}
        gpsPosition={gpsPosition}
        theme={theme}
        mode={mode}
        isFollowingCamera={isFollowingCamera}
        onMapClick={handleMapClick}
      />

      {/* Floating Top UI Layer */}
      <div className="absolute top-4 left-4 right-4 z-20 space-y-3 pointer-events-none">
        <div className="flex items-center justify-between gap-3 pointer-events-auto max-w-4xl mx-auto">
          {/* Brand Logo Pill */}
          <div className="glass-panel px-4 py-2 rounded-2xl flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-slate-200">
            <Bike className="w-4 h-4 text-sky-400" />
            <span>BLR<b className="text-lime-400 font-black">NAV</b></span>
          </div>

          {/* Mode Selector Dropdown Bar */}
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
                setVoiceEnabled(!voiceEnabled);
                voiceGuidance.setEnabled(!voiceEnabled);
              }}
            />
          </div>
        )}
      </div>

      {/* Floating Bottom Navigation Controls & Drawer */}
      <div className="absolute bottom-4 left-4 right-4 z-20 pointer-events-none">
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
          /* Route Overview & Start Button Bottom Panel */
          routeData?.path && (
            <div className="pointer-events-auto max-w-xl mx-auto glass-panel p-4 rounded-3xl space-y-3 shadow-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-sky-500/10 rounded-2xl text-sky-400 border border-sky-500/20">
                    <Navigation className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xl font-black text-slate-100 flex items-baseline gap-2">
                      <span>{routeData.distance_km} km</span>
                      {routeData.google_base_duration_mins && (
                        <span className="text-sm font-semibold text-pink-400">
                          {routeData.google_base_duration_mins} min live
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 font-medium capitalize">
                      {mode === 'shortest' ? 'Shortest Path' : 'Dynamic Route'} • {routeData.maneuvers?.length || 0} maneuvers
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleStartNavigation}
                  className="px-6 py-3.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-black rounded-2xl shadow-lg shadow-sky-500/30 flex items-center gap-2 transition-all transform active:scale-95"
                >
                  <Navigation className="w-4 h-4 fill-current" />
                  <span>Start Navigation</span>
                </button>
              </div>

              {/* Simulation Driver Controls */}
              <SimulatedGpsControl
                isSimulating={isSimulating}
                onToggleSimulate={() => setIsSimulating(!isSimulating)}
                onResetSimulate={() => setSimIndex(0)}
                speedKmh={simSpeedKmh}
                onSpeedChange={setSimSpeedKmh}
              />
            </div>
          )
        )}
      </div>

      {/* Loading Spinner Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-sm z-50 flex items-center justify-center pointer-events-none">
          <div className="glass-panel px-6 py-4 rounded-2xl flex items-center gap-3 text-sky-400 font-bold">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Calculating route...</span>
          </div>
        </div>
      )}
    </div>
  );
}

