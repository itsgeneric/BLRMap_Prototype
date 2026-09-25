'use client';

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  APIProvider,
  Map as GMap,
  useMap,
  AdvancedMarker,
  Pin,
} from '@vis.gl/react-google-maps';
import { Loader2 } from 'lucide-react';
import { LatLng as LatLngType, Point, GPSPosition, RouteMode } from '@/lib/types';
import { haversineMeters } from '@/lib/geo';
import { darkMapStyle, lightMapStyle } from './googleMapStyles';

export interface MapContainerProps {
  origin?: Point | null;
  destination?: Point | null;
  activeInput?: 'origin' | 'destination';
  routePath?: LatLngType[] | null;
  alternateRoutePath?: LatLngType[] | null;
  selectedRouteType?: 'shortest' | 'dynamic';
  onSelectRouteType?: (type: 'shortest' | 'dynamic') => void;
  traveledIndex?: number;
  gpsPosition?: GPSPosition | null;
  deviceHeading?: number;
  theme?: 'dark' | 'light' | string;
  mode?: RouteMode;
  isFollowingCamera?: boolean;
  isNavigating?: boolean;
  onSelectOrigin?: (location: Point) => void;
  onSelectDestination?: (location: Point) => void;
  onMapClick?: (latlng: [number, number]) => void;
  onRecenter?: () => void;
}

const GOOGLE_MAPS_API_KEY =
  process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY ||
  'AIzaSyDMeViVgIxe2EueO72GXA60D13o1ra-6yQ';

// ─────────────────────────────────────────────────────────────────
// Zoom-adaptive stroke weights — mirrors Google Maps route rendering
// ─────────────────────────────────────────────────────────────────
function getStrokeWeights(zoom: number): { casing: number; foreground: number; alternate: number } {
  if (zoom <= 10) return { casing: 3,   foreground: 2,   alternate: 1.5 };
  if (zoom <= 12) return { casing: 5,   foreground: 3.5, alternate: 2.5 };
  if (zoom <= 13) return { casing: 6,   foreground: 4.5, alternate: 3   };
  if (zoom <= 14) return { casing: 7,   foreground: 5,   alternate: 3.5 };
  if (zoom <= 15) return { casing: 8,   foreground: 6,   alternate: 4   };
  if (zoom <= 16) return { casing: 9,   foreground: 6.5, alternate: 4.5 };
  if (zoom <= 17) return { casing: 10,  foreground: 7.5, alternate: 5   };
  return                  { casing: 12, foreground: 9,   alternate: 6   };
}

