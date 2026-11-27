"""
Road-network quality checks (used by tests/graph_qa_benchmark.py and the /qa/* endpoints; NOT used by routing).

Question answered: "Can our graph follow a reference route (e.g. Google's two-wheeler route), in the right
direction?"  It does NOT compare which route we would choose, so it does not penalise us for being faster or
smarter than the reference -- it only reveals roads the reference uses that our graph lacks (missing) or only
allows the other way (wrong_direction, e.g. a one-way street).

How it works
  1. RoadIndex.from_graph(): every directed edge is sampled every ~12 m along its real shape. Each sample keeps
     its position (local metres), its direction of travel and its edge. A KD-tree makes lookups fast.
  2. match_polyline(): the reference polyline is resampled every 10 m. For each sample we look for graph samples
     within 20 m:
        - one whose direction is within 45 deg of the reference's direction  -> covered
        - only ones pointing the opposite way (>= 135 deg)                    -> wrong_direction
        - none, or only crossing roads                                        -> missing
     Stretches shorter than 30 m are forgiven (junction/roundabout noise).

The reference polyline is only held in memory for the duration of a call; nothing is stored.
"""
import math

import numpy as np
from sklearn.neighbors import KDTree

SAMPLE_SPACING_M = 10.0      # spacing of reference samples
INDEX_SPACING_M = 12.0       # spacing of graph samples
MATCH_RADIUS_M = 20.0        # OSM vs Google centre-lines differ by ~3 m (p95 ~7 m); divided roads sit up to ~20 m apart
ALIGNED_DEG = 45.0           # graph direction within this of the reference direction = same direction of travel
OPPOSITE_DEG = 135.0         # graph direction at least this far from the reference = opposite direction
MIN_GAP_M = 30.0             # shorter uncovered stretches are tolerated

COVERED, WRONG_DIRECTION, MISSING = 0, 1, 2
KIND_NAMES = {COVERED: 'covered', WRONG_DIRECTION: 'wrong_direction', MISSING: 'missing'}


def edge_class_group(highway):
    """Road class used for grouping: first value of a list, lower-cased, '_link' folded into its parent class."""
    hw = highway[0] if isinstance(highway, list) and highway else highway
    hw = str(hw or 'unclassified').lower()
    return hw[:-5] if hw.endswith('_link') else hw


def angular_difference(a, b):
    """Smallest angle between two bearings in degrees (0..180); works on arrays."""
    return np.abs(((a - b + 540.0) % 360.0) - 180.0)


class LocalProjection:
    """Flat local projection (metres east/north of a centre point); accurate to well under 1 m across a city."""

    def __init__(self, lat0, lng0):
        self.lat0 = float(lat0)
        self.lng0 = float(lng0)
        self.kx = 111320.0 * math.cos(math.radians(self.lat0))
        self.ky = 110574.0

    def forward(self, lat, lng):
        return (np.asarray(lng, dtype=float) - self.lng0) * self.kx, (np.asarray(lat, dtype=float) - self.lat0) * self.ky

    def inverse(self, x, y):
        return self.lat0 + np.asarray(y, dtype=float) / self.ky, self.lng0 + np.asarray(x, dtype=float) / self.kx


def fill_short_gaps(status, spacing_m=SAMPLE_SPACING_M, min_gap_m=MIN_GAP_M):
    """Marks uncovered runs shorter than min_gap_m as covered (noise at junctions, roundabouts, route ends)."""
    status = status.copy()
    n = len(status)
    i = 0
    while i < n:
        if status[i] == COVERED:
            i += 1
            continue
        j = i
        while j + 1 < n and status[j + 1] != COVERED:
            j += 1
        if (j - i + 1) * spacing_m < min_gap_m:
            status[i:j + 1] = COVERED
        i = j + 1
    return status


