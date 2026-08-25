'use client';

import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { ThemeMode } from '@/lib/types';

interface ThemeToggleProps {
  theme: ThemeMode;
  onToggle: (theme: ThemeMode) => void;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ theme, onToggle }) => {
  return (
    <button
      onClick={() => onToggle(theme === 'dark' ? 'light' : 'dark')}
      className="p-2.5 rounded-xl glass-panel transition-all duration-200 hover:scale-105 active:scale-95 text-slate-300 dark:text-slate-200 hover:text-sky-400"
      title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <Sun className="w-5 h-5 text-amber-400" />
      ) : (
        <Moon className="w-5 h-5 text-indigo-600" />
      )}
    </button>
  );
};
