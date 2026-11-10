'use client';

import React from 'react';
import { Crosshair, X, Gauge } from 'lucide-react';
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
    <div className="fixed bottom-2.5 sm:bottom-4 left-2.5 right-2.5 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-lg z-[1000] font-sans pb-[env(safe-area-inset-bottom)] animate-in fade-in slide-in-from-bottom-2 duration-200">
      {/* Google Maps Authentic Navigation Footer Card */}
      <div className="bg-white rounded-3xl p-3.5 sm:p-4 text-slate-900 flex items-center justify-between gap-3 shadow-2xl shadow-black/25 border border-slate-200">
        {/* ETA & Distance Info */}
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2 flex-wrap">
            <span className="text-2xl sm:text-3xl font-black font-mono text-[#188038] leading-none tracking-tight">
              {durationRemaining}
            </span>
            <span className="text-xs sm:text-sm font-bold text-slate-500 font-mono">
              ({etaTime})
            </span>
            {/* Speed Badge */}
            <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-mono text-[11px] font-bold flex items-center gap-1 shrink-0">
              <Gauge className="w-3 h-3 text-[#1a73e8]" />
              <span>{speedText}</span>
            </span>
          </div>
          <div className="text-xs font-semibold text-slate-500 mt-1 flex items-center gap-1.5 truncate">
            <span>{displayDist} remaining</span>
            <span>•</span>
            <span className="text-[#188038] font-bold">Bangalore GPS Active</span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Recenter Button inside Navigation HUD */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              if (typeof window !== 'undefined') {
                if ('vibrate' in navigator) navigator.vibrate(10);
                window.dispatchEvent(new CustomEvent('recenter-map'));
              }
              if (onRecenter) onRecenter();
            }}
            title="Recenter camera"
            className={`flex items-center gap-1.5 p-2.5 rounded-full text-xs font-bold transition cursor-pointer shadow-sm active:scale-95 border ${
              isFollowingCamera
                ? 'bg-blue-50 border-blue-200 text-[#1a73e8]'
                : 'bg-slate-100 border-slate-200 text-slate-600 hover:text-slate-900'
            }`}
          >
            <Crosshair className="w-4 h-4 text-[#1a73e8]" />
            <span className="hidden sm:inline">Recenter</span>
          </button>

          {/* Google Maps Circular Red Close / End Navigation Button */}
          <button
            type="button"
            onClick={onEndNavigation}
            title="Exit Navigation"
            aria-label="Exit Navigation"
            className="w-10 h-10 sm:w-11 sm:h-11 bg-[#d93025] hover:bg-[#b3261e] active:scale-95 text-white rounded-full flex items-center justify-center transition cursor-pointer shadow-md shadow-red-500/25"
          >
            <X className="w-5 h-5 text-white stroke-[2.5]" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default NavigationFooter;
