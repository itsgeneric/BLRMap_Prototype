'use client';

import React from 'react';
import { Navigation, MapPin, X, Loader2 } from 'lucide-react';
import { Point } from '@/lib/types';
import type { PinAction } from '@/lib/pinActions';

interface PlaceSheetProps {
  pin: Point | null;
  /** true while the place's name is still being looked up */
  resolving: boolean;
  /** a start point already exists (so "Directions" will not need the phone's location) */
  hasOrigin: boolean;
  onAction: (action: PinAction) => void;
  onClose: () => void;
}

/** Bottom card after a press-and-hold on the map: the place, and what to do with it (like Google Maps' dropped pin). */
export const PlaceSheet: React.FC<PlaceSheetProps> = ({ pin, resolving, hasOrigin, onAction, onClose }) => {
  if (!pin) return null;

  return (
    <div
      role="dialog"
      aria-label="Dropped pin"
      className="fixed left-2.5 right-2.5 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-lg z-[1100] font-sans"
      style={{ bottom: 'calc(env(safe-area-inset-bottom, 0px) + 10px)' }}
    >
      <div className="bg-white text-slate-900 rounded-3xl shadow-2xl shadow-black/30 border border-slate-200 p-4 space-y-3">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center shrink-0">
            <MapPin className="w-5 h-5 text-orange-600" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-lg font-black leading-tight truncate flex items-center gap-2">
              <span className="truncate">{pin.name || 'Dropped pin'}</span>
              {resolving && <Loader2 className="w-4 h-4 animate-spin text-slate-400 shrink-0" />}
            </div>
            <div className="text-xs text-slate-500 truncate mt-0.5">
              {pin.address || `${pin.lat.toFixed(5)}, ${pin.lng.toFixed(5)}`}
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="w-11 h-11 -mr-2 -mt-2 rounded-full flex items-center justify-center text-slate-500 active:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onAction('directions')}
            className="flex-1 min-h-[48px] rounded-2xl bg-[#1a73e8] active:bg-[#1557b0] text-white font-bold flex items-center justify-center gap-2"
          >
            <Navigation className="w-5 h-5" />
            <span>Directions</span>
          </button>
          <button
            type="button"
            onClick={() => onAction('start_here')}
            className="min-h-[48px] px-4 rounded-2xl border border-slate-300 active:bg-slate-100 text-slate-700 font-bold"
          >
            Start here
          </button>
        </div>
        {!hasOrigin && (
          <div className="text-[11px] text-slate-500 -mt-1">Directions will start from your current location.</div>
        )}
      </div>
    </div>
  );
};

export default PlaceSheet;
