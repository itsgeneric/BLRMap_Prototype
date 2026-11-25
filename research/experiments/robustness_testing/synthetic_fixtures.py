"""
Synthetic Graph Fixtures for Phase 12: Robustness and Edge-Case Testing.

Provides isolated, mathematically defined test graphs to verify:
1. One-way directionality without reverse traversal.
2. Disconnected components and unreachable destinations.
3. Multi-route parallel ranking and choice behavior.
4. Dead-end / cul-de-sac traversal and avoidance.
5. Detour tolerance enforcement (detour ratio > 1.20).
6. Shared edge overlap filtering (overlap > 70%).

All graphs use standard NetworkX MultiDiGraph structures with valid (lat, lng)
coordinates and OSMnx-compatible node and edge attributes.
"""

import math
import networkx as nx
from shapely.geometry import LineString


class MockGraphManager:
    """Mock GraphManager providing neutral (1.0) surface penalty."""
    def get_surface_penalty(self, u, v):
        return 1.0


def _add_edge_with_geom(G, u, v, length, highway, oneway=True, key=0, **kwargs):
    """Helper to add an edge with synthetic 2-point LineString geometry."""
    u_data = G.nodes[u]
    v_data = G.nodes[v]
    geom = LineString([(u_data["x"], u_data["y"]), (v_data["x"], v_data["y"])])
    G.add_edge(
        u, v, key=key,
        length=float(length),
        highway=highway,
        oneway=oneway,
        geometry=geom,
        **kwargs
    )


# ==============================================================================
# Fixture 1: One-way Road with No Legal Reverse Path
# ==============================================================================
def create_oneway_no_reverse_graph():
    """
    Fixture 1: Linear directed corridor A -> B -> C -> D.
    No reverse edges exist.
    Expected:
      - A -> D succeeds.
      - D -> A raises NetworkXNoPath.
      - C -> B raises NetworkXNoPath.
    """
    G = nx.MultiDiGraph()
    # Coordinates along a straight west-to-east line in central Bengaluru
    base_lat = 12.9700
    base_lng = 77.5900
    nodes = {
        "A": (base_lat, base_lng),
        "B": (base_lat, base_lng + 0.0010),
        "C": (base_lat, base_lng + 0.0020),
        "D": (base_lat, base_lng + 0.0030),
    }
    for n, (lat, lng) in nodes.items():
        G.add_node(n, y=lat, x=lng)

    _add_edge_with_geom(G, "A", "B", length=100.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "B", "C", length=100.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "C", "D", length=100.0, highway="residential", oneway=True)

    return G


# ==============================================================================
# Fixture 2: Disconnected Graph Components
# ==============================================================================
def create_disconnected_graph():
    """
    Fixture 2: Two completely disjoint subgraphs.
    Component 1: A <-> B <-> C
    Component 2: X <-> Y <-> Z
    Expected:
      - A -> C succeeds within Component 1.
      - X -> Z succeeds within Component 2.
      - A -> Z raises NetworkXNoPath.
      - X -> A raises NetworkXNoPath.
    """
    G = nx.MultiDiGraph()
    # Component 1 (South)
    c1_nodes = {
        "A": (12.9700, 77.5900),
        "B": (12.9700, 77.5910),
        "C": (12.9700, 77.5920),
    }
    for n, (lat, lng) in c1_nodes.items():
        G.add_node(n, y=lat, x=lng)

    for u, v in [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]:
        _add_edge_with_geom(G, u, v, length=100.0, highway="residential", oneway=False)

    # Component 2 (North - isolated by 1 km)
    c2_nodes = {
        "X": (12.9800, 77.5900),
        "Y": (12.9800, 77.5910),
        "Z": (12.9800, 77.5920),
    }
    for n, (lat, lng) in c2_nodes.items():
        G.add_node(n, y=lat, x=lng)

    for u, v in [("X", "Y"), ("Y", "X"), ("Y", "Z"), ("Z", "Y")]:
        _add_edge_with_geom(G, u, v, length=100.0, highway="residential", oneway=False)

    return G


