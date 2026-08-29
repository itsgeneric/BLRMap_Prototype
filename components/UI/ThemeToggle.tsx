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
      className="p-2.5 sm:p-3 rounded-2xl glass-panel touch-press transition-all duration-200 text-slate-300 dark:text-slate-200 hover:text-sky-400 active:scale-95 flex items-center justify-center cursor-pointer shadow-md"
      title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <Sun className="w-4 h-4 sm:w-5 sm:h-5 text-amber-400 transition-transform hover:rotate-45" />
      ) : (
        <Moon className="w-4 h-4 sm:w-5 sm:h-5 text-sky-600 transition-transform hover:-rotate-12" />
      )}
    </button>
  );
};

export default ThemeToggle;
