'use client';

import React from 'react';
import { ToastMessage } from '@/lib/types';
import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react';

interface ToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (!toasts || toasts.length === 0) return null;

  const renderIcon = (type: ToastMessage['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />;
      default:
        return <Info className="w-4 h-4 text-sky-400 shrink-0" />;
    }
  };

  const getBorderColor = (type: ToastMessage['type']) => {
    switch (type) {
      case 'success':
        return 'border-emerald-500/40 bg-emerald-950/80 text-emerald-100';
      case 'error':
        return 'border-red-500/40 bg-red-950/80 text-red-100';
      case 'warning':
        return 'border-amber-500/40 bg-amber-950/80 text-amber-100';
      default:
        return 'border-sky-500/40 bg-slate-900/90 text-slate-100';
    }
  };

  return (
    <div className="fixed top-16 left-1/2 -translate-x-1/2 z-[3000] w-full max-w-sm px-4 pointer-events-none space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto flex items-center justify-between gap-2.5 p-3 rounded-2xl border backdrop-blur-xl shadow-2xl transition-all duration-300 animate-in fade-in slide-in-from-top-2 text-xs font-medium ${getBorderColor(
            toast.type
          )}`}
        >
          <div className="flex items-center gap-2 min-w-0">
            {renderIcon(toast.type)}
            <span className="truncate">{toast.text}</span>
          </div>
          <button
            onClick={() => onDismiss(toast.id)}
            className="p-1 text-slate-400 hover:text-slate-200 cursor-pointer rounded-lg hover:bg-white/10 shrink-0"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};
