# Phase 1.5 – Critical Literature Audit Report

**Project Title:** GIS-Based Intelligent Navigation and Path Optimization Framework: Self-Calibrating, Two-Wheeler-Aware Routing for Bengaluru  
**Stage:** Phase 1.5 Literature Review Audit  
**Date of Audit:** 2026-11-03  
**Auditor:** Academic Research Assistant  
**Target Venue Alignment:** IEEE Transactions on Intelligent Transportation Systems / IEEE International Conference on Intelligent Transportation Systems (ITSC)

---

## 1. Executive Summary & Audit Rationale

The objective of Phase 1.5 is to rigorously audit the preliminary 16-paper literature selection against the concrete software architecture and algorithmic contributions of the **Bengaluru Two-Wheeler Routing Engine**. 

### Core Technical Pillars of the Engine:
1. **Locally Controlled OpenStreetMap Graph Management:** Python/OSMnx pipeline extracting non-planar road networks, edge geometries, and highway tag hierarchies.
2. **Turn-Aware A\* Search & Edge-Based State Expansion:** Graph traversal with state tracking $(u, v) = (\text{previous\_node}, \text{current\_node})$, dynamic turn-angle calculation, and sharp/moderate turn penalty assignment.
3. **Customizable Route Cost Functions & Road Suitability:** Admissible A\* heuristic scaling with variable road penalties (penalizing major arterials, prioritizing residential/service roads, flyover exceptions, and roundabout damping).
4. **Lane-Filtering Junction Modeling:** Edge-level capacity scores discounting junction traversal time based on lane width and signal presence.
5. **Alternative Route Generation & Candidate Diversity:** Perpendicular offset waypoint injection and route splitting for long-distance congested urban trips.

The audit revealed that while Phase 1 established strong traffic-engineering foundations, several papers focused on disconnected domains (e.g., computer networking packet routing, general deep learning speed forecasting, autonomous car fleet rebalancing). These have been formally removed and replaced with landmark peer-reviewed publications covering **turn-cost graph routing, customizable route planning, alternative route diversity, and empirical motorcycle route choice**.

---

## 2. Reassessment and Three-Tier Classification of the Literature

Every paper in the revised 16-paper corpus has been audited and classified into three distinct relevance tiers:

### Tier 1: Directly Relevant (Core Algorithmic & Domain Alignment)
*These papers directly provide the mathematical formulations, graph representations, algorithmic heuristics, or empirical vehicle behavioral models used in the codebase.*

1. **[1] Promraksa et al. (2022)** — *Lane-Filtering Behavior at Signalized Intersections*: Directly grounds the junction lane-filtering capacity calculation and discount factors in `routing/algorithms.py`.
2. **[4] Fadilah et al. (2024)** — *Motorcycle Route Choice Behavior in Mixed Traffic*: Provides empirical proof that two-wheeler riders deliberately deviate from car-centric shortest paths to avoid arterial congestion by exploiting secondary roads and tolerating higher turn frequencies.
3. **[5] Asvial et al. (2020)** — *Motorcycle Routing in Megacities (Jakarta)*: Evaluates motorcycle navigation on OpenStreetMap road graphs in a congested Asian megacity, addressing road suitability and traffic dispersion.
4. **[6] Winter (2002)** — *Modeling Costs of Turns in Route Planning*: Foundational mathematical proof for turn-cost route planning; establishes the state-expansion dual graph representation $(u, v)$ utilized by our A\* engine.
5. **[7] Geisberger & Vetter (2011)** — *Efficient Routing in Road Networks with Turn Costs*: Demonstrates edge-based routing and turn-penalty enforcement without full dual graph explosion, directly supporting our turn penalty thresholds (`TURN_PENALTY_SHARP`, `TURN_PENALTY_MODERATE`).
6. **[8] Delling et al. (2017)** — *Customizable Route Planning (CRP)*: The benchmark framework for decoupling topological road graphs from dynamic metric customization (road-type penalties, vehicle profiles, and turn metrics).
7. **[9] Abraham et al. (2013)** — *Alternative Routes in Road Networks*: Algorithmic foundation defining route diversity (bounded detour, limited sharing) and via-node penalty methods; mathematically grounds our perpendicular offset route splitting.
8. **[14] Boeing (2017)** — *OSMnx Street Network Modeling*: The exact geospatial graph library powering our backend network ingestion, topological cleaning, and road attribute extraction.
9. **[15] Luxen & Vetter (2011)** — *Real-time Routing with OpenStreetMap Data (OSRM)*: Foundational architectural paradigm for vehicle-profile-driven edge costing on OpenStreetMap graphs.

