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
  Volume2,
  VolumeX,
} from 'lucide-react';
import { TurnManeuver } from '@/lib/types';
import { formatDistance, cleanManeuverText } from '@/lib/geo';

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
    const iconClass = 'w-6 h-6 sm:w-8 sm:h-8';
    switch (type) {
      case 'turn_left':
        return <CornerUpLeft className={`${iconClass} text-sky-400`} />;
      case 'slight_left':
        return <ArrowUpLeft className={`${iconClass} text-sky-400`} />;
      case 'turn_right':
        return <CornerUpRight className={`${iconClass} text-sky-400`} />;
      case 'slight_right':
        return <ArrowUpRight className={`${iconClass} text-sky-400`} />;
      case 'u_turn':
        return <RotateCcw className={`${iconClass} text-amber-400`} />;
      case 'arrive':
        return <Flag className={`${iconClass} text-emerald-400`} />;
      case 'straight':
      case 'depart':
      default:
        return <ArrowUp className={`${iconClass} text-sky-400`} />;
    }
  };

  const currentAction = cleanManeuverText(currentManeuver);
  const nextAction = cleanManeuverText(nextManeuver);

  return (
    <div className="w-full max-w-lg mx-auto font-sans relative z-[1000] animate-in fade-in slide-in-from-top-2 duration-200">
      <div className="bg-[#0f172a] p-2.5 sm:p-4 rounded-2xl sm:rounded-3xl shadow-2xl shadow-black/90 border border-emerald-500/40 space-y-2 sm:space-y-2.5">
        <div className="flex items-center justify-between gap-2.5 sm:gap-4">
          {/* Maneuver Icon */}
          <div className="p-2 sm:p-3 bg-[#060910] rounded-xl sm:rounded-2xl border border-slate-800 flex items-center justify-center shrink-0 shadow-inner">
            {renderIcon(currentManeuver.type)}
          </div>

          {/* Distance & Action */}
          <div className="flex-1 min-w-0">
            <div className="text-lg sm:text-2xl font-black tracking-tight text-white font-mono flex items-baseline gap-1.5 sm:gap-2">
              <span>{formatDistance(distanceToManeuverMeters)}</span>
            </div>
            <div className="text-xs sm:text-base font-bold text-sky-300 truncate">
              {currentAction}
            </div>
          </div>

          {/* Voice Toggle Button */}
          <button
            type="button"
            onClick={onToggleVoice}
            className={`p-2 sm:p-2.5 rounded-xl sm:rounded-2xl border transition-all cursor-pointer shrink-0 active:scale-95 ${
              voiceEnabled
                ? 'bg-sky-500/20 border-sky-500/40 text-sky-300 shadow-md shadow-sky-500/10'
                : 'bg-slate-800/60 border-slate-700 text-slate-500'
            }`}
            title={voiceEnabled ? 'Mute Voice Guidance' : 'Enable Voice Guidance'}
            aria-label={voiceEnabled ? 'Mute Voice Guidance' : 'Enable Voice Guidance'}
          >
            {voiceEnabled ? (
              <Volume2 className="w-3.5 h-3.5 sm:w-5 sm:h-5" />
            ) : (
              <VolumeX className="w-3.5 h-3.5 sm:w-5 sm:h-5" />
            )}
          </button>
        </div>

        {/* Upcoming Secondary Maneuver Preview */}
        {nextManeuver && (
          <div className="pt-1.5 sm:pt-2 border-t border-slate-800 flex items-center gap-2 text-[10px] sm:text-xs font-medium text-slate-400">
            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[9px] sm:text-[10px] uppercase font-bold">
              Then
            </span>
            <span className="font-semibold text-slate-200 truncate">
              {nextAction}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TurnByTurnBanner;
