import { Point, RouteMode, RouteResponse, SearchResult } from './types';

// Dynamic API Base: Automatically uses port 8000 on current host (localhost or 192.168.0.180)
const getApiBase = () => {
  if (typeof window !== 'undefined') {
    return `http://${window.location.hostname}:8000`;
  }
  return 'http://127.0.0.1:8000';
};

export async function searchPlaces(query: string): Promise<SearchResult[]> {
  if (!query || query.trim().length < 2) return [];
  try {
    const res = await fetch(`${getApiBase()}/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || [];
  } catch (err) {
    console.error('Error searching places:', err);
    return [];
  }
}

export async function fetchRoute(
  mode: RouteMode,
  from: Point,
  to: Point
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
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return await res.json();
  } catch (err: any) {
    console.error('Error fetching route:', err);
    return {
      status: 'error',
      message: err.message || 'Failed to connect to backend server.',
    };
  }
}
