// lib/routeInfo.ts must reproduce the app's ORIGINAL time formulas exactly. The originals are copied below, unchanged in
// meaning, from components/Navigation/BottomActionBar.tsx and lib/api.ts as they were on this branch before the UI work.
// Run from the repo root:  node --test "tests/frontend/*.test.ts"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import './helpers/register.mjs';

const { singleRouteMinutes, comparisonMinutes, completeRoute } = await import('../../lib/routeInfo.ts');

const originalSingle = (km: number, google: number | null) =>
  google ? Math.round(google) : Math.max(2, Math.round(((km || 0) / 24) * 60));
const originalShortest = (km: number, google: number | null) =>
  google ? Math.round(google) : Math.max(2, Math.round((km / 22) * 60));
const originalDynamic = (km: number) => Math.max(2, Math.round((km / 27.5) * 60));

const distances = [0, 0.1, 0.4, 1, 2.35, 5.5, 8.4, 10.2, 20.9, 47.3];
const traffic = [null, 1, 3.4, 12.5, 41.7, 90];

test('every distance and traffic value gives the same minutes as the original formulas', () => {
  for (const km of distances) {
    for (const google of traffic) {
      const route: any = { status: 'success', distance_km: km, google_base_duration_mins: google };
      assert.equal(singleRouteMinutes(route), originalSingle(km, google), `single ${km} ${google}`);
      for (const dynamicKm of distances) {
        const both = comparisonMinutes(route, { status: 'success', distance_km: dynamicKm, google_base_duration_mins: google });
        assert.equal(both.shortest, originalShortest(km, google), `shortest ${km} ${google}`);
        assert.equal(both.dynamic, originalDynamic(dynamicKm), `dynamic ${dynamicKm}`);
      }
    }
  }
});

test('a missing route never wins the comparison', () => {
  assert.deepEqual(comparisonMinutes(null, null), { shortest: Infinity, dynamic: Infinity });
});

test('completeRoute leaves errors alone, keeps what a server sends, and does not modify its input', () => {
  const error: any = { status: 'error', message: 'x' };
  assert.equal(completeRoute(error), error);
  const path = [[12.9, 77.5], [12.91, 77.5]];
  const maneuvers = [{ type: 'depart' }, { type: 'arrive' }];
  const sent: any = { status: 'success', path, distance_km: 1.1, duration_s: 99, maneuvers };
  const out = completeRoute(sent);
  assert.equal(out.duration_s, 99);
  assert.equal(out.maneuvers, maneuvers);
  const bare: any = { status: 'success', path, distance_km: 1.1 };
  completeRoute(bare);
  assert.deepEqual(Object.keys(bare), ['status', 'path', 'distance_km']);
});
