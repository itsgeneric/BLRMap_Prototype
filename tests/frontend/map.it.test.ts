// The real map component driven by a fake Google map: gestures, the pin, the compass and the navigation camera.
// What Google actually draws on a phone cannot be tested here.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test, before, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';
import { render, find, findAll, nameOf } from './helpers/fakes/react.mjs';
import { installBrowser, sleep, PATH, north, east } from './helpers/env.mjs';

let MapContainer: any;
let Inner: any;
let frames: ((t: number) => void)[] = [];
let mounted: any[] = [];

const element = () => {
  const target = new EventTarget() as any;
  target.style = {};
  target.appendChild = () => {};
  target.clientHeight = 800;
  target.getBoundingClientRect = () => ({ left: 10, top: 20, width: 400, height: 800 });
  return target;
};

function fakeMap() {
  const listeners = new Map<number, { type: string; fn: any }>();
  let id = 0;
  const div = element();
  const state = { zoom: 16, heading: 0, tilt: 0, center: { lat: north(0), lng: east(0) } };
  const cameras: any[] = [];
  return {
    div,
    state,
    cameras,
    listeners,
    addListener(type: string, fn: any) {
      const key = ++id;
      listeners.set(key, { type, fn });
      return { remove: () => listeners.delete(key) };
    },
    emit(type: string, arg?: any) {
      for (const l of [...listeners.values()]) if (l.type === type) l.fn(arg);
    },
    getDiv: () => div,
    getZoom: () => state.zoom,
    getHeading: () => state.heading,
    getTilt: () => state.tilt,
    getCenter: () => ({ lat: () => state.center.lat, lng: () => state.center.lng }),
    getRenderingType: () => 'VECTOR',
    moveCamera(c: any) {
      cameras.push(c);
      Object.assign(state, c);
      if (c.heading !== undefined) this.emit('heading_changed');
    },
    panTo(c: any) { state.center = c; },
    setZoom(z: number) { state.zoom = z; },
    setHeading(h: number) { state.heading = h; },
    setTilt(t: number) { state.tilt = t; },
    setOptions() {},
    fitBounds() {},
  };
}

const lines: any[] = [];
function installGoogle() {
  class Polyline {
    options: any;
    path: any[] = [];
    shown = false;
    constructor(o: any = {}) { this.options = o; this.shown = !!o.map; lines.push(this); }
    setPath(p: any[]) { this.path = [...p]; }
    getPath() {
      const path = this.path;
      return { getLength: () => path.length, setAt: (i: number, v: any) => { path[i] = v; } };
    }
    setMap(m: any) { this.shown = !!m; }
    setOptions(o: any) { Object.assign(this.options, o); }
    addListener() { return { remove() {} }; }
  }
  class OverlayView {
    map: any = null;
    onAdd = () => {};
    setMap(m: any) { this.map = m; if (m) this.onAdd(); }
    getProjection() {
      return { fromContainerPixelToLatLng: (p: any) => ({ lat: () => 13 - p.y / 10000, lng: () => 77 + p.x / 10000 }) };
    }
  }
  (globalThis as any).google = {
    maps: {
      Polyline,
      OverlayView,
      Point: class { x: number; y: number; constructor(x: number, y: number) { this.x = x; this.y = y; } },
      LatLng: class { lat: number; lng: number; constructor(lat: number, lng: number) { this.lat = lat; this.lng = lng; } },
      LatLngBounds: class { extend() {} },
      event: { removeListener: (h: any) => h.remove() },
    },
  };
  const doc = new EventTarget() as any;
  doc.hidden = false;
  (globalThis as any).document = doc;
  (globalThis as any).requestAnimationFrame = (fn: any) => frames.push(fn);
  (globalThis as any).cancelAnimationFrame = () => {};
}

before(async () => {
  installBrowser();
  installGoogle();
  const mod = await import('../../components/Map/GoogleMapContainer.tsx');
  MapContainer = mod.GoogleMapContainer;
  const outer = render(MapContainer, {});
  Inner = find(outer.result(), 'GoogleMapInner').type;
});

