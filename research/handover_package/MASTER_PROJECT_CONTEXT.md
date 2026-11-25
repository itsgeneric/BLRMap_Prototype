# Master Project Context

## 1. Research project
The user is developing a Bengaluru-focused two-wheeler-aware routing prototype (BLRMap Prototype). The system uses OpenStreetMap road-network data and a custom routing engine. The broader research programme is split into two papers with strict separation of scope.

## 2. The two-paper strategy

### Paper 1
**Title:** *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*

Focus: algorithmic formulation and controlled evaluation of state-expanded A* search, turn penalties, road-class impedance, heuristic correctness, and computational trade-offs.

Paper 1 is already written, frozen, formatted in IEEE two-column style, and compiled to a six-page PDF. Do not reopen or modify frozen content unless the user explicitly authorises it or a material error is found.

### Paper 2
**Title:** *Design and Empirical Evaluation of a Two-Wheeler-Aware Routing Framework for Urban Road Networks*

Focus: the broader routing framework, alternative-route generation, route diversity, and external comparison with commercial navigation apps (Google Maps and Waze), plus the user's real-world route observations.

Paper 2 must not simply duplicate Paper 1. Keep the algorithmic analysis and A–D controlled ablations in Paper 1. Experiment E and alternative-route work belong to Paper 2. The commercial-platform and Strava field comparison is a proposed expansion of Paper 2.

## 3. Project stack and routing context
Known components from project audit:
- FastAPI backend (`api_server.py`).
- Next.js frontend; `lib/api.ts` and `ModeSelector.tsx` were inspected in the route audit.
- `routing/algorithms.py` contains `two_wheeler_astar`.
- `routing/graph_manager.py` resolves route nodes to coordinate geometry.
- `core/config.py` contains road penalty configuration and minimum penalty floor.
- `services/external_api.py` calls Google Routes API for dynamic traffic data.
- MongoDB Atlas database `blrnav`, collection `journeys`, stored route snapshots.
- Bengaluru OSM graph artifacts include `bengaluru_graph.pkl` and `bengaluru_roads_extended.graphml`.

Do not assume the current local project code matches the historical runtime. Verify exact files/commits if code-level claims are required.

## 4. Historical two-wheeler routing configuration from route audit
Reported configuration:
- State-expanded A*: state represents previous/current node (edge-state representation).
- Road-class multipliers:
  - motorway 4.0
  - trunk / trunk_link 3.0 / 2.5
  - primary / primary_link 2.2 / 2.0
  - secondary / secondary_link 1.5 / 1.4
  - tertiary / tertiary_link 1.15 / 1.10
  - residential 1.0
  - living_street 0.95
  - unclassified 1.0
  - service 0.90
  - road 1.10
- Bridge/flyover override: 0.80 for qualifying main-road bridge segments.
- Roundabout multiplier: 0.95.
- Turn penalties: 25 m for deflection >=60 degrees; 8 m for 30 to <60 degrees; 0 below 30 degrees.
- Historical heuristic changed from `h = d / 0.8` (1.25d, aggressive/overestimating) to `h = 0.8d` (admissible lower-bound formulation). The audit reports working-tree modification at 4 Nov 2026 13:44:20 IST. The two versions were reported to yield the same 183-node/381-coordinate/11.230 km route on the tested static graph. Treat exact historical runtime version as partially established, not fully proven.

## 5. Research integrity rules
- Never invent experimental results, metrics, app outputs, or source evidence.
- Clearly distinguish actual journey time from navigation-app ETA.
- Do not claim real-world travel-time savings based only on route distance, turn count, or search runtime.
- Route geometry and GPS adherence do not by themselves prove what an application displayed at a particular historical moment.
- Preserve the user's firsthand account as a working premise when explicitly requested.
- Do not repeatedly reopen the CMH provenance investigation; the user has explicitly said time is limited and does not want more Antigravity testing.
- Do not spend Antigravity tokens on additional route provenance tests unless explicitly authorised.
- Work one phase at a time; use explicit approval gates for significant changes.
- Never mix Paper 1 and Paper 2 evidence.
