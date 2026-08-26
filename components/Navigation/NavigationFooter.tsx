'use client';

import React from 'react';
import { Crosshair, X } from 'lucide-react';
import { formatDistance, formatDuration } from '@/lib/geo';

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
  const displayDist = distanceRemaining || (remainingMeters ? formatDistance(remainingMeters) : '4.1 km');
  const displayTime = etaTime || (remainingMeters ? formatDuration((remainingMeters / 1000 / 30) * 3600) : '8 min');

  // Direct 0ms Instant Recenter Event Dispatcher
  const handleRecenterClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onRecenter) onRecenter();
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('recenter-map'));
    }
  };

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[1000] bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-3xl shadow-2xl px-5 py-3 text-slate-100 flex items-center justify-between gap-6 font-sans">
      <div>
        <div className="text-xl font-bold font-mono text-emerald-400">{displayTime}</div>
        <div className="text-xs font-mono text-slate-400">{displayDist}</div>
      </div>

      <div className="flex items-center gap-2">
        {/* Direct 0ms Recenter Button */}
        <button
          onClick={handleRecenterClick}
          title="Recenter rider camera instantly"
          className="flex items-center gap-1.5 px-3.5 py-2 bg-sky-500/20 hover:bg-sky-500/30 text-sky-400 border border-sky-500/40 rounded-xl text-xs font-semibold transition active:scale-95 cursor-pointer"
        >
          <Crosshair className="w-4 h-4" />
          <span>Recenter</span>
        </button>

        {/* Exit Button */}
        <button
          onClick={onEndNavigation}
          title="Exit Navigation"
          className="p-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/40 rounded-xl transition active:scale-95 cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default NavigationFooter;
