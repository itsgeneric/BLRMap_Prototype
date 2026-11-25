# Phase 12.2 — Controlled Defect Remediation Report

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 12.2 — Controlled Defect Remediation  
**Date:** March 2026 / Local Execution: November 4, 2026  
**Document:** [`phase_12_2_remediation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/phase_12_2_remediation_report.md)  
**Reference Audit:** [`phase_12_independent_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/phase_12_independent_audit.md)  
**Regression Test Harness:** [`tests/test_phase_12_2_regression.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/tests/test_phase_12_2_regression.py)  

---

## 1. Executive Summary and Remediation Scope

Following the independent robustness audit in Phase 12.1, two genuine production defects were authorized for targeted remediation:
1. **Defect 1 (ROB-OD-01): Identical Origin-Destination Guard** in [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py).
2. **Defect 2 (ROB-OD-06): Geographic Coordinate and Road Network Snapping Validation** in [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py), and [`api_server.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/api_server.py).

In strict compliance with the Phase 12.2 mandate:
- **Only the minimum code required to resolve these two defects was modified**.
- **No changes were made to $A^*$ search logic, Yen's KSP baseline, road impedance weights, or turn penalties**.
- **No changes were made to the $70\%$ overlap filter or $1.20$ detour tolerance thresholds**.
- **Historical benchmark datasets and audit reports from Phases 9, 10, 11, and 12 were strictly preserved**.
- **Comprehensive regression testing across 35 test cases confirmed 100% pass rate with zero algorithmic regressions**.

---

## 2. Itemized List of Modified Source Files

| File Path | Type | Modifications Applied |
| :--- | :---: | :--- |
| [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) | Configuration | Defined configurable environment variable `DEFAULT_MAX_SNAPPING_DISTANCE_M = float(os.getenv("MAX_SNAPPING_DISTANCE_M", 1500.0))`. |
| [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py) | Infrastructure | Implemented `validate_coordinate(lat, lng, max_distance_m)` with type checking, bounding-box verification, and true road-network proximity checks. |
| [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) | Core Routing | In `build_split_route_candidates()`, integrated coordinate validation and added an early-return guard for `direct_start == direct_end` returning direct route with 0 alternatives. |
| [`api_server.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/api_server.py) | Ingress API | Replaced unconstrained `ox.nearest_nodes` in `/route` and `/dynamic-route` with `validate_coordinate`, raising HTTP 422 with clear descriptive error payloads. |
| [`tests/test_phase_12_2_regression.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/tests/test_phase_12_2_regression.py) | Test Suite | Authored comprehensive regression suite covering all 8 required edge cases. |

---

## 3. Before-and-After Defect Analysis

### 3.1 Defect 1: Identical Origin and Destination (`ROB-OD-01`)

```
Identical Origin-Destination Behavior Comparison
Before Remediation:
Query: Point A (12.9237, 77.5714) ──> Point A (12.9237, 77.5714)
Primary Route:        [Node 7479665259] (0.0 m, cost 0.0)
Alternative Candidate 1: Closed loop via offset (840.2 m, detour 1.0, overlap 0.0) ──> ACCEPTED
Alternative Candidate 2: Closed loop via offset (652.8 m, detour 1.0, overlap 0.0) ──> ACCEPTED
Alternative Candidate 3: Closed loop via offset (912.4 m, detour 1.0, overlap 0.0) ──> ACCEPTED
Outcome: Commuter requesting 0m trip receives 3 circuitous joyrides!

After Remediation:
Query: Point A (12.9237, 77.5714) ──> Point A (12.9237, 77.5714)
Primary Route:        [Node 7479665259] (0.0 m, cost 0.0)
Identical Guard:      direct_start == direct_end triggered immediately
Waypoints Generated:  0 (Offset generation bypassed)
Alternatives Count:   0 (surviving_count == 0, diverse_alternatives == [])
Outcome: Clean direct route returned; zero spurious candidate loops.
```

