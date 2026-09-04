import { Point, RouteMode, RouteResponse, SearchResult } from './types';

// Explicit IPv4 API Base to prevent IPv6/IPv4 localhost connection mismatch
const getApiBase = () => {
  return 'http://127.0.0.1:8000';
};

/**
 * Searches places using Google Places Autocomplete (client-side)
 * or falls back to backend Nominatim / Places API.
 */
export async function searchPlaces(query: string, signal?: AbortSignal): Promise<SearchResult[]> {
  if (!query || query.trim().length < 2) return [];

  // Try Google Places JavaScript Autocomplete Service if available in browser
  if (typeof window !== 'undefined' && window.google?.maps?.places?.AutocompleteService) {
    try {
      const autoService = new window.google.maps.places.AutocompleteService();
      const geocoder = new window.google.maps.Geocoder();

      const predictions = await new Promise<google.maps.places.AutocompletePrediction[]>((resolve) => {
        autoService.getPlacePredictions(
          {
            input: query.trim(),
            componentRestrictions: { country: 'in' },
          },
          (res, status) => {
            if (status === window.google.maps.places.PlacesServiceStatus.OK && res) {
              resolve(res.slice(0, 5));
            } else {
              resolve([]);
            }
          }
        );
      });

      if (predictions.length > 0) {
        const results = await Promise.all(
          predictions.map(async (pred) => {
            const geoRes = await geocoder.geocode({ placeId: pred.place_id });
            if (geoRes.results && geoRes.results.length > 0) {
              const loc = geoRes.results[0].geometry.location;
              return {
                name: pred.structured_formatting?.main_text || pred.description.split(',')[0],
                address: pred.description,
                lat: loc.lat(),
                lng: loc.lng(),
              };
            }
            return null;
          })
        );
        const valid = results.filter((r): r is SearchResult => r !== null);
        if (valid.length > 0) return valid;
      }
    } catch (e) {
      console.warn('Google Places search fallback:', e);
    }
  }

  // Fallback to Python backend search endpoint
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);
    const combinedSignal = signal || controller.signal;

    const res = await fetch(`${getApiBase()}/search?q=${encodeURIComponent(query.trim())}`, {
      signal: combinedSignal,
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      if (data.results && data.results.length > 0) return data.results;
    }
  } catch (err: any) {
    if (err.name === 'AbortError') return [];
  }

  return [];
}

/**
 * Calculates route strictly using YOUR Python Backend Algorithm (A*, 2W Penalties, Dynamic Traffic)
 * on http://127.0.0.1:8000.
 */
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
      throw new Error(errJson.message || `Backend server returned status ${res.status}`);
    }

    const data: RouteResponse = await res.json();
    if (data.status === 'error') {
      throw new Error(data.message || 'Route could not be calculated by algorithm.');
    }

    return data;
  } catch (err: any) {
    if (err.name === 'AbortError') {
      return {
        status: 'error',
        message: 'Routing request timed out. Make sure api_server.py is running.',
      };
    }
    console.error('Error fetching route from backend algorithm:', err);
    return {
      status: 'error',
      message:
        err.message ||
        'Failed to connect to backend server. Make sure `python api_server.py` is running on port 8000.',
    };
  }
}

export interface BothRoutesResponse {
  shortest: RouteResponse | null;
  dynamic: RouteResponse | null;
  fastestChoice: 'shortest' | 'dynamic';
  timeDiffMins: number;
}

/**
 * Fetches both Shortest Path and Dynamic Traffic Route in parallel to compare timings.
 */
export async function fetchBothRoutes(
  from: Point,
  to: Point,
  signal?: AbortSignal
): Promise<BothRoutesResponse> {
  const [shortestRes, dynamicRes] = await Promise.allSettled([
    fetchRoute('shortest', from, to, signal),
    fetchRoute('dynamic', from, to, signal),
  ]);

  const shortest =
    shortestRes.status === 'fulfilled' && shortestRes.value.status === 'success'
      ? shortestRes.value
      : null;
  const dynamic =
    dynamicRes.status === 'fulfilled' && dynamicRes.value.status === 'success'
      ? dynamicRes.value
      : null;

  const shortestKm = shortest?.distance_km || 0;
  const shortestEstMins = shortest ? Math.max(2, Math.round((shortestKm / 28) * 60)) : Infinity;

  const dynamicEstMins = dynamic?.google_base_duration_mins
    ? Math.round(dynamic.google_base_duration_mins)
    : dynamic
    ? Math.max(2, Math.round(((dynamic.distance_km || 0) / 28) * 60))
    : Infinity;

  const fastestChoice: 'shortest' | 'dynamic' =
    dynamicEstMins <= shortestEstMins && dynamic ? 'dynamic' : 'shortest';

  const timeDiffMins = Math.abs(shortestEstMins - dynamicEstMins);

  return {
    shortest,
    dynamic,
    fastestChoice,
    timeDiffMins: isFinite(timeDiffMins) ? timeDiffMins : 0,
  };
}

