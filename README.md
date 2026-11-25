# BLRMap — Two-Wheeler Routing for Bengaluru

BLRMap is a routing engine and navigation app for two-wheelers in Bengaluru. It keeps the full
OpenStreetMap road graph locally and runs a custom A* with a two-wheeler cost model (road-class
penalties, turn/roundabout modifiers, congestion-aware rerouting and alternative routes), so the
routing logic is fully editable instead of being outsourced to a map provider.

The repository holds both the **application** and the **research/paper work** built on top of it.
They are kept in separate top-level folders:

| Folder       | What it is                                                                 |
|--------------|----------------------------------------------------------------------------|
| `backend/`   | **Core:** FastAPI routing server, algorithms, config, data access          |
| `frontend/`  | **Core:** Next.js navigation UI + Capacitor Android app                    |
| `tests/`     | Application tests (pytest) for the routing engine                          |
| `research/`  | Experiments, evaluation pipelines, results, field-study data, audits       |
| `paper/`     | Manuscripts (LaTeX), paper planning, literature and drafts                 |
| `docs/`      | Changelog and repository documentation                                     |

## Repository layout

```
BLRMap_Prototype/
├── backend/                      # ── Application: routing server ──
│   ├── api_server.py             # FastAPI entry point (port 8000)
│   ├── core/config.py            # Settings, env vars, data-file paths, cost-model constants
│   ├── routing/                  # algorithms.py (A*, penalties, alternatives), graph_manager.py
│   ├── services/external_api.py  # Google Places / Routes API calls
│   ├── database/                 # MongoDB (motor) client, models, operations
│   ├── data/learning_layer.py    # Route-decision logging (SQLite / MongoDB)
│   ├── scripts/                  # download_graph_full.py, debug_graph.py, debug_places.py
│   ├── router.py                 # Offline CLI route check (no server needed)
│   ├── data_assets/              # Road graph .graphml + .pkl cache   (git-ignored, ~750 MB)
│   ├── route_decisions.db        # Local SQLite learning log          (git-ignored)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                     # ── Application: UI ──
│   ├── app/ components/ hooks/ lib/   # Next.js 15 + React 19 + Google Maps
│   ├── android/                  # Capacitor Android project (webDir = out/)
│   ├── legacy/leaflet_index.html # Original single-file Leaflet test UI
│   ├── package.json, next.config.mjs, tsconfig.json, tailwind.config.js, capacitor.config.ts
│   └── .env.example
│
├── tests/                        # pytest suite for backend routing
│
├── research/                     # ── Research (see research/README.md) ──
│   ├── experiments/              # Benchmark / evaluation / robustness scripts
│   ├── literature_survey/        # Phase 03–13 research log, results & frozen ablation study
│   ├── field_study/              # Strava rides, Exp. E, pilot protocol, route screenshots
│   ├── audits/                   # Stand-alone verification reports
│   └── handover_package/         # Self-contained research handover (SHA-256 manifest)
│
├── paper/                        # ── Papers ──
│   ├── paper1/  latex/  blueprint/  literature/  manuscript_drafts/
│   └── paper2/  latex/
│
├── docs/   CHANGES.md, PATH_MIGRATION.md
└── .agents/skills/               # Research-protocol & evidence-integrity agent skills
```

## Setup

### Prerequisites
- Python 3.11+ (developed on 3.13)
- Node.js 20+
- The Bengaluru road graph in `backend/data_assets/` (see below)

### 1. Backend

```bash
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env      # then fill in your keys
cd backend
python api_server.py                       # add --reload for auto-reload
```

The server listens on `http://127.0.0.1:8000`. On first start it loads
`data_assets/bengaluru_roads_extended.graphml`, filters it, and writes the processed graph to
`data_assets/bengaluru_graph.pkl`. Later starts load the `.pkl` in a few seconds.

**Road graph data.** The graph files are too large for git. Put them in `backend/data_assets/`,
or regenerate the GraphML:

