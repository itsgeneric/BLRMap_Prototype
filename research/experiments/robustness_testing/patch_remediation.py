"""
Patch script to apply Phase 12.2 controlled defect remediation:
1. graph_manager.py: validate_coordinate
2. algorithms.py: identical OD guard in build_split_route_candidates
3. api_server.py: validate_coordinate usage in /route and /dynamic-route
"""

import os
import re

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend"))

# ------------------------------------------------------------------------------
# 1. Patch routing/graph_manager.py
# ------------------------------------------------------------------------------
gm_path = os.path.join(base_dir, "routing", "graph_manager.py")
with open(gm_path, "r", encoding="utf-8") as f:
    gm_content = f.read()

# Add import if not present
if "DEFAULT_MAX_SNAPPING_DISTANCE_M" not in gm_content:
    old_imp = "from core.config import GRAPH_FILE_PATH, SURFACE_QUALITY_FILE, INNER_ROAD_TYPES"
    new_imp = "import math\nfrom core.config import GRAPH_FILE_PATH, SURFACE_QUALITY_FILE, INNER_ROAD_TYPES, DEFAULT_MAX_SNAPPING_DISTANCE_M"
    gm_content = gm_content.replace(old_imp, new_imp, 1)

# Add validate_coordinate method if not present
if "def validate_coordinate" not in gm_content:
    target_marker = 'return self.surface_penalties.get(key_fwd, self.surface_penalties.get(key_rev, 1.0))'
    validate_code = '''return self.surface_penalties.get(key_fwd, self.surface_penalties.get(key_rev, 1.0))

    def validate_coordinate(
        self,
        lat: float,
        lng: float,
        max_distance_m: float = DEFAULT_MAX_SNAPPING_DISTANCE_M
    ) -> int:
        """
        Validate that input coordinates lie within the supported road network coverage.

        Performs:
        1. Type and value checking (numeric, non-NaN, non-inf, valid lat/lng range).
        2. Bounding box check against self.bounds with safety margin.
        3. Road network coverage check: ensures distance to nearest graph node
           does not exceed max_distance_m.

        Returns:
            int: The nearest valid graph node ID.
        Raises:
            TypeError: If coordinates are non-numeric.
            ValueError: If coordinates are invalid, out of bounds, or too far from road network.
        """
        if not (isinstance(lat, (int, float)) and isinstance(lng, (int, float))):
            raise TypeError(f"Coordinates must be numeric floats. Received lat={type(lat).__name__}, lng={type(lng).__name__}")
        if math.isnan(lat) or math.isnan(lng) or math.isinf(lat) or math.isinf(lng):
            raise ValueError(f"Invalid coordinate values: lat={lat}, lng={lng}")
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
            raise ValueError(f"Coordinates out of geographic range: lat={lat}, lng={lng}")

        if self.G is None or len(self.G) == 0:
            raise RuntimeError("Road network graph is not loaded. Call load_graph() first.")

        # 1. Bounding-box verification with buffer (~0.05 deg ≈ 5.5 km)
        buffer = 0.05
        b = self.bounds
        if b:
            if not (b["min_lat"] - buffer <= lat <= b["max_lat"] + buffer and
                    b["min_lng"] - buffer <= lng <= b["max_lng"] + buffer):
                raise ValueError(
                    f"Coordinates ({lat:.4f}, {lng:.4f}) lie outside the Bengaluru coverage area "
                    f"[lat: {b['min_lat']:.2f}..{b['max_lat']:.2f}, lng: {b['min_lng']:.2f}..{b['max_lng']:.2f}]."
                )

        # 2. Road network proximity validation
        nearest_node = ox.nearest_nodes(self.G, lng, lat)
        node_data = self.G.nodes[nearest_node]
        dist_m = haversine_m(lat, lng, node_data["y"], node_data["x"])

        if dist_m > max_distance_m:
            raise ValueError(
                f"Coordinate ({lat:.4f}, {lng:.4f}) is {dist_m:.1f}m from nearest road node, "
                f"exceeding the maximum allowed snapping threshold of {max_distance_m:.1f}m."
            )

        return nearest_node'''
    gm_content = gm_content.replace(target_marker, validate_code, 1)

with open(gm_path, "w", encoding="utf-8") as f:
    f.write(gm_content)
print("Updated routing/graph_manager.py successfully.")

# ------------------------------------------------------------------------------
# 2. Patch routing/algorithms.py
# ------------------------------------------------------------------------------
algo_path = os.path.join(base_dir, "routing", "algorithms.py")
with open(algo_path, "r", encoding="utf-8") as f:
    algo_content = f.read()

