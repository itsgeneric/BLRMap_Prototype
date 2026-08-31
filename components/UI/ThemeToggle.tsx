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
      type="button"
      onClick={() => onToggle(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 sm:p-2.5 rounded-xl sm:rounded-2xl bg-[#0f172a] border border-slate-700/80 transition-all duration-200 text-slate-300 hover:text-sky-400 active:scale-95 flex items-center justify-center cursor-pointer shadow-md"
      title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <Sun className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-400 transition-transform hover:rotate-45" />
      ) : (
        <Moon className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-sky-400 transition-transform hover:-rotate-12" />
      )}
    </button>
  );
};

export default ThemeToggle;
