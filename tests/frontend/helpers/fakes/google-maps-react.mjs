// Stand-in for @vis.gl/react-google-maps. A test puts its fake map on globalThis.__fakeMap.
export function APIProvider() {
  return null;
}
export function Map() {
  return null;
}
export function AdvancedMarker() {
  return null;
}
export function Pin() {
  return null;
}
export const RenderingType = { VECTOR: 'VECTOR', RASTER: 'RASTER' };
export const AdvancedMarkerAnchorPoint = { CENTER: ['50%', '50%'], BOTTOM: ['50%', '100%'] };
export const useMap = () => globalThis.__fakeMap ?? null;
export const useMapsLibrary = () => globalThis.__fakeMarkerLib ?? null;
// the rider marker: the map moves it imperatively, so a test only needs the object
export const useAdvancedMarkerRef = () => [() => {}, globalThis.__riderMarker ?? null];
