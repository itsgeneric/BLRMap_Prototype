'use client';

import React from 'react';
import { Flag, Check } from 'lucide-react';
import { TripSummary } from '@/lib/types';
import { formatDuration } from '@/lib/geo';

interface ArrivalModalProps {
  summary: TripSummary | null;
  /** Tapped "Done": the app clears the trip and returns to the starting map. */
  onDone: () => void;
}

export const ArrivalModal: React.FC<ArrivalModalProps> = ({ summary, onDone }) => {
  if (!summary) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Trip completed"
      className="fixed inset-0 z-[4000] bg-slate-950/70 backdrop-blur-sm flex items-end sm:items-center justify-center p-4 pb-[max(1rem,env(safe-area-inset-bottom))]"
    >
      <div className="w-full max-w-sm rounded-3xl bg-white text-slate-900 p-6 text-center shadow-2xl space-y-5">
        <div className="mx-auto w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center">
          <Flag className="w-8 h-8 text-emerald-600" />
        </div>

        <div>
          <h2 className="text-2xl font-black tracking-tight">You have arrived</h2>
          <p className="text-sm text-slate-500 mt-1 truncate">{summary.destinationName || 'Destination'}</p>
        </div>

        <div className="grid grid-cols-3 gap-2 rounded-2xl bg-slate-100 p-3">
          <div>
            <div className="text-[10px] uppercase tracking-wide text-slate-500">Distance</div>
            <div className="text-lg font-black">{summary.distanceKm.toFixed(1)} km</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wide text-slate-500">Time</div>
            <div className="text-lg font-black">{formatDuration(summary.timeTakenSec)}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wide text-slate-500">Avg speed</div>
            <div className="text-lg font-black">{Math.round(summary.avgSpeedKmh)} km/h</div>
          </div>
        </div>

        <button
          type="button"
          onClick={onDone}
          className="w-full min-h-[52px] rounded-2xl bg-[#1a73e8] active:bg-[#1557b0] text-white font-bold text-base flex items-center justify-center gap-2"
        >
          <Check className="w-5 h-5" />
          <span>Done</span>
        </button>
      </div>
    </div>
  );
};

export default ArrivalModal;
