'use client';

import { GOOGLE_MAPS_API_KEY } from '@/lib/mapsKey';
import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  APIProvider,
  Map as GMap,
  useMap,
  useMapsLibrary,
  AdvancedMarker,
  Pin,
  RenderingType,
} from '@vis.gl/react-google-maps';
import { Loader2 } from 'lucide-react';
import { LatLng as LatLngType, Point, GPSPosition, RouteMode, NavPose, ManeuverType } from '@/lib/types';
import { haversineMeters } from '@/lib/geo';
import { RouteIndex, destinationPoint, lerpAngle, sliceRoute } from '@/lib/navigation';
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
  // ── Turn-by-turn navigation ──
  navPose?: NavPose | null;               // rider position snapped to the route
  routeIndex?: RouteIndex | null;         // indexed active route (for trimming at the rider)
  maneuverAlong?: number | null;          // along-route position of the next turn
  maneuverType?: ManeuverType | null;
  distanceToManeuver?: number;
  onUserPan?: () => void;                 // user dragged/zoomed the map during navigation
}

// Navigation-mode colours (route blue, as in navigation apps)
const NAV_ROUTE = '#4285F4';
const NAV_ROUTE_CASING = '#1967D2';
const NAV_TILT = 50;

/** Camera zoom for the rider's speed, closer in when a turn is near. */
function navZoom(speedMps: number, distToTurn: number): number {
  const kmh = speedMps * 3.6;
  let z = kmh < 20 ? 18 : kmh < 40 ? 17.6 : kmh < 60 ? 17.1 : 16.4;
  if (distToTurn < 200) z = Math.max(z, 18.2);
  return z;
}

/** Ground metres per CSS pixel at a zoom level and latitude (256 px tiles). */
function metersPerPixel(zoom: number, lat: number): number {
  return (156543.03392 * Math.cos((lat * Math.PI) / 180)) / Math.pow(2, zoom);
}

