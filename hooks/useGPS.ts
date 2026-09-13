'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { GPSPosition } from '@/lib/types';

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
  const gpsPositionRef = useRef<GPSPosition | null>(null);

  useEffect(() => {
    gpsPositionRef.current = gpsPosition;
  }, [gpsPosition]);

  // Compass Heading Listener
  useEffect(() => {
    if (!options.enableCompass || typeof window === 'undefined' || !window.DeviceOrientationEvent) return;

    const handleOrientation = (e: DeviceOrientationEvent) => {
      if (e.alpha !== null) {
        const compass = (e as any).webkitCompassHeading ?? (360 - e.alpha);
        setDeviceHeading(Math.round(compass));
      }
    };

    window.addEventListener('deviceorientation', handleOrientation, true);
    return () => window.removeEventListener('deviceorientation', handleOrientation, true);
  }, [options.enableCompass]);

  // Single Hardware GPS Watcher
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

        prevCoords.current = { lat: pos.coords.latitude, lng: pos.coords.longitude };

        const currentPos: GPSPosition = {
          lat: Number(pos.coords.latitude.toFixed(6)),
          lng: Number(pos.coords.longitude.toFixed(6)),
          heading: heading !== null ? Math.round(heading) : deviceHeading,
          speed: pos.coords.speed !== null && pos.coords.speed >= 0 ? pos.coords.speed : 0,
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
  }, [deviceHeading]);

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
          heading: pos.coords.heading || deviceHeading || 0,
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
  }, [deviceHeading]);

  return {
    gpsPosition,
    deviceHeading,
    isLocating,
    permissionState,
    error,
    getCurrentLocation,
  };
}
