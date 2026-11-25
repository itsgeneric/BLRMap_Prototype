'use client';

/**
 * Arrival card shown when the rider reaches the destination: destination name,
 * which side of the road it is on, a short trip summary, and Done.
 */
import React from 'react';
import { MapPin } from 'lucide-react';
import { TripSummary } from '@/lib/types';
import { formatRemainingTime } from '@/lib/navigation';

interface ArrivalModalProps {
  summary: TripSummary | null;
  side?: 'left' | 'right' | null;
  onClose: () => void;
  onNewRoute: () => void;
}

export const ArrivalModal: React.FC<ArrivalModalProps> = ({ summary, side, onClose, onNewRoute }) => {
  if (!summary) return null;

  return (
    <div className="fixed inset-x-0 bottom-0 z-[4000] font-sans animate-in fade-in slide-in-from-bottom-4 duration-300">
      <div className="bg-white text-[#202124] rounded-t-[28px] sm:rounded-[28px] sm:max-w-lg sm:mx-auto sm:mb-3 shadow-[0_-4px_18px_rgba(0,0,0,0.2)] px-5 pt-3 pb-[max(18px,env(safe-area-inset-bottom))]">
        <div className="mx-auto w-9 h-1 rounded-full bg-[#dadce0] mb-4" />
        <div className="flex items-start gap-3.5">
          <div className="w-11 h-11 rounded-full bg-[#e6f4ea] flex items-center justify-center shrink-0">
            <MapPin className="w-6 h-6 text-[#188038]" />
          </div>
          <div className="min-w-0">
            <div className="text-[14px] font-medium text-[#188038]">
              You have arrived{side ? ` · on the ${side}` : ''}
            </div>
            <div className="text-[22px] font-bold leading-tight truncate">
              {summary.destinationName || 'Destination'}
            </div>
            <div className="text-[14px] text-[#5f6368] mt-0.5">
              {summary.distanceKm.toFixed(1)} km · {formatRemainingTime(summary.timeTakenSec)}
            </div>
          </div>
        </div>

        <div className="flex gap-2 mt-5">
          <button
            onClick={onClose}
            className="flex-1 h-12 rounded-full border border-[#dadce0] text-[#1a73e8] font-semibold text-[15px] hover:bg-[#f8f9fa] active:scale-[0.98] transition cursor-pointer"
          >
            Close
          </button>
          <button
            onClick={onNewRoute}
            className="flex-1 h-12 rounded-full bg-[#1a73e8] text-white font-semibold text-[15px] hover:bg-[#1967d2] active:scale-[0.98] transition cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

export default ArrivalModal;
