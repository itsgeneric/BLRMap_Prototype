"""
Turn-by-turn guidance in the style of consumer navigation apps.

Builds the list of spoken/visual instructions for a SnappedRoute:

- Turn angles are measured from the actual road geometry next to each junction
  (not from straight lines between junctions), so curving roads don't read as turns.
- A junction is only announced when the rider has a real decision to make: a turn,
  a fork ("Keep left"), a roundabout, or a change to a different named road.
  Bends with no other road to take are silent.
- Roundabouts become one instruction ("At the roundabout, take the 2nd exit").
- Instructions that fall within a few metres of each other (split carriageways,
  slip roads) are merged into one.
- Start: "Head north on X toward Y". End: "Your destination is on the left".

Every maneuver carries `along_m`, its distance from the start of the drawn route,
so the app can track progress along the route instead of by straight-line distance.

This module only reads the graph; it does not change routing or costs.
"""
import math

from routing.algorithms import haversine_m

BEARING_SAMPLE_M = 20.0     # length of road used to measure the direction at a junction
MERGE_WITHIN_M = 30.0       # instructions closer than this are merged into one
NAME_CHANGE_MIN_M = 150.0   # only announce "Continue onto X" if X lasts at least this long

CARDINALS = ["north", "northeast", "east", "southeast",
             "south", "southwest", "west", "northwest"]


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _bearing(a, b):
    lat1, lat2 = math.radians(a[0]), math.radians(b[0])
    dlng = math.radians(b[1] - a[1])
    y = math.sin(dlng) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlng)
    return math.degrees(math.atan2(y, x)) % 360


def _norm(angle):
    """Normalise to (-180, 180]; positive = clockwise (right)."""
    a = (angle + 180.0) % 360.0 - 180.0
    return 180.0 if a == -180.0 else a


def _length(pts):
    return sum(haversine_m(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:]))


def _point_at(pts, dist):
    """Point `dist` metres along pts (clamped)."""
    run = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = haversine_m(a[0], a[1], b[0], b[1])
        if seg > 0 and run + seg >= dist:
            t = (dist - run) / seg
            return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
        run += seg
    return list(pts[-1])


def _bearing_out(pts):
    """Direction of travel leaving the start of pts."""
    d = min(BEARING_SAMPLE_M, max(_length(pts), 0.5))
    return _bearing(pts[0], _point_at(pts, d))


def _bearing_in(pts):
    """Direction of travel arriving at the end of pts."""
    rev = pts[::-1]
    d = min(BEARING_SAMPLE_M, max(_length(rev), 0.5))
    return _bearing(_point_at(rev, d), pts[-1])


# ---------------------------------------------------------------------------
# OSM tag helpers
# ---------------------------------------------------------------------------

