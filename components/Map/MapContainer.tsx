'use client';

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  MapContainer as LeafletMapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import { Crosshair, Loader2 } from 'lucide-react';
import { LatLng as LatLngType, Point, GPSPosition, RouteMode } from '@/lib/types';

interface MapContainerProps {
  origin?: Point | null;
  destination?: Point | null;
  activeInput?: 'origin' | 'destination';
  routePath?: LatLngType[] | null;
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

const STADIA_API_KEY = process.env.NEXT_PUBLIC_STADIA_KEY || '4594f003-3a5c-4cb1-bff3-60d813fd242b';

// Custom Map Markers (DivIcons)
const originIcon = L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:24px;height:24px;display:flex;align-items:center;justify-content:center;">
      <div style="position:absolute;inset:0;background:#38bdf8;border-radius:50%;opacity:0.35;animation:ping 2s cubic-bezier(0,0,0.2,1) infinite;"></div>
      <div style="width:16px;height:16px;background:#0284c7;border-radius:50%;border:3px solid #ffffff;box-shadow:0 0 12px rgba(56,189,248,0.8);"></div>
    </div>
  `,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const destIcon = L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:28px;height:34px;display:flex;align-items:center;justify-content:center;">
      <svg width="28" height="34" viewBox="0 0 24 30" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 8.5 12 18 12 18s12-9.5 12-18c0-6.63-5.37-12-12-12z" fill="#f97316"/>
        <circle cx="12" cy="11" r="5" fill="#ffffff"/>
      </svg>
    </div>
  `,
  iconSize: [28, 34],
  iconAnchor: [14, 34],
});

// Cache rider icons by quantized heading (every 5 degrees)
const iconCache: Record<number, L.DivIcon> = {};
function getRiderIcon(heading: number = 0): L.DivIcon {
  const quantized = Math.round((heading % 360) / 5) * 5;
  if (!iconCache[quantized]) {
    iconCache[quantized] = L.divIcon({
      className: '',
      html: `
        <div style="position:relative;width:46px;height:46px;display:flex;align-items:center;justify-content:center;transform:translateZ(0);">
          <div style="position:absolute;inset:4px;background:#0284c7;opacity:0.25;border-radius:50%;animation:ping 2.5s cubic-bezier(0,0,0.2,1) infinite;"></div>
          <div style="width:28px;height:28px;background:#0284c7;border-radius:50%;border:3px solid #ffffff;box-shadow:0 0 16px rgba(56,189,248,0.9);display:flex;align-items:center;justify-content:center;transform:rotate(${quantized}deg);transition:transform 0.2s cubic-bezier(0.2,0,0,1);">
            <div style="width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:10px solid #ffffff;margin-bottom:3px;"></div>
          </div>
        </div>
      `,
      iconSize: [46, 46],
      iconAnchor: [23, 23],
    });
  }
  return iconCache[quantized];
}

