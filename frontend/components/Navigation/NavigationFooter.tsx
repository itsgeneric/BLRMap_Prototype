'use client';

/**
 * Bottom trip sheet during navigation: exit button, time remaining (large, green),
 * distance remaining and arrival time, and a route-overview button. Above it sit
 * the speed bubble and, after the user pans the map, the "Re-centre" button.
 */
import React from 'react';
import { X, Route, Navigation2 } from 'lucide-react';
import { formatClock, formatRemainingDistance, formatRemainingTime } from '@/lib/navigation';

interface NavigationFooterProps {
  remainingSeconds: number;
  remainingMeters: number;
  currentSpeedMps: number | null;
  isFollowingCamera: boolean;
  onRecenter: () => void;
  onOverview: () => void;
  onEndNavigation: () => void;
}

export const NavigationFooter: React.FC<NavigationFooterProps> = ({
  remainingSeconds,
  remainingMeters,
  currentSpeedMps,
  isFollowingCamera,
  onRecenter,
  onOverview,
  onEndNavigation,
}) => {
  const eta = new Date(Date.now() + remainingSeconds * 1000);
  const speedKmh = currentSpeedMps && currentSpeedMps > 0.5 ? Math.round(currentSpeedMps * 3.6) : 0;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[1000] font-sans pointer-events-none">
      {/* Floating controls above the sheet */}
      <div className="sm:max-w-lg sm:mx-auto px-3 pb-3 flex items-end justify-between gap-2">
        <div className="flex items-end gap-2 pointer-events-auto">
          <div className="w-[60px] h-[60px] rounded-full bg-white shadow-lg shadow-black/25 flex flex-col items-center justify-center text-[#202124]">
            <span className="text-[22px] font-bold leading-none">{speedKmh}</span>
            <span className="text-[10px] font-medium text-[#5f6368] leading-none mt-0.5">km/h</span>
          </div>
          {!isFollowingCamera && (
            <button
              type="button"
              onClick={onRecenter}
              className="h-[48px] px-4 rounded-full bg-white shadow-lg shadow-black/25 flex items-center gap-2 text-[#1a73e8] font-semibold text-[15px] active:scale-95 transition cursor-pointer"
            >
              <Navigation2 className="w-5 h-5 fill-[#1a73e8]" />
              Re-centre
            </button>
          )}
        </div>
      </div>

      {/* Trip sheet */}
      <div className="pointer-events-auto bg-white text-[#202124] rounded-t-[28px] sm:rounded-[28px] sm:max-w-lg sm:mx-auto sm:mb-3 shadow-[0_-4px_18px_rgba(0,0,0,0.18)] px-4 pt-2 pb-[max(14px,env(safe-area-inset-bottom))]">
        <div className="mx-auto w-9 h-1 rounded-full bg-[#dadce0] mb-2" />
        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={onEndNavigation}
            title="Exit navigation"
            aria-label="Exit navigation"
            className="w-12 h-12 rounded-full bg-[#f1f3f4] hover:bg-[#e8eaed] flex items-center justify-center active:scale-95 transition cursor-pointer shrink-0"
          >
            <X className="w-6 h-6 text-[#3c4043]" />
          </button>

          <div className="flex-1 min-w-0 text-center">
            <div className="text-[26px] font-bold text-[#188038] leading-tight">
              {formatRemainingTime(remainingSeconds)}
            </div>
            <div className="text-[15px] text-[#5f6368] leading-tight">
              {formatRemainingDistance(remainingMeters)} · {formatClock(eta)}
            </div>
          </div>

          <button
            type="button"
            onClick={onOverview}
            title="Route overview"
            aria-label="Route overview"
            className="w-12 h-12 rounded-full bg-[#f1f3f4] hover:bg-[#e8eaed] flex items-center justify-center active:scale-95 transition cursor-pointer shrink-0"
          >
            <Route className="w-6 h-6 text-[#3c4043]" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default NavigationFooter;
