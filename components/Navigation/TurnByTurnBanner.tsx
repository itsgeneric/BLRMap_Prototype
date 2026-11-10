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
  const renderIcon = (type?: TurnManeuver['type']) => {
    const iconClass = 'w-7 h-7 text-white stroke-[2.5]';
    switch (type) {
      case 'turn_left':
        return <CornerUpLeft className={iconClass} />;
      case 'slight_left':
        return <ArrowUpLeft className={iconClass} />;
      case 'turn_right':
        return <CornerUpRight className={iconClass} />;
      case 'slight_right':
        return <ArrowUpRight className={iconClass} />;
      case 'u_turn':
        return <RotateCcw className={iconClass} />;
      case 'arrive':
        return <Flag className={iconClass} />;
      case 'straight':
      case 'depart':
      default:
        return <ArrowUp className={iconClass} />;
    }
  };

  const currentAction = currentManeuver ? cleanManeuverText(currentManeuver) : 'Proceed along the highlighted route';
  const nextAction = nextManeuver ? cleanManeuverText(nextManeuver) : null;
  const distText = distanceToManeuverMeters > 0 ? formatDistance(distanceToManeuverMeters) : '';

  return (
    <div className="w-full max-w-lg mx-auto font-sans relative z-[1000] animate-in fade-in slide-in-from-top-2 duration-200 px-2 sm:px-0">
      {/* Google Maps Signature Dark Green Navigation Banner */}
      <div className="bg-[#0b8043] text-white p-3 sm:p-3.5 rounded-2xl shadow-2xl shadow-black/40 border border-[#0d944f] space-y-2">
        <div className="flex items-center justify-between gap-3">
          {/* Large Turn Maneuver Icon */}
          <div className="w-11 h-11 rounded-xl bg-black/15 flex items-center justify-center shrink-0 border border-white/10 shadow-sm">
            {renderIcon(currentManeuver?.type)}
          </div>

          {/* Distance & Action Text */}
          <div className="flex-1 min-w-0">
            {distText && (
              <div className="text-xl sm:text-2xl font-black tracking-tight text-white font-mono leading-none mb-0.5">
                {distText}
              </div>
            )}
            <div className="text-sm sm:text-base font-bold text-emerald-50 truncate leading-snug">
              {currentAction}
            </div>
          </div>

          {/* Voice Guidance Toggle */}
          <button
            type="button"
            onClick={onToggleVoice}
            className={`p-2.5 rounded-full border transition-all cursor-pointer shrink-0 active:scale-95 ${
              voiceEnabled
                ? 'bg-white/20 border-white/30 text-white shadow-md'
                : 'bg-black/20 border-white/10 text-white/60 hover:text-white'
            }`}
            title={voiceEnabled ? 'Mute Voice Guidance' : 'Enable Voice Guidance'}
            aria-label={voiceEnabled ? 'Mute Voice Guidance' : 'Enable Voice Guidance'}
          >
            {voiceEnabled ? (
              <Volume2 className="w-4 h-4" />
            ) : (
              <VolumeX className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Upcoming Next Maneuver Preview ("Then turn...") */}
        {nextAction && (
          <div className="pt-2 border-t border-white/15 flex items-center gap-2 text-xs font-medium text-emerald-100">
            <span className="px-1.5 py-0.5 rounded bg-black/20 text-white text-[10px] uppercase font-bold tracking-wider">
              Then
            </span>
            <span className="font-semibold text-white truncate">
              {nextAction}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TurnByTurnBanner;