afterEach(() => {
  mounted.splice(0).forEach((m) => m.unmount());
  frames = [];
});

function mount(props: any = {}) {
  const map = fakeMap();
  (globalThis as any).__fakeMap = map;
  const marker: any = { position: null };
  (globalThis as any).__riderMarker = marker;
  lines.length = 0;
  const presses: any[] = [];
  const calls = { recenter: 0, pan: 0 };
  const all = {
    onLongPress: (p: any) => presses.push(p),
    onRecenter: () => calls.recenter++,
    onCameraUnlink: () => calls.pan++,
    isFollowingCamera: true,
    ...props,
  };
  const view = render(Inner, all);
  mounted.push(view);
  const touch = (type: string, ...points: [number, number][]) => {
    const event = new Event(type) as any;
    event.touches = points.map(([clientX, clientY]) => ({ clientX, clientY }));
    map.div.dispatchEvent(event);
  };
  return {
    map, view, presses, calls, touch, marker,
    update: (next: any) => view.rerender(Object.assign(all, next) && { ...all }),
    runFrames(n: number, startOffsetMs = 2000) {
      let t = performance.now() + startOffsetMs; // 2000 = past the 1 s glide between fixes
      for (let i = 0; i < n; i++) {
        const due = frames.splice(0);
        t += 16;
        due.forEach((f) => f(t));
      }
    },
  };
}

// ------------------------------------------------------------------ the map's own settings
test('the map uses the 2D vector Map ID and Google\'s own place pop-ups are off', () => {
  const gmap = find(render(MapContainer, {}).result(), (e: any) => 'mapId' in e.props);
  assert.equal(gmap.props.mapId, 'ee3c7f039aa26cded2f28d04');
  assert.equal(gmap.props.renderingType, 'VECTOR');
  assert.equal(gmap.props.clickableIcons, false);
});

// ------------------------------------------------------------------ gestures
test('a tap selects nothing', async () => {
  const m = mount();
  m.touch('touchstart', [100, 100]);
  await sleep(120);
  m.touch('touchend');
  m.map.emit('click', { latLng: { lat: () => 1, lng: () => 2 } });
  await sleep(600);
  assert.equal(m.presses.length, 0);
  assert.equal([...m.map.listeners.values()].some((l) => l.type === 'click'), false);
});

test('press and hold reports the place under the finger, once', async () => {
  const m = mount();
  m.touch('touchstart', [110, 220]); // 100, 200 inside the map
  await sleep(700);
  assert.deepEqual(m.presses, [{ lat: 12.98, lng: 77.01 }]);
  m.map.emit('contextmenu', { latLng: { lat: () => 1, lng: () => 2 } }); // Android also reports a context menu
  assert.equal(m.presses.length, 1);
});

test('a slightly shaky finger still counts; a drag does not', async () => {
  const m = mount();
  m.touch('touchstart', [100, 100]);
  m.touch('touchmove', [105, 104]);
  await sleep(700);
  assert.equal(m.presses.length, 1);
  const d = mount();
  d.touch('touchstart', [100, 100]);
  d.touch('touchmove', [160, 100]);
  await sleep(700);
  assert.equal(d.presses.length, 0);
});

test('pinch, map drag and zoom all cancel the hold', async () => {
  const cancellers: ((m: any) => void)[] = [
    (m) => m.touch('touchstart', [100, 100], [200, 200]),
    (m) => m.map.emit('dragstart'),
    (m) => m.map.emit('zoom_changed'),
    (m) => m.touch('touchcancel'),
  ];
  for (const cancel of cancellers) {
    const m = mount();
    m.touch('touchstart', [100, 100]);
    cancel(m);
    await sleep(650);
    assert.equal(m.presses.length, 0, cancel.toString());
  }
});

