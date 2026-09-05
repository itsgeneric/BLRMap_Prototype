'use client';

import React from 'react';
import { Flag, CheckCircle2, Navigation, RotateCcw } from 'lucide-react';
import { TripSummary } from '@/lib/types';
import { formatDuration } from '@/lib/geo';

interface ArrivalModalProps {
  summary: TripSummary | null;
  onClose: () => void;
  onNewRoute: () => void;
}

export const ArrivalModal: React.FC<ArrivalModalProps> = ({ summary, onClose, onNewRoute }) => {
  if (!summary) return null;

  return (
    <div className="fixed inset-0 z-[4000] bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="glass-panel-heavy w-full max-w-sm rounded-3xl p-6 text-center shadow-2xl border border-emerald-500/40 space-y-5">
        {/* Animated Check & Flag Icon */}
        <div className="mx-auto w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <Flag className="w-8 h-8 text-emerald-400 fill-emerald-400/20 animate-bounce" />
        </div>

        {/* Title */}
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">You Have Arrived!</h2>
          <p className="text-xs text-slate-400 mt-1 truncate">
            {summary.destinationName || 'Destination reached successfully'}
          </p>
        </div>

        {/* Trip Stats Grid */}
        <div className="grid grid-cols-2 gap-2.5 bg-slate-950/70 p-3.5 rounded-2xl border border-slate-800 text-left">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Total Distance</div>
            <div className="text-lg font-black text-white font-mono">{summary.distanceKm.toFixed(1)} km</div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Time Taken</div>
            <div className="text-lg font-black text-emerald-400 font-mono">
              {formatDuration(summary.timeTakenSec)}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2 pt-1">
          <button
            onClick={onNewRoute}
            className="w-full py-2.5 sm:py-2.5 bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 text-slate-950 font-black text-xs sm:text-xs rounded-xl sm:rounded-xl shadow-xl shadow-emerald-500/25 transition-all flex items-center justify-center gap-2 cursor-pointer touch-press"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Plan Another Route</span>
          </button>
          <button
            onClick={onClose}
            className="w-full py-2 sm:py-2 bg-slate-800/80 hover:bg-slate-700 active:bg-slate-800 text-slate-300 font-bold text-xs rounded-xl sm:rounded-xl border border-slate-700 transition cursor-pointer"
          >
            Close Summary
          </button>
        </div>
      </div>
    </div>
  );
};
