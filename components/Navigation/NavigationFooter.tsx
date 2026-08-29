'use client';

import React from 'react';
import { Crosshair, X, Gauge, Clock, Navigation } from 'lucide-react';
import { formatDistance, formatDuration, formatSpeed } from '@/lib/geo';

interface NavigationFooterProps {
  currentSpeedMps?: number | null;
  remainingMeters?: number;
  isFollowingCamera?: boolean;
  etaTime?: string;
  distanceRemaining?: string;
  onRecenter?: () => void;
  onEndNavigation?: () => void;
}

export const NavigationFooter: React.FC<NavigationFooterProps> = ({
  currentSpeedMps,
  remainingMeters = 0,
  isFollowingCamera,
  etaTime,
  distanceRemaining,
  onRecenter,
  onEndNavigation,
}) => {
  const displayDist = distanceRemaining || (remainingMeters ? formatDistance(remainingMeters) : '0 m');
  const displayTime = etaTime || (remainingMeters ? formatDuration((remainingMeters / 1000 / 30) * 3600) : '0 min');
  const speedText = formatSpeed(currentSpeedMps ?? null);

  // Direct 0ms Instant Recenter Event Dispatcher
  const handleRecenterClick = (e: React.MouseEvent | React.TouchEvent) => {
    e.stopPropagation();
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(10);
    if (onRecenter) onRecenter();
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('recenter-map'));
    }
  };

  const handleEndClick = (e: React.MouseEvent | React.TouchEvent) => {
    e.stopPropagation();
    if (typeof window !== 'undefined' && 'vibrate' in navigator) navigator.vibrate(15);
    if (onEndNavigation) onEndNavigation();
  };

  return (
    <div className="fixed bottom-4 sm:bottom-6 left-3 right-3 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-md z-[1000] font-sans pb-[env(safe-area-inset-bottom)]">
      <div className="glass-panel-heavy rounded-3xl p-3.5 sm:p-4 text-slate-100 flex items-center justify-between gap-3 shadow-2xl border border-slate-700/80">
        {/* ETA & Distance Info */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xl sm:text-2xl font-black font-mono text-emerald-400">
              {displayTime}
            </span>
            {/* Speed Badge */}
            <span className="px-2 py-0.5 rounded-lg bg-sky-500/15 border border-sky-500/30 text-sky-300 font-mono text-[11px] font-bold flex items-center gap-1 shrink-0">
              <Gauge className="w-3 h-3 text-sky-400" />
              <span>{speedText}</span>
            </span>
          </div>
          <div className="text-xs font-mono text-slate-400 mt-0.5 flex items-center gap-1.5 truncate">
            <span>{displayDist} remaining</span>
            <span>•</span>
            <span className="text-lime-400">Live GPS</span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Direct 0ms Recenter Button */}
          <button
            onClick={handleRecenterClick}
            title="Recenter rider camera"
            className="flex items-center gap-1.5 px-3.5 py-2.5 bg-sky-500/20 hover:bg-sky-500/30 active:bg-sky-500/40 text-sky-300 border border-sky-500/40 rounded-2xl text-xs font-bold transition touch-press cursor-pointer shadow-md"
          >
            <Crosshair className="w-4 h-4 text-sky-400" />
            <span className="hidden sm:inline">Recenter</span>
          </button>

          {/* End Navigation Button */}
          <button
            onClick={handleEndClick}
            title="Exit Navigation"
            aria-label="Exit Navigation"
            className="p-2.5 sm:p-3 bg-red-500/20 hover:bg-red-500/30 active:bg-red-500/40 text-red-400 border border-red-500/40 rounded-2xl transition touch-press cursor-pointer shadow-md"
          >
            <X className="w-4 h-4 sm:w-5 sm:h-5 text-red-400" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default NavigationFooter;
