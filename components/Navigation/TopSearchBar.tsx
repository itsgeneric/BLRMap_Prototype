'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ArrowUpDown, Navigation, MapPin, Loader2, X, Search } from 'lucide-react';
import { searchPlaces } from '@/lib/api';

interface TopSearchBarProps {
  origin?: any;
  source?: any;
  destination?: any;
  activeInput?: 'source' | 'destination';
  setActiveInput?: (field: 'source' | 'destination') => void;
  onSelectOrigin?: (loc: any) => void;
  onSelectSource?: (loc: any) => void;
  onSelectDestination?: (loc: any) => void;
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
  const activeSource = source || origin;
  const setSourceFn = onSelectSource || onSelectOrigin;

  const [fromQuery, setFromQuery] = useState('');
  const [toQuery, setToQuery] = useState('');
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<'source' | 'destination' | null>(null);

  const searchTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (activeSource) {
      setFromQuery(activeSource.name || activeSource.address || `${activeSource.lat}, ${activeSource.lng}`);
    } else {
      setFromQuery('');
    }
  }, [activeSource]);

  useEffect(() => {
    if (destination) {
      setToQuery(destination.name || destination.address || `${destination.lat}, ${destination.lng}`);
    } else {
      setToQuery('');
    }
  }, [destination]);

  if (isNavigating) return null;

  const handleQueryChange = (val: string, field: 'source' | 'destination') => {
    if (field === 'source') setFromQuery(val);
    else setToQuery(val);

    if (searchTimer.current) clearTimeout(searchTimer.current);

    if (val.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    setLoadingSearch(true);
    searchTimer.current = setTimeout(async () => {
      try {
        const results = await searchPlaces(val);
        setSuggestions(results || []);
      } catch (err) {
        setSuggestions([]);
      } finally {
        setLoadingSearch(false);
      }
    }, 300);
  };

  const handleSelectSuggestion = (item: any, field: 'source' | 'destination') => {
    const loc = {
      lat: item.lat,
      lng: item.lng,
      name: item.name,
      address: item.address || item.name,
    };

    if (field === 'source') {
      setFromQuery(item.name || item.address);
      if (setSourceFn) setSourceFn(loc);
    } else {
      setToQuery(item.name || item.address);
      if (onSelectDestination) onSelectDestination(loc);
    }

    setSuggestions([]);
    setFocusedField(null);
  };

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
        const loc = {
          lat: Number(pos.coords.latitude.toFixed(5)),
          lng: Number(pos.coords.longitude.toFixed(5)),
          name: 'My Location',
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

        <div className="flex items-center gap-2">
          <div className="flex-1 space-y-2 relative">
            {/* Source Box */}
            <div className="relative flex items-center">
              <div className="absolute left-3 w-2.5 h-2.5 rounded-full bg-sky-400 ring-4 ring-sky-500/20"></div>
              <input
                type="text"
                value={fromQuery}
                onChange={(e) => handleQueryChange(e.target.value, 'source')}
                onFocus={() => {
                  setFocusedField('source');
                  if (setActiveInput) setActiveInput('source');
                }}
                placeholder="Search or click map for Source..."
                className={`w-full bg-slate-950/90 border text-xs text-slate-200 pl-8 pr-24 py-2 rounded-xl outline-none transition ${
                  activeInput === 'source' || focusedField === 'source'
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
                value={toQuery}
                onChange={(e) => handleQueryChange(e.target.value, 'destination')}
                onFocus={() => {
                  setFocusedField('destination');
                  if (setActiveInput) setActiveInput('destination');
                }}
                placeholder="Search or click map for Destination..."
                className={`w-full bg-slate-950/90 border text-xs text-slate-200 pl-8 pr-3 py-2 rounded-xl outline-none transition ${
                  activeInput === 'destination' || focusedField === 'destination'
                    ? 'border-orange-500 ring-2 ring-orange-500/20'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              />
            </div>

            {/* Suggestions Overlay */}
            {focusedField && (suggestions.length > 0 || loadingSearch) && (
              <div className="absolute top-full left-0 right-0 mt-1.5 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl z-[2000] max-h-48 overflow-y-auto">
                {loadingSearch ? (
                  <div className="p-3 text-xs text-slate-400 flex items-center justify-center gap-2 font-mono">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400" /> Searching places...
                  </div>
                ) : (
                  suggestions.map((item, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleSelectSuggestion(item, focusedField)}
                      className="px-3 py-2.5 hover:bg-slate-800 cursor-pointer border-b border-slate-800/50 last:border-0 transition"
                    >
                      <div className="text-xs font-medium text-slate-100 flex items-center gap-1.5">
                        <Search className="w-3 h-3 text-sky-400 shrink-0" />
                        <span className="truncate">{item.name}</span>
                      </div>
                      {item.address && (
                        <div className="text-[10px] text-slate-400 truncate pl-4 mt-0.5">{item.address}</div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Swap Button */}
          {onSwap && (
            <button
              onClick={onSwap}
              title="Swap Origin & Destination"
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
