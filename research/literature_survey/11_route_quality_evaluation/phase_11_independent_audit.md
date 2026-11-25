# Phase 11 Independent Audit: Route Quality, Experimental Reproducibility, and Algorithmic Integrity

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Audit Target:** Phase 11 — Route Quality Evaluation, Parameter Sensitivity Analysis, and Runtime Variability Benchmarking  
**Audit Date:** March 2026 / Local Audit: November 4, 2026  
**Auditor:** Independent Antigravity Audit Agent  
**Audit Scope:** Coordinate gap & graph geometry integrity, raw CSV/JSON metric recalculation, parameter sensitivity isolation, runtime benchmark fairness across Phases 9–11, and academic claims validation.  
**Deliverable Path:** `research/literature_survey/11_route_quality_evaluation/phase_11_independent_audit.md`  

---

## Executive Summary & Formal Audit Verdict

| Audit Dimension | Core Verification Target | Independent Audit Finding | Status |
| :--- | :--- | :--- | :---: |
| **1. Route Geometry & Coordinate Gaps** | Consecutive coordinate gaps (OD_15: ~4.9 km, OD_04: ~606 m, OD_06: ~263 m, OD_01: ~275 m, OD_12: ~180 m) | **Graph topology is 100% complete and connected.** Gaps represent uninterrupted road segments where OSMnx simplified intermediate degree-2 nodes. Edge `LineString` geometries are fully intact in the graph, and routing distance uses true edge lengths. However, coordinate exports and visualizations sampled only graph nodes, causing visualizations to render straight-line chords skipping curve vertices. | **VERIFIED WITH VISUALIZATION CAVEAT** |
| **2. Experimental Results Recalculation** | Recompute primary & alternative metrics from raw JSON/CSV across 25 corridors | **Core metric computations match published tables.** (Mean dist: 7.65 km, Mean cost: 9,135.62, Offset detour: 1.046x, overlap: 49.61%). **Discrepancy identified:** `phase_11_final_report.md` cited erroneous/draft road-class percentages (18.4% Arterial vs. actual 13.84%) and cost-per-meter ratio (1.218 vs. actual 1.195). | **VERIFIED WITH DOCUMENTATION DISCREPANCIES** |
| **3. Parameter Sensitivity Isolation** | Verify ablation configurations (C0–C7) change only intended parameters | **Mechanisms verified, but experimental confound identified:** C6 and C7 bundled bridge multipliers with roundabout multipliers (compound variation). The claimed OD_15 shift under C7 (arterial 82.05% $\to$ 6.48%, surviving alts 0 $\to$ 3) was mathematically verified as 100% driven by the bridge penalty on the elevated NH44 expressway. Sharp turn surge (+63.2%) was misattributed to OD_01 instead of OD_06. | **VERIFIED WITH DESIGN & CITATION DEFECTS** |
| **4. Runtime Fairness & Benchmarking** | Multi-repetition runtime protocol, timing boundaries, and cross-phase distinction | **Parity verified; Phase 10 conflation caught:** Phase 11 multi-repetition benchmark established Admissible A* speedup of **$3.03\times$** over Dijkstra and Offset speedup of **$3.90\times$** over Yen KSP. Reports erroneously cited $3.78\times$ (unsupported) and copied Phase 10's single-run numbers (13.74 s, 86.90 s, $6.33\times$). Claims of universal speedup on trips >8 km ignore OD_04 and OD_15 where Yen was faster. | **CORRECTED & DISENTANGLED** |
| **5. Academic Claims Integrity** | Safety claims, impedance vs. time, universal superiority, engineering assumptions | **Claims required tempering:** Formal disclaimers correctly state impedance cost is not travel time. However, turn reduction is improperly equated with "improved safety" / "preventing dangerous shortcuts" without crash telemetry, and Offset superiority is overstated on linear/bottleneck corridors. | **ACTIONABLE REVISIONS IDENTIFIED** |

**Final Audit Recommendation:** **CONDITIONAL ACCEPTANCE (MINOR REVISIONS REQUIRED).**  
The underlying graph, pathfinding algorithms, cost functions, and raw experimental datasets are mathematically robust, topologically intact, and completely sound. Production code (`routing/algorithms.py`, `core/config.py`) remains pristine and unmodified. However, acceptance is conditional upon correcting narrative discrepancies in `phase_11_final_report.md`, `parameter_sensitivity_report.md`, and `runtime_evaluation_report.md` before incorporating these findings into the IEEE research publication.

