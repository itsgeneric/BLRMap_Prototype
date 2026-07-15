# BLR Map Prototype

This project experiments with Bengaluru two-wheeler routing by keeping the full road graph locally and controlling the routing logic in `api_server.py`.

The goal is not to copy Google Maps behavior. The goal is to build a route engine that can be tuned for Bengaluru traffic patterns, where the best motorcycle route is often not the route that looks best for cars.

## Core Idea

The backend loads a Bengaluru road graph from OpenStreetMap and then runs custom graph search on top of it.

The current implementation uses three routing ideas:

1. Plain shortest path on the full graph.
2. Inner-road biased routing for local roads.
3. Two-wheeler smart routing that scores routes with road-type penalties and tries route splitting for longer trips.

The important part is that the graph is kept broad, so the algorithm can decide which roads to prefer instead of being locked into one narrow map view.

## Routing Logic

### 1. Full graph routing

The file `api_server.py` loads `bengaluru_roads_full.graphml` and uses A* search with road length as the base metric.

This gives a baseline shortest route and is useful for comparison.

### 2. Inner-road routing

The inner-road mode builds a subgraph from road types like:

- residential
- living_street
- unclassified
- service
- tertiary
- tertiary_link

It then routes through that reduced graph first and falls back to the full graph if a segment cannot be found.

This is useful for testing the idea that two-wheelers in Bengaluru can benefit from smaller roads instead of staying on large main roads.

### 3. Two-wheeler smart routing

The new `two-wheeler-route` endpoint adds a custom cost model on top of A*.

Instead of using only road length, each edge gets a weighted cost based on road type:

- main roads get higher penalties
- local roads get lower penalties
- service and residential roads are favored more strongly
- roundabouts get a small adjustment

This means the route optimizer can prefer shorter, more local paths even if the raw distance is slightly longer.

### 4. Route splitting

For longer trips, the backend does not only try one direct A* route.

It also generates split candidates and compares them against the direct path.

The current version uses a segment-length control from the frontend. That control decides how aggressively the trip should be split into subroutes.

The idea is:

- long congested trip from A to B
- split into smaller pieces
- route each piece with the local cost model
- stitch the pieces back together
- compare the result against the direct path

This is the main experimental logic behind the project.

## API Modes

The backend exposes the following routing endpoints:

- `/route` - shortest path on the full graph
- `/inner-route` - inner-road biased routing with waypoint-based segmentation
- `/traffic-route` - Google Directions comparison route, currently using `mode=driving`
- `/two-wheeler-route` - custom route evaluator with road penalties and split candidates

The frontend in `index.html` lets you switch between these modes.

## Frontend Behavior

`index.html` is a single-page Leaflet UI that:

- searches places through the backend
- lets you click start and end points on the map
- sends the selected mode to the API
- draws the returned route on the map
- shows candidate route scores for the smart two-wheeler mode

The two-wheeler mode also exposes tuning controls for:

- main road penalty
- inner-road preference
- service-road preference
- segment length used for route splitting

## Current Run Steps


0. pip install geopandas shapely --break-system-packages
1. Install dependencies:

   ```bash
   pip install osmnx networkx fastapi uvicorn geopandas httpx python-dotenv

   ```

2. Make sure `bengaluru_roads_full.graphml` exists.

   If you need to regenerate it, run:

   ```bash
   python download_graph_full.py
   ```

3. Add your Google API key in a `.env` file:

   ```env
   GOOGLE_PLACES_API_KEY=your_key_here
   ```

4. Start the backend:

   ```bash
   python api_server.py
   ```

5. Open `index.html` in the browser.

## What This Project Is Testing

The main question is whether Bengaluru two-wheeler routing can be improved by combining:

- local road preference
- reduced penalty on main-road bias
- route splitting for long congested trips
- comparison against Google Directions for calibration only

The implementation is intentionally experimental. The important part is that the routing logic is now editable locally instead of being fully outsourced to a map provider.

## Notes

- `api_server.py` is the main algorithm file.
- `router.py` and the debug scripts are legacy helpers.
- The current two-wheeler logic is still a work in progress and will likely need tuning on real Bengaluru origin-destination pairs.






