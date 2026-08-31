'use client';

import React from 'react';
import { Zap, Navigation } from 'lucide-react';
import { RouteMode } from '@/lib/types';

interface ModeSelectorProps {
  mode: RouteMode;
  onSelectMode: (mode: RouteMode) => void;
}

export const ModeSelector: React.FC<ModeSelectorProps> = ({
  mode,
  onSelectMode,
}) => {
  const modes: { id: RouteMode; label: string; shortLabel: string; icon: React.ReactNode; color: string }[] = [
    {
      id: 'shortest',
      label: 'Shortest Path',
      shortLabel: 'Shortest',
      icon: <Navigation className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-lime-400 fill-lime-400/20 shrink-0" />,
      color: 'border-lime-400/40 text-lime-400 bg-lime-400/15 shadow-lime-500/20',
    },
    {
      id: 'dynamic',
      label: 'Dynamic Route',
      shortLabel: 'Dynamic',
      icon: <Zap className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-pink-400 fill-pink-400/20 shrink-0" />,
      color: 'border-pink-400/40 text-pink-400 bg-pink-400/15 shadow-pink-500/20',
    },
  ];

  return (
    <div className="bg-[#0f172a] p-0.5 sm:p-1 rounded-xl sm:rounded-2xl border border-slate-700/80 flex items-center gap-0.5 sm:gap-1 shadow-md">
      {modes.map((m) => {
        const active = mode === m.id;
        return (
          <button
            key={m.id}
            type="button"
            onClick={() => onSelectMode(m.id)}
            className={`px-2 py-1 sm:px-3 sm:py-1.5 rounded-lg sm:rounded-xl text-[11px] sm:text-xs font-bold flex items-center gap-1 sm:gap-1.5 whitespace-nowrap transition-all border cursor-pointer active:scale-95 ${
              active
                ? `${m.color} shadow-sm font-black`
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            {m.icon}
            <span className="hidden sm:inline">{m.label}</span>
            <span className="inline sm:hidden">{m.shortLabel}</span>
          </button>
        );
      })}
    </div>
  );
};

export default ModeSelector;
