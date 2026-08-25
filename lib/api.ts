import { Point, RouteMode, RouteResponse, TwoWheelerOptions, SearchResult } from './types';

const API_BASE = typeof window !== 'undefined' ? '/api/backend' : 'http://127.0.0.1:8000';

export async function searchPlaces(query: string): Promise<SearchResult[]> {
  if (!query || query.trim().length < 2) return [];
  try {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
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


  try {
    const res = await fetch(`${API_BASE}${endpoint}?${params.toString()}`);
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