---

## 1. Route Geometry and Consecutive Coordinate Gap Investigation

The audit conducted an exhaustive node-by-node and edge-by-edge inspection of the five deep-dive case-study routes on the pre-compiled Bengaluru metropolitan graph (`bengaluru_graph.pkl`, 308,643 nodes, 744,216 edges).

### 1.1 Summary of Investigated Long Segments

| Corridor ID | Consecutive Coordinate Gap | Edge Endpoints $(u \to v)$ | OSM Way Name & Highway Class | Stored Graph Edge Length | Straight Chord Distance | Edge Geometry Present? | Intermediate Shape Vertices |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **OD_15** | **$4,897.55\text{ m}$** (~4.90 km) | $12553535777 \to 332955193$ | Bellary Road (`trunk`, `bridge=yes`) | **$4,973.21\text{ m}$** | $4,897.55\text{ m}$ | **Yes** (`LineString`) | **68 vertices** |
| **OD_04** | **$605.62\text{ m}$** (~606 m) | $845778275 \to 12000439030$ | Varthur Road (`primary`, oneway) | **$605.62\text{ m}$** | $605.62\text{ m}$ | **Yes** (`LineString`) | **11 vertices** |
| **OD_06** | **$262.56\text{ m}$** (~263 m) | $302493094 \to 249075661$ | 7th Main Road (`residential`) | **$262.71\text{ m}$** | $262.56\text{ m}$ | **Yes** (`LineString`) | **4 vertices** |
| **OD_01** | **$275.39\text{ m}$** (~275 m) | $2227928339 \to 1837408670$ | Unnamed layout avenue (`residential`) | **$375.69\text{ m}$** | $275.39\text{ m}$ | **Yes** (`LineString`) | **9 vertices** |
| **OD_12** | **$180.49\text{ m}$** (~180 m) | $7617898612 \to 12139153741$ | Saunders Road (`tertiary`) | **$180.74\text{ m}$** | $180.49\text{ m}$ | **Yes** (`LineString`) | **6 vertices** |

### 1.2 Detailed Segment Audits

#### 1. OD_15 (Yelahanka to Hebbal): The 4.90 km Gap on NH44 Bellary Road
- **Node Pair:** $u = 12553535777$ ($\text{Lat: } 13.091090^\circ\text{N}, \text{Lng: } 77.596758^\circ\text{E}$) to $v = 332955193$ ($\text{Lat: } 13.047304^\circ\text{N}, \text{Lng: } 77.591864^\circ\text{E}$).
- **Graph Topology:** Edge exists directly in `G` (`G.has_edge(u, v) == True`). Key 0 attributes: `highway: trunk`, `name: Bellary Road`, `oneway: True`, `bridge: yes`.
- **Topological Cause of Gap:** This segment corresponds to the access-controlled elevated expressway between Yelahanka and the Hebbal flyover approach. Because there are no at-grade cross-streets or intermediate signalized junctions along this 5 km elevated structure, standard OSMnx graph simplification collapsed the non-junction nodes into a single edge connecting the entry ramp to the Hebbal approach.
- **Physical Distance Integrity:** In `routing/algorithms.py`, `calc_route_distance()` accesses `min(float(d.get("length", 1.0)) for d in edge_data.values())`. The engine accumulated the true road length of **$4,973.21\text{ m}$**, not the $4,897.55\text{ m}$ straight-line chord. Physical distance calculations are **100% accurate**.
- **Geometry Attribute:** The edge contains a complete `shapely.geometry.linestring.LineString` consisting of **68 coordinate pairs** capturing the subtle curves of the highway.
- **Visualization Defect Identified:** In `experiments/evaluate_route_quality.py`, route coordinates were exported as:
  ```python
  prim_coords = [[round(G.nodes[n]["y"], 6), round(G.nodes[n]["x"], 6)] for n in primary_route]
  ```
  The script exported only node endpoints, discarding the internal 66 vertices of the `LineString`. When rendered in Matplotlib (`generate_route_visualizations.py`) and Leaflet.js, the visualizer drew a straight line between Yelahanka and Hebbal, clipping across terrain bends. The route is physically and topologically continuous, but visually abstracted.

