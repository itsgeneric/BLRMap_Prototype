"""
Where should a trip END when no public road reaches the destination?

Snapping the pin to the nearest road in a straight line ignores walls: it can pick a dead end BEHIND a campus while the
way in is on the other side. Google knows which side a place is approached from. So when the pin is far from every road,
we take Google's route to it and walk that route BACKWARDS from its end to the last stretch that runs along one of OUR
public roads. The trip ends there.

  * Not Google's last point: that is often inside the campus, on roads we do not have or may not use.
  * "Runs along" means close to the road AND pointing the same way, for a short stretch. A road that Google's line merely
    crosses (or passes behind a wall) does not count.
Nothing is drawn from that point to the pin.
"""
import math

from core.config import ARRIVAL_ON_ROAD_M, ARRIVAL_MAX_FROM_PIN_M
from routing.algorithms import _bearing_deg, haversine_m
from routing.snapping import find_snaps

STEP_M = 5.0            # Google's route is examined this often
FOLLOW_M = 15.0         # it must run along the road for at least this far
MAX_ANGLE_DEG = 30.0    # "pointing the same way" (either direction along the road)


def _samples(path):
    """[(lat, lng, heading), ...] every STEP_M along the path."""
    out = []
    for (a_lat, a_lng), (b_lat, b_lng) in zip(path, path[1:]):
        length = haversine_m(a_lat, a_lng, b_lat, b_lng)
        if length < 0.5:
            continue
        heading = _bearing_deg(a_lat, a_lng, b_lat, b_lng)
        for i in range(max(1, int(math.ceil(length / STEP_M)))):
            t = i * STEP_M / length
            out.append((a_lat + t * (b_lat - a_lat), a_lng + t * (b_lng - a_lng), heading))
    if out:
        out.append((path[-1][0], path[-1][1], out[-1][2]))
    return out


def _road_heading(snap):
    """Direction of the snapped road at the snapped point."""
    ahead = snap.after_coords if len(snap.after_coords) > 1 else snap.before_coords
    (a_lat, a_lng), (b_lat, b_lng) = ahead[0], ahead[1]
    return _bearing_deg(a_lat, a_lng, b_lat, b_lng)


def _aligned(heading_a, heading_b):
    difference = abs(heading_a - heading_b) % 180.0
    return min(difference, 180.0 - difference) <= MAX_ANGLE_DEG


def _along_public_road(G, index, sample):
    """The public road edges that this point of Google's route runs along (empty if none)."""
    lat, lng, heading = sample
    found = find_snaps(G, index, lat, lng, ARRIVAL_ON_ROAD_M, tolerance_m=5.0, limit=6)
    return [s for s in found
            if s.edge and not G[s.edge[0]][s.edge[1]][s.edge[2]].get('access_only')
            and len(s.after_coords) + len(s.before_coords) > 2 and _aligned(heading, _road_heading(s))]


def arrival_snaps(G, index, google_path, pin):
    """
    Destination candidates (like snapping.find_snaps) at the point where Google's route last runs along a public road,
    or None. Each candidate's distance_m is measured from the real pin.
    """
    if not google_path or len(google_path) < 2:
        return None
    samples = _samples(google_path)
    need = int(FOLLOW_M // STEP_M) + 1
    run = []                                            # the newest-first run of samples that follow a road
    for sample in reversed(samples):
        if haversine_m(sample[0], sample[1], pin[0], pin[1]) > ARRIVAL_MAX_FROM_PIN_M:
            return None                                 # no usable road anywhere near the place
        roads = _along_public_road(G, index, sample)
        if not roads:
            run = []
            continue
        run.append(roads)
        if len(run) >= need:
            snaps = run[0]                              # the point nearest the destination end of that run
            for snap in snaps:
                snap.pin = (pin[0], pin[1])
                snap.distance_m = haversine_m(pin[0], pin[1], snap.point[0], snap.point[1])
            return snaps
    return None