# Add DEFAULT_MAX_SNAPPING_DISTANCE_M to imports in algorithms.py if not present
if "DEFAULT_MAX_SNAPPING_DISTANCE_M" not in algo_content:
    old_imp = "from core.config import (\n    TWO_WHEELER_ROAD_PENALTIES,"
    new_imp = "from core.config import (\n    DEFAULT_MAX_SNAPPING_DISTANCE_M,\n    TWO_WHEELER_ROAD_PENALTIES,"
    algo_content = algo_content.replace(old_imp, new_imp, 1)

# In build_split_route_candidates:
# 1. Update signature to include max_snapping_distance
old_sig = 'def build_split_route_candidates(\n    graph,\n    graph_mgr,\n    from_lat,\n    from_lng,\n    to_lat,\n    to_lng,\n    split_fractions=DEFAULT_ROUTE_SPLIT_FRACTIONS,\n    penalties=None,\n    max_overlap=0.70,\n    max_detour=DETOUR_TOLERANCE,\n    max_alternatives=3,\n    undirected=False,\n    return_diagnostics=False\n):'
new_sig = 'def build_split_route_candidates(\n    graph,\n    graph_mgr,\n    from_lat,\n    from_lng,\n    to_lat,\n    to_lng,\n    split_fractions=DEFAULT_ROUTE_SPLIT_FRACTIONS,\n    penalties=None,\n    max_overlap=0.70,\n    max_detour=DETOUR_TOLERANCE,\n    max_alternatives=3,\n    undirected=False,\n    return_diagnostics=False,\n    max_snapping_distance=DEFAULT_MAX_SNAPPING_DISTANCE_M\n):'
if old_sig in algo_content:
    algo_content = algo_content.replace(old_sig, new_sig, 1)

# 2. Add validation and identical OD guard right after direct_start / direct_end
old_snapping = '''    direct_start = ox.nearest_nodes(
        graph,
        from_lng,
        from_lat
    )

    direct_end = ox.nearest_nodes(
        graph,
        to_lng,
        to_lat
    )'''

new_snapping = '''    if graph_mgr is not None and hasattr(graph_mgr, "validate_coordinate"):
        direct_start = graph_mgr.validate_coordinate(from_lat, from_lng, max_snapping_distance)
        direct_end = graph_mgr.validate_coordinate(to_lat, to_lng, max_snapping_distance)
    else:
        direct_start = ox.nearest_nodes(graph, from_lng, from_lat)
        direct_end = ox.nearest_nodes(graph, to_lng, to_lat)

    # --------------------------------------------------------
    # Identical OD Guard: If start and end snap to identical node,
    # return direct zero-distance route immediately with 0 alternatives.
    # --------------------------------------------------------
    if direct_start == direct_end:
        primary_entry = {
            "strategy": "direct",
            "nodes": [direct_start],
            "cost": 0.0,
            "distance": 0.0,
            "detour_ratio": 1.0,
            "overlap_ratio": 1.0,
            "jaccard_similarity": 1.0,
        }
        if return_diagnostics:
            return {
                "candidates": [primary_entry],
                "direct_route": primary_entry,
                "diverse_alternatives": [],
                "generated_count": 0,
                "rejected_candidates": [],
                "surviving_count": 0,
            }
        return [primary_entry]'''

if old_snapping in algo_content:
    algo_content = algo_content.replace(old_snapping, new_snapping, 1)

with open(algo_path, "w", encoding="utf-8") as f:
    f.write(algo_content)
print("Updated routing/algorithms.py successfully.")

# ------------------------------------------------------------------------------
# 3. Patch api_server.py
# ------------------------------------------------------------------------------
api_path = os.path.join(base_dir, "api_server.py")
with open(api_path, "r", encoding="utf-8") as f:
    api_content = f.read()

# Update /route endpoint
old_route_snap = '''@app.get("/route")
async def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
    end   = ox.nearest_nodes(graph_manager.G, to_lng,  to_lat)'''

new_route_snap = '''@app.get("/route")
async def get_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    try:
        start = graph_manager.validate_coordinate(from_lat, from_lng)
        end   = graph_manager.validate_coordinate(to_lat, to_lng)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))'''

if old_route_snap in api_content:
    api_content = api_content.replace(old_route_snap, new_route_snap, 1)

# Update /dynamic-route endpoint
old_dyn_snap = '''@app.get("/dynamic-route")
async def dynamic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
    end   = ox.nearest_nodes(graph_manager.G, to_lng,  to_lat)'''

new_dyn_snap = '''@app.get("/dynamic-route")
async def dynamic_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    try:
        start = graph_manager.validate_coordinate(from_lat, from_lng)
        end   = graph_manager.validate_coordinate(to_lat, to_lng)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))'''

if old_dyn_snap in api_content:
    api_content = api_content.replace(old_dyn_snap, new_dyn_snap, 1)

with open(api_path, "w", encoding="utf-8") as f:
    f.write(api_content)
print("Updated api_server.py successfully.")