test('desktop: holding the mouse button or right-clicking drops a pin', async () => {
  const at = { latLng: { lat: () => 12.5, lng: () => 77.25 }, domEvent: { clientX: 5, clientY: 5 } };
  const held = mount();
  held.map.emit('mousedown', at);
  await sleep(700);
  assert.deepEqual(held.presses, [{ lat: 12.5, lng: 77.25 }]);
  const right = mount();
  right.map.emit('contextmenu', at);
  assert.equal(right.presses.length, 1);
});

test('during a trip touching or holding the map does nothing, including a hold already in progress', async () => {
  const m = mount();
  m.touch('touchstart', [100, 100]);
  m.update({ isNavigating: true });
  await sleep(700);
  m.touch('touchstart', [100, 100]);
  await sleep(700);
  m.map.emit('contextmenu', { latLng: { lat: () => 1, lng: () => 2 } });
  m.map.emit('click', { latLng: { lat: () => 1, lng: () => 2 } });
  assert.equal(m.presses.length, 0);
});

test('dragging the map during a trip pauses camera following', () => {
  const m = mount({ isNavigating: true });
  m.map.emit('dragstart');
  assert.equal(m.calls.pan, 1);
});

test('the orange pin is drawn while browsing and hidden during a trip', () => {
  const pin = { lat: 12.9, lng: 77.5 };
  const m = mount({ droppedPin: pin });
  const dropped = () => findAll(m.view.result(), (e: any) => e.props.title === 'Dropped pin');
  assert.equal(dropped().length, 1);
  m.update({ isNavigating: true });
  assert.equal(dropped().length, 0);
});

test('the rider marker is centred on the position, and appears as soon as there is a fix', () => {
  const m = mount();
  const rider = () => find(m.view.result(), (e: any) => e.props.title === 'Rider');
  assert.equal(rider(), null);
  m.update({ gpsPosition: { lat: 12.9, lng: 77.5, heading: 0, speed: 0, timestamp: 1 } });
  assert.deepEqual(rider().props.anchorPoint, ['50%', '50%']);
});

// ------------------------------------------------------------------ camera, compass, route line
const compass = (m: any) => find(m.view.result(), 'CompassButton');
const recenterButton = (m: any) =>
  find(m.view.result(), (e: any) => e.type === 'button' && e.props.title === 'Re-center on my location');
const GPS = { lat: north(100), lng: east(0), heading: 90, speed: 8, accuracy: 5, timestamp: 1 };

function riding() {
  const m = mount({ routePath: PATH, gpsPosition: GPS });
  m.update({ isNavigating: true, displayPosition: { lat: north(100), lng: east(0) }, routePoint: null });
  return m;
}

test('while browsing: no compass on a north-up map, a Re-center button instead', () => {
  const m = mount({ gpsPosition: GPS });
  assert.equal(compass(m), null);
  assert.ok(recenterButton(m));
  m.map.moveCamera({ heading: 40 });
  assert.ok(compass(m), 'the compass appears once the map is turned');
  compass(m).props.onToggle();
  assert.equal(m.map.state.heading, 0);
  assert.equal(m.map.state.tilt, 0);
  assert.equal(compass(m), null);
});

test('the Re-center button centres flat on the rider', () => {
  const m = mount({ gpsPosition: GPS });
  m.map.state.heading = 70;
  recenterButton(m).props.onClick({ stopPropagation() {}, preventDefault() {} });
  assert.deepEqual(m.map.cameras.at(-1), { center: { lat: GPS.lat, lng: GPS.lng }, zoom: 16, tilt: 0, heading: 0 });
});

test('a trip starts heading-up, tilted and zoomed in on the rider', () => {
  const m = riding();
  const first = m.map.cameras.find((c: any) => c.zoom === 18);
  assert.ok(first);
  assert.equal(first.tilt, 45);
  assert.equal(recenterButton(m), null, 'the footer has its own Re-center during a trip');
  m.runFrames(80);
  assert.ok(Math.abs(m.map.cameras.at(-1).heading - 90) < 1);
});

