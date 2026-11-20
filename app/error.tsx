'use client';

import React, { useEffect } from 'react';
import { RefreshCw, AlertTriangle } from 'lucide-react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Next.js Client-Side Error Boundary caught:', error);
  }, [error]);

  return (
    <div className="w-screen h-screen bg-[#090a0f] text-slate-100 flex flex-col items-center justify-center p-6 text-center select-none font-sans">
      <div className="w-16 h-16 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-amber-400 flex items-center justify-center mb-4 shadow-xl">
        <AlertTriangle className="w-8 h-8" />
      </div>
      <h2 className="text-lg font-bold text-white mb-2">Navigation App Recovering</h2>
      <p className="text-xs text-slate-400 max-w-sm mb-6 leading-relaxed">
        The application encountered an unexpected state. Tap the button below to reload cleanly.
      </p>
      <button
        type="button"
        onClick={() => reset()}
        className="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 active:scale-95 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-sky-600/30 transition cursor-pointer"
      >
        <RefreshCw className="w-4 h-4" />
        <span>Reload Navigation</span>
      </button>
    </div>
  );
}
