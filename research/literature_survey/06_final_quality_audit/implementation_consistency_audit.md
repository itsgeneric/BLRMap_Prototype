# Technical Implementation Consistency Audit

**Project Title:** GIS-Based Intelligent Navigation and Path Optimization Framework: Self-Calibrating, Two-Wheeler-Aware Routing for Bengaluru  
**Stage:** Final Academic Quality Audit  
**Document:** `research/literature_survey/06_final_quality_audit/implementation_consistency_audit.md`  
**Date:** 2026-11-03  
**Auditor:** Lead Technical Implementation Auditor  
**Inspected Codebase Files:** `routing/algorithms.py`, `core/config.py`, `api_server.py`, `routing/graph_manager.py`, `router.py`  

---

## 1. Executive Summary

This document presents a rigorous, line-by-line technical consistency audit comparing the literature review claims, proposed methodologies, and the actual implementation in the project codebase. The goal is to identify exact matches, partial alignments, implementation omissions, and physical unit discrepancies so that no false claims are made in the final IEEE conference paper.

### Audit Summary:
* **Fully Implemented & Consistent:** Goal-directed A\* heuristic admissibility, dynamic state-expanded search tracking `(prev_node, curr_node)`, spherical bearing deflection turn calculations, inverted road-class penalty mappings, bridge/flyover bonus handling, roundabout damping, dynamic congestion node impedance, and perpendicular offset waypoint geometry.
* **Discrepancies & Gaps Flagged:**
  1. *Junction Filtering Discount Disconnect (Critical):* Defined as helper functions in `algorithms.py`, but never invoked in `two_wheeler_astar` or `api_server.py`.
  2. *Turn Penalty Units Discrepancy (Major):* Code applies turn penalties in distance units (meters of virtual detour), whereas literature review text described them in time units (seconds).
  3. *Alternative Route Sharing Filter Missing (Major):* Detour tolerance is enforced ($\le 1.20$), but the 70% edge-sharing filter ($\gamma \le 0.70$) is not calculated in `build_split_route_candidates`.
  4. *API Endpoint Gaps (Major):* `build_split_route_candidates` is not exposed via FastAPI in `api_server.py`, and `/dynamic-route` does not accept customization query parameters (`main_road_penalty`, `inner_road_multiplier`).

---

## 2. Comprehensive Traceability Matrix: Literature $\to$ Methodology $\to$ Codebase $\to$ Experiment

The table below maps every literature concept to its proposed mathematical methodology, actual codebase location, implementation status, and required experimental validation:

| Literature Foundation | Proposed Methodology | Actual Codebase Component & Line Reference | Current Implementation Status | Required Experimental Benchmark |
| :--- | :--- | :--- | :--- | :--- |
| **[1] Promraksa et al. (2022)**<br>Microscopic queue-filtering clearances at signalized junctions | Multi-lane junction filtering discount discounting traversal time/cost by compounding factor ($0.985^{N}$, floor $0.85$) | `routing/algorithms.py`:<br>• `count_filterable_junctions` (L. 169–208)<br>• `apply_filtering_discount` (L. 211–225)<br>• `FILTER_DISCOUNT_PER_JUNCTION = 0.985`<br>• `FILTER_DISCOUNT_FLOOR = 0.85` | **Partially Implemented (Detached Helper):** Functions exist, but are **never invoked** inside `two_wheeler_astar` or `api_server.py`. | **Experiment 1:** Must wire filtering discount into duration evaluation to compare travel time savings on multi-lane signalized corridors. |
| **[2] Kotagi et al. (2020)**<br>Non-lane lateral placement on Indian roads | Inverted road hierarchy penalizing wide congested arterials and promoting local streets | `core/config.py` (L. 61–77):<br>`TWO_WHEELER_ROAD_PENALTIES`<br>`routing/algorithms.py` (L. 231–258):<br>`build_two_wheeler_penalties` | **Fully Implemented:** Base penalties assign `motorway: 4.0`, `primary: 2.2`, `residential: 1.0`, `service: 0.9`. | **Experiment 1:** Benchmark road-class utilization distribution (% primary vs. % secondary/local). |
| **[3] Das & Maurya (2019)**<br>Motorcycle speed advantage in congested queues | Peak-hour arterial speed degradation and filtering speed curves | `routing/algorithms.py` (L. 261–343):<br>`two_wheeler_edge_cost`<br>`core/config.py`: `PEAK_HOUR_MULTIPLIER` | **Partially Implemented:** Static multipliers in place; dynamic time-of-day clock windowing not yet hooked into `api_server.py`. | **Experiment 1:** Peak vs. off-peak travel duration comparison under arterial queue states. |
| **[4] Fadilah et al. (2024)**<br>Rider queue avoidance & turn tolerance | Inner-road biased routing mode tolerating turns on secondary roads | `core/config.py` (L. 56–59):<br>`INNER_ROAD_BIASED_TYPES`<br>`routing/algorithms.py` (L. 245–249):<br>`inner_road_multiplier` | **Fully Implemented in Algorithms, Missing in API:** Multipliers exist in `build_two_wheeler_penalties`, but `api_server.py` does not expose them as query parameters. | **Experiment 1 & 2:** Evaluate path diversion onto secondary networks under varying inner road bias weights. |
| **[5] Asvial et al. (2020)**<br>Motorcycle routing on OSM; flaw: zero turn modeling | Two-wheeler routing on OSM with turn awareness and candidate diversification | `routing/algorithms.py`:<br>`two_wheeler_astar`<br>`bengaluru_roads_extended.graphml` | **Fully Implemented:** Direct baseline comparison against Asvial's turn-agnostic formulation. | **Experiment 1 & 2:** Benchmark turn count and travel time against turn-agnostic A\*. |
| **[6] Winter (2002)**<br>Turn costs require incoming edge tracking $(e_{in})$ | Search state tracking `state = (prev_node, curr_node)` in priority queue | `routing/algorithms.py` (L. 472–525):<br>`start_state = (None, start_node)`<br>`next_state = (current_node, next_node)`<br>`g_score[state]` | **Fully Implemented:** State expansion tracks incoming edge orientation without line graph memory allocation. | **Experiment 2:** Verify memory consumption and state expansion count vs. standard A\*. |
| **[7] Geisberger & Vetter (2011)**<br>Edge-based turn costs and discrete thresholds | Coordinate bearing deflection $\Delta \theta$ with discrete penalties ($30^\circ$, $60^\circ$) | `routing/algorithms.py` (L. 32–37, 105–163):<br>`_turn_angle`<br>`_turn_penalty`<br>`TURN_THRESHOLD_MODERATE = 30.0`<br>`TURN_THRESHOLD_SHARP = 60.0`<br>`TURN_PENALTY_MODERATE = 8.0`<br>`TURN_PENALTY_SHARP = 25.0` | **Fully Implemented (Unit Discrepancy):** Penalty is added in **meters of cost distance**, whereas text described it in seconds. | **Experiment 2:** Turn count and severity distribution (straight vs. moderate vs. sharp turns). |
| **[8] Delling et al. (2017)**<br>Decoupling topology from dynamic metric customization | Invariant OSM graph cached in RAM; dynamic edge penalties passed per query | `routing/graph_manager.py` (L. 100–133):<br>`bengaluru_graph.pkl` cached once;<br>`routing/algorithms.py`: runtime penalties | **Fully Implemented in Backend:** Graph topology loaded once; weights evaluated per request. | **Experiment 1 & 2:** Query latency benchmarking (<100 ms) across parameter updates. |
| **[9] Abraham et al. (2013)**<br>Alternative route criteria: limited sharing $\gamma$, bounded detour $\epsilon$ | Perpendicular offset via-nodes; candidate filtering by detour $\le 1.20$ and sharing $\le 70\%$ | `routing/algorithms.py` (L. 753–991):<br>`_offset_split_points`<br>`build_split_route_candidates`<br>`DETOUR_TOLERANCE = 1.20` | **Partially Implemented:** Offset generation and detour cap ($\le 1.20$) are implemented; **70% sharing filter is missing**; not exposed via API. | **Experiment 3:** Jaccard edge distance, edge overlap percentage ($\gamma$), and detour ratio ($\epsilon$). |
| **[10] Bast et al. (2016)**<br>Heuristic admissibility & Pareto complexity | Haversine lower bound divided by minimum penalty floor ($0.8$) | `routing/algorithms.py` (L. 23, 480–490):<br>`heuristic = haversine_m / MIN_PENALTY_FLOOR`<br>`MIN_PENALTY_FLOOR = 0.8` | **Fully Implemented:** Strict mathematical admissibility guaranteed ($\pi \le \text{dist}$). | **Experiment 2:** Heuristic optimality and search space expansion efficiency. |
| **[11] Lee et al. (2007)**<br>TRACLUS trajectory partitioning | Corridor-level traffic delay aggregation | Conceptual design; corridor grouping in test scripts | **Conceptual / Future Pipeline:** Used to inform corridor test design. | **Experiment 4:** Test corridor sequence selection. |
| **[12] Du et al. (2020)**<br>Recurrent vs. non-recurrent arterial congestion | Diurnal peak-hour congestion multipliers on radial corridors | `core/config.py`: peak windows defined; static multipliers in `algorithms.py` | **Partially Implemented:** Multipliers exist; automated clock-based trigger in API not active. | **Experiment 1:** Peak vs. off-peak commute scenarios. |
| **[13] Abbas et al. (2020)**<br>Dynamic edge weight modulation for traffic jams | Multiplicative penalty on incident edges of congested nodes | `routing/algorithms.py` (L. 311–316):<br>`if congested_nodes and (u in congested_nodes or v in congested_nodes): penalty *= 25.0` | **Fully Implemented:** Saturated nodes receive $25\times$ penalty, forcing dynamic bypass. | **Experiment 4:** Congested nodes avoided count and bypass detour ratio. |
| **[14] Boeing (2017)**<br>OSMnx street multigraph simplification | Ingestion and cleaning of Bengaluru road network | `routing/graph_manager.py` (L. 135–200):<br>`ox.load_graphml`, largest strongly connected component | **Fully Implemented:** `bengaluru_roads_extended.graphml` (50,000+ nodes) processed and cached. | **All Experiments:** Spatial road network substrate. |
| **[15] Luxen & Vetter (2011)**<br>OSRM profile routing on OSM | Vehicle-specific speed mapping and road suitability profiles | `core/config.py`: road classification dictionaries;<br>`routing/algorithms.py`: edge costing | **Fully Implemented:** Direct baseline comparison against OSRM default car profiles. | **Experiment 1:** Travel duration vs. OSRM car hierarchy baseline. |
| **[16] Kumar et al. (2025)**<br>Bengaluru congestion prediction baseline | Empirical bottleneck test corridors (Hosur Rd, Trinity Circle, Yeshwanthpur) | `api_server.py`: `/dynamic-route`<br>`tests/test_bengaluru_corridors.py` | **Implemented as Validation Testbed:** Kumar's corridors used as ground-truth bottleneck inputs. | **Experiment 4:** Saturated corridor bypass evaluation. |

---

## 3. In-Depth Analysis of Flagged Implementation Gaps

### Gap 1 (Critical): The Junction Filtering Discount Disconnect
* **Literature Claim:** The framework translates microscopic filtering clearances into macroscopic edge impedance via a compounding junction filtering discount for multi-lane approaches ($\ge 2$ lanes).
* **Codebase Reality:**
  - `count_filterable_junctions(graph, route)` (lines 169–208) accurately counts signalized multi-lane junctions along a completed path.
  - `apply_filtering_discount(traffic_seconds, filterable_junction_count)` (lines 211–225) computes `traffic_seconds * max(0.85, 0.985 ** count)`.
  - **The Disconnect:** Neither function is called inside `two_wheeler_astar` (which drives path selection) nor in `api_server.py` (which returns route duration).
  - Consequently, the A\* search does *not* prioritize paths with filterable junctions; it routes purely on `two_wheeler_edge_cost` and `_turn_penalty`.
* **Action Required:**
  - *For the Paper:* Clearly specify that the junction filtering discount is a **post-route travel time calibration model** applied to estimated trip duration, rather than an active graph search edge weight, OR explicitly wire it into the benchmark evaluation scripts.

### Gap 2 (Major): Turn Penalty Units Discrepancy (Meters vs. Seconds)
* **Literature Claim:** Literature review draft describes turn penalties in temporal units: $8.0\text{ s}$ for moderate turns and $25.0\text{ s}$ for sharp turns.
* **Codebase Reality:**
  - `routing/algorithms.py` lines 28–31 explicitly state:
    ```python
    # Penalty is expressed in the same cost units as road length.
    # It is applied only to actual direction changes.
    TURN_PENALTY_SHARP = 25.0
    TURN_PENALTY_MODERATE = 8.0
    ```
  - In `two_wheeler_astar` (L. 613–617):
    ```python
    new_cost = current_cost + edge_cost + turn_cost
    ```
  - Since `edge_cost` is in **meters** (`length * penalty`), `turn_cost` is added as an **equivalent distance penalty in meters** (e.g., executing a sharp turn is mathematically penalized as adding 25 meters of road distance), NOT 25 seconds!
* **Action Required:**
  - The conference paper must formally define turn penalty as an **equivalent distance impedance** ($P_{turn} \in \{0\text{ m}, 8\text{ m}, 25\text{ m}\}$), or define the cost function in generalized cost units. Describing it as seconds while the code adds meters would be an instant target for sharp IEEE reviewers.

### Gap 3 (Major): Missing 70% Edge-Sharing Filter in Alternative Generation
* **Literature Claim:** Candidate alternative routes are filtered to ensure they do not share more than 70% of edges with the primary route ($\gamma \le 0.70$).
* **Codebase Reality:**
  - In `routing/algorithms.py:807–991` (`build_split_route_candidates`), the code filters by:
    1. Exact duplicate path suppression (`tuple(stitched) in seen_paths`).
    2. Detour cap (`calc_route_distance(stitched) > fallback_cap_length * DETOUR_TOLERANCE`).
  - However, the code **does not calculate edge-sharing percentage ($\gamma$)** or prune candidates that share >70% of edges.
* **Action Required:**
  - In the experimental benchmark script, an explicit Jaccard edge-overlap filter must be computed, or the limitation must be acknowledged as a proposed filter to be integrated into the candidate generation pass.

### Gap 4 (Major): Unexposed Alternative Route API Endpoint
* **Literature Claim:** The system architecture provides an online REST API serving alternative routes and user customization.
* **Codebase Reality:**
  - `api_server.py` defines `/route` and `/dynamic-route`.
  - `build_split_route_candidates` is fully implemented in `routing/algorithms.py`, but is not imported or hooked to an endpoint in `api_server.py`.
  - Furthermore, `/dynamic-route` hardcodes `penalties = build_two_wheeler_penalties()` without query parameters, preventing frontend sliders from dynamically altering `main_road_penalty` or `inner_road_multiplier`.
* **Action Required:**
  - For experimental evaluation, batch scripts can call `build_split_route_candidates` directly in Python. Prior to production deployment, `api_server.py` should expose `/alternatives` and accept query parameters.