test('the compass switches to flat north-up while following, and back', () => {
  const m = riding();
  m.runFrames(80);
  compass(m).props.onToggle();
  m.update({ displayPosition: { lat: north(130), lng: east(0) } });
  m.runFrames(30);
  let camera = m.map.cameras.at(-1);
  assert.equal(compass(m).props.compassMode, 'north_up');
  assert.equal(camera.heading, 0);
  assert.equal(camera.tilt, 0);
  assert.ok(Math.abs(camera.center.lat - north(130)) < 1e-7, 'still follows the rider');
  compass(m).props.onToggle();
  m.runFrames(30);
  camera = m.map.cameras.at(-1);
  assert.equal(compass(m).props.compassMode, 'heading_up');
  assert.equal(camera.tilt, 45);
});

test('the marker glides between two fixes instead of jumping', () => {
  const m = riding();
  m.runFrames(1);
  m.update({ displayPosition: { lat: north(200), lng: east(0) } });
  m.runFrames(1, 500); // half a second into the 1 s glide
  const mid = m.marker.position.lat;
  assert.ok(mid > north(120) && mid < north(180), `half way, got ${(mid - north(100)) * 111195} m`);
  m.runFrames(1);
  assert.ok(Math.abs(m.marker.position.lat - north(200)) < 1e-9);
});

test('dragging unlinks the camera at once; the Re-center event brings it back', () => {
  const m = riding();
  m.runFrames(20);
  m.map.emit('dragstart');
  assert.equal(m.calls.pan, 1);
  const held = m.map.cameras.length;
  m.update({ displayPosition: { lat: north(300), lng: east(0) } });
  m.runFrames(20);
  assert.equal(m.map.cameras.length, held, 'the camera stays where the rider put it');
  (globalThis as any).window.dispatchEvent(new CustomEvent('recenter-map'));
  assert.equal(m.map.cameras.at(-1).zoom, 18);
});

test('the route line is split exactly at the rider', () => {
  const m = riding();
  m.update({ traveledIndex: 2 });
  const at = { lat: north(250), lng: east(0) };
  m.update({ routePoint: at });
  const shown = lines.filter((l) => l.shown && l.path.length > 1);
  const route = shown.find((l) => l.options.strokeColor === '#1A73E8');
  const travelled = shown.find((l) => l.options.strokeColor === '#94a3b8');
  assert.deepEqual({ ...route.path[0] }, at);
  assert.deepEqual({ ...travelled.path.at(-1) }, at);
});

test('no straight connector line is drawn from a pin to the road', () => {
  const off = { lat: north(50), lng: east(300), name: 'Far from the road' };
  mount({ routePath: PATH, origin: off, destination: off });
  for (const l of lines) {
    assert.equal(l.path.some((p: any) => Math.abs(p.lng - off.lng) < 1e-9 && Math.abs(p.lat - off.lat) < 1e-9), false);
  }
});

test('ending the trip flattens the map; the next trip starts heading-up again', () => {
  const m = riding();
  compass(m).props.onToggle();
  m.update({ isNavigating: false, displayPosition: null });
  assert.equal(m.map.state.tilt, 0);
  assert.equal(m.map.state.heading, 0);
  m.update({ isNavigating: true });
  assert.equal(compass(m).props.compassMode, 'heading_up');
});

test('reported incidents are shown on the map', () => {
  const m = mount({ activeIncidents: [{ id: 'i1', type: 'crash', title: 'Crash', lat: 12.9, lng: 77.5, upvotes: 1 }] });
  assert.equal(findAll(m.view.result(), (e: any) => /Reported on road/.test(e.props.title || '')).length, 1);
});

test('removing the map releases every listener', () => {
  const m = mount();
  assert.ok(m.map.listeners.size > 0);
  mounted.splice(mounted.indexOf(m.view), 1);
  m.view.unmount();
  assert.equal(m.map.listeners.size, 0);
});
