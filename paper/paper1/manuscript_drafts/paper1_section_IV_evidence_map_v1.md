# Section IV Evidence Map — Code Traceability and Epistemological Audit (v1.0)

**Document:** [`paper1_section_IV_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_evidence_map_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1 — Section IV Structural Planning and Mathematical Admissibility Evidence Map  
**Date:** 2026-11-06  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Source Code References:** [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py), [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py)  
**Serialized Graph Dataset:** [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE CODE TRACEABILITY AND MATHEMATICAL EVIDENCE MAP**

---

## 1. Codebase Traceability Matrix

Every algorithmic mechanism, data structure, priority queue operation, and mathematical guarantee in Section IV maps directly to concrete source lines in [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py).

| Section IV Mathematical Element | Symbolic Notation | Implementation Variable / Function | Codebase File | Exact Line Numbers | Implementation Logic / Code Excerpt |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Heuristic Multiplier Floor** | $\mu_{\min}$ | `MIN_PENALTY_FLOOR` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L28) | Line 28 | `MIN_PENALTY_FLOOR = 0.8` |
| **Spherical Haversine Distance** | $D_{\text{haversine}}$ | `haversine_m(lat1, lng1, lat2, lng2)` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L45-L60) | Lines 45–60 | Great-circle distance using spherical haversine formula with radius $R = 6,371,000\text{ m}$ |
| **Admissible Heuristic Mode** | $h(s)$ (Eq. 4) | `heuristic(node)` with `heuristic_mode="admissible"` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L500-L513) | Lines 500–513 | `h_dist = haversine_m(...); if heuristic_mode == "admissible": return h_dist * MIN_PENALTY_FLOOR` |
| **Synthetic Origin State** | $s_0^{\text{state}}$ | `start_state = (initial_previous_node, start_node)` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L522-L525) | Lines 522–525 | State initialized as `(None, start_node)` representing zero departure direction |
| **Tentative Cost Map** | $g(s)$ | `g_score = {start_state: 0.0}` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L527-L529) | Lines 527–529 | Dictionary storing minimal discovered cost from origin to state $s$ |
| **Backpointer Map** | $\pi(s)$ | `came_from = {}` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L531) | Line 531 | Dictionary storing predecessor state for path reconstruction |
| **Tie-Breaker Counter** | $\kappa$ | `counter = itertools.count()` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L533) | Line 533 | Monotonic integer sequence guaranteeing FIFO priority queue tie-breaking |
| **Priority Queue Init** | $\mathcal{Q}$ | `open_set = []`; `heapq.heappush(open_set, (heuristic(start_node), next(counter), start_state))` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L535-L544) | Lines 535–544 | Min-heap entry structured as 3-tuple `(priority, counter, state)` |
| **State Extraction** | Pop $s$ | `_, _, state = heapq.heappop(open_set)` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L552-L554) | Lines 552–554 | Popping minimal $f$-score state $(u, v)$ |
| **State Unpacking** | $(u, v)$ | `previous_node, current_node = state` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L557) | Line 557 | Unpacks predecessor node $u$ and current intersection $v$ |
| **Target Reached Check** | Goal Test | `if current_node == end_node:` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L566) | Line 566 | Halts search loop immediately without evaluating exit turn penalties |
| **Path Reconstruction** | Path $P$ | Backtracking `came_from` loop and reversing `route` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L568-L591) | Lines 568–591 | Traverses backpointers from goal state back to synthetic origin state |
| **Successor Exploration** | Successors | `for next_node in graph.successors(current_node):` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L611-L613) | Lines 611–613 | Iterates over physical outbound neighbours of intersection $v$ |
| **Multigraph Parallel Cost** | $c_{\min}(v, w)$ | `min(two_wheeler_edge_cost(data, ...) for data in edge_data.values())` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L645-L655) | Lines 645–655 | Resolves multi-edge records to minimal complete impedance edge cost |
| **Turn Penalty Computation** | $P_{\text{turn}}$ | `turn_cost = _turn_penalty(graph, previous_node, current_node, next_node)` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L661-L666) | Lines 661–666 | Computes chord deflection $\Delta\theta(u, v, w)$ and returns $\{0.0, 8.0, 25.0\}$ |
| **Transition Cost Addition** | $c(s, s')$ | `new_cost = current_cost + edge_cost + turn_cost` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L668-L672) | Lines 668–672 | Accrues transition cost strictly according to Equation (3) |
| **Successor State Packaging** | $s'$ | `next_state = (current_node, next_node)` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L674-L677) | Lines 674–677 | Constructs successor directed edge-state $(v, w)$ |
| **Relaxation Test** | Relaxation | `if next_state not in g_score or new_cost < g_score[next_state]:` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L679-L682) | Lines 679–682 | Filters out non-improving paths to state $(v, w)$ |
| **Score & Pointer Update** | Record $g(s')$ | `g_score[next_state] = new_cost; came_from[next_state] = state` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L684-L686) | Lines 684–686 | Updates minimal tentative cost and predecessor link |
| **Priority Evaluation** | $f(s')$ | `priority = new_cost + heuristic(next_node)` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L688-L691) | Lines 688–691 | Evaluates $f(s') = g(s') + h(s')$ |
| **Heap Insertion** | Push $s'$ | `heapq.heappush(open_set, (priority, next(counter), next_state))` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L693-L700) | Lines 693–700 | Inserts relaxed state into binary min-heap without `decrease-key` |

---

## 2. Empirical Ground-Truth Graph Evidence

The theoretical valence and complexity claims in Subsection IV-D are grounded in direct measurements from the serialized Bengaluru road network ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)).

| Graph Metric | Mathematical Symbol | Exact Ground-Truth Value | Source / Verification Method | Scholarly Significance |
| :--- | :---: | :---: | :--- | :--- |
| **Physical Vertices** | $\|V\|$ | $308,643$ | `len(graph.nodes)` | Number of physical intersections and curve shape points |
| **Raw Multigraph Edges** | $\|E_{\text{raw}}\|$ | $744,216$ | `graph.number_of_edges()` | Total directed edge records in raw OSM extraction |
| **Effective Directed Edges** | $\|E_s\|$ | $740,822$ | Distinct adjacent node pairs | Routing graph size after collapsing parallel multigraph edges |
| **State Space Size** | $\|S\|$ | $740,823$ | $\|E_s\| + 1$ | Directed edge-states plus synthetic departure state $s_0^{\text{state}}$ |
| **Valid State Transitions** | $\|E_S\|$ | $2,103,894$ | $\sum_{v} d_{\text{in}}(v) \cdot d_{\text{out}}(v) + d_{\text{out}}(s_0)$ | Exact transition space size; represents $2.84 \times \|E_s\|$ |
| **Maximum In-Degree** | $d_{\max}^{\text{in}}$ | $6$ | $\max_{v} d_{\text{in}}(v)$ | Maximum incoming roadways converging at any physical intersection |
| **Maximum Out-Degree** | $d_{\max}^{\text{out}}$ | $6$ | $\max_{v} d_{\text{out}}(v)$ | Maximum outgoing roadways diverging from any physical intersection |
| **Mean Physical Degree** | $\bar{d}$ | $2.41$ | $\|E_s\| / \|V\|$ | Verifies sparse near-planar terrestrial road network |
| **Bridge-Roundabout Co-Occurrences** | $N_{\text{overlap}}$ | $0$ | Exhaustive attribute scan | Verifies $\mu(e) \ge 0.80$ holds strictly across entire corpus |

---

## 3. Epistemological and Architectural Demarcations

In accordance with [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), the following boundaries are formally audited:

1. **Static Graph Search Guarantee:**
   The algorithm executes single-threaded static shortest-path search on a fixed graph snapshot. No dynamic edge reweighting occurs during execution.
2. **Absence of Re-Opening Logic:**
   Because the heuristic is proven monotonically consistent (Theorem 2), the implementation does not require a `closed_set` removal or state-reopening loop. The first extraction of state $(u, v)$ from `open_set` is provably optimal.
3. **Min-Heap Without `decrease-key`:**
   Because Python's standard `heapq` does not implement `decrease-key`, when a cheaper path to state $(v, w)$ is discovered before an earlier entry is popped, a duplicate entry is pushed to the heap. As established in Theorem 3, the number of such duplicate entries is bounded by $d_{\text{in}}(v) \le 6 = \mathcal{O}(1)$, preserving $\mathcal{O}(|E_s|)$ memory and $\mathcal{O}(|E_s| \log |E_s|)$ time.
4. **Exclusion of Uncalibrated Queue Filtering:**
   The exploratory functions `count_filterable_junctions` and `apply_filtering_discount` in [`routing/algorithms.py#L174-L234`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L174-L234) are confirmed **completely uncalled** in `two_wheeler_astar` and are excluded from Section IV.