# ==============================================================================
# Fixture 3: Multiple Parallel Corridors
# ==============================================================================
def create_parallel_routes_graph():
    """
    Fixture 3: Origin S, Destination D connected by 4 parallel corridors:
      - Corridor 1 (Primary Arterial): Straight, length 400m, primary (penalty 1.25).
      - Corridor 2 (Residential Bypass): S -> R1 -> R2 -> D, length 420m, residential (penalty 1.0), 2 turns.
      - Corridor 3 (Tertiary Street): S -> T1 -> T2 -> D, length 460m, tertiary (penalty 1.0), 2 turns.
      - Corridor 4 (Service Lane): S -> W1 -> W2 -> D, length 550m, service (penalty 1.0), 2 turns.
    Expected:
      - Correct cost calculation incorporating road penalties and turn penalties.
      - Deterministic ranking of corridors.
    """
    G = nx.MultiDiGraph()
    nodes = {
        "S":  (12.9700, 77.5900),
        "D":  (12.9700, 77.5940),
        # Arterial corridor (straight along y = 12.9700)
        "M1": (12.9700, 77.5913),
        "M2": (12.9700, 77.5927),
        # Residential corridor (north offset y = 12.9715)
        "R1": (12.9715, 77.5913),
        "R2": (12.9715, 77.5927),
        # Tertiary corridor (further north offset y = 12.9730)
        "T1": (12.9730, 77.5913),
        "T2": (12.9730, 77.5927),
        # Service corridor (south offset y = 12.9680)
        "W1": (12.9680, 77.5913),
        "W2": (12.9680, 77.5927),
    }
    for n, (lat, lng) in nodes.items():
        G.add_node(n, y=lat, x=lng)

    # Corridor 1: Primary Arterial (400m total, straight)
    _add_edge_with_geom(G, "S", "M1", length=130.0, highway="primary", oneway=True)
    _add_edge_with_geom(G, "M1", "M2", length=140.0, highway="primary", oneway=True)
    _add_edge_with_geom(G, "M2", "D", length=130.0, highway="primary", oneway=True)

    # Corridor 2: Residential Bypass (420m total, 2 turns)
    _add_edge_with_geom(G, "S", "R1", length=140.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "R1", "R2", length=140.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "R2", "D", length=140.0, highway="residential", oneway=True)

    # Corridor 3: Tertiary Connector (460m total, 2 turns)
    _add_edge_with_geom(G, "S", "T1", length=150.0, highway="tertiary", oneway=True)
    _add_edge_with_geom(G, "T1", "T2", length=160.0, highway="tertiary", oneway=True)
    _add_edge_with_geom(G, "T2", "D", length=150.0, highway="tertiary", oneway=True)

    # Corridor 4: Service Lane (550m total, 2 turns)
    _add_edge_with_geom(G, "S", "W1", length=180.0, highway="service", oneway=True)
    _add_edge_with_geom(G, "W1", "W2", length=190.0, highway="service", oneway=True)
    _add_edge_with_geom(G, "W2", "D", length=180.0, highway="service", oneway=True)

    return G


