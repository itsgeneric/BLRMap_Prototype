# Phase 10 Independent Audit: Implementation, Metrics, and Experimental Integrity

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Audit Target:** Phase 10 — Alternative Route Generation, 70% Edge-Overlap Diversity Filtering, and Yen's K-Shortest Paths (KSP) Baseline  
**Audit Date:** November 3, 2026 (Local Time)  
**Auditor:** Independent Antigravity Audit Agent  
**Audit Scope:** Overlap calculation mathematics, boundary conditions, state-expanded Yen's KSP fidelity, raw benchmark data recalculation, experimental parity, academic claims validation, and publication recommendations.

---

## Executive Summary & Audit Verdict

| Audit Dimension | Evaluation Criterion | Independent Audit Finding | Status |
| :--- | :--- | :--- | :---: |
| **1. Overlap Mathematics** | Physical edge lengths, directed/undirected, multi-edge handling | Exact physical lengths extracted; directed mode prevents one-way/dual-carriageway conflation. | **VERIFIED** |
| **2. Boundary Enforcement** | Strict 70% overlap rejection ($\le 0.70$ keep, $> 0.70$ drop) & 1.20 detour cap | Strict inequality verified in source code and unit tests; 1.20 detour cap properly enforced. | **VERIFIED** |
| **3. Mutual Overlap Check** | Overlap check between accepted alternatives | **Architectural Limitation Identified:** Filtering is strictly pairwise between candidate and primary route ($P_{\text{primary}}$). Mutual diversity between alternatives is unconstrained except for exact duplicate suppression. | **DOCUMENTED** |
| **4. Yen's KSP Fidelity** | Turn-aware state expansion, spur bearing preservation, loop freedom | Exact Yen (1971) formulation; spur node initializes state from root path predecessor; banned nodes prevent cycles. | **VERIFIED** |
| **5. Data Integrity** | Raw JSON route-level recalculation vs. reported summary metrics | Recalculated values match published tables to 4 decimal places across all 25 OD corridors. | **VERIFIED** |
| **6. Comparison Fairness** | Identical graph, OD nodes, cost functions, turn penalties, and caps | Exact parity maintained across all benchmark dimensions. Both algorithms ran on identical state-expanded graph. | **VERIFIED** |
| **7. Scientific Claims** | Validity of diversity, speedup, and bottleneck claims for IEEE paper | Claims of diversity, computational speedup, and plateau mitigation are rigorously supported; safety/universal superiority claims must be restrained. | **ALIGNED** |

**Final Recommendation:** **APPROVED WITH MINOR ACADEMIC CAVEATS.** The implementation and experimental data are mathematically sound, reproducible, and ready for IEEE paper drafting, provided the documented architectural nuances and scope boundaries are explicitly stated.

---

## 1. Verification of the 70% Overlap Calculation

### 1.1 Physical Edge Length Extraction and Graph Representation
In [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L740-L775), edge lengths are extracted via `get_route_edge_lengths(graph, route, undirected=False)`.
- **Physical Lengths:** The function accesses `graph.get_edge_data(u, v)`. In OpenStreetMap MultiDiGraphs, multiple edge keys may exist between nodes $u$ and $v$. The implementation selects:
  ```python
  length = min(float(d.get("length", 1.0)) for d in edge_data.values())
  ```
  This correctly measures the physical road distance in meters rather than relying on hop counts or node counts.
- **Directed vs. Undirected Handling:**
  - In directed mode (`undirected=False`, the default throughout Phase 10), each edge key is represented as `(u, v)`. Traversal from $u \to v$ is strictly distinguished from $v \to u$.
  - This prevents conflating opposing directions on dual-carriageway divided arterials (e.g., Outer Ring Road, Hosur Road, Bellary Road) and preserves the one-way topology of Bengaluru's urban grid.
  - In undirected mode (`undirected=True`), edges are canonicalized as `(min(u, v), max(u, v))`, which is available as a parameter option.
- **Parallel Edge Conflation:** Because OSM MultiDiGraphs can possess parallel edges (e.g., service lanes adjacent to main carriageways), choosing the minimum physical length provides a consistent, deterministic lower bound for edge distance without double-counting.

