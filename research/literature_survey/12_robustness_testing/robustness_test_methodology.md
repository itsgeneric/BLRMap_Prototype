# Robustness and Edge-Case Testing Methodology

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 12 — Robustness and Edge-Case Testing  
**Date:** March 2026 / Local Execution: November 4, 2026  
**Document:** [`robustness_test_methodology.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/robustness_test_methodology.md)  
**Test Harness:** [`experiments/robustness_testing/run_robustness_tests.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/run_robustness_tests.py)  
**Synthetic Fixtures:** [`experiments/robustness_testing/synthetic_fixtures.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/synthetic_fixtures.py)  

---

## 1. Executive Overview and Scope

Phase 12 conducts an exhaustive empirical evaluation of the reliability, mathematical correctness, boundary condition stability, and failure handling of the Two-Wheeler Routing Engine under difficult road-network conditions and challenging origin-destination scenarios.

Following the audited and finalized algorithmic enhancements of Phase 9 (Admissible $A^*$ Heuristic Correction), Phase 10 (Alternative Route Diversity & Overlap Filtering), and Phase 11 (25-Corridor Quality Evaluation & Parameter Sensitivity), Phase 12 focuses strictly on **testing and validation**. In accordance with Phase 12 constraints:
- **No production code is modified** ([`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py), and [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) remain untouched).
- **No graph edge weights, costs, or routing parameters are altered**.
- **No previous benchmark datasets from Phases 9, 10, or 11 are overwritten**.
- **All unexpected results, failures, and boundary anomalies are preserved transparently** without silent workarounds.

---

## 2. Testing Taxonomy and Suite Architecture

The Phase 12 evaluation framework is organized into four complementary testing suites comprising 26 formal test cases:

```
Phase 12 Robustness Matrix (26 Tests)
├── Suite A: Road Network Integrity (Bengaluru Graph) [7 Tests: ROB-NET-01 to 07]
│   ├── One-way directionality enforcement
│   ├── Bidirectional street traversal symmetry
│   ├── Restricted access tag auditing & purge verification
│   ├── Missing geometry filling & LineString continuity
│   ├── Strongly connected component & partition failure handling
│   ├── Parallel edges & divided carriageway separation
│   └── Dead-end / cul-de-sac leaf node navigation
├── Suite B: Origin-Destination Edge Cases (Bengaluru Graph) [7 Tests: ROB-OD-01 to 07]
│   ├── Identical origin and destination (s == e)
│   ├── Ultra-short commute (< 50m)
│   ├── Trans-metropolitan long-distance journey (> 35km / 58km span)
│   ├── Network boundary / peripheral coordinate snapping
│   ├── Unreachable destination under network severance
│   ├── Out-of-bounds extraterritorial coordinates (Bay of Bengal)
│   └── Central business district dense grid micro-trip
├── Suite C: Alternative Routing Robustness (Perpendicular Offset) [6 Tests: ROB-ALT-01 to 06]
│   ├── Metropolitan grid corridor (OD_01 BNMIT to MG Road)
│   ├── Lake/railway infrastructure choke point (OD_04 Whitefield-Marathahalli)
│   ├── Dense radial grid corridor (OD_06 Jayanagar to Majestic)
│   ├── Short inner-city corridor (OD_12 Frazer Town to Shivajinagar)
│   ├── Linear highway spine without parallel roads (OD_15 Yelahanka to Hebbal)
│   └── Graceful degradation under zero surviving alternatives
└── Suite D: Synthetic Graph Validation (Isolated Controlled Fixtures) [6 Tests: ROB-SYN-01 to 06]
    ├── Linear one-way corridor without reverse path
    ├── Disconnected graph components
    ├── Multiple parallel corridors with road-type/turn cost ranking
    ├── Dead-end road / cul-de-sac traversal and avoidance
    ├── Detour tolerance constraint enforcement (detour > 1.20)
    └── Shared edge overlap threshold enforcement (overlap > 70%)
```

---

## 3. Mathematical and Algorithmic Formulations

### 3.1 Directed Edge Traversal and Path Continuity
A route $R = [v_0, v_1, \dots, v_k]$ is mathematically valid if and only if every consecutive node pair forms a valid directed edge in the graph:
$$\forall i \in \{0, \dots, k-1\}, \quad (v_i, v_{i+1}) \in E(G)$$
For any strictly one-way edge where $(u, v) \in E(G)$ but $(v, u) \notin E(G)$, any reverse traversal query from $v$ to $u$ must strictly route via an alternative legal cycle in $G$ or raise a `NetworkXNoPath` exception. Traversing $(v, u)$ in reverse is mathematically prohibited.

