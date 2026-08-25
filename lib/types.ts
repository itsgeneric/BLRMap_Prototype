export type LatLng = [number, number];

export interface Point {
  lat: number;
  lng: number;
  name?: string;
  address?: string;
}

export type RouteMode = 'shortest' | 'dynamic';


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
  path?: LatLng[];
  distance_km?: number;
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
  accuracy: number;       // meters
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
