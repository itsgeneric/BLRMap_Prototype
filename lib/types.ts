export type LatLng = [number, number];

export interface Point {
  lat: number;
  lng: number;
  name?: string;
  address?: string;
}

export type RouteMode = 'shortest' | 'dynamic' | 'fastest';

export interface TurnManeuver {
  type: 'depart' | 'turn_left' | 'slight_left' | 'straight' | 'slight_right' | 'turn_right' | 'u_turn' | 'arrive';
  instruction: string;
  road_name: string;
  distance_m: number;
  lat: number;
  lng: number;
}

export interface CandidateRoute {
  strategy: string;
  distance_km?: number | null;
  weighted_cost?: number | null;
  traffic_minutes?: number | null;
  traffic_seconds?: number | null;
  split_fraction?: number | null;
}

export interface RouteResponse {
  status: 'success' | 'error';
  message?: string;
  journey_id?: string;
  path?: LatLng[];
  distance_km?: number;
  /** planned travel time in seconds: sent by the backend, or filled in by the app (lib/routeInfo.ts) */
  duration_s?: number;
  /** true when the app had to estimate duration_s because the backend sent none */
  time_from_app?: boolean;
  /** where the route really starts / ends (on a road) and how far that is from the pin */
  origin_snap?: SnapInfo | null;
  destination_snap?: SnapInfo | null;
  weighted_cost?: number;
  best_strategy?: string;
  google_base_duration_mins?: number | null;
  congested_nodes_avoided?: number;
  candidate_routes?: CandidateRoute[];
  maneuvers?: TurnManeuver[];
  waypoints_used?: number;
  /** true when the request was cancelled because a newer one replaced it: not an error, nothing to show */
  aborted?: boolean;
}

export interface GPSPosition {
  lat: number;
  lng: number;
  heading: number | null; // 0-360 degrees
  speed: number | null;   // meters per second
  accuracy?: number;      // meters
  timestamp: number;
}

export interface SearchResult {
  name: string;
  address: string;
  lat: number;
  lng: number;
}

export interface TwoWheelerOptions {
  mainRoadPenalty: number;
  innerRoadMultiplier: number;
  serviceMultiplier: number;
  segmentKm: number;
}

export type ThemeMode = 'dark' | 'light';

export interface ToastMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  text: string;
  duration?: number;
}

export interface TripSummary {
  distanceKm: number;
  timeTakenSec: number;
  avgSpeedKmh: number;
  originName: string;
  destinationName: string;
}

export interface JourneyPlaceInfo {
  name: string;
  address?: string;
  lat: number;
  lng: number;
}

export interface JourneyStartPayload {
  session_id: string;
  origin: JourneyPlaceInfo;
  destination: JourneyPlaceInfo;
}

export interface JourneyCompletePayload {
  actual_duration_secs: number;
  actual_avg_speed_kmh: number;
}

export interface ReroutePayload {
  lat: number;
  lng: number;
  distance_off_route_m: number;
  time_since_start_secs: number;
}

// ---------------------------------------------------------------------------
// Incident Reporting Types
// ---------------------------------------------------------------------------

export type IncidentType =
  | 'crash'
  | 'slowdown'
  | 'construction'
  | 'lane_closure'
  | 'hazard'
  | 'flooded'
  | 'visibility';

export interface RoadIncident {
  id: string;
  type: IncidentType;
  title: string;
  lat: number;
  lng: number;
  heading?: number;
  road_name?: string;
  created_at: string;
  expires_at: string;
  status: 'active' | 'resolved' | 'expired';
  upvotes: number;
  downvotes: number;
}

export interface SnapInfo {
  lat: number;
  lng: number;
  distance_m: number;
}
