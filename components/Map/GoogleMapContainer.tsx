'use client';

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  APIProvider,
  Map as GMap,
  useMap,
  AdvancedMarker,
  Pin,
} from '@vis.gl/react-google-maps';
import { Crosshair, Loader2 } from 'lucide-react';
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

// SVG Rider Marker with dynamic heading
function RiderMarkerIcon({ heading }: { heading: number }) {
  const quantized = Math.round((heading % 360) / 5) * 5;
  return (
    <div className="relative w-8 h-8 flex items-center justify-center pointer-events-none select-none -translate-y-1/2">
      <div className="absolute inset-0 bg-sky-500/30 rounded-full animate-ping" />
      <div
        className="w-5 h-5 bg-sky-500 rounded-full border-2 border-white shadow-[0_0_12px_rgba(56,189,248,0.9)] flex items-center justify-center transition-transform duration-200"
        style={{ transform: `rotate(${quantized}deg)` }}
      >
        <div className="w-0 h-0 border-l-[4px] border-l-transparent border-r-[4px] border-r-transparent border-b-[8px] border-b-white -mb-0.5" />
      </div>
    </div>
  );
}

// Inner Google Maps Controller: Polylines, bounds, camera, clicks
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
  const containerRef = useRef<HTMLDivElement | null>(null);

  // References to Google Maps Polyline instances
  const polylineTraveledRef = useRef<google.maps.Polyline | null>(null);
  const polylineRemainingCasingRef = useRef<google.maps.Polyline | null>(null);
  const polylineRemainingRef = useRef<google.maps.Polyline | null>(null);
  const polylineAlternateRef = useRef<google.maps.Polyline | null>(null);
  const prevRouteKeyRef = useRef<string>('');

  const activeThemeStyle = useMemo(() => {
    return theme === 'dark' ? darkMapStyle : lightMapStyle;
  }, [theme]);

  // Apply map styles dynamically on theme change
  useEffect(() => {
    if (map && activeThemeStyle) {
      map.setOptions({
        styles: activeThemeStyle,
      });
    }
  }, [map, activeThemeStyle]);

  // Connect Origin -> Backend Route Road Coordinates -> Destination Pin seamlessly
  const fullConnectedPath = useMemo(() => {
    if (!routePath || routePath.length === 0) return [];

    const pts: LatLngType[] = [...routePath];

    if (origin) {
      const first = pts[0];
      const distFromOrigin = haversineMeters(origin.lat, origin.lng, first[0], first[1]);
      if (distFromOrigin > 2 && distFromOrigin < 3000) {
        pts.unshift([origin.lat, origin.lng]);
      }
    }

    if (destination) {
      const last = pts[pts.length - 1];
      const distToDest = haversineMeters(destination.lat, destination.lng, last[0], last[1]);
      if (distToDest > 2 && distToDest < 3000) {
        pts.push([destination.lat, destination.lng]);
      }
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
      if (distFromOrigin > 2 && distFromOrigin < 3000) {
        pts.unshift([origin.lat, origin.lng]);
      }
    }

    if (destination) {
      const last = pts[pts.length - 1];
      const distToDest = haversineMeters(destination.lat, destination.lng, last[0], last[1]);
      if (distToDest > 2 && distToDest < 3000) {
        pts.push([destination.lat, destination.lng]);
      }
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

  // Manage Google Maps Polylines directly on the road network
  useEffect(() => {
    if (!map) return;

    // Convert coords to google.maps.LatLngLiteral format
    const traveledLatLngs = traveledCoords.map(([lat, lng]) => ({ lat, lng }));
    const remainingLatLngs = remainingCoords.map(([lat, lng]) => ({ lat, lng }));
    const alternateLatLngs = fullConnectedAlternatePath.map(([lat, lng]) => ({ lat, lng }));

    // 1. Alternate Route Polyline (rendered in different color, clickable)
    const alternateType = selectedRouteType === 'shortest' ? 'dynamic' : 'shortest';
    const altColor = alternateType === 'dynamic' ? '#f472b6' : '#38bdf8';

    if (alternateLatLngs.length > 1 && !isNavigating) {
      if (!polylineAlternateRef.current) {
        polylineAlternateRef.current = new google.maps.Polyline({
          strokeColor: altColor,
          strokeOpacity: 0.55,
          strokeWeight: 4.5,
          geodesic: true,
          zIndex: 12,
          clickable: true,
          map,
        });
      } else {
        polylineAlternateRef.current.setOptions({ strokeColor: altColor });
      }
      polylineAlternateRef.current.setPath(alternateLatLngs);
      polylineAlternateRef.current.setMap(map);

      // Click alternate polyline to switch to it
      const clickListener = polylineAlternateRef.current.addListener('click', () => {
        if (onSelectRouteType) onSelectRouteType(alternateType);
      });

      return () => {
        google.maps.event.removeListener(clickListener);
      };
    } else if (polylineAlternateRef.current) {
      polylineAlternateRef.current.setMap(null);
    }

    // 2. Traveled Polyline (greyed out)
    if (traveledLatLngs.length > 1) {
      if (!polylineTraveledRef.current) {
        polylineTraveledRef.current = new google.maps.Polyline({
          strokeColor: '#64748b',
          strokeOpacity: 0.6,
          strokeWeight: 6,
          geodesic: true,
          zIndex: 10,
          map,
        });
      }
      polylineTraveledRef.current.setPath(traveledLatLngs);
      polylineTraveledRef.current.setMap(map);
    } else if (polylineTraveledRef.current) {
      polylineTraveledRef.current.setMap(null);
    }

    // 3. Remaining Active Polyline Casing & Vibrant Foreground Line
    if (remainingLatLngs.length > 1) {
      if (!polylineRemainingCasingRef.current) {
        polylineRemainingCasingRef.current = new google.maps.Polyline({
          strokeColor: '#0f172a',
          strokeOpacity: 0.85,
          strokeWeight: 9.5,
          geodesic: true,
          zIndex: 20,
          map,
        });
      }
      polylineRemainingCasingRef.current.setPath(remainingLatLngs);
      polylineRemainingCasingRef.current.setMap(map);

      const activeColor = selectedRouteType === 'dynamic' ? '#f472b6' : '#38bdf8';
      if (!polylineRemainingRef.current) {
        polylineRemainingRef.current = new google.maps.Polyline({
          strokeColor: activeColor,
          strokeOpacity: 0.95,
          strokeWeight: 6.5,
          geodesic: true,
          zIndex: 22,
          map,
        });
      } else {
        polylineRemainingRef.current.setOptions({ strokeColor: activeColor });
      }
      polylineRemainingRef.current.setPath(remainingLatLngs);
      polylineRemainingRef.current.setMap(map);
    } else {
      if (polylineRemainingCasingRef.current) polylineRemainingCasingRef.current.setMap(null);
      if (polylineRemainingRef.current) polylineRemainingRef.current.setMap(null);
    }
  }, [map, traveledCoords, remainingCoords, fullConnectedAlternatePath, selectedRouteType, isNavigating, onSelectRouteType]);

  // Clean up polylines when component unmounts
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
      map.fitBounds(bounds, {
        top: 140,
        bottom: 200,
        left: 50,
        right: 50,
      });
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
        map.fitBounds(bounds, {
          top: 140,
          bottom: 200,
          left: 50,
          right: 50,
        });
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
      const loc: Point = {
        lat,
        lng,
        address: `${lat}, ${lng}`,
        name: `${lat}, ${lng}`,
      };

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

    return () => {
      google.maps.event.removeListener(listener);
    };
  }, [map, activeInput, origin, destination, onSelectOrigin, onSelectDestination, onMapClick]);

  // Recenter button click
  const handleRecenterClick = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.stopPropagation();
      e.preventDefault();

      if (typeof window !== 'undefined' && 'vibrate' in navigator) {
        navigator.vibrate(10);
      }

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
            if (origin) {
              map.panTo({ lat: origin.lat, lng: origin.lng });
            } else if (destination) {
              map.panTo({ lat: destination.lat, lng: destination.lng });
            }
          },
          { enableHighAccuracy: true, timeout: 6000, maximumAge: 3000 }
        );
      } else if (origin) {
        map.panTo({ lat: origin.lat, lng: origin.lng });
      }
    },
    [map, gpsPosition, origin, destination, isNavigating, onRecenter]
  );

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
  const riderHeading = gpsPosition?.heading || 0;

  return (
    <>
      {/* Origin Marker (Iconic Google Blue Pin with readable label and pinpoint anchor) */}
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
            <Pin
              background="#1A73E8"
              borderColor="#1557B0"
              glyphColor="#FFFFFF"
              scale={1.1}
            />
          </div>
        </AdvancedMarker>
      )}

      {/* Destination Marker (Iconic Google Red Pin with readable label and pinpoint anchor) */}
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
            <Pin
              background="#EA4335"
              borderColor="#B31412"
              glyphColor="#FFFFFF"
              scale={1.2}
            />
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

      {/* Floating Recenter HUD Control */}
      {!isNavigating && (
        <div
          ref={containerRef}
          className={`fixed right-4 sm:right-8 z-[1000] transition-all duration-300 pointer-events-auto ${mobileBottomClass} sm:bottom-8`}
          onMouseDown={(e) => e.stopPropagation()}
          onTouchStart={(e) => e.stopPropagation()}
        >
          <button
            type="button"
            onClick={handleRecenterClick}
            onMouseDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
            title="Re-center on my location"
            className="w-12 h-12 sm:w-14 sm:h-14 bg-[#0f172a] hover:bg-slate-800 active:scale-90 text-sky-400 border border-slate-700/80 rounded-2xl sm:rounded-full shadow-2xl transition-all flex items-center justify-center cursor-pointer"
          >
            {locating ? (
              <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
            ) : (
              <Crosshair className="w-5 h-5 sm:w-6 sm:h-6 text-sky-400" />
            )}
          </button>
        </div>
      )}
    </>
  );
}

export const GoogleMapContainer: React.FC<MapContainerProps> = (props) => {
  const [defaultCenter] = useState<{ lat: number; lng: number }>({
    lat: 12.9716,
    lng: 77.5946, // Central Bengaluru
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