#### 2. OD_04 (Whitefield to Marathahalli): The 605.62 m Gap on Varthur Road
- **Node Pair:** $u = 845778275 \to v = 12000439030$.
- **Graph Topology:** Edge exists directly. Highway: `primary`, name: `Varthur Road`.
- **Edge Length:** $605.62\text{ m}$ (matches Euclidean chord because Varthur Road runs in a nearly straight east-west tangent).
- **Geometry Attribute:** Valid `LineString` with 11 vertices. Distance calculation is exact. Visualization draws a straight segment that closely matches reality due to the straight road corridor.

#### 3. OD_06 (Jayanagar to Malleshwaram): The 262.56 m Gap on 7th Main Road
- **Node Pair:** $u = 302493094 \to v = 249075661$.
- **Graph Topology:** Edge exists directly. Highway: `residential`, name: `7th Main Road`.
- **Edge Length:** Stored length is $262.71\text{ m}$; chord distance is $262.56\text{ m}$.
- **Geometry Attribute:** Valid `LineString` with 4 shape points. Fully connected.

#### 4. OD_01 (BNMIT to MG Road): The 275.39 m Gap vs. 375.69 m True Length
- **Node Pair:** $u = 2227928339 \to v = 1837408670$.
- **Graph Topology:** Edge exists directly. Highway: `residential`.
- **Physical Distance Accuracy:** The straight chord distance between nodes is $275.39\text{ m}$, whereas the true road length is **$375.69\text{ m}$** (a $+36.4\%$ curvature expansion).
- **Audit Verification:** The routing engine correctly accumulated the full $375.69\text{ m}$ edge length into the primary route distance. The edge contains a 9-point `LineString` tracking curved residential layout geometry. The visualization clipped this curve into a straight chord.

#### 5. OD_12 (Frazer Town to Shivajinagar): The 180.49 m Gap on Saunders Road
- **Node Pair:** $u = 7617898612 \to v = 12139153741$.
- **Graph Topology:** Edge exists directly. Highway: `tertiary`, name: `Saunders Road`. Stored length: $180.74\text{ m}$. Geometry contains 6 shape points. Fully connected.

### 1.3 Audit Verdict on Route Geometry
1. **Network Connectivity:** **PASSED.** All 5 routes are genuinely, topologically connected through directed graph edges. No disconnected hops, phantom edges, or coordinate teleports exist.
2. **Distance Calculation:** **PASSED.** Physical distance and impedance calculations strictly use OSM edge `length` attributes, never straight-line chord approximations.
3. **Visualization Fidelity:** **DOCUMENTED DEFECT (LOW SEVERITY).** The visualization pipeline failed to unpack `edge['geometry'].coords`, rendering straight lines between junction nodes. This does not impact any numerical findings, benchmark tables, or routing decisions, but represents a graphic rendering simplification.

---

## 2. Independent Verification of Experimental Results

The auditor recalculated all primary and alternative route metrics directly from the raw data files (`route_quality_evaluation.json`, 25 corridors; `route_quality_evaluation.csv`, 96 rows) using independent statistical scripts.

### 2.1 Primary Route Benchmark Recalculation (25 Metropolitan Corridors)

