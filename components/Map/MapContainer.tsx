'use client';

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { MapContainer as LeafletMapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Crosshair, Loader2 } from 'lucide-react';

export interface LatLng {
  lat: number;
  lng: number;
  address?: string;
  name?: string;
}

interface MapContainerProps {
  origin?: LatLng | any;
  source?: LatLng | any;
  destination?: LatLng | any;
  activeInput?: 'source' | 'destination';
  theme?: 'dark' | 'light' | string;
  mode?: string;
  gpsPosition?: any;
  isFollowingCamera?: boolean;
  isNavigating?: boolean;
  onSelectSource?: (location: LatLng) => void;
  onSelectDestination?: (location: LatLng) => void;
  onMapClick?: (latlng: [number, number]) => void;
  routePath?: any;
}

const STADIA_API_KEY = process.env.NEXT_PUBLIC_STADIA_KEY || '';

// Custom Map Markers
const sourceIcon = L.divIcon({
  className: '',
  html: `<div style="width:20px;height:20px;background:#38bdf8;border-radius:50%;border:3px solid #0f172a;box-shadow:0 0 16px #38bdf8;transform:translateZ(0);"></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

const destIcon = L.divIcon({
  className: '',
  html: `<div style="width:20px;height:20px;background:#f97316;border-radius:50%;border:3px solid #0f172a;box-shadow:0 0 16px #f97316;transform:translateZ(0);"></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

const createRiderDirectionIcon = (heading: number = 0) => L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:44px;height:44px;display:flex;align-items:center;justify-content:center;transform:translateZ(0);">
      <div style="position:absolute;inset:0;background:#0284c7;opacity:0.25;border-radius:50%;animation:ping 2s cubic-bezier(0,0,0.2,1) infinite;"></div>
      <div style="width:28px;height:28px;background:#0284c7;border-radius:50%;border:3px solid #ffffff;box-shadow:0 0 18px #38bdf8;display:flex;align-items:center;justify-content:center;transform:rotate(${heading}deg);transition:transform 0.15s ease-out;">
        <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-bottom:11px solid #ffffff;margin-bottom:3px;"></div>
      </div>
    </div>
  `,
  iconSize: [44, 44],
  iconAnchor: [22, 22],
});

function MapViewController({ center, zoom }: { center: [number, number]; zoom?: number }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, zoom || map.getZoom(), { animate: false });
    }
  }, [center, zoom, map]);
  return null;
}

function MapClickListener({
  source,
  destination,
  activeInput,
  onSelectSource,
  onSelectDestination,
  onMapClick,
}: {
  source?: LatLng | null;
  destination?: LatLng | null;
  activeInput: 'source' | 'destination';
  onSelectSource?: (loc: LatLng) => void;
  onSelectDestination?: (loc: LatLng) => void;
  onMapClick?: (latlng: [number, number]) => void;
}) {
  const sourceRef = useRef(source);
  const destRef = useRef(destination);
  const activeInputRef = useRef(activeInput);

  useEffect(() => { sourceRef.current = source; }, [source]);
  useEffect(() => { destRef.current = destination; }, [destination]);
  useEffect(() => { activeInputRef.current = activeInput; }, [activeInput]);

  useMapEvents({
    click(e: L.LeafletMouseEvent) {
      const coords: [number, number] = [Number(e.latlng.lat.toFixed(5)), Number(e.latlng.lng.toFixed(5))];
      const loc: LatLng = {
        lat: coords[0],
        lng: coords[1],
        address: `${coords[0]}, ${coords[1]}`,
        name: `${coords[0]}, ${coords[1]}`,
      };

      if (onMapClick) {
        onMapClick(coords);
      }

      const curSource = sourceRef.current;
      const curDest = destRef.current;
      const curActive = activeInputRef.current;

      if (curActive === 'destination' && onSelectDestination) {
        onSelectDestination(loc);
      } else if (curActive === 'source' && onSelectSource) {
        onSelectSource(loc);
      } else if (!curSource && onSelectSource) {
        onSelectSource(loc);
      } else if (!curDest && onSelectDestination) {
        onSelectDestination(loc);
      } else if (onSelectDestination) {
        onSelectDestination(loc);
      }
    },
  });

  return null;
}

export const MapContainerComponent: React.FC<MapContainerProps> = ({
  origin,
  source,
  destination,
  activeInput = 'source',
  theme = 'dark',
  mode = 'shortest',
  gpsPosition,
  isFollowingCamera = false,
  isNavigating = false,
  onSelectSource,
  onSelectDestination,
  onMapClick,
  routePath,
}) => {
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [deviceHeading, setDeviceHeading] = useState<number>(0);
  const [mapCenter, setMapCenter] = useState<[number, number]>([12.9716, 77.5946]);
  const [mapZoom, setMapZoom] = useState<number>(13);
  const [locLoading, setLocLoading] = useState(false);

  const activeSource = source || origin;

  // Background GPS Watcher
  useEffect(() => {
    if (typeof window === 'undefined' || !navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
      (pos) => setUserLocation([pos.coords.latitude, pos.coords.longitude]),
      undefined,
      { enableHighAccuracy: true, maximumAge: 30000, timeout: 3000 }
    );

    const watchId = navigator.geolocation.watchPosition(
      (pos) => setUserLocation([pos.coords.latitude, pos.coords.longitude]),
      undefined,
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 4000 }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

  // Real-time Compass Orientation
  useEffect(() => {
    const handleOrientation = (e: DeviceOrientationEvent) => {
      if (e.alpha !== null) {
        const compass = (e as any).webkitCompassHeading || (360 - e.alpha);
        setDeviceHeading(Math.round(compass));
      }
    };

    if (typeof window !== 'undefined' && window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientation', handleOrientation, true);
    }
    return () => {
      if (typeof window !== 'undefined' && window.DeviceOrientationEvent) {
        window.removeEventListener('deviceorientation', handleOrientation, true);
      }
    };
  }, []);

  // Instant 0ms Recenter Handler
  const handleRecenterGps = useCallback(() => {
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(8);
    const existing = gpsPosition ? [gpsPosition.lat, gpsPosition.lng] as [number, number] : userLocation;

    if (existing) {
      setMapCenter([...existing]);
      setMapZoom(16);
      return;
    }

    if (typeof window !== 'undefined' && navigator.geolocation) {
      setLocLoading(true);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocLoading(false);
          const coords: [number, number] = [pos.coords.latitude, pos.coords.longitude];
          setUserLocation(coords);
          setMapCenter(coords);
          setMapZoom(16);
        },
        () => setLocLoading(false),
        { enableHighAccuracy: true, maximumAge: 30000, timeout: 3000 }
      );
    }
  }, [gpsPosition, userLocation]);

  // Global Recenter Event Listener
  useEffect(() => {
    const handleGlobalRecenter = () => {
      handleRecenterGps();
    };
    if (typeof window !== 'undefined') {
      window.addEventListener('recenter-map', handleGlobalRecenter);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('recenter-map', handleGlobalRecenter);
      }
    };
  }, [handleRecenterGps]);

  const currentRiderCoord: [number, number] | null = gpsPosition
    ? [gpsPosition.lat, gpsPosition.lng]
    : userLocation;

  const currentRiderHeading = gpsPosition?.heading ?? deviceHeading;

  const center: [number, number] = (isNavigating || isFollowingCamera) && currentRiderCoord
    ? currentRiderCoord
    : activeSource
      ? [activeSource.lat, activeSource.lng]
      : mapCenter;

  const polylineCoords = useMemo(() => {
    if (!routePath || !Array.isArray(routePath)) return [];
    return routePath.map((pt: any) => (Array.isArray(pt) ? pt : [pt.lat, pt.lng]));
  }, [routePath]);

  // Calculate dynamic bottom spacing for Floating FAB to avoid overlapping with bottom drawer/panels
  const fabBottomClass = isNavigating
    ? 'bottom-28 sm:bottom-28'
    : routePath && routePath.length > 0
      ? 'bottom-32 sm:bottom-32'
      : 'bottom-6 sm:bottom-8';

  return (
    <div className="h-full w-full relative z-0 touch-action-manipulation">
      {/* Floating Target Location Button */}
      <button
        onClick={handleRecenterGps}
        title="Re-center on my location"
        className={`absolute ${fabBottomClass} right-4 sm:right-6 z-[1000] p-3 sm:p-3.5 glass-panel-heavy hover:bg-slate-800 text-sky-400 border border-slate-700/80 rounded-2xl sm:rounded-full shadow-2xl transition-all touch-press flex items-center justify-center cursor-pointer`}
      >
        {locLoading ? (
          <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
        ) : (
          <Crosshair className="w-5 h-5 sm:w-6 sm:h-6 text-sky-400" />
        )}
      </button>

      <LeafletMapContainer
        center={center}
        zoom={mapZoom}
        scrollWheelZoom={true}
        className="h-full w-full z-0"
      >
        {/* Stadia Maps Dark & Light Tile Swap */}
        {theme === 'dark' ? (
          <TileLayer
            key="stadia-dark-layer"
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
            url={`https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key=${STADIA_API_KEY}`}
            maxZoom={19}
            maxNativeZoom={18}
            updateWhenIdle={true}
            updateWhenZooming={false}
            keepBuffer={4}
          />
        ) : (
          <TileLayer
            key="stadia-light-layer"
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
            url={`https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=${STADIA_API_KEY}`}
            maxZoom={19}
            maxNativeZoom={18}
            updateWhenIdle={true}
            updateWhenZooming={false}
            keepBuffer={4}
          />
        )}

        <MapViewController center={center} zoom={mapZoom} />

        <MapClickListener
          source={activeSource}
          destination={destination}
          activeInput={activeInput}
          onSelectSource={onSelectSource}
          onSelectDestination={onSelectDestination}
          onMapClick={onMapClick}
        />

        {activeSource && (
          <Marker position={[activeSource.lat, activeSource.lng]} icon={sourceIcon}>
            <Popup>
              <div className="text-xs font-semibold text-sky-600">Start: {activeSource.address || activeSource.name || 'Origin'}</div>
            </Popup>
          </Marker>
        )}

        {destination && (
          <Marker position={[destination.lat, destination.lng]} icon={destIcon}>
            <Popup>
              <div className="text-xs font-semibold text-orange-600">Destination: {destination.address || destination.name || 'Destination'}</div>
            </Popup>
          </Marker>
        )}

        {currentRiderCoord && (
          <Marker position={currentRiderCoord} icon={createRiderDirectionIcon(currentRiderHeading)}>
            <Popup>
              <div className="text-xs font-semibold text-emerald-600">Rider Position ({currentRiderHeading}° heading)</div>
            </Popup>
          </Marker>
        )}

        {polylineCoords.length > 0 && (
          <Polyline
            positions={polylineCoords}
            pathOptions={{
              color: mode === 'dynamic' ? '#f472b6' : '#38bdf8',
              weight: 6,
              opacity: 0.9,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />
        )}
      </LeafletMapContainer>
    </div>
  );
};

export const MapContainer = MapContainerComponent;
export default MapContainerComponent;