'use client';

import React from 'react';
import { Crosshair, X } from 'lucide-react';
import { formatDistance } from '@/lib/geo';
import { formatClock, formatRemaining } from '@/lib/eta';

interface NavigationFooterProps {
  /** remaining time in seconds (counts down every second) */
  remainingSeconds: number;
  /** estimated arrival, epoch milliseconds (0 = not known yet) */
  arrivalMs: number;
  remainingMeters: number;
  /** smoothed speed, whole km/h */
  speedKmh: number;
  isFollowingCamera?: boolean;
  onRecenter?: () => void;
  onEndNavigation?: () => void;
}

/** Bottom bar while navigating: arrival time, time left, distance left and a speedometer, the way Google Maps lays them out. */
export const NavigationFooter: React.FC<NavigationFooterProps> = ({
  remainingSeconds,
  arrivalMs,
  remainingMeters,
  speedKmh,
  isFollowingCamera = true,
  onRecenter,
  onEndNavigation,
}) => {
  const hasEta = arrivalMs > 0;

  const recenter = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (typeof window !== 'undefined') {
      if ('vibrate' in navigator) navigator.vibrate(12);
      window.dispatchEvent(new CustomEvent('recenter-map'));
    }
    onRecenter?.();
  };

  return (
    <div className="fixed bottom-2.5 sm:bottom-4 left-2.5 right-2.5 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-lg z-[1000] font-sans pb-[env(safe-area-inset-bottom)]">
      {/* Re-center pill: appears after the rider drags the map away from their position */}
      {!isFollowingCamera && (
        <div className="absolute -top-14 left-1/2 -translate-x-1/2 z-[1002]">
          <button
            type="button"
            onClick={recenter}
            className="bg-white active:bg-slate-100 text-[#1a73e8] px-5 min-h-[44px] rounded-full shadow-2xl shadow-black/30 border border-slate-200 flex items-center gap-2 font-bold text-sm"
          >
            <Crosshair className="w-4 h-4" />
            <span>Re-center</span>
          </button>
        </div>
      )}

      <div className="bg-white rounded-3xl px-4 py-3 text-slate-900 flex items-center gap-3 shadow-2xl shadow-black/25 border border-slate-200">
        {/* Speedometer */}
        <div className="shrink-0 w-[60px] h-[60px] rounded-full border-[3px] border-slate-200 flex flex-col items-center justify-center bg-slate-50" aria-label="Speed">
          <span className="text-xl font-black leading-none tabular-nums">{speedKmh}</span>
          <span className="text-[9px] font-bold text-slate-500 leading-none mt-0.5">km/h</span>
        </div>

        {/* Time left, arrival and distance */}
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2 flex-wrap">
            <span className="text-2xl font-black text-[#188038] leading-none tabular-nums">
              {hasEta ? formatRemaining(remainingSeconds) : '–'}
            </span>
            {hasEta && (
              <span className="text-sm font-bold text-slate-500 tabular-nums">{formatClock(arrivalMs)}</span>
            )}
          </div>
          <div className="text-xs font-semibold text-slate-500 mt-1 tabular-nums">
            {formatDistance(remainingMeters)} remaining
          </div>
        </div>

        {/* End trip */}
        <button
          type="button"
          onClick={onEndNavigation}
          title="End navigation"
          aria-label="End navigation"
          className="shrink-0 w-12 h-12 bg-[#d93025] active:bg-[#b3261e] text-white rounded-full flex items-center justify-center shadow-md shadow-red-500/25"
        >
          <X className="w-6 h-6 stroke-[2.5]" />
        </button>
      </div>
    </div>
  );
};

export default NavigationFooter;