| Metric | Raw Recalculated Value | Published Table (`route_quality_tables.md`) | Executive Summary (`phase_11_final_report.md`) | Audit Evaluation |
| :--- | :---: | :---: | :---: | :---: |
| **Total Physical Distance** | **$191.19\text{ km}$** | $191.2\text{ km}$ | $191.2\text{ km}$ | **VERIFIED (Exact Match)** |
| **Mean Primary Distance** | **$7.647\text{ km}$** | $7.65\text{ km}$ | $7.65\text{ km}$ | **VERIFIED (Exact Match)** |
| **Mean Impedance Cost** | **$9,135.62\text{ units}$** | $9,135.62\text{ units}$ | $9,135.62\text{ units}$ | **VERIFIED (Exact Match)** |
| **Aggregate Cost / Dist Ratio** | **$1.1946\text{ units/m}$** | $1.195\text{ units/m}$ | **$1.218\text{ units/m}$** | **DISCREPANCY (Report Error)** |
| **Mean of Corridor Ratios** | **$1.2240\text{ units/m}$** | Not reported | **$1.218\text{ units/m}$** | **DISCREPANCY (Report Error)** |
| **Mean Arterial Exposure** | **$13.84\%$** | $13.84\%$ | **$18.4\%$** | **DISCREPANCY (Report Error)** |
| **Mean Collector Exposure** | **$37.13\%$** | $37.13\%$ | **$31.2\%$** | **DISCREPANCY (Report Error)** |
| **Mean Residential Exposure**| **$44.24\%$** | $44.24\%$ | **$50.4\%$** | **DISCREPANCY (Report Error)** |
| **Mean Total Maneuvers** | **$29.48\text{ turns}$** | $29.48\text{ turns}$ | Not reported | **VERIFIED (Exact Match)** |
| **Mean Sharp Maneuvers** | **$21.44\text{ turns}$** | $21.44\text{ turns}$ | Not reported | **VERIFIED (Exact Match)** |
| **Mean Turn Penalty Cost** | **$600.32\text{ units}$** | $600.3\text{ units}$ | Not reported | **VERIFIED (Exact Match)** |

#### Detailed Finding on Report Discrepancy:
In `phase_11_final_report.md` Section 1, Item 1 (lines 20–21), the executive summary claims:
> *"diverged from physical distance by a mean factor of 1.218 cost units per meter... (primary routes averaged 18.4% Arterial, 31.2% Collector, and 50.4% Residential/Local streets)."*
- The raw data and `route_quality_tables.md` prove that the true aggregate ratio is **$1.195\text{ units/m}$** (or mean of ratios **$1.224\text{ units/m}$**), and true road composition is **$13.84\%$ Arterial, $37.13\%$ Collector, and $44.24\%$ Residential**.
- The numbers in `phase_11_final_report.md` are uncorrected draft figures and must be aligned with `route_quality_tables.md` and the raw JSON.

### 2.2 Perpendicular-Offset Alternative Route Benchmark Recalculation (56 Surviving Routes)

| Metric | Raw Recalculated Value | Published Table (`route_quality_tables.md`) | Audit Evaluation |
| :--- | :---: | :---: | :---: |
| **Surviving Valid Alternatives** | **56 routes** (across 22 corridors) | 56 routes (across 22 corridors) | **VERIFIED** |
| **Corridors with 0 Surviving Alts** | **3 corridors** (OD_04, OD_15, OD_23) | 3 corridors (OD_04, OD_15, OD_23) | **VERIFIED** |
| **Mean Distance Detour Ratio** | **$1.0460\times$** ($+4.60\%$) | $1.0460\times$ | **VERIFIED (Exact Match)** |
| **Mean Impedance Cost Detour** | **$1.0993\times$** ($+9.93\%$) | $1.0993\times$ | **VERIFIED (Exact Match)** |
| **Mean Shared-Edge Overlap** | **$49.61\%$** | $49.61\%$ | **VERIFIED (Exact Match)** |
| **Mean Arterial Exposure** | **$11.69\%$** | $11.69\%$ | **VERIFIED (Exact Match)** |
| **Mean Residential Exposure**| **$53.84\%$** | $53.84\%$ | **VERIFIED (Exact Match)** |
| **Mean Total Maneuvers** | **$36.30\text{ turns}$** | $36.30\text{ turns}$ | **VERIFIED (Exact Match)** |

### 2.3 Yen's KSP Re-Benchmarking in Phase 11
- In `experiments/evaluate_route_quality.py` lines 401–403, Yen's KSP ($K=4$) was executed **strictly for the 5 case-study corridors** (`OD_01`, `OD_04`, `OD_06`, `OD_12`, `OD_15`), evaluating **15 alternative candidates**.
- Recalculated results from `route_quality_evaluation.json`:
  - Exactly **2 out of 15** alternatives survived the $\le 70\%$ overlap filter (both in OD_12 Frazer Town).
  - Mean shared edge overlap across the 15 alternatives was **$90.70\%$**.