// Controller for camera panning, auto-fitting bounds and smooth navigation tracking
function MapCameraController({
  center,
  routePath,
  isNavigating,
  isFollowingCamera,
  gpsPosition,
}: {
  center: [number, number];
  routePath?: LatLngType[] | null;
  isNavigating?: boolean;
  isFollowingCamera?: boolean;
  gpsPosition?: GPSPosition | null;
}) {
  const map = useMap();
  const prevRouteRef = useRef<LatLngType[] | null>(null);

  // Auto-fit route bounds when a new route is loaded
  useEffect(() => {
    if (routePath && routePath.length > 1 && !isNavigating) {
      if (prevRouteRef.current !== routePath) {
        prevRouteRef.current = routePath;
        try {
          const bounds = L.latLngBounds(routePath);
          map.fitBounds(bounds, {
            paddingTopLeft: [40, 140],
            paddingBottomRight: [40, 200],
            maxZoom: 16,
            animate: true,
            duration: 0.8,
          });
        } catch (e) {}
      }
    }
  }, [routePath, isNavigating, map]);

  // Global fit-route-bounds listener for Preview Route button
  useEffect(() => {
    const handleFitBounds = () => {
      if (routePath && routePath.length > 1) {
        try {
          const bounds = L.latLngBounds(routePath);
          map.fitBounds(bounds, {
            paddingTopLeft: [40, 140],
            paddingBottomRight: [40, 200],
            maxZoom: 16,
            animate: true,
            duration: 0.8,
          });
        } catch (e) {}
      }
    };

    window.addEventListener('fit-route-bounds', handleFitBounds);
    return () => window.removeEventListener('fit-route-bounds', handleFitBounds);
  }, [routePath, map]);

  // Global recenter listener
  useEffect(() => {
    const handleGlobalRecenter = () => {
      const isMobile = typeof window !== 'undefined' ? window.innerWidth < 640 : false;
      const zoomLevel = isMobile ? (isNavigating ? 18 : 17) : (isNavigating ? 16.5 : 15.5);

      if (gpsPosition && gpsPosition.lat && gpsPosition.lng) {
        map.flyTo([gpsPosition.lat, gpsPosition.lng], zoomLevel, {
          animate: true,
          duration: 0.7,
        });
      } else if (typeof window !== 'undefined' && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            map.flyTo([pos.coords.latitude, pos.coords.longitude], zoomLevel, {
              animate: true,
              duration: 0.7,
            });
          },
          undefined,
          { enableHighAccuracy: true, timeout: 5000, maximumAge: 3000 }
        );
      }
    };

    window.addEventListener('recenter-map', handleGlobalRecenter);
    return () => window.removeEventListener('recenter-map', handleGlobalRecenter);
  }, [gpsPosition, isNavigating, map]);

  // Smooth camera follow during active navigation
  useEffect(() => {
    if (isNavigating && isFollowingCamera && center && center[0] && center[1]) {
      map.panTo(center, { animate: true, duration: 0.5, easeLinearity: 0.25 });
    }
  }, [center, isNavigating, isFollowingCamera, map]);

  return null;
}

// Recenter and Map Controller Button (Guaranteed Zero-Clickthrough to Map)
function MapRecenterControl({
  gpsPosition,
  origin,
  destination,
  isNavigating,
  routePath,
  onRecenter,
}: {
  gpsPosition?: GPSPosition | null;
  origin?: Point | null;
  destination?: Point | null;
  isNavigating?: boolean;
  routePath?: LatLngType[] | null;
  onRecenter?: () => void;
}) {
  const map = useMap();
  const [locating, setLocating] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Disable all Leaflet click / touch bubbling on this control container
  useEffect(() => {
    if (containerRef.current) {
      L.DomEvent.disableClickPropagation(containerRef.current);
      L.DomEvent.disableScrollPropagation(containerRef.current);
    }
  }, []);

  const getOptimalZoom = useCallback((forNav: boolean = false) => {
    const isMobile = typeof window !== 'undefined' ? window.innerWidth < 640 : false;
    if (forNav || isNavigating) {
      return isMobile ? 18 : 16.5;
    }
    return isMobile ? 17 : 15.5;
  }, [isNavigating]);

  const handleRecenter = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.stopPropagation();
    e.preventDefault();

    if (typeof window !== 'undefined' && 'vibrate' in navigator) {
      navigator.vibrate(10);
    }

    if (onRecenter) onRecenter();

    const zoomLevel = getOptimalZoom();

    if (gpsPosition && gpsPosition.lat && gpsPosition.lng) {
      map.flyTo([gpsPosition.lat, gpsPosition.lng], zoomLevel, {
        animate: true,
        duration: 0.7,
      });
      return;
    }

    // Direct hardware GPS query if prop isn't ready
    if (typeof window !== 'undefined' && navigator.geolocation) {
      setLocating(true);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocating(false);
          map.flyTo([pos.coords.latitude, pos.coords.longitude], zoomLevel, {
            animate: true,
            duration: 0.7,
          });
        },
        () => {
          setLocating(false);
          if (origin) {
            map.flyTo([origin.lat, origin.lng], zoomLevel - 0.5, { animate: true, duration: 0.7 });
          } else if (destination) {
            map.flyTo([destination.lat, destination.lng], zoomLevel - 0.5, { animate: true, duration: 0.7 });
          }
        },
        { enableHighAccuracy: true, timeout: 6000, maximumAge: 3000 }
      );
    } else if (origin) {
      map.flyTo([origin.lat, origin.lng], zoomLevel - 0.5, { animate: true, duration: 0.7 });
    }
  }, [map, gpsPosition, origin, destination, onRecenter, getOptimalZoom]);

  // Clean responsive bottom offset: On desktop laptops sm:, it is rock-solid at sm:bottom-8. On mobile, it adjusts above drawer.
  const mobileBottomClass = isNavigating
    ? 'bottom-[94px]'
    : routePath && routePath.length > 0
    ? 'bottom-[175px]'
    : 'bottom-[24px]';

  return (
    <div
      ref={containerRef}
      className={`fixed right-4 sm:right-8 z-[1000] transition-all duration-300 pointer-events-auto ${mobileBottomClass} sm:bottom-8`}
      onMouseDown={(e) => e.stopPropagation()}
      onTouchStart={(e) => e.stopPropagation()}
    >
      <button
        type="button"
        onClick={handleRecenter}
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
  );
}

