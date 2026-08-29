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
      icon: <Navigation className="w-3.5 h-3.5 text-lime-400 fill-lime-400/20 shrink-0" />,
      color: 'border-lime-400/40 text-lime-400 bg-lime-400/15 shadow-lime-500/20',
    },
    {
      id: 'dynamic',
      label: 'Dynamic Route',
      shortLabel: 'Dynamic',
      icon: <Zap className="w-3.5 h-3.5 text-pink-400 fill-pink-400/20 shrink-0" />,
      color: 'border-pink-400/40 text-pink-400 bg-pink-400/15 shadow-pink-500/20',
    },
  ];

  return (
    <div className="glass-panel p-1 rounded-2xl flex items-center gap-1 overflow-x-auto no-scrollbar max-w-full shadow-lg">
      {modes.map((m) => {
        const active = mode === m.id;
        return (
          <button
            key={m.id}
            onClick={() => onSelectMode(m.id)}
            className={`px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 whitespace-nowrap transition-all duration-200 border touch-press cursor-pointer ${
              active
                ? `${m.color} shadow-md scale-[1.02]`
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