- **Discrepancy in `phase_11_final_report.md`:** Line 25 states: *"Under a practical 70% overlap cap, 97.3% of Yen alternatives were rejected (only 2 out of 75 survived)... average overlap of 93.23%."*
- **Audit Assessment:** The author quoted the **Phase 10** 25-corridor benchmark (75 alternatives, 93.23% overlap) without clarifying that in Phase 11's route quality dataset, Yen was only re-run on the 5 case studies (15 alternatives, 90.70% overlap). The report must explicitly distinguish the Phase 10 city-wide benchmark from the Phase 11 case-study runs.

---

## 3. Parameter Sensitivity Analysis Audit

The auditor audited the sensitivity script (`experiments/evaluate_parameter_sensitivity.py`) and raw dataset (`sensitivity_analysis.json`, 8 configurations across 5 corridors = 40 runs).

### 3.1 Parameter Isolation and Experimental Confound
The audit verified whether each configuration modified ONLY the intended parameters:
1. **C0_Baseline:** Production defaults (Main 1.5, Inner 0.9, Service 0.9, Bridge 0.8, Roundabout 0.95, Sharp 25, Mod 8).
2. **C1_Neutral_Roads:** Multipliers set to 1.0. Intended baseline.
3. **C2_Aggressive_Inner:** Main 2.5, Inner 0.75, Service 0.8. Properly isolated.
4. **C3_Extreme_Highway_Aversion:** Custom dictionary penalizing trunks/motorways. Properly isolated.
5. **C4_Zero_Turn_Penalty:** `turn_sharp = 0.0`, `turn_moderate = 0.0`. All other parameters held at baseline. **Properly isolated.**
6. **C5_High_Turn_Penalty:** `turn_sharp = 60.0`, `turn_moderate = 25.0`. All other parameters held at baseline. **Properly isolated.**
7. **C6 & C7 (Flyover Modifiers) — METHODOLOGICAL CONFOUND IDENTIFIED:**
   - In C6: `bridge_multiplier = 1.0` AND `roundabout_multiplier = 1.0` were altered together.
   - In C7: `bridge_multiplier = 1.5` AND `roundabout_multiplier = 1.2` were altered together.
   - **Audit Finding:** C6 and C7 introduced compound parameter variations by simultaneously altering vertical grade separation (flyover) and horizontal junction topology (roundabouts).

### 3.2 Verification of the OD_15 Arterial Reduction (82.05% $\to$ 6.48%) and Alternative Route Emergence
The report claimed that under C7, OD_15 (Yelahanka to Hebbal) arterial exposure plummeted from **82.05% to 6.48%**, and surviving alternatives surged from **0 to 3**.
- **Auditor's Controlled Test:** To prove whether this was caused by the bridge modifier or the unintended roundabout modifier, the auditor executed a controlled run in scratch script `audit_c7_od15.py` with `bridge_multiplier = 1.5` but keeping `roundabout_multiplier = 0.95` (baseline).
- **Results:**
  - Route cost: $12,072.20$ (Identical to C7).
  - Arterial share: **$6.48\%$** (Collector: $70.98\%$, Residential: $22.55\%$).
  - Surviving alternatives: **3 valid alternatives** (Detours: 1.125x, 1.139x, 1.194x; Overlaps: 59.3%, 58.6%, 69.6%).
- **Causal Mechanism Verified:**
  - The 4.97 km uninterrupted elevated section of Bellary Road (Edge $12553535777 \to 332955193$) carries the tag `bridge=yes` in OpenStreetMap.
  - In Baseline (C0), `bridge_multiplier = 0.8` discounted this segment to $0.8 \times 4973 = 3,978.5\text{ cost units}$, artificially making the elevated trunk road cheaper than surface streets.
  - In C7, `bridge_multiplier = 1.5` increased the segment cost to $1.5 \times 4973 = 7,460.0\text{ cost units}$ ($+87.5\%$).
  - This forced the primary path off the elevated highway onto surface collector roads (Jakkur Main Road, Kempapura Road, Kanaka Nagar), expanding primary distance from $8.67\text{ km}$ to $10.82\text{ km}$.
  - The expanded primary distance widened the 1.20 detour cap from $10.40\text{ km}$ to **$12.98\text{ km}$**, allowing parallel surface routes through Amrutahalli and Byatarayanapura (which were previously rejected under the 10.40 km cap) to survive the filter!