/** Navigation arrow (rider puck) element: blue chevron with a white outline. */
function createNavPuckElement(): { root: HTMLDivElement; arrow: HTMLDivElement } {
  const root = document.createElement('div');
  root.style.cssText = 'transform: translateY(50%); pointer-events: none;';
  const arrow = document.createElement('div');
  arrow.style.cssText =
    'width:44px;height:44px;display:flex;align-items:center;justify-content:center;' +
    'filter: drop-shadow(0 2px 3px rgba(0,0,0,0.35)); will-change: transform;';
  arrow.innerHTML =
    '<svg width="40" height="40" viewBox="0 0 40 40">' +
    '<circle cx="20" cy="20" r="18" fill="rgba(66,133,244,0.18)"/>' +
    '<path d="M20 5 L32 33 L20 26.5 L8 33 Z" fill="#1A73E8" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/>' +
    '</svg>';
  root.appendChild(arrow);
  return { root, arrow };
}


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
  navPose = null,
  routeIndex = null,
  maneuverAlong = null,
  maneuverType = null,
  distanceToManeuver = Infinity,
  onUserPan,
}: MapContainerProps) {
  const map = useMap();
  const markerLib = useMapsLibrary('marker');

  // ── Navigation camera / puck state (mutable, driven by requestAnimationFrame) ──
  const navAnimRef = useRef<{
    from: { lat: number; lng: number; bearing: number; along: number };
    to: { lat: number; lng: number; bearing: number; along: number };
    cur: { lat: number; lng: number; bearing: number; along: number };
    start: number;
    duration: number;
    lastPoseAt: number;
    speed: number;
  } | null>(null);
  const camRef = useRef<{ lat: number; lng: number; heading: number; zoom: number; tilt: number } | null>(null);
  const navPuckRef = useRef<google.maps.marker.AdvancedMarkerElement | null>(null);
  const navPuckArrowRef = useRef<HTMLDivElement | null>(null);
  const maneuverArrowRef = useRef<google.maps.Polyline | null>(null);
  const lastTrimAlongRef = useRef<number>(-1);
  const followingRef = useRef(isFollowingCamera);
  const recoverUntilRef = useRef(0);
  const navPropsRef = useRef({ routeIndex, distanceToManeuver });
  navPropsRef.current = { routeIndex, distanceToManeuver };
  const [locating, setLocating] = useState(false);
  const [mapHeading, setMapHeading] = useState(0);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // References to Google Maps Polyline instances
  const polylineTraveledRef = useRef<google.maps.Polyline | null>(null);
  const polylineRemainingCasingRef = useRef<google.maps.Polyline | null>(null);
  const polylineRemainingRef = useRef<google.maps.Polyline | null>(null);
  const polylineAlternateRef = useRef<google.maps.Polyline | null>(null);
  const accessLineOriginRef = useRef<google.maps.Polyline | null>(null);
  const accessLineDestRef = useRef<google.maps.Polyline | null>(null);
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

  // The route line is exactly the backend's road-following path, which already
  // starts and ends on the road nearest each pin. The gap between a pin (which may
  // sit inside a building) and the road is drawn separately as a dotted access line,
  // never as a solid straight segment across buildings.
  const fullConnectedPath = useMemo<LatLngType[]>(
    () => (routePath && routePath.length > 0 ? routePath : []),
    [routePath]
  );

  const fullConnectedAlternatePath = useMemo<LatLngType[]>(
    () => (alternateRoutePath && alternateRoutePath.length > 0 ? alternateRoutePath : []),
    [alternateRoutePath]
  );

  // Dotted pin → road access lines
  useEffect(() => {
    if (!map) return;

    const dotted = (from: LatLngType, to: LatLngType): google.maps.PolylineOptions => ({
      path: [
        { lat: from[0], lng: from[1] },
        { lat: to[0], lng: to[1] },
      ],
      strokeOpacity: 0,
      icons: [
        {
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: '#64748b',
            fillOpacity: 1,
            strokeOpacity: 0,
            scale: 2.5,
          },
          offset: '0',
          repeat: '10px',
        },
      ],
      zIndex: 9,
      clickable: false,
      map,
    });

    const update = (
      ref: React.MutableRefObject<google.maps.Polyline | null>,
      pin: Point | null | undefined,
      roadPoint: LatLngType | undefined
    ) => {
      const show =
        pin && roadPoint && haversineMeters(pin.lat, pin.lng, roadPoint[0], roadPoint[1]) > 3;
      if (show) {
        const opts = dotted([pin!.lat, pin!.lng], roadPoint!);
        if (ref.current) ref.current.setOptions(opts);
        else ref.current = new google.maps.Polyline(opts);
      } else if (ref.current) {
        ref.current.setMap(null);
        ref.current = null;
      }
    };

    update(accessLineOriginRef, isNavigating ? null : origin, fullConnectedPath[0]);
    update(accessLineDestRef, destination, fullConnectedPath[fullConnectedPath.length - 1]);
  }, [map, origin, destination, fullConnectedPath, isNavigating]);

  useEffect(() => {
    return () => {
      accessLineOriginRef.current?.setMap(null);
      accessLineDestRef.current?.setMap(null);
    };
  }, []);

  // Split route into Traveled vs Remaining for Google Maps progression
  const { traveledCoords, remainingCoords } = useMemo<{ traveledCoords: LatLngType[]; remainingCoords: LatLngType[] }>(() => {
    if (!fullConnectedPath || fullConnectedPath.length === 0) {
      return { traveledCoords: [], remainingCoords: [] };
    }
    // During navigation the route behind the rider is simply not drawn; the
    // animation loop below trims the remaining line exactly at the rider arrow.
    return { traveledCoords: [], remainingCoords: fullConnectedPath };
  }, [fullConnectedPath]);

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
          strokeColor: isNavigating ? NAV_ROUTE_CASING : '#0f172a',
          strokeOpacity: 0.9,
          strokeWeight: w.casing,
          geodesic: true,
          zIndex: 20,
          map,
        });
      } else {
        polylineRemainingCasingRef.current.setOptions({
          strokeColor: isNavigating ? NAV_ROUTE_CASING : '#0f172a',
          strokeWeight: w.casing,
          geodesic: true,
        });
      }
      polylineRemainingCasingRef.current.setPath(remainingLatLngs);
      polylineRemainingCasingRef.current.setMap(map);
      lastTrimAlongRef.current = -1; // let the navigation loop re-trim at the rider

      // Foreground (colour)
      const activeColor = isNavigating ? NAV_ROUTE : selectedRouteType === 'dynamic' ? '#f472b6' : '#38bdf8';
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
        map.moveCamera({ tilt: 0, heading: 0 });
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
      if (!map || isNavigating) return;
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

  // ═════════════════════════════════════════════════════════════════
  // Turn-by-turn navigation: camera, rider arrow, route trimming
  // ═════════════════════════════════════════════════════════════════

  const onUserPanRef = useRef(onUserPan);
  onUserPanRef.current = onUserPan;
  const lastRouteIndexRef = useRef<RouteIndex | null>(null);

  // Resuming "follow" (Re-centre) eases the camera back instead of jumping.
  useEffect(() => {
    if (isFollowingCamera && !followingRef.current) recoverUntilRef.current = performance.now() + 1000;
    followingRef.current = isFollowingCamera;
  }, [isFollowingCamera]);

  // Start / stop of navigation
  const wasNavigatingRef = useRef(false);
  useEffect(() => {
    if (!map) return;
    if (isNavigating && !wasNavigatingRef.current) {
      navAnimRef.current = null;
      camRef.current = null;
      recoverUntilRef.current = performance.now() + 1400; // glide into the 3D view
    }
    if (!isNavigating && wasNavigatingRef.current) {
      navAnimRef.current = null;
      camRef.current = null;
      map.moveCamera({ tilt: 0, heading: 0 });
    }
    wasNavigatingRef.current = isNavigating;
  }, [map, isNavigating]);

  // Each new rider pose becomes an animation target (smooth glide between GPS fixes)
  useEffect(() => {
    if (!isNavigating || !navPose) return;
    const now = performance.now();
    const target = { lat: navPose.lat, lng: navPose.lng, bearing: navPose.bearing, along: navPose.along };
    const a = navAnimRef.current;
    const newRoute = lastRouteIndexRef.current !== routeIndex;
    lastRouteIndexRef.current = routeIndex;
    if (!a || haversineMeters(a.cur.lat, a.cur.lng, target.lat, target.lng) > 250) {
      navAnimRef.current = {
        from: { ...target }, to: target, cur: { ...target },
        start: now, duration: 1, lastPoseAt: now, speed: navPose.speedMps,
      };
      return;
    }
    const from = { ...a.cur };
    if (newRoute) from.along = target.along; // progress on a new route isn't comparable
    navAnimRef.current = {
      from, to: target, cur: a.cur, start: now,
      duration: Math.min(1500, Math.max(300, now - a.lastPoseAt)),
      lastPoseAt: now, speed: navPose.speedMps,
    };
  }, [navPose, isNavigating, routeIndex]);

  // Rider arrow (imperative marker, moved every frame)
  useEffect(() => {
    if (!map || !markerLib || !isNavigating) return;
    const { root, arrow } = createNavPuckElement();
    const marker = new markerLib.AdvancedMarkerElement({ map, content: root, zIndex: 2000 });
    navPuckRef.current = marker;
    navPuckArrowRef.current = arrow;
    return () => {
      marker.map = null;
      navPuckRef.current = null;
      navPuckArrowRef.current = null;
    };
  }, [map, markerLib, isNavigating]);

  // Animation loop: glide the arrow, trim the route at it, drive the camera
  useEffect(() => {
    if (!map || !isNavigating) return;
    let raf = 0;
    let lastTrimAt = 0;
    const lerp = (x: number, y: number, t: number) => x + (y - x) * t;

    const frame = (now: number) => {
      raf = requestAnimationFrame(frame);
      const a = navAnimRef.current;
      if (!a) return;
      const t = Math.min(1, (now - a.start) / a.duration);
      a.cur = {
        lat: lerp(a.from.lat, a.to.lat, t),
        lng: lerp(a.from.lng, a.to.lng, t),
        bearing: lerpAngle(a.from.bearing, a.to.bearing, t),
        along: lerp(a.from.along, a.to.along, t),
      };
      const { routeIndex: idx, distanceToManeuver: dTurn } = navPropsRef.current;

      // Rider arrow: position + direction relative to the (rotated) map
      if (navPuckRef.current) navPuckRef.current.position = { lat: a.cur.lat, lng: a.cur.lng };
      if (navPuckArrowRef.current) {
        const mapHeading = map.getHeading() ?? 0;
        navPuckArrowRef.current.style.transform = `rotate(${a.cur.bearing - mapHeading}deg)`;
      }

      // Remaining route starts under the arrow (throttled)
      if (idx && now - lastTrimAt > 200 && Math.abs(a.cur.along - lastTrimAlongRef.current) > 1) {
        lastTrimAt = now;
        lastTrimAlongRef.current = a.cur.along;
        const rest = sliceRoute(idx, a.cur.along).map(([lat, lng]) => ({ lat, lng }));
        if (rest.length > 1) {
          polylineRemainingRef.current?.setPath(rest);
          polylineRemainingCasingRef.current?.setPath(rest);
        }
      }

      // Camera: heading-up, tilted, arrow in the lower part of the screen
      if (!followingRef.current) {
        camRef.current = null;
        return;
      }
      const h = map.getDiv().clientHeight || 700;
      const center = map.getCenter();
      const cam = camRef.current ?? {
        lat: center?.lat() ?? a.cur.lat,
        lng: center?.lng() ?? a.cur.lng,
        heading: map.getHeading() ?? 0,
        zoom: map.getZoom() ?? 16,
        tilt: map.getTilt() ?? 0,
      };
      const recovering = now < recoverUntilRef.current;
      const k = recovering ? 0.08 : 0.3;
      cam.zoom += (navZoom(a.speed, dTurn) - cam.zoom) * (recovering ? 0.08 : 0.03);
      cam.tilt += (NAV_TILT - cam.tilt) * 0.08;
      // Look ahead of the rider so the arrow sits ~70% down the screen. Only on a
      // vector map: a raster map can't rotate, so the offset would push the rider sideways.
      const canRotate = map.getRenderingType?.() === 'VECTOR';
      const lookAhead = canRotate ? metersPerPixel(cam.zoom, a.cur.lat) * h * 0.22 * 1.35 : 0;
      const ahead = destinationPoint(a.cur.lat, a.cur.lng, a.cur.bearing, lookAhead);
      cam.lat += (ahead.lat - cam.lat) * k;
      cam.lng += (ahead.lng - cam.lng) * k;
      cam.heading = lerpAngle(cam.heading, a.cur.bearing, k);
      camRef.current = cam;
      map.moveCamera({
        center: { lat: cam.lat, lng: cam.lng },
        heading: cam.heading,
        tilt: cam.tilt,
        zoom: cam.zoom,
      });
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, [map, isNavigating]);

  // Dragging / pinching / scrolling the map pauses follow mode (shows Re-centre)
  useEffect(() => {
    if (!map || !isNavigating) return;
    const drag = map.addListener('dragstart', () => onUserPanRef.current?.());
    const div = map.getDiv();
    const wheel = () => onUserPanRef.current?.();
    const touch = (e: TouchEvent) => {
      if (e.touches.length > 1) onUserPanRef.current?.();
    };
    div.addEventListener('wheel', wheel, { passive: true });
    div.addEventListener('touchstart', touch, { passive: true });
    return () => {
      google.maps.event.removeListener(drag);
      div.removeEventListener('wheel', wheel);
      div.removeEventListener('touchstart', touch);
    };
  }, [map, isNavigating]);

  // White turn arrow painted on the road at the next turn
  const turnArrowVisible =
    isNavigating &&
    !!routeIndex &&
    maneuverAlong != null &&
    !!maneuverType &&
    !['arrive', 'depart', 'straight', 'continue'].includes(maneuverType) &&
    distanceToManeuver <= 800;
  useEffect(() => {
    if (!map) return;
    if (!turnArrowVisible || !routeIndex || maneuverAlong == null) {
      maneuverArrowRef.current?.setMap(null);
      maneuverArrowRef.current = null;
      return;
    }
    const seg = sliceRoute(routeIndex, maneuverAlong - 22, maneuverAlong + 18).map(([lat, lng]) => ({ lat, lng }));
    if (seg.length < 2) return;
    if (!maneuverArrowRef.current) {
      maneuverArrowRef.current = new google.maps.Polyline({
        strokeColor: '#ffffff',
        strokeOpacity: 1,
        strokeWeight: 5,
        zIndex: 40,
        clickable: false,
        icons: [
          {
            icon: {
              path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
              scale: 3.4,
              fillColor: '#ffffff',
              fillOpacity: 1,
              strokeColor: NAV_ROUTE_CASING,
              strokeWeight: 1.2,
            },
            offset: '100%',
          },
        ],
        map,
      });
    }
    maneuverArrowRef.current.setPath(seg);
  }, [map, turnArrowVisible, routeIndex, maneuverAlong]);

  useEffect(() => {
    return () => {
      maneuverArrowRef.current?.setMap(null);
    };
  }, []);

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
      {riderCoord && !isNavigating && (
        <AdvancedMarker
          position={{ lat: riderCoord.lat, lng: riderCoord.lng }}
          zIndex={1000}
          title={`Rider (${riderHeading}°)`}
        >
          <RiderMarkerIcon heading={riderHeading} />
        </AdvancedMarker>
      )}

      {/* ── Compass "N" Button (always visible, rotates with map) ── */}
      {!isNavigating && (
      <CompassButton
        mapHeading={mapHeading}
        deviceHeading={deviceHeading ?? 0}
        onReset={handleCompassReset}
        bottomClass={mobileBottomClass}
      />
      )}

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
          renderingType={RenderingType.VECTOR}
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