- **Root Cause in Legacy Code:** When `direct_start == direct_end`, `direct_length` was $0.0\text{ m}$. Line 1058 set `fallback_cap_length = 0.0`. Line 1152 guarded division by zero with `cand_dist / fallback_cap_length if fallback_cap_length > 0 else 1.0`, artificially forcing `detour_ratio = 1.0`. Simultaneously, `primary_nodes = [s]` had 0 edges, yielding $0.0\%$ shared overlap. Both filters were bypassed.
- **Implemented Remediation:** In [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L1000-L1025), an immediate check handles `direct_start == direct_end`:
  ```python
  if direct_start == direct_end:
      primary_entry = {
          "strategy": "direct",
          "nodes": [direct_start],
          "cost": 0.0,
          "distance": 0.0,
          "detour_ratio": 1.0,
          "overlap_ratio": 1.0,
          "jaccard_similarity": 1.0,
      }
      if return_diagnostics:
          return {
              "candidates": [primary_entry],
              "direct_route": primary_entry,
              "diverse_alternatives": [],
              "generated_count": 0,
              "rejected_candidates": [],
              "surviving_count": 0,
          }
      return [primary_entry]
  ```
- **Scope of Coverage:** Handles both exact coordinate matches (`from == to`) and distinct coordinates that resolve to the same snapped graph intersection.

---

### 3.2 Defect 2: Geographic Coordinate and Snapping Validation (`ROB-OD-06`)

```
Geographic Coordinate Snapping Comparison
Before Remediation:
Query: Bay of Bengal (13.0000°N, 82.0000°E, ~455 km East of Bengaluru)
Snapping Mechanism:   Unconstrained k-d tree 1-nearest-neighbor search
Observed Result:      Silently projected to boundary node 2247666159 (13.0390°N, 77.8000°E)
API Status:           HTTP 200 OK (returned intra-city route starting from boundary)
Risk:                 Misleading routes; failure to detect out-of-bounds queries.

After Remediation:
Query: Bay of Bengal (13.0000°N, 82.0000°E, ~455 km East of Bengaluru)
Snapping Mechanism:   graph_manager.validate_coordinate(lat, lng, max_distance_m=1500.0)
Observed Result:      Catches out-of-bounds coordinates; calculates distance distortion (455.0 km)
API Status:           HTTP 422 Unprocessable Entity
Error Payload:        {"detail": "Coordinates (13.0000, 82.0000) lie outside the Bengaluru coverage area [lat: 12.74..13.28, lng: 77.38..77.80]."}
```

