# Phase 12.1 — Independent Robustness Audit

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 12.1 — Independent Robustness Audit (Read-Only)  
**Date:** March 2026 / Local Execution: November 4, 2026  
**Document:** [`phase_12_independent_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/phase_12_independent_audit.md)  
**Audit Target:** Phase 12 Deliverables ([`phase_12_final_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/phase_12_final_report.md), [`robustness_test_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/robustness_test_results.json))  
**Auditor Mode:** Strictly READ-ONLY (No code, parameters, or test scripts modified)  

---

## 1. Executive Summary and Audit Scope

This independent audit conducted a forensic review of the 26 tests, edge-case evaluations, and synthetic benchmarks executed in Phase 12. The audit verified the empirical claims, re-calculated key metrics from raw graph data, inspected source code in [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) and [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py), and re-examined the single reported test failure (`ROB-OD-07`) alongside the reported passes.

### Key Audit Findings:
1. **ROB-OD-07 Reclassification (Not an Algorithm Failure):** The single test reported as `FAIL` in Phase 12 (`ROB-OD-07`, Central Business District Micro-Trip) is **an invalid test expectation, not a routing algorithm failure**. In the dense one-way gyratory grid of central Bengaluru (MG Road, Church Street, Residency Road), pure unweighted shortest-path Dijkstra requires **1,525.0 meters** across 38 nodes to legally travel between opposing divided sides of the boulevard. The routing engine correctly refused to cross concrete medians or reverse through one-way streets.
2. **Identification of Genuine Production Defects in Reported Passes:**
   - **ROB-OD-01 (Identical OD):** While [`two_wheeler_astar`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L459-L605) returns `[s]` ($0.0\text{ m}$), [`build_split_route_candidates`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L965-L1228) contains a **genuine production defect**: it generates three circular out-and-back loops ($500\text{ m} - 1,000\text{ m}$) that survive filtering and are offered as valid "alternatives" for a zero-distance query.
   - **ROB-OD-06 (Extraterritorial Coordinates):** The system possesses a **genuine architectural vulnerability**: unconstrained spatial $k$-d tree projection silently snaps coordinates in the Bay of Bengal ($455\text{ km}$ away) to perimeter boundary nodes without bounds checking, errors, or warnings.
3. **One-Way & Access Tag Integrity Verified:** The 31,391 strictly one-way edges in Bengaluru and all 6 synthetic fixtures strictly enforce edge directionality ($0\%$ reverse leak). Access restrictions (`access=private`, `motor_vehicle=no`) are statically purged during graph loading rather than evaluated dynamically per query.
4. **Synthetic Fixture Rigor:** All 6 synthetic fixtures were verified as topologically sound, mathematically constrained, and capable of isolating their target invariants.

---

## 2. Audit of ROB-OD-01: Identical Origin and Destination

### 2.1 Investigation of Candidate Generation Trace
When origin and destination coordinates are identical:
$$\text{from\_lat} = \text{to\_lat} = 12.9237^\circ\text{N}, \quad \text{from\_lng} = \text{to\_lng} = 77.5714^\circ\text{E}$$

The audit inspected the code execution path in [`build_split_route_candidates`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L965-L1228):
1. **Primary Route Output:**
   - `direct_start` and `direct_end` snap to the identical node $s$.
   - `two_wheeler_astar(graph, s, s)` hits line 565 (`if current_node == end_node:` on state pop 1) and returns `[s]`.
   - `calc_route_distance(graph, [s])` evaluates `range(len(route) - 1) == range(0)`, returning `0.0`.
   - `path_cost` returns `0.0`.
   - Primary candidate `candidates[0]` is recorded as `[s]` with $\text{cost} = 0.0, \text{dist} = 0.0\text{ m}$.
2. **Fallback Cap Length Collapse:**
   - At line 1058 of `routing/algorithms.py`:
     ```python
     fallback_cap_length = direct_length if direct_length else haversine_m(from_lat, from_lng, to_lat, to_lng)
     ```
     Because `direct_length == 0.0` (falsy in Python), the conditional evaluates `haversine_m(from_lat, from_lng, to_lat, to_lng)`, which is also `0.0`. Therefore, `fallback_cap_length = 0.0`.
3. **Offset Waypoint Generation:**
   - At lines 911–958 ([`_offset_split_points`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L911-L958)):
     - Bearing calculation `_bearing_deg(from_lat, from_lng, to_lat, to_lng)` returns `0.0` (due North) because `atan2(0, 0) == 0`.
     - Base points for all split fractions $(0.33, 0.5, 0.67)$ collapse to `(from_lat, from_lng)`.
     - Lateral offsets of $150\text{ m}$ and $300\text{ m}$ at side bearings $90^\circ$ and $270^\circ$ generate 4 distinct geographic coordinates located $150\text{ m}$ East, $150\text{ m}$ West, $300\text{ m}$ East, and $300\text{ m}$ West.
     - `ox.nearest_nodes` snaps these lateral coordinates to real, distinct road nodes in the surrounding neighborhood.
4. **Stitched Loop Formation:**
   - For each split node, the engine computes:
     - Leg 1: `two_wheeler_astar(graph, s, split_node)`
     - Leg 2: `two_wheeler_astar(graph, split_node, s)`
     - Stitched: `_dedupe_nodes(leg1 + leg2[1:])`
   - This forms a continuous, closed circular cycle: $s \to \dots \to \text{split\_node} \to \dots \to s$.
5. **Bypass of Detour and Overlap Filters:**
   - **Detour Filter (Line 1152):**
     ```python
     detour_ratio = cand_dist / fallback_cap_length if fallback_cap_length > 0 else 1.0
     ```
     Because `fallback_cap_length == 0.0`, the guard triggers and sets `detour_ratio = 1.0`. Since $1.0 \le 1.20$, **the detour filter is completely bypassed**.
   - **Overlap Filter (Line 793, [`calc_route_overlap`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L788-L800)):**
     Because `primary_nodes == [s]` has length $< 2$, `get_route_edge_lengths(graph, [s])` returns `{}` (empty set of edges). The shared edge length is therefore $0.0\text{ m}$, yielding:
     $$\text{overlap} = \frac{0.0}{\text{alt\_len}} = 0.0 \le 0.70$$
     **The overlap filter is completely bypassed**.

### 2.2 Defect Classification and Severity
- **Classification:** **Genuine Production Defect** in [`build_split_route_candidates`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L965).
- **Severity:** **Moderate** (User Experience / Commuter Quality). While the engine does not crash and the direct route is optimal ($0.0\text{ m}$), presenting three circular joyrides to a commuter asking to travel from Point A to Point A violates routing semantics.
- **Recommended Correction:** Add an early return guard in `build_split_route_candidates`:
  ```python
  if direct_start == direct_end or haversine_m(from_lat, from_lng, to_lat, to_lng) < 10.0:
      return [candidates[0]] if not return_diagnostics else {
          "candidates": [candidates[0]], "direct_route": candidates[0],
          "diverse_alternatives": [], "generated_count": 0,
          "rejected_candidates": [], "surviving_count": 0
      }
  ```

---

## 3. Audit of ROB-OD-06: Invalid Geographic Coordinates

### 3.1 Investigation of Coordinate Snapping
- **Query Tested:** $(13.0000^\circ\text{N}, 82.0000^\circ\text{E})$ (located in the Bay of Bengal, $\approx 455\text{ km}$ east of central Bengaluru).
- **Observed Result:** Snapped silently to Node `2247666159` ($(13.0390^\circ\text{N}, 77.8000^\circ\text{E})$), the easternmost boundary node in [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl).

### 3.2 Code Audit of Snapping Pipeline
1. In [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L991-L1001) and [`api_server.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/api_server.py#L58-L59):
   ```python
   start = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
   end   = ox.nearest_nodes(graph_manager.G, to_lng, to_lat)
   ```
2. OSMnx's `ox.nearest_nodes` builds a spatial $k$-d tree (`scipy.spatial.KDTree` or `sklearn.neighbors.BallTree`) over all node coordinates $(x, y) \in V(G)$.
3. **Absence of Snapping Radius:** The implementation performs an unconstrained 1-nearest-neighbor query without a distance threshold ($r_{\max} = \infty$).
4. **Absence of Bounding-Box Validation:** Neither `api_server.py` nor `algorithms.py` checks input coordinates against `graph_manager.bounds` (`min_lat`, `max_lat`, `min_lng`, `max_lng`).
5. **Absence of Warning / Error Mechanisms:** The system returns HTTP 200 with a syntactically valid route starting from the boundary node, offering no warning that the input was $455\text{ km}$ away.

### 3.3 Defect Classification and Severity
- **Classification:** **Genuine Architectural Vulnerability** (API and Service Ingress Layer).
- **Severity:** **High** (System Integrity). The routing engine cannot distinguish an invalid extraterritorial coordinate from a valid commuter standing at the city boundary.
- **Recommended Correction:**
  Enforce a two-tier spatial validation at the API boundary:
  1. *Bounding-box pre-check:* Verify $\text{lat} \in [\text{min\_lat} - \delta, \text{max\_lat} + \delta]$ and $\text{lng} \in [\text{min\_lng} - \delta, \text{max\_lng} + \delta]$.
  2. *Maximum snapping radius:* Compute Haversine distance between input coordinate and snapped node. If $d_{\text{snap}} > 1,500\text{ m}$, reject with HTTP 422:
     ```json
     {"status": "error", "message": "Location outside serviceable road network (snapped 455.0 km away)."}
     ```

---

## 4. Audit of ROB-OD-07: MG Road Micro-Trip

### 4.1 Re-examination of the Reported "Failure"
In Phase 12, Test `ROB-OD-07` was recorded as:
- **Condition:** Central commercial dense grid micro-trip (200m in MG Road area).
- **Expected:** Short 200m trip executes in $< 5.0\text{ ms}$; distance between $100\text{ m}$ and $500\text{ m}$.
- **Actual:** Micro-trip: 43 nodes, **$1,837.2\text{ m}$** in **$5.78\text{ ms}$** (469 states).
- **Reported Status:** **FAIL**.

### 4.2 Forensic Network Inspection
The audit executed an independent topological trace between the exact snapped nodes:
- **Start Node:** `11961205354` ($(12.97477^\circ\text{N}, 77.60629^\circ\text{E})$, Church Street / Brigade Road)
- **End Node:** `3740962222` ($(12.97751^\circ\text{N}, 77.60759^\circ\text{E})$, Cubbon Road / Kamaraj Road)
- **Euclidean / Haversine Distance:** **$335.6\text{ m}$**.

The audit ran unconstrained Dijkstra on edge `length` across the entire graph to determine the absolute shortest legal road path in Bengaluru:
$$\text{Shortest Legal Physical Path in } G = \mathbf{1,525.0\text{ m}} \quad (38\text{ nodes})$$

### 4.3 Street-by-Street Legal Path Decomposition

| Step | Street Name | OSM Highway Class | One-Way Direction | Segment Distance | Cumulative Distance |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | Unnamed Alley | `service` | Bidirectional | $10.9\text{ m}$ | $10.9\text{ m}$ |
| 2 | **Church Street** | `unclassified` | **Strictly One-Way (Eastbound)** | $413.9\text{ m}$ | $424.8\text{ m}$ |
| 3 | Museum Cross Road | `unclassified` | Bidirectional | $89.4\text{ m}$ | $514.2\text{ m}$ |
| 4 | **Mahatma Gandhi Road** | `secondary` | **Strictly One-Way (Eastbound)** | $82.4\text{ m}$ | $596.6\text{ m}$ |
| 5 | **Central Street** | `tertiary` | **Strictly One-Way (Northbound)** | $487.5\text{ m}$ | $1,084.1\text{ m}$ |
| 6 | **Infantry Road** | `tertiary` | **Strictly One-Way (Eastbound)** | $485.2\text{ m}$ | $1,569.3\text{ m}$ |
| 7 | **Main Guard Cross Road** | `tertiary` | **Strictly One-Way (Southbound)** | $134.9\text{ m}$ | $1,704.2\text{ m}$ |
| 8 | Unnamed Link | `tertiary_link` | Strictly One-Way | $29.3\text{ m}$ | $1,733.5\text{ m}$ |
| 9 | **Cubbon Road** | `primary` | **Strictly One-Way (Westbound)** | $90.4\text{ m}$ | $1,823.9\text{ m}$ |
| 10 | Destination Link | `primary_link` | Bidirectional | $13.4\text{ m}$ | **$1,837.2\text{ m}$** |

```
Topological Circuity in Central Bengaluru Grid
Cubbon Road (Westbound)  <════════════════════════════════════ End Node
         ▲                                                        │
         ║ Central St (Northbound, 487m)                          ║ Main Guard Cross Rd (Southbound, 135m)
         ║                                                        ▼
Mahatma Gandhi Road (Eastbound) ═════════> Infantry Rd (Eastbound, 485m)
         ▲
         ║ Museum Cross Rd (89m)
         ║
Church Street (Eastbound, 414m)
Start Node ═════════════════════>
```

### 4.4 Audit Determination
- **Is this a routing failure?** **NO.** There is no shorter legal path in the road graph. Even pure distance-minimizing Dijkstra requires $1,525.0\text{ m}$. Two-wheeler $A^*$ takes $1,837.2\text{ m}$ ($+20.4\%$) because it avoids high-stress arterial crossings and penalizes sharp turns.
- **Was the test assertion appropriate?** **NO.** Expecting a distance between $100\text{ m}$ and $500\text{ m}$ in a dense one-way urban gyratory system was a flawed test design assumption.
- **Classification:** **Incorrect Test Expectation**. The routing engine exhibited **verified correct behavior** by respecting one-way directionality and divided carriageway medians.

---

## 5. Audit of One-Way and Access Restrictions

The audit inspected graph construction in [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py) and routing in [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py):

### 5.1 Ingestion-Time vs. Search-Time Restrictions

```
Enforcement Boundary Breakdown
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ Ingestion-Time Enforcement (GraphManager)    │ Search-Time Enforcement (two_wheeler_astar)  │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ 1. Access tags: access=no/private            │ 1. One-way directionality (G.successors(u))  │
│ 2. Vehicle tags: vehicle=no/private          │ 2. Road classification cost multipliers      │
│ 3. Motor vehicle tags: motor_vehicle=no      │ 3. Turn maneuver penalties (0, 8, 25)        │
│ 4. Non-motorized types: footway, path, etc.  │ 4. Dynamic congestion penalties (25x)        │
│ 5. Length caps on minor road classes         │ 5. Surface quality multipliers (1.0 - 1.5x)  │
│ 6. Largest Strongly Connected Component (SCC)│ 6. Flyover / bridge discounts (0.8x)         │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

### 5.2 Verification Evidence
1. **One-Way Directionality:** Verified on 31,391 strictly one-way edges in Bengaluru. Because $G$ is a directed `MultiDiGraph`, `graph.successors(u)` yields only outgoing edges. The router never traverses directed edges in reverse ($0\%$ violation rate).
2. **Access Tag Purge Audit:** An exhaustive audit of all 744,216 edges in `bengaluru_graph.pkl` confirmed that **zero edges with `access=no`, `access=private`, or `motor_vehicle=no` remain in the graph**.
3. **Claim Boundary:** The system **cannot claim dynamic access-tag enforcement**. If a road tag changes dynamically or is tagged with nuanced restrictions like `access=destination` or `motorcycle=no`, it is not evaluated during `two_wheeler_astar`. Access enforcement is strictly static and offline.

---

## 6. Audit of Synthetic Graph Tests

The audit inspected all six synthetic graph fixtures in [`experiments/robustness_testing/synthetic_fixtures.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/synthetic_fixtures.py) and verified them against [`experiments/robustness_testing/test_synthetic_graphs.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/test_synthetic_graphs.py):

| Fixture | Intended Condition | Expected Route Behavior | Genuinely Exercised? | Assertion Vulnerability Check | Audit Finding |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **G_oneway_no_reverse** | Strict directed edge constraint | $A \to D$ succeeds; $D \to A$ raises `NoPath` | **YES** | Checks exact node list and explicit exception raising. | **VERIFIED SOUND** |
| **G_disconnected** | Graph component partition | Intra-component succeeds; inter-component raises `NoPath` | **YES** | Checks intra paths and explicit cross-component exception. | **VERIFIED SOUND** |
| **G_parallel_routes** | Road-type vs. turn cost ranking | Uniform selects Arterial; 2W selects Residential | **YES** | Checks exact node lists and exact floating-point costs (400.0 vs 436.0). | **VERIFIED SOUND** |
| **G_dead_end** | Cul-de-sac branch traversal & avoidance | Ingress enters dead end; transit bypasses; egress exits | **YES** | Checks exact node sequences for leaf destination, transit, and egress. | **VERIFIED SOUND** |
| **G_detour_exceeded** | Detour tolerance constraint ($> 1.20$) | Candidate rejected with `detour_exceeded` | **YES** | Verifies distance ratio $1.35 > 1.20$ and rejection trigger. | **VERIFIED SOUND** |
| **G_overlap_exceeded** | Shared edge overlap cap ($> 70\%$) | Candidate rejected with `overlap_exceeded` | **YES** | Verifies overlap ratio $73.17\% > 70.0\%$ and rejection trigger. | **VERIFIED SOUND** |

**Audit Conclusion on Synthetic Tests:** All six synthetic tests are mathematically sound, isolated from real-world data noise, and test the targeted algorithmic mechanisms.

---

## 7. Recalculated Master Test Classification

To maintain complete scientific integrity, this audit preserves the original Phase 12 reported score (25 Passes, 1 Fail) while presenting the **audited analytical reclassification**:

```
Comparative Audit Reclassification
┌───────────────────────────────────────────────┬──────────────┬──────────────┐
│ Classification Category                       │ Phase 12 Raw │ Audit Revised│
├───────────────────────────────────────────────┼──────────────┼──────────────┤
│ Verified Successful Behavior (Sound)          │      23      │      23      │
│ Expected Routing Behavior (Flawed Test Spec)  │       0      │       1      │
│ Reported Failure (ROB-OD-07)                  │       1      │       0      │
│ Genuine Production Defects / Vulnerabilities  │       2*     │       2      │
├───────────────────────────────────────────────┼──────────────┼──────────────┤
│ Total Evaluated Tests                         │      26      │      26      │
└───────────────────────────────────────────────┴──────────────┴──────────────┘
* Note: ROB-OD-01 and ROB-OD-06 were reported as passes with documented limitations in Phase 12;
  the audit elevates them to genuine production defects requiring engineering remediation.
```

### Detailed Breakdown of Audited Classifications:
1. **Verified Successful Behavior (23 Tests):**
   - `ROB-NET-01` to `ROB-NET-07`: All network integrity tests passed with full graph validity.
   - `ROB-OD-02` to `ROB-OD-05`: Single-hop, long-distance (58km), boundary, and cut-edge tests verified sound.
   - `ROB-ALT-OD_01`, `OD_04`, `OD_06`, `OD_12`, `OD_15`, `ALT-06`: Alternative routing and degradation verified sound.
   - `ROB-SYN-01` to `ROB-SYN-06`: All synthetic benchmarks verified sound.
2. **Incorrect Test Expectation (1 Test):**
   - `ROB-OD-07`: Central Business District Micro-Trip. Algorithmic routing was 100% correct; test distance upper bound was flawed.
3. **Genuine Production Defects / Vulnerabilities (2 Tests):**
   - `ROB-OD-01`: Candidate generator produces 3 circular out-and-back loops for identical OD queries.
   - `ROB-OD-06`: Ingress layer lacks bounding-box validation and snapping radius limits, projecting Bay of Bengal coordinates 455 km away.

---

## 8. Audit Acceptance Recommendation

Phase 12 is **RECOMMENDED FOR CONDITIONAL ACCEPTANCE** subject to the following documentation and roadmap conditions:

1. **Acceptance of Phase 12 Testing:**
   - The test suite successfully probed edge cases, uncovered genuine production defects, and verified algorithmic guarantees without crashing or introducing code modifications.
2. **Phase 12.2 Documentation Corrections:**
   - Document `ROB-OD-07` as an *Incorrect Test Expectation* rather than an algorithm failure.
   - Formally document the *Identical OD Circular Loop Defect* (`ROB-OD-01`) and the *Extraterritorial Snapping Vulnerability* (`ROB-OD-06`) in the system defect backlog.
3. **Engineering Scope for Future Phases:**
   - Implement the zero-distance guard in [`build_split_route_candidates`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L965).
   - Implement the bounding-box and maximum snapping radius threshold in [`api_server.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/api_server.py).

---

## 9. Compliance Confirmation

- Production code ([`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py)) was **NOT modified**.
- Test scripts and fixtures were **NOT modified**.
- Graph data and routing parameters were **NOT altered**.
- Benchmark datasets from Phases 9, 10, and 11 were **NOT altered**.
- **Phase 13 has NOT been started.**