### 1.2 Overlap Formulation and Boundary Verification
The overlap metric is computed in `calc_route_overlap(graph, primary_route, alt_route, undirected=False)` as:
$$\text{Overlap}(P_{\text{primary}}, P_{\text{alt}}) = \frac{\sum_{e \in E(P_{\text{primary}}) \cap E(P_{\text{alt}})} \text{Length}(e)}{\sum_{e \in E(P_{\text{alt}})} \text{Length}(e)}$$
Where:
- The denominator is the total physical length of the candidate alternative route ($\text{AlternativeRouteEdgeLength}$).
- The numerator is the total physical length of edges belonging to both routes ($\text{SharedEdgeLength}$).
- If $\sum_{e \in E(P_{\text{alt}})} \text{Length}(e) = 0.0$, the function safely returns $0.0$.

In `build_split_route_candidates()`:
```python
overlap_ratio = calc_route_overlap(graph, primary_route_nodes, candidate_route, undirected=False)
if overlap_ratio > max_overlap:
    continue  # Rejected: shares too much physical distance with primary
```
- **Boundary Condition:** With `max_overlap = 0.70`, a candidate sharing **exactly 70.00%** of its physical length is **retained** ($\le 0.70$). A candidate sharing **70.01%** is **rejected** ($> 0.70$).
- This was confirmed in unit test `test_04_overlap_boundary_condition` in [`tests/test_alternative_routing.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/tests/test_alternative_routing.py#L110-L135), which passed.

### 1.3 Detour Constraint Enforcement
The maximum detour constraint is verified against the primary route distance:
```python
primary_dist = sum(get_route_edge_lengths(graph, primary_route_nodes, undirected=False).values())
fallback_cap_length = primary_route_info.get("total_distance_m", primary_dist)
cand_dist = sum(get_route_edge_lengths(graph, candidate_route, undirected=False).values())
detour_ratio = cand_dist / fallback_cap_length
if detour_ratio > max_detour_ratio:
    continue  # Rejected: exceeds 1.20x physical distance
```
- The constraint strictly bounds candidate length to $\le 1.20 \times \text{Length}(P_{\text{primary}})$, preventing circuitous detours.

### 1.4 Identified Architectural Limitation: Primary-Limited vs. Mutual Overlap Filtering
- **Audit Finding:** In `build_split_route_candidates()`, candidate alternatives are evaluated **exclusively against the primary route** (`primary_route_nodes = candidates[0]["nodes"]`).
- **Mechanism:**
  1. $P_{\text{alt}, 1}$ is compared against $P_{\text{primary}}$. If $\text{Overlap}(P_{\text{primary}}, P_{\text{alt}, 1}) \le 0.70$, it is accepted.
  2. $P_{\text{alt}, 2}$ is compared against $P_{\text{primary}}$. If $\text{Overlap}(P_{\text{primary}}, P_{\text{alt}, 2}) \le 0.70$, it is accepted.
  3. $P_{\text{alt}, 3}$ is compared against $P_{\text{primary}}$. If $\text{Overlap}(P_{\text{primary}}, P_{\text{alt}, 3}) \le 0.70$, it is accepted.
  4. Between alternatives themselves, the only constraint enforced is **exact duplicate path sequence suppression** (`tuple(candidate_route) in seen_paths`).
- **Implication:** If Candidate A (e.g., $+150\text{ m}$ left lateral offset) and Candidate B (e.g., $+300\text{ m}$ left lateral offset) each share 45% of their road segments with the primary route, but share 85% of their segments with each other along an adjacent parallel corridor, **both are accepted**.
- **Assessment for IEEE Paper:** This is standard for primary-referenced alternative routing (such as Google Maps or OpenStreetMap split routing), but it must be clearly described in the methodology section as:
  $$\text{Filter Condition:} \quad \text{Overlap}(P_{\text{primary}}, P_k) \le 0.70 \quad \forall k \in \{1, 2, 3\}$$
  rather than claiming all-pairs mutual diversity filtering $\text{Overlap}(P_j, P_k) \le 0.70$. Pairwise diversity across the full set is reported separately via the Jaccard-based pairwise diversity metric.

---

## 2. Verification of Yen's KSP Implementation

### 2.1 State-Expanded Turn Awareness
In [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L960-L1075), `yen_ksp_two_wheeler()` implements Yen's K-Shortest Paths algorithm over the state-expanded directed road network.

To preserve turn awareness across spur node transitions, the implementation addresses the transition state:
```python
if len(root_path) >= 2:
    spur_prev_node = root_path[-2]
else:
    spur_prev_node = None

spur_path = two_wheeler_astar(
    graph=graph,
    start_node=spur_node,
    end_node=destination_node,
    graph_mgr=graph_mgr,
    penalties=penalties,
    congested_nodes=congested_nodes,
    heuristic_mode=heuristic_mode,
    initial_previous_node=spur_prev_node,
    banned_nodes=banned_nodes,
    banned_edges=banned_edges,
    return_metrics=False,
)
```
- **Spur Incoming Bearing:** By passing `initial_previous_node=spur_prev_node`, the spur search begins with initial state `(root_path[-2], spur_node)`.
- **Turn Cost Accuracy:** When the spur search examines the first outgoing edge $(spur\_node \to next\_node)$, `_turn_penalty(graph, root_path[-2], spur_node, next_node)` computes the exact angular penalty of turning from the root path into the spur branch.
- **Fairness:** The identical cost function (`two_wheeler_edge_cost`) and turn penalties ($0.0, 8.0, 25.0$) are evaluated during spur exploration as in the primary route search.

### 2.2 Loop Freedom and Subgraph Banning
- **Banned Nodes:** `banned_nodes = set(root_path[:-1])`. Every node along the root path prior to the spur node is strictly excluded from expansion. This guarantees that the spur path cannot form cycles back into the prefix of the route.
- **Banned Edges:**
  ```python
  banned_edges = set()
  for p in A:
      if len(p) > i and p[:i + 1] == root_path:
          banned_edges.add((p[i], p[i + 1]))
  ```
  Any outgoing edge from the spur node that was utilized by an earlier accepted path sharing the identical root path is pruned from the priority queue.
- **Path Validity:** The reconstructed candidate path $P_{\text{total}} = \text{root\_path}[:-1] + \text{spur\_path}$ is checked via `is_valid_connected_route(graph, total_path)`. If disconnected or cyclical, it is rejected.
- **Algorithm Fidelity:** The implementation adheres to the classical Yen (1971) algorithm on a state-expanded search space. It is an exact $K$-shortest paths implementation rather than an edge-penalization heuristic.

---

## 3. Independent Recalculation of Experimental Results

The raw data in [`alternative_routing_raw.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/10_alternative_routing/alternative_routing_raw.json) (encompassing all 25 OD pairs and 156 route traces) was independently processed and recalculated using an automated script.

### 3.1 Aggregate Metric Audit Matrix
The table below presents an audit comparison between values reported in `alternative_routing_results.md` and values recalculated directly from the raw JSON payload:

| Evaluation Metric | Offset Reported | Offset Recalculated | Yen (Raw) Reported | Yen (Raw) Recalculated | Yen (Filtered) Reported | Yen (Filtered) Recalculated | Audit Discrepancy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total OD Corridors** | 25 | 25 | 25 | 25 | 25 | 25 | None (0) |
| **Total Alternatives Generated** | 56 | 56 | 75 | 75 | 2 | 2 | None (0) |
| **Mean Alts per Corridor** | 2.24 | 2.2400 | 3.00 | 3.0000 | 0.08 | 0.0800 | None (0) |
| **Corridors with $\ge 1$ Alt** | 22 (88.0%) | 22 (88.00%) | 25 (100.0%) | 25 (100.00%) | 1 (4.0%) | 1 (4.00%) | None (0) |
| **Corridors with 3 Alts** | 14 (56.0%) | 14 (56.00%) | 25 (100.0%) | 25 (100.00%) | 0 (0.0%) | 0 (0.00%) | None (0) |
| **Corridors with 0 Alts** | 3 (12.0%) | 3 (12.00%) | 0 (0.0%) | 0 (0.00%) | 24 (96.0%) | 24 (96.00%) | None (0) |
| **Mean Primary Overlap (%)** | 49.61% | 49.6104% | 93.23% | 93.2265% | 67.43% | 67.4300% | < 0.01% (Rounding) |
| **Median Primary Overlap (%)** | 50.84% | 50.8400% | 94.61% | 94.6100% | 67.43% | 67.4300% | None (0) |
| **Min Primary Overlap (%)** | 13.91% | 13.9100% | 67.06% | 67.0600% | 67.06% | 67.0600% | None (0) |
| **Max Primary Overlap (%)** | 69.87% | 69.8700% | 99.41% | 99.4100% | 67.80% | 67.8000% | None (0) |
| **Mean Jaccard Similarity** | 0.3536 | 0.3536 | 0.8872 | 0.8872 | 0.5090 | 0.5090 | None (0) |
| **Mean Detour Ratio** | 1.046 | 1.0460 | 1.008 | 1.0085 | 1.0185 | 1.0185 | < 0.001 (Rounding) |
| **Mean Pairwise Diversity** | 0.4932 | 0.4932 | 0.1284 | 0.1284 | 0.4910 | 0.4910 | None (0) |
| **Mean Execution Time (ms)** | 13,736.76 | 13,736.7600 | 86,903.66 | 86,903.6600 | 86,903.66 | 86,903.6600 | None (0) |
| **Speedup Ratio (Offset vs Yen)** | 6.33x | 6.3264x | 1.00x | 1.0000x | — | — | None (Rounding) |

### 3.2 Verification of Candidate Rejection Accounting
In the 25 experimental corridors:
- **Perpendicular Offset:**
  - Total raw candidate route segments evaluated: $25 \times 6 = 150$ offset variations (left/right offsets at $150\text{ m}, 300\text{ m}, 450\text{ m}$).
  - Total candidate routes synthesized: 118 routes.
  - Candidates rejected by **Detour Ratio ($> 1.20$)**: 28 candidates (23.7%).
  - Candidates rejected by **Primary Overlap ($> 70\%$)**: 34 candidates (28.8%).
  - Surviving valid alternatives: **56 candidates** (47.5% acceptance rate).
  - Corridors producing 0 alternatives: Exactly 3 corridors (OD_04 Whitefield railway bottleneck, OD_15 NH 44 elevated expressway funnel, OD_23 Cubbon Park/CBD short grid).
- **Yen's KSP Baseline:**
  - Total routes generated: Exactly 100 paths ($K=4$, comprising 1 primary $+ 3$ alternatives per corridor across 25 corridors).
  - Unfiltered alternatives: **75 alternatives**.
  - Alternatives failing the $\le 70\%$ overlap requirement: **73 out of 75 (97.33%)**.
  - Surviving alternatives under identical 70% filter: **2 alternatives** (OD_12, Frazer Town to Shivajinagar).
  - Corridors producing 0 alternatives under 70% filter: **24 out of 25 (96.0%)**.

**Audit Finding:** All reported summary tables, percentages, candidate rejection counts, and corridor totals are verified against raw experimental data. No runs failed, timed out, or were silently omitted.

---

## 4. Evaluation of Experimental Fairness

### 4.1 Parameter and Environmental Parity
The experimental methodology was inspected for fairness across both algorithms:

| Dimension | Perpendicular Offset | Yen's KSP Baseline | Fair? | Audit Notes |
| :--- | :--- | :--- | :---: | :--- |
| **Graph Network** | `bengaluru_graph.pkl` | `bengaluru_graph.pkl` | **Yes** | Identical 744,216 directed edges. |
| **OD Snapped Nodes** | `ox.nearest_nodes` | `ox.nearest_nodes` | **Yes** | Snapping executed once per corridor; identical node IDs passed to both algorithms. |
| **Edge Cost Function** | `two_wheeler_edge_cost` | `two_wheeler_edge_cost` | **Yes** | Identical OSM highway multipliers and discounts. |
| **Turn Penalties** | `_turn_penalty` ($0, 8, 25$) | `_turn_penalty` ($0, 8, 25$) | **Yes** | Evaluated on identical transition-state space. |
| **Detour Threshold** | $\le 1.20$ | $\le 1.20$ | **Yes** | Both cap alternatives at $+20\%$ physical distance. |
| **Target Route Count** | Up to 3 alternatives | Up to 3 alternatives ($K=4$) | **Yes** | Evaluated on identical route quota. |
| **Timing Scope** | Algorithm execution | Algorithm execution | **Yes** | Both exclude graph unpickling and nearest-node snapping; timing covers route exploration, spur searches, and filtering. |

### 4.2 Fair Apples-to-Apples Comparison: Filtered vs. Unfiltered
A critical fairness question in benchmark reporting is whether comparing filtered Offset against unfiltered Yen is equitable:
1. **The Asymmetry:** Perpendicular Offset actively applies the 70% overlap filter inside its generation loop, rejecting candidates that share $>70\%$ with the primary route. In contrast, standard textbook Yen's KSP is an unconstrained rank-ordered shortest-path search that optimizes cost without intrinsic diversity filtering.
2. **Impact when Filter is Applied to Both:**
   - When the identical $\le 70\%$ overlap requirement is applied to Yen's KSP, **Yen's success rate collapses from 100% to 4.0%** (generating valid alternatives in only 1 of 25 corridors).
   - In 24 of 25 Bengaluru corridors, Yen's 2nd, 3rd, and 4th shortest paths are micro-deviations (e.g., turning through an alley or parallel service lane for 100 meters before rejoining the primary arterial), yielding an average overlap of **93.23%**.
3. **Audit Requirement:** The paper must **never present the raw Yen diversity numbers without clearly noting that Yen was run in standard unconstrained form**, AND must present the filtered comparison showing that standard Yen cannot reliably discover alternative corridors under a 70% overlap ceiling.

---

## 5. Evaluation of Scientific Conclusions

The findings in Phase 10 were audited against the claims intended for academic publication:

### 5.1 Claims Confirmed by Experimental Evidence

1. **Claim: Yen's KSP suffers from the "plateau problem" in urban road networks.**
   - *Status:* **SUPPORTED.**
   - *Evidence:* Across 25 Bengaluru corridors spanning 1.35 km to 17.65 km, Yen's KSP generated alternative routes with a mean physical overlap of **93.23%** (max 99.41%) and mean Jaccard similarity of **0.8872**. This provides empirical confirmation that unconstrained $K$-shortest paths on dense urban grids produce functionally indistinguishable routes.

2. **Claim: Perpendicular offset routing generates significantly more diverse alternatives.**
   - *Status:* **SUPPORTED.**
   - *Evidence:* Perpendicular offset routing achieved an average overlap of **49.61%** with the primary route (a 43.6 percentage point reduction compared to Yen) and an average pairwise diversity of **0.4932** (compared to Yen's 0.1284).

3. **Claim: Perpendicular offset routing is computationally faster than turn-aware Yen's KSP.**
   - *Status:* **SUPPORTED.**
   - *Evidence:* Mean execution time for Perpendicular Offset was **13.74 seconds** compared to **86.90 seconds** for Yen's KSP ($6.33\times$ speedup). The theoretical basis is sound: Yen requires $O(K \cdot N)$ state-expanded A* queries (averaging 250–700 A* queries per corridor), whereas Perpendicular Offset requires at most 24 bounded A* half-leg queries.

4. **Claim: Perpendicular offset routing discovers independent arterial corridors.**
   - *Status:* **SUPPORTED.**
   - *Evidence:* Case studies in radial corridors (e.g., OD_01 Majestic to Whitefield, OD_05 Indiranagar to Electronic City) demonstrate that lateral geometric offsets successfully route vehicles along distinct regional corridors (e.g., Old Airport Road vs. Outer Ring Road vs. Hosur Road) rather than sharing the same primary spine.

### 5.2 Claims That Are NOT Supported or Must Be Restrained

1. **DO NOT CLAIM: "Lower route overlap automatically produces safer or faster two-wheeler routes."**
   - *Reasoning:* Route diversity is an orthogonal geometric and topological property. While lateral offsets force exploration away from congested primary arterials, an alternative route that utilizes secondary or residential streets may incur higher pavement degradation, narrower lane widths, or un-signaled intersections. The safety and impedance profile of alternative routes depends on the cost function weights, not the overlap metric itself.
   - *Guidance:* State that diversity filtering *enables genuine choice* between independent corridors, allowing riders to bypass arterial-level incidents or blockages.

2. **DO NOT CLAIM: "Perpendicular offset routing is universally superior to Yen's KSP across all road networks."**
   - *Reasoning:* The benchmark was conducted on 25 corridors within the Bengaluru metropolitan area. While Bengaluru's road topology exhibits characteristics common to rapidly developing Asian megacities (irregular organic inner networks combined with congested radial arterials and physical railway/drainage barriers), claims of universal superiority across global or grid-iron networks (e.g., Manhattan, Chicago) cannot be made without broader geographic sampling.
   - *Guidance:* Confine claims specifically to "complex, organically developed metropolitan road networks such as Bengaluru."

3. **DO NOT CLAIM: "Perpendicular offset routing guarantees that accepted alternatives are mutually diverse from one another."**
   - *Reasoning:* As identified in Section 1.4, candidate filtering is performed pairwise between each candidate and the primary route ($P_{\text{primary}}$). Two accepted alternatives may share substantial overlap with each other along an adjacent parallel corridor.
   - *Guidance:* Accurately describe the filter as a *Primary-Referenced Overlap Filter* with duplicate sequence suppression.

---

## 6. Required Adjustments & Recommendations for IEEE Paper

Before integrating Phase 10 results into the final IEEE paper draft, the following specific adjustments must be observed:

1. **Clarify Terminology:** Explicitly define the filtering mechanism as the **Primary-Referenced 70% Edge-Overlap Filter ($\text{PROF}_{70}$)**:
   $$\text{PROF}_{70}(P_{\text{alt}}) = \begin{cases} \text{Accept}, & \text{if } \frac{\|E(P_{\text{primary}}) \cap E(P_{\text{alt}})\|}{\|E(P_{\text{alt}})\|} \le 0.70 \text{ and } \frac{\text{Length}(P_{\text{alt}})}{\text{Length}(P_{\text{primary}})} \le 1.20 \\ \text{Reject}, & \text{otherwise} \end{cases}$$
2. **Present Dual Yen Baselines in Tables:** In the paper's comparison table, include both **Standard Yen ($K=4$)** and **Yen with $\text{PROF}_{70}$ Filter**:
   - Showing standard Yen highlights the severity of the plateau problem (93.2% overlap).
   - Showing filtered Yen demonstrates that standard $K$-shortest paths cannot serve as an effective alternative route generator when diversity is mandated (96% corridor failure rate).
3. **Discuss Bottleneck Failure Modes:** Highlight the 3 corridors where Perpendicular Offset generated 0 alternatives (OD_04, OD_15, OD_23). Explaining that severe physical constraints (e.g., railway bridge bottlenecks or narrow lake causeways) leave no viable detour within $+20\%$ distance is a strength of the analysis that reinforces the physical validity of the engine.
4. **Computational Complexity Note:** Explain that while turn-aware Yen's KSP requires hundreds of state-expanded A* spur searches, Perpendicular Offset decouples route generation into bounded geometric waypoint queries, reducing computational latency by over $84\%$.

---

## 7. Audit Sign-Off

- **Source Code Verification:** Complete.
- **Mathematical Validation:** Complete.
- **Experimental Recalculation:** Complete.
- **No Unintended Changes Made:** Verified.

**Verdict:** Phase 10 is **OFFICIALLY AUDITED, VERIFIED, AND APPROVED**.

*No further implementation or modification of Phase 10 files is required. Awaiting user authorization to proceed to Phase 11.*