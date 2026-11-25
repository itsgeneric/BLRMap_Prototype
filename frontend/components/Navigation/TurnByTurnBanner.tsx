'use client';

/**
 * Top guidance banner, laid out like a navigation app's turn card:
 * green card with the turn arrow, distance to the turn and the road to take,
 * a darker "Then" strip when the following turn comes soon after, and a grey
 * "Rerouting…" state while a new route is being fetched.
 */
import React from 'react';
import { Loader2 } from 'lucide-react';
import { NavStatus, TurnManeuver } from '@/lib/types';
import { formatBannerDistance } from '@/lib/navigation';
import { ManeuverIcon } from './ManeuverIcon';

interface TurnByTurnBannerProps {
  status: NavStatus;
  currentManeuver: TurnManeuver | null;
  nextManeuver: TurnManeuver | null;
  distanceToManeuverMeters: number;
  distanceBetweenManeuvers: number;
}

const GREEN = 'bg-[#137333]';
const GREEN_DARK = 'bg-[#0d5626]';

function ordinal(n: number) {
  const s = n % 100 >= 11 && n % 100 <= 13 ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' } as Record<number, string>)[n % 10] || 'th';
  return `${n}${s}`;
}

function headline(m: TurnManeuver): { title: string; subtitle?: string } {
  if (m.type === 'arrive') {
    return { title: 'Destination', subtitle: m.side ? `on the ${m.side}` : undefined };
  }
  if (m.type === 'roundabout') {
    const exit = `${ordinal(m.exit ?? 1)} exit`;
    return m.road_name ? { title: m.road_name, subtitle: `Roundabout · ${exit}` } : { title: `Take the ${exit}` };
  }
  if (m.road_name) {
    const verb =
      m.type.startsWith('keep') ? (m.type === 'keep_left' ? 'Keep left' : 'Keep right') :
      m.type === 'u_turn' ? 'U-turn' : undefined;
    return { title: m.road_name, subtitle: verb };
  }
  return { title: m.instruction };
}

export const TurnByTurnBanner: React.FC<TurnByTurnBannerProps> = ({
  status,
  currentManeuver,
  nextManeuver,
  distanceToManeuverMeters,
  distanceBetweenManeuvers,
}) => {
  if (status === 'rerouting') {
    return (
      <div className="w-full max-w-lg mx-auto rounded-2xl bg-[#3c4043] text-white shadow-xl shadow-black/30 px-5 py-5 flex items-center gap-4 animate-in fade-in duration-200">
        <Loader2 className="w-8 h-8 animate-spin text-white/90 shrink-0" />
        <span className="text-[22px] font-semibold tracking-tight">Rerouting…</span>
      </div>
    );
  }

  if (!currentManeuver) return null;

  const { title, subtitle } = headline(currentManeuver);
  const showThen =
    !!nextManeuver && nextManeuver.type !== 'arrive' && distanceBetweenManeuvers < 300 && distanceToManeuverMeters < 600;

  return (
    <div className="w-full max-w-lg mx-auto font-sans shadow-xl shadow-black/30 rounded-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
      <div className={`${GREEN} text-white px-4 py-3.5 flex items-center gap-3.5`}>
        <div className="flex flex-col items-center shrink-0 w-[64px]">
          <ManeuverIcon type={currentManeuver.type} exit={currentManeuver.exit} size={52} />
          <span className="text-[17px] font-bold leading-none mt-1 whitespace-nowrap">
            {formatBannerDistance(distanceToManeuverMeters)}
          </span>
        </div>
        <div className="min-w-0 flex-1">
          {subtitle && <div className="text-[15px] font-medium text-white/85 leading-tight">{subtitle}</div>}
          <div className="text-[24px] sm:text-[26px] font-bold leading-[1.15] tracking-tight line-clamp-2 break-words">
            {title}
          </div>
        </div>
      </div>
      {showThen && nextManeuver && (
        <div className={`${GREEN_DARK} text-white px-4 py-2 flex items-center gap-2`}>
          <span className="text-[16px] font-semibold">Then</span>
          <ManeuverIcon type={nextManeuver.type} exit={nextManeuver.exit} size={24} />
        </div>
      )}
    </div>
  );
};

export default TurnByTurnBanner;
