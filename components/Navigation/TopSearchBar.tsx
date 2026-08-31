'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowUpDown,
  Navigation,
  MapPin,
  Loader2,
  X,
  Search,
  Clock,
  Compass,
  Building2,
  ChevronRight,
} from 'lucide-react';
import { Point, SearchResult } from '@/lib/types';
import { searchPlaces } from '@/lib/api';

interface TopSearchBarProps {
  origin?: Point | null;
  destination?: Point | null;
  activeInput?: 'origin' | 'destination';
  setActiveInput?: (field: 'origin' | 'destination') => void;
  onSelectOrigin?: (loc: Point | null) => void;
  onSelectDestination?: (loc: Point | null) => void;
  onSwap?: () => void;
  onClear?: () => void;
  onUseGpsOrigin?: () => void;
  gpsLoading?: boolean;
  isNavigating?: boolean;
}

const RECENT_SEARCHES_KEY = 'blr_nav_recent_searches_v3';

const POPULAR_BLR_HUBS: SearchResult[] = [
  { name: 'MG Road Metro Station', address: 'MG Road, Shanthala Nagar, Ashok Nagar', lat: 12.9756, lng: 77.6066 },
  { name: 'Indiranagar 100ft Road', address: 'Indiranagar, Bengaluru, Karnataka', lat: 12.9784, lng: 77.6408 },
  { name: 'Koramangala 5th Block', address: 'Koramangala, Bengaluru, Karnataka', lat: 12.9352, lng: 77.6245 },
  { name: 'Electronic City Phase 1', address: 'Hosur Road, Bengaluru, Karnataka', lat: 12.8452, lng: 77.6602 },
  { name: 'Whitefield ITPL', address: 'Whitefield Main Rd, Pattandur Agrahara', lat: 12.9863, lng: 77.7346 },
];

