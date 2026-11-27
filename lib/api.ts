import { Point, RouteMode, RouteResponse, SearchResult, IncidentType, RoadIncident } from './types';

import { API_BASE } from './apiBase';
import { completeRoute, comparisonMinutes } from './routeInfo';
import { requestRoute } from './routeClient';
import { shortPlaceName } from './pinActions';

// Backend address: see lib/apiBase.ts (NEXT_PUBLIC_API_BASE, set before `npm run build`).
const getApiBase = () => API_BASE;


/**
 * Searches places using Google Places Autocomplete (client-side)
 * or falls back to backend Nominatim / Places API.
 */
export async function searchPlaces(query: string, signal?: AbortSignal): Promise<SearchResult[]> {
  if (!query || query.trim().length < 2) return [];

  // Try Google Places JavaScript Autocomplete (New: AutocompleteSuggestion / Place Autocomplete, or fallback to AutocompleteService)
  if (typeof window !== 'undefined' && window.google?.maps?.places) {
    try {
      // 1. Try modern AutocompleteSuggestion from Google Maps JavaScript API
      const placesLib = window.google.maps.places as any;
      if (placesLib.AutocompleteSuggestion && placesLib.AutocompleteSuggestion.fetchAutocompleteSuggestions) {
        const request = {
          input: query.trim(),
          region: 'in',
          locationBias: {
            center: { lat: 12.9716, lng: 77.5946 },
            radius: 50000,
          },
        };
        const { suggestions } = await placesLib.AutocompleteSuggestion.fetchAutocompleteSuggestions(request);
        if (suggestions && suggestions.length > 0) {
          const results: (SearchResult | null)[] = await Promise.all(
            suggestions.slice(0, 5).map(async (sugg: any) => {
              try {
                const placePrediction = sugg.placePrediction;
                if (!placePrediction) return null;
                const place = placePrediction.toPlace();
                await place.fetchFields({ fields: ['displayName', 'formattedAddress', 'location'] });
                if (place.location) {
                  return {
                    name: place.displayName || placePrediction.mainText?.text || placePrediction.text?.text,
                    address: place.formattedAddress || placePrediction.text?.text || '',
                    lat: typeof place.location.lat === 'function' ? place.location.lat() : place.location.lat,
                    lng: typeof place.location.lng === 'function' ? place.location.lng() : place.location.lng,
                  };
                }
              } catch (err) {}
              return null;
            })
          );
          const valid = results.filter((r): r is SearchResult => r !== null);
          if (valid.length > 0) return valid;
        }
      }

      // 2. Fallback to classic AutocompleteService + Geocoder
      if (placesLib.AutocompleteService) {
        const autoService = new placesLib.AutocompleteService();
        const geocoder = new window.google.maps.Geocoder();

        const predictions = await new Promise<any[]>((resolve) => {
          autoService.getPlacePredictions(
            {
              input: query.trim(),
              componentRestrictions: { country: 'in' },
            },
            (res: any, status: any) => {
              if (status === window.google.maps.places.PlacesServiceStatus.OK && res) {
                resolve(res.slice(0, 5));
              } else {
                resolve([]);
              }
            }
          );
        });

        if (predictions && predictions.length > 0) {
          const results = await Promise.all(
            predictions.map(async (pred) => {
              try {
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
              } catch (e) {}
              return null;
            })
          );
          const valid = results.filter((r): r is SearchResult => r !== null);
          if (valid.length > 0) return valid;
        }
      }
    } catch (e) {
      console.warn('Google Places JS search fallback to backend:', e);
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
  // All the request logic (timeout, retries, cancel handling, readable errors) lives in lib/routeClient.ts, where it is tested.
  const res = await requestRoute(
    { fetchImpl: (input, init) => fetch(input, init), baseUrl: getApiBase() },
    mode,
    from,
    to,
    signal
  );
  return completeRoute(res); // travel time and turn list (see lib/routeInfo.ts)
}

export interface BothRoutesResponse {
  shortest: RouteResponse | null;
  dynamic: RouteResponse | null;
  fastestChoice: 'shortest' | 'dynamic';
  timeDiffMins: number;
  /** a request was cancelled by a newer one: the caller should ignore this result silently */
  aborted?: boolean;
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

  const aborted = [shortestRes, dynamicRes].some((r) => r.status === 'fulfilled' && r.value.aborted === true);

  const shortest =
    shortestRes.status === 'fulfilled' && shortestRes.value.status === 'success'
      ? shortestRes.value
      : null;
  const dynamic =
    dynamicRes.status === 'fulfilled' && dynamicRes.value.status === 'success'
      ? dynamicRes.value
      : null;

  // The backend times both routes with one model; compare those times. Only for a backend that sends none is the app's
  // original comparison used. Either way each route keeps the compared time, so the cards, the choice and the arrival
  // time during the ride all show the same number.
  if (shortest?.time_from_app || dynamic?.time_from_app) {
    const compared = comparisonMinutes(shortest, dynamic);
    if (shortest) shortest.duration_s = compared.shortest * 60;
    if (dynamic) dynamic.duration_s = compared.dynamic * 60;
  }
  const minutes = (route: typeof shortest) => (route?.duration_s != null ? Math.max(1, Math.round(route.duration_s / 60)) : Infinity);
  const shortestEstMins = minutes(shortest);
  const dynamicEstMins = minutes(dynamic);

  const fastestChoice: 'shortest' | 'dynamic' =
    dynamicEstMins < shortestEstMins && dynamic ? 'dynamic' : 'shortest';

  const timeDiffMins = Math.abs(shortestEstMins - dynamicEstMins);

  return {
    shortest,
    dynamic,
    fastestChoice,
    timeDiffMins: isFinite(timeDiffMins) ? timeDiffMins : 0,
    aborted,
  };
}


// ---------------------------------------------------------------------------
// Incident Reporting API Client
// ---------------------------------------------------------------------------

export async function reportIncident(
  type: IncidentType,
  lat: number,
  lng: number,
  heading?: number | null,
  roadName?: string,
  sessionId?: string
): Promise<{ status: string; incident?: RoadIncident; message?: string }> {
  try {
    const res = await fetch(`${getApiBase()}/incidents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type,
        lat,
        lng,
        heading: heading ?? null,
        road_name: roadName ?? null,
        session_id: sessionId ?? null,
      }),
    });
    return await res.json();
  } catch (err) {
    console.error('Failed to report incident:', err);
    return { status: 'error', message: 'Failed to submit report' };
  }
}

export async function fetchActiveIncidents(params?: {
  minLat?: number;
  minLng?: number;
  maxLat?: number;
  maxLng?: number;
  lat?: number;
  lng?: number;
  radiusM?: number;
}): Promise<RoadIncident[]> {
  try {
    const url = new URL(`${getApiBase()}/incidents`);
    if (params) {
      if (params.minLat !== undefined) url.searchParams.set('min_lat', params.minLat.toString());
      if (params.minLng !== undefined) url.searchParams.set('min_lng', params.minLng.toString());
      if (params.maxLat !== undefined) url.searchParams.set('max_lat', params.maxLat.toString());
      if (params.maxLng !== undefined) url.searchParams.set('max_lng', params.maxLng.toString());
      if (params.lat !== undefined) url.searchParams.set('lat', params.lat.toString());
      if (params.lng !== undefined) url.searchParams.set('lng', params.lng.toString());
      if (params.radiusM !== undefined) url.searchParams.set('radius_m', params.radiusM.toString());
    }
    const res = await fetch(url.toString());
    const data = await res.json();
    return data.incidents || [];
  } catch (err) {
    console.error('Failed to fetch active incidents:', err);
    return [];
  }
}

export async function verifyIncident(
  incidentId: string,
  vote: 'yes' | 'no',
  sessionId?: string
): Promise<{ status: string; message?: string }> {
  try {
    const res = await fetch(`${getApiBase()}/incidents/${incidentId}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vote, session_id: sessionId }),
    });
    return await res.json();
  } catch (err) {
    console.error('Failed to verify incident:', err);
    return { status: 'error', message: 'Network error verifying incident' };
  }
}


/** Name and address of a point on the map (Google Geocoder, already loaded with the map). Always resolves, with a fallback. */
export async function reverseGeocode(lat: number, lng: number): Promise<{ name: string; address: string }> {
  const fallback = { name: 'Dropped pin', address: `${lat.toFixed(5)}, ${lng.toFixed(5)}` };
  if (typeof window === 'undefined' || !(window as any).google?.maps?.Geocoder) return fallback;
  try {
    const geocoder = new (window as any).google.maps.Geocoder();
    const answer: any = await Promise.race([
      geocoder.geocode({ location: { lat, lng } }),
      new Promise((_, reject) => setTimeout(() => reject(new Error('geocoder timeout')), 4000)),
    ]);
    const best = answer?.results?.[0];
    if (!best?.formatted_address) return fallback;
    return { name: shortPlaceName(best.formatted_address), address: best.formatted_address };
  } catch {
    return fallback;
  }
}
