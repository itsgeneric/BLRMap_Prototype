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
// Google Maps-style Rider Marker with heading arrow
// ─────────────────────────────────────────────────────────────────
function RiderMarkerIcon({ heading }: { heading: number }) {
  const quantized = Math.round((heading % 360) / 5) * 5;
  return (
    <div className="relative w-10 h-10 flex items-center justify-center pointer-events-none select-none">
      {/* Accuracy pulse ring */}
      <div className="absolute inset-0 bg-sky-500/20 rounded-full animate-ping" />
      {/* Heading cone — points in direction of travel */}
      <div
        className="absolute w-0 h-0"
        style={{
          transform: `rotate(${quantized}deg)`,
          transformOrigin: 'center bottom',
          bottom: '50%',
        }}
      >
        <div
          style={{
            width: 0,
            height: 0,
            borderLeft: '6px solid transparent',
            borderRight: '6px solid transparent',
            borderBottom: '14px solid rgba(56,189,248,0.5)',
            marginLeft: '-6px',
            marginBottom: '-2px',
          }}
        />
      </div>
      {/* Blue dot */}
      <div className="w-5 h-5 bg-sky-500 rounded-full border-[2.5px] border-white shadow-[0_0_14px_rgba(56,189,248,0.95)] z-10 flex items-center justify-center" />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Compass "N" Button — Google Maps style
// ─────────────────────────────────────────────────────────────────
function CompassButton({
  mapHeading,
  deviceHeading,
  onReset,
  bottomClass,
}: {
  mapHeading: number;
  deviceHeading: number;
  onReset: () => void;
  bottomClass: string;
}) {
  // Only show if map is rotated OR we have heading data
  const isRotated = Math.abs(mapHeading) > 1;
  const rotationDeg = -mapHeading; // counter-rotate so "N" always points true north

  return (
    <div
      className={`fixed right-4 sm:right-6 z-[1001] transition-all duration-300 pointer-events-auto ${bottomClass}`}
      style={{ marginBottom: '52px' }} // stack above the recenter button
    >
      <button
        type="button"
        onClick={onReset}
        title="Tap to orient map north"
        className={`w-11 h-11 sm:w-10 sm:h-10 rounded-full shadow-2xl flex items-center justify-center transition-all duration-200 active:scale-90 cursor-pointer border ${
          isRotated
            ? 'bg-white border-slate-200 shadow-black/40'
            : 'bg-[#0f172a] border-slate-700/80 shadow-black/70'
        }`}
        style={{ transform: `rotate(${rotationDeg}deg)` }}
      >
        {/* Compass SVG — red N needle + white S needle */}
        <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
          {/* N needle (red, points to north) */}
          <polygon points="14,4 11,14 14,12 17,14" fill={isRotated ? '#EA4335' : '#38bdf8'} />
          {/* S needle (grey, points south) */}
          <polygon points="14,24 11,14 14,16 17,14" fill={isRotated ? '#9CA3AF' : '#475569'} />
          {/* Center dot */}
          <circle cx="14" cy="14" r="2" fill={isRotated ? '#374151' : '#94a3b8'} />
        </svg>
      </button>
      {/* "N" label underneath when rotated */}
      {isRotated && (
        <div className="text-center mt-0.5">
          <span className="text-[9px] font-black font-mono text-slate-400 tracking-widest">N</span>
        </div>
      )}
    </div>
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
  const containerRef = useRef<HTMLDivElement | null>(null);

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

  // Split route into Traveled vs Remaining for Google Maps progression
  const { traveledCoords, remainingCoords } = useMemo(() => {
    if (!fullConnectedPath || fullConnectedPath.length === 0) {
      return { traveledCoords: [], remainingCoords: [] };
    }
    if (!isNavigating || traveledIndex <= 0) {
      return { traveledCoords: [], remainingCoords: fullConnectedPath };
    }
    const splitIdx = Math.min(traveledIndex, fullConnectedPath.length - 1);
    const traveled = fullConnectedPath.slice(0, splitIdx + 1);
    const remaining = fullConnectedPath.slice(splitIdx);
    return { traveledCoords: traveled, remainingCoords: remaining };
  }, [fullConnectedPath, isNavigating, traveledIndex]);

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

    // 2. Traveled Polyline (greyed out)
    if (traveledLatLngs.length > 1) {
      if (!polylineTraveledRef.current) {
        polylineTraveledRef.current = new google.maps.Polyline({
          strokeColor: '#64748b',
          strokeOpacity: 0.55,
          strokeWeight: Math.max(2, w.foreground - 1),
          geodesic: true,
          zIndex: 10,
          map,
        });
      } else {
        polylineTraveledRef.current.setOptions({
          strokeWeight: Math.max(2, w.foreground - 1),
          geodesic: true,
        });
      }
      polylineTraveledRef.current.setPath(traveledLatLngs);
      polylineTraveledRef.current.setMap(map);
    } else if (polylineTraveledRef.current) {
      polylineTraveledRef.current.setMap(null);
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

  // Compass reset — snap map heading back to North
  const handleCompassReset = useCallback(() => {
    if (!map) return;
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(8);
    map.setHeading(0);
    map.setTilt(0);
    setMapHeading(0);
  }, [map]);

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

  const mobileBottomClass = isNavigating
    ? 'bottom-[94px]'
    : fullConnectedPath.length > 0
    ? 'bottom-[175px]'
    : 'bottom-[24px]';

  const riderCoord = gpsPosition?.lat && gpsPosition?.lng ? gpsPosition : null;
  const riderHeading = gpsPosition?.heading || deviceHeading || 0;

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
          title={`Rider (${riderHeading}°)`}
        >
          <RiderMarkerIcon heading={riderHeading} />
        </AdvancedMarker>
      )}

      {/* ── Compass "N" Button (always visible, rotates with map) ── */}
      <CompassButton
        mapHeading={mapHeading}
        deviceHeading={deviceHeading ?? 0}
        onReset={handleCompassReset}
        bottomClass={mobileBottomClass}
      />

      {/* ── Recenter / GPS Button ── */}
      {!isNavigating && (
        <div
          ref={containerRef}
          className={`fixed right-4 sm:right-6 z-[1000] transition-all duration-300 pointer-events-auto ${mobileBottomClass} sm:bottom-6`}
          onMouseDown={(e) => e.stopPropagation()}
          onTouchStart={(e) => e.stopPropagation()}
        >
          <button
            type="button"
            onClick={handleRecenterClick}
            onMouseDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
            title="Re-center on my location"
            className="w-11 h-11 sm:w-10 sm:h-10 bg-[#0f172a] hover:bg-slate-800 active:scale-90 text-sky-400 border border-slate-700/80 rounded-full shadow-2xl transition-all flex items-center justify-center cursor-pointer"
          >
            {locating ? (
              <Loader2 className="w-4 h-4 sm:w-4 sm:h-4 animate-spin text-sky-400" />
            ) : (
              /* Custom GPS target icon */
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
        </div>
      )}
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
