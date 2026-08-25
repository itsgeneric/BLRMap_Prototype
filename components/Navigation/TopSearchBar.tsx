'use client';

import React, { useState } from 'react';
import { ArrowUpDown, Navigation, MapPin, Loader2, X } from 'lucide-react';
import { LatLng } from '../Map/MapContainer';

interface TopSearchBarProps {
  origin?: LatLng | null;
  source?: LatLng | null;
  destination?: LatLng | null;
  activeInput?: 'source' | 'destination';
  setActiveInput?: (field: 'source' | 'destination') => void;
  onSelectOrigin?: (loc: LatLng | null) => void;
  onSelectSource?: (loc: LatLng | null) => void;
  onSelectDestination?: (loc: LatLng | null) => void;
  onSwap?: () => void;
  onClear?: () => void;
  isNavigating?: boolean;
}

export const TopSearchBar: React.FC<TopSearchBarProps> = ({
  origin,
  source,
  destination,
  activeInput = 'source',
  setActiveInput,
  onSelectOrigin,
  onSelectSource,
  onSelectDestination,
  onSwap,
  onClear,
  isNavigating = false,
}) => {
  const [gpsLoading, setGpsLoading] = useState(false);

  if (isNavigating) return null;

  const activeSource = source || origin;
  const setSourceFn = onSelectSource || onSelectOrigin;

  const handleStartFromMyLocation = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGpsLoading(false);
        const loc: LatLng = {
          lat: Number(pos.coords.latitude.toFixed(5)),
          lng: Number(pos.coords.longitude.toFixed(5)),
          address: 'My Location',
        };
        if (setSourceFn) setSourceFn(loc);
      },
      () => {
        setGpsLoading(false);
        alert('Could not fetch location permissions.');
      },
      { enableHighAccuracy: true }
    );
  };

  return (
    <div className="w-full max-w-md mx-auto space-y-2 font-sans relative z-[1000]">
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-2xl shadow-2xl p-3.5 space-y-2.5">
        {/* Header */}
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 border-b border-slate-800/80 pb-2">
          <span className="flex items-center gap-1.5 font-semibold text-sky-400">
            <Navigation className="w-3.5 h-3.5" /> BLR ROUTER — GMAPS
          </span>
          {onClear && (
            <button onClick={onClear} className="hover:text-red-400 transition cursor-pointer flex items-center gap-1 text-[11px]">
              <X className="w-3 h-3" /> Clear All
            </button>
          )}
        </div>

        {/* Inputs Row with Swap Button on Right Side */}
        <div className="flex items-center gap-2">
          <div className="flex-1 space-y-2">
            {/* Source Box */}
            <div className="relative flex items-center">
              <div className="absolute left-3 w-2.5 h-2.5 rounded-full bg-sky-400 ring-4 ring-sky-500/20"></div>
              <input
                type="text"
                readOnly
                onFocus={() => setActiveInput && setActiveInput('source')}
                value={activeSource ? activeSource.address || `${activeSource.lat}, ${activeSource.lng}` : ''}
                placeholder="Click map to set Source..."
                className={`w-full bg-slate-950/90 border text-xs text-slate-200 pl-8 pr-26 py-2 rounded-xl outline-none transition cursor-pointer ${activeInput === 'source'
                  ? 'border-sky-500 ring-2 ring-sky-500/20'
                  : 'border-slate-800 hover:border-slate-700'
                  }`}
              />
              <button
                onClick={handleStartFromMyLocation}
                title="Start from my current GPS location"
                className="absolute right-1.5 px-2 py-0.5 bg-sky-500/20 hover:bg-sky-500/30 text-sky-400 border border-sky-500/40 rounded-lg text-[10px] font-medium flex items-center gap-1 transition cursor-pointer"
              >
                {gpsLoading ? (
                  <Loader2 className="w-3 h-3 animate-spin text-sky-400" />
                ) : (
                  <MapPin className="w-3 h-3" />
                )}
                <span>My Location</span>
              </button>
            </div>

            {/* Destination Box */}
            <div className="relative flex items-center">
              <div className="absolute left-3 w-2.5 h-2.5 rounded-full bg-orange-500 ring-4 ring-orange-500/20"></div>
              <input
                type="text"
                readOnly
                onFocus={() => setActiveInput && setActiveInput('destination')}
                value={destination ? destination.address || `${destination.lat}, ${destination.lng}` : ''}
                placeholder="Click map to set Destination..."
                className={`w-full bg-slate-950/90 border text-xs text-slate-200 pl-8 pr-3 py-2 rounded-xl outline-none transition cursor-pointer ${activeInput === 'destination'
                  ? 'border-orange-500 ring-2 ring-orange-500/20'
                  : 'border-slate-800 hover:border-slate-700'
                  }`}
              />
            </div>
          </div>

          {/* Swap Button on Right side */}
          {onSwap && (
            <button
              onClick={onSwap}
              title="Swap Source & Destination"
              className="p-2.5 bg-slate-800/90 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl border border-slate-700/80 shadow transition cursor-pointer shrink-0 self-center"
            >
              <ArrowUpDown className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopSearchBar;