// ─────────────────────────────────────────────────────────────────
// Google Maps-style Rider Marker (3D Navigation Arrow in nav, Blue dot + beam in browse)
// ─────────────────────────────────────────────────────────────────
function RiderMarkerIcon({
  heading,
  isNavigating = false,
}: {
  heading: number;
  isNavigating?: boolean;
}) {
  if (isNavigating) {
    // ── Google Maps Navigation 3D Chevron Arrow ──
    return (
      <div
        className="relative w-14 h-14 flex items-center justify-center pointer-events-none select-none"
        style={{
          transform: `rotate(${heading}deg)`,
          transition: 'transform 0.25s cubic-bezier(0.2, 0.8, 0.4, 1)',
        }}
      >
        <svg
          width="44"
          height="44"
          viewBox="0 0 48 48"
          fill="none"
          className="drop-shadow-[0_4px_12px_rgba(0,0,0,0.65)]"
        >
          {/* White outer stroke casing */}
          <path
            d="M24 3 L43 43 L24 33 L5 43 Z"
            fill="#FFFFFF"
          />
          {/* Left Wing (vibrant bright cyan) */}
          <path
            d="M24 6.5 L8.5 40 L24 31.5 Z"
            fill="#38bdf8"
          />
          {/* Right Wing (deep cobalt blue for 3D bevel lighting) */}
          <path
            d="M24 6.5 L39.5 40 L24 31.5 Z"
            fill="#0284c7"
          />
          {/* Center spine highlight */}
          <line
            x1="24"
            y1="7"
            x2="24"
            y2="31"
            stroke="#bae6fd"
            strokeWidth="1.2"
            strokeLinecap="round"
          />
        </svg>
      </div>
    );
  }

  // ── Browse Mode: Google Maps Blue Dot with Flashlight Cone & Directional Needle ──
  return (
    <div className="relative w-14 h-14 flex items-center justify-center pointer-events-none select-none">
      {/* Accuracy Pulse Ring */}
      <div className="absolute inset-2 bg-sky-400/20 rounded-full animate-ping" />

      {/* Rotating directional flashlight beam & needle */}
      <div
        className="absolute inset-0 flex items-center justify-center"
        style={{
          transform: `rotate(${heading}deg)`,
          transition: 'transform 0.3s cubic-bezier(0.2, 0, 0, 1)',
        }}
      >
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
          <defs>
            <radialGradient id="beamGrad" cx="28" cy="28" r="28" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.55" />
              <stop offset="70%" stopColor="#38bdf8" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
            </radialGradient>
          </defs>
          {/* 60-degree beam */}
          <path d="M28 28 L14 4 A28 28 0 0 1 42 4 Z" fill="url(#beamGrad)" />
          {/* Direction needle tip pointing out from dot */}
          <polygon points="28,2 24,14 32,14" fill="#38bdf8" />
        </svg>
      </div>

      {/* Center Blue Dot */}
      <div className="relative z-10 w-5 h-5 bg-sky-500 rounded-full border-[2.5px] border-white shadow-[0_0_12px_rgba(56,189,248,0.9)]" />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Compass Button — GMaps style:
// - Tap once: locks map to North-Up (flat view facing North)
// - Tap again: switches back to Local POV (facing where user is seeing, with 3D tilt)
// - Needle rotates dynamically to show True North relative to phone/POV
// ─────────────────────────────────────────────────────────────────
function CompassButton({
  mapHeading,
  deviceHeading = 0,
  isNavigating = false,
  riderHeading = 0,
  compassMode = 'heading_up',
  onToggle,
}: {
  mapHeading: number;
  deviceHeading?: number;
  isNavigating?: boolean;
  riderHeading?: number;
  compassMode?: 'heading_up' | 'north_up';
  onToggle: () => void;
}) {
  // If in North-Up mode, map is fixed North, needle points straight Up (0deg).
  // If in Heading-Up (Local POV), needle counter-rotates by -heading so red N points to true North.
  const activeHeading = compassMode === 'north_up'
    ? 0
    : (mapHeading !== 0 ? mapHeading : (isNavigating && riderHeading !== 0 ? riderHeading : (deviceHeading || 0)));

  const rotationDeg = -activeHeading;

  return (
    <button
      type="button"
      onClick={onToggle}
      title={
        compassMode === 'heading_up'
          ? 'Orient North (Tap to face North)'
          : 'Follow Point of View (Tap to face direction of travel)'
      }
      aria-label="Compass mode toggle"
      className={`w-11 h-11 sm:w-10 sm:h-10 rounded-full shadow-2xl flex items-center justify-center active:scale-90 cursor-pointer border transition-all duration-200 ${
        compassMode === 'heading_up'
          ? 'bg-slate-900/95 hover:bg-slate-800 border-slate-700/80 shadow-black/70'
          : 'bg-white hover:bg-slate-100 border-slate-300 shadow-slate-950/20'
      }`}
    >
      {/* Compass Needle with smooth spring rotation */}
      <div
        className="w-7 h-7 relative flex items-center justify-center pointer-events-none select-none"
        style={{
          transform: `rotate(${rotationDeg}deg)`,
          transition: 'transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)',
        }}
      >
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          {/* North needle: Bright Google Red */}
          <polygon points="14,3 10,14 14,12 18,14" fill="#EA4335" />
          {/* South needle: Clean crisp Silver */}
          <polygon points="14,25 10,14 14,16 18,14" fill={compassMode === 'heading_up' ? '#CBD5E1' : '#64748B'} />
          {/* North "N" mark */}
          <text
            x="14"
            y="9"
            textAnchor="middle"
            fill="#FFFFFF"
            fontSize="5"
            fontWeight="900"
            fontFamily="system-ui, -apple-system, sans-serif"
          >
            N
          </text>
          {/* Pivot Dot */}
          <circle cx="14" cy="14" r="2.2" fill={compassMode === 'heading_up' ? '#0F172A' : '#334155'} stroke="#F8FAFC" strokeWidth="1" />
        </svg>
      </div>
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────
// Inner Google Maps Controller: Polylines, bounds, camera, clicks
// ─────────────────────────────────────────────────────────────────
function GoogleMapInner({
  origin,
  destination,
  activeInput = 'origin',
  routePath,
  alternateRoutePath,
  selectedRouteType = 'shortest',
  onSelectRouteType,
  traveledIndex = 0,
  gpsPosition,
  deviceHeading = 0,
  theme = 'dark',
  mode = 'shortest',
  isFollowingCamera = true,
  isNavigating = false,
  onSelectOrigin,
  onSelectDestination,
  onMapClick,
  onRecenter,
}: MapContainerProps) {
  const map = useMap();
  const [locating, setLocating] = useState(false);
  const [mapHeading, setMapHeading] = useState(0);
  const [compassMode, setCompassMode] = useState<'heading_up' | 'north_up'>('heading_up');
  const containerRef = useRef<HTMLDivElement | null>(null);
  const prevIsNavigatingRef = useRef(false);

  // When navigation starts, automatically enter heading_up (Local POV) mode
  useEffect(() => {
    if (isNavigating) {
      setCompassMode('heading_up');
    }
  }, [isNavigating]);

  // References to Google Maps Polyline instances
  const polylineTraveledRef = useRef<google.maps.Polyline | null>(null);
  const polylineRemainingCasingRef = useRef<google.maps.Polyline | null>(null);
  const polylineRemainingRef = useRef<google.maps.Polyline | null>(null);
  const polylineAlternateRef = useRef<google.maps.Polyline | null>(null);
  const prevRouteKeyRef = useRef<string>('');
  const currentZoomRef = useRef<number>(13);

  const activeThemeStyle = useMemo(() => {
    return theme === 'dark' ? darkMapStyle : lightMapStyle;
  }, [theme]);

  // Apply map styles dynamically on theme change
  useEffect(() => {
    if (map && activeThemeStyle) {
      map.setOptions({ styles: activeThemeStyle });
    }
  }, [map, activeThemeStyle]);

  // Connect Origin → Backend Route Road Coordinates → Destination Pin seamlessly
  const fullConnectedPath = useMemo(() => {
    if (!routePath || routePath.length === 0) return [];
    const pts: LatLngType[] = [...routePath];
    if (origin) {
      const first = pts[0];
      const distFromOrigin = haversineMeters(origin.lat, origin.lng, first[0], first[1]);
      if (distFromOrigin > 1) pts.unshift([origin.lat, origin.lng]);
    }
    if (destination) {
      const last = pts[pts.length - 1];
      const distToDest = haversineMeters(destination.lat, destination.lng, last[0], last[1]);
      if (distToDest > 1) pts.push([destination.lat, destination.lng]);
    }
    return pts;
  }, [routePath, origin, destination]);

  // Connect Alternate route seamlessly
  const fullConnectedAlternatePath = useMemo(() => {
    if (!alternateRoutePath || alternateRoutePath.length === 0) return [];
    const pts: LatLngType[] = [...alternateRoutePath];
    if (origin) {
      const first = pts[0];
      const distFromOrigin = haversineMeters(origin.lat, origin.lng, first[0], first[1]);
      if (distFromOrigin > 1) pts.unshift([origin.lat, origin.lng]);
    }
    if (destination) {
      const last = pts[pts.length - 1];
      const distToDest = haversineMeters(destination.lat, destination.lng, last[0], last[1]);
      if (distToDest > 1) pts.push([destination.lat, destination.lng]);
    }
    return pts;
  }, [alternateRoutePath, origin, destination]);

  // How many extra points were prepended to fullConnectedPath before the raw route points
  const pathPrefixOffset = useMemo(() => {
    if (!routePath || routePath.length === 0 || !origin) return 0;
    const first = routePath[0];
    const dist = Math.abs(origin.lat - first[0]) + Math.abs(origin.lng - first[1]);
    // If origin was prepended (dist > tiny epsilon in degrees), offset is 1
    return dist > 0.00001 ? 1 : 0;
  }, [routePath, origin]);

  // Split route into Traveled vs Remaining for Google Maps progression
  // traveledIndex indexes into routeData.path, so we correct for the origin prefix
  const { traveledCoords, remainingCoords } = useMemo(() => {
    if (!fullConnectedPath || fullConnectedPath.length === 0) {
      return { traveledCoords: [], remainingCoords: [] };
    }
    if (!isNavigating || traveledIndex <= 0) {
      return { traveledCoords: [], remainingCoords: fullConnectedPath };
    }
    // Adjust for the origin prefix that was prepended to fullConnectedPath
    const adjustedIdx = Math.min(traveledIndex + pathPrefixOffset, fullConnectedPath.length - 1);
    const traveled = fullConnectedPath.slice(0, adjustedIdx + 1);
    const remaining = fullConnectedPath.slice(adjustedIdx);
    return { traveledCoords: traveled, remainingCoords: remaining };
  }, [fullConnectedPath, isNavigating, traveledIndex, pathPrefixOffset]);

  // ─── Zoom-change listener: track heading + update polyline weights ───
  useEffect(() => {
    if (!map) return;

    const updateWeights = () => {
      const zoom = map.getZoom() ?? 13;
      currentZoomRef.current = zoom;
      const w = getStrokeWeights(zoom);

      if (polylineRemainingCasingRef.current) {
        polylineRemainingCasingRef.current.setOptions({ strokeWeight: w.casing });
      }
      if (polylineRemainingRef.current) {
        polylineRemainingRef.current.setOptions({ strokeWeight: w.foreground });
      }
      if (polylineTraveledRef.current) {
        polylineTraveledRef.current.setOptions({ strokeWeight: Math.max(2, w.foreground - 1) });
      }
      if (polylineAlternateRef.current) {
        polylineAlternateRef.current.setOptions({ strokeWeight: w.alternate });
      }
    };

    const updateHeading = () => {
      setMapHeading(map.getHeading() ?? 0);
    };

    const zoomListener = map.addListener('zoom_changed', updateWeights);
    const headingListener = map.addListener('heading_changed', updateHeading);
    // Initialize
    updateWeights();
    updateHeading();

    return () => {
      google.maps.event.removeListener(zoomListener);
      google.maps.event.removeListener(headingListener);
    };
  }, [map]);

  // ─── Map heading follow during navigation (GMaps-style) ───
  // When in 'heading_up' (Local POV) mode with camera follow:
  // Smoothly rotate map to face direction of travel + 30-deg perspective tilt.
  // When in 'north_up' mode or navigation ends: lock map heading to 0 and flat view.
  useEffect(() => {
    if (!map) return;
    const riderHeading = gpsPosition?.heading ?? deviceHeading ?? 0;

    if (isNavigating && isFollowingCamera && compassMode === 'heading_up' && riderHeading !== null) {
      // Smoothly rotate map to rider heading + slight tilt for perspective
      map.setHeading(riderHeading);
      map.setTilt(30);
    } else if (compassMode === 'north_up') {
      map.setHeading(0);
      map.setTilt(0);
    } else if (!isNavigating) {
      // Reset to north-up flat view when not navigating
      if (prevIsNavigatingRef.current) {
        map.setHeading(0);
        map.setTilt(0);
      }
    }
    prevIsNavigatingRef.current = isNavigating;
  }, [map, isNavigating, isFollowingCamera, compassMode, gpsPosition?.heading, deviceHeading]);

  // Also reset heading when camera unlinks (user pans map during navigation)
  useEffect(() => {
    if (!map || isNavigating) return;
    map.setHeading(0);
    map.setTilt(0);
  }, [map, isFollowingCamera, isNavigating]);

  // ─── Manage Google Maps Polylines imperatively ───
  useEffect(() => {
    if (!map) return;

    const zoom = currentZoomRef.current;
    const w = getStrokeWeights(zoom);

    const traveledLatLngs = traveledCoords.map(([lat, lng]) => ({ lat, lng }));
    const remainingLatLngs = remainingCoords.map(([lat, lng]) => ({ lat, lng }));
    const alternateLatLngs = fullConnectedAlternatePath.map(([lat, lng]) => ({ lat, lng }));

    let clickListener: google.maps.MapsEventListener | null = null;

    // 1. Alternate Route Polyline (ghost line, clickable to switch)
    const alternateType = selectedRouteType === 'shortest' ? 'dynamic' : 'shortest';
    const altColor = alternateType === 'dynamic' ? '#f472b6' : '#38bdf8';

    if (alternateLatLngs.length > 1 && !isNavigating) {
      if (!polylineAlternateRef.current) {
        polylineAlternateRef.current = new google.maps.Polyline({
          strokeColor: altColor,
          strokeOpacity: 0.45,
          strokeWeight: w.alternate,
          geodesic: true,
          zIndex: 12,
          clickable: true,
          map,
        });
      } else {
        polylineAlternateRef.current.setOptions({
          strokeColor: altColor,
          strokeOpacity: 0.45,
          strokeWeight: w.alternate,
          geodesic: true,
        });
      }
      polylineAlternateRef.current.setPath(alternateLatLngs);
      polylineAlternateRef.current.setMap(map);

      clickListener = polylineAlternateRef.current.addListener('click', () => {
        if (onSelectRouteType) onSelectRouteType(alternateType);
      });
    } else if (polylineAlternateRef.current) {
      polylineAlternateRef.current.setMap(null);
    }

    // 2. Traveled Polyline (greyed out — only shown while navigating and index > 0)
    if (traveledLatLngs.length > 1 && isNavigating) {
      if (!polylineTraveledRef.current) {
        polylineTraveledRef.current = new google.maps.Polyline({
          strokeColor: '#64748b',
          strokeOpacity: 0.5,
          strokeWeight: Math.max(2, w.foreground - 1),
          geodesic: true,
          zIndex: 10,
          map,
        });
      } else {
        polylineTraveledRef.current.setOptions({
          strokeWeight: Math.max(2, w.foreground - 1),
          geodesic: true,
          strokeOpacity: 0.5,
        });
      }
      polylineTraveledRef.current.setPath(traveledLatLngs);
      polylineTraveledRef.current.setMap(map);
    } else {
      // Always hide traveled line when not navigating or no progress yet
      if (polylineTraveledRef.current) {
        polylineTraveledRef.current.setMap(null);
      }
    }

    // 3. Remaining Active Polyline — dark casing + vibrant foreground
    if (remainingLatLngs.length > 1) {
      // Casing (outline)
      if (!polylineRemainingCasingRef.current) {
        polylineRemainingCasingRef.current = new google.maps.Polyline({
          strokeColor: '#0f172a',
          strokeOpacity: 0.9,
          strokeWeight: w.casing,
          geodesic: true,
          zIndex: 20,
          map,
        });
      } else {
        polylineRemainingCasingRef.current.setOptions({
          strokeWeight: w.casing,
          geodesic: true,
        });
      }
      polylineRemainingCasingRef.current.setPath(remainingLatLngs);
      polylineRemainingCasingRef.current.setMap(map);

      // Foreground (colour)
      const activeColor = selectedRouteType === 'dynamic' ? '#f472b6' : '#38bdf8';
      if (!polylineRemainingRef.current) {
        polylineRemainingRef.current = new google.maps.Polyline({
          strokeColor: activeColor,
          strokeOpacity: 1.0,
          strokeWeight: w.foreground,
          geodesic: true,
          zIndex: 22,
          map,
        });
      } else {
        polylineRemainingRef.current.setOptions({
          strokeColor: activeColor,
          strokeWeight: w.foreground,
          geodesic: true,
        });
      }
      polylineRemainingRef.current.setPath(remainingLatLngs);
      polylineRemainingRef.current.setMap(map);
    } else {
      if (polylineRemainingCasingRef.current) polylineRemainingCasingRef.current.setMap(null);
      if (polylineRemainingRef.current) polylineRemainingRef.current.setMap(null);
    }

    return () => {
      if (clickListener) google.maps.event.removeListener(clickListener);
    };
  }, [map, traveledCoords, remainingCoords, fullConnectedAlternatePath, selectedRouteType, isNavigating, onSelectRouteType]);

  // Clean up polylines on unmount
  useEffect(() => {
    return () => {
      if (polylineTraveledRef.current) polylineTraveledRef.current.setMap(null);
      if (polylineRemainingCasingRef.current) polylineRemainingCasingRef.current.setMap(null);
      if (polylineRemainingRef.current) polylineRemainingRef.current.setMap(null);
      if (polylineAlternateRef.current) polylineAlternateRef.current.setMap(null);
    };
  }, []);

  // Auto-fit route bounds when a new route is loaded
  useEffect(() => {
    if (!map || fullConnectedPath.length < 2 || isNavigating) return;

    const firstPt = fullConnectedPath[0];
    const lastPt = fullConnectedPath[fullConnectedPath.length - 1];
    const routeKey = `${firstPt[0]},${firstPt[1]}->${lastPt[0]},${lastPt[1]}`;
    if (prevRouteKeyRef.current === routeKey) return;
    prevRouteKeyRef.current = routeKey;

    try {
      const bounds = new google.maps.LatLngBounds();
      fullConnectedPath.forEach(([lat, lng]) => bounds.extend({ lat, lng }));
      map.fitBounds(bounds, { top: 150, bottom: 220, left: 60, right: 60 });
    } catch (e) {
      console.warn('fitBounds error:', e);
    }
  }, [map, fullConnectedPath, isNavigating]);

  // Global fit-route-bounds event listener
  useEffect(() => {
    const handleFitBounds = () => {
      if (!map || fullConnectedPath.length < 2) return;
      try {
        const bounds = new google.maps.LatLngBounds();
        fullConnectedPath.forEach(([lat, lng]) => bounds.extend({ lat, lng }));
        map.fitBounds(bounds, { top: 150, bottom: 220, left: 60, right: 60 });
      } catch (e) {}
    };
    window.addEventListener('fit-route-bounds', handleFitBounds);
    return () => window.removeEventListener('fit-route-bounds', handleFitBounds);
  }, [map, fullConnectedPath]);

  // Global recenter listener
  useEffect(() => {
    const handleGlobalRecenter = () => {
      if (!map) return;
      const zoomLevel = isNavigating ? 18 : 16;
      if (gpsPosition?.lat && gpsPosition?.lng) {
        map.panTo({ lat: gpsPosition.lat, lng: gpsPosition.lng });
        map.setZoom(zoomLevel);
      } else if (typeof window !== 'undefined' && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            map.panTo({ lat: pos.coords.latitude, lng: pos.coords.longitude });
            map.setZoom(zoomLevel);
          },
          undefined,
          { enableHighAccuracy: true, timeout: 5000, maximumAge: 3000 }
        );
      }
    };
    window.addEventListener('recenter-map', handleGlobalRecenter);
    return () => window.removeEventListener('recenter-map', handleGlobalRecenter);
  }, [map, gpsPosition, isNavigating]);

  // Camera follow during active navigation
  useEffect(() => {
    if (!map || !isNavigating || !isFollowingCamera) return;
    if (gpsPosition?.lat && gpsPosition?.lng) {
      map.panTo({ lat: gpsPosition.lat, lng: gpsPosition.lng });
    }
  }, [map, gpsPosition, isNavigating, isFollowingCamera]);

  // Handle map click events to set Origin / Destination
  useEffect(() => {
    if (!map) return;
    const listener = map.addListener('click', (e: google.maps.MapMouseEvent) => {
      if (!e.latLng) return;
      const lat = Number(e.latLng.lat().toFixed(5));
      const lng = Number(e.latLng.lng().toFixed(5));
      const loc: Point = { lat, lng, address: `${lat}, ${lng}`, name: `${lat}, ${lng}` };

      if (onMapClick) onMapClick([lat, lng]);

      if (activeInput === 'destination' && onSelectDestination) {
        onSelectDestination(loc);
      } else if (activeInput === 'origin' && onSelectOrigin) {
        onSelectOrigin(loc);
      } else if (!origin && onSelectOrigin) {
        onSelectOrigin(loc);
      } else if (!destination && onSelectDestination) {
        onSelectDestination(loc);
      } else if (onSelectDestination) {
        onSelectDestination(loc);
      }
    });
    return () => google.maps.event.removeListener(listener);
  }, [map, activeInput, origin, destination, onSelectOrigin, onSelectDestination, onMapClick]);

  // Recenter button click handler
  const handleRecenterClick = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.stopPropagation();
      e.preventDefault();
      if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(10);
      if (onRecenter) onRecenter();
      if (!map) return;

      const zoomLevel = isNavigating ? 18 : 16;
      if (gpsPosition?.lat && gpsPosition?.lng) {
        map.panTo({ lat: gpsPosition.lat, lng: gpsPosition.lng });
        map.setZoom(zoomLevel);
        return;
      }

      if (typeof window !== 'undefined' && navigator.geolocation) {
        setLocating(true);
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            setLocating(false);
            map.panTo({ lat: pos.coords.latitude, lng: pos.coords.longitude });
            map.setZoom(zoomLevel);
          },
          () => {
            setLocating(false);
            if (origin) map.panTo({ lat: origin.lat, lng: origin.lng });
            else if (destination) map.panTo({ lat: destination.lat, lng: destination.lng });
          },
          { enableHighAccuracy: true, timeout: 6000, maximumAge: 3000 }
        );
      } else if (origin) {
        map.panTo({ lat: origin.lat, lng: origin.lng });
      }
    },
    [map, gpsPosition, origin, destination, isNavigating, onRecenter]
  );

  // Compass toggle — GMaps style:
  // - Tap once: locks map to North-Up (flat view facing North)
  // - Tap again: switches back to Local POV (where user is seeing / facing, with 3D tilt)
  const handleCompassToggle = useCallback(() => {
    if (!map) return;
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(10);

    const riderHeading = gpsPosition?.heading ?? deviceHeading ?? 0;

    if (compassMode === 'heading_up') {
      // Tap 1: Switch to North-Up flat view
      setCompassMode('north_up');
      map.setHeading(0);
      map.setTilt(0);
      setMapHeading(0);
    } else {
      // Tap 2: Switch back to Local POV (facing where user is seeing/traveling)
      setCompassMode('heading_up');
      if (riderHeading !== null) {
        map.setHeading(riderHeading);
        if (isNavigating) {
          map.setTilt(30);
        }
        setMapHeading(riderHeading);
      }
      if (gpsPosition?.lat && gpsPosition?.lng) {
        map.panTo({ lat: gpsPosition.lat, lng: gpsPosition.lng });
      }
    }
  }, [map, compassMode, isNavigating, gpsPosition, deviceHeading]);

  const isOriginMyLocation = useMemo(() => {
    if (!origin) return false;
    const name = (origin.name || '').toLowerCase();
    const addr = (origin.address || '').toLowerCase();
    return (
      name.includes('my location') ||
      addr.includes('my location') ||
      name.includes('current location') ||
      addr.includes('current location')
    );
  }, [origin]);

  // Bottom offset for the floating button stack (compass + recenter)
  // These must clear above any drawer/footer that is currently visible
  const buttonStackBottomClass = isNavigating
    ? 'bottom-[108px]'       // above NavigationFooter (~88px) + gap
    : fullConnectedPath.length > 0
    ? 'bottom-[185px]'       // above BottomActionBar (~168px) + gap
    : 'bottom-[28px]';       // idle — near bottom edge

  const riderCoord = gpsPosition?.lat && gpsPosition?.lng ? gpsPosition : null;
  const riderHeading = gpsPosition?.heading ?? deviceHeading ?? 0;

  return (
    <>
      {/* Origin Marker */}
      {origin && !isNavigating && !isOriginMyLocation && (
        <AdvancedMarker
          position={{ lat: origin.lat, lng: origin.lng }}
          title={origin.name || 'Origin'}
          zIndex={40}
        >
          <div className="flex flex-col items-center pointer-events-none select-none">
            {origin.name && (
              <div className="mb-1 max-w-[180px] truncate px-2.5 py-0.5 bg-slate-900/95 text-sky-400 text-[11px] font-semibold font-sans rounded-full shadow-lg border border-slate-700/90 whitespace-nowrap">
                {origin.name}
              </div>
            )}
            <Pin background="#1A73E8" borderColor="#1557B0" glyphColor="#FFFFFF" scale={1.1} />
          </div>
        </AdvancedMarker>
      )}

      {/* Destination Marker */}
      {destination && (
        <AdvancedMarker
          position={{ lat: destination.lat, lng: destination.lng }}
          title={destination.name || 'Destination'}
          zIndex={50}
        >
          <div className="flex flex-col items-center pointer-events-none select-none">
            {destination.name && (
              <div className="mb-1 max-w-[180px] truncate px-2.5 py-0.5 bg-slate-900/95 text-rose-400 text-[11px] font-semibold font-sans rounded-full shadow-lg border border-slate-700/90 whitespace-nowrap">
                {destination.name}
              </div>
            )}
            <Pin background="#EA4335" borderColor="#B31412" glyphColor="#FFFFFF" scale={1.2} />
          </div>
        </AdvancedMarker>
      )}

      {/* Rider GPS Position & Orientation Arrow */}
      {riderCoord && (
        <AdvancedMarker
          position={{ lat: riderCoord.lat, lng: riderCoord.lng }}
          zIndex={1000}
          title={`Rider (${Math.round(riderHeading)}°)`}
        >
          <RiderMarkerIcon heading={riderHeading} isNavigating={isNavigating} />
        </AdvancedMarker>
      )}

      {/*
       * ── Floating button stack: Compass (top) + Recenter (bottom) ──
       * Single container so they always align together and reposition as one unit.
       * Compass is ALWAYS visible — allows user to see/reset north at any time.
       * Recenter is hidden during navigation (NavigationFooter has its own).
       */}
      <div
        ref={containerRef}
        className={`fixed right-4 sm:right-6 z-[1001] flex flex-col items-center gap-2 transition-all duration-300 pointer-events-auto ${buttonStackBottomClass} sm:bottom-6`}
        onMouseDown={(e) => e.stopPropagation()}
        onTouchStart={(e) => e.stopPropagation()}
      >
        {/* ── Compass "N" Button — always visible ── */}
        <CompassButton
          mapHeading={mapHeading}
          deviceHeading={deviceHeading}
          isNavigating={isNavigating}
          riderHeading={riderHeading}
          compassMode={compassMode}
          onToggle={handleCompassToggle}
        />

        {/* ── Recenter / GPS Button — hidden during navigation ── */}
        {!isNavigating && (
          <button
            type="button"
            onClick={handleRecenterClick}
            onMouseDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
            title="Re-center on my location"
            className="w-11 h-11 sm:w-10 sm:h-10 bg-[#0f172a] hover:bg-slate-800 active:scale-90 text-sky-400 border border-slate-700/80 rounded-full shadow-2xl transition-all flex items-center justify-center cursor-pointer"
          >
            {locating ? (
              <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
            ) : (
              /* Custom GPS target / crosshair icon */
              <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
                <circle cx="11" cy="11" r="8" stroke="#38bdf8" strokeWidth="1.5" />
                <circle cx="11" cy="11" r="3" fill="#38bdf8" />
                <line x1="11" y1="1" x2="11" y2="5" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="11" y1="17" x2="11" y2="21" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="1" y1="11" x2="5" y2="11" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="17" y1="11" x2="21" y2="11" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            )}
          </button>
        )}
      </div>
    </>
  );
}

// ─────────────────────────────────────────────────────────────────
// Root exported component — wraps GMap APIProvider
// ─────────────────────────────────────────────────────────────────
export const GoogleMapContainer: React.FC<MapContainerProps> = (props) => {
  const [defaultCenter] = useState<{ lat: number; lng: number }>({
    lat: 12.9716,
    lng: 77.5946,
  });

  return (
    <div className="h-full w-full relative z-0 touch-action-manipulation select-none overflow-hidden bg-slate-950">
      <APIProvider apiKey={GOOGLE_MAPS_API_KEY} libraries={['places', 'geometry', 'routes', 'marker']}>
        <GMap
          defaultCenter={defaultCenter}
          defaultZoom={13}
          mapId="DEMO_MAP_ID"
          gestureHandling="greedy"
          disableDefaultUI={true}
          style={{ width: '100%', height: '100%' }}
        >
          <GoogleMapInner {...props} />
        </GMap>
      </APIProvider>
    </div>
  );
};

export default GoogleMapContainer;