```bash
cd backend/data_assets
python ../scripts/download_graph_full.py   # writes bengaluru_roads_extended.graphml here
```

You can also point at a graph elsewhere with `GRAPH_FILE_PATH=/path/to/file.graphml`.

**Environment variables** (`backend/.env`, or a `.env` at the repo root; both are found):

| Variable                  | Purpose                                                    |
|---------------------------|------------------------------------------------------------|
| `GOOGLE_PLACES_API_KEY`   | Place search                                               |
| `GOOGLE_MAPS_API_KEY`     | Google Routes API (live traffic); falls back to Places key |
| `MONGODB_URI`             | Optional. Journey/decision storage; disabled when unset    |
| `GRAPH_FILE_PATH`, `DECISIONS_DB`, `MAX_SNAPPING_DISTANCE_M` | Optional overrides       |

Quick offline check without the server: `cd backend && python router.py`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local                 # NEXT_PUBLIC_GOOGLE_MAPS_KEY, NEXT_PUBLIC_STADIA_KEY
npm run dev                                # http://localhost:3000
```

Routes are drawn on Google's own road geometry using the **Roads API**, so enable "Roads API"
for the Google Maps key (otherwise the OSM geometry is drawn and the console shows one warning;
set `NEXT_PUBLIC_SNAP_ROUTES=0` to turn it off).

The frontend calls the backend at `http://127.0.0.1:8000` by default. To use the app on a
phone, set `NEXT_PUBLIC_API_BASE=http://<your-PC-LAN-IP>:8000` in `frontend/.env.local`.

**Testing navigation on a desktop:** open `http://localhost:3000/?simulate=40` and start
navigating from "My Location": a simulated rider follows the route at ~40 km/h, so you can watch
the camera, turn banner and voice prompts. Add `&detour=20` to make the rider leave the route
after 20 s and trigger a reroute.

**Android (Capacitor):**

```bash
cd frontend
npm run build          # static export to frontend/out/
npx cap sync android
npx cap open android
```

`frontend/legacy/leaflet_index.html` is the original Leaflet test page. Open it directly in a
browser while the backend is running.

## API

| Method | Endpoint                             | Description                                        |
|--------|--------------------------------------|----------------------------------------------------|
| GET    | `/`                                  | Health check                                       |
| GET    | `/search?q=`                         | Place search                                       |
| GET    | `/route?from_lat&from_lng&to_lat&to_lng`         | Shortest path (A*) with maneuvers      |
| GET    | `/dynamic-route?from_lat&from_lng&to_lat&to_lng` | Traffic-aware two-wheeler A* route     |
| POST   | `/journeys/{id}/start`               | Log journey start                                  |
| POST   | `/journeys/{id}/complete`            | Log journey completion                             |
| POST   | `/journeys/{id}/reroute`             | Log an off-route reroute event                     |

Interactive docs: `http://127.0.0.1:8000/docs`.

## Tests

From the repository root:

```bash
python -m pytest tests research/experiments/robustness_testing/test_synthetic_graphs.py
```

`tests/` holds the routing regression and mathematical-validation tests. `test_synthetic_graphs.py`
runs the robustness suite on synthetic graphs. Most tests load the real road graph, so
`backend/data_assets/` must be populated.

## Research and papers

See [`research/README.md`](research/README.md) for how the experiments are organised and run.

> **Frozen data.** `research/literature_survey/13_ablation_study/` holds the officially frozen
> Phase 13.4 ablation dataset. Its files are read-only and stay at their original path.
> Do not edit, move or re-run them without explicit authorisation
> (see `.agents/skills/evidence-integrity-audit/SKILL.md`).

LaTeX sources for the papers are in `paper/paper1/latex/` and `paper/paper2/latex/` and are
Overleaf-ready.

If you are looking for a file by its old location, see
[`docs/PATH_MIGRATION.md`](docs/PATH_MIGRATION.md).