export const TopSearchBar: React.FC<TopSearchBarProps> = ({
  origin,
  destination,
  activeInput = 'origin',
  setActiveInput,
  onSelectOrigin,
  onSelectDestination,
  onSwap,
  onClear,
  onUseGpsOrigin,
  gpsLoading = false,
  isNavigating = false,
}) => {
  const [fromQuery, setFromQuery] = useState('');
  const [toQuery, setToQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchResult[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [focusedField, setFocusedField] = useState<'origin' | 'destination' | null>(null);
  const [recentSearches, setRecentSearches] = useState<SearchResult[]>([]);

  const searchTimer = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Load Recent Searches
  useEffect(() => {
    try {
      const saved = localStorage.getItem(RECENT_SEARCHES_KEY);
      if (saved) {
        setRecentSearches(JSON.parse(saved).slice(0, 5));
      }
    } catch (e) {}
  }, []);

  const saveRecentSearch = (item: SearchResult) => {
    try {
      const updated = [item, ...recentSearches.filter((r) => r.name !== item.name)].slice(0, 5);
      setRecentSearches(updated);
      localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
    } catch (e) {}
  };

  // Sync prop changes
  useEffect(() => {
    if (origin) {
      setFromQuery(origin.name || origin.address || `${origin.lat.toFixed(4)}, ${origin.lng.toFixed(4)}`);
    } else {
      setFromQuery('');
    }
  }, [origin]);

  useEffect(() => {
    if (destination) {
      setToQuery(destination.name || destination.address || `${destination.lat.toFixed(4)}, ${destination.lng.toFixed(4)}`);
    } else {
      setToQuery('');
    }
  }, [destination]);

  // Click outside listener
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

  const handleQueryChange = (val: string, field: 'origin' | 'destination') => {
    if (field === 'origin') setFromQuery(val);
    else setToQuery(val);

    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (abortControllerRef.current) abortControllerRef.current.abort();

    if (val.trim().length < 2) {
      setSuggestions([]);
      setLoadingSearch(false);
      return;
    }

    setLoadingSearch(true);
    searchTimer.current = setTimeout(async () => {
      abortControllerRef.current = new AbortController();
      try {
        const results = await searchPlaces(val, abortControllerRef.current.signal);
        setSuggestions(results || []);
      } catch (err) {
        setSuggestions([]);
      } finally {
        setLoadingSearch(false);
      }
    }, 300);
  };

  const handleSelect = (item: SearchResult, field: 'origin' | 'destination') => {
    const loc: Point = {
      lat: item.lat,
      lng: item.lng,
      name: item.name,
      address: item.address || item.name,
    };

    saveRecentSearch(item);

    if (field === 'origin') {
      setFromQuery(item.name);
      if (onSelectOrigin) onSelectOrigin(loc);
    } else {
      setToQuery(item.name);
      if (onSelectDestination) onSelectDestination(loc);
    }

    setSuggestions([]);
    setFocusedField(null);
  };

  const showDropdown = focusedField !== null;

  return (
    <div ref={containerRef} className="w-full max-w-lg mx-auto font-sans relative z-[1000]">
      {/* Solid Compact Modern Search Container */}
      <div className="bg-[#0f172a] rounded-2xl sm:rounded-3xl p-2 sm:p-3.5 space-y-2 sm:space-y-3 shadow-2xl shadow-black/80 border border-slate-700/80">
        {/* Top Header Branding & Reset */}
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 border-b border-slate-800 pb-1.5 sm:pb-2">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
            <span className="font-bold text-slate-300 uppercase tracking-wider text-[10px] sm:text-[11px]">
              BLR Navigation Search
            </span>
          </div>
          {onClear && (origin || destination) && (
            <button
              type="button"
              onClick={onClear}
              className="text-slate-400 hover:text-red-400 active:text-red-400 transition flex items-center gap-1 text-[10px] sm:text-[11px] font-semibold cursor-pointer py-0.5 px-2 rounded-lg hover:bg-red-500/10 active:scale-95"
            >
              <X className="w-3 h-3" />
              <span>Clear</span>
            </button>
          )}
        </div>

        {/* Inputs Layout */}
        <div className="flex items-center gap-2 sm:gap-2.5 relative">
          {/* Connector Route Dots */}
          <div className="flex flex-col items-center justify-center self-stretch py-1.5 px-0.5 shrink-0">
            <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-sky-400 ring-2 sm:ring-4 ring-sky-500/20 shadow-sm"></div>
            <div className="w-0.5 flex-1 my-0.5 bg-gradient-to-b from-sky-400 via-slate-600 to-orange-500 min-h-[16px] sm:min-h-[22px]"></div>
            <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-orange-500 ring-2 sm:ring-4 ring-orange-500/20 shadow-sm"></div>
          </div>

          {/* Text Input Stack */}
          <div className="flex-1 space-y-1.5 sm:space-y-2 relative min-w-0">
            {/* Origin Input */}
            <div className="relative flex items-center">
              <input
                type="text"
                value={fromQuery}
                onChange={(e) => handleQueryChange(e.target.value, 'origin')}
                onFocus={() => {
                  setFocusedField('origin');
                  if (setActiveInput) setActiveInput('origin');
                }}
                placeholder="Choose start location or tap map..."
                className={`w-full bg-[#090d16] border text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 pl-3 pr-20 sm:pr-24 py-1.5 sm:py-2 rounded-xl sm:rounded-2xl outline-none transition duration-150 ${
                  focusedField === 'origin' || activeInput === 'origin'
                    ? 'border-sky-400 ring-2 ring-sky-500/25 bg-[#060910]'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              />

              {/* My Location GPS Button */}
              {onUseGpsOrigin && (
                <button
                  type="button"
                  onClick={onUseGpsOrigin}
                  title="Use current GPS location"
                  className="absolute right-1 px-2 py-1 sm:px-2.5 sm:py-1 bg-sky-500/10 hover:bg-sky-500/20 active:bg-sky-500/30 text-sky-400 border border-sky-500/30 rounded-lg sm:rounded-xl text-[10px] sm:text-[11px] font-bold flex items-center gap-1 transition active:scale-95 cursor-pointer shrink-0"
                >
                  {gpsLoading ? (
                    <Loader2 className="w-3 h-3 animate-spin text-sky-400" />
                  ) : (
                    <MapPin className="w-3 h-3" />
                  )}
                  <span>GPS</span>
                </button>
              )}
            </div>

            {/* Destination Input */}
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
                className={`w-full bg-[#090d16] border text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 pl-3 pr-8 py-1.5 sm:py-2 rounded-xl sm:rounded-2xl outline-none transition duration-150 ${
                  focusedField === 'destination' || activeInput === 'destination'
                    ? 'border-orange-400 ring-2 ring-orange-500/25 bg-[#060910]'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              />
              {toQuery && (
                <button
                  type="button"
                  onClick={() => {
                    setToQuery('');
                    if (onSelectDestination) onSelectDestination(null);
                  }}
                  className="absolute right-2 text-slate-400 hover:text-slate-200 p-1 cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Solid High-Contrast Results Dropdown */}
            {showDropdown && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-[#0f172a] border border-slate-700 rounded-2xl sm:rounded-3xl overflow-hidden shadow-2xl shadow-black/95 z-[2000] max-h-64 sm:max-h-72 overflow-y-auto no-scrollbar animate-in fade-in slide-in-from-top-1">
                {/* Searching Spinner */}
                {loadingSearch && (
                  <div className="p-3.5 text-xs text-slate-400 flex items-center justify-center gap-2 font-mono">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400" />
                    <span>Searching locations across Bengaluru...</span>
                  </div>
                )}

                {/* Search Results */}
                {!loadingSearch && suggestions.length > 0 && (
                  <div className="p-1.5 space-y-0.5">
                    <div className="px-2.5 py-1 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold flex items-center justify-between border-b border-slate-800 pb-1">
                      <span className="flex items-center gap-1.5 text-sky-400">
                        <Search className="w-3 h-3" />
                        <span>Matching Places</span>
                      </span>
                      <span>{suggestions.length} found</span>
                    </div>

                    {suggestions.map((item, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleSelect(item, focusedField!)}
                        className="group p-2 sm:p-2.5 hover:bg-[#1e293b] active:bg-[#334155] rounded-xl sm:rounded-2xl cursor-pointer transition flex items-center gap-2.5 border border-transparent hover:border-slate-700"
                      >
                        {/* Icon Badge */}
                        <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg sm:rounded-xl bg-[#1e293b] group-hover:bg-sky-500/20 border border-slate-700/80 group-hover:border-sky-500/40 flex items-center justify-center text-sky-400 shrink-0 transition">
                          <MapPin className="w-3.5 h-3.5" />
                        </div>
                        {/* Place Title & Subtitle */}
                        <div className="min-w-0 flex-1">
                          <div className="text-xs sm:text-sm font-bold text-slate-100 group-hover:text-white truncate">
                            {item.name}
                          </div>
                          {item.address && (
                            <div className="text-[10px] sm:text-[11px] text-slate-400 group-hover:text-slate-300 truncate mt-0.5 font-medium">
                              {item.address}
                            </div>
                          )}
                        </div>
                        <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300 shrink-0 transition" />
                      </div>
                    ))}
                  </div>
                )}

                {/* Empty Query: Show Recents & Popular Bangalore Hubs */}
                {!loadingSearch && suggestions.length === 0 && (
                  <div className="p-1.5 space-y-1.5">
                    {/* Recent Searches */}
                    {recentSearches.length > 0 && (
                      <div className="space-y-0.5">
                        <div className="px-2.5 py-1 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold flex items-center gap-1">
                          <Clock className="w-3 h-3 text-sky-400" />
                          <span>Recent Searches</span>
                        </div>
                        {recentSearches.map((item, idx) => (
                          <div
                            key={idx}
                            onClick={() => handleSelect(item, focusedField!)}
                            className="group p-2 sm:p-2.5 hover:bg-[#1e293b] active:bg-[#334155] rounded-xl sm:rounded-2xl cursor-pointer transition flex items-center gap-2.5 border border-transparent hover:border-slate-700"
                          >
                            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg sm:rounded-xl bg-[#1e293b] border border-slate-700/60 flex items-center justify-center text-slate-400 group-hover:text-sky-300 shrink-0 transition">
                              <Clock className="w-3.5 h-3.5" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="text-xs sm:text-sm font-bold text-slate-200 group-hover:text-white truncate">
                                {item.name}
                              </div>
                              {item.address && (
                                <div className="text-[10px] sm:text-[11px] text-slate-400 truncate mt-0.5">
                                  {item.address}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Popular Bangalore Locations */}
                    <div className="space-y-0.5 border-t border-slate-800 pt-1.5">
                      <div className="px-2.5 py-1 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold flex items-center gap-1">
                        <Compass className="w-3 h-3 text-emerald-400" />
                        <span>Popular Destinations</span>
                      </div>
                      {POPULAR_BLR_HUBS.map((item, idx) => (
                        <div
                          key={idx}
                          onClick={() => handleSelect(item, focusedField!)}
                          className="group p-2 sm:p-2.5 hover:bg-[#1e293b] active:bg-[#334155] rounded-xl sm:rounded-2xl cursor-pointer transition flex items-center gap-2.5 border border-transparent hover:border-slate-700"
                        >
                          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg sm:rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400 shrink-0 transition">
                            <Building2 className="w-3.5 h-3.5" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="text-xs sm:text-sm font-bold text-slate-200 group-hover:text-white truncate">
                              {item.name}
                            </div>
                            <div className="text-[10px] sm:text-[11px] text-slate-400 truncate mt-0.5">
                              {item.address}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Swap Button */}
          {onSwap && (
            <button
              type="button"
              onClick={onSwap}
              title="Swap Origin & Destination"
              className="p-2 sm:p-2.5 bg-[#1e293b] hover:bg-[#334155] active:scale-95 text-slate-200 hover:text-white rounded-xl sm:rounded-2xl border border-slate-700/80 shadow-md cursor-pointer shrink-0 self-center transition"
            >
              <ArrowUpDown className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-sky-400" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopSearchBar;
