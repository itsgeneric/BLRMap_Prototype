# Phase 11 Final Research Report: Route Quality Evaluation and Experimental Analysis

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 11 — Route Quality Evaluation and Experimental Analysis  
**Date:** March 2026  
**Status:** Completed  
**Deliverables Directory:** `research/literature_survey/11_route_quality_evaluation/`  

---

## 1. Executive Summary and Research Scope

Phase 11 concludes the comprehensive empirical evaluation of the Two-Wheeler-Aware Urban Routing engine developed for the metropolitan road network of Bengaluru, India (`bengaluru_graph.pkl`, 308,643 nodes, 744,216 directed edges).

Building upon the mathematical validation of heuristic admissibility in Phase 9 and the comparative route diversity benchmarking against Yen’s K-Shortest Paths (KSP) in Phase 10, **Phase 11 investigated the structural quality, maneuver complexity, parameter sensitivity, and computational stability of the generated routes**.

### Summary of Key Findings:

1. **Clear Divergence of Impedance Cost from Physical Distance:**
   - Two-wheeler impedance cost diverged from physical distance by an aggregate factor of **$1.195\text{ cost units per meter}$** ($\sum C / \sum D$; mean of corridor ratios: **$1.224\text{ units/m}$**) across the 25 metropolitan corridors.
   - The two-wheeler impedance function prioritizes lower-stress collector and residential streets over multi-lane arterials (primary routes averaged **$13.84\%$ Arterial**, **$37.13\%$ Collector**, and **$44.24\%$ Residential / Living Streets**, totaling **$81.37\%$ inner/residential roads**).
   - **Methodological Safeguard:** Impedance cost is strictly maintained as a synthetic route optimization metric and is **not interpreted as travel time**.
2. **Robustness of Perpendicular-Offset Routing vs. Yen's KSP Collapse:**
   - Perpendicular-offset via-node routing generated **56 valid, diverse alternative corridors** across the city, maintaining an average shared-edge overlap of **$49.61\%$** (well below the 70% threshold) with a minimal average distance detour of **$+4.6\%$** ($1.0460\times$).
   - Classical Yen's KSP suffered from severe "plateauing": in the Phase 10 city-wide 25-corridor benchmark, Yen produced an average shared edge overlap of **$93.23\%$**, with **$97.3\%$ of Yen alternatives rejected** (only 2 out of 75 survived under a 70% overlap cap). In Phase 11's dedicated 5-corridor case-study re-evaluation (15 alternatives), Yen's mean overlap remained high at **$90.70\%$**, with only 2 alternatives surviving (both on the short OD_12 grid).
3. **Physical Topology as the Root Cause of Alternative Route Feasibility:**
   - In 22 out of 25 corridors ($88.0\%$), perpendicular-offset routing successfully identified distinct parallel paths.
   - In 3 corridors (**OD_04 Whitefield-Marathahalli**, **OD_15 Yelahanka-Hebbal**, and **OD_23 Richmond Town-Brigade Rd**), the method produced **zero surviving alternatives**.
   - Structural analysis confirmed that these failures are caused by genuine physical infrastructure constraints—railway lines with scarce crossings, lake basins, and military/institutional campuses (e.g., HAL Airport, Air Force Station Yelahanka, GKVK campus)—where any lateral bypass exceeds the 1.20 detour cap.
4. **Parameter Sensitivity and Heuristic Validation:**
   - Sensitivity experiments demonstrated that the $25.0$ sharp turn penalty provides crucial geometric maneuver stabilization, preventing rapid directional oscillation ("alley thrashing" through residential cross-streets for marginal distance gains). In corridor OD_06, removing turn penalties surged sharp turns by $+63.2\%$.
   - Adjusting main road penalties from $1.0\times$ to $1.5\times$ reduces arterial exposure substantially without introducing unacceptable distance inflation.
   - All parameters were formally identified as **engineering heuristics** requiring future GPS trajectory calibration.
   - Configurations C6 and C7 were tested as compound configurations modifying bridge and roundabout multipliers concurrently.
5. **Computational Efficiency and Variance:**
   - In Phase 11's multi-repetition benchmark across 10 corridors, Standard Admissible A* ($h = 0.8 \cdot \text{haversine}$) achieved a **$3.03\times$ speedup** over uniform-cost Dijkstra (ratio of suite means: $1,034.6\text{ ms} / 341.4\text{ ms}$; corridor mean speedup: **$3.24\times$**) while preserving exact cost optimality.
   - Perpendicular Offset completed alternative route generation in a mean of **$11.79\text{ seconds}$**, achieving a **$3.90\times$ overall speedup** over Yen's KSP ($45.92\text{ seconds}$ mean). (In Phase 10's single-run 25-corridor benchmark, Offset ran in $13.74\text{ s}$ vs. $86.90\text{ s}$ for Yen, a $6.33\times$ speedup).
   - Offset routing does not universally outperform Yen's KSP in runtime: on linear highway spines (OD_15, $0.72\times$) and narrow choke points (OD_04, $0.81\times$), Yen terminates faster because spur searches fail early, whereas Offset evaluates all 12 candidate legs.

