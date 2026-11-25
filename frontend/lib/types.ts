export type LatLng = [number, number];

export interface Point {
  lat: number;
  lng: number;
  name?: string;
  address?: string;
}

export type RouteMode = 'shortest' | 'dynamic' | 'fastest';

export type ManeuverType =
  | 'depart'
  | 'arrive'
  | 'straight'
  | 'continue'
  | 'turn_left'
  | 'turn_right'
  | 'slight_left'
  | 'slight_right'
  | 'sharp_left'
  | 'sharp_right'
  | 'keep_left'
  | 'keep_right'
  | 'u_turn'
  | 'roundabout';

export interface TurnManeuver {
  type: ManeuverType;
  instruction: string;      // full sentence, e.g. "Turn left onto 100 Feet Road"
  road_name: string;        // '' when the road is unnamed
  distance_m: number;       // distance from this maneuver to the next one
  along_m?: number;         // position along the route polyline, metres from its start
  lat: number;
  lng: number;
  exit?: number | null;     // roundabout exit number
  side?: 'left' | 'right' | null; // arrive: side of the road the destination is on
  bearing_before?: number;
  bearing_after?: number;
}

/** Rider position used for drawing and camera during navigation (snapped to the route). */
export interface NavPose {
  lat: number;
  lng: number;
  bearing: number;          // direction of travel, degrees
  along: number;            // metres along the route
  speedMps: number;
  onRoute: boolean;
  timestamp: number;
}

export type NavStatus = 'idle' | 'navigating' | 'rerouting' | 'arrived';

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
  duration_mins?: number;
  weighted_cost?: number;
  best_strategy?: string;
  google_base_duration_mins?: number | null;
  congested_nodes_avoided?: number;
  candidate_routes?: CandidateRoute[];
  maneuvers?: TurnManeuver[];
  waypoints_used?: number;
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

