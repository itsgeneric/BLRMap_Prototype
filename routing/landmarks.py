"""
Landmark (ALT) lower bounds for the Dynamic search: a much tighter, still PROVABLY admissible A* heuristic.

Why: the plain heuristic is  multiplier * straight-line distance  and the multiplier must be a lower bound for EVERY road
class, so one fast class (motorway, 0.31) drags it to ~0.3 per metre while real routes cost ~1.0+. The search then explores
a large part of the city (up to ~6 s for a 20 km trip).

How: pick K landmark junctions spread over the city. Once, run Dijkstra from each landmark L over the BASE cost graph
(length x road-class x roundabout x flyover factor) and the same over the reversed graph:
      dF[L, x] = cost(L -> x)        dR[L, x] = cost(x -> L)
For any node n and target t the triangle inequality gives
      cost(n -> t) >= dF[L, t] - dF[L, n]      and      cost(n -> t) >= dR[L, n] - dR[L, t]
so  h(n) = max over landmarks of those terms  never overestimates, and it is consistent.

Why it stays valid at query time: the real edge cost is  base x (congestion >= 1) x (incident >= 1) x (surface >= 1)
x (blacklist >= 1) + (alley penalty >= 0) + (turn penalty >= 0). Every extra term only RAISES the cost, so base distances are
lower bounds of the real ones. valid_for() checks the conditions that can break this (a different cost table, a surface or
blacklist factor below 1) and the caller then falls back to the plain heuristic.

Needs scipy (already installed: osmnx depends on it). Memory: 2 * K * N float64 (about 60 MB for 16 landmarks, 231k nodes).
"""
import time

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from routing.algorithms import two_wheeler_edge_cost

EARTH_R = 6371000.0


def _haversine_vec(lat, lng, lat0, lng0):
    p1, p2 = np.radians(lat), np.radians(lat0)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lng0 - lng) / 2) ** 2
    return 2 * EARTH_R * np.arcsin(np.sqrt(a))


class Landmarks:
    def __init__(self, node_index, lat, lng, d_from, d_to, landmark_nodes, penalties, build_seconds):
        self.node_index = node_index        # node id -> row/column number
        self.lat, self.lng = lat, lng
        self.d_from = d_from                # (K, N) cost(L -> x)
        self.d_to = d_to                    # (K, N) cost(x -> L)
        self.landmark_nodes = landmark_nodes
        self.penalties = dict(penalties)
        self.build_seconds = build_seconds

    # ------------------------------------------------------------------ build
    @classmethod
    def build(cls, G, penalties, n_landmarks=16, progress=None):
        t0 = time.perf_counter()
        node_ids = list(G.nodes)
        n = len(node_ids)
        node_index = {node: i for i, node in enumerate(node_ids)}
        lat = np.array([G.nodes[x]['y'] for x in node_ids], dtype=float)
        lng = np.array([G.nodes[x]['x'] for x in node_ids], dtype=float)

        # base cost of every edge: no congestion / incidents / surface / blacklist / alley penalty (see module docstring)
        us, vs, cs = [], [], []
        for u, v, d in G.edges(data=True):
            us.append(node_index[u])
            vs.append(node_index[v])
            cs.append(two_wheeler_edge_cost(d, None, penalties, None, None))
        us, vs = np.array(us, dtype=np.int64), np.array(vs, dtype=np.int64)
        cs = np.maximum(np.array(cs, dtype=float), 1e-6)

        # parallel edges: keep the cheapest (csr would otherwise SUM duplicates)
        key = us * n + vs
        order = np.argsort(key, kind='stable')
        key, us, vs, cs = key[order], us[order], vs[order], cs[order]
        starts = np.flatnonzero(np.concatenate(([True], key[1:] != key[:-1])))
        cs = np.minimum.reduceat(cs, starts)
        us, vs = us[starts], vs[starts]
        matrix = csr_matrix((cs, (us, vs)), shape=(n, n))

        # landmarks: farthest-point selection on a flat projection, starting from the point farthest from the centre
        x = (lng - lng.mean()) * 111320.0 * np.cos(np.radians(lat.mean()))
        y = (lat - lat.mean()) * 110574.0
        chosen = [int(np.argmax(x * x + y * y))]
        nearest = np.hypot(x - x[chosen[0]], y - y[chosen[0]])
        while len(chosen) < min(n_landmarks, n):
            nxt = int(np.argmax(nearest))
            chosen.append(nxt)
            nearest = np.minimum(nearest, np.hypot(x - x[nxt], y - y[nxt]))

        if progress:
            progress("forward")
        d_from = dijkstra(matrix, directed=True, indices=chosen)
        if progress:
            progress("reverse")
        d_to = dijkstra(matrix.T.tocsr(), directed=True, indices=chosen)
        return cls(node_index, lat, lng, d_from, d_to, [node_ids[i] for i in chosen], penalties,
                   time.perf_counter() - t0)

    # ------------------------------------------------------------------ validity
    def valid_for(self, penalties, graph_mgr, blacklist):
        """True only when the base distances are guaranteed lower bounds of the real edge costs."""
        if dict(penalties) != self.penalties:
            return False
        if graph_mgr is not None and any(v < 1.0 for v in graph_mgr.surface_penalties.values()):
            return False
        return blacklist.min_penalty() >= 1.0

    # ------------------------------------------------------------------ heuristic
    def heuristic(self, targets, multiplier, start_nodes, use=6):
        """
        h(node) for one query: min over targets of (max(landmark bound, multiplier * haversine) + extra cost at that target).
        Uses the `use` landmarks that look best from the start (any subset of landmarks is still admissible).
        """
        idx = self.node_index
        t_idx = [(idx[t], float(extra), t) for t, extra in targets.items()]
        s_idx = [idx[s] for s in start_nodes]

        def bounds_at(sel, j):
            # inf - inf is nan (a landmark that cannot reach/see either node tells us nothing): treat it as "no information"
            # (-inf) so it never poisons the maximum. A genuine +inf (target unreachable from n) is kept: it is correct.
            with np.errstate(invalid='ignore'):
                forward = self.d_from[sel, j][:, None] - self.d_from[sel]
                backward = self.d_to[sel] - self.d_to[sel, j][:, None]
            forward[np.isnan(forward)] = -np.inf
            backward[np.isnan(backward)] = -np.inf
            return np.maximum(forward, backward)

        everyone = np.arange(len(self.landmark_nodes))
        score = np.zeros(len(everyone))
        for j, _, _ in t_idx:
            score = np.maximum(score, np.max([bounds_at(everyone, j)[:, s] for s in s_idx], axis=0))
        sel = everyone[np.argsort(-score)[:use]]

        best = np.full(len(self.lat), np.inf)
        for j, extra, t in t_idx:
            alt = np.maximum(bounds_at(sel, j).max(axis=0), 0.0)
            straight = multiplier * _haversine_vec(self.lat, self.lng, self.lat[j], self.lng[j])
            best = np.minimum(best, np.maximum(alt, straight) + extra)
        table = best.tolist()
        return lambda node: table[idx[node]]
