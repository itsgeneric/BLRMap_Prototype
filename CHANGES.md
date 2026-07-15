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