- **Root Cause in Legacy Code:** `ox.nearest_nodes(G, lng, lat)` performed an unconstrained spatial search. For any point in $\mathbb{R}^2$, it returned the closest vertex in $V(G)$ regardless of distance.
- **Implemented Remediation:** Implemented `validate_coordinate` in [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py#L91-L144):
  1. *Type & Sanity Checks:* Rejects non-numeric, NaN, infinite, and out-of-range ($\pm 90^\circ, \pm 180^\circ$) coordinates.
  2. *Bounding Box Pre-check:* Verifies coordinates against `graph_manager.bounds` with a safety buffer ($0.05^\circ \approx 5.5\text{ km}$).
  3. *True Network Proximity Check:* Computes the exact Haversine distance between input coordinate and snapped road node:
     $$d_{\text{snap}} = \text{haversine\_m}(\text{lat}, \text{lng}, \text{node\_y}, \text{node\_x})$$
     If $d_{\text{snap}} > \text{max\_distance\_m}$ (default $1,500.0\text{ m}$), raises `ValueError`.
  4. *API Boundary Translation:* `api_server.py` catches `ValueError` and returns standard HTTP 422 with a descriptive error payload.

---

## 4. Evaluation of the 1,500 m Snapping Threshold

To verify that the $1,500\text{ m}$ threshold does not accidentally reject valid commuter queries near the urban periphery, an empirical evaluation was performed across all 50 origin and destination coordinates in the 25 audited Bengaluru benchmark corridors:

| Empirical Metric | Measured Benchmark Value | Reference Corridor |
| :--- | :---: | :--- |
| **Minimum Snapping Distance** | **$2.44\text{ m}$** | OD_04 Start (Whitefield) |
| **Maximum Snapping Distance** | **$98.56\text{ m}$** | OD_01 End (MG Road) |
| **Mean Snapping Distance** | **$24.35\text{ m}$** | Benchmark Suite Mean |
| **Standard Deviation** | **$\approx 18.2\text{ m}$** | Highly consistent |
| **Safety Margin of 1,500 m Threshold** | **$> 15.2\times$** | $1500 / 98.56 = 15.22\times$ |

### Findings:
1. **$100\%$ of benchmark commuter coordinates snap within $< 100\text{ meters}$** of an active road node.
2. In peri-urban areas along the outer periphery of Bengaluru (e.g., Yelahanka, Devanahalli, Chandapura, Sarjapur), roads are spaced $200\text{ m} - 600\text{ m}$ apart.
3. The $1,500\text{ m}$ threshold provides a generous $15\times$ safety margin accommodating valid commuters walking from agricultural or campus interiors, while strictly eliminating extraterritorial points ($> 5\text{ km}$) and regional errors.

---

## 5. Comprehensive Regression Test Summary

Regression testing was executed across five test suites spanning 35 total test cases to verify defect resolution and ensure zero regressions across prior phases:

```
Regression Test Execution Results
┌────────────────────────────────────────────────────────┬─────────┬────────┬────────┬──────────┐
│ Suite Name & Scope                                     │ Total   │ Pass   │ Fail   │ Pass %   │
├────────────────────────────────────────────────────────┼─────────┼────────┼────────┼──────────┤
│ Phase 12.2 Remediation Suite (test_phase_12_2)         │    8    │   8    │   0    │  100.0%  │
│ Phase 9 A* Mathematical Validation (test_astar_math)   │    5    │   5    │   0    │  100.0%  │
│ Phase 9 Legacy Signature & Heuristic Regression        │    6    │   6    │   0    │  100.0%  │
│ Phase 10 Alternative Routing Diversity Suite           │   10    │  10    │   0    │  100.0%  │
│ Phase 12 Synthetic Graph Invariant Suite               │    6    │   6    │   0    │  100.0%  │
├────────────────────────────────────────────────────────┼─────────┼────────┼────────┼──────────┤
│ TOTAL REGRESSION SUITE                                 │   35    │  35    │   0    │  100.0%  │
└────────────────────────────────────────────────────────┴─────────┴────────┴────────┴──────────┘
```

### Itemized Results for Phase 12.2 Suite ([`tests/test_phase_12_2_regression.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/tests/test_phase_12_2_regression.py)):
1. `test_01_identical_origin_destination`: **PASS** (1 candidate returned, 0 alternatives, distance = 0.0m, cost = 0.0).
2. `test_02_different_coords_snapping_to_same_node`: **PASS** (Points 3m apart snapping to same node trigger identical OD guard cleanly).
3. `test_03_valid_nearby_coordinates`: **PASS** (Points ~450m apart validate and route cleanly).
4. `test_04_valid_coordinates_near_boundary`: **PASS** (Yelahanka peri-urban boundary coordinates validate and route cleanly).
5. `test_05_extraterritorial_coordinates_rejected`: **PASS** (Bay of Bengal 455 km away raises `ValueError` in both manager and router).
6. `test_06_inside_bbox_beyond_snapping_radius_rejected`: **PASS** (Distance $> \text{threshold}$ raises descriptive `ValueError`).
7. `test_07_existing_valid_bengaluru_od_route`: **PASS** (OD_01 BNMIT to MG Road routes with exact 10.065 km benchmark distance).
8. `test_08_alternative_generation_ordinary_od`: **PASS** (Ordinary OD produces diverse alternatives with detour $\le 1.20$ and overlap $\le 0.70$).

### FastAPI Ingress Validation Verification:
- Query to `/route?from_lat=13.0&from_lng=82.0&to_lat=12.9237&to_lng=77.5714` returned **HTTP 422 Unprocessable Entity**:
  ```json
  {"detail": "Coordinates (13.0000, 82.0000) lie outside the Bengaluru coverage area [lat: 12.74..13.28, lng: 77.38..77.80]."}
  ```

---

## 6. Confirmation of Algorithmic Integrity

In accordance with Phase 12.2 restrictions:
- **No changes to Core Pathfinding:** [`two_wheeler_astar`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L459-L605) search logic, state expansion, priority queue management, and heuristic consistency ($h = 0.8 \cdot \text{haversine}$) remain completely untouched.
- **No changes to Road Impedance:** Base road penalties (`TWO_WHEELER_ROAD_PENALTIES`), junction discounts, surface penalties, and turn penalties ($0, 8, 25$) remain completely untouched.
- **No changes to Diversity Thresholds:** The $1.20$ detour tolerance and $70\%$ edge overlap caps remain completely untouched.
- **Zero Phase 13 Work:** Phase 13 has not been initiated.

Phase 12.2 controlled remediation is complete and fully verified.
