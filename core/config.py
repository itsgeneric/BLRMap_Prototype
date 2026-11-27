import os
from dotenv import load_dotenv

load_dotenv()

# This dynamically finds the BLRMAP_Prototype root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
ROUTES_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or GOOGLE_KEY
ROADS_KEY = os.getenv("GOOGLE_ROADS_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY") or GOOGLE_KEY
ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
ROADS_SNAP_API_URL = "https://roads.googleapis.com/v1/snapToRoads"

MONGODB_URI = os.getenv("MONGODB_URI")  # mongodb+srv://... from Atlas

# Folder holding the graph assets (graphml / pkl / geojson).
# Set DATA_DIR in .env; relative paths are resolved against BASE_DIR.
DATA_DIR = os.path.join(BASE_DIR, os.getenv("DATA_DIR", "Data Assets"))

GRAPH_FILE_PATH = os.getenv("GRAPH_FILE_PATH", os.path.join(DATA_DIR, "bengaluru_roads_extended.graphml"))
# The compiled map has its OWN file name, so a map built by another branch is never loaded by mistake. It is rebuilt
# automatically from the GraphML source when missing or built with older rules (GRAPH_CLEANUP_VERSION).
GRAPH_PKL_PATH = os.getenv("GRAPH_PKL_PATH", os.path.join(DATA_DIR, "bengaluru_graph.smart.pkl"))
EXCLUDE_POLYS_FILE = os.getenv("EXCLUDE_POLYS_FILE", os.path.join(DATA_DIR, "bengaluru_exclude_polys.geojson"))

# These remain in your root folder
SURFACE_QUALITY_FILE = os.getenv("SURFACE_QUALITY_FILE", os.path.join(BASE_DIR, "bad_surface_segments.json"))
# Only roads blocked by hand (POST /blacklist/add). A new file name: bans made automatically by the old road check,
# which blocked real inner roads, are not carried over.
EDGE_BLACKLIST_FILE = os.getenv("EDGE_BLACKLIST_FILE", os.path.join(BASE_DIR, "edge_blacklist_manual.json"))
DECISIONS_DB = os.getenv("DECISIONS_DB", os.path.join(BASE_DIR, "route_decisions.db"))

SNAP_DEVIATION_THRESHOLD_M = float(os.getenv("SNAP_DEVIATION_THRESHOLD_M", "65.0"))

# The displayed route line is our own graph geometry (the road A* actually chose). Re-snapping it through the
# Google Roads API is OFF by default: tests/diag_route_geometry.py showed that with sparse point sampling the
# snapped line can jump onto a different road (up to ~150 m off, 6.6% longer on one route). Set
# SNAP_FINAL_POLYLINE=true in .env to turn the old behaviour back on.
SNAP_FINAL_POLYLINE = os.getenv("SNAP_FINAL_POLYLINE", "false").strip().lower() in ("1", "true", "yes", "on")

# A pin is attached to the nearest road edge within this distance (metres). Farther than this there is no road to start
# from or arrive at, and the request fails with a clear message instead of drawing a line through buildings.
MAX_SNAP_DISTANCE_M = float(os.getenv("MAX_SNAP_DISTANCE_M", "500.0"))

# Google Roads check: every route's smaller roads are compared with Google's road network, and a road Google does not have
# is blocked and the route planned again (services/external_api.py). Uses paid Roads API calls, and the "Roads API" must be
# enabled for the key. ENABLE_ROAD_VERIFY=false turns it off.
ENABLE_ROAD_VERIFY = os.getenv("ENABLE_ROAD_VERIFY", "true").strip().lower() in ("1", "true", "yes", "on")
ROAD_VERIFY_MAX_DEVIATION_M = float(os.getenv("ROAD_VERIFY_MAX_DEVIATION_M", "25"))  # farther than this: not Google's road
ROAD_VERIFY_SPACING_M = 40.0        # test points along each road (at least 3 per road)
ROAD_VERIFY_MAX_REQUESTS = 15       # per check; 100 points each
ROAD_VERIFY_MAX_ROUNDS = 5          # check, block, plan again ... at most this many times
# Shadow mode: only LOG what the check would block. OFF by default.
VERIFY_SHADOW_MODE = os.getenv("VERIFY_SHADOW_MODE", "false").strip().lower() in ("1", "true", "yes", "on")
BLACKLIST_PENALTY_MULTIPLIER = float(os.getenv("BLACKLIST_PENALTY_MULTIPLIER", "10000.0"))

