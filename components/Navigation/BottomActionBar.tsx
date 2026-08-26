'use client';

import React from 'react';
import { Navigation, Eye, List, Clock, MapPin } from 'lucide-react';
import { LatLng } from '../Map/MapContainer';

interface BottomActionBarProps {
  source: LatLng | null;
  destination: LatLng | null;
  distanceKm: number | null;
  durationMins: number | null;
  onStartLiveGps: () => void;
  onStartPreview: () => void;
  onToggleSteps: () => void;
}

export default function BottomActionBar({
  source,
  destination,
  distanceKm,
  durationMins,
  onStartLiveGps,
  onStartPreview,
  onToggleSteps,
}: BottomActionBarProps) {
  if (!source || !destination) return null;

  // Check if Source is user's live current location
  const isSourceMyLocation =
    source.address?.toLowerCase().includes('my location') ||
    source.name?.toLowerCase().includes('my location');

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[1000] w-full max-w-md px-4 font-sans">
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-3xl shadow-2xl p-4 space-y-3">
        {/* Route Stats (ETA & Distance) */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <div className="text-2xl font-black text-emerald-400 font-mono">
              {durationMins ? `${durationMins} mins` : 'Calculating...'}
            </div>
            <div className="text-xs text-slate-400 font-mono mt-0.5 flex items-center gap-1.5">
              <span>{distanceKm ? `${distanceKm} km` : '--'}</span>
              <span>•</span>
              <span className="text-sky-400">Fastest Route</span>
            </div>
          </div>

          <button
            onClick={onToggleSteps}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition cursor-pointer"
          >
            <List className="w-3.5 h-3.5 text-slate-400" />
            <span>Steps</span>
          </button>
        </div>

        {/* Action Button: Start vs Preview */}
        <div className="flex items-center gap-2">
          {isSourceMyLocation ? (
            /* Live GPS Start Navigation Button (When starting from My Location) */
            <button
              onClick={onStartLiveGps}
              className="flex-1 py-3 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-slate-950 font-bold text-sm rounded-2xl shadow-xl transition flex items-center justify-center gap-2 cursor-pointer"
            >
              <Navigation className="w-4 h-4 fill-slate-950" />
              <span>Start Navigation</span>
            </button>
          ) : (
            /* Preview Route Button (When starting from custom location) */
            <button
              onClick={onStartPreview}
              className="flex-1 py-3 bg-sky-500 hover:bg-sky-600 active:scale-95 text-slate-950 font-bold text-sm rounded-2xl shadow-xl transition flex items-center justify-center gap-2 cursor-pointer"
            >
              <Eye className="w-4 h-4" />
              <span>Preview Route</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
