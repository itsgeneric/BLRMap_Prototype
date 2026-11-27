'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { GPSPosition } from '@/lib/types';
import { createSpeedEstimator } from '@/lib/gpsSpeed';

interface UseGPSOptions {
  enableCompass?: boolean;
}

export function useGPS(options: UseGPSOptions = { enableCompass: true }) {
  const [gpsPosition, setGpsPosition] = useState<GPSPosition | null>(null);
  const [deviceHeading, setDeviceHeading] = useState<number>(0);
  const [permissionState, setPermissionState] = useState<'granted' | 'prompt' | 'denied' | 'unknown'>('unknown');
  const [isLocating, setIsLocating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const prevCoords = useRef<{ lat: number; lng: number } | null>(null);
  const speedEstimator = useRef(createSpeedEstimator());
  const gpsPositionRef = useRef<GPSPosition | null>(null);
  const headingSmoothedRef = useRef<number>(0);
  const deviceHeadingRef = useRef<number>(0);

  useEffect(() => {
    gpsPositionRef.current = gpsPosition;
  }, [gpsPosition]);

  // Request iOS 13+ permission for DeviceOrientation
  const requestCompassPermission = useCallback(async (): Promise<boolean> => {
    if (typeof window === 'undefined') return false;
    const DOE = (window as any).DeviceOrientationEvent;
    if (DOE && typeof DOE.requestPermission === 'function') {
      try {
        const response = await DOE.requestPermission();
        return response === 'granted';
      } catch (e) {
        console.warn('Device orientation permission rejected:', e);
        return false;
      }
    }
    return true;
  }, []);

  // Smooth circular heading update using Exponential Moving Average (EMA)
  const updateSmoothedHeading = useCallback((rawHeading: number) => {
    if (isNaN(rawHeading)) return;
    const current = headingSmoothedRef.current;
    // Circular difference (-180 to +180)
    let diff = ((rawHeading - current + 540) % 360) - 180;
    // Discard tiny micro-vibrations (< 1.0 degree)
    if (Math.abs(diff) < 1.0) return;
    // EMA smoothing factor (0.35 allows swift responsive turning while eliminating sensor jitter)
    const next = ((current + diff * 0.35) % 360 + 360) % 360;
    headingSmoothedRef.current = next;
    const rounded = Math.round(next);
    deviceHeadingRef.current = rounded;
    setDeviceHeading(rounded);
  }, []);

  // Compass Heading Listener (Supports Android Absolute True North + iOS webkitCompassHeading)
  useEffect(() => {
    if (!options.enableCompass || typeof window === 'undefined') return;

    let absoluteFired = false;

    // 1. Android Chrome standard for True North: deviceorientationabsolute
    const handleAbsoluteOrientation = (e: DeviceOrientationEvent) => {
      if (e.alpha !== null) {
        absoluteFired = true;
        // alpha on absolute orientation is degrees counterclockwise from North -> convert to clockwise heading
        const heading = (360 - e.alpha) % 360;
        updateSmoothedHeading(heading);
      }
    };

    // 2. Fallback / iOS Safari: deviceorientation with webkitCompassHeading
    const handleStandardOrientation = (e: DeviceOrientationEvent) => {
      // If Android absolute listener is active and firing, skip standard to avoid conflicts
      if (absoluteFired && (e as any).webkitCompassHeading === undefined) return;

      if ((e as any).webkitCompassHeading !== undefined && (e as any).webkitCompassHeading !== null) {
        // iOS Safari provides True North directly in degrees
        updateSmoothedHeading(Math.round((e as any).webkitCompassHeading));
      } else if (e.alpha !== null) {
        const heading = (360 - e.alpha) % 360;
        updateSmoothedHeading(heading);
      }
    };

    if ('ondeviceorientationabsolute' in window) {
      window.addEventListener('deviceorientationabsolute', handleAbsoluteOrientation as EventListener, true);
    }
    window.addEventListener('deviceorientation', handleStandardOrientation as EventListener, true);

    return () => {
      if ('ondeviceorientationabsolute' in window) {
        window.removeEventListener('deviceorientationabsolute', handleAbsoluteOrientation as EventListener, true);
      }
      window.removeEventListener('deviceorientation', handleStandardOrientation as EventListener, true);
    };
  }, [options.enableCompass, updateSmoothedHeading]);

  // Single Hardware GPS Watcher (Runs continuously — NOT torn down on compass change)
  useEffect(() => {
    if (typeof window === 'undefined' || !('geolocation' in navigator)) {
      setError('Geolocation not supported');
      return;
    }

    if (navigator.permissions && navigator.permissions.query) {
      navigator.permissions.query({ name: 'geolocation' }).then((status) => {
        setPermissionState(status.state);
        status.onchange = () => setPermissionState(status.state);
      }).catch(() => {});
    }

    setIsLocating(true);

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        setIsLocating(false);
        setError(null);
        setPermissionState('granted');

        let heading = pos.coords.heading;
        if (heading === null || isNaN(heading)) {
          if (prevCoords.current) {
            const dlat = pos.coords.latitude - prevCoords.current.lat;
            const dlng = pos.coords.longitude - prevCoords.current.lng;
            if (Math.abs(dlat) > 0.00002 || Math.abs(dlng) > 0.00002) {
              heading = (Math.atan2(dlng, dlat) * 180 / Math.PI + 360) % 360;
            }
          }
        }

        // Speed: the phone's own value when it gives one; otherwise worked out from movement (see lib/gpsSpeed.ts)
        const derived = speedEstimator.current.push({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
          timestamp: pos.timestamp,
        });
        const speed = pos.coords.speed !== null && pos.coords.speed >= 0 ? pos.coords.speed : derived;

        prevCoords.current = { lat: pos.coords.latitude, lng: pos.coords.longitude };

        const currentPos: GPSPosition = {
          lat: Number(pos.coords.latitude.toFixed(6)),
          lng: Number(pos.coords.longitude.toFixed(6)),
          heading: heading !== null && !isNaN(heading) ? Math.round(heading) : deviceHeadingRef.current,
          speed,
          accuracy: pos.coords.accuracy,
          timestamp: pos.timestamp,
        };

        setGpsPosition(currentPos);
      },
      (err) => {
        setIsLocating(false);
        if (err.code === err.PERMISSION_DENIED) {
          setPermissionState('denied');
          setError('Location permission denied');
        } else {
          setError(err.message);
        }
      },
      {
        enableHighAccuracy: true,
        maximumAge: 2000,
        timeout: 10000,
      }
    );

    return () => {
      navigator.geolocation.clearWatch(watchId);
    };
  }, []); // Intentionally empty dependency array: keeps GPS watch active permanently

  // Effective Heading:
  // When rider is moving (> 1.5 m/s or > 5 km/h), GPS motion course is used.
  // When rider is stationary / stopped at signal or phone rotated in hand, device compass is used.
  const effectiveHeading = (gpsPosition && gpsPosition.speed !== null && gpsPosition.speed > 1.5 && gpsPosition.heading !== null && !isNaN(gpsPosition.heading))
    ? gpsPosition.heading
    : deviceHeading;

  // Robust one-shot locate function with instant cache check & standard accuracy fallback
  const getCurrentLocation = useCallback((): Promise<GPSPosition> => {
    return new Promise((resolve, reject) => {
      // 1. If recent GPS exists (< 15 seconds old), resolve instantly
      if (gpsPositionRef.current && Date.now() - gpsPositionRef.current.timestamp < 15000) {
        resolve(gpsPositionRef.current);
        return;
      }

      if (typeof window === 'undefined' || !navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }

      setIsLocating(true);

      const onSuccess = (pos: GeolocationPosition) => {
        setIsLocating(false);
        const current: GPSPosition = {
          lat: Number(pos.coords.latitude.toFixed(6)),
          lng: Number(pos.coords.longitude.toFixed(6)),
          heading: pos.coords.heading || deviceHeadingRef.current || 0,
          speed: pos.coords.speed || 0,
          accuracy: pos.coords.accuracy,
          timestamp: pos.timestamp,
        };
        setGpsPosition(current);
        resolve(current);
      };

      // 2. Query high-accuracy GPS with fallback to standard cellular/Wi-Fi accuracy
      navigator.geolocation.getCurrentPosition(
        onSuccess,
        (highErr) => {
          console.warn('High-accuracy GPS attempt timed out, trying fallback:', highErr.message);
          navigator.geolocation.getCurrentPosition(
            onSuccess,
            (fallbackErr) => {
              setIsLocating(false);
              reject(fallbackErr);
            },
            { enableHighAccuracy: false, timeout: 8000, maximumAge: 30000 }
          );
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 5000 }
      );
    });
  }, []);

  return {
    gpsPosition,
    deviceHeading,
    effectiveHeading,
    isLocating,
    permissionState,
    error,
    getCurrentLocation,
    requestCompassPermission,
  };
}
