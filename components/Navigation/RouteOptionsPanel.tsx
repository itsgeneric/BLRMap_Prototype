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
    <div className="glass-panel p-4 rounded-2xl w-72 shadow-2xl space-y-4 text-xs font-sans">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-1.5 font-bold text-sky-400 uppercase tracking-wider">
          <Sliders className="w-3.5 h-3.5" />
          <span>2W Routing Penalties</span>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3">
        {/* Main Road Penalty */}
        <div className="flex items-center justify-between">
          <span className="text-slate-400 font-medium">Main Road Penalty</span>
          <input
            type="number"
            min="1"
            max="3"
            step="0.05"
            value={options.mainRoadPenalty}
            onChange={(e) =>
              onChange({ ...options, mainRoadPenalty: parseFloat(e.target.value) || 1.35 })
            }
            className="w-16 bg-slate-900 border border-slate-700 text-slate-100 px-2 py-1 rounded text-right font-mono"
          />
        </div>

        {/* Inner Road Multiplier */}
        <div className="flex items-center justify-between">
          <span className="text-slate-400 font-medium">Inner Road Preference</span>
          <input
            type="number"
            min="0.5"
            max="2"
            step="0.05"
            value={options.innerRoadMultiplier}
            onChange={(e) =>
              onChange({ ...options, innerRoadMultiplier: parseFloat(e.target.value) || 0.95 })
            }
            className="w-16 bg-slate-900 border border-slate-700 text-slate-100 px-2 py-1 rounded text-right font-mono"
          />
        </div>

        {/* Service Road Multiplier */}
        <div className="flex items-center justify-between">
          <span className="text-slate-400 font-medium">Service Road Preference</span>
          <input
            type="number"
            min="0.5"
            max="2"
            step="0.05"
            value={options.serviceMultiplier}
            onChange={(e) =>
              onChange({ ...options, serviceMultiplier: parseFloat(e.target.value) || 1.2 })
            }
            className="w-16 bg-slate-900 border border-slate-700 text-slate-100 px-2 py-1 rounded text-right font-mono"
          />
        </div>

        {/* Segment Split Slider */}
        <div className="space-y-1 pt-1 border-t border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium">Segment Split Distance</span>
            <span className="font-mono text-sky-400">{options.segmentKm} km</span>
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
            className="w-full accent-sky-400 cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
};