- **Verdict:** The claimed result is **genuinely caused by the bridge parameter change**, and the roundabout parameter had zero effect. However, bundling the two parameters was an experimental design flaw.

### 3.3 Misattribution of Sharp Turn Surge Under Zero Turn Penalty (C4)
In `parameter_sensitivity_report.md` Section 4.1 line 73:
> *"In OD_01, the number of sharp turns increases from 33 to 54 turns (+63.6%)."*
And in `phase_11_final_report.md` line 93:
> *"Removing turn penalties ($\tau = 0$) increased sharp turns by +63.6%..."*
- **Auditor's Data Inspection:**
  - For **OD_01**: Baseline sharp turns = 35; C4 sharp turns = 39 (+11.4%). Total turns: 48 $\to$ 52.
  - For **OD_06**: Baseline sharp turns = 38; C4 sharp turns = 62 (**+63.15%**). Total turns: 50 $\to$ 78 (**+56.0%**).
- **Audit Verdict:** The report author **misattributed the OD_06 sharp turn surge (+63.2%) to OD_01**. The claim is true for OD_06, but false for OD_01. This citation error must be corrected in the text.

---

## 4. Runtime Fairness and Cross-Phase Distinctions

The auditor examined the runtime variability protocol (`experiments/evaluate_runtime_variability.py`, 10 corridors, 5 repetitions for fast algorithms, 3 repetitions for Yen KSP).

### 4.1 Timing Boundary Audit
- **Dijkstra, Admissible A*, Aggressive A*:** Timed strictly around `two_wheeler_astar()` using `time.perf_counter()`. Snap nodes snapped once outside timing block.
- **Yen's KSP:** Timed strictly around `yen_ksp_two_wheeler()`. Snap nodes snapped once outside timing block.
- **Perpendicular Offset:** Timed around `build_split_route_candidates(from_lat, from_lng, to_lat, to_lng)`.
  - **Identified Asymmetry:** `build_split_route_candidates()` executes nearest-node snapping for the origin, destination, and all 6–12 lateral split waypoints **inside the timed function block**.
  - **Impact on Fairness:** This timing boundary is slightly conservative against Perpendicular Offset (Offset carries ~10–15 ms of spatial snapping overhead that Yen and Dijkstra do not). Despite this slight handicap, Offset demonstrated massive speedups on long corridors, validating that the speedup is robust.

### 4.2 Cross-Phase Runtime Disentanglement

| Dimension | Phase 9 Runtime Experiment | Phase 10 Runtime Experiment | Phase 11 Runtime Experiment |
| :--- | :--- | :--- | :--- |
| **Objective** | Validate heuristic admissibility & state reduction | Alternative diversity vs. Yen's KSP | Multi-repetition variance & stability ($\mu, \sigma, \text{CV}$) |
| **Corridor Suite** | 10 metropolitan corridors | 25 metropolitan corridors | 10 representative corridors (Short, Med, Long) |
| **Repetitions** | 1 run per corridor | 1 run per corridor | **5 runs** (Dijkstra, A*, Offset), **3 runs** (Yen) |
| **Dijkstra Mean** | $1,927.23\text{ ms}$ | Not evaluated | **$1,034.59\text{ ms}$** ($\sigma = 948.9\text{ ms}$) |
| **Admissible A* Mean**| $599.07\text{ ms}$ | Not evaluated | **$341.37\text{ ms}$** ($\sigma = 298.1\text{ ms}$) |
| **A* vs. Dijkstra Speedup** | **$3.22\times$** | Not evaluated | **$3.03\times$** (Ratio of Means) / **$3.24\times$** (Mean of Ratios) |
| **Offset Routing Mean**| Not evaluated | $13,736.76\text{ ms}$ ($13.74\text{ s}$) | **$11,790.46\text{ ms}$** ($11.79\text{ s}$) |
| **Yen's KSP Mean** | Not evaluated | $86,903.66\text{ ms}$ ($86.90\text{ s}$) | **$45,922.79\text{ ms}$** ($45.92\text{ s}$) |
| **Offset vs. Yen Speedup** | Not evaluated | **$6.33\times$** | **$3.90\times$** (Ratio of Means) |

