'use client';

import React, { useState } from 'react';
import { Navigation, Eye, List, ChevronUp, ChevronDown } from 'lucide-react';
import { RouteResponse, RouteMode } from '@/lib/types';

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

  const handleStart = () => {
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(15);
    onStartNavigation();
  };

  const handlePreview = () => {
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(10);
    onStartPreview();
  };

  return (
    <div className="fixed bottom-3 sm:bottom-6 left-3 right-3 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-lg z-[1000] font-sans pb-[env(safe-area-inset-bottom)] transition-all">
      <div className="glass-panel-heavy rounded-3xl p-3.5 sm:p-4 shadow-2xl border border-slate-700/80 space-y-3">
        {/* Drawer Pull Handle (Visual Cue for Mobile) */}
        <div className="flex justify-center -mt-1 sm:hidden">
          <div className="w-10 h-1 rounded-full bg-slate-700"></div>
        </div>

        {/* Route Stats (ETA, Distance, Mode) */}
        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl sm:text-3xl font-black text-white font-mono">
                {routeData.distance_km ? `${routeData.distance_km} km` : '--'}
              </span>
              {routeData.google_base_duration_mins && (
                <span className="text-xs sm:text-sm font-bold text-pink-400 bg-pink-500/10 px-2 py-0.5 rounded-lg border border-pink-500/20">
                  ~{routeData.google_base_duration_mins} min live
                </span>
              )}
            </div>
            <div className="text-xs text-slate-400 font-medium mt-0.5 flex items-center gap-1.5 truncate">
              <span className="capitalize text-slate-300 font-semibold">
                {mode === 'shortest' ? 'Shortest Distance' : 'Dynamic BLR Route'}
              </span>
              <span>•</span>
              <span>{maneuvers.length} maneuvers</span>
            </div>
          </div>

          {/* Quick Steps Toggle Button */}
          {maneuvers.length > 0 && (
            <button
              onClick={() => setShowSteps(!showSteps)}
              className="px-3 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-200 rounded-2xl text-xs font-bold flex items-center gap-1.5 border border-slate-700 touch-press cursor-pointer shrink-0 shadow-sm"
            >
              <List className="w-3.5 h-3.5 text-sky-400" />
              <span>{showSteps ? 'Hide Steps' : 'Steps'}</span>
              {showSteps ? <ChevronDown className="w-3 h-3 text-slate-400" /> : <ChevronUp className="w-3 h-3 text-slate-400" />}
            </button>
          )}
        </div>

        {/* Expandable Step-by-Step Maneuver List */}
        {showSteps && maneuvers.length > 0 && (
          <div className="bg-slate-950/80 rounded-2xl p-3 border border-slate-800/80 max-h-52 overflow-y-auto space-y-2 no-scrollbar">
            <div className="text-[11px] uppercase tracking-wider font-mono text-sky-400 font-bold border-b border-slate-800 pb-1.5 flex items-center justify-between">
              <span>Turn-by-Turn Route Instructions</span>
              <span>{maneuvers.length} Total</span>
            </div>
            {maneuvers.map((m, idx) => (
              <div key={idx} className="flex items-start gap-2.5 text-xs py-1 border-b border-slate-800/40 last:border-0">
                <span className="font-mono text-slate-500 text-[10px] w-5 text-right shrink-0 mt-0.5">
                  {idx + 1}.
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-slate-200 font-semibold truncate">{m.instruction}</div>
                  {m.road_name && (
                    <div className="text-[10px] text-slate-400 truncate">{m.road_name}</div>
                  )}
                </div>
                <span className="font-mono text-sky-400 text-[11px] shrink-0 font-bold">
                  {m.distance_m}m
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Main CTA Actions (Start Navigation vs Preview Route) */}
        <div className="flex items-center gap-2 pt-0.5">
          {isOriginMyLocation ? (
            <button
              onClick={handleStart}
              className="flex-1 py-3 sm:py-3.5 bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 text-slate-950 font-black text-sm sm:text-base rounded-2xl shadow-xl shadow-emerald-500/25 transition-all flex items-center justify-center gap-2 touch-press cursor-pointer"
            >
              <Navigation className="w-4 h-4 fill-slate-950" />
              <span>Start Navigation</span>
            </button>
          ) : (
            <button
              onClick={handlePreview}
              className="flex-1 py-3 sm:py-3.5 bg-sky-500 hover:bg-sky-400 active:bg-sky-600 text-slate-950 font-black text-sm sm:text-base rounded-2xl shadow-xl shadow-sky-500/25 transition-all flex items-center justify-center gap-2 touch-press cursor-pointer"
            >
              <Eye className="w-4 h-4" />
              <span>Preview Route</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BottomActionBar;
