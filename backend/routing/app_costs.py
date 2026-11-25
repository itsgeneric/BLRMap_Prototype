"""
App-only routing refinements for the Dynamic (two-wheeler) route.

The two-wheeler cost model deliberately prefers minor roads. On its own that makes
it leave a main road for a few dozen metres of unnamed alley and come straight back
whenever that saves a handful of cost units ("cut-throughs"). Those alleys are often
tiny lanes, compound or temple-street ways that the public basemap doesn't draw, so
the route looks as if it crosses buildings, and they are poor riding choices anyway.

`lane_entry_cost` adds a one-off cost (in metres-equivalent) each time the route
turns off a main road (tertiary or above) onto a minor way (residential,
unclassified, living_street, service): APP_LANE_ENTRY_PENALTY_M (100) for unnamed
ways and APP_MINOR_ENTRY_PENALTY_M (50) for named ones, since OSM also names some
passages the basemap doesn't draw. A detour off the main road is then taken only if
it saves more than that, which genuine inner-road routes do and cut-throughs don't.

Measured on 60 random 3-10 km trips: short main->minor->main cut-throughs fell from
50 to 20 (Shortest has 26), the minor-road share went from 45% to 40% (Shortest 18%),
and route length was unchanged at the median (worst case +4.9%).

It also adds APP_PASSAGE_ENTRY_PENALTY_M (100) for entering an UNNAMED
living_street or service way from any other road. OSM uses those for gullies,
passages and compound driveways (e.g. a 30 m unnamed living_street joining 5th and
4th Cross Road in Indiranagar that the basemap doesn't show); they are then used to
reach a destination on them, not as shortcuts between streets.

This is applied by the API only (via two_wheeler_astar's optional transition_cost);
research code that calls two_wheeler_astar without it is unchanged.
"""
from core.config import APP_LANE_ENTRY_PENALTY_M, APP_MINOR_ENTRY_PENALTY_M, APP_PASSAGE_ENTRY_PENALTY_M

MAIN_ROAD_CLASSES = {
    "motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
    "secondary", "secondary_link", "tertiary", "tertiary_link",
}
LANE_CLASSES = {"residential", "unclassified", "road", "living_street", "service"}
PASSAGE_CLASSES = {"living_street", "service"}


def _first(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _edge(graph, a, b):
    return min(graph[a][b].values(), key=lambda d: float(d.get("length", 1.0)))


def _is_main(d):
    return _first(d.get("highway")) in MAIN_ROAD_CLASSES


def _is_unnamed_lane(d):
    if _first(d.get("highway")) not in LANE_CLASSES:
        return False
    name = _first(d.get("name")) or _first(d.get("ref"))
    return not name or str(name).lower() in ("none", "nan")


def _is_minor(d):
    return _first(d.get("highway")) in LANE_CLASSES


def lane_entry_cost(graph, penalty_m=APP_LANE_ENTRY_PENALTY_M, named_penalty_m=APP_MINOR_ENTRY_PENALTY_M,
                    passage_penalty_m=APP_PASSAGE_ENTRY_PENALTY_M):
    """
    transition_cost callable for two_wheeler_astar (see module docstring).

    penalty_m:         turning off a main road onto an UNNAMED minor way
    named_penalty_m:   turning off a main road onto a NAMED minor way
    passage_penalty_m: entering an UNNAMED living_street/service way from any other road
    """
    cache = {}

    def edge_kind(a, b):
        key = (a, b)
        if key not in cache:
            d = _edge(graph, a, b)
            passage = _first(d.get("highway")) in PASSAGE_CLASSES and _is_unnamed_lane(d)
            cache[key] = (_is_main(d), _is_minor(d), _is_unnamed_lane(d), passage)
        return cache[key]

    def cost(prev, cur, nxt):
        if nxt not in graph[cur] or cur not in graph[prev]:
            return 0.0
        in_main, _, _, in_passage = edge_kind(prev, cur)
        _, out_minor, out_unnamed, out_passage = edge_kind(cur, nxt)
        extra = 0.0
        if in_main and out_minor:
            extra = penalty_m if out_unnamed else named_penalty_m
        if out_passage and not in_passage:
            extra = max(extra, passage_penalty_m)
        return extra

    return cost
