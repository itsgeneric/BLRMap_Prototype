'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  AlertTriangle,
  X,
  Car,
  Clock,
  HardHat,
  Cone,
  AlertOctagon,
  Waves,
  CloudFog,
  Check,
  Undo2,
} from 'lucide-react';
import { IncidentType, RoadIncident } from '@/lib/types';
import { reportIncident, verifyIncident } from '@/lib/api';

interface IncidentReportModalProps {
  isNavigating: boolean;
  currentLat?: number;
  currentLng?: number;
  currentHeading?: number | null;
  currentRoadName?: string;
  activeIncidents?: RoadIncident[];
  onIncidentReported?: (incident: RoadIncident) => void;
  onIncidentUpdated?: () => void;
}

interface IncidentOption {
  type: IncidentType;
  label: string;
  theme: 'red' | 'amber';
  icon: React.ReactNode;
}

const INCIDENT_OPTIONS: IncidentOption[] = [
  {
    type: 'crash',
    label: 'Crash',
    theme: 'red',
    icon: (
      <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
        <circle cx="7" cy="17" r="2" />
        <path d="M9 17h6" />
        <circle cx="17" cy="17" r="2" />
        <path d="M13 3l-2 3h4l-2 3" />
      </svg>
    ),
  },
  {
    type: 'slowdown',
    label: 'Slowdown',
    theme: 'red',
    icon: (
      <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
        <circle cx="7" cy="17" r="2" />
        <path d="M9 17h6" />
        <circle cx="17" cy="17" r="2" />
        <path d="M5 6l2 2-2 2" />
      </svg>
    ),
  },
  {
    type: 'construction',
    label: 'Construction',
    theme: 'amber',
    icon: <HardHat className="w-5 h-5 text-amber-950" />,
  },
  {
    type: 'lane_closure',
    label: 'Lane closure',
    theme: 'amber',
    icon: <Cone className="w-5 h-5 text-amber-950" />,
  },
  {
    type: 'hazard',
    label: 'Object on road',
    theme: 'amber',
    icon: (
      <svg className="w-5 h-5 text-amber-950" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="6" y1="3" x2="4" y2="21" />
        <line x1="18" y1="3" x2="20" y2="21" />
        <path d="M12 8v5" />
        <path d="M12 16h.01" />
      </svg>
    ),
  },
  {
    type: 'flooded',
    label: 'Flooded road',
    theme: 'amber',
    icon: <Waves className="w-5 h-5 text-amber-950" />,
  },
  {
    type: 'visibility',
    label: 'Low visibility',
    theme: 'amber',
    icon: <CloudFog className="w-5 h-5 text-amber-950" />,
  },
];