def _first(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _road_name(edge):
    name = _first(edge.get("name"))
    if name and str(name).lower() not in ("none", "nan"):
        return str(name)
    ref = _first(edge.get("ref"))
    if ref and str(ref).lower() not in ("none", "nan"):
        return str(ref)
    return ""


_RANK = {
    "motorway": 7, "trunk": 6, "primary": 5, "secondary": 4, "tertiary": 3,
    "unclassified": 2, "residential": 2, "road": 2, "living_street": 1, "service": 1,
}


def _rank(edge):
    """Importance of a road; *_link roads rank with their parent road."""
    hw = str(_first(edge.get("highway")) or "")
    return _RANK.get(hw.replace("_link", ""), 2)


def _is_roundabout(edge):
    return _first(edge.get("junction")) in ("roundabout", "circular")


def _ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# ---------------------------------------------------------------------------
# Instruction text
# ---------------------------------------------------------------------------

_VERBS = {
    "turn_left": "Turn left", "turn_right": "Turn right",
    "slight_left": "Slight left", "slight_right": "Slight right",
    "sharp_left": "Sharp left", "sharp_right": "Sharp right",
    "keep_left": "Keep left", "keep_right": "Keep right",
    "u_turn": "Make a U-turn", "straight": "Continue straight",
}


def _instruction(m):
    t, name = m["type"], m["road_name"]
    if t == "depart":
        text = f"Head {m['cardinal']}" + (f" on {name}" if name else "")
        if m.get("toward"):
            text += f" toward {m['toward']}"
        return text
    if t == "arrive":
        side = m.get("side")
        return f"Your destination is on the {side}" if side else "You have arrived at your destination"
    if t == "roundabout":
        text = f"At the roundabout, take the {_ordinal(m['exit'])} exit"
        return text + (f" onto {name}" if name else "")
    if t == "continue":
        return f"Continue onto {name}"
    verb = _VERBS.get(t, "Continue")
    if t.startswith("keep"):
        return verb + (f" to stay on {name}" if m.get("same_road") and name else (f" onto {name}" if name else ""))
    if t == "u_turn":
        return verb + (f" onto {name}" if name else "")
    return verb + (f" onto {name}" if name else "")


def _classify(turn):
    a = abs(turn)
    side = "right" if turn > 0 else "left"
    if a >= 155:
        return "u_turn"
    if a >= 115:
        return f"sharp_{side}"
    if a >= 50:
        return f"turn_{side}"
    if a >= 20:
        return f"slight_{side}"
    return "straight"


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_guidance(gm, snapped, destination=None):
    """
    Turn-by-turn maneuvers for a routing.graph_manager.SnappedRoute.

    destination: optional (lat, lng) of the destination pin, used to say which side
    of the road it is on.

    Each maneuver: {type, instruction, road_name, distance_m, along_m, lat, lng,
    exit, side, bearing_before, bearing_after}. distance_m is the distance from this
    maneuver to the next one.
    """
    G = gm.G
    nodes, keys, coords = snapped.nodes, snapped.keys, snapped.coords

    # ── Per-edge geometry and tags ────────────────────────────────────────
    edges = []
    for (a, b), k in zip(zip(nodes, nodes[1:]), keys):
        data = G[a][b][k] if (b in G[a] and k in G[a][b]) else {}
        pts = gm.edge_points(a, b, key=k)
        edges.append({
            "pts": pts, "len": _length(pts), "data": data,
            "name": _road_name(data), "roundabout": _is_roundabout(data),
        })

    # along_m of every node: node i sits at the end of edge i-1
    node_along = [0.0] * len(nodes)
    run = -snapped.start_trim_m
    for i, e in enumerate(edges):
        node_along[i] = max(0.0, run)
        run += e["len"]
    node_along[-1] = max(0.0, run)
    total = max(0.0, sum(e["len"] for e in edges) - snapped.start_trim_m - snapped.end_trim_m)

    def name_run_length(i, name):
        """How far the road called `name` continues from edge i onwards."""
        dist = 0.0
        for e in edges[i:]:
            if e["name"] != name:
                break
            dist += e["len"]
        return dist

    raw = []   # candidate maneuvers at internal nodes
    current_name = edges[0]["name"] if edges else ""   # last named road the rider was on

    i = 1
    while i < len(nodes) - 1:
        node = nodes[i]
        e_in, e_out = edges[i - 1], edges[i]
        b_in, b_out = _bearing_in(e_in["pts"]), _bearing_out(e_out["pts"])
        lat, lng = G.nodes[node]["y"], G.nodes[node]["x"]

        # ── Roundabout: one instruction at the entry, counting exits ───────
        if e_out["roundabout"] and not e_in["roundabout"]:
            j, exits = i + 1, 0
            while j < len(nodes) - 1 and edges[j]["roundabout"]:
                # a node on the ring counts as an exit if a non-ring road leaves it
                nj = nodes[j]
                if any(not _is_roundabout(d) for w in G.successors(nj) for d in G[nj][w].values()
                       if w not in (nodes[j - 1], nodes[j + 1])):
                    exits += 1
                j += 1
            leave = edges[j] if j < len(edges) else edges[-1]
            current_name = leave["name"] or current_name
            raw.append({
                "type": "roundabout", "exit": exits + 1, "road_name": leave["name"],
                "along_m": node_along[i], "lat": lat, "lng": lng,
                "bearing_before": b_in, "bearing_after": _bearing_out(leave["pts"]),
            })
            i = j + 1
            continue
        if e_in["roundabout"]:
            i += 1
            continue

        turn = _norm(b_out - b_in)
        kind = "u_turn" if nodes[i + 1] == nodes[i - 1] else _classify(turn)

        # Other roads the rider could take here (excluding going back)
        # alt_comparable: those at least about as important as the road we take.
        alts, alt_comparable = [], []
        our_rank = _rank(e_out["data"])
        for w in G.successors(node):
            if w in (nodes[i + 1], nodes[i - 1]):
                continue
            k_alt = min(G[node][w], key=lambda kk: float(G[node][w][kk].get("length", 1.0)))
            alt_turn = _norm(_bearing_out(gm.edge_points(node, w, key=k_alt)) - b_in)
            alts.append(alt_turn)
            if _rank(G[node][w][k_alt]) >= our_rank - 1:
                alt_comparable.append(alt_turn)

        name_change = bool(e_out["name"]) and e_out["name"] != current_name \
            and name_run_length(i, e_out["name"]) >= NAME_CHANGE_MIN_M

        announce = False
        same_road = False
        if kind in ("u_turn",) or kind.startswith(("turn_", "sharp_")):
            announce = bool(alts) or abs(turn) >= 70 or name_change
        else:
            straightest = not alts or all(abs(t) >= abs(turn) for t in alts)
            # A minor lane or driveway peeling off a main road is not a fork.
            fork = [t for t in alt_comparable if abs(t - turn) < 40 and abs(t) < 60]
            if fork and straightest:
                # Two similar-looking options: tell the rider which side to keep to
                kind = "keep_left" if all(t > turn for t in fork) else (
                    "keep_right" if all(t < turn for t in fork) else kind)
                announce = kind.startswith("keep")
                same_road = bool(e_out["name"]) and e_out["name"] == current_name
            elif kind.startswith("slight_") and not straightest:
                announce = True               # leaving the main line at an angle
            elif name_change:
                kind, announce = "continue", True

        if e_out["name"]:
            current_name = e_out["name"]
        if announce:
            raw.append({
                "type": kind, "road_name": e_out["name"], "same_road": same_road,
                "along_m": node_along[i], "lat": lat, "lng": lng,
                "bearing_before": b_in, "bearing_after": b_out,
            })
        i += 1

    # ── Merge instructions that sit almost on top of each other ────────────
    merged = []
    for m in raw:
        prev = merged[-1] if merged else None
        if prev and m["along_m"] - prev["along_m"] < MERGE_WITHIN_M \
                and prev["type"] != "roundabout" and m["type"] != "roundabout":
            combined = _norm(m["bearing_after"] - prev["bearing_before"])
            kind = _classify(combined)
            if kind == "straight":
                kind = "continue" if m["road_name"] and m["road_name"] != prev["road_name"] else "straight"
            prev.update({
                "type": kind, "road_name": m["road_name"] or prev["road_name"],
                "bearing_after": m["bearing_after"], "same_road": False,
            })
            if kind == "straight":
                merged.pop()            # the two cancelled out: nothing to announce
            continue
        merged.append(m)

    # ── Depart ────────────────────────────────────────────────────────────
    first_bearing = _bearing_out(coords) if len(coords) > 1 else 0.0
    first_name = edges[0]["name"] if edges else ""
    toward = next((m["road_name"] for m in merged if m["road_name"] and m["road_name"] != first_name), "")
    depart = {
        "type": "depart", "road_name": first_name, "along_m": 0.0,
        "lat": coords[0][0], "lng": coords[0][1],
        "cardinal": CARDINALS[int(((first_bearing + 22.5) % 360) // 45)],
        "toward": toward if merged else "",
        "bearing_before": first_bearing, "bearing_after": first_bearing,
    }

    # ── Arrive (+ side of the road) ───────────────────────────────────────
    last_bearing = _bearing_in(coords) if len(coords) > 1 else 0.0
    side = None
    if destination is not None:
        end = coords[-1]
        if haversine_m(end[0], end[1], destination[0], destination[1]) > 5:
            rel = _norm(_bearing(end, destination) - last_bearing)
            if 20 < abs(rel) < 160:
                side = "right" if rel > 0 else "left"
    arrive = {
        "type": "arrive", "road_name": edges[-1]["name"] if edges else "",
        "along_m": total, "lat": coords[-1][0], "lng": coords[-1][1], "side": side,
        "bearing_before": last_bearing, "bearing_after": last_bearing,
    }

    maneuvers = [depart] + [m for m in merged if 0 < m["along_m"] < total] + [arrive]

    out = []
    for idx, m in enumerate(maneuvers):
        nxt = maneuvers[idx + 1]["along_m"] if idx + 1 < len(maneuvers) else m["along_m"]
        out.append({
            "type": m["type"],
            "instruction": _instruction(m),
            "road_name": m["road_name"],
            "distance_m": round(max(0.0, nxt - m["along_m"]), 1),
            "along_m": round(m["along_m"], 1),
            "lat": float(m["lat"]),
            "lng": float(m["lng"]),
            "exit": m.get("exit"),
            "side": m.get("side"),
            "bearing_before": round(m["bearing_before"], 1),
            "bearing_after": round(m["bearing_after"], 1),
        })
    return out, total