### 4.3 Discrepancies and Unsupported Speedup Claims
1. **The Claimed $3.78\times$ Speedup for Admissible A*:**
   - In `phase_11_final_report.md` line 35 and `runtime_evaluation_report.md` line 59:
     *"Standard Admissible A* achieved a $3.78\times$ speedup over uniform-cost Dijkstra..."*
   - **Audit Finding:** This claim is **unsupported by any raw dataset**. In Phase 11 Table 2, the speedup is explicitly **$3.03\times$** (ratio of suite means: $1,034.6 / 341.4$) or **$3.24\times$** (mean of corridor speedups). In Phase 9, it was $3.22\times$. The figure $3.78\times$ is an uncited typographical error.
2. **Conflation of Phase 10 and Phase 11 Offset vs. Yen Runtimes:**
   - `phase_11_final_report.md` line 36 copied Phase 10's single-run numbers ($13.74\text{ s}$, $86.90\text{ s}$, $6.33\times$) rather than reporting Phase 11's multi-repetition benchmark results ($11.79\text{ s}$, $45.92\text{ s}$, $3.90\times$).
3. **Overstated Speedup on Trips >8 km:**
   - In `runtime_evaluation_report.md` line 74:
     *"Across metropolitan trips (>8 km), Perpendicular Offset achieves a 6.33x to 15.2x runtime speedup over Yen's KSP."*
   - **Audit Finding:** This ignores the empirical data for OD_03 ($2.13\times$), OD_04 ($0.81\times$), OD_09 ($3.84\times$), and OD_15 ($0.72\times$). In corridors with extreme physical bottlenecks (OD_04) or single linear spines (OD_15), Yen terminated **faster** than Offset because spur paths failed immediately, whereas Offset executed all 12 candidate legs. The claim of uniform 6.33x–15.2x speedup on all trips >8 km is demonstrably false.

---

## 5. Academic Claim Review and Publication Guidance

In accordance with strict scientific peer-review standards (e.g., IEEE Transactions on Intelligent Transportation Systems), the auditor reviewed all academic assertions:

### 5.1 Equating Turn Reduction with Improved Safety
- **Problematic Passages:** `parameter_sensitivity_report.md` describes zero-turn routes as *"practically unrideable and hazardous for two-wheelers"* and claims turn penalties *"conclusively validate"* safety benefits.
- **Academic Requirement:** Turn penalties represent a **computational maneuver stabilization heuristic** designed to penalize frequent direction changes and suppress erratic residential zig-zags ("alley thrashing"). Unless supported by empirical crash data, conflict analysis, or rider eye-tracking studies, the paper must **not claim improved vehicular safety or accident reduction**.
- **Required Framing:** Describe turn penalties as minimizing *navigational complexity*, *rider cognitive workload*, and *maneuver friction*.

### 5.2 Impedance Cost vs. Travel Time
- **Audit Verification:** Phase 11 documents prominently feature formal disclaimers declaring that impedance cost is a synthetic optimization metric and not travel time.
- **Academic Requirement:** Ensure that all colloquial references to "faster routes", "time savings", or "trip duration" are eliminated when discussing impedance costs. Maintain strict adherence to "lower impedance" or "reduced traversal cost".

### 5.3 Claims of Universal Algorithmic Superiority
- **Problematic Passages:** Claims that Perpendicular Offset is uniformly superior to Yen's KSP across all operational dimensions.
- **Academic Requirement:**
  1. Acknowledge that Yen's KSP guarantees exact rank-ordered shortest paths in cost space, whereas Perpendicular Offset is a heuristic via-node sampling method.
  2. Acknowledge that in corridors with narrow choke points or strict linear topology (OD_04, OD_15), Yen's KSP executes faster than Perpendicular Offset.
  3. Acknowledge that filtering in Perpendicular Offset is pairwise against the primary route ($\text{Overlap}(P_{\text{primary}}, P_k) \le 0.70$), and mutual overlap between accepted alternatives is unconstrained except for duplicate suppression.

### 5.4 Distinction Between Empirical Calibration and Engineering Assumptions
- **Academic Requirement:** All parameter values ($1.5\times$ main road, $0.9\times$ inner road, $0.8\times$ bridge, $25.0$ sharp turn, $70\%$ overlap, $1.20$ detour cap) must be formally declared in the methodology section as **engineering design heuristics**. State clearly that empirical calibration via commuter GPS trajectory logs and driver preference modeling remains future work.

