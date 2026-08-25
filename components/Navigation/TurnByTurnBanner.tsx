'use client';

import React from 'react';
import {
  ArrowUp,
  ArrowUpLeft,
  ArrowUpRight,
  CornerUpLeft,
  CornerUpRight,
  RotateCcw,
  Flag,
  Navigation,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { TurnManeuver } from '@/lib/types';
import { formatDistance } from '@/lib/geo';

interface TurnByTurnBannerProps {
  currentManeuver: TurnManeuver | null;
  nextManeuver: TurnManeuver | null;
  distanceToManeuverMeters: number;
  voiceEnabled: boolean;
  onToggleVoice: () => void;
}

export const TurnByTurnBanner: React.FC<TurnByTurnBannerProps> = ({
  currentManeuver,
  nextManeuver,
  distanceToManeuverMeters,
  voiceEnabled,
  onToggleVoice,
}) => {
  if (!currentManeuver) return null;

  const renderIcon = (type: TurnManeuver['type']) => {
    switch (type) {
      case 'turn_left':
        return <CornerUpLeft className="w-8 h-8 text-sky-400" />;
      case 'slight_left':
        return <ArrowUpLeft className="w-8 h-8 text-sky-400" />;
      case 'turn_right':
        return <CornerUpRight className="w-8 h-8 text-sky-400" />;
      case 'slight_right':
        return <ArrowUpRight className="w-8 h-8 text-sky-400" />;
      case 'u_turn':
        return <RotateCcw className="w-8 h-8 text-amber-400" />;
      case 'arrive':
        return <Flag className="w-8 h-8 text-emerald-400" />;
      case 'straight':
      case 'depart':
      default:
        return <ArrowUp className="w-8 h-8 text-sky-400" />;
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto glass-panel p-4 rounded-3xl shadow-2xl space-y-2 border-emerald-500/30">
      <div className="flex items-center justify-between gap-4">
        {/* Maneuver Icon */}
        <div className="p-3 bg-slate-900/80 rounded-2xl border border-slate-700/60 flex items-center justify-center flex-shrink-0">
          {renderIcon(currentManeuver.type)}
        </div>

        {/* Distance & Main Instruction */}
        <div className="flex-1 min-w-0">
          <div className="text-2xl font-black tracking-tight text-slate-100 flex items-baseline gap-2">
            <span>{formatDistance(distanceToManeuverMeters)}</span>
          </div>
          <div className="text-sm font-semibold text-sky-300 truncate">
            {currentManeuver.instruction}
          </div>
        </div>

        {/* Voice Toggle Button */}
        <button
          onClick={onToggleVoice}
          className={`p-2.5 rounded-xl border transition-colors ${
            voiceEnabled
              ? 'bg-sky-500/10 border-sky-500/30 text-sky-400'
              : 'bg-slate-800/40 border-slate-700 text-slate-500'
          }`}
          title={voiceEnabled ? 'Mute Voice Guidance' : 'Enable Voice Guidance'}
        >
          {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
        </button>
      </div>

      {/* Upcoming Secondary Maneuver Preview */}
      {nextManeuver && (
        <div className="pt-2 border-t border-slate-800/60 flex items-center gap-2 text-xs font-medium text-slate-400">
          <span className="text-slate-500">Then</span>
          <span className="font-semibold text-slate-300 truncate">{nextManeuver.instruction}</span>
        </div>
      )}
    </div>
  );
};
