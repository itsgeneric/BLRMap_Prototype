'use client';

import React, { useState, useEffect, useRef } from 'react';
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

const sourceIcon = L.divIcon({
  className: '',
  html: `<div style="width:18px;height:18px;background:#38bdf8;border-radius:50%;border:3px solid #0f172a;box-shadow:0 0 14px #38bdf8;"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

const destIcon = L.divIcon({
  className: '',
  html: `<div style="width:18px;height:18px;background:#f97316;border-radius:50%;border:3px solid #0f172a;box-shadow:0 0 14px #f97316;"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

const createRiderDirectionIcon = (heading: number = 0) => L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
      <div style="position:absolute;inset:0;background:#0284c7;opacity:0.25;border-radius:50%;animation:ping 2s cubic-bezier(0,0,0.2,1) infinite;"></div>
      <div style="width:26px;height:26px;background:#0284c7;border-radius:50%;border:3px solid #ffffff;box-shadow:0 0 16px #38bdf8;display:flex;align-items:center;justify-content:center;transform:rotate(${heading}deg);transition:transform 0.1s linear;">
        <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-bottom:10px solid #ffffff;margin-bottom:3px;"></div>
      </div>
    </div>
  `,
  iconSize: [40, 40],
  iconAnchor: [20, 20],
});

function MapViewController({ center, zoom }: { center: [number, number]; zoom?: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom || map.getZoom(), { animate: false });
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
        address: `Point: ${coords[0]}, ${coords[1]}`,
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

  // Instant 0ms Recenter Function
  const handleRecenterGps = () => {
    const currentGps = gpsPosition ? [gpsPosition.lat, gpsPosition.lng] as [number, number] : userLocation;

    if (currentGps) {
      setMapCenter([...currentGps]);
      setMapZoom(18);
    }

    if (navigator.geolocation) {
      setLocLoading(true);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocLoading(false);
          const coords: [number, number] = [pos.coords.latitude, pos.coords.longitude];
          setUserLocation(coords);
          setMapCenter(coords);
          setMapZoom(18);
        },
        () => setLocLoading(false),
        { enableHighAccuracy: false, timeout: 2000, maximumAge: 10000 }
      );
    }
  };

  // Direct Global Event Listener (0ms Instant Trigger from NavigationFooter)
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
  }, [gpsPosition, userLocation]);

  useEffect(() => {
    if (isNavigating || isFollowingCamera) {
      handleRecenterGps();
    }
  }, [isFollowingCamera, isNavigating]);

  const currentRiderCoord: [number, number] | null = gpsPosition
    ? [gpsPosition.lat, gpsPosition.lng]
    : userLocation;

  const currentRiderHeading = gpsPosition?.heading ?? deviceHeading;

  const center: [number, number] = (isNavigating || isFollowingCamera) && currentRiderCoord
    ? currentRiderCoord
    : activeSource
      ? [activeSource.lat, activeSource.lng]
      : mapCenter;

  const polylineCoords = Array.isArray(routePath)
    ? routePath.map((pt: any) => (Array.isArray(pt) ? pt : [pt.lat, pt.lng]))
    : [];

  const darkTileUrl = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
  const lightTileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
  const tileUrl = theme === 'dark' ? darkTileUrl : lightTileUrl;

  return (
    <div className="h-full w-full relative z-0">
      {/* Floating Bottom-Right Target Button */}
      <button
        onClick={handleRecenterGps}
        title="Re-center on my location"
        className="absolute bottom-8 right-6 z-[1000] p-3.5 bg-slate-900/95 hover:bg-slate-800 backdrop-blur-md text-sky-400 border border-slate-800 rounded-full shadow-2xl transition transform active:scale-90 flex items-center justify-center cursor-pointer"
      >
        {locLoading ? (
          <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
        ) : (
          <Crosshair className="w-5 h-5 text-sky-400" />
        )}
      </button>

      <LeafletMapContainer
        center={center}
        zoom={mapZoom}
        scrollWheelZoom={true}
        className="h-full w-full z-0"
      >
        <TileLayer
          key={theme}
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OSM</a>'
          url={tileUrl}
        />

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
              <div className="text-xs font-semibold text-sky-600">Source: {activeSource.address || activeSource.name || 'Selected Start'}</div>
            </Popup>
          </Marker>
        )}

        {destination && (
          <Marker position={[destination.lat, destination.lng]} icon={destIcon}>
            <Popup>
              <div className="text-xs font-semibold text-orange-600">Destination: {destination.address || destination.name || 'Selected Destination'}</div>
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
            pathOptions={{ color: '#38bdf8', weight: 6, opacity: 0.85 }}
          />
        )}
      </LeafletMapContainer>
    </div>
  );
};

export const MapContainer = MapContainerComponent;
export default MapContainerComponent;
