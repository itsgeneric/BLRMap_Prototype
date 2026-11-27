'use client';

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  APIProvider,
  Map as GMap,
  useMap,
  AdvancedMarker,
  AdvancedMarkerAnchorPoint,
  Pin,
  RenderingType,
  useAdvancedMarkerRef,
} from '@vis.gl/react-google-maps';
import { Loader2 } from 'lucide-react';
import { LatLng as LatLngType, Point, GPSPosition, RouteMode, RoadIncident } from '@/lib/types';
import { darkMapStyle, lightMapStyle } from './googleMapStyles';
import { LongPressDetector } from '@/lib/longPress';

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
  activeIncidents?: RoadIncident[];
  /** while navigating: where to draw the rider (on the road when genuinely on the route), from the navigation engine */
  displayPosition?: { lat: number; lng: number } | null;
  /** the closest point on the route to the rider: the route line is split exactly here */
  routePoint?: { lat: number; lng: number } | null;
  /** a place dropped by press-and-hold (shown as an orange pin until the card is closed) */
  droppedPin?: Point | null;
  /** the rider pressed and held the map at this position */
  onLongPress?: (position: { lat: number; lng: number }) => void;
  onSelectOrigin?: (location: Point) => void;
  onSelectDestination?: (location: Point) => void;
  onMapClick?: (latlng: [number, number]) => void;
  onRecenter?: () => void;
  onCameraUnlink?: () => void;
}

// The project's styled Map ID (Google Cloud Console > Map Management): a vector map whose style has no 3D buildings, so the camera can
// tilt like Google Maps' navigation view while buildings stay flat and the roads stay visible. A Map ID is a public identifier, not a
// secret. Override with NEXT_PUBLIC_GOOGLE_MAP_ID in .env (before `npm run build`). With 'DEMO_MAP_ID' the map has 3D buildings.
const MAP_ID = process.env.NEXT_PUBLIC_GOOGLE_MAP_ID || 'ee3c7f039aa26cded2f28d04';

// Camera tilt in heading-up navigation. 45 with the styled Map ID (flat buildings). With the demo Map ID tilt would extrude 3D
// buildings over the roads, so it defaults to 0 there. Override with NEXT_PUBLIC_NAV_TILT (0-60). North-up is always flat.
const DEFAULT_TILT = MAP_ID === 'DEMO_MAP_ID' ? 0 : 45;
const NAV_TILT_DEG = Math.min(60, Math.max(0, Number(process.env.NEXT_PUBLIC_NAV_TILT ?? DEFAULT_TILT)));

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
  isNavigating = false,
  rotRef,
}: {
  isNavigating?: boolean;
  /** the element rotated every animation frame by (rider heading - map heading); see the animation loop below */
  rotRef: React.Ref<HTMLDivElement>;
}) {
  if (isNavigating) {
    // Navigation chevron with a soft ground halo. Centre of the 64px box = the rider's true position (anchorPoint CENTER).
    return (
      <div className="relative w-16 h-16 flex items-center justify-center pointer-events-none select-none">
        <div className="absolute inset-3 rounded-full bg-blue-500/20" />
        <div ref={rotRef} className="relative w-12 h-12 flex items-center justify-center will-change-transform">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" className="drop-shadow-[0_4px_8px_rgba(0,0,0,0.5)]">
            <path d="M24 3 L43 43 L24 33 L5 43 Z" fill="#FFFFFF" />
            <path d="M24 6.5 L8.5 40 L24 31.5 Z" fill="#4285F4" />
            <path d="M24 6.5 L39.5 40 L24 31.5 Z" fill="#1A73E8" />
            <line x1="24" y1="7" x2="24" y2="31" stroke="#FFFFFF" strokeWidth="1.2" strokeLinecap="round" />
          </svg>
        </div>
      </div>
    );
  }

  // Browsing: blue dot with a direction beam
  return (
    <div className="relative w-14 h-14 flex items-center justify-center pointer-events-none select-none">
      <div className="absolute inset-3 bg-sky-400/20 rounded-full" />
      <div ref={rotRef} className="absolute inset-0 flex items-center justify-center will-change-transform">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
          <defs>
            <radialGradient id="beamGrad" cx="28" cy="28" r="28" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.55" />
              <stop offset="70%" stopColor="#38bdf8" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
            </radialGradient>
          </defs>
          <path d="M28 28 L14 4 A28 28 0 0 1 42 4 Z" fill="url(#beamGrad)" />
          <polygon points="28,2 24,14 32,14" fill="#38bdf8" />
        </svg>
      </div>
      <div className="relative z-10 w-5 h-5 bg-sky-500 rounded-full border-[2.5px] border-white shadow-[0_0_12px_rgba(56,189,248,0.9)]" />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Incident Marker on Map (Google Maps badge style)
// ─────────────────────────────────────────────────────────────────
function IncidentMarkerIcon({ incident }: { incident: RoadIncident }) {
  const isRed = incident.type === 'crash' || incident.type === 'slowdown';
  const bg = isRed ? '#d93025' : '#fbbc04';
  const color = isRed ? '#ffffff' : '#451a03';

  return (
    <div
      className="flex flex-col items-center cursor-pointer group"
      title={`${incident.title} (${incident.upvotes} verified)`}
    >
      <div
        className="w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white transition-transform hover:scale-115 active:scale-95"
        style={{ backgroundColor: bg, color }}
      >
        {incident.type === 'crash' && (
          <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
            <circle cx="7" cy="17" r="2" />
            <circle cx="17" cy="17" r="2" />
          </svg>
        )}
        {incident.type === 'slowdown' && (
          <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
            <circle cx="7" cy="17" r="2" />
            <circle cx="17" cy="17" r="2" />
          </svg>
        )}
        {incident.type === 'flooded' && (
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 12c1.5 1.5 3 2 4.5 2s3-.5 4.5-2 3-2 4.5-2 3 .5 4.5 2" />
            <path d="M2 18c1.5 1.5 3 2 4.5 2s3-.5 4.5-2 3-2 4.5-2 3 .5 4.5 2" />
          </svg>
        )}
        {incident.type === 'construction' && (
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 18h20" />
            <path d="M5 18v-4a7 7 0 0 1 14 0v4" />
          </svg>
        )}
        {incident.type === 'lane_closure' && (
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
            <line x1="4" y1="22" x2="4" y2="15" />
          </svg>
        )}
        {incident.type === 'hazard' && (
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="6" y1="3" x2="4" y2="21" />
            <line x1="18" y1="3" x2="20" y2="21" />
            <path d="M12 8v5" />
            <path d="M12 16h.01" />
          </svg>
        )}
        {incident.type === 'visibility' && (
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
            <path d="M8 19h8" />
          </svg>
        )}
      </div>
      <div className="hidden group-hover:block px-2 py-0.5 mt-1 bg-slate-900/95 text-white text-[10px] font-bold rounded-md whitespace-nowrap shadow-md border border-slate-700/80">
        {incident.title} ({incident.upvotes}✓)
      </div>
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
  compassMode = 'heading_up',
  onToggle,
}: {
  mapHeading: number;
  compassMode?: 'heading_up' | 'north_up';
  onToggle: () => void;
}) {
  // The needle points to true north: counter-rotate by the map's actual heading.
  const rotationDeg = -mapHeading;

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
          transition: 'transform 0.08s linear',
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
  activeIncidents = [],
  displayPosition = null,
  routePoint = null,
  droppedPin = null,
  onLongPress,
  onSelectOrigin,
  onSelectDestination,
  onMapClick,
  onRecenter,
  onCameraUnlink,
}: MapContainerProps) {
  const map = useMap();
  const [locating, setLocating] = useState(false);
  const [mapHeading, setMapHeading] = useState(0);
  const [compassMode, setCompassMode] = useState<'heading_up' | 'north_up'>('heading_up');
  const [isLocallyFollowing, setIsLocallyFollowing] = useState(isFollowingCamera);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const prevIsNavigatingRef = useRef(false);

  // Rider marker + camera follow are driven from one animation loop OUTSIDE React state, so a GPS fix does not re-render
  // the whole map: positions are interpolated between fixes and written straight to the marker and to map.moveCamera.
  const [riderMarkerRef, riderMarker] = useAdvancedMarkerRef();
  const arrowRef = useRef<HTMLDivElement | null>(null);
  const anim = useRef<{
    lat: number; lng: number; fromLat: number; fromLng: number; toLat: number; toLng: number;
    t0: number; h: number; hTarget: number;
  } | null>(null);
  // Latest values for event handlers and the loop (updated on every render, so they are never stale).
  const liveRef = useRef<{
    isNavigating: boolean;
    following: boolean;
    compassMode: 'heading_up' | 'north_up';
    gps: GPSPosition | null;
    riderHeading: number;
    marker: google.maps.marker.AdvancedMarkerElement | null;
  }>({ isNavigating: false, following: true, compassMode: 'heading_up', gps: null, riderHeading: 0, marker: null });

  // Keep local follow state synced when prop changes (e.g. from Recenter button)
  useEffect(() => {
    setIsLocallyFollowing(isFollowingCamera);
  }, [isFollowingCamera]);

  // A real drag unlinks the camera (so the rider can look around). A tap or a pinch-zoom does not.
  useEffect(() => {
    if (!map) return;

    const unlink = () => {
      liveRef.current.following = false; // stop the follow loop on the very next frame, before React re-renders
      setIsLocallyFollowing(false);
      if (onCameraUnlink) onCameraUnlink();
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('camera-unlinked'));
      }
    };

    const dragStartListener = map.addListener('dragstart', unlink);
    return () => {
      google.maps.event.removeListener(dragStartListener);
    };
  }, [map, onCameraUnlink]);

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

  // The route is drawn exactly as the backend returns it. It starts and ends ON a road (the backend snaps each pin to
  // the nearest road), so NO straight connector is drawn between a pin and the road: lines exist only where roads do.
  const fullConnectedPath = useMemo<LatLngType[]>(
    () => (routePath && routePath.length > 0 ? [...routePath] : []),
    [routePath]
  );

  const fullConnectedAlternatePath = useMemo<LatLngType[]>(
    () => (alternateRoutePath && alternateRoutePath.length > 0 ? [...alternateRoutePath] : []),
    [alternateRoutePath]
  );

  // Kept for the traveled/remaining split below: no points are prepended any more.
  const pathPrefixOffset = 0;

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
    traveled.push(fullConnectedPath[adjustedIdx]); // placeholder end vertex, moved to the rider's road point per fix
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
      const h = map.getHeading() ?? 0;
      setMapHeading((prev) => (Math.abs(h - prev) >= 1 || h === 0 ? h : prev));
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

  // ─── Animation loop: rider marker, arrow rotation and camera follow (Google-Maps-style) ───
  // Each GPS fix only sets a new TARGET; every frame we glide from the current position toward it (no teleporting), rotate the
  // arrow relative to the map, and, while following, move the camera with ONE map.moveCamera call (centre + heading + tilt).
  useEffect(() => {
    if (!map) return;
    let raf = 0;
    let alive = true;
    const last = { lat: NaN, lng: NaN, h: NaN, tilt: NaN };

    const tick = (now: number) => {
      if (!alive) return;
      const a = anim.current;
      const L = liveRef.current;
      if (a) {
        const k = Math.min(1, (now - a.t0) / 1000); // one GPS fix per second: glide linearly to the next one
        a.lat = a.fromLat + (a.toLat - a.fromLat) * k;
        a.lng = a.fromLng + (a.toLng - a.fromLng) * k;
        const dh = ((a.hTarget - a.h + 540) % 360) - 180;
        a.h = (a.h + dh * 0.15 + 360) % 360;

        if (L.marker) L.marker.position = { lat: a.lat, lng: a.lng };
        const mapHeadingNow = map.getHeading() ?? 0;
        if (arrowRef.current) arrowRef.current.style.transform = `rotate(${a.h - mapHeadingNow}deg)`;

        if (L.isNavigating && L.following) {
          const headingUp = L.compassMode === 'heading_up';
          const heading = headingUp ? a.h : 0;
          const tilt = headingUp ? NAV_TILT_DEG : 0;
          if (
            Math.abs(a.lat - last.lat) > 1e-8 || Math.abs(a.lng - last.lng) > 1e-8 ||
            Math.abs(heading - last.h) > 0.05 || tilt !== last.tilt
          ) {
            map.moveCamera({ center: { lat: a.lat, lng: a.lng }, heading, tilt });
            last.lat = a.lat; last.lng = a.lng; last.h = heading; last.tilt = tilt;
          }
        }
      }
      raf = requestAnimationFrame(tick);
    };

    const onVisibility = () => {
      if (document.hidden) {
        alive = false;
        cancelAnimationFrame(raf);
      } else if (!alive) {
        alive = true;
        raf = requestAnimationFrame(tick);
      }
    };

    raf = requestAnimationFrame(tick);
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      alive = false;
      cancelAnimationFrame(raf);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [map]);

  // Navigation starts: jump to the rider (zoom 18, tilted, facing the direction of travel). Navigation ends: back to a flat north-up map.
  useEffect(() => {
    if (!map) return;
    if (isNavigating) {
      const L = liveRef.current;
      const a = anim.current;
      const pos = a ? { lat: a.lat, lng: a.lng } : L.gps ? { lat: L.gps.lat, lng: L.gps.lng } : null;
      if (pos) map.moveCamera({ center: pos, zoom: 18, tilt: NAV_TILT_DEG, heading: a ? a.h : L.riderHeading });
    } else if (prevIsNavigatingRef.current) {
      map.moveCamera({ tilt: 0, heading: 0 });
    }
    prevIsNavigatingRef.current = isNavigating;
  }, [map, isNavigating]);

  // ─── Manage Google Maps Polylines imperatively ───
  useEffect(() => {
    if (!map) return;

    const zoom = currentZoomRef.current;
    const w = getStrokeWeights(zoom);

    const traveledLatLngs = traveledCoords.map(([lat, lng]) => ({ lat, lng }));
    const remainingLatLngs = remainingCoords.map(([lat, lng]) => ({ lat, lng }));
    const alternateLatLngs = fullConnectedAlternatePath.map(([lat, lng]) => ({ lat, lng }));

    let clickListener: google.maps.MapsEventListener | null = null;

    // 1. Alternate Route Polyline (Google Maps Muted Slate Gray)
    const alternateType = selectedRouteType === 'shortest' ? 'dynamic' : 'shortest';
    const altColor = '#80868B'; // Official Google Alternate Gray

    if (alternateLatLngs.length > 1 && !isNavigating) {
      if (!polylineAlternateRef.current) {
        polylineAlternateRef.current = new google.maps.Polyline({
          strokeColor: altColor,
          strokeOpacity: 0.65,
          strokeWeight: w.alternate,
          geodesic: true,
          zIndex: 12,
          clickable: true,
          map,
        });
      } else {
        polylineAlternateRef.current.setOptions({
          strokeColor: altColor,
          strokeOpacity: 0.65,
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
          strokeColor: '#94a3b8',
          strokeOpacity: 0.45,
          strokeWeight: Math.max(2, w.foreground - 1),
          geodesic: true,
          zIndex: 10,
          map,
        });
      } else {
        polylineTraveledRef.current.setOptions({
          strokeWeight: Math.max(2, w.foreground - 1),
          geodesic: true,
          strokeOpacity: 0.45,
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

    // 3. Remaining Active Polyline — Google Navigation Royal Blue (#1A73E8)
    if (remainingLatLngs.length > 1) {
      // Soft Casing (outline)
      const casingColor = theme === 'dark' ? '#0f172a' : '#1557B0';
      if (!polylineRemainingCasingRef.current) {
        polylineRemainingCasingRef.current = new google.maps.Polyline({
          strokeColor: casingColor,
          strokeOpacity: 0.85,
          strokeWeight: w.casing,
          geodesic: true,
          zIndex: 20,
          map,
        });
      } else {
        polylineRemainingCasingRef.current.setOptions({
          strokeColor: casingColor,
          strokeWeight: w.casing,
          geodesic: true,
        });
      }
      polylineRemainingCasingRef.current.setPath(remainingLatLngs);
      polylineRemainingCasingRef.current.setMap(map);

      // Foreground: Official Google Navigation Royal Blue
      const activeColor = '#1A73E8';
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

  // Each GPS fix: move just the split vertex to the exact point on the road where the rider is. The remaining (blue) line then
  // starts at the rider and the traveled (grey) line ends there, without re-creating the whole path on every fix.
  useEffect(() => {
    if (!isNavigating || !routePoint) return;
    const at = new google.maps.LatLng(routePoint.lat, routePoint.lng);
    for (const line of [polylineRemainingCasingRef.current, polylineRemainingRef.current]) {
      const path = line?.getPath();
      if (path && path.getLength() > 1) path.setAt(0, at);
    }
    const traveledPath = polylineTraveledRef.current?.getPath();
    if (traveledPath && traveledPath.getLength() > 1) traveledPath.setAt(traveledPath.getLength() - 1, at);
  }, [routePoint, isNavigating, remainingCoords, traveledCoords]);

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

  // Re-center, Google-Maps-style. Navigating: back onto the rider, zoom 18, tilted, facing the direction of travel (or north-up
  // if the compass is in north-up mode). Browsing: centre on the rider's position, flat, north-up, zoom 16.
  const recenterCamera = useCallback(() => {
    if (!map) return;
    const L = liveRef.current;
    const a = anim.current;
    const pos = a ? { lat: a.lat, lng: a.lng } : L.gps ? { lat: L.gps.lat, lng: L.gps.lng } : null;
    const apply = (center: { lat: number; lng: number }) => {
      if (L.isNavigating) {
        const headingUp = L.compassMode === 'heading_up';
        map.moveCamera({ center, zoom: 18, tilt: headingUp ? NAV_TILT_DEG : 0, heading: headingUp ? (a ? a.h : L.riderHeading) : 0 });
      } else {
        map.moveCamera({ center, zoom: 16, tilt: 0, heading: 0 });
      }
    };
    if (pos) {
      apply(pos);
    } else if (typeof navigator !== 'undefined' && navigator.geolocation) {
      setLocating(true);
      navigator.geolocation.getCurrentPosition(
        (p) => {
          setLocating(false);
          apply({ lat: p.coords.latitude, lng: p.coords.longitude });
        },
        () => setLocating(false),
        { enableHighAccuracy: true, timeout: 6000, maximumAge: 3000 }
      );
    }
  }, [map]);

  // Global recenter event (the navigation footer and the page dispatch it)
  useEffect(() => {
    const handleGlobalRecenter = () => {
      liveRef.current.following = true;
      setIsLocallyFollowing(true);
      recenterCamera();
    };
    window.addEventListener('recenter-map', handleGlobalRecenter);
    return () => window.removeEventListener('recenter-map', handleGlobalRecenter);
  }, [recenterCamera]);

  // Press-and-hold drops a pin (like Google Maps). A plain tap or a drag does NOTHING, so touching the map around can no longer
  // select places by accident. Touch is handled at the DOM level (the position is converted with the map's own projection, which
  // stays exact when the map is rotated); the mouse uses the map's events. Never while navigating.
  useEffect(() => {
    if (!map || isNavigating || !onLongPress) return;
    const container = map.getDiv();

    const overlay = new google.maps.OverlayView(); // only needed for its pixel -> latitude/longitude projection
    overlay.onAdd = () => {};
    overlay.draw = () => {};
    overlay.onRemove = () => {};
    overlay.setMap(map);

    let lastFire = 0;
    const fire = (lat: number, lng: number) => {
      const now = Date.now();
      if (now - lastFire < 800) return; // a touch hold and a context-menu event can both report the same press
      lastFire = now;
      if (typeof navigator !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(25);
      onLongPress({ lat: Number(lat.toFixed(6)), lng: Number(lng.toFixed(6)) });
    };
    const detector = new LongPressDetector<{ lat: number; lng: number }>({ onLongPress: (p) => fire(p.lat, p.lng) });

    const toLatLng = (clientX: number, clientY: number) => {
      const projection = overlay.getProjection();
      if (!projection) return null;
      const rect = container.getBoundingClientRect();
      const ll = projection.fromContainerPixelToLatLng(new google.maps.Point(clientX - rect.left, clientY - rect.top));
      return ll ? { lat: ll.lat(), lng: ll.lng() } : null;
    };

    const onTouchStart = (ev: TouchEvent) => {
      if (ev.touches.length !== 1) return detector.cancel(); // a second finger (pinch) is never a long press
      const t = ev.touches[0];
      const pos = toLatLng(t.clientX, t.clientY);
      if (pos) detector.start(t.clientX, t.clientY, pos);
      else detector.cancel();
    };
    const onTouchMove = (ev: TouchEvent) => {
      if (ev.touches.length !== 1) detector.cancel();
      else detector.move(ev.touches[0].clientX, ev.touches[0].clientY);
    };
    const onTouchEnd = () => detector.cancel();
    const opts: AddEventListenerOptions = { capture: true, passive: true };
    container.addEventListener('touchstart', onTouchStart, opts);
    container.addEventListener('touchmove', onTouchMove, opts);
    container.addEventListener('touchend', onTouchEnd, opts);
    container.addEventListener('touchcancel', onTouchEnd, opts);

    // Mouse (desktop): hold the button down, or right-click.
    const mouseEvent = (e: google.maps.MapMouseEvent) => {
      const dom = e.domEvent as MouseEvent | TouchEvent | undefined;
      if (!dom || 'touches' in dom) return null;
      return dom as MouseEvent;
    };
    const listeners = [
      map.addListener('mousedown', (e: google.maps.MapMouseEvent) => {
        const m = mouseEvent(e);
        if (m && e.latLng) detector.start(m.clientX, m.clientY, { lat: e.latLng.lat(), lng: e.latLng.lng() });
      }),
      map.addListener('mousemove', (e: google.maps.MapMouseEvent) => {
        const m = mouseEvent(e);
        if (m) detector.move(m.clientX, m.clientY);
      }),
      map.addListener('mouseup', () => detector.cancel()),
      map.addListener('dragstart', () => detector.cancel()),
      map.addListener('zoom_changed', () => detector.cancel()),
      map.addListener('contextmenu', (e: google.maps.MapMouseEvent) => {
        detector.cancel();
        if (e.latLng) fire(e.latLng.lat(), e.latLng.lng());
      }),
    ];

    return () => {
      detector.cancel();
      container.removeEventListener('touchstart', onTouchStart, opts);
      container.removeEventListener('touchmove', onTouchMove, opts);
      container.removeEventListener('touchend', onTouchEnd, opts);
      container.removeEventListener('touchcancel', onTouchEnd, opts);
      listeners.forEach((l) => google.maps.event.removeListener(l));
      overlay.setMap(null);
    };
  }, [map, isNavigating, onLongPress]);

  // Recenter button (browsing mode; while navigating the footer has its own)
  const handleRecenterClick = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.stopPropagation();
      e.preventDefault();
      if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(10);
      liveRef.current.following = true;
      setIsLocallyFollowing(true);
      if (onRecenter) onRecenter();
      recenterCamera();
    },
    [onRecenter, recenterCamera]
  );

  // Compass, Google-Maps-style:
  //  - browsing: tap resets the map to north-up and flat
  //  - navigating: toggles "heading up" (map turns with you, tilted) and "north up" (flat, north at the top)
  const handleCompassToggle = useCallback(() => {
    if (!map) return;
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(10);

    if (!liveRef.current.isNavigating) {
      map.moveCamera({ heading: 0, tilt: 0 });
      setMapHeading(0);
      return;
    }
    if (compassMode === 'heading_up') {
      liveRef.current.compassMode = 'north_up';
      setCompassMode('north_up');
      map.moveCamera({ heading: 0, tilt: 0 });
      setMapHeading(0);
    } else {
      liveRef.current.compassMode = 'heading_up';
      liveRef.current.following = true;
      setCompassMode('heading_up');
      setIsLocallyFollowing(true);
      if (onRecenter) onRecenter();
      recenterCamera();
    }
  }, [map, compassMode, onRecenter, recenterCamera]);

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
  // Stacked cleanly above the Report Incident button (~104px + 48px + 12px gap)
  // Offsets include the phone's bottom safe area (gesture bar), so nothing is hidden behind the footer:
  //   navigating : footer card (~96px) + report button (48px) + gaps  -> compass sits above the report button
  //   route shown: above the route panel (~168px)
  const buttonStackBottom = isNavigating
    ? 'calc(env(safe-area-inset-bottom, 0px) + 176px)'
    : fullConnectedPath.length > 0
    ? 'calc(var(--route-panel-height, 173px) + 12px)' // just above the route panel, whatever its height
    : 'calc(env(safe-area-inset-bottom, 0px) + 28px)';

  const riderCoord = gpsPosition?.lat && gpsPosition?.lng ? gpsPosition : null;
  const isMoving = gpsPosition?.speed !== null && gpsPosition?.speed !== undefined && gpsPosition.speed > 1.5;
  const riderHeading = (isMoving && gpsPosition?.heading !== null && gpsPosition?.heading !== undefined)
    ? gpsPosition.heading
    : (deviceHeading || gpsPosition?.heading || 0);

  // Where the marker should be: the engine's road-aligned position while navigating, the raw GPS fix otherwise.
  const target = isNavigating && displayPosition ? displayPosition : riderCoord ? { lat: riderCoord.lat, lng: riderCoord.lng } : null;

  // The marker is created once at the first known position; the animation loop moves it from then on.
  const riderInitial = useRef<{ lat: number; lng: number } | null>(null);
  if (!riderInitial.current && target) riderInitial.current = { lat: target.lat, lng: target.lng };

  // A new GPS target: start gliding from wherever the marker is now (never from a stale position).
  useEffect(() => {
    if (!target) return;
    const now = performance.now();
    const a = anim.current;
    if (!a) {
      anim.current = {
        lat: target.lat, lng: target.lng, fromLat: target.lat, fromLng: target.lng, toLat: target.lat, toLng: target.lng,
        t0: now, h: riderHeading, hTarget: riderHeading,
      };
      return;
    }
    a.fromLat = a.lat;
    a.fromLng = a.lng;
    a.toLat = target.lat;
    a.toLng = target.lng;
    a.t0 = now;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target?.lat, target?.lng]);

  useEffect(() => {
    if (anim.current) anim.current.hTarget = riderHeading;
  }, [riderHeading]);

  // Latest values for the animation loop and the event handlers (written during render, read later: never stale).
  liveRef.current = {
    isNavigating,
    following: isLocallyFollowing,
    compassMode,
    gps: gpsPosition ?? null,
    riderHeading,
    marker: riderMarker,
  };

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

      {/* Pin dropped by press-and-hold */}
      {droppedPin && !isNavigating && (
        <AdvancedMarker position={{ lat: droppedPin.lat, lng: droppedPin.lng }} title="Dropped pin" zIndex={60}>
          <Pin background="#F97316" borderColor="#C2410C" glyphColor="#FFFFFF" scale={1.2} />
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
      {riderInitial.current && (
        <AdvancedMarker
          ref={riderMarkerRef}
          position={riderInitial.current}
          anchorPoint={AdvancedMarkerAnchorPoint.CENTER}
          zIndex={1000}
          title="Rider"
        >
          <RiderMarkerIcon isNavigating={isNavigating} rotRef={arrowRef} />
        </AdvancedMarker>
      )}

      {/* Live Crowd-Reported Incident Markers (Accidents, Floods, Closures) */}
      {activeIncidents.map((incident) => (
        <AdvancedMarker
          key={incident.id}
          position={{ lat: incident.lat, lng: incident.lng }}
          zIndex={150}
          title={`${incident.title} (Reported on road)`}
        >
          <IncidentMarkerIcon incident={incident} />
        </AdvancedMarker>
      ))}

      {/*
       * ── Floating button stack: Compass (top) + Recenter (bottom) ──
       * Single container so they always align together and reposition as one unit.
       * Compass is ALWAYS visible — allows user to see/reset north at any time.
       * Recenter is hidden during navigation (NavigationFooter has its own).
       */}
      <div
        ref={containerRef}
        style={{ bottom: buttonStackBottom }}
        className="fixed right-4 sm:right-6 z-[1001] flex flex-col items-center gap-2 transition-all duration-300 pointer-events-auto"
        onMouseDown={(e) => e.stopPropagation()}
        onTouchStart={(e) => e.stopPropagation()}
      >
        {/* ── Compass "N" Button — always visible ── */}
        {(isNavigating || Math.abs(mapHeading) >= 1) && (
          <CompassButton mapHeading={mapHeading} compassMode={compassMode} onToggle={handleCompassToggle} />
        )}

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
          mapId={MAP_ID}
          renderingType={RenderingType.VECTOR}
          clickableIcons={false}
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