// Click listener on map using live refs
function MapClickListener({
  origin,
  destination,
  activeInput = 'origin',
  onSelectOrigin,
  onSelectDestination,
  onMapClick,
}: {
  origin?: Point | null;
  destination?: Point | null;
  activeInput?: 'origin' | 'destination';
  onSelectOrigin?: (loc: Point) => void;
  onSelectDestination?: (loc: Point) => void;
  onMapClick?: (latlng: [number, number]) => void;
}) {
  const originRef = useRef(origin);
  const destRef = useRef(destination);
  const activeInputRef = useRef(activeInput);
  const onSelectOriginRef = useRef(onSelectOrigin);
  const onSelectDestRef = useRef(onSelectDestination);
  const onMapClickRef = useRef(onMapClick);

  useEffect(() => { originRef.current = origin; }, [origin]);
  useEffect(() => { destRef.current = destination; }, [destination]);
  useEffect(() => { activeInputRef.current = activeInput; }, [activeInput]);
  useEffect(() => { onSelectOriginRef.current = onSelectOrigin; }, [onSelectOrigin]);
  useEffect(() => { onSelectDestRef.current = onSelectDestination; }, [onSelectDestination]);
  useEffect(() => { onMapClickRef.current = onMapClick; }, [onMapClick]);

  useMapEvents({
    click(e: L.LeafletMouseEvent) {
      const coords: [number, number] = [
        Number(e.latlng.lat.toFixed(5)),
        Number(e.latlng.lng.toFixed(5)),
      ];
      const loc: Point = {
        lat: coords[0],
        lng: coords[1],
        address: `${coords[0]}, ${coords[1]}`,
        name: `${coords[0]}, ${coords[1]}`,
      };

      if (onMapClickRef.current) {
        onMapClickRef.current(coords);
      }

      const curOrigin = originRef.current;
      const curDest = destRef.current;
      const curActive = activeInputRef.current;

      if (curActive === 'destination' && onSelectDestRef.current) {
        onSelectDestRef.current(loc);
      } else if (curActive === 'origin' && onSelectOriginRef.current) {
        onSelectOriginRef.current(loc);
      } else if (!curOrigin && onSelectOriginRef.current) {
        onSelectOriginRef.current(loc);
      } else if (!curDest && onSelectDestRef.current) {
        onSelectDestRef.current(loc);
      } else if (onSelectDestRef.current) {
        onSelectDestRef.current(loc);
      }
    },
  });

  return null;
}