---

## 6. Comprehensive Defect Matrix and Required Corrections

| Item ID | Category | Defect Description | Severity | Impact on Project | Required Correction |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **DEF-01** | Geometry / Vis | Route coordinate export omitted intermediate `LineString` vertices; maps render straight-line chords. | **Low** | Graphical abstraction only; numerical calculations are 100% accurate. | In future visualization scripts, unpack `edge_data['geometry'].coords` when exporting polyline coordinates. |
| **DEF-02** | Data / Reporting | `phase_11_final_report.md` cited draft numbers: 1.218 cost/m ratio and 18.4% / 31.2% / 50.4% road classes. | **Medium** | Internal inconsistency between executive report and data tables. | Update `phase_11_final_report.md` Section 1 to cite **$1.195\text{ units/m}$** and **$13.84\%$ Arterial / $37.13\%$ Collector / $44.24\%$ Residential**. |
| **DEF-03** | Data / Reporting | Conflation of Phase 10 (75 alts, 93.23% overlap) with Phase 11 case studies (15 alts, 90.70% overlap) in report text. | **Medium** | Confusion regarding which dataset is being discussed. | Clarify in `phase_11_final_report.md` that 75 alts refers to Phase 10 city-wide benchmark, while Phase 11 evaluated 15 alts across 5 case studies. |
| **DEF-04** | Experimental | Sensitivity configurations C6 and C7 bundled bridge multiplier and roundabout multiplier. | **Medium** | Minor experimental confound; bridge effect was independently isolated and verified. | Document in `parameter_sensitivity_report.md` that bridge and roundabout modifiers were tested as a compound junction configuration. |
| **DEF-05** | Reporting / Citation | Sharp turn surge (+63.2%) under C4 misattributed to OD_01 instead of OD_06. | **Low** | Factually incorrect corridor citation in text. | Change "OD_01" to **"OD_06"** in `parameter_sensitivity_report.md` Section 4.1. |
| **DEF-06** | Benchmarking | Claim of $3.78\times$ Admissible A* speedup over Dijkstra is unsupported by raw data ($3.03\times$). | **Medium** | Overstated speedup in narrative summaries. | Correct $3.78\times$ to **$3.03\times$** (suite mean) / **$3.24\times$** (corridor mean) in final report and runtime report. |
| **DEF-07** | Benchmarking | Claim of uniform 6.33x–15.2x speedup on trips >8 km contradicts OD_04 (0.81x) and OD_15 (0.72x). | **Medium** | Overstated operational superiority claim. | Revise text to reflect that Offset achieves up to $14.4\times$ speedup on grid networks, but Yen is faster on linear choke-points. |
| **DEF-08** | Academic Claims | Equating turn reduction with traffic safety and accident prevention. | **Medium** | Vulnerable to rejection in academic peer review. | Reframe turn penalties as minimizing maneuver friction and navigational complexity rather than proven safety. |

---

## 7. Acceptance Recommendation and Final Verdict

### Audit Verdict: **ACCEPTED WITH CONDITIONAL REVISIONS**

The core technical work of Phase 11 is of high quality:
- The graph geometry is intact and fully connected.
- Route metrics and alternative generation algorithms are mathematically rigorous.
- Parameter sensitivity confirmed the mechanical behavior of turn penalties and road multipliers.
- Runtime variability experiments demonstrated high algorithmic stability ($\text{CV} \le 3.5\%$).
- Production code files and previous phase archives remain clean and unmodified.

The issues identified during this audit are strictly confined to **documentation discrepancies, numerical citations in narrative text, and academic claim tempering**. No production code modifications, graph re-compilations, or full experiment re-runs are necessary.

### Conditions for Final Sign-Off:
1. Update `phase_11_final_report.md` to correct the road-class percentages, cost-per-meter ratio, and A* speedup ratio.
2. Update `parameter_sensitivity_report.md` to fix the OD_01 vs. OD_06 turn count attribution and note the C6/C7 compound parameter bundling.
3. Update `runtime_evaluation_report.md` to remove the unsupported $3.78\times$ speedup claim and temper the >8 km speedup generalization.
4. Maintain read-only restrictions and await user approval before proceeding to Phase 12.
