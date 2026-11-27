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
  Loader2,
  TriangleAlert,
} from 'lucide-react';
import { TurnManeuver } from '@/lib/types';
import { maneuverTitle, formatManeuverDistance } from '@/lib/geo';
import type { NavState } from '@/hooks/useNavigationEngine';

interface TurnByTurnBannerProps {
  /** the next turn ahead (from the engine) */
  currentManeuver: TurnManeuver | null;
  /** the one after it, shown as "Then ..." */
  nextManeuver: TurnManeuver | null;
  distanceToManeuverMeters: number;
  currentRoadName?: string | null;
  navState?: NavState;
  voiceEnabled: boolean;
  onToggleVoice: () => void;
}

const ICON_CLASS = 'w-8 h-8 text-white stroke-[2.5]';

function maneuverIcon(type?: TurnManeuver['type'], className = ICON_CLASS) {
  switch (type) {
    case 'turn_left':
      return <CornerUpLeft className={className} />;
    case 'slight_left':
      return <ArrowUpLeft className={className} />;
    case 'turn_right':
      return <CornerUpRight className={className} />;
    case 'slight_right':
      return <ArrowUpRight className={className} />;
    case 'u_turn':
      return <RotateCcw className={className} />;
    case 'arrive':
      return <Flag className={className} />;
    default:
      return <ArrowUp className={className} />;
  }
}

export const TurnByTurnBanner: React.FC<TurnByTurnBannerProps> = ({
  currentManeuver,
  nextManeuver,
  distanceToManeuverMeters,
  currentRoadName,
  navState = 'following',
  voiceEnabled,
  onToggleVoice,
}) => {
  const rerouting = navState === 'rerouting';
  const offRoute = navState === 'off_route';
  const approaching = navState === 'approaching';

  const voiceButton = (
    <button
      type="button"
      onClick={onToggleVoice}
      className={`w-11 h-11 rounded-full flex items-center justify-center border transition-colors shrink-0 active:scale-95 ${
        voiceEnabled ? 'bg-white/20 border-white/30 text-white' : 'bg-black/25 border-white/10 text-white/70'
      }`}
      title={voiceEnabled ? 'Mute voice guidance' : 'Turn on voice guidance'}
      aria-label={voiceEnabled ? 'Mute voice guidance' : 'Turn on voice guidance'}
    >
      {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
    </button>
  );

  // Off route / rerouting: one clear state, no stale turn instruction
  if (rerouting || offRoute) {
    return (
      <div className="w-full max-w-lg mx-auto font-sans relative z-[1000] px-2 sm:px-0">
        <div className="bg-[#b06000] text-white p-3.5 rounded-2xl shadow-2xl flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-black/15 flex items-center justify-center shrink-0">
            {rerouting ? <Loader2 className="w-7 h-7 animate-spin" /> : <TriangleAlert className="w-7 h-7" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-lg font-black leading-tight">{rerouting ? 'Rerouting…' : 'You are off route'}</div>
            <div className="text-sm text-white/85">Finding the best way from where you are</div>
          </div>
          {voiceButton}
        </div>
      </div>
    );
  }

  const title = currentManeuver ? maneuverTitle(currentManeuver) : currentRoadName ? `Continue on ${currentRoadName}` : 'Continue on the route';
  const dist = currentManeuver ? formatManeuverDistance(distanceToManeuverMeters) : '';
  const then = nextManeuver ? maneuverTitle(nextManeuver) : null;

  return (
    <div className="w-full max-w-lg mx-auto font-sans relative z-[1000] px-2 sm:px-0">
      <div
        className={`text-white p-3.5 rounded-2xl shadow-2xl shadow-black/40 space-y-2 transition-colors ${
          approaching ? 'bg-[#0a6b38]' : 'bg-[#0b8043]'
        }`}
      >
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 rounded-xl bg-black/15 flex items-center justify-center shrink-0">
            {maneuverIcon(currentManeuver?.type)}
          </div>

          <div className="flex-1 min-w-0">
            {dist && <div className="text-3xl font-black tracking-tight leading-none mb-1 tabular-nums">{dist}</div>}
            <div className="text-base font-bold text-white leading-snug line-clamp-2">{title}</div>
          </div>

          {voiceButton}
        </div>

        {then && currentManeuver?.type !== 'arrive' && (
          <div className="pt-2 border-t border-white/20 flex items-center gap-2 text-sm">
            <span className="px-2 py-0.5 rounded bg-black/25 text-[11px] uppercase font-bold tracking-wider">Then</span>
            {maneuverIcon(nextManeuver?.type, 'w-4 h-4 text-white stroke-[2.5] shrink-0')}
            <span className="font-semibold truncate">{then}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TurnByTurnBanner;
