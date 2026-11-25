import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# This dynamically finds the backend/ folder (BLRMap_Prototype/backend) without any hardcoded username/path.
BASE_DIR = Path(__file__).resolve().parents[1]


def _resolve_existing_file(filename: str, *candidate_dirs: Path) -> str:
    """Return the first existing file in the project tree, with a safe fallback."""
    candidates = [
        BASE_DIR / filename,
        *[directory / filename for directory in candidate_dirs],
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(BASE_DIR / filename)


GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
ROUTES_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or GOOGLE_KEY
ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

MONGODB_URI = os.getenv("MONGODB_URI")  # mongodb+srv://... from Atlas

# Resolve the GraphML file from the project layout instead of assuming a single fixed directory.
GRAPH_FILE_PATH = os.getenv(
    "GRAPH_FILE_PATH",
    _resolve_existing_file(
        "bengaluru_roads_extended.graphml",
        BASE_DIR / "data_assets",
        BASE_DIR / "Data Assets",
        BASE_DIR / "Data Assets" / "Data Assets",
    ),
)
EXCLUDE_POLYS_FILE = os.getenv("EXCLUDE_POLYS_FILE", str(BASE_DIR / "data_assets" / "bengaluru_exclude_polys.geojson"))

# These live directly in the backend/ folder
SURFACE_QUALITY_FILE = os.getenv("SURFACE_QUALITY_FILE", str(BASE_DIR / "bad_surface_segments.json"))
DECISIONS_DB = os.getenv("DECISIONS_DB", str(BASE_DIR / "route_decisions.db"))

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

TWO_WHEELER_ROAD_PENALTIES = {
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

FILTER_DISCOUNT_PER_JUNCTION = 0.985
FILTER_DISCOUNT_FLOOR = 0.85
MIN_LANES_FOR_FILTERING = 2
DEFAULT_ROUTE_SPLIT_FRACTIONS = (0.33, 0.5, 0.67)
DETOUR_TOLERANCE = 1.20

DEFAULT_MAX_SNAPPING_DISTANCE_M = float(os.getenv("MAX_SNAPPING_DISTANCE_M", 1500.0))

# App-only (Dynamic route): one-off cost, in metres-equivalent, for turning off a main
# road onto an UNNAMED minor lane. Stops "cut-throughs" through tiny alleys that save a
# few metres; set to 0 to disable. Not used by the research experiments.
APP_LANE_ENTRY_PENALTY_M = float(os.getenv("APP_LANE_ENTRY_PENALTY_M", 100.0))
# Same, for turning off a main road onto a NAMED minor road (named lanes in OSM can
# also be passages the basemap doesn't show). Set to 0 to disable.
APP_MINOR_ENTRY_PENALTY_M = float(os.getenv("APP_MINOR_ENTRY_PENALTY_M", 50.0))
# Same, for entering an UNNAMED living_street/service way (passages, gullies, compound
# driveways) from any other road. Set to 0 to disable.
APP_PASSAGE_ENTRY_PENALTY_M = float(os.getenv("APP_PASSAGE_ENTRY_PENALTY_M", 100.0))
