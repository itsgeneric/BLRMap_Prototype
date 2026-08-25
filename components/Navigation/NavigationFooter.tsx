'use client';

import React from 'react';
import { Compass, X, Gauge, Clock, Navigation, LocateFixed } from 'lucide-react';
import { formatDistance, formatDuration, formatSpeed, calculateETA } from '@/lib/geo';

interface NavigationFooterProps {
  currentSpeedMps: number | null;
  remainingMeters: number;
  isFollowingCamera: boolean;
  onRecenter: () => void;
  onEndNavigation: () => void;
}

export const NavigationFooter: React.FC<NavigationFooterProps> = ({
  currentSpeedMps,
  remainingMeters,
  isFollowingCamera,
  onRecenter,
  onEndNavigation,
}) => {
  const eta = calculateETA(remainingMeters, currentSpeedMps);
  const remainingSeconds = (remainingMeters / 1000 / 25) * 3600; // Estimated at 25km/h

  return (
    <div className="w-full max-w-lg mx-auto glass-panel p-4 rounded-3xl shadow-2xl flex items-center justify-between gap-4 border-slate-700/60">
      {/* Speed Display */}
      <div className="flex items-center gap-2">
        <div className="p-2 rounded-xl bg-sky-500/10 text-sky-400">
          <Gauge className="w-5 h-5" />
        </div>
        <div>
          <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Speed</div>
          <div className="text-base font-black text-slate-100">{formatSpeed(currentSpeedMps)}</div>
        </div>
      </div>

      {/* ETA & Remaining Time */}
      <div className="text-center">
        <div className="text-xl font-black text-emerald-400 tracking-tight">{eta}</div>
        <div className="text-xs font-semibold text-slate-400 flex items-center justify-center gap-1">
          <span>{formatDuration(remainingSeconds)}</span>
          <span>•</span>
          <span>{formatDistance(remainingMeters)}</span>
        </div>
      </div>

      {/* Controls: Recenter & Stop */}
      <div className="flex items-center gap-2">
        <button
          onClick={onRecenter}
          className={`p-2.5 rounded-xl border transition-all ${
            isFollowingCamera
              ? 'bg-sky-500/20 border-sky-400/40 text-sky-400'
              : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-slate-200'
          }`}
          title="Recenter Camera on GPS Position"
        >
          <LocateFixed className="w-5 h-5" />
        </button>

        <button
          onClick={onEndNavigation}
          className="p-2.5 rounded-xl bg-red-500/20 border border-red-500/40 text-red-400 hover:bg-red-500/30 transition-colors"
          title="End Navigation"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
