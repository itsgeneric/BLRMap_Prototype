'use client';

import React, { useState } from 'react';
import { Navigation, Eye, List, ChevronUp, ChevronDown } from 'lucide-react';
import { RouteResponse, RouteMode } from '@/lib/types';
import { cleanManeuverText, formatDistance } from '@/lib/geo';

interface BottomActionBarProps {
  routeData: RouteResponse | null;
  mode: RouteMode;
  isOriginMyLocation: boolean;
  onStartNavigation: () => void;
  onStartPreview: () => void;
}

export const BottomActionBar: React.FC<BottomActionBarProps> = ({
  routeData,
  mode,
  isOriginMyLocation,
  onStartNavigation,
  onStartPreview,
}) => {
  const [showSteps, setShowSteps] = useState(false);

  if (!routeData?.path || routeData.path.length < 2) return null;

  const maneuvers = routeData.maneuvers || [];
  const distanceKm = routeData.distance_km || 0;

  const durationMinutes = routeData.google_base_duration_mins
    ? Math.round(routeData.google_base_duration_mins)
    : Math.max(2, Math.round((distanceKm / 28) * 60));

  const handlePreviewClick = () => {
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(8);
    setShowSteps(!showSteps);
    onStartPreview();
  };

  const handleStartClick = () => {
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(12);
    onStartNavigation();
  };

  return (
    <div className="fixed bottom-2.5 sm:bottom-6 left-2.5 right-2.5 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-lg z-[1000] font-sans pb-[env(safe-area-inset-bottom)] transition-all animate-in fade-in slide-in-from-bottom-3 duration-200">
      <div className="bg-[#0f172a] rounded-2xl sm:rounded-3xl p-3 sm:p-4 shadow-2xl shadow-black/90 border border-slate-700/80 space-y-2 sm:space-y-3">
        {/* Visual Drawer Handle */}
        <div className="flex justify-center -mt-1 sm:hidden">
          <div className="w-8 h-1 rounded-full bg-slate-700"></div>
        </div>

        {/* Route Stats Header */}
        <div className="flex items-center justify-between gap-2 sm:gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-baseline gap-1.5 sm:gap-2">
              <span className="text-xl sm:text-3xl font-black text-white font-mono">
                {durationMinutes} min
              </span>
              <span className="text-xs sm:text-base font-bold text-slate-300 font-mono">
                ({distanceKm.toFixed(1)} km)
              </span>
              {routeData.google_base_duration_mins && (
                <span className="text-[9px] sm:text-xs font-bold text-pink-400 bg-pink-500/10 px-1.5 py-0.5 rounded-md border border-pink-500/20">
                  Live Traffic
                </span>
              )}
            </div>
            <div className="text-[11px] sm:text-xs text-slate-400 font-medium mt-0.5 flex items-center gap-1.5 truncate">
              <span className="capitalize text-slate-200 font-semibold">
                {mode === 'shortest' ? 'Shortest Distance' : 'Dynamic BLR Route'}
              </span>
              <span>•</span>
              <span>{maneuvers.length} maneuvers</span>
            </div>
          </div>

          {/* Quick Steps Toggle Button */}
          {maneuvers.length > 0 && (
            <button
              type="button"
              onClick={() => setShowSteps(!showSteps)}
              className="px-2.5 py-1.5 sm:px-3 sm:py-2 bg-slate-800/90 hover:bg-slate-700 active:scale-95 text-slate-200 rounded-xl sm:rounded-2xl text-[11px] sm:text-xs font-bold flex items-center gap-1 sm:gap-1.5 border border-slate-700 cursor-pointer shrink-0 shadow-sm transition"
            >
              <List className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-sky-400" />
              <span>{showSteps ? 'Hide' : 'Steps'}</span>
              {showSteps ? (
                <ChevronDown className="w-3 h-3 text-slate-400" />
              ) : (
                <ChevronUp className="w-3 h-3 text-slate-400" />
              )}
            </button>
          )}
        </div>

        {/* Expandable Step-by-Step Maneuvers Drawer */}
        {showSteps && maneuvers.length > 0 && (
          <div className="bg-[#090d16] rounded-xl sm:rounded-2xl p-2 sm:p-3 border border-slate-800 max-h-40 sm:max-h-52 overflow-y-auto space-y-1.5 no-scrollbar animate-in fade-in">
            <div className="text-[10px] sm:text-[11px] uppercase tracking-wider font-mono text-sky-400 font-bold border-b border-slate-800 pb-1 flex items-center justify-between">
              <span>Turn Instructions</span>
              <span>{maneuvers.length} Total</span>
            </div>
            {maneuvers.map((m, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between gap-2 text-xs py-1.5 border-b border-slate-800/40 last:border-0"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="font-mono text-slate-500 text-[10px] w-4 text-right shrink-0 font-bold">
                    {idx + 1}.
                  </span>
                  <div className="text-slate-200 font-bold truncate text-[11px] sm:text-xs">
                    {cleanManeuverText(m)}
                  </div>
                </div>
                <span className="font-mono text-sky-400 text-[10px] sm:text-[11px] shrink-0 font-bold">
                  {formatDistance(m.distance_m)}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Dynamic Action Button: Start Navigation vs Preview Route */}
        <div className="flex items-center gap-2 pt-0.5">
          {isOriginMyLocation ? (
            <button
              type="button"
              onClick={handleStartClick}
              className="flex-1 py-2.5 sm:py-3.5 bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 text-slate-950 font-black text-xs sm:text-sm rounded-xl sm:rounded-2xl shadow-xl shadow-emerald-500/25 transition-all flex items-center justify-center gap-1.5 sm:gap-2 cursor-pointer active:scale-95"
            >
              <Navigation className="w-3.5 h-3.5 sm:w-4 sm:h-4 fill-slate-950" />
              <span>Start Navigation</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={handlePreviewClick}
              className="flex-1 py-2.5 sm:py-3.5 bg-sky-500 hover:bg-sky-400 active:bg-sky-600 text-slate-950 font-black text-xs sm:text-sm rounded-xl sm:rounded-2xl shadow-xl shadow-sky-500/25 transition-all flex items-center justify-center gap-1.5 sm:gap-2 cursor-pointer active:scale-95"
            >
              <Eye className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span>Preview Route</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BottomActionBar;
