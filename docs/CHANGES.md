## 2026-11-23 — Routes drawn on Google's road geometry

- Reported: Dynamic routes run along the side of the road (e.g. Robertson Road and Wheeler
  Road, Fraser Town), while Shortest routes sit on the road.
- Cause: drawing, not road choice. Routes are computed on OpenStreetMap, and on many inner
  roads OSM's centre-line is 5-15 m from where Google's basemap draws the same road. Shortest
  mostly uses major roads, which OSM maps accurately (L K Legacy -> CAIR: Millers Road,
  St John's Church Road, Swamy Vivekananda Road); Dynamic deliberately uses inner roads
  (Pottery Lane, Robertson Road, Charles Campbell Road), so it shows the offset far more.
  An audit of 120 random trips found both modes ride beside a bigger road for ~6% of their
  length (mostly real service roads along ORR/trunk roads), so this is not a road-choice bug.
- Fix (frontend): `lib/snapToRoads.ts` redraws each route returned by the backend on Google's
  roads with the Roads API (snapToRoads, 100 points per request, ~2 requests per 5 km).
  Google's line is checked span by span (between consecutive route points): it must stay
  within 60 m of our route, keep moving forward along it, and not be more than 30% longer;
  otherwise our own geometry is kept for that span only. Off when the Roads API refuses the
  key (one console warning) or with NEXT_PUBLIC_SNAP_ROUTES=0.
- Follow-up (report: CAIR -> L K Legacy, Fraser Town, line between Maiganda Deva Mudaliar Rd
  and 4th Cross Rd): the Roads API was working, but the first version judged whole
  100-point requests (~3 km) with a 25 m limit. Near Mosque Road Google's snap made a U-turn
  into Mosque Road and put one point 30 m back up the street, so the whole 3 km piece fell
  back to OSM geometry. With per-span checks, that trip is now drawn on Google's roads for
  324/326 and 343/349 spans (Shortest/Dynamic); the rest are spans where Google has no
  road within 60 m or snaps into a side street.
- The Maps key constant moved from GoogleMapContainer.tsx to `lib/mapsKey.ts` (shared).

## 2026-11-23 — Dynamic route: no shortcuts through unnamed passages

- Reported: CAIR -> L K Legacy (Dynamic) cut through a block in Indiranagar where Google's
  map shows 1st A Main Road ending at 4th Cross Road. The route used a 30 m unnamed
  `living_street` (OSM way 995154351) between 5th and 4th Cross Road. The forward trip
  didn't use it, which is why only one direction showed the problem.
- The earlier rule only charged for leaving a MAIN road; this one went residential ->
  passage -> residential. New rule: entering an unnamed living_street/service way from any
  other road costs 100 m-equivalent (APP_PASSAGE_ENTRY_PENALTY_M). Such passages are still
  used to reach a destination on them, not as shortcuts.
- CAIR -> L K Legacy now stays on 5th Cross Road (11.63 -> 11.75 km); L K Legacy -> CAIR is
  unchanged. On 60 trips: mid-route passages 19 -> 11 (Shortest 7); route length change at
  most +0.6%.

## 2026-11-23 — Dynamic route no longer cuts through lanes the map doesn't show

- Cause: the two-wheeler cost model rates minor roads far cheaper than main roads
  (e.g. primary x2.2, residential x1.0, living_street x0.95), so Dynamic left a main road
  for a few dozen metres of OSM alley/passage whenever that saved a few cost units.
  Many of those ways aren't drawn on Google's basemap, so the route appeared to cross
  buildings (e.g. "Roberston Cross Road" in Fraser Town; living_street lanes off Pottery Lane).
- Fix (app only): `routing/app_costs.py` adds a one-off cost for turning off a main road
  onto a minor road: 100 m-equivalent for unnamed ways (APP_LANE_ENTRY_PENALTY_M),
  50 m for named ones (APP_MINOR_ENTRY_PENALTY_M). Used by /dynamic-route through a new
  optional `transition_cost` argument of `two_wheeler_astar` (default None = unchanged).
- Measured on 60 trips: short main->minor->main cut-throughs 50 -> 20 (Shortest: 26),
  minor-road share 45% -> 40% (Shortest: 18%), median route length unchanged (max +4.9%).
- Not changed: on divided roads OSM maps each direction separately, so at high zoom the
  route sits on one carriageway of Google's wide road (same in Shortest and Dynamic).

## 2026-11-23 — Turn-by-turn navigation rebuilt (navigation-app style)

Backend
- New `backend/routing/guidance.py`: instructions from real road geometry; bends with no
  alternative are silent; forks -> "Keep left/right" (minor lanes ignored); roundabouts ->
  "take the 2nd exit"; split-junction instructions merged; "Head north on X toward Y";
  "Your destination is on the left/right". Each maneuver carries `along_m`.
  (~1.7 instructions/km, down from 2.7; none closer than 20 m, was 180 per 40 trips.)
- `/route` and `/dynamic-route` accept optional `heading` so reroutes continue forward.
- Route starts/ends avoid dead-end stubs that force a U-turn.

Frontend
- Heading-up, tilted (vector) camera that glides between GPS fixes, rider arrow in the lower
  third, zooms in for turns and out at speed; arrow snapped to the route.
- Route behind the rider disappears; white turn arrow painted on the road at the next turn.
- Green turn banner with "Then" strip and grey "Rerouting..." state; bottom trip sheet with
  time left, distance, arrival time, exit and overview; speed bubble; Re-centre after panning.
- Progress tracked along the route; voice prompts "In 300 metres, turn left onto X",
  "Turn right, then turn left", "Continue on X for 3 kilometres", arrival side; voice on by default.
- Faster accuracy-aware rerouting; screen kept awake while navigating; arrival card.
- Fixed: GPS watcher restarted on every compass change.
- `NEXT_PUBLIC_API_BASE` sets the backend address (needed to use the app on a phone).
- Testing: open `http://localhost:3000/?simulate=40` (km/h) to ride the route automatically;
  add `&detour=20` to leave the route after 20 s and exercise rerouting.

## 2026-11-23 — Route geometry fixes (routes crossing buildings / leaving the road)

- Pins now snap to the nearest *road* (edge) instead of the nearest junction (node).
  The drawn route starts and ends exactly on that road, trimmed so it never rides to
  a junction and U-turns back (`GraphManager.snap_to_road`, `build_snapped_route`).
- Frontend no longer draws a solid straight line from each pin to the route; the
  pin-to-road gap is shown as a short dotted access line.
- Excluded roads closed to the public from the routable graph: `access=military`,
  `customers`, `bus`, `psv`, `permit`, `delivery`, `agricultural`, `forestry`,
  `emergency`, and `service=driveway|parking_aisle|drive-through|emergency_access`
  (5,982 edges). The graph cache rebuilds itself on next start.
- `/dynamic-route` now draws the same parallel edge the two-wheeler cost model chose.
- The pre-change graph cache, used by the frozen Phase 13 experiments, is preserved as
  `backend/data_assets/bengaluru_graph_phase13_snapshot.pkl`
  (sha256 4a7a191fca1baccbbc11f4009b2e1ef7c09b313df87cc08519fdc4c05512e659).

Fix two-wheeler routing: live traffic selection, real road geometry, diverse candidates

Backend (api_server.py):

- Add Google Routes API call to score candidates by live TWO_WHEELER
  traffic duration instead of static cost only (fallback to static
  cost if API unavailable)
- Fix routes drawing straight lines across buildings by using actual
  edge geometry from OSM instead of node-to-node lines
- Keep only the largest strongly-connected graph component so routes
  no longer get stuck/incomplete heading south
- Fix segment-length slider appearing broken: split candidates were
  mathematically guaranteed to never beat the direct route on cost,
  so the same route was always selected regardless of slider value
- Generate split candidates via perpendicular offset points (parallel
  inner roads) instead of points that snapped back onto the direct
  corridor, producing genuinely different route options
- Dedupe identical candidates before scoring to avoid wasted API calls

Frontend (index.html):

- Show live traffic minutes in the top stat bar instead of the
  static "score" number (falls back to score if traffic unavailable)
- Show live traffic time on each candidate row alongside score and
  distance, so it's visible when a worse-scored route was picked
  for being faster in real traffic
- Highlight the actually-selected candidate in the list (green tint
  - "picked (live traffic)" label) instead of leaving the reason
    for selection invisible
