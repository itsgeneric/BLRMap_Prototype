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
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Sync prop changes
  useEffect(() => {
    if (activeSource) {
      setFromQuery(activeSource.name || activeSource.address || `${activeSource.lat.toFixed(4)}, ${activeSource.lng.toFixed(4)}`);
    } else {
      setFromQuery('');
    }
  }, [activeSource]);

  useEffect(() => {
    if (destination) {
      setToQuery(destination.name || destination.address || `${destination.lat.toFixed(4)}, ${destination.lng.toFixed(4)}`);
    } else {
      setToQuery('');
    }
  }, [destination]);

  // Click outside listener to close suggestions
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent | TouchEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setFocusedField(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

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
    }, 250);
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

  const handleStartFromMyLocation = (e: React.MouseEvent | React.TouchEvent) => {
    e.stopPropagation();
    if (typeof window !== 'undefined' && 'vibrate' in navigator) {
      navigator.vibrate(10);
    }

    if (!navigator.geolocation) {
      alert('Geolocation is not supported on this device.');
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
      (err) => {
        setGpsLoading(false);
        console.warn('GPS location fetch failed:', err.message);
        alert('Could not access device GPS. Please check location permissions.');
      },
      { enableHighAccuracy: true, timeout: 6000 }
    );
  };

  return (
    <div ref={containerRef} className="w-full max-w-lg mx-auto font-sans relative z-[1000]">
      <div className="glass-panel-heavy rounded-3xl p-3 sm:p-4 space-y-2.5 shadow-2xl border border-slate-700/60">
        {/* Top Header Label & Clear Button */}
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 border-b border-slate-800 pb-2">
          <span className="flex items-center gap-1.5 font-bold text-sky-400">
            <Navigation className="w-3.5 h-3.5 fill-sky-400/20" />
            <span>BLR NAV ROUTER</span>
          </span>
          {onClear && (activeSource || destination) && (
            <button
              onClick={onClear}
              className="touch-press text-slate-400 hover:text-red-400 active:text-red-400 transition flex items-center gap-1 text-[11px] font-medium cursor-pointer py-0.5 px-2 rounded-lg hover:bg-red-500/10"
            >
              <X className="w-3 h-3" />
              <span>Reset</span>
            </button>
          )}
        </div>

        {/* Search Inputs Container */}
        <div className="flex items-center gap-2 relative">
          {/* Connector Dots Indicator on the left */}
          <div className="flex flex-col items-center justify-center self-stretch py-2.5 px-1 shrink-0">
            <div className="w-2.5 h-2.5 rounded-full bg-sky-400 ring-4 ring-sky-500/20 shadow-sm"></div>
            <div className="w-0.5 flex-1 my-1 bg-gradient-to-b from-sky-400 via-slate-700 to-orange-500 min-h-[22px]"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-orange-500 ring-4 ring-orange-500/20 shadow-sm"></div>
          </div>

          {/* Text Input Stack */}
          <div className="flex-1 space-y-2 relative min-w-0">
            {/* Origin / Source Box */}
            <div className="relative flex items-center">
              <input
                type="text"
                value={fromQuery}
                onChange={(e) => handleQueryChange(e.target.value, 'source')}
                onFocus={() => {
                  setFocusedField('source');
                  if (setActiveInput) setActiveInput('source');
                }}
                placeholder="Choose starting point or tap map..."
                className={`w-full bg-slate-950/80 border text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 pl-3 pr-24 py-2 sm:py-2.5 rounded-xl outline-none transition ${
                  activeInput === 'source' || focusedField === 'source'
                    ? 'border-sky-400 ring-2 ring-sky-500/20 bg-slate-950'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              />

              {/* My Location GPS Button */}
              <button
                onClick={handleStartFromMyLocation}
                title="Use current GPS location"
                className="absolute right-1.5 px-2.5 py-1 bg-sky-500/15 hover:bg-sky-500/25 active:bg-sky-500/35 text-sky-400 border border-sky-500/30 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition touch-press cursor-pointer shrink-0"
              >
                {gpsLoading ? (
                  <Loader2 className="w-3 h-3 animate-spin text-sky-400" />
                ) : (
                  <MapPin className="w-3 h-3" />
                )}
                <span>GPS</span>
              </button>
            </div>

            {/* Destination Box */}
            <div className="relative flex items-center">
              <input
                type="text"
                value={toQuery}
                onChange={(e) => handleQueryChange(e.target.value, 'destination')}
                onFocus={() => {
                  setFocusedField('destination');
                  if (setActiveInput) setActiveInput('destination');
                }}
                placeholder="Choose destination or tap map..."
                className={`w-full bg-slate-950/80 border text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 pl-3 pr-8 py-2 sm:py-2.5 rounded-xl outline-none transition ${
                  activeInput === 'destination' || focusedField === 'destination'
                    ? 'border-orange-400 ring-2 ring-orange-500/20 bg-slate-950'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              />
              {toQuery && (
                <button
                  onClick={() => {
                    setToQuery('');
                    if (onSelectDestination) onSelectDestination(null);
                  }}
                  className="absolute right-2 text-slate-400 hover:text-slate-200 p-1"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Autocomplete Dropdown */}
            {focusedField && (suggestions.length > 0 || loadingSearch) && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-slate-900/98 backdrop-blur-xl border border-slate-700/80 rounded-2xl overflow-hidden shadow-2xl z-[2000] max-h-56 overflow-y-auto">
                {loadingSearch ? (
                  <div className="p-3.5 text-xs text-slate-400 flex items-center justify-center gap-2 font-mono">
                    <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
                    <span>Searching Bengaluru locations...</span>
                  </div>
                ) : (
                  suggestions.map((item, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleSelectSuggestion(item, focusedField)}
                      className="px-3.5 py-2.5 hover:bg-slate-800/80 active:bg-slate-700/90 cursor-pointer border-b border-slate-800/60 last:border-0 transition flex items-center gap-2.5 touch-press"
                    >
                      <Search className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                      <div className="min-w-0 flex-1">
                        <div className="text-xs sm:text-sm font-semibold text-slate-100 truncate">
                          {item.name}
                        </div>
                        {item.address && (
                          <div className="text-[11px] text-slate-400 truncate mt-0.5">
                            {item.address}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Swap Button on the right */}
          {onSwap && (
            <button
              onClick={onSwap}
              title="Swap Origin & Destination"
              className="p-2.5 sm:p-3 bg-slate-800/90 hover:bg-slate-700 text-slate-300 hover:text-white rounded-2xl border border-slate-700/80 shadow-md touch-press cursor-pointer shrink-0 self-center active:scale-95 transition"
            >
              <ArrowUpDown className="w-4 h-4 text-sky-400" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopSearchBar;
