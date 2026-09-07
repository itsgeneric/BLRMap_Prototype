import os
from dotenv import load_dotenv

load_dotenv()

# This dynamically finds the BLRMAP_Prototype root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
ROUTES_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or GOOGLE_KEY
ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

MONGODB_URI = os.getenv("MONGODB_URI")  # mongodb+srv://... from Atlas

# Correctly mapped to your Data Assets folder
GRAPH_FILE_PATH = os.getenv("GRAPH_FILE_PATH", os.path.join(BASE_DIR, "Data Assets", "bengaluru_roads_extended.graphml"))
EXCLUDE_POLYS_FILE = os.getenv("EXCLUDE_POLYS_FILE", os.path.join(BASE_DIR, "Data Assets", "bengaluru_exclude_polys.geojson"))

# These remain in your root folder
SURFACE_QUALITY_FILE = os.getenv("SURFACE_QUALITY_FILE", os.path.join(BASE_DIR, "bad_surface_segments.json"))
DECISIONS_DB = os.getenv("DECISIONS_DB", os.path.join(BASE_DIR, "route_decisions.db"))

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