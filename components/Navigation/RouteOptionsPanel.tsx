'use client';

import React from 'react';
import { Sliders, X } from 'lucide-react';
import { TwoWheelerOptions } from '@/lib/types';

interface RouteOptionsPanelProps {
  options: TwoWheelerOptions;
  onChange: (options: TwoWheelerOptions) => void;
  onClose: () => void;
}

export const RouteOptionsPanel: React.FC<RouteOptionsPanelProps> = ({
  options,
  onChange,
  onClose,
}) => {
  return (
    <div className="glass-panel-heavy p-4 rounded-3xl w-full max-w-sm sm:w-80 shadow-2xl space-y-4 text-xs font-sans border border-slate-700/80">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center gap-2 font-bold text-sky-400 uppercase tracking-wider text-xs">
          <Sliders className="w-4 h-4" />
          <span>2W Routing Penalties</span>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white touch-press cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3.5">
        {/* Main Road Penalty */}
        <div className="flex items-center justify-between gap-2">
          <span className="text-slate-300 font-medium">Main Road Penalty</span>
          <input
            type="number"
            min="1"
            max="3"
            step="0.05"
            value={options.mainRoadPenalty}
            onChange={(e) =>
              onChange({ ...options, mainRoadPenalty: parseFloat(e.target.value) || 1.35 })
            }
            className="w-20 bg-slate-950 border border-slate-700 text-slate-100 px-2.5 py-1.5 rounded-xl text-right font-mono text-xs outline-none focus:border-sky-400"
          />
        </div>

        {/* Inner Road Multiplier */}
        <div className="flex items-center justify-between gap-2">
          <span className="text-slate-300 font-medium">Inner Road Preference</span>
          <input
            type="number"
            min="0.5"
            max="2"
            step="0.05"
            value={options.innerRoadMultiplier}
            onChange={(e) =>
              onChange({ ...options, innerRoadMultiplier: parseFloat(e.target.value) || 0.95 })
            }
            className="w-20 bg-slate-950 border border-slate-700 text-slate-100 px-2.5 py-1.5 rounded-xl text-right font-mono text-xs outline-none focus:border-sky-400"
          />
        </div>

        {/* Service Road Multiplier */}
        <div className="flex items-center justify-between gap-2">
          <span className="text-slate-300 font-medium">Service Road Preference</span>
          <input
            type="number"
            min="0.5"
            max="2"
            step="0.05"
            value={options.serviceMultiplier}
            onChange={(e) =>
              onChange({ ...options, serviceMultiplier: parseFloat(e.target.value) || 1.2 })
            }
            className="w-20 bg-slate-950 border border-slate-700 text-slate-100 px-2.5 py-1.5 rounded-xl text-right font-mono text-xs outline-none focus:border-sky-400"
          />
        </div>

        {/* Segment Split Slider */}
        <div className="space-y-1.5 pt-2 border-t border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-slate-300 font-medium">Segment Split</span>
            <span className="font-mono font-bold text-sky-400">{options.segmentKm} km</span>
          </div>
          <input
            type="range"
            min="1.5"
            max="5.5"
            step="0.5"
            value={options.segmentKm}
            onChange={(e) =>
              onChange({ ...options, segmentKm: parseFloat(e.target.value) || 3.0 })
            }
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
          />
        </div>
      </div>
    </div>
  );
};

export default RouteOptionsPanel;
