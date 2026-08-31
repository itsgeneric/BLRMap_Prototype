'use client';

import React from 'react';
import { Crosshair, X, Gauge, Compass } from 'lucide-react';
import { formatDistance, formatDuration, formatSpeed, calculateETA } from '@/lib/geo';

interface NavigationFooterProps {
  currentSpeedMps?: number | null;
  remainingMeters?: number;
  isFollowingCamera?: boolean;
  onRecenter?: () => void;
  onEndNavigation?: () => void;
}

export const NavigationFooter: React.FC<NavigationFooterProps> = ({
  currentSpeedMps,
  remainingMeters = 0,
  isFollowingCamera = true,
  onRecenter,
  onEndNavigation,
}) => {
  const displayDist = formatDistance(remainingMeters);
  const etaTime = calculateETA(remainingMeters, currentSpeedMps ?? null);
  const durationRemaining = formatDuration(
    Math.max(30, (remainingMeters / 1000 / (currentSpeedMps && currentSpeedMps > 1 ? currentSpeedMps * 3.6 : 28)) * 3600)
  );
  const speedText = formatSpeed(currentSpeedMps ?? null);

  return (
    <div className="fixed bottom-3 sm:bottom-6 left-3 right-3 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-lg z-[1000] font-sans pb-[env(safe-area-inset-bottom)] animate-in fade-in slide-in-from-bottom-2 duration-200">
      <div className="glass-panel-heavy rounded-3xl p-3.5 sm:p-4 text-slate-100 flex items-center justify-between gap-3 shadow-2xl border border-slate-700/80">
        {/* ETA & Distance Info */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xl sm:text-2xl font-black font-mono text-emerald-400">
              {durationRemaining}
            </span>
            <span className="text-xs sm:text-sm font-bold text-slate-300 font-mono">
              (ETA {etaTime})
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
            <span className="text-lime-400 font-semibold">Live GPS Active</span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Recenter Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (typeof window !== 'undefined') {
                if ('vibrate' in navigator) navigator.vibrate(10);
                window.dispatchEvent(new CustomEvent('recenter-map'));
              }
              if (onRecenter) onRecenter();
            }}
            title="Recenter rider camera"
            className={`flex items-center gap-1.5 px-3 py-2.5 sm:px-3.5 sm:py-2.5 rounded-2xl text-xs font-bold transition cursor-pointer shadow-md active:scale-95 border ${
              isFollowingCamera
                ? 'bg-sky-500/20 border-sky-500/40 text-sky-300'
                : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'
            }`}
          >
            <Crosshair className="w-4 h-4 text-sky-400" />
            <span className="hidden sm:inline">Recenter</span>
          </button>

          {/* End Navigation Button */}
          <button
            onClick={onEndNavigation}
            title="Exit Navigation"
            aria-label="Exit Navigation"
            className="p-2.5 sm:p-3 bg-red-500/20 hover:bg-red-500/30 active:bg-red-500/40 text-red-400 border border-red-500/40 rounded-2xl transition cursor-pointer shadow-md active:scale-95"
          >
            <X className="w-4 h-4 sm:w-5 sm:h-5 text-red-400" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default NavigationFooter;
