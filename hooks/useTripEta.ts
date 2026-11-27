'use client';

import { useEffect, useRef, useState } from 'react';
import { GPSPosition } from '@/lib/types';
import { EtaEstimator, SpeedSmoother } from '@/lib/eta';

interface UseTripEtaProps {
  isNavigating: boolean;
  /** length of the active route, metres */
  totalM: number;
  /** the server's planned duration of the active route, seconds (null = unknown) */
  plannedDurationS: number | null;
  /** distance still to go along the route, metres (from the navigation engine) */
  remainingM: number;
  gpsPosition: GPSPosition | null;
}

/**
 * Remaining time, arrival clock time and the speedometer, all from the same numbers (see lib/eta.ts).
 * The remaining time counts down every second; the estimate itself is refreshed on every position update.
 */
export function useTripEta({ isNavigating, totalM, plannedDurationS, remainingM, gpsPosition }: UseTripEtaProps) {
  const estimator = useRef(new EtaEstimator());
  const smoother = useRef(new SpeedSmoother());
  const [arrivalMs, setArrivalMs] = useState(0);
  const [speedKmh, setSpeedKmh] = useState(0);
  const [now, setNow] = useState(() => Date.now());
  const remainingRef = useRef(remainingM);
  remainingRef.current = remainingM;

  // A trip begins: fresh timing and a fresh speedometer.
  useEffect(() => {
    if (!isNavigating) return;
    estimator.current.startTrip(Date.now());
    smoother.current.reset();
    setArrivalMs(0);
  }, [isNavigating]);

  // The active route changed (first route, or a reroute): the planned duration changes, the distance already covered is kept.
  useEffect(() => {
    if (!isNavigating || totalM <= 0) return;
    estimator.current.setRoute(totalM, plannedDurationS);
    // a route that has just been set is entirely ahead of the rider
    const t = Date.now();
    setArrivalMs(estimator.current.update(totalM, t).arrivalMs);
    setNow(t);
  }, [isNavigating, totalM, plannedDurationS]);

  // New progress along the route: refresh the estimate.
  useEffect(() => {
    if (!isNavigating || totalM <= 0) return;
    const t = Date.now();
    const result = estimator.current.update(remainingM, t);
    setArrivalMs(result.arrivalMs);
    setNow(t);
    // Only real progress triggers this. When the route changes, remainingM still holds the OLD route's value for one render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [remainingM]);

  // Speedometer: smoothed GPS speed (the GPS hook derives a speed from movement when the phone reports none).
  useEffect(() => {
    if (!gpsPosition) return;
    setSpeedKmh(smoother.current.push(gpsPosition.speed));
  }, [gpsPosition]);

  // Tick every second so the remaining time counts down smoothly between GPS fixes. Every 5 s the estimate is also refreshed
  // from the latest distance, so a rider who is stopped at a signal sees the arrival time slip later even with no new position.
  useEffect(() => {
    if (!isNavigating) return;
    let ticks = 0;
    const id = setInterval(() => {
      const t = Date.now();
      setNow(t);
      ticks += 1;
      if (ticks % 5 === 0 && totalM > 0) setArrivalMs(estimator.current.update(remainingRef.current, t).arrivalMs);
    }, 1000);
    return () => clearInterval(id);
  }, [isNavigating, totalM]);

  return {
    remainingS: isNavigating ? estimator.current.remainingAt(now) : 0,
    arrivalMs,
    speedKmh,
  };
}
