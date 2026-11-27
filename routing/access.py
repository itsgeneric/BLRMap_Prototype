"""
"Access-only" roads: service lanes, driveways, and roads tagged for destination traffic only.

Deleting them (the old behaviour) stopped routes short of places that are inside a campus, a layout or a compound. Using
them freely would send riders through other people's property. So they are kept in the graph and marked `access_only`,
and a trip may use one only if it belongs to the cluster of such roads that its OWN start or destination is on: the first
or last stretch of a trip, never a cut-through. Roads tagged private / no are not in the graph at all.
"""
import math
from collections import deque

from core.config import ACCESS_ONLY_COST_MULTIPLIER, ACCESS_ONLY_REACH_M


def _near(G, node, lat, lng, reach_m):
    n = G.nodes[node]
    dy = (n['y'] - lat) * 110574.0
    dx = (n['x'] - lng) * 111320.0 * math.cos(math.radians(lat))
    return math.hypot(dx, dy) <= reach_m


def allowed_access_edges(G, snaps, reach_m=ACCESS_ONLY_REACH_M):
    """
    The access-only edges this trip may use, as a set of (u, v): every access-only road connected (through other
    access-only roads, in either direction) to an access-only road that a start or destination pin is snapped onto,
    no farther than `reach_m` from that point.
    """
    allowed = set()
    for snap in snaps:
        if not snap.edge:
            continue
        u, v, key = snap.edge
        if not G[u][v][key].get('access_only'):
            continue
        lat, lng = snap.point
        seen = {u, v}
        queue = deque((u, v))
        while queue:
            node = queue.popleft()
            for a, b in [(node, x) for x in G.successors(node)] + [(x, node) for x in G.predecessors(node)]:
                if (a, b) in allowed or not any(d.get('access_only') for d in G[a][b].values()):
                    continue
                other = b if a == node else a
                if other not in seen:
                    if not _near(G, other, lat, lng, reach_m):
                        continue
                    seen.add(other)
                    queue.append(other)
                allowed.add((a, b))
    return allowed


def gate_access(weight, allowed):
    """
    Wraps an edge weight function. Public roads cost what they did before. An access-only road costs
    ACCESS_ONLY_COST_MULTIPLIER times more when this trip may use it, and infinity otherwise. Costs only ever go UP,
    so the A* lower bound stays valid.
    """
    def gated(u, v, edge_data):
        parallel = [edge_data] if 'length' in edge_data else list(edge_data.values())
        if not any(d.get('access_only') for d in parallel):
            return weight(u, v, edge_data)
        public = {k: d for k, d in enumerate(parallel) if not d.get('access_only')}
        if public:
            return weight(u, v, public)
        if (u, v) not in allowed:
            return float('inf')
        return weight(u, v, edge_data) * ACCESS_ONLY_COST_MULTIPLIER
    return gated
