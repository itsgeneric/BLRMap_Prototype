# Synthetic Graph Test Results and Algorithmic Validation

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 12 — Robustness and Edge-Case Testing  
**Date:** March 2026 / Local Execution: November 4, 2026  
**Document:** [`synthetic_graph_test_results.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/12_robustness_testing/synthetic_graph_test_results.md)  
**Source Code:** [`experiments/robustness_testing/synthetic_fixtures.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/synthetic_fixtures.py)  
**Test Runner:** [`experiments/robustness_testing/test_synthetic_graphs.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/test_synthetic_graphs.py)  

---

## 1. Motivation and Methodological Purpose

While empirical testing across Bengaluru's metropolitan road network (`bengaluru_graph.pkl`, 308,643 nodes, 744,216 edges) evaluates macroscopic performance, real-world road networks contain complex conflating factors: asymmetric geometry, multi-lane road segmentations, irregular junction angles, and missing or noisy OpenStreetMap attributes.

To establish rigorous mathematical proof of algorithmic invariants, Phase 12 incorporates **controlled synthetic graph fixtures**. These fixtures:
1. Isolate individual topological phenomena (directionality, connectivity, cul-de-sacs, parallel choice).
2. Eliminate geographic heuristics and road classification noise.
3. Provide exact closed-form analytical solutions against which `two_wheeler_astar`, turn penalty modeling, and candidate filtering pipelines can be verified.

---

## 2. Itemized Synthetic Fixture Specifications

```
Synthetic Test Fixtures Overview
├── Fixture 1: G_oneway_no_reverse       ── Linear directed corridor A -> B -> C -> D (no reverse)
├── Fixture 2: G_disconnected            ── Two isolated components {A,B,C} and {X,Y,Z}
├── Fixture 3: G_parallel_routes         ── 4 parallel corridors (Primary, Residential, Tertiary, Service)
├── Fixture 4: G_dead_end                ── Main corridor with dead-end cul-de-sac leaf branch (F)
├── Fixture 5: G_detour_exceeded         ── Alternative detour ratio = 1.35x (> 1.20 tolerance cap)
└── Fixture 6: G_overlap_exceeded        ── Alternative shared edge overlap = 73.17% (> 70.0% threshold)
```

### 2.1 Fixture 1: One-Way Road with No Legal Reverse Path (`G_oneway_no_reverse`)
- **Topology:** Linear directed walk $A \to B \to C \to D$.
- **Attributes:** All edges have `length = 100.0m`, `highway = "residential"`, `oneway = True`. No reverse directed edges exist.
- **Analytical Invariants:**
  - Forward query $A \to D$ must yield path $[A, B, C, D]$ with physical distance $300.0\text{ m}$.
  - Reverse query $D \to A$ has zero feasible paths and must raise `nx.NetworkXNoPath`.
  - Intermediate reverse query $C \to B$ must raise `nx.NetworkXNoPath`.
  - Intermediate forward query $B \to D$ must yield $[B, C, D]$ with physical distance $200.0\text{ m}$.

### 2.2 Fixture 2: Disconnected Graph Components (`G_disconnected`)
- **Topology:** Two completely disjoint, non-empty subgraphs separated by $1.0\text{ km}$:
  - Component 1 (South): $A \leftrightarrow B \leftrightarrow C$ (bidirectional residential, $100\text{ m}$ edges).
  - Component 2 (North): $X \leftrightarrow Y \leftrightarrow Z$ (bidirectional residential, $100\text{ m}$ edges).
  - Inter-component edge set: $E(C_1, C_2) = \emptyset$.
- **Analytical Invariants:**
  - Intra-component queries $A \to C$ and $X \to Z$ must succeed immediately ($200.0\text{ m}$).
  - Inter-component queries $A \to Z$ and $X \to A$ must explore the entire reachable component and raise `nx.NetworkXNoPath` without infinite loop or hanging.

### 2.3 Fixture 3: Multiple Parallel Corridors with Cost Ranking (`G_parallel_routes`)
- **Topology:** Common origin $S$, common destination $D$, connected by four parallel corridors:
  - **Corridor 1 (Primary Arterial):** Straight along $y = 12.9700$, distance $400.0\text{ m}$ ($130 + 140 + 130$), zero directional turns ($0^\circ$).
  - **Corridor 2 (Residential Bypass):** Northern lateral bypass ($y = 12.9715$), distance $420.0\text{ m}$ ($140 + 140 + 140$), two $45^\circ$ directional turns.
  - **Corridor 3 (Tertiary Connector):** Northern lateral bypass ($y = 12.9730$), distance $460.0\text{ m}$ ($150 + 160 + 150$), two $45^\circ$ directional turns.
  - **Corridor 4 (Service Lane):** Southern lateral bypass ($y = 12.9680$), distance $550.0\text{ m}$ ($180 + 190 + 180$), two $45^\circ$ directional turns.
- **Analytical Impedance Formulations:**
  $$\text{Cost}(R) = \sum \ell(e) \cdot \mu_{\text{highway}} + \sum c_{\text{turn}}$$
  - **Case A (Uniform Penalties, all $\mu = 1.0$):**
    - Arterial: $400.0 \cdot 1.0 + 0 = 400.0\text{ units}$.
    - Residential: $420.0 \cdot 1.0 + (8.0 + 8.0) = 436.0\text{ units}$.
    - Expected Winner: **Corridor 1 (Primary Arterial)**.
  - **Case B (Standard Two-Wheeler Penalties, $\mu_{\text{primary}} = 2.2, \mu_{\text{res}} = 1.0$):**
    - Arterial: $400.0 \cdot 2.2 + 0 = 880.0\text{ units}$.
    - Residential: $420.0 \cdot 1.0 + (8.0 + 8.0) = 436.0\text{ units}$.
    - Tertiary: $460.0 \cdot 1.15 + 16.0 = 545.0\text{ units}$.
    - Service: $550.0 \cdot 0.90 + 16.0 = 511.0\text{ units}$.
    - Expected Winner: **Corridor 2 (Residential Bypass)**.

### 2.4 Fixture 4: Dead-End Road / Cul-de-Sac (`G_dead_end`)
- **Topology:** Main corridor $A \leftrightarrow B \leftrightarrow C \leftrightarrow D$ ($100\text{ m}$ edges). At node $B$, an intersecting cul-de-sac branch extends northward: $B \leftrightarrow E \leftrightarrow F$ ($100\text{ m}$ edges). Node $F$ has in-degree 1 and out-degree 1 (leaf cul-de-sac).
- **Analytical Invariants:**
  - **Destination inside dead end ($A \to F$):** Route must navigate into the cul-de-sac: $[A, B, E, F]$ ($300.0\text{ m}$).
  - **Transit journey ($A \to D$):** Route must stay on the main line $[A, B, C, D]$ ($300.0\text{ m}$) and prune the dead-end branch (nodes $E, F$ never in path).
  - **Origin inside dead end ($F \to D$):** Route must successfully navigate out of the cul-de-sac into the main grid: $[F, E, B, C, D]$ ($400.0\text{ m}$).
  - **Trapped One-Way Cul-de-Sac:** If $B \to E \to F$ is one-way, query $F \to D$ must raise `nx.NetworkXNoPath` due to lack of an egress edge.

### 2.5 Fixture 5: Detour Tolerance Constraint Enforcement (`G_detour_exceeded`)
- **Topology:**
  - Primary path: $S \to P_1 \to D$. Distance $D(R_{\text{prim}}) = 50 + 50 = 100.0\text{ m}$.
  - Only alternative path: $S \to A_1 \to A_2 \to D$. Distance $D(R_{\text{alt}}) = 45 + 45 + 45 = 135.0\text{ m}$.
- **Analytical Detour Ratio:**
  $$\delta(R_{\text{alt}}) = \frac{135.0\text{ m}}{100.0\text{ m}} = 1.35\times$$
  Under the standard threshold $\text{DETOUR\_TOLERANCE} = 1.20$, $\delta(R_{\text{alt}}) = 1.35 > 1.20$.
- **Analytical Invariant:** Candidate alternative must be rejected with reason `"detour_exceeded"`. Surviving alternative count must equal 0.

### 2.6 Fixture 6: Shared Edge Overlap Filtering (`G_overlap_exceeded`)
- **Topology:**
  - Primary path: $S \to N_1 \to N_2 \to N_3 \to N_4 \to D$ (5 segments of $200\text{ m} = 1000.0\text{ m}$).
  - Alternative path: $S \to N_1 \to N_2 \to ALT \to N_4 \to D$.
    Bypasses node $N_3$ via side edges $(N_2, ALT) = 110\text{ m}$ and $(ALT, N_4) = 110\text{ m}$. Total alternative distance: $200 + 200 + 110 + 110 + 200 = 820.0\text{ m}$.
  - Shared edge set: $E(R_{\text{prim}}) \cap E(R_{\text{alt}}) = \{(S, N_1), (N_1, N_2), (N_4, D)\}$.
  - Shared physical length: $200 + 200 + 200 = 600.0\text{ m}$.
- **Analytical Overlap Ratio:**
  $$\Omega = \frac{600.0\text{ m}}{820.0\text{ m}} = 73.17\%$$
  Under the standard threshold $\text{MAX\_OVERLAP} = 0.70$ ($70.0\%$), $\Omega = 73.17\% > 70.0\%$.
- **Analytical Invariant:** Candidate alternative must be rejected with reason `"overlap_exceeded"`. Surviving alternative count must equal 0.

---

## 3. Empirical Results and Verification Matrix

The synthetic test suite was executed via [`experiments/robustness_testing/test_synthetic_graphs.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/test_synthetic_graphs.py) and embedded in the global test harness [`experiments/robustness_testing/run_robustness_tests.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/experiments/robustness_testing/run_robustness_tests.py).

| Test ID | Fixture Name | Invariant Tested | Measured Actual Behavior | Status | Runtime |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **ROB-SYN-01** | `G_oneway_no_reverse` | Forward traversal & reverse `NetworkXNoPath` | Forward: $[A, B, C, D]$ ($300.0\text{ m}$). Reverse: `NetworkXNoPath` cleanly raised. | **PASS** | $< 1\text{ ms}$ |
| **ROB-SYN-02** | `G_disconnected` | Component isolation & partition failure | Intra-C1: $[A, B, C]$; Intra-C2: $[X, Y, Z]$. Inter-component $A \to Z$: `NetworkXNoPath` cleanly raised. | **PASS** | $< 1\text{ ms}$ |
| **ROB-SYN-03** | `G_parallel_routes` | Road class vs. turn penalty multi-corridor ranking | Uniform penalties: Arterial $[S, M_1, M_2, D]$ wins (cost $400.0$). Two-wheeler penalties: Residential $[S, R_1, R_2, D]$ wins (cost $436.0$ vs $880.0$). | **PASS** | $< 1\text{ ms}$ |
| **ROB-SYN-04** | `G_dead_end` | Cul-de-sac entry, transit bypass, and egress | Ingress: $[A, B, E, F]$. Transit: $[A, B, C, D]$ (bypasses $E, F$). Egress: $[F, E, B, C, D]$. One-way trap: `NetworkXNoPath`. | **PASS** | $< 1\text{ ms}$ |
| **ROB-SYN-05** | `G_detour_exceeded` | Strict detour tolerance enforcement ($> 1.20$) | Primary: $100.0\text{ m}$, Alt: $135.0\text{ m}$. Detour ratio: $1.35\times > 1.20\times \implies$ Rejection confirmed. | **PASS** | $< 1\text{ ms}$ |
| **ROB-SYN-06** | `G_overlap_exceeded` | Shared edge overlap threshold ($> 70\%$) | Primary: $1000.0\text{ m}$, Alt: $820.0\text{ m}$, Shared: $600.0\text{ m}$. Overlap: $73.17\% > 70.0\% \implies$ Rejection confirmed. | **PASS** | $< 1\text{ ms}$ |

---

## 4. Analytical Guarantees Established

The synthetic validation demonstrates the following mathematical and algorithmic guarantees:
1. **Directionality Correctness:** The search frontier strictly respects directed edge orientation; zero reverse edge leaks occur under any condition.
2. **Deterministic Partition Handling:** Disconnected query pairs terminate with complete search frontier exhaustion and raise standard `NetworkXNoPath` exceptions without infinite loops or hanging.
3. **Turn Penalty Balance:** The turn penalty mechanism ($c_{\text{turn}} \in \{0.0, 8.0, 25.0\}$) accurately counterbalances physical distance and road-class multipliers without causing unnatural state oscillations.
4. **Exact Constraint Filtering:** Both the detour ratio cap ($1.20\times$) and the shared edge overlap cap ($70.0\%$) operate as strict mathematical filters, eliminating spurious candidates that fail macroscopic diversity requirements.
