'use client';

import React, { useState, useEffect, useRef } from 'react';
import { MapContainer as LeafletMapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Crosshair, Loader2 } from 'lucide-react';

export interface LatLng {
  lat: number;
  lng: number;
  address?: string;
}

interface MapContainerProps {
  origin?: LatLng | null;
  source?: LatLng | null;
  destination?: LatLng | null;
  activeInput?: 'source' | 'destination';
  theme?: 'dark' | 'light' | string;
  onSelectSource?: (location: LatLng) => void;
  onSelectDestination?: (location: LatLng) => void;
  onMapClick?: (latlng: [number, number]) => void;
  routePath?: any;
  isNavigating?: boolean;
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

const userGpsIcon = L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:24px;height:24px;display:flex;align-items:center;justify-content:center;">
      <div style="position:absolute;inset:0;background:#10b981;opacity:0.35;border-radius:50%;animation:ping 1.5s cubic-bezier(0,0,0.2,1) infinite;"></div>
      <div style="width:18px;height:18px;background:#10b981;border-radius:50%;border:3px solid #ffffff;box-shadow:0 0 14px #10b981;"></div>
    </div>
  `,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

function MapViewController({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, map.getZoom(), { duration: 1.2 });
  }, [center, map]);
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
  onSelectSource,
  onSelectDestination,
  onMapClick,
  routePath,
}) => {
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [mapCenter, setMapCenter] = useState<[number, number]>([12.9716, 77.5946]);
  const [locLoading, setLocLoading] = useState(false);

  const activeSource = source || origin;

  const handleRecenterGps = () => {
    if (!navigator.geolocation) {
      alert('GPS is not supported by your browser.');
      return;
    }
    setLocLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocLoading(false);
        const coords: [number, number] = [pos.coords.latitude, pos.coords.longitude];
        setUserLocation(coords);
        setMapCenter(coords);
      },
      () => {
        setLocLoading(false);
        alert('Could not fetch location permissions.');
      },
      { enableHighAccuracy: true }
    );
  };

  const center: [number, number] = activeSource
    ? [activeSource.lat, activeSource.lng]
    : mapCenter;

  const polylineCoords = Array.isArray(routePath)
    ? routePath.map((pt: any) => (Array.isArray(pt) ? pt : [pt.lat, pt.lng]))
    : [];

  // Dark vs Light Tile URL
  const darkTileUrl = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
  const lightTileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
  const tileUrl = theme === 'dark' ? darkTileUrl : lightTileUrl;

  return (
    <div className="h-full w-full relative z-0">
      {/* Floating Bottom-Right Location Button */}
      <button
        onClick={handleRecenterGps}
        title="Show my current location"
        className="absolute bottom-8 right-6 z-[1000] p-3.5 bg-slate-900/95 hover:bg-slate-800 backdrop-blur-md text-sky-400 border border-slate-800 rounded-full shadow-2xl transition transform active:scale-90 flex items-center justify-center cursor-pointer"
      >
        {locLoading ? (
          <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
        ) : (
          <Crosshair className="w-5 h-5" />
        )}
      </button>

      <LeafletMapContainer
        center={center}
        zoom={13}
        scrollWheelZoom={true}
        className="h-full w-full z-0"
      >
        {/* Dynamic Dark / Light Tiles with Key for Instant Switch */}
        <TileLayer
          key={theme}
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OSM</a>'
          url={tileUrl}
        />

        <MapViewController center={center} />

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
              <div className="text-xs font-semibold text-sky-600">Source: {activeSource.address || 'Selected Start'}</div>
            </Popup>
          </Marker>
        )}

        {destination && (
          <Marker position={[destination.lat, destination.lng]} icon={destIcon}>
            <Popup>
              <div className="text-xs font-semibold text-orange-600">Destination: {destination.address || 'Selected Destination'}</div>
            </Popup>
          </Marker>
        )}

        {userLocation && (
          <Marker position={userLocation} icon={userGpsIcon}>
            <Popup>
              <div className="text-xs font-semibold text-emerald-600">Your Current Location</div>
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