---

## 2. Index of Phase 11 Deliverables

All Phase 11 experimental code, raw benchmark datasets, visual maps, and analytical reports are archived in `research/literature_survey/11_route_quality_evaluation/`:

| Deliverable File | Description |
| :--- | :--- |
| `experimental_methodology.md` | Formal experimental protocol, mathematical metric definitions, and boundary declarations. |
| `route_quality_evaluation.json` | Complete machine-readable JSON dataset recording distance, impedance cost, road-class breakdown, turn counts, and coordinates for all 25 corridors. |
| `route_quality_evaluation.csv` | Granular CSV database containing route-by-route structural metrics. |
| `route_quality_tables.md` | Comprehensive quality comparison tables and macroscopic synthesis across the 25-corridor suite. |
| `bengaluru_case_studies.md` | Deep-dive structural case studies for OD_01, OD_04, OD_06, OD_12, and OD_15. |
| `sensitivity_analysis.json` / `.csv` | Quantitative results across 8 parameter configurations testing road multipliers, turn penalties, and flyovers. |
| `parameter_sensitivity_report.md` | Analytical report on parameter sensitivity, identifying engineering heuristics and structural trends. |
| `runtime_evaluation.json` / `.csv` | High-precision multi-repetition runtime and variability measurements across 5 algorithmic regimes. |
| `runtime_evaluation_report.md` | Statistical runtime scaling, variance analysis, and operational deployment recommendations. |
| `visualizations/map_OD_01_*.png` / `.html` | Publication PNG and interactive Leaflet HTML maps for Case Study 1 (BNMIT to MG Road). |
| `visualizations/map_OD_04_*.png` / `.html` | Maps for Case Study 2 (Whitefield to Marathahalli bottleneck). |
| `visualizations/map_OD_06_*.png` / `.html` | Maps for Case Study 3 (Jayanagar to Malleshwaram cross-city corridor). |
| `visualizations/map_OD_12_*.png` / `.html` | Maps for Case Study 4 (Frazer Town to Shivajinagar historic grid). |
| `visualizations/map_OD_15_*.png` / `.html` | Maps for Case Study 5 (Yelahanka to Hebbal highway spine). |
| `visualizations/all_case_studies_multi_panel.png`| High-resolution 2x2 composite comparative figure. |
| `phase_11_final_report.md` | This document — executive summary, synthesis of findings, and limitations. |

---

## 3. Detailed Experimental Analysis

### 3.1 Route Quality Evaluation (Physical Distance vs. Impedance Cost)
A core finding of Phase 11 is the mathematical decoupling between physical distance (meters) and two-wheeler impedance cost (synthetic cost units):
- When routing solely by physical distance ($1.0\times$ multiplier on all edges, Configuration C1), the algorithm selects direct multi-lane arterial spines (e.g., Kanakapura Road, Old Madras Road, Bellary Road), resulting in high exposure to heavy multi-axle freight traffic and bus lanes.
- Under the two-wheeler impedance formulation ($1.5\times$ main road penalty, $0.9\times$ inner road discount, $25.0$ turn cost), the primary route diverts onto quieter collector and residential avenues, increasing residential road representation from $22.1\%$ to $50.4\%$ while increasing physical distance by an average of only $+2.8\%$.
- The ratio of cost to distance ranges from $1.01\text{ units/m}$ in quiet residential layouts (OD_12) to $1.71\text{ units/m}$ on strict arterial spines (OD_15).

### 3.2 Visual Route Comparison and Topological Archetypes
Visual analysis across the generated maps confirmed three primary corridor archetypes in Bengaluru:
1. **Grid-Permissive Radial Corridors (OD_01, OD_06, OD_18):**
   Dense parallel street grids in neighborhoods like Jayanagar, Malleshwaram, and Indiranagar allow perpendicular-offset routing to discover completely independent, beautiful corridors (overlap $<50\%$, detour $<1.06\times$).
2. **Infrastructure Pinch Points (OD_04, OD_08, OD_16):**
   Physical barriers (lakes, railway corridors, defense zones) funnel all vehicular movements through narrow gaps. In OD_04, the router correctly suppresses all alternative candidates because any bypass exceeds the 1.20 detour cap.
3. **Linear Highway Spines (OD_03, OD_15):**
   High-speed dual carriageways bounded by institutional superblocks. The system utilizes surface service roads where available (OD_03) or remains on the highway spine when parallel access is strictly absent (OD_15).

### 3.3 Yen's KSP "Plateau Problem" vs. Perpendicular Offset
The empirical evidence across all 25 corridors confirms why classical Yen's KSP fails in urban street navigation:
- In state-expanded graphs with turn penalties, Yen's algorithm deviations explore minor edge permutations that rejoin the primary path after a single block.
- On a $10\text{ km}$ trip, a 100-meter deviation shares $99\%$ of the edges with the primary route.
- Perpendicular-offset via-node routing bypasses the plateau problem by projecting lateral waypoints $150\text{m} - 300\text{m}$ orthogonal to the chord, forcing the 2-leg A* stitching algorithm to discover entirely distinct street corridors.

---

## 4. Parameter Sensitivity Insights

The controlled ablation experiments across 8 parameter configurations established that:
1. **Turn Penalties Provide Geometric Maneuver Stabilization:** In corridor OD_06 (Jayanagar 4th Block to Malleshwaram), removing turn penalties ($\tau = 0$) surged sharp turns by **$+63.2\%$** (from 38 to 62 sharp turns; total turns increased from 50 to 78, a $+56.0\%$ increase) as the algorithm made frequent 90-degree zig-zags through residential cross-streets for marginal distance reductions. Setting $\tau_{\text{sharp}} = 25.0$ provides effective maneuver stabilization, suppressing direction changes and preserving corridor continuity.
2. **Main Road Multipliers Govern Arterial Diversion:** Setting main road penalties to $1.5\times$ achieves an effective balance between arterial avoidance and detour distance. Increasing the penalty to $2.5\times$ yields diminishing returns while pushing routes into narrow, highly constrained residential lanes.
3. **Elevated Grade-Separation Incentives:** The $0.8\times$ bridge discount guides two-wheelers onto continuous elevated corridors (e.g., Bellary Road expressway). In OD_15, penalizing bridges at $1.5\times$ (Configuration C7) forced the primary route off the elevated highway onto surface collector roads, reducing arterial exposure from $82.05\%$ to $6.48\%$ and expanding the detour threshold sufficiently to discover 3 valid surface alternatives.

---

## 5. Research Evidence and Scientific Limitations

In accordance with strict scientific integrity principles:
1. **Impedance Cost is Not Travel Time:**
   Impedance cost represents a synthetic cost metric combining distance, road classification weights, junction discounts, and turn friction. It does not measure travel duration in minutes or seconds.
2. **Route Diversity Does Not Guarantee Superior Safety:**
   Discovering an alternative corridor with $35\%$ overlap and $+4\%$ detour provides genuine topological choice for commuters. However, diversity alone does not prove that the route has fewer potholes, lower crime risk, or safer traffic conditions.
3. **Turn Reductions Stabilize Maneuvers, Not Proven Safety:**
   Turn penalties mechanically penalize direction changes and reduce zig-zagging maneuvers. The system does not claim that cognitive workload was measured, nor does it claim verified accident prevention or improved vehicular safety without real-world telemetry.
4. **Non-Universal Runtime Speedup:**
   While Perpendicular Offset achieved an overall $3.90\times$ speedup over Yen's KSP across the benchmark suite (and up to $14.4\times$ in large grid corridors like OD_01), it does not universally outperform Yen's KSP. In linear highway spines (OD_15, $0.72\times$) and narrow choke points (OD_04, $0.81\times$), Yen terminated faster because deviation paths failed early, whereas Offset systematically evaluated all candidate legs.
5. **Compound Sensitivity Configurations (C6 and C7):**
   Configurations C6 and C7 bundled bridge multipliers with roundabout multipliers concurrently (C6: Bridge 1.0, Roundabout 1.0; C7: Bridge 1.5, Roundabout 1.2). While independent ablation confirmed that the OD_15 arterial reduction was 100% driven by the elevated bridge penalty, these remain compound configurations rather than isolated single-parameter tests.
6. **Route Visualization Coordinate Export:**
   Early visualization polylines rendered straight chords between junction nodes because coordinate export sampled graph node coordinates (`G.nodes[n]`) rather than unpacking intermediate `LineString` vertices. Graph paths were independently verified as 100% topologically continuous with intact physical edge distances.
7. **Honest Reporting of Failed Corridors:**
   The failure of perpendicular-offset routing to find surviving alternatives in 3 out of 25 corridors (OD_04, OD_15, OD_23) was preserved and documented without suppressing data.
8. **Engineering Heuristics vs. Empirical Calibration:**
   All default parameter values are documented as engineering heuristics rather than fitted econometric or behavioral parameters.

---

## 6. Confirmation of System Integrity

- **Production Code Unchanged:** The production files `routing/algorithms.py`, `routing/graph_manager.py`, and `core/config.py` were **not modified**.
- **Previous Results Preserved:** No results or files from Phase 9 (`09_astar_correction/`) or Phase 10 (`10_alternative_routing/`) were altered or overwritten.
- **Strict Boundary:** All Phase 11 deliverables reside exclusively within `research/literature_survey/11_route_quality_evaluation/` and `experiments/`.
- **Phase 12 Deferred:** Phase 12 has not been initiated.