### Tier 2: Technically Relevant (Methodological & Pipeline Support)
*These papers provide algorithmic components, clustering techniques, or microscopic behavioral models that support secondary pipeline stages.*

10. **[2] Kotagi et al. (2020)** — *Lateral Placement on Indian Undivided Roads*: Models how two-wheelers occupy road width in Indian mixed traffic, proving they require minimal lateral safety buffers compared to cars.
11. **[3] Das & Maurya (2019)** — *Microscopic Two-Wheeler Filtering Maneuverability*: Quantifies that motorized two-wheelers maintain a 35%–48% speed advantage over cars during congested queue states in India.
12. **[10] Bast et al. (2016)** — *Route Planning in Transportation Networks*: Definitive survey on shortest-path speed-up techniques, A\* heuristics, and multi-criteria routing complexity.
13. **[11] Lee et al. (2007)** — *Trajectory Clustering (TRACLUS)*: Foundational partition-and-group trajectory clustering algorithm; provides the spatial density-based clustering principles adapting DBSCAN to road segments.
14. **[12] Du et al. (2020)** — *Recurrent and Non-Recurrent Congestion Detection*: Validates that urban commuter congestion concentrates in recurrent bottleneck corridors that follow predictable diurnal profiles.
15. **[13] Abbas et al. (2020)** — *Streaming Graph Analytics for Congestion Reduction*: Establishes dynamic edge-weight updating on directed graphs to alleviate urban congestion in real-time.

### Tier 3: Supporting / Background Research (Context & Baseline Benchmarking)
*These papers establish regional context or demonstrate existing system limitations.*

16. **[16] Kumar et al. (2025)** — *Real-Time Bengaluru Traffic Prediction*: Establishes the current baseline for traffic forecasting in Bengaluru (CNN/LSTM/SVR) and illustrates the critical gap: predictive models fail to feed back into routing weights.

---

## 3. Audit of Changes: Retained, Replaced, and Introduced Papers

