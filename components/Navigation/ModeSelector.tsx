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
  const modes: { id: RouteMode; label: string; icon: React.ReactNode; color: string }[] = [
    {
      id: 'shortest',
      label: 'Shortest Path',
      icon: <Navigation className="w-3.5 h-3.5 text-lime-400" />,
      color: 'border-lime-400/30 text-lime-400 bg-lime-400/10',
    },
    {
      id: 'dynamic',
      label: 'Dynamic Route',
      icon: <Zap className="w-3.5 h-3.5 text-pink-400" />,
      color: 'border-pink-400/30 text-pink-400 bg-pink-400/10',
    },
  ];

  return (
    <div className="glass-panel p-1.5 rounded-2xl flex items-center gap-1 overflow-x-auto max-w-full no-scrollbar">
      {modes.map((m) => {
        const active = mode === m.id;
        return (
          <button
            key={m.id}
            onClick={() => onSelectMode(m.id)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 whitespace-nowrap transition-all duration-200 border ${
              active
                ? m.color + ' shadow-lg font-bold scale-[1.02]'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            {m.icon}
            <span>{m.label}</span>
          </button>
        );
      })}
    </div>
  );
};