class RoadIndex:
    def __init__(self, tree, points, bearings, edge_ids, edges, edge_class_idx, class_names, proj):
        self.tree = tree
        self.points = points                # (N, 2) local metres
        self.bearings = bearings            # (N,) compass degrees of the edge's direction of travel at that sample
        self.edge_ids = edge_ids            # (N,) index into `edges`
        self.edges = edges                  # [(u, v, key)]
        self.edge_class_idx = edge_class_idx  # (E,) index into class_names
        self.class_names = class_names
        self.proj = proj

    @property
    def size(self):
        return int(len(self.points))

    @classmethod
    def from_graph(cls, G, spacing_m=INDEX_SPACING_M, progress=None):
        node_ids = list(G.nodes)
        lats = np.array([G.nodes[n]['y'] for n in node_ids], dtype=float)
        lngs = np.array([G.nodes[n]['x'] for n in node_ids], dtype=float)
        proj = LocalProjection(lats.mean(), lngs.mean())
        nx_, ny_ = proj.forward(lats, lngs)
        node_xy = {n: (float(x), float(y)) for n, x, y in zip(node_ids, nx_, ny_)}

        xs_parts, ys_parts, br_parts, id_parts = [], [], [], []
        edges, class_idx = [], []
        class_names, class_lookup = [], {}

        for count, (u, v, k, d) in enumerate(G.edges(keys=True, data=True)):
            if progress and count and count % 100000 == 0:
                progress(count)
            ux, uy = node_xy[u]
            vx, vy = node_xy[v]
            geom = d.get('geometry')
            if geom is not None and hasattr(geom, 'xy'):
                gx, gy = geom.xy
                ex, ey = proj.forward(np.asarray(gy), np.asarray(gx))
                # Some builders store the same shape for both directions: orient it u -> v.
                if (ex[-1] - ux) ** 2 + (ey[-1] - uy) ** 2 < (ex[0] - ux) ** 2 + (ey[0] - uy) ** 2:
                    ex, ey = ex[::-1], ey[::-1]
            else:
                ex, ey = np.array([ux, vx]), np.array([uy, vy])

            dx, dy = np.diff(ex), np.diff(ey)
            seg_len = np.hypot(dx, dy)
            keep = seg_len > 1e-6
            if not keep.any():
                continue
            x0, y0, dx, dy, seg_len = ex[:-1][keep], ey[:-1][keep], dx[keep], dy[keep], seg_len[keep]
            bearing = (np.degrees(np.arctan2(dx, dy)) + 360.0) % 360.0

            per_seg = np.maximum(1, np.ceil(seg_len / spacing_m)).astype(np.int64)
            total = int(per_seg.sum())
            seg_idx = np.repeat(np.arange(len(per_seg)), per_seg)
            first = np.cumsum(per_seg) - per_seg
            t = (np.arange(total) - np.repeat(first, per_seg)) / np.repeat(per_seg, per_seg)
            px = np.append(x0[seg_idx] + t * dx[seg_idx], x0[-1] + dx[-1])
            py = np.append(y0[seg_idx] + t * dy[seg_idx], y0[-1] + dy[-1])
            br = np.append(bearing[seg_idx], bearing[-1])

            cname = edge_class_group(d.get('highway'))
            if cname not in class_lookup:
                class_lookup[cname] = len(class_names)
                class_names.append(cname)
            eid = len(edges)
            edges.append((u, v, k))
            class_idx.append(class_lookup[cname])
            xs_parts.append(px)
            ys_parts.append(py)
            br_parts.append(br)
            id_parts.append(np.full(len(px), eid, dtype=np.int32))

        if not xs_parts:
            raise ValueError("Graph has no usable edges")
        points = np.column_stack([np.concatenate(xs_parts), np.concatenate(ys_parts)])
        bearings = np.concatenate(br_parts).astype(np.float32)
        edge_ids = np.concatenate(id_parts)
        tree = KDTree(points, leaf_size=40)
        return cls(tree, points, bearings, edge_ids, edges, np.array(class_idx, dtype=np.int32), class_names, proj)

    def match_polyline(self, coords, spacing_m=SAMPLE_SPACING_M, radius_m=MATCH_RADIUS_M,
                       min_gap_m=MIN_GAP_M):
        """
        coords: [[lat, lng], ...] reference route. Returns a report dict:
          total_m, covered_m, missing_m, wrong_direction_m, covered_pct
          segments: [{kind, length_m, path:[[lat,lng],...]}]    consecutive runs of the same kind (for drawing)
          gaps:     [{kind, length_m, lat, lng}]                uncovered runs, longest first
          class_metres: {road_class: metres}                    covered length per graph road class
        """
        arr = np.asarray(coords, dtype=float)
        if arr.ndim != 2 or arr.shape[0] < 2:
            raise ValueError("Need at least two [lat, lng] points")
        x, y = self.proj.forward(arr[:, 0], arr[:, 1])
        cum = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
        total = float(cum[-1])
        if total < 1.0:
            raise ValueError("Reference route has no length")

        pos = np.arange(0.0, total, spacing_m)
        if pos[-1] < total - 1e-6:
            pos = np.append(pos, total)
        sx, sy = np.interp(pos, cum, x), np.interp(pos, cum, y)
        n = len(pos)
        idx = np.arange(n)
        prev_i, next_i = np.maximum(idx - 2, 0), np.minimum(idx + 2, n - 1)
        heading = (np.degrees(np.arctan2(sx[next_i] - sx[prev_i], sy[next_i] - sy[prev_i])) + 360.0) % 360.0

        neighbours = self.tree.query_radius(np.column_stack([sx, sy]), r=radius_m)
        status = np.full(n, MISSING, dtype=np.int8)
        sample_edge = np.full(n, -1, dtype=np.int64)
        for i, cand in enumerate(neighbours):
            if len(cand) == 0:
                continue
            diff = angular_difference(self.bearings[cand], heading[i])
            aligned = diff <= ALIGNED_DEG
            if aligned.any():
                c = cand[aligned]
                d2 = (self.points[c, 0] - sx[i]) ** 2 + (self.points[c, 1] - sy[i]) ** 2
                sample_edge[i] = self.edge_ids[c[int(np.argmin(d2))]]
                status[i] = COVERED
            elif (diff >= OPPOSITE_DEG).any():
                status[i] = WRONG_DIRECTION

        status = fill_short_gaps(status, spacing_m, min_gap_m)
        step = np.append(np.diff(pos), 0.0)         # length each sample stands for

        covered_m = float(step[status == COVERED].sum())
        missing_m = float(step[status == MISSING].sum())
        wrong_m = float(step[status == WRONG_DIRECTION].sum())

        class_metres = {}
        for i in np.nonzero(status == COVERED)[0]:
            eid = sample_edge[i]
            name = self.class_names[self.edge_class_idx[eid]] if eid >= 0 else 'unmatched'
            class_metres[name] = class_metres.get(name, 0.0) + float(step[i])

        lat_all, lng_all = self.proj.inverse(sx, sy)
        segments, gaps = [], []
        i = 0
        while i < n:
            j = i
            while j + 1 < n and status[j + 1] == status[i]:
                j += 1
            last = min(j + 1, n - 1)                # include the next sample so drawn runs touch
            length = float(step[i:j + 1].sum())
            kind = KIND_NAMES[int(status[i])]
            segments.append({
                'kind': kind,
                'length_m': round(length, 1),
                'path': [[float(lat_all[m]), float(lng_all[m])] for m in range(i, last + 1)],
            })
            if status[i] != COVERED:
                mid = (i + j) // 2
                gaps.append({'kind': kind, 'length_m': round(length, 1),
                             'lat': float(lat_all[mid]), 'lng': float(lng_all[mid])})
            i = j + 1

        gaps.sort(key=lambda g: -g['length_m'])
        return {
            'total_m': round(total, 1),
            'covered_m': round(covered_m, 1),
            'missing_m': round(missing_m, 1),
            'wrong_direction_m': round(wrong_m, 1),
            'covered_pct': round(100.0 * covered_m / total, 1),
            'segments': segments,
            'gaps': gaps,
            'class_metres': {k: round(v, 1) for k, v in class_metres.items()},
        }