### 3.2 State Transition Cost and Turn Penalty Function
The pathfinding engine operates on the state space of directed transitions $S = (p, u)$ where $p$ is the predecessor node and $u$ is the current node. The cost of transitioning from state $(p, u)$ to state $(u, v)$ is:
$$c((p, u) \to (u, v)) = c_{\text{edge}}(u, v) + c_{\text{turn}}(p, u, v)$$
Where edge traversal impedance is defined by:
$$c_{\text{edge}}(u, v) = \ell(u, v) \cdot \mu_{\text{highway}} \cdot \mu_{\text{bridge}} \cdot \mu_{\text{roundabout}} \cdot \mu_{\text{surface}}$$
And the maneuver penalty function $c_{\text{turn}}(p, u, v)$ evaluates the bearing deflection angle $\Delta \theta = |\theta_{\text{in}} - \theta_{\text{out}}| \pmod{360}$:
$$c_{\text{turn}}(p, u, v) = \begin{cases} 
25.0 & \text{if } \Delta \theta \ge 60^\circ \quad (\text{Sharp Turn}) \\
8.0 & \text{if } 30^\circ \le \Delta \theta < 60^\circ \quad (\text{Moderate Turn}) \\
0.0 & \text{if } \Delta \theta < 30^\circ \quad (\text{Straight / Negligible})
\end{cases}$$

### 3.3 Physical Route Distance vs. Geometric Heuristic
Physical cumulative distance $D(R)$ strictly evaluates edge attributes:
$$D(R) = \sum_{i=0}^{k-1} \min_{k} \left\{ \text{length}(e_{v_i, v_{i+1}, k}) \right\}$$
The Euclidean/Haversine heuristic $h(u, \text{goal})$ provides admissible lower bounds scaled by the global minimum cost floor ($\mu_{\min} = 0.8$):
$$h(u, \text{goal}) = 0.8 \cdot \text{haversine}(u, \text{goal})$$

### 3.4 Alternative Route Filtering Criteria
For any candidate alternative route $R_{\text{alt}}$ evaluated against the primary route $R_{\text{prim}}$:
1. **Physical Detour Ratio Constraint:**
   $$\delta(R_{\text{alt}}) = \frac{D(R_{\text{alt}})}{D(R_{\text{prim}})} \le 1.20$$
2. **Shared Edge Overlap Constraint:**
   $$\Omega(R_{\text{prim}}, R_{\text{alt}}) = \frac{\sum_{e \in E(R_{\text{prim}}) \cap E(R_{\text{alt}})} \text{length}(e)}{D(R_{\text{alt}})} \le 0.70$$
3. **Exact Sequence Duplicate Suppression:**
   $$\text{tuple}(R_{\text{alt}}) \notin \mathcal{H}_{\text{seen}}$$

---

## 4. Test Harness Implementation and Environment

### 4.1 System Environment
- **Host OS:** Windows 11 Enterprise (x64)
- **Python Runtime:** Python 3.13.0
- **Graph Topology:** `bengaluru_graph.pkl` (308,643 nodes, 744,216 directed edges)
- **Dependencies:** `networkx` 3.4.2, `osmnx` 1.9.4, `shapely` 2.0.6

### 4.2 Logging and Record Schema
Every test execution records the following 8 standardized fields in both [`robustness_test_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/robustness_test_results.json) and [`robustness_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/robustness_test_results.csv):
1. `test_id`: Unique identifier (e.g., `ROB-NET-01`, `ROB-OD-01`, `ROB-ALT-01`, `ROB-SYN-01`).
2. `suite`: Testing category name.
3. `condition`: Specific network topology, coordinate configuration, or edge case under test.
4. `expected`: Precise expected mathematical or behavioral outcome.
5. `actual`: Measured empirical result, including node counts, distances, runtimes, or raised exceptions.
6. `status`: Binary classification (`PASS` or `FAIL`).
7. `error`: Traceback or exception string if an unhandled failure occurred.
8. `limitation`: Inherent algorithmic, geometric, or architectural limitation identified by the test.

---

## 5. Pass/Fail Decision Criteria

| Severity Level | Definition | Benchmark Impact | Handling Rule |
| :--- | :--- | :--- | :--- |
| **FATAL CRASH** | Unhandled process crash, unhandled Python exception, or infinite loop/deadlock. | Immediate Suite Failure | Recorded as FAIL; requires root cause documentation. |
| **INTEGRITY VIOLATION** | Route traverses a one-way edge backward, traverses private roads, or contains disconnected hops. | Immediate Suite Failure | Recorded as FAIL; invalidates routing correctness. |
| **THRESHOLD BREACH** | Surviving candidate violates detour cap ($> 1.20$) or overlap threshold ($> 0.70$). | Filter Pipeline Failure | Recorded as FAIL. |
| **EMPIRICAL ANOMALY** | System behaves deterministically but diverges from naive geometric expectations (e.g. extreme circuity due to one-way CBD network). | Informational / Architectural | Recorded transparently with status and limitation analysis. |
| **DOCUMENTED VULNERABILITY** | Boundary vulnerability documented without code crash (e.g., unconstrained KDTree coordinate projection). | Architectural Limitation | Recorded as PASS with explicit vulnerability disclosure. |