export const MapContainer: React.FC<MapContainerProps> = ({
  origin,
  destination,
  activeInput = 'origin',
  routePath,
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
}) => {
  const [mapCenter] = useState<[number, number]>([12.9716, 77.5946]); // Central Bengaluru
  const [mapZoom] = useState<number>(13);

  const riderCoord: [number, number] | null = gpsPosition
    ? [gpsPosition.lat, gpsPosition.lng]
    : null;

  const riderHeading = gpsPosition?.heading || 0;

  // Active camera center
  const activeCenter: [number, number] = useMemo(() => {
    if (riderCoord && (isNavigating || isFollowingCamera)) return riderCoord;
    if (origin) return [origin.lat, origin.lng];
    if (destination) return [destination.lat, destination.lng];
    return mapCenter;
  }, [riderCoord, isNavigating, isFollowingCamera, origin, destination, mapCenter]);

  // Split route into Traveled vs Remaining for Google Maps style progression
  const { traveledCoords, remainingCoords } = useMemo(() => {
    if (!routePath || routePath.length === 0) {
      return { traveledCoords: [], remainingCoords: [] };
    }

    if (!isNavigating || traveledIndex <= 0) {
      return { traveledCoords: [], remainingCoords: routePath };
    }

    const splitIdx = Math.min(traveledIndex, routePath.length - 1);
    const traveled = routePath.slice(0, splitIdx + 1);
    const remaining = routePath.slice(splitIdx);

    return { traveledCoords: traveled, remainingCoords: remaining };
  }, [routePath, isNavigating, traveledIndex]);

  // Rider Icon with quantized heading
  const riderIcon = useMemo(() => getRiderIcon(riderHeading), [riderHeading]);

  // Check if Origin is "My Location"
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

  return (
    <div className="h-full w-full relative z-0 touch-action-manipulation select-none overflow-hidden">
      <LeafletMapContainer
        center={activeCenter}
        zoom={mapZoom}
        scrollWheelZoom={true}
        className="h-full w-full z-0"
        zoomControl={false}
      >
        {/* Stadia Maps Tiles with Dark / Light Mode Support */}
        {theme === 'dark' ? (
          <TileLayer
            key="stadia-dark"
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
            url={`https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key=${STADIA_API_KEY}`}
            maxZoom={20}
            maxNativeZoom={18}
            keepBuffer={6}
          />
        ) : (
          <TileLayer
            key="stadia-light"
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
            url={`https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=${STADIA_API_KEY}`}
            maxZoom={20}
            maxNativeZoom={18}
            keepBuffer={6}
          />
        )}

        <MapCameraController
          center={activeCenter}
          routePath={routePath}
          isNavigating={isNavigating}
          isFollowingCamera={isFollowingCamera}
          gpsPosition={gpsPosition}
        />

        <MapClickListener
          origin={origin}
          destination={destination}
          activeInput={activeInput}
          onSelectOrigin={onSelectOrigin}
          onSelectDestination={onSelectDestination}
          onMapClick={onMapClick}
        />

        {/* Recenter Crosshair Control Inside Map Context (Bubble-Proof) */}
        <MapRecenterControl
          gpsPosition={gpsPosition}
          origin={origin}
          destination={destination}
          isNavigating={isNavigating}
          routePath={routePath}
          onRecenter={onRecenter}
        />

        {/* Origin Pin: Only shown for static distant routes when NOT actively navigating and NOT My Location */}
        {origin && !isNavigating && !isOriginMyLocation && (
          <Marker position={[origin.lat, origin.lng]} icon={originIcon}>
            <Popup>
              <div className="text-xs font-bold text-sky-500">
                Start: {origin.name || origin.address || 'Origin'}
              </div>
            </Popup>
          </Marker>
        )}

        {/* Destination Pin */}
        {destination && (
          <Marker position={[destination.lat, destination.lng]} icon={destIcon}>
            <Popup>
              <div className="text-xs font-bold text-orange-500">
                Destination: {destination.name || destination.address || 'Destination'}
              </div>
            </Popup>
          </Marker>
        )}

        {/* Rider GPS Position & Orientation Arrow */}
        {riderCoord && (
          <Marker position={riderCoord} icon={riderIcon} zIndexOffset={1000}>
            <Popup>
              <div className="text-xs font-semibold text-sky-500">
                Live Rider Location ({riderHeading}°)
              </div>
            </Popup>
          </Marker>
        )}

        {/* Traveled Route Polyline (Greyed Out) */}
        {traveledCoords.length > 1 && (
          <Polyline
            positions={traveledCoords}
            pathOptions={{
              color: '#64748b',
              weight: 5,
              opacity: 0.5,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />
        )}

        {/* Active Remaining Route Polyline */}
        {remainingCoords.length > 1 && (
          <>
            {/* Outline / Casing for High Contrast */}
            <Polyline
              positions={remainingCoords}
              pathOptions={{
                color: '#0f172a',
                weight: 8,
                opacity: 0.6,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
            {/* Main Vibrant Color Line */}
            <Polyline
              positions={remainingCoords}
              pathOptions={{
                color: mode === 'dynamic' ? '#f472b6' : '#38bdf8',
                weight: 5,
                opacity: 0.95,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
          </>
        )}
      </LeafletMapContainer>
    </div>
  );
};

export default MapContainer;