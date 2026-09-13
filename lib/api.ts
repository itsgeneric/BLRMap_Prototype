import { Point, RouteMode, RouteResponse, SearchResult } from './types';

// Dynamic API Base with graceful fallbacks
const getApiBase = () => {
  if (typeof window !== 'undefined') {
    // If running on browser, try direct backend port first
    return `http://${window.location.hostname}:8000`;
  }
  return 'http://127.0.0.1:8000';
};

export async function searchPlaces(query: string, signal?: AbortSignal): Promise<SearchResult[]> {
  if (!query || query.trim().length < 2) return [];
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);
    
    // Combine with passed signal if provided
    const combinedSignal = signal || controller.signal;

    const res = await fetch(`${getApiBase()}/search?q=${encodeURIComponent(query.trim())}`, {
      signal: combinedSignal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) return [];
    const data = await res.json();
    return data.results || [];
  } catch (err: any) {
    if (err.name === 'AbortError') return [];
    console.warn('Search places notice:', err?.message || err);
    return [];
  }
}

export async function fetchRoute(
  mode: RouteMode,
  from: Point,
  to: Point,
  signal?: AbortSignal
): Promise<RouteResponse> {
  const endpoint = mode === 'dynamic' ? '/dynamic-route' : '/route';
  const params = new URLSearchParams({
    from_lat: from.lat.toString(),
    from_lng: from.lng.toString(),
    to_lat: to.lat.toString(),
    to_lng: to.lng.toString(),
  });

  const url = `${getApiBase()}${endpoint}?${params.toString()}`;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 12000); // 12s timeout

    const res = await fetch(url, { signal: signal || controller.signal });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.message || `Server returned status ${res.status}`);
    }

    const data: RouteResponse = await res.json();
    if (data.status === 'error') {
      throw new Error(data.message || 'Route could not be calculated.');
    }

    return data;
  } catch (err: any) {
    if (err.name === 'AbortError') {
      return {
        status: 'error',
        message: 'Request timed out. Please try again.',
      };
    }
    console.error('Error fetching route:', err);
    return {
      status: 'error',
      message: err.message || 'Failed to connect to backend server. Make sure api_server.py is running on port 8000.',
    };
  }
}