| Original Ref ID | Original Paper | Audit Verdict | Action Taken | Rationale for Decision | Replacement / Retained Paper |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[1]** | Promraksa et al. (2022) | Strong | **Retained** as `[1]` | Directly provides empirical constants for intersection lane-filtering. | *Retained* |
| **[2]** | Kotagi et al. (2020) | Strong | **Retained** as `[2]` | Empirical data on Indian mixed-traffic road width utilization. | *Retained* |
| **[3]** | Das & Maurya (2019) | Strong | **Retained** as `[3]` | Quantifies motorcycle speed advantage in Indian traffic queues. | *Retained* |
| **[4]** | Kumar et al. (2025) | Moderate | **Shifted** to `[16]` | Strong regional baseline for Bengaluru, but should serve as Background. | Shifted to `[16]`; slot used for Fadilah et al. |
| **[5]** | George et al. (2020) | Weak (Routing) | **Replaced** | Focuses strictly on physical sensor density estimation, not graph routing. | **Replaced by Fadilah et al. (2024)** (`[4]`), which directly models motorcycle route choice behavior. |
| **[6]** | Yu et al. (2018) | Weak (Routing) | **Replaced** | STGCN forecasts sensor speeds; does not perform path planning or turn evaluation. | **Replaced by Geisberger & Vetter (2011)** (`[7]`), which models turn costs in road graphs. |
| **[7]** | Mojaveri & Faragó (2021) | **Disqualified** | **Removed & Replaced** | **Critical Finding:** This paper addresses computer networking / ACL packet routing, not road traffic. | **Replaced by Winter (2002)** (`[6]`), the landmark paper on turn-cost route planning. |
| **[8]** | Rossi et al. (2018) | Weak (Routing) | **Replaced** | Evaluates centralized autonomous car fleet dispatching; lacks turn/two-wheeler awareness. | **Replaced by Abraham et al. (2013)** (`[9]`), the definitive reference for alternative route diversity. |
| **[9]** | Abbas et al. (2020) | Moderate | **Retained** as `[13]` | Direct streaming edge-weight updates; local PDF in workspace. | *Retained* |
| **[10]** | Bast et al. (2016) | Strong | **Retained** as `[10]` | Essential algorithmic survey for shortest paths and A\* heuristics. | *Retained* |
| **[11]** | Yang (2025) | Moderate | **Replaced** | Analyzes taxi regular trajectory mining; less aligned with custom route cost functions. | **Replaced by Delling et al. (2017)** (`[8]`), the benchmark paper on Customizable Route Planning. |
| **[12]** | Lee et al. (2007) | Strong | **Retained** as `[11]` | Foundational TRACLUS algorithm adapting DBSCAN to edge/line segments. | *Retained* |
| **[13]** | Du et al. (2020) | Strong | **Retained** as `[12]` | Directly justifies auto-detecting recurrent diurnal congestion corridors. | *Retained* |
| **[14]** | Boeing (2017) | Strong | **Retained** as `[14]` | Core library for our OpenStreetMap graph pipeline. | *Retained* |
| **[15]** | Asvial et al. (2020) | Strong | **Retained** as `[5]` | Motorcycle-specific OpenStreetMap routing in an Asian megacity. | *Retained* |
| **[16]** | Luxen & Vetter (2011) | Strong | **Retained** as `[15]` | Foundational vehicle profile routing on OSM graphs (OSRM). | *Retained* |

---

## 4. In-Depth Analysis of Newly Introduced Papers

### Paper A: Winter (2002) — *Modeling costs of turns in route planning*
* **Bibliographic Data:** *GeoInformatica*, 6(4), pp. 345–361. Springer. DOI: [10.1023/A:1020853410145](https://doi.org/10.1023/A:1020853410145).
* **Technical Gap Filled:** Turn-cost modeling and state-expanded graph representations.
* **Why it was chosen:** Standard shortest-path algorithms assume edge costs are independent of the traversal path. Winter proved that turns depend on the previous edge $(e_{in}, e_{out})$, requiring either a line-graph transformation or an expanded search state $(u, v)$ where $u$ is the predecessor node. This directly validates the design of `astar_on_graph` and `two_wheeler_astar` in `routing/algorithms.py`.

### Paper B: Geisberger & Vetter (2011) — *Efficient Routing in Road Networks with Turn Costs*
* **Bibliographic Data:** *Proc. 10th Int. Symp. on Experimental Algorithms (SEA 2011)*, LNCS 6630, pp. 100–111. Springer. DOI: [10.1007/978-3-642-20662-7_9](https://doi.org/10.1007/978-3-642-20662-7_9).
* **Technical Gap Filled:** Edge-based turn restrictions and turn-cost algorithms.
* **Why it was chosen:** Co-authored by Christian Vetter (co-author of OSRM), this work demonstrates how to handle complex non-linear turn penalties and prohibited maneuvers efficiently on road networks. It provides the computational benchmark for our discrete turn thresholds (`TURN_THRESHOLD_MODERATE = 30°`, `TURN_THRESHOLD_SHARP = 60°`).

### Paper C: Delling, Goldberg, Pajor, & Werneck (2017) — *Customizable Route Planning in Road Networks*
* **Bibliographic Data:** *Transportation Science*, 51(2), pp. 566–591. INFORMS. DOI: [10.1287/trsc.2014.0579](https://doi.org/10.1287/trsc.2014.0579).
* **Technical Gap Filled:** Customizable edge-cost functions and multi-metric routing.
* **Why it was chosen:** Delling et al. introduced Customizable Route Planning (CRP), proving that modern routing engines must separate metric-independent topology from dynamic, customizable cost functions. This paper validates our parameter tuning sliders (`main_road_penalty`, `inner_road_multiplier`, `service_multiplier`, `roundabout_multiplier`) operating on a single OpenStreetMap graph.

### Paper D: Abraham, Delling, Goldberg, & Werneck (2013) — *Alternative Routes in Road Networks*
* **Bibliographic Data:** *ACM Journal of Experimental Algorithmics*, 18(1), pp. 1.3:1–1.3:17. ACM. DOI: [10.1145/2444016.2444019](https://doi.org/10.1145/2444016.2444019).
* **Technical Gap Filled:** Alternative route generation, route diversity, and via-node penalty heuristics.
* **Why it was chosen:** Addresses the common failure mode where standard $k$-shortest path algorithms return trivial, overlapping detours. Abraham et al. define formal criteria for route diversity (bounded overlap, local optimality) and introduce via-node heuristics. This directly grounds our split-candidate generation and perpendicular offset waypoints in `routing/algorithms.py`.

### Paper E: Fadilah, Nishiuchi, & Ngoc (2024) — *Identifying the role of route choice behavior of motorcycle riders in microscopic simulation modeling under mixed traffic conditions*
* **Bibliographic Data:** *Transportation Research Interdisciplinary Perspectives*, 28, 101247. Elsevier. DOI: [10.1016/j.trip.2024.101247](https://doi.org/10.1016/j.trip.2024.101247).
* **Technical Gap Filled:** Motorcycle-specific route choice and road suitability.
* **Why it was chosen:** Published in late 2024, this peer-reviewed open-access study investigates why motorcycle riders in developing, mixed-traffic Asian cities choose alternative routes. It provides empirical evidence that riders accept higher turn counts to access inner residential roads and bypass congested arterials, directly supporting our inner-road biased routing logic.

---

## 5. Remaining Literature Gaps and Scope Boundaries

While the revised 16-paper corpus is tightly aligned with our engine's algorithmic core, the following literature gaps and scope boundaries are noted:

1. **City-Wide Dynamic Micro-Signal Simulation vs. Empirical Graph Weighting:**
   - *Literature Gap:* There is no single published paper that models signalized intersection delays across the entire Bengaluru road network in real-time.
   - *Project Mitigation:* We bound our project scope to graph-level edge discounting at signalized intersections with $\ge 2$ approach lanes (`count_filterable_junctions`), rather than full microscopic signal queue simulation.
2. **Formal Dynamic Calibration via Reinforcement Learning:**
   - *Literature Gap:* Literature on self-calibrating route edge weights typically relies on offline regression or batch simulation rather than online closed-loop reinforcement learning.
   - *Project Mitigation:* Our project implements clustering-based corridor detection (DBSCAN) and time-of-day multiplier fitting calibrated against live Google Routes API probe durations.
3. **OpenStreetMap Tag Sparsity for Indian Secondary Roads:**
   - *Literature Gap:* In developing cities, road width and lane tags on residential and service roads are frequently unmapped or incomplete in OSM.
   - *Project Mitigation:* Grounded in Boeing (2017) and Kotagi et al. (2020), our engine uses structural fallback rules (defaulting unknown road widths and lane counts to single-lane residential defaults).

---

## 6. Audit Conclusion

The revised 16-paper selection resolves all alignment concerns:
* Disqualified non-vehicular networking preprints (Mojaveri & Faragó).
* Replaced general sensor forecasting and fleet rebalancing with turn-aware routing, customizable route planning, and route diversity algorithms.
* Strengthened the core literature foundation to directly reflect the actual Python/OSMnx/A\* implementation.

All project files have been synchronized. The collection is now ready for **Phase 2 – Full-Text Collection** upon user approval.