# ==============================================================================
# Fixture 4: Dead-End Road / Cul-de-Sac
# ==============================================================================
def create_dead_end_graph(trapped_oneway=False):
    """
    Fixture 4: Main corridor A <-> B <-> C <-> D with a side cul-de-sac branch B <-> E <-> F.
    Node F is a dead-end leaf node (in-degree 1, out-degree 1 if bidirectional).
    If trapped_oneway=True, the cul-de-sac branch is one-way B -> E -> F, trapping anyone at F.
    Expected:
      - A -> F enters dead-end successfully: [A, B, E, F].
      - A -> D stays on main road: [A, B, C, D], never visiting E or F.
      - F -> D navigates out: [F, E, B, C, D] (bidirectional mode).
      - F -> D raises NetworkXNoPath (trapped_oneway mode).
    """
    G = nx.MultiDiGraph()
    nodes = {
        "A": (12.9700, 77.5900),
        "B": (12.9700, 77.5910),
        "C": (12.9700, 77.5920),
        "D": (12.9700, 77.5930),
        # Cul-de-sac branch north of B
        "E": (12.9710, 77.5910),
        "F": (12.9720, 77.5910),
    }
    for n, (lat, lng) in nodes.items():
        G.add_node(n, y=lat, x=lng)

    # Main corridor (bidirectional)
    for u, v in [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B"), ("C", "D"), ("D", "C")]:
        _add_edge_with_geom(G, u, v, length=100.0, highway="residential", oneway=False)

    # Cul-de-sac branch
    if trapped_oneway:
        _add_edge_with_geom(G, "B", "E", length=100.0, highway="residential", oneway=True)
        _add_edge_with_geom(G, "E", "F", length=100.0, highway="residential", oneway=True)
    else:
        for u, v in [("B", "E"), ("E", "B"), ("E", "F"), ("F", "E")]:
            _add_edge_with_geom(G, u, v, length=100.0, highway="residential", oneway=False)

    return G


# ==============================================================================
# Fixture 5: Detour Exceeded Graph
# ==============================================================================
def create_detour_exceeded_graph():
    """
    Fixture 5: Origin S, Destination D.
      - Primary route: S -> P1 -> D. Total length: 100.0m.
      - Only alternative route: S -> A1 -> A2 -> D. Total length: 135.0m.
      - Detour ratio = 135.0 / 100.0 = 1.35x.
    Expected:
      - Under DETOUR_TOLERANCE = 1.20, the alternative route must be rejected with
        reason 'detour_exceeded'.
      - Surviving alternative count = 0.
    """
    G = nx.MultiDiGraph()
    nodes = {
        "S":  (12.9700, 77.5900),
        "D":  (12.9700, 77.5920),
        # Primary path nodes
        "P1": (12.9700, 77.5910),
        # Alternative path nodes (wide northern detour)
        "A1": (12.9720, 77.5905),
        "A2": (12.9720, 77.5915),
    }
    for n, (lat, lng) in nodes.items():
        G.add_node(n, y=lat, x=lng)

    # Primary path (100m total)
    _add_edge_with_geom(G, "S", "P1", length=50.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "P1", "D", length=50.0, highway="residential", oneway=True)

    # Alternative path (135m total: 45 + 45 + 45)
    _add_edge_with_geom(G, "S", "A1", length=45.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "A1", "A2", length=45.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "A2", "D", length=45.0, highway="residential", oneway=True)

    return G


# ==============================================================================
# Fixture 6: Overlap Exceeded Graph
# ==============================================================================
def create_overlap_exceeded_graph():
    """
    Fixture 6: Origin S, Destination D. Total primary distance = 1000m.
      - Primary route: S -> N1 -> N2 -> N3 -> N4 -> D (5 edges of 200m = 1000m).
      - Alternative route: S -> N1 -> N2 -> ALT -> N4 -> D.
      - Edges shared with primary: (S, N1) [200m], (N1, N2) [200m], (N4, D) [200m].
        Total shared edge length = 600m + bypass = 600m / 800m = 75.0% overlap.
      - Overlap ratio = 75.0% > 70.0% threshold.
    Expected:
      - Under MAX_OVERLAP = 0.70, the alternative route must be rejected with
        reason 'overlap_exceeded'.
      - Surviving alternative count = 0.
    """
    G = nx.MultiDiGraph()
    nodes = {
        "S":   (12.9700, 77.5900),
        "N1":  (12.9700, 77.5910),
        "N2":  (12.9700, 77.5920),
        "N3":  (12.9700, 77.5930),
        "N4":  (12.9700, 77.5940),
        "D":   (12.9700, 77.5950),
        # Small parallel detour node bypassing N3
        "ALT": (12.9708, 77.5930),
    }
    for n, (lat, lng) in nodes.items():
        G.add_node(n, y=lat, x=lng)

    # Primary route (1000m total: 5 segments of 200m)
    _add_edge_with_geom(G, "S", "N1", length=200.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "N1", "N2", length=200.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "N2", "N3", length=200.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "N3", "N4", length=200.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "N4", "D", length=200.0, highway="residential", oneway=True)

    # Alternative route detour around N3 (N2 -> ALT -> N4)
    # Bypass edges are 110m each. Total alt length = 200 + 200 + 110 + 110 + 200 = 820m.
    # Shared edges = (S, N1), (N1, N2), (N4, D) = 600m.
    # Overlap relative to alt = 600 / 820 = 73.17% > 70.0%.
    _add_edge_with_geom(G, "N2", "ALT", length=110.0, highway="residential", oneway=True)
    _add_edge_with_geom(G, "ALT", "N4", length=110.0, highway="residential", oneway=True)

    return G