export const IncidentReportModal: React.FC<IncidentReportModalProps> = ({
  isNavigating,
  currentLat,
  currentLng,
  currentHeading,
  currentRoadName,
  activeIncidents = [],
  onIncidentReported,
  onIncidentUpdated,
}) => {
  const [sheetOpen, setSheetOpen] = useState(false);
  const [pendingIncident, setPendingIncident] = useState<IncidentOption | null>(null);
  const [countdown, setCountdown] = useState<number>(5);
  const [nearbyIncidentToVerify, setNearbyIncidentToVerify] = useState<RoadIncident | null>(null);

  const countdownTimerRef = useRef<NodeJS.Timeout | null>(null);
  const hasVotedIncidentsRef = useRef<Set<string>>(new Set());

  // Proximity check: Prompt rider if an unverified incident is within 150m ahead
  useEffect(() => {
    if (!isNavigating || !currentLat || !currentLng || activeIncidents.length === 0) {
      setNearbyIncidentToVerify(null);
      return;
    }

    const unvoted = activeIncidents.find((inc) => {
      if (hasVotedIncidentsRef.current.has(inc.id)) return false;
      // Simple approximate distance in meters
      const dLat = (inc.lat - currentLat) * 111320;
      const dLng = (inc.lng - currentLng) * 110540 * Math.cos((currentLat * Math.PI) / 180);
      const dist = Math.sqrt(dLat * dLat + dLng * dLng);
      return dist <= 150;
    });

    setNearbyIncidentToVerify(unvoted || null);
  }, [isNavigating, currentLat, currentLng, activeIncidents]);

  // Handle 5-second countdown submission
  useEffect(() => {
    if (pendingIncident) {
      setCountdown(5);
      countdownTimerRef.current = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            handleConfirmReport(pendingIncident);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
    }

    return () => {
      if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
    };
  }, [pendingIncident]);

  const handleSelectOption = (option: IncidentOption) => {
    if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
      navigator.vibrate(15);
    }
    setSheetOpen(false);
    setPendingIncident(option);
  };

  const handleConfirmReport = async (incident: IncidentOption) => {
    if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
    const selected = incident || pendingIncident;
    setPendingIncident(null);

    if (!selected || currentLat === undefined || currentLng === undefined) return;

    try {
      const res = await reportIncident(
        selected.type,
        currentLat,
        currentLng,
        currentHeading,
        currentRoadName
      );
      if (res.status === 'ok' && res.incident) {
        if (onIncidentReported) onIncidentReported(res.incident);
        if (onIncidentUpdated) onIncidentUpdated();
      }
    } catch (err) {
      console.error('Failed to submit incident report:', err);
    }
  };

  const handleUndo = () => {
    if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
    setPendingIncident(null);
  };

  const handleVote = async (vote: 'yes' | 'no') => {
    if (!nearbyIncidentToVerify) return;
    const incId = nearbyIncidentToVerify.id;
    hasVotedIncidentsRef.current.add(incId);
    setNearbyIncidentToVerify(null);

    try {
      await verifyIncident(incId, vote);
      if (onIncidentUpdated) onIncidentUpdated();
    } catch (err) {
      console.error('Failed to verify incident:', err);
    }
  };

  if (!isNavigating) return null;

  return (
    <>
      {/* ── 1. Floating Report Action Button (Bottom Right) ───────────── */}
      <div className="fixed right-4 sm:right-6 bottom-[100px] sm:bottom-[104px] z-[1001] pointer-events-auto">
        <button
          type="button"
          onClick={() => setSheetOpen(true)}
          title="Report incident"
          aria-label="Report incident"
          className="w-11 h-11 sm:w-12 sm:h-12 rounded-full bg-white text-amber-500 shadow-2xl shadow-black/40 border border-slate-300 flex items-center justify-center hover:bg-slate-50 active:scale-95 transition cursor-pointer"
        >
          {/* Google Maps Amber Warning Triangle with '+' icon */}
          <div className="relative flex items-center justify-center">
            <svg
              className="w-6 h-6 sm:w-6.5 sm:h-6.5 text-amber-500 fill-amber-100/70"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
              <line x1="12" y1="10" x2="12" y2="16" />
              <line x1="9" y1="13" x2="15" y2="13" />
            </svg>
          </div>
        </button>
      </div>

      {/* ── 2. "Still here?" Proximity Verification Dialog ──────────── */}
      {nearbyIncidentToVerify && (
        <div className="fixed top-28 left-4 right-4 sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-md z-[1002] pointer-events-auto animate-in fade-in slide-in-from-top-4 duration-200">
          <div className="bg-white/95 backdrop-blur-md rounded-2xl p-4 shadow-2xl border border-slate-200 text-slate-800 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900 leading-tight">
                  {nearbyIncidentToVerify.title} ahead
                </h4>
                <p className="text-xs text-slate-500">Is it still there?</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleVote('no')}
                className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition active:scale-95"
              >
                No
              </button>
              <button
                type="button"
                onClick={() => handleVote('yes')}
                className="px-3.5 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition active:scale-95 shadow-md shadow-teal-600/30"
              >
                Yes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── 3. Bottom Sheet: "Add a report" Grid (Matches Screenshot 2) ── */}
      {sheetOpen && (
        <div className="fixed inset-0 z-[1005] pointer-events-auto flex flex-col justify-end">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
            onClick={() => setSheetOpen(false)}
          />

          {/* Slide-up Container */}
          <div className="relative w-full max-w-lg mx-auto bg-white rounded-t-3xl shadow-2xl p-5 pb-8 animate-in slide-in-from-bottom duration-200 font-sans">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-slate-900 tracking-tight">Add a report</h3>
              <button
                type="button"
                onClick={() => setSheetOpen(false)}
                className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-700 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 2-Column Grid */}
            <div className="grid grid-cols-2 gap-3 max-h-[65vh] overflow-y-auto pr-1">
              {INCIDENT_OPTIONS.map((item) => (
                <button
                  key={item.type}
                  type="button"
                  onClick={() => handleSelectOption(item)}
                  className="bg-[#f0f4f9] hover:bg-[#e4ebf5] active:scale-[0.98] transition rounded-2xl p-4 flex flex-col items-center justify-center gap-2.5 text-center min-h-[110px] cursor-pointer"
                >
                  <div
                    className={`w-11 h-11 rounded-full flex items-center justify-center shadow-sm ${
                      item.theme === 'red' ? 'bg-[#d93025]' : 'bg-[#fbbc04]'
                    }`}
                  >
                    {item.icon}
                  </div>
                  <span className="text-sm font-semibold text-slate-800 leading-snug">
                    {item.label}
                  </span>
                </button>
              ))}
            </div>

            {/* Bottom Safe Area */}
            <div className="w-12 h-1 bg-slate-300 rounded-full mx-auto mt-4" />
          </div>
        </div>
      )}

      {/* ── 4. Confirmation Drawer with Countdown (Matches Screenshot 3) ── */}
      {pendingIncident && (
        <div className="fixed bottom-0 left-0 right-0 z-[1006] pointer-events-auto">
          <div className="w-full max-w-lg mx-auto bg-white rounded-t-3xl shadow-2xl p-5 pb-7 border-t border-slate-100 animate-in slide-in-from-bottom duration-200">
            {/* Heading row */}
            <div className="flex items-center gap-3 mb-5">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                  pendingIncident.theme === 'red' ? 'bg-[#d93025]' : 'bg-[#fbbc04]'
                }`}
              >
                {pendingIncident.icon}
              </div>
              <span className="text-xl font-bold text-slate-900">
                Reporting {pendingIncident.label.toLowerCase()}
              </span>
            </div>

            {/* Undo / Done Action Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={handleUndo}
                className="py-3.5 px-4 rounded-full bg-[#dcf1fb] hover:bg-[#cde9f7] active:scale-[0.98] text-[#006584] font-bold text-base transition flex items-center justify-center gap-2 cursor-pointer"
              >
                Undo
              </button>

              <button
                type="button"
                onClick={() => handleConfirmReport(pendingIncident)}
                className="relative overflow-hidden py-3.5 px-4 rounded-full bg-[#006874] hover:bg-[#005762] active:scale-[0.98] text-white font-bold text-base transition flex items-center justify-center gap-2 cursor-pointer shadow-md"
              >
                {/* Visual Progress Bar filling up */}
                <div
                  className="absolute inset-0 bg-[#004f58]/40 origin-left transition-all duration-1000"
                  style={{ width: `${((5 - countdown) / 5) * 100}%` }}
                />
                <span className="relative z-10 flex items-center gap-1.5">
                  Done ({countdown}s)
                </span>
              </button>
            </div>

            {/* Bottom Handle */}
            <div className="w-12 h-1 bg-slate-300 rounded-full mx-auto mt-4" />
          </div>
        </div>
      )}
    </>
  );
};

export default IncidentReportModal;

