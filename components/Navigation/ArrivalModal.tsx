'use client';

import React from 'react';
import { CheckCircle2, RotateCcw, MapPin, Sparkles } from 'lucide-react';
import { TripSummary } from '@/lib/types';
import { formatDuration } from '@/lib/geo';

interface ArrivalModalProps {
  summary: TripSummary | null;
  onDone: () => void;
}

export const ArrivalModal: React.FC<ArrivalModalProps> = ({ summary, onDone }) => {
  if (!summary) return null;

  return (
    <div className="fixed inset-0 z-[4000] bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="glass-panel-heavy w-full max-w-sm rounded-3xl p-6 text-center shadow-2xl border border-emerald-500/50 space-y-5">
        {/* Animated Check Icon */}
        <div className="mx-auto w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center shadow-lg shadow-emerald-500/25">
          <CheckCircle2 className="w-10 h-10 text-emerald-400 fill-emerald-400/20" />
        </div>

        {/* Title */}
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-mono font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-3 h-3" />
            <span>Journey Complete</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">You Have Arrived!</h2>
          <p className="text-xs text-slate-300 mt-1 truncate flex items-center justify-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span className="truncate">{summary.destinationName || 'Destination reached'}</span>
          </p>
        </div>

        {/* Trip Stats Grid */}
        <div className="grid grid-cols-2 gap-2.5 bg-slate-900/90 p-3.5 rounded-2xl border border-slate-800 text-left">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400">Total Distance</div>
            <div className="text-lg font-black text-white font-mono">{summary.distanceKm.toFixed(1)} km</div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400">Time Taken</div>
            <div className="text-lg font-black text-emerald-400 font-mono">
              {formatDuration(summary.timeTakenSec)}
            </div>
          </div>
        </div>

        {/* Clean Primary Done Action (Clears map and resets to fresh home view) */}
        <div className="pt-1">
          <button
            type="button"
            onClick={onDone}
            className="w-full py-3.5 bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 text-slate-950 font-black text-sm rounded-xl shadow-xl shadow-emerald-500/25 transition-all flex items-center justify-center gap-2 cursor-pointer touch-press"
          >
            <CheckCircle2 className="w-4 h-4 stroke-[2.5]" />
            <span>Done</span>
          </button>
        </div>
      </div>
    </div>
  );
};