# Anti-Rat-Running: extra cost (metres) when a main-road node leads onto a minor residential alley.
# OFF by default (0). It was added on 2026-11-15 to stop zig-zag "looping" routes, but together with flattened road
# weights it pushed routes onto arterials and made them longer. Turn penalties (below) now handle zig-zagging properly.
# Set MAJOR_TO_MINOR_TRANSITION_PENALTY_M=45 in .env to bring it back.
MAJOR_TO_MINOR_TRANSITION_PENALTY_M = float(os.getenv("MAJOR_TO_MINOR_TRANSITION_PENALTY_M", "0.0"))

# Turn penalties (metres of extra cost). The search tracks (previous node, current node) so a turn costs what it should:
# this is what keeps routes from zig-zagging through grids of small roads. Applied to /route and /dynamic-route.
TURN_PENALTY_SHARP_M = 25.0          # direction change of TURN_THRESHOLD_SHARP_DEG or more
TURN_PENALTY_MODERATE_M = 8.0        # direction change of TURN_THRESHOLD_MODERATE_DEG or more
TURN_THRESHOLD_SHARP_DEG = 60.0
TURN_THRESHOLD_MODERATE_DEG = 30.0

# Flyover exception: a bridge/flyover on a main road costs FLYOVER_MAIN_ROAD_MULTIPLIER per metre, cheaper than ANY ground road.
# OFF by default: it makes the elevated expressways (Electronic City Flyover, Silk Board ...) the cheapest roads on the map, so
# trips such as AGS Layout -> Electronic City ran 13 km on highways and were ~2 km LONGER than the inner-road route. For a
# two-wheeler router that prefers inner roads that is the wrong default. FLYOVER_EXCEPTION=true in .env turns it back on.
FLYOVER_EXCEPTION_ENABLED = os.getenv("FLYOVER_EXCEPTION", "false").strip().lower() in ("1", "true", "yes", "on")
FLYOVER_MAIN_ROAD_MULTIPLIER = 0.8

# Road access. Three groups (routing/graph_manager.py):
#   removed      private / no, and military, emergency-only and permit-only roads: the public may not drive there.
#   access-only  service roads and destination / customers / delivery / permissive: usable only as the first or last stretch,
#                to reach a place inside a campus, layout or compound (routing/access.py). Never as a cut-through.
#   public       everything else. access=permissive roads (often estate and campus roads, open at the owner's will) were
#                briefly public: that added 2,449 segments that routes cut through and riders found not to be real roads.
RESTRICTED_ACCESS_VALUES = {'private', 'no', 'military', 'emergency', 'permit'}
ACCESS_ONLY_VALUES = {'destination', 'customers', 'delivery', 'permissive'}
ACCESS_ONLY_COST_MULTIPLIER = 1.5     # so a public road is taken when both reach the pin
ACCESS_ONLY_REACH_M = 1500.0          # how far from the pin its cluster of access-only roads may extend
# A junction offered as an alternative start/end for an off-road pin: every metre it is farther from the pin than the
# nearest road costs this many metres. Walking "through the buildings" is not free, so the route goes to the near road.
OFF_ROAD_COST_PER_M = 3.0
# A compiled graph PKL stores the graph AFTER cleanup. When this value differs from the one stored in the PKL, the PKL is
# rebuilt from the GraphML source on the next start (a few minutes, once). Bump it whenever the cleanup rules change.
GRAPH_CLEANUP_VERSION = "6:permissive-is-access-only"

# ------------------------------------------------------------------ smart two-wheeler planning (routing/smart.py)
# A Dynamic route is never longer than max(direct x MAX_DETOUR_RATIO, direct + DETOUR_SLACK_M).
MAX_DETOUR_RATIO = float(os.getenv("MAX_DETOUR_RATIO", "1.15"))
DETOUR_SLACK_M = float(os.getenv("DETOUR_SLACK_M", "300"))
PREFERENCE_LEVELS = (1.0, 0.6, 0.3, 0.0)   # inner-road preference, strongest first
# Cost of a metre of jammed road. It was 25, which made a 300 m queue "worth" avoiding by 7 km. A two-wheeler filters
# through traffic: at 2.0 it goes round only when the other way is less than twice the length of the jam.
JAM_COST_MULTIPLIER = float(os.getenv("JAM_COST_MULTIPLIER", "2.0"))

# Post-process that collapses tiny box loops in a route. OFF by default: turn penalties prevent those loops at the source.
COLLAPSE_MICRO_LOOPS = os.getenv("COLLAPSE_MICRO_LOOPS", "false").strip().lower() in ("1", "true", "yes", "on")

MINOR_ALLEY_TYPES = {
    'residential', 'living_street', 'unclassified', 'service'
}

MAJOR_HIGHWAY_TYPES = {
    'motorway', 'motorway_link', 'trunk', 'trunk_link',
    'primary', 'primary_link', 'secondary', 'secondary_link'
}

INNER_ROAD_TYPES = {
    'residential', 'living_street', 'unclassified', 'service',
    'tertiary', 'tertiary_link'
}

MAIN_ROAD_TYPES = {
    'motorway', 'motorway_link', 'trunk', 'trunk_link',
    'primary', 'primary_link', 'secondary', 'secondary_link'
}

INNER_ROAD_BIASED_TYPES = {
    'tertiary', 'tertiary_link', 'residential', 'living_street',
    'unclassified', 'service', 'road'
}

# ---------------------------------------------------------------------------------------------------------------
# Road-class cost per metre. Two models, chosen by DYNAMIC_COST_MODEL (default "hierarchy" = the "was working well" weights):
#
#   "time"       cost = length / speed. Every class gets a free-flow SPEED, so a longer route on faster roads beats a shorter
#                one on slower roads, and distance still counts. The speeds were FITTED, not guessed: tests/graph_qa_benchmark.py
#                (40 Bengaluru trips, 2026-11-23) solved "Google's no-traffic duration = sum(length_on_class / speed)" by
#                non-negative least squares (median error 7%, p90 17.6%). Classes with too little data share a tier speed:
#                  motorway 66.1, trunk 28.2, primary 20.0 / secondary 19.6 / tertiary 21.8 -> pooled arterial 20.6 (their
#                  differences are inside the fit error), residential 16.3. *_link takes its parent class (as in the fit).
#                  living_street, unclassified, service, road were not separable in the data: ASSUMED = residential speed.
#                The multiplier is REF_SPEED / speed, so an arterial = 1.0 and the cost stays in "metres at arterial speed";
#                turn penalties (metres) and the flyover factor keep their meaning. Traffic by hour is the next step.
#   "hierarchy"  the paper's impedance table (arterials expensive, inner roads cheap): avoids main roads regardless of
#                how fast or empty they are. Kept for comparison and as a fallback.
# ---------------------------------------------------------------------------------------------------------------
DYNAMIC_COST_MODEL = os.getenv("DYNAMIC_COST_MODEL", "hierarchy").strip().lower()
if DYNAMIC_COST_MODEL not in ("time", "hierarchy"):
    raise ValueError(f"DYNAMIC_COST_MODEL must be 'time' or 'hierarchy', got {DYNAMIC_COST_MODEL!r}")

FREE_FLOW_SPEED_KMH = {
    'motorway': 66.1, 'motorway_link': 66.1,
    'trunk': 28.2, 'trunk_link': 28.2,
    'primary': 20.6, 'primary_link': 20.6,
    'secondary': 20.6, 'secondary_link': 20.6,
    'tertiary': 20.6, 'tertiary_link': 20.6,
    'residential': 16.3, 'living_street': 16.3, 'unclassified': 16.3, 'service': 16.3, 'road': 16.3,
}
REFERENCE_SPEED_KMH = 20.6

TWO_WHEELER_ROAD_PENALTIES_TIME = {
    road_class: round(REFERENCE_SPEED_KMH / speed, 4) for road_class, speed in FREE_FLOW_SPEED_KMH.items()
}

# The paper's impedance hierarchy (restored 2026-11-23 from "was working well"; it had been flattened to primary 1.0 /
# residential 1.10 on 2026-11-15, which favoured arterials and lengthened routes).
TWO_WHEELER_ROAD_PENALTIES_HIERARCHY = {
    'motorway': 4.0,
    'motorway_link': 3.0,
    'trunk': 3.0,
    'trunk_link': 2.5,
    'primary': 2.2,
    'primary_link': 2.0,
    'secondary': 1.5,
    'secondary_link': 1.4,
    'tertiary': 1.15,
    'tertiary_link': 1.1,
    'residential': 1.0,
    'living_street': 0.95,
    'unclassified': 1.0,
    'service': 0.9,
    'road': 1.1,
}

TWO_WHEELER_ROAD_PENALTIES = (
    TWO_WHEELER_ROAD_PENALTIES_TIME if DYNAMIC_COST_MODEL == "time" else TWO_WHEELER_ROAD_PENALTIES_HIERARCHY
)

FILTER_DISCOUNT_PER_JUNCTION = 0.985
FILTER_DISCOUNT_FLOOR = 0.85
MIN_LANES_FOR_FILTERING = 2
DEFAULT_ROUTE_SPLIT_FRACTIONS = (0.33, 0.5, 0.67)
DETOUR_TOLERANCE = 1.20