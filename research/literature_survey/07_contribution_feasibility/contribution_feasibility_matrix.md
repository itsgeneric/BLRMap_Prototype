# Contribution Feasibility Matrix

**Project Title:** GIS-Based Intelligent Navigation and Path Optimization Framework: Self-Calibrating, Two-Wheeler-Aware Routing for Bengaluru  
**Stage:** Phase 7 – Contribution Feasibility and Research Scope Decision  
**Document:** `research/literature_survey/07_contribution_feasibility/contribution_feasibility_matrix.md`  
**Date:** 2026-11-03  

---

## 1. Objective and Assessment Framework

This document presents a rigorous academic and technical feasibility assessment of the four candidate research contributions proposed during the literature survey. Rather than relying on previous summary documents, this analysis directly inspects the source code in `routing/algorithms.py`, `core/config.py`, `routing/graph_manager.py`, and `api_server.py`.

Each candidate contribution is evaluated across six formal technical criteria:
1. **Literature Grounding:** What the reviewed literature ([1]–[16]) specifically supports.
2. **Current Codebase Implementation:** Exactly what functions, lines of code, and logic are currently written.
3. **Missing or Incomplete Components:** Code gaps, uncalled functions, or logical disconnects.
4. **Experimental Validability:** Feasibility of empirical testing using standard baselines, datasets, and measurable metrics.
5. **Academic Defensibility & Distinctiveness:** Whether the contribution represents a defensible, distinct scientific addition suitable for an IEEE conference paper.
6. **Required Pre-Experimental Changes:** Exact code adjustments and experimental harnesses needed before conducting experiments.

---

## 2. In-Depth Evaluation of the Four Candidate Contributions

---

### Candidate Contribution 1: Two-Wheeler-Specific Edge Impedance and Filtering Behaviour

#### 1. Literature Grounding
* **Empirical Support:** Microscopic traffic studies establish that motorized two-wheelers maintain smaller lateral buffers ($0.3\text{ m}–0.6\text{ m}$ on undivided Indian roads, Kotagi et al. [2]), filter through stationary car queues with $0.75\text{ m}–0.90\text{ m}$ clearances at signalized junctions (Promraksa et al. [1]), and maintain higher speeds than cars in congested traffic (context-specific 35%–48% speed advantage on Mumbai arterials, Das & Maurya [3]). Route choice behavior indicates that riders actively avoid arterial vehicular queues and choose secondary roads (Fadilah et al. [4]).
* **Literature Boundary:** The literature establishes behavioral and kinematic patterns, but does not provide or validate a mathematical formulation translating these empirical observations into macroscopic graph edge costs.

#### 2. Current Codebase Implementation
* **Road Hierarchy Inversion:** `core/config.py` (L. 61–77) defines `TWO_WHEELER_ROAD_PENALTIES`:
  ```python
  TWO_WHEELER_ROAD_PENALTIES = {
      'motorway': 4.0, 'trunk': 3.0, 'primary': 2.2,
      'secondary': 1.5, 'tertiary': 1.15, 'residential': 1.0,
      'living_street': 0.95, 'service': 0.9
  }
  ```
* **Dynamic Modifiers:** `routing/algorithms.py` (L. 261–343) in `two_wheeler_edge_cost()` applies:
  - Base cost: $\text{length} \times \text{penalty}$.
  - Flyover / Bridge Exception: If `bridge` is tagged on a main road, penalty is reduced to `0.8` (bypassing surface signals).
  - Roundabout Damping: Multiplies penalty by `0.95`.
  - Surface Degradation: Multiplies penalty by `graph_mgr.get_surface_penalty(u, v)`.
* **Filtering Helper Functions:** `routing/algorithms.py` defines:
  - `count_filterable_junctions(graph, route)` (L. 169–208): Counts junctions along a route where `tag == "traffic_signals"` and approach `lanes >= 2`.
  - `apply_filtering_discount(traffic_seconds, filterable_junction_count)` (L. 211–225): Applies $T_{calibrated} = T \times \max(0.85, 0.985^N)$.

#### 3. Missing or Incomplete Components
* **Critical Disconnect on Filtering:** Neither `count_filterable_junctions` nor `apply_filtering_discount` is invoked inside `two_wheeler_astar()` or in `api_server.py`. The A\* search algorithm does **not** consider junction filtering when selecting edges; filtering exists only as an uncalled post-processing calculation.
* **API Hardcoding:** `api_server.py:118` calls `penalties = build_two_wheeler_penalties()` with no arguments, ignoring runtime client customization.

#### 4. Experimental Validability
* **High Validability for Road Hierarchy:** Running batch OD pairs through distance A\* vs. OSRM car hierarchy vs. two-wheeler A\* produces measurable shifts in road-class distribution (% primary vs. % secondary/residential) and route length.
* **Post-Route Duration Validability:** The post-route filtering discount can be experimentally evaluated in batch testing scripts by comparing trip duration estimates before and after discount application across signalized corridors.

#### 5. Academic Defensibility & Distinctiveness
* **Defensible Component:** The inverted road hierarchy, flyover exceptions, and multi-attribute edge impedance model is academically defensible and distinct from car-centric OSRM profiles.
* **Indefensible Component:** Claiming that the A\* routing algorithm performs "filtering-aware path selection" is **indefensible** under the current code, because filtering does not influence edge costs during search.

#### 6. Required Changes Before Experiments
* Formally re-scope the paper text: define filtering discount strictly as a **post-route travel time calibration model**, OR wire filtering into edge costs during search.
* In experimental batch scripts, explicitly invoke `apply_filtering_discount()` on completed routes.
* Expose `main_road_penalty` and `inner_road_multiplier` query parameters in `api_server.py`.

---

### Candidate Contribution 2: State-Expanded, Turn-Aware A\* Routing

#### 1. Literature Grounding
* **Theoretical Foundation:** Winter (2002) [6] mathematically proved that shortest-path algorithms produce erratic, zigzag routes unless incoming edge state $(e_{in})$ is maintained. Geisberger & Vetter (2011) [7] demonstrated edge-based routing with junction turn tables for automobiles. Bast et al. (2016) [10] established conditions for A\* heuristic admissibility.
* **Literature Gap:** Existing turn-cost literature either targets automobiles (penalizing physical turning radii) or static continental pre-computation (CH). In motorcycle literature, Asvial et al. [5] completely omitted turn costs ($P_{turn} = 0$).

#### 2. Current Codebase Implementation
* **Search State Space:** `routing/algorithms.py` (L. 472–525) implements dynamic state expansion in `two_wheeler_astar`:
  ```python
  start_state = (None, start_node)
  next_state = (current_node, next_node)
  g_score[state] = ...
  ```
* **Spherical Angle Deflection:** `_turn_angle(graph, prev_node, current_node, next_node)` (L. 105–139) computes bearing changes using spherical trigonometry (`_bearing_deg`).
* **Discrete Thresholds:** `_turn_penalty()` (L. 141–163) assigns:
  - $\Delta \theta < 30^\circ$: $0.0$ (Gentle curve)
  - $30^\circ \le \Delta \theta < 60^\circ$: $8.0$ (Moderate turn)
  - $\Delta \theta \ge 60^\circ$: $25.0$ (Sharp turn)
* **Cost Accumulation:** Line 614: `new_cost = current_cost + edge_cost + turn_cost`.

#### 3. Missing or Incomplete Components
* **Critical Heuristic Admissibility Bug:** In lines 480–490 of `routing/algorithms.py`:
  ```python
  def heuristic(node):
      return haversine_m(...) / MIN_PENALTY_FLOOR
  ```
  Since `MIN_PENALTY_FLOOR = 0.8`, dividing by $0.8$ multiplies the Haversine distance by $1.25$! When traversing edges with penalties $\le 1.0$, the heuristic overestimates true remaining cost, **violating A\* admissibility and consistency**. To be admissible, it must multiply by the minimum floor: `haversine_m * MIN_PENALTY_FLOOR`.
* **Physical Unit Mismatch:** `turn_cost` is added to `length * penalty` in **meters**, but earlier documentation described it in seconds.

#### 4. Experimental Validability
* **Extremely High:** Can be directly benchmarked against turn-agnostic A\* (penalties = 0) and standard node-based Dijkstra across 300 test queries in dense grid sectors (Malleshwaram, Chickpet, Jayanagar).
* **Metrics:** Turn count, turn severity breakdown (moderate vs. sharp), circuity index ($\tau$), settled search states, and query execution latency (ms).

#### 5. Academic Defensibility & Distinctiveness
* **Highly Distinct and Defensible:** Combines dynamic state expansion with vehicle-differentiated discrete angle penalties on OpenStreetMap without line graph memory explosion. Represents a solid algorithmic contribution for an IEEE ITS conference.

#### 6. Required Changes Before Experiments
* **Fix the Heuristic Formula:** Correct `heuristic = haversine_m * MIN_PENALTY_FLOOR` (or `haversine_m * 0.8`) in `routing/algorithms.py:489` to restore mathematical admissibility.
* **Harmonize Units:** Formally define turn penalties in the paper as **equivalent virtual detour distance** in meters ($P_{turn} \in \{0\text{ m}, 8\text{ m}, 25\text{ m}\}$).

---

### Candidate Contribution 3: Alternative Route Generation and Route Diversity

#### 1. Literature Grounding
* **Theoretical Foundation:** Abraham et al. (2013) [9] established that Yen's $k$-shortest paths algorithm fails in urban grids due to single-block sharing (>95% edge overlap). They formalized three quality criteria: limited sharing ($\gamma \le 70\%$), bounded detour ($\epsilon \le 20\%$), and local optimality.
* **Literature Gap:** Asvial et al. [5] relied on Yen's $k$-shortest paths for motorcycles, inheriting its grid flaws. Western highway via-node plateaus do not discover secondary street corridors in dense Asian cities.

#### 2. Current Codebase Implementation
* **Perpendicular Offset Waypoint Generator:** `routing/algorithms.py` (L. 753–802) in `_offset_split_points()`:
  - Segment fractions: $f \in \{0.33, 0.50, 0.67\}$.
  - Lateral perpendicular offsets: $d_{lat} \in \{150\text{ m}, 300\text{ m}\}$ at orthogonal bearings ($\theta_{OD} \pm 90^\circ$).
  - Evaluates coordinates via spherical destination point geodesy.
* **Two-Leg Candidate Stitching:** `build_split_route_candidates()` (L. 807–991):
  - Snaps offset coordinates to nearest OSM nodes.
  - Computes two-leg turn-aware A\* ($s \to v_{via}$ and $v_{via} \to t$).
  - Enforces bounded detour: `calc_route_distance(stitched) <= fallback_cap_length * DETOUR_TOLERANCE` (`DETOUR_TOLERANCE = 1.20`).
  - Enforces exact duplicate suppression: `if tuple(stitched) in seen_paths: continue`.

#### 3. Missing or Incomplete Components
* **Missing 70% Edge-Sharing Filter:** `build_split_route_candidates()` suppresses identical paths, but does not calculate edge-sharing percentage ($\gamma$) and does not discard paths sharing >70% of edges with the primary route.
* **Unexposed API Endpoint:** The function is completely absent from `api_server.py`.

#### 4. Experimental Validability
* **High Validability:** Can be directly benchmarked against Yen's $k$-shortest paths ($k=3, 5$) across 25 representative OD pairs in Bengaluru.
* **Metrics:** Edge sharing percentage ($\gamma$), Jaccard edge distance, detour ratio ($\epsilon$), and runtime latency.

#### 5. Academic Defensibility & Distinctiveness
* **Strong Supporting Contribution:** Resolves an acknowledged limitation in motorcycle routing literature ([5]) by applying geometric via-node projection to urban secondary street discovery.

#### 6. Required Changes Before Experiments
* Implement an explicit edge-sharing overlap calculation function:
  $$\text{Sharing}(P_{alt}, P_{opt}) = \frac{\sum_{e \in P_{alt} \cap P_{opt}} \text{length}(e)}{\text{length}(P_{opt})}$$
* Filter candidate routes exceeding $\gamma > 0.70$ during candidate selection or in the evaluation harness.
* Expose `build_split_route_candidates` via a `/route/alternatives` endpoint in `api_server.py`.

---

### Candidate Contribution 4: Congestion-Aware Route Selection and Bypassing

#### 1. Literature Grounding
* **Literature Foundation:** Kumar et al. (2025) [16] demonstrated deep learning models (1D CNN, LSTM, SVR; MAE = 6.02) to predict arterial traffic congestion in Bengaluru, proving that corridors like Hosur Road and Trinity Circle routinely reach 100% volume saturation during peak hours. However, Kumar et al. terminated at prediction without routing vehicles around bottlenecks.
* **Literature Gap:** Streaming graph engines (Abbas et al. [13]) require dense inductive loop sensors unavailable in Indian cities.

#### 2. Current Codebase Implementation
* **Dynamic Node Penalty:** `routing/algorithms.py` (L. 311–316) in `two_wheeler_edge_cost()`:
  ```python
  if congested_nodes and (u in congested_nodes or v in congested_nodes):
      penalty *= 25.0
  ```
* **API Integration:** `api_server.py:104–165` exposes `/dynamic-route`, ingests `jam_coords` from `fetch_traffic_data()`, maps coordinates to nearest graph nodes (`congested_nodes`), and executes `two_wheeler_astar()`.

#### 3. Missing or Incomplete Components
* **No Predictive Engine Implemented:** The codebase does not train or run machine learning models. Traffic data is fetched from external APIs or simulated.
* **Arbitrary Multiplier:** The $25.0\times$ multiplier is an uncalibrated heuristic constant.

#### 4. Experimental Validability
* **Valid as an Empirical Case Study:** Kumar et al.'s [16] documented corridors (Hosur Road, Trinity Circle / MG Road, Yeshwanthpur) can be configured as congested node sets, testing whether the engine routes two-wheelers through secondary bypasses.

#### 5. Academic Defensibility & Distinctiveness
* **Not Defensible as an Independent Algorithmic Contribution:** Multiplying edge weights by 25.0 is a simple standard impedance scaling technique, not a novel routing theory. Claiming a novel predictive traffic engine would be rejected because the code does not implement deep learning or streaming analytics.
* **Defensible as an Empirical Case Study:** Highly defensible when framed as an application testbed demonstrating how our two-wheeler A\* engine bypasses known Bengaluru bottleneck corridors.

#### 6. Required Changes Before Experiments
* Clearly frame this contribution as an **Empirical Case Study / Validation Scenario** rather than a primary technical contribution.
* Conduct sensitivity analysis on the congestion multiplier ($5\times, 10\times, 25\times, 50\times$).

---

## 3. Summary Feasibility and Status Matrix

| Candidate Contribution | Theoretical Literature Support | Codebase Implementation Status | Missing Technical Elements | Experimental Validability | Recommended Research Scope Role |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **1. Two-Wheeler Edge Impedance & Filtering** | High ([1], [2], [3], [4], [15]) | **75% Implemented** (Inverted penalties active; filtering discount helper uncalled) | Wire filtering into travel time calibration; expose API parameters | **High** (Road-class share, travel time, length) | **Core Contribution** (Inverted hierarchy + duration calibration) |
| **2. State-Expanded Turn-Aware A\*** | Very High ([6], [7], [10]) | **95% Implemented** (Active in `two_wheeler_astar`) | **Fix heuristic formula** (`* 0.8` instead of `/ 0.8`); clarify distance units | **Very High** (Turn counts, severity, circuity, latency) | **Core Contribution** (Algorithmic center of the paper) |
| **3. Perpendicular Offset Alternative Routing** | High ([5], [9], [14]) | **70% Implemented** (Offset generation active; sharing filter missing) | Add 70% edge-sharing calculation; expose API endpoint | **High** (Jaccard distance, edge sharing %, detour $\epsilon$) | **Supporting Contribution** (Practical commuter value) |
| **4. Congestion Bypass & Prediction Integration** | Moderate ([12], [13], [16]) | **40% Implemented** (Heuristic $25\times$ penalty active; zero ML/streaming code) | No predictive ML pipeline in code | **Moderate** (Bottleneck nodes avoided, detour efficiency) | **Empirical Case Study & Future Work** (Do not claim novel prediction) |
