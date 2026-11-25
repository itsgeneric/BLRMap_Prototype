# Phase 13.0 — Controlled Ablation Study: Experimental Design and Preflight Audit

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 13.0 — Controlled Ablation Study: Experimental Design & Preflight Audit  
**Date:** March 2026 / Local Execution: November 4, 2026  
**Document:** [`phase_13_0_experimental_design.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_0_experimental_design.md)  
**Correction Addendum:** [`phase_13_0_1_correction_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_0_1_correction_report.md)  
**Status:** Preflight Experimental Design (Strictly Read-Only / No Code Modifications / No Execution)  

---

## 1. Executive Summary & Objective

The objective of Phase 13 is to conduct a scientifically defensible, statistically rigorous **Controlled Ablation Study** that quantifies and isolates the individual contribution of each architectural component within the Two-Wheeler-Aware Routing system.

Up to Phase 12.2, the routing engine was evaluated as a holistic system combining road impedance weights, turn penalties, grade/junction modifiers, and geometric alternative generation. While prior phases established superior route safety, residential road bias, and computational efficiency over classical baselines (Dijkstra and Yen's KSP), holistic benchmarking cannot determine:
1. *How much of the observed maneuver reduction is attributable strictly to turn-awareness vs. road-class hierarchy.*
2. *Whether flyover and roundabout modifiers create statistically significant route diversions or act as minor edge adjustments.*
3. *How sensitive the routing engine is to varying turn penalty magnitudes.*
4. *How perpendicular-offset via-node generation compares against Yen's K-Shortest Paths when both are evaluated with and without edge-overlap pruning.*

**Phase 13.0 Mandate:**  
In strict compliance with project governance:
- **No production code files are modified.**
- **No test files or benchmark datasets are altered.**
- **No experiment execution is performed in this phase.**
- **No parameters are tuned to maximize outcomes.**
- **Phase 13.1 execution remains blocked until this design document is reviewed and formally authorized.**

---

## 2. Implementation Inventory of Routing Components

An exhaustive code audit of [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py), and [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) establishes the exact implementation details, parameter bounds, default values, and operational dependencies of each component under study.

### 2.1 State-Expanded, Turn-Aware A* (`two_wheeler_astar`)
- **File & Lines:** [`routing/algorithms.py#L460-L704`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L460-L704)
- **Signature:**
  ```python
  def two_wheeler_astar(
      graph,
      start_node,
      end_node,
      graph_mgr,
      penalties=None,
      congested_nodes=None,
      heuristic_mode="admissible",
      return_metrics=False,
      initial_previous_node=None,
      banned_nodes=None,
      banned_edges=None
  )
  ```
- **State Representation:** State space is expanded from vertex space $V$ to directed edge transitions $E$:
  $$\text{state} = (u_{\text{prev}}, v_{\text{curr}}) \in (V \cup \{\text{None}\}) \times V$$
- **Transition Cost Formulation:** For transition from $(u, v)$ to $(v, w)$:
  $$c\big((u, v) \to (v, w)\big) = c_{\text{edge}}(v, w) + P_{\text{turn}}(u, v, w)$$
- **Default Parameters:** `heuristic_mode="admissible"`, `return_metrics=False`, `initial_previous_node=None`.
- **Dependencies:** [`two_wheeler_edge_cost`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L266), [`_turn_penalty`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L146), [`haversine_m`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L45), [`_dedupe_nodes`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L896).

### 2.2 A* Heuristic Modes
- **File & Lines:** [`routing/algorithms.py#L500-L518`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L500-L518)
- **Mathematical Formulations:**
  1. **Standard Admissible (Default):**
     $$h_{\text{admissible}}(n) = \text{haversine}(n, \text{goal}) \times \text{MIN\_PENALTY\_FLOOR} = 0.8 \cdot \text{haversine}(n, \text{goal})$$
     *Admissibility Guarantee:* Because the absolute lowest impedance multiplier on any edge in the network is $0.8$ (a bridge on an arterial road), scaling Haversine distance by $0.8$ strictly ensures $h(n) \le c^*(n, \text{goal})$, guaranteeing optimal paths.
  2. **Aggressive (Legacy Phase 8):**
     $$h_{\text{aggressive}}(n) = \frac{\text{haversine}(n, \text{goal})}{\text{MIN\_PENALTY\_FLOOR}} = 1.25 \cdot \text{haversine}(n, \text{goal})$$
     Overestimates true shortest cost; acts as a goal-directed greedier search with possible suboptimality (empirically up to $+4.90\%$).
  3. **Dijkstra / Zero Heuristic:**
     $$h_{\text{zero}}(n) = 0.0$$
     Uniform-cost search baseline providing mathematical ground truth.

### 2.3 Two-Wheeler Road Impedance Weights
- **File & Lines:** [`core/config.py#L61-L77`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py#L61-L77) and [`routing/algorithms.py#L236-L263`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L236-L263)
- **Base Multipliers (`TWO_WHEELER_ROAD_PENALTIES`):**
  - Motorway: $4.0$ | Motorway link: $3.0$
  - Trunk: $3.0$ | Trunk link: $2.5$
  - Primary: $2.2$ | Primary link: $2.0$
  - Secondary: $1.5$ | Secondary link: $1.4$
  - Tertiary: $1.15$ | Tertiary link: $1.1$
  - Residential: $1.0$ | Living street: $0.95$
  - Unclassified: $1.0$ | Service: $0.9$ | Road: $1.1$
- **Production Benchmark Configuration (`build_two_wheeler_penalties`):**
  Configured in Phase 11 production via `build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)`:
  - Effective Primary: $2.2 \times 1.5 = 3.30$
  - Effective Secondary: $1.5 \times 1.5 = 2.25$
  - Effective Residential: $1.0 \times 0.9 = 0.90$
  - Effective Living Street: $0.95 \times 0.9 = 0.855$
- **Evaluation:** Inside [`two_wheeler_edge_cost`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L266-L347):
  $$c_{\text{edge}}(u, v) = \text{length}(u, v) \cdot \mu_{\text{road}}(hw) \cdot \mu_{\text{bridge}} \cdot \mu_{\text{roundabout}} \cdot \mu_{\text{surface}}(u, v) \cdot \mu_{\text{congestion}}$$

### 2.4 Turn Penalties
- **File & Lines:** [`routing/algorithms.py#L37-L43`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L37-L43) and [`#L146-L167`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L146-L167)
- **Thresholds & Magnitudes:**
  - `TURN_THRESHOLD_SHARP = 60.0` degrees
  - `TURN_THRESHOLD_MODERATE = 30.0` degrees
  - `TURN_PENALTY_SHARP = 25.0` (meters cost equivalent)
  - `TURN_PENALTY_MODERATE = 8.0` (meters cost equivalent)
- **Computation:**
  $$\theta = \big| \text{bearing}(u, v) - \text{bearing}(v, w) \big| \pmod{360^\circ}$$
  $$P_{\text{turn}}(u, v, w) = \begin{cases} 25.0, & \text{if } \theta \ge 60.0^\circ \\ 8.0, & \text{if } 30.0^\circ \le \theta < 60.0^\circ \\ 0.0, & \text{if } \theta < 30.0^\circ \end{cases}$$
- **Operational Dependency:** Reads `TURN_PENALTY_SHARP` and `TURN_PENALTY_MODERATE` from module globals.

### 2.5 Bridge / Flyover Modifiers
- **File & Lines:** [`routing/algorithms.py#L298-L311`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L298-L311)
- **Exact Semantics (Replacement vs. Multiplication):**
  ```python
  is_bridge = edge_data.get("bridge")
  if is_bridge and is_bridge not in ["no", "false", "0"]:
      if hw in MAIN_ROAD_TYPES:
          penalty = 0.8  # <--- REPLACES road penalty with 0.8
  ```
  The bridge condition **replaces** the arterial road-class penalty (e.g. $3.3$ or $2.25$) with a favorable assignment of `0.80`. It does **not** multiply the road penalty by $0.8$.
- **Disabling Behavior:** When disabled in ablation testing, this conditional assignment is bypassed, allowing the edge to retain its standard road-class penalty `penalty_map.get(hw, 1.0)`.

### 2.6 Roundabout Modifiers
- **File & Lines:** [`routing/algorithms.py#L326-L331`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L326-L331)
- **Exact Semantics (Multiplicative):**
  ```python
  if edge_data.get("junction") == "roundabout":
      penalty *= penalty_map.get("_roundabout_multiplier", 0.95)
  ```
  The roundabout condition **multiplies** the accumulated edge penalty by $0.95$ ($5\%$ discount).
- **Disabling Behavior:** Setting `_roundabout_multiplier = 1.0` neutralizes the effect completely.

### 2.7 Perpendicular-Offset Alternative Generation
- **File & Lines:** [`routing/algorithms.py#L966-L1250`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L966-L1250)
- **Signature:**
  ```python
  def build_split_route_candidates(
      graph,
      graph_mgr,
      from_lat, from_lng,
      to_lat, to_lng,
      split_fractions=DEFAULT_ROUTE_SPLIT_FRACTIONS,
      penalties=None,
      max_overlap=0.70,
      max_detour=DETOUR_TOLERANCE,
      max_alternatives=3,
      undirected=False,
      return_diagnostics=False,
      max_snapping_distance=DEFAULT_MAX_SNAPPING_DISTANCE_M
  )
  ```
- **Defaults:** `split_fractions=(0.33, 0.50, 0.67)`, offsets $=(150\text{ m}, 300\text{ m})$, bearings $= \theta \pm 90^\circ$ ($12$ total offset points), `max_detour=1.20`, `max_overlap=0.70`, `max_alternatives=3`.
- **Filtering Pipeline:**
  1. Snapping validation via `graph_mgr.validate_coordinate()`.
  2. Identical OD guard (`direct_start == direct_end`).
  3. Exact duplicate sequence suppression.
  4. Detour constraint: $D_{\text{cand}} / D_{\text{direct}} \le 1.20$.
  5. Edge overlap filtering: $\mathcal{O}(R_{\text{prim}}, R_{\text{cand}}) \le 0.70$.
  6. Cost ranking and top-$K$ truncation ($K \le 3$).

### 2.8 State-Expanded Yen's K-Shortest Paths Baseline
- **File & Lines:** [`routing/algorithms.py#L1256-L1410`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L1256-L1410)
- **Signature:**
  ```python
  def yen_ksp_two_wheeler(
      graph,
      start_node,
      end_node,
      graph_mgr,
      penalties=None,
      K=4,
      max_detour=DETOUR_TOLERANCE,
      max_overlap=0.70,
      apply_overlap_filter=False,
      undirected=False,
      return_diagnostics=False
  )
  ```
- **Turn-Aware Spur Search:** Crucially integrates turn penalties at the spur deviation node by seeding `initial_previous_node = root_path[-2]` into `two_wheeler_astar`.
- **Dual Execution Modes:**
  - *Raw Yen:* `apply_overlap_filter=False` (unfiltered by overlap; paths generated purely in non-decreasing cost order subject only to detour $\le 1.20$).
  - *Filtered Yen:* `apply_overlap_filter=True` (applies the same $70\%$ overlap filter used by Perpendicular Offset).

---

## 3. Experiment Specifications

To rigorously isolate component effects, five independent experiments are structured.

```
                      Ablation Study Architecture (Phase 13)
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                      Phase 11 Benchmark Corridors                           │
 │                (25 Representative Bengaluru OD Pairs)                       │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
      ┌──────────────────┬──────────────┴─────┬─────────────────┬──────────────┐
      ▼                  ▼                    ▼                 ▼              ▼
┌───────────┐      ┌───────────┐        ┌───────────┐     ┌───────────┐  ┌───────────┐
│  Exp. A   │      │  Exp. B   │        │  Exp. C   │     │  Exp. D   │  │  Exp. E   │
│Turn-Aware │      │Road       │        │Turn Pen.  │     │Bridge &   │  │Alt. Route │
│Ablation   │      │Impedance  │        │Sensitivity│     │Roundabout │  │Offset vs  │
│           │      │Ablation   │        │           │     │Factorial  │  │Yen KSP    │
└─────┬─────┘      └─────┬─────┘        └─────┬─────┘     └─────┬─────┘  └─────┬─────┘
      │                  │                    │                 │              │
 [Turn-Aware        [B0 Control vs       [C0 Zero Turn     [2x2           [Offset vs
     vs.             B1 Neutral Road      Penalties vs      Factorial:     Raw Yen vs.
  Unaware]           vs B2 Physical]      C1, C2, C3]       4 Combos]      Filtered Yen]
```

---

### 3.1 Experiment A — Turn-Aware Routing Ablation

#### A.1 Objective & Hypothesis
Determine the specific contribution of turn-transition penalties ($P_{\text{turn}}$) to maneuver suppression, geometric straightness, physical distance, and search complexity.
- **Null Hypothesis ($H_0^{(A)}$):** Eliminating turn-transition penalties causes no statistically significant increase in total or sharp turns across urban corridors.
- **Alternative Hypothesis ($H_1^{(A)}$):** Turn-unaware routing significantly increases sharp ($\ge 60^\circ$) and moderate ($30^\circ - 60^\circ$) turns as the search exploits minor alley shortcuts at the expense of maneuver stability.

#### A.2 Treatment Groups & Parameters

| Group ID | Configuration Name | $P_{\text{sharp}}$ | $P_{\text{mod}}$ | State Expansion | Heuristic Mode | Road Penalties |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **A0 (Control)** | Turn-Aware A* (Production Default) | $25.0$ | $8.0$ | $(u_{\text{prev}}, v_{\text{curr}})$ | `admissible` | Production $1.5 / 0.9$ |
| **A1 (Treatment)**| Turn-Unaware State-Expanded A* | $0.0$ | $0.0$ | $(u_{\text{prev}}, v_{\text{curr}})$ | `admissible` | Production $1.5 / 0.9$ |
| **A2 (Reference)**| Pure Vertex-Space Turn-Unaware A* | $0.0$ | $0.0$ | $v_{\text{curr}}$ (Node-level) | `admissible` | Production $1.5 / 0.9$ |

> [!IMPORTANT]
> **Methodological Separation of A1 and A2:**  
> - **A1** isolates the *objective cost function*: it keeps the state-expanded search architecture identical and sets turn penalties to zero. Any difference between A0 and A1 is 100% attributable to the turn penalty values.
> - **A2** isolates the *state space dimensionality*: it reduces the state space from directed edges ($|E|$) to vertices ($|V|$). Comparing A1 vs A2 quantifies the computational overhead of maintaining edge-expanded states when turn penalties are absent.

#### A.3 Measured Metrics
- Physical route distance ($D(R)$ in meters)
- Two-wheeler impedance cost ($C(R)$ in synthetic cost units)
- Total turn count, Sharp turns ($\ge 60^\circ$), Moderate turns ($30^\circ - 60^\circ$), Straight/Gentle maneuvers ($< 30^\circ$)
- Execution runtime (ms, 5 repeated runs)
- Search state expansions ($|\mathcal{S}_{\text{expanded}}|$) and visited vertices ($|\mathcal{V}_{\text{visited}}|$)

---

### 3.2 Experiment B — Road Impedance Model Ablation

#### B.1 Objective & Methodological Revision
Isolate the specific contribution of two-wheeler road-class impedance weights ($\mu_{\text{road}}(hw)$) from all other components, and provide a clear reference against naive physical-distance shortest paths.

#### B.2 Corrected Treatment Matrix

| Treatment ID | Configuration Role | Road-Class Multipliers ($\mu_{\text{road}}$) | Turn Penalties ($P_{\text{turn}}$) | Bridge Modifier ($\mu_{\text{bridge}}$) | Roundabout Modifier ($\mu_{\text{roundabout}}$) | Surface Quality Penalties | Primary Analytical Purpose |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **B0 (Control)** | Production Two-Wheeler Engine | Production Penalties ($1.5$ Main / $0.9$ Inner) | $25.0 / 8.0$ | Enabled ($0.8$) | Enabled ($0.95$) | Active | Serves as the calibrated production baseline. |
| **B1 (Ablation)** | Controlled Road-Class Neutrality | **Neutral:** $\mu_{\text{road}}(hw) = 1.0 \ \forall hw$ | **Identical ($25.0 / 8.0$)** | **Identical ($0.8$)** | **Identical ($0.95$)** | **Active** | **Isolates strictly the effect of road-class impedance weights.** |
| **B2 (Reference)**| Pure Physical-Distance Shortest Path | **Neutral:** $\mu_{\text{road}}(hw) = 1.0 \ \forall hw$ | **Zero ($0.0 / 0.0$)** | **Disabled ($1.0$)** | **Disabled ($1.0$)** | **Disabled ($1.0$)** | Unweighted distance-minimal benchmark (naive GPS routing). |

#### B.3 Distinct Conclusions Supported
1. **Comparison B0 vs. B1 (Controlled Road-Class Ablation):**
   - *Inference:* Isolates the exact percentage of arterial avoidance and residential road usage attributable strictly to the road-type penalty mapping $\mu_{\text{road}}(hw)$ when turns, bridges, roundabouts, and surfaces are held strictly constant.
2. **Comparison B0 vs. B2 (Holistic Navigational Divergence):**
   - *Inference:* Quantifies the total behavioral and geometric divergence between the complete two-wheeler-aware routing engine and the naive physical-distance shortest path produced by standard consumer navigators.

#### B.4 Strict Metric Units Safeguard
- Physical distance is strictly reported in **meters / kilometers**.
- Two-wheeler impedance cost is strictly reported in **dimensionless cost units**.
- **No direct numerical comparison:** The physical-distance cost of B2 (in meters) will never be compared against the impedance cost of B0 (in cost units). Instead, all routes ($R_{\text{B0}}, R_{\text{B1}}, R_{\text{B2}}$) are evaluated symmetrically post-hoc on BOTH metric dimensions using the standard scoring evaluator:
  $$C_{\text{eval}}(R) = \text{path\_cost}(G, R, \text{graph\_mgr}, \text{penalties}=\text{production\_penalties})$$

---

### 3.3 Experiment C — Turn Penalty Sensitivity Analysis

#### C.1 Objective & Terminology Standardization
Characterize the behavioral response curve of route generation across four distinct turn penalty configurations to evaluate sensitivity, non-linearities, and saturation thresholds.
- **Terminology Correction:** Configuration C0 is formally designated:
  > **"Two-wheeler impedance routing with zero turn penalties"**  
  All road-class weights ($1.5 / 0.9$), bridge modifiers ($0.8$), roundabout modifiers ($0.95$), and surface penalties remain **fully active**. Setting turn penalties to zero ($P_{\text{turn}} = 0.0$) isolates the effect of turn costs on an otherwise fully parameterized two-wheeler road network.

#### C.2 Standardized Treatment Matrix

| Configuration ID | Standardized Descriptive Label | $P_{\text{sharp}}$ ($\ge 60^\circ$) | $P_{\text{mod}}$ ($30^\circ - 60^\circ$) | Road-Class Hierarchy | Junction / Grade Modifiers | Analytical Scope |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **C0** | **Two-wheeler impedance routing with zero turn penalties** | $0.0$ | $0.0$ | Active ($1.5 / 0.9$) | Active ($0.8 / 0.95$) | Turn-unconstrained impedance routing. |
| **C1** | **Low turn penalties (50% reduction)** | $12.0$ | $4.0$ | Active ($1.5 / 0.9$) | Active ($0.8 / 0.95$) | Mild turn dampening. |
| **C2 (Base)**| **Baseline turn penalties (Production default)** | $25.0$ | $8.0$ | Active ($1.5 / 0.9$) | Active ($0.8 / 0.95$) | Production standard calibration. |
| **C3** | **High turn penalties (2x baseline)** | $50.0$ | $16.0$ | Active ($1.5 / 0.9$) | Active ($0.8 / 0.95$) | Heavy corridor straightness enforcement. |

#### C.3 Measured Metrics
- Total turns, Sharp turns ($\ge 60^\circ$), Moderate turns ($30^\circ - 60^\circ$)
- Total accumulated turn penalty cost ($C_{\text{turn}}$)
- Physical route distance ($D(R)$ in meters) and detour delta relative to C0 ($\Delta D\%$)
- Two-wheeler impedance cost ($C(R)$)
- Execution runtime (ms) and state expansions

---

### 3.4 Experiment D — Bridge and Roundabout Modifier Factorial ($2 \times 2$)

#### D.1 Objective & Semantics Clarification
Decouple the individual and interaction effects of flyover/bridge preference and roundabout flow preference on route geometry and grade selection.
- **Bridge Modifier Semantics:** Verified as a **replacement / assignment** (`penalty = 0.8`) on main road bridge edges. When disabled, the edge retains its standard road-class penalty `penalty_map.get(hw, 1.0)`.
- **Roundabout Modifier Semantics:** Verified as **multiplicative** (`penalty *= 0.95`). When disabled, `_roundabout_multiplier = 1.00`.

#### D.2 Factorial Treatment Matrix ($2 \times 2$)

| Treatment ID | Factorial Combination | Bridge Condition Behavior | Roundabout Condition Behavior | Road Hierarchy & Turn Penalties |
| :--- | :--- | :--- | :--- | :---: |
| **D1** | Bridge Disabled, Roundabout Disabled | Retains road penalty (`penalty_map[hw]`) | Multiplier = $1.00$ (Neutral) | Fixed ($1.5 / 0.9, 25/8$) |
| **D2** | Bridge Enabled, Roundabout Disabled | Overwrites `penalty = 0.8` on main roads | Multiplier = $1.00$ (Neutral) | Fixed ($1.5 / 0.9, 25/8$) |
| **D3** | Bridge Disabled, Roundabout Enabled | Retains road penalty (`penalty_map[hw]`) | Multiplier = $0.95$ (Discounted)| Fixed ($1.5 / 0.9, 25/8$) |
| **D4 (Control)**| Bridge Enabled, Roundabout Enabled | Overwrites `penalty = 0.8` on main roads | Multiplier = $0.95$ (Discounted)| Fixed ($1.5 / 0.9, 25/8$) |

#### D.3 Measured Metrics
- Bridge/flyover exposure: Total traversed bridge length ($m$) and percentage of route on bridges
- Roundabout exposure: Total traversed roundabout length ($m$) and roundabout traversal count
- Route identity check: Jaccard edge similarity against Control (D4)
- Physical distance ($m$), impedance cost, and runtime (ms)

---

### 3.5 Experiment E — Alternative Routing Comparison (Perpendicular Offset vs. Yen's KSP)

#### E.1 Objective & Evaluation Rules
Compare Perpendicular-Offset alternative route generation against the state-expanded Yen's K-Shortest Paths (KSP) baseline under identical graph, penalty, and tolerance rules.
- **Mandated Reporting:**
  1. Evaluate raw Yen KSP (`apply_overlap_filter=False`).
  2. Evaluate filtered Yen KSP (`apply_overlap_filter=True`).
  3. Evaluate Perpendicular Offset (with $70\%$ overlap filter).
  4. Fixed constraints: $\text{max\_detour} = 1.20$ and $\text{max\_overlap} = 0.70$.

#### E.2 Comparison Matrix

| Algorithmic Pipeline | Method ID | Generation Mechanism | Detour Cap | Overlap Filter ($\le 70\%$) | $K$ Cap |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Perpendicular Offset** | **E1** | Lateral via-point injection ($12$ candidates, $2$-leg stitching) | $1.20\times$ | Enforced | $\le 3$ alternatives |
| **Raw Yen's KSP** | **E2** | Iterative spur deviations on graph | $1.20\times$ | **Disabled** (Raw ranking) | $K=4$ ($1$ prim + $3$ alts) |
| **Filtered Yen's KSP** | **E3** | Iterative spur deviations on graph | $1.20\times$ | **Enforced** ($\le 70\%$) | $K=4$ ($1$ prim + $3$ alts) |

#### E.3 Measured Metrics
- Valid surviving alternatives count ($K_{\text{surv}}$)
- Alternative success rate: Percentage of corridors generating $\ge 1$ surviving alternative
- Physical distance ($m$) and Detour ratio ($D_{\text{alt}} / D_{\text{prim}}$)
- Edge overlap ratio with primary route ($\mathcal{O}(R_{\text{prim}}, R_{\text{alt}})$)
- Jaccard similarity ($\mathcal{J}$) with primary route
- Pairwise diversity ($\mathcal{D} = 1 - \text{mean}(\mathcal{J})$) across the route set
- End-to-end execution runtime (ms) and computational speedup ratio

---

## 4. Experimental Controls & Benchmark Corpus

### 4.1 Graph Invariant Controls
- **Graph Source:** Pre-compiled metropolitan road graph [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) ($|V| = 308,643$ nodes, $|E| = 744,216$ directed edges).
- **Coordinate Snapping:** Fixed origin/destination snapping using [`graph_manager.validate_coordinate(lat, lng, max_distance_m=1500.0)`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py#L90-L144).

### 4.2 Validated 25 Bengaluru Metropolitan Corridors (Phase 13.0.1 Recomputation)

All 50 coordinates have been independently re-snapped and validated: **100% of the corridors resolve to distinct vertices, produce connected routes, and exhibit non-zero physical distance.**

| ID | Corridor Name | From Lat, Lng | To Lat, Lng | Snapped Start Node | Snapped End Node | Snap Dist (S / E) | Distinct? | Connected? | Dist (km) | Node Count |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **OD_01** | BNMIT to MG Road | `(12.9237, 77.5714)` | `(12.9756, 77.6066)` | `7479665259` | `11961205354` | $11.3\text{m} / 98.6\text{m}$ | True | True | $10.065$ | 213 |
| **OD_02** | Koramangala to Indiranagar | `(12.9352, 77.6245)` | `(12.9719, 77.6412)` | `309592695` | `448306395` | $6.5\text{m} / 13.9\text{m}$ | True | True | $6.380$ | 105 |
| **OD_03** | Electronic City to Silk Board | `(12.8452, 77.6602)` | `(12.9176, 77.6238)` | `12450442633` | `9968184749` | $6.1\text{m} / 20.9\text{m}$ | True | True | $9.505$ | 174 |
| **OD_04** | Whitefield to Marathahalli | `(12.9698, 77.7500)` | `(12.9569, 77.7011)` | `1104250513` | `343334152` | $2.4\text{m} / 18.7\text{m}$ | True | True | $8.814$ | 186 |
| **OD_05** | Hebbal to Majestic | `(13.0358, 77.5970)` | `(12.9767, 77.5713)` | `2460383180` | `3755675128` | $5.3\text{m} / 38.8\text{m}$ | True | True | $9.944$ | 189 |
| **OD_06** | Jayanagar to Malleshwaram | `(12.9250, 77.5838)` | `(13.0031, 77.5643)` | `303923398` | `610181412` | $10.9\text{m} / 9.1\text{m}$ | True | True | $12.447$ | 252 |
| **OD_07** | HSR Layout to Bellandur | `(12.9121, 77.6446)` | `(12.9304, 77.6784)` | `11178931802` | `4824673767` | $6.3\text{m} / 9.8\text{m}$ | True | True | $5.807$ | 105 |
| **OD_08** | Banashankari to Yeshwanthpur | `(12.9255, 77.5468)` | `(13.0285, 77.5409)` | `7410528383` | `12193906419` | $22.6\text{m} / 24.4\text{m}$ | True | True | $14.554$ | 322 |
| **OD_09** | Rajajinagar to Commercial St | `(12.9915, 77.5523)` | `(12.9822, 77.6083)` | `6753406912` | `429415637` | $55.9\text{m} / 5.4\text{m}$ | True | True | $8.290$ | 168 |
| **OD_10** | BTM Layout to Domlur | `(12.9166, 77.6101)` | `(12.9609, 77.6387)` | `10123822801` | `11337845996` | $4.0\text{m} / 5.2\text{m}$ | True | True | $7.784$ | 131 |
| **OD_11** | Basavanagudi to Ulsoor | `(12.9416, 77.5738)` | `(12.9818, 77.6284)` | `1837757332` | `3304182912` | $17.8\text{m} / 6.7\text{m}$ | True | True | $11.425$ | 258 |
| **OD_12** | Frazer Town to Shivajinagar | `(12.9982, 77.6145)` | `(12.9856, 77.6006)` | `2228426756` | `10038561456` | $55.3\text{m} / 10.4\text{m}$ | True | True | $2.735$ | 67 |
| **OD_13** | JP Nagar to Koramangala | `(12.9063, 77.5855)` | `(12.9352, 77.6245)` | `7100647721` | `309592695` | $20.2\text{m} / 6.5\text{m}$ | True | True | $7.851$ | 165 |
| **OD_14** | Vijayanagar to Majestic | `(12.9719, 77.5306)` | `(12.9767, 77.5713)` | `1512512264` | `3755675128` | $6.6\text{m} / 38.8\text{m}$ | True | True | $7.186$ | 160 |
| **OD_15** | Yelahanka to Hebbal | `(13.1007, 77.5963)` | `(13.0358, 77.5970)` | `2464052225` | `2460383180` | $38.9\text{m} / 5.3\text{m}$ | True | True | $8.670$ | 62 |
| **OD_16** | Bellandur to Whitefield | `(12.9304, 77.6784)` | `(12.9698, 77.7500)` | `4824673767` | `1104250513` | $9.8\text{m} / 2.4\text{m}$ | True | True | $15.036$ | 333 |
| **OD_17** | Malleshwaram to Rajajinagar | `(13.0031, 77.5643)` | `(12.9915, 77.5523)` | `610181412` | `6753406912` | $9.1\text{m} / 55.9\text{m}$ | True | True | $3.422$ | 56 |
| **OD_18** | Indiranagar to MG Road | `(12.9719, 77.6412)` | `(12.9756, 77.6066)` | `448306395` | `11961205354` | $13.9\text{m} / 98.6\text{m}$ | True | True | $5.876$ | 117 |
| **OD_19** | Silk Board to BTM 2nd Stage | `(12.9176, 77.6238)` | `(12.9166, 77.6101)` | `9968184749` | `10123822801` | $20.9\text{m} / 4.0\text{m}$ | True | True | $2.013$ | 45 |
| **OD_20** | Kengeri to Satellite Bus Stn | `(12.9081, 77.4852)` | `(12.9536, 77.5432)` | `13260995293` | `4926591971` | $89.9\text{m} / 4.3\text{m}$ | True | True | $12.327$ | 238 |
| **OD_21** | RT Nagar to Cantonment | `(13.0238, 77.5936)` | `(12.9935, 77.6001)` | `6461900267` | `7250050350` | $38.5\text{m} / 73.9\text{m}$ | True | True | $4.984$ | 129 |
| **OD_22** | Marathahalli to HAL Airport | `(12.9569, 77.7011)` | `(12.9609, 77.6582)` | `343334152` | `4937997455` | $18.7\text{m} / 29.9\text{m}$ | True | True | $7.727$ | 150 |
| **OD_23** | Richmond Town to Brigade Rd | `(12.9667, 77.6015)` | `(12.9733, 77.6074)` | `9825123715` | `10017310826` | $42.6\text{m} / 26.7\text{m}$ | True | True | $1.353$ | 29 |
| **OD_24** | Banaswadi to Kammanahalli | `(13.0142, 77.6519)` | `(13.0094, 77.6367)` | `6562189762` | `7271096808` | $7.2\text{m} / 29.9\text{m}$ | True | True | $2.398$ | 61 |
| **OD_25** | Padmanabhanagar to Gandhi Bz| `(12.9180, 77.5576)` | `(12.9463, 77.5694)` | `503308828` | `249782667` | $33.8\text{m} / 25.3\text{m}$ | True | True | $4.594$ | 95 |

---

## 5. Metrics & Measurement Methodology

### 5.1 Mathematical Metric Formulations

#### 1. Physical Route Distance ($D(R)$)
$$D(R) = \sum_{i=1}^{|R|-1} \text{length}\big(R[i], R[i+1]\big) \quad \text{[meters]}$$

#### 2. Two-Wheeler Impedance Cost ($C(R)$)
$$C(R) = \sum_{i=1}^{|R|-1} c_{\text{edge}}\big(R[i], R[i+1]\big) + \sum_{i=2}^{|R|-1} P_{\text{turn}}\big(R[i-1], R[i], R[i+1]\big) \quad \text{[synthetic cost units]}$$

#### 3. Turn Classification
For each interior vertex $R[i]$ ($i = 2 \dots |R|-1$):
$$\theta_i = \text{heading\_change}(R[i-1], R[i], R[i+1])$$
- **Sharp Turns:** Count where $\theta_i \ge 60.0^\circ$
- **Moderate Turns:** Count where $30.0^\circ \le \theta_i < 60.0^\circ$
- **Straight / Gentle:** Count where $\theta_i < 30.0^\circ$
- **Total Turns:** $\text{Sharp} + \text{Moderate}$

#### 4. Road-Class Composition
Extract physical edge lengths partitioned into 9 OSM categories and aggregated into 3 macro-classes:
$$\text{Arterial \%} = \frac{\sum_{e \in \{\text{motorway, trunk, primary, secondary}\}} \text{len}(e)}{D(R)} \times 100\%$$
$$\text{Collector \%} = \frac{\sum_{e \in \{\text{tertiary}\}} \text{len}(e)}{D(R)} \times 100\%$$
$$\text{Residential \%} = \frac{\sum_{e \in \{\text{residential, living\_street, unclassified}\}} \text{len}(e)}{D(R)} \times 100\%$$

#### 5. Bridge and Roundabout Exposure
$$\text{Bridge Length} = \sum_{e \in R, \text{bridge}(e)=\text{True}} \text{len}(e) \quad [m], \quad \text{Bridge \%} = \frac{\text{Bridge Length}}{D(R)} \times 100\%$$
$$\text{Roundabout Length} = \sum_{e \in R, \text{junction}(e)=\text{roundabout}} \text{len}(e) \quad [m]$$

#### 6. Route Overlap & Diversity
- **Shared Edge Overlap Ratio:**
  $$\mathcal{O}(R_1, R_2) = \frac{\sum_{e \in E(R_1) \cap E(R_2)} \text{len}(e)}{D(R_2)}$$
- **Jaccard Similarity:**
  $$\mathcal{J}(R_1, R_2) = \frac{\sum_{e \in E(R_1) \cap E(R_2)} \text{len}(e)}{\sum_{e \in E(R_1) \cup E(R_2)} \text{len}(e)}$$
- **Pairwise Diversity:**
  $$\mathcal{D}(\mathcal{R}) = 1.0 - \frac{2}{|\mathcal{R}|(|\mathcal{R}|-1)} \sum_{i < j} \mathcal{J}(R_i, R_j)$$

#### 7. Computational Speedup Formula
Speedup is strictly defined as the ratio of baseline runtime to candidate runtime:
$$\text{Speedup} = \frac{T_{\text{baseline}}}{T_{\text{candidate}}}$$
A speedup $> 1.0$ indicates that the candidate algorithm is faster; $< 1.0$ indicates slower.

---

## 6. Feasibility & Codebase Audit

### 6.1 Audit of Existing Code Capabilities vs. Missing Elements

| Ablation Requirement | Existing Code Status | Identified Gap / Missing Implementation | Proposed Safe Solution (Harness Layer) |
| :--- | :--- | :--- | :--- |
| **A: Turn-Awareness Ablation** | `two_wheeler_astar` always uses edge states `(prev, curr)`. | No native parameter to toggle off state expansion into node-level search. Setting $P_{\text{turn}}=0$ tests zero-cost turns, not node-space search. | Provide both: (1) $P_{\text{turn}}=0$ inside existing state expansion (A1); (2) Node-level $A^*$ harness running on $G$ with edge cost to compare search complexity (A2). |
| **B: Road Impedance Model** | Production weights defined in `core/config.py`. | Distance-only baseline requires neutral weights ($\mu = 1.0$ everywhere). `astar_on_graph` uses base length but includes turn penalties. | Instantiate neutral penalty dictionary (`penalties = {k: 1.0}`) and evaluate both routes using standard scoring function. |
| **C: Turn Penalty Sensitivity** | Turn thresholds hardcoded in `routing/algorithms.py`. | Turn penalty magnitudes (`TURN_PENALTY_SHARP = 25.0`) read from module globals, not passed via function argument. | Dynamic module-attribute scoping inside experiment harness (scoped execution context, as validated in Phase 11). |
| **D: Bridge & Roundabout Factorial** | Roundabout multiplier accepts dictionary parameter. | Bridge discount ($0.8\times$) is an assignment (`penalty = 0.8`) inside `two_wheeler_edge_cost()` and does not read from `penalties`. | Scoped edge-cost function wrapper inside experiment runner (bypassing bridge check when disabled). |
| **D: Exposure Metrics** | `evaluate_route_quality.py` extracts road classes and turns. | **Missing dedicated metric functions** for bridge exposure ($m$) and roundabout exposure ($m$). | Implement metric helper functions `analyze_bridge_exposure(G, route)` and `analyze_roundabout_exposure(G, route)` in experiment harness. |
| **E: Alternative Routing Comparison** | `build_split_route_candidates` and `yen_ksp_two_wheeler` implemented. | `yen_ksp_two_wheeler` supports `apply_overlap_filter=False` (raw) and `True` (filtered). Ready for direct comparison. | Can be executed directly using existing functions in `routing/algorithms.py`. |

---

## 7. Potential Confounding Variables & Mitigation Strategies

```
┌─────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Confounding Variable            │ Methodological Mitigation Strategy                                     │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 1. Units Conflation             │ Never compare physical meters with impedance cost units. Symmetrically │
│    (Meters vs. Cost Units)      │ evaluate all routes on BOTH physical distance (m) and impedance cost.  │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 2. Line-Graph State Overhead    │ Separately report cost-function isolation (A0 vs A1, both edge-state)  │
│    vs. Node-Level Search Space  │ from search-space isolation (A1 edge-state vs A2 node-state).          │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 3. Cold Start & JIT Jitter      │ Execute 1 mandatory unmeasured warm-up query per algorithm; perform    │
│                                 │ 5 repeated timing runs for A* and 3 for Yen KSP; aggregate via median. │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 4. Corridor Topology Bias       │ Use the complete, stratified 25-corridor corpus (Short, Medium, Long,  │
│                                 │ Grids, Bottlenecks, Highway Spines) rather than cherry-picked subsets. │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 5. Multiple Shortest Paths      │ Multi-edge road segments (parallel ways) resolved deterministically by │
│    Ties in Graph Search         │ strictly selecting the minimum length edge: min(..., key=length).      │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 6. Compound Modifier Confounding│ Never bundle bridge and roundabout modifiers into a single toggle; use │
│                                 │ a formal 2x2 factorial orthogonal design (Exp. D).                     │
└─────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Statistical Analysis & Reporting Plan

### 8.1 Statistical Unit of Analysis & Measurement Aggregation
- **Unit of Analysis:** The statistical unit of analysis is the **individual OD corridor** ($N = 25$).
- **Runtime Aggregation:** Repeated timing runs ($R = 5$ for $A^*$, $R = 3$ for Yen KSP) represent repeated technical measurements on the same corridor. Prior to paired statistical testing, measurements are aggregated into the within-corridor median:
  $$\tilde{T}_i = \text{median}\big(T_{i, 1}, T_{i, 2}, \dots, T_{i, R}\big)$$
  Paired tests operate strictly on the $N = 25$ aggregated values $\tilde{T}_i$.

### 8.2 Descriptive Statistics
For every metric across all 25 corridors:
- Mean ($\mu$), Median ($M$), Standard Deviation ($\sigma$), Minimum, Maximum, and Interquartile Range (IQR = $Q_3 - Q_1$).
- Relative percentage difference: $\Delta\% = \frac{X_{\text{treatment}} - X_{\text{control}}}{X_{\text{control}}} \times 100\%$.

### 8.3 Multiple Comparison Control (Holm-Bonferroni Correction)
When testing multiple treatments against a common control (e.g. C0, C1, C3 vs. Baseline C2 in Experiment C; or D1, D2, D3 vs. Control D4 in Experiment D), unadjusted $p$-values will be adjusted using the **Holm-Bonferroni step-down procedure**:
1. Sort raw $p$-values in ascending order: $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$.
2. Compare sequentially: reject $H_{0, (k)}$ if $p_{(k)} \le \alpha / (m - k + 1)$ for all $j \le k$ ($\alpha = 0.05$).
3. Report both unadjusted $p$ and Holm-adjusted $p_{\text{adj}}$.

### 8.4 Handling of Zero-Valued Differences in Wilcoxon Tests
For paired comparisons where multiple corridors yield identical routes ($\Delta_i = 0$):
- **Pratt's Method (Primary):** Ranks all differences including zeros ($|d_i|$), assigns mid-ranks to ties, and drops zero ranks only when summing the signed rank statistic $W^+$, adjusting the mean and variance accordingly.
- **Sensitivity Reporting:** Results from standard Wilcoxon zero-drop (`zero_method='wilcox'`) will be reported alongside Pratt's method for complete transparency.

### 8.5 Effect Sizes and Confidence Intervals
- **Parametric:** Cohen's $d_z = \bar{d} / s_d$, with paired $95\%$ Confidence Intervals ($\bar{d} \pm t_{0.025, N-1} \cdot s_d / \sqrt{N}$).
- **Non-Parametric:** Rank-biserial correlation $r_{\text{rb}} = (W^+ - W^-) / (W^+ + W^-)$ and Hodges-Lehmann median difference estimator with non-parametric $95\%$ confidence intervals.

---

## 9. Proposed Phased Execution Order (Phase 13.1 Roadmap)

Upon user approval of this experimental design, Phase 13.1 will execute following a strictly structured, non-destructive sequence:

```
                          Phase 13.1 Phased Execution Sequence
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Harness Construction & Smoke Validation                                      │
│ - Author `experiments/run_ablation_study.py` in isolated experiments directory        │
│ - Integrate missing bridge/roundabout exposure metrics                                │
│ - Dry-run on single corridor (OD_01) to verify data structures and memory stability   │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Core Algorithm Ablations (Experiments A, B, C, D)                            │
│ - Exp B: Road Impedance Model (B0 Control vs. B1 Neutral Road vs. B2 Physical)        │
│ - Exp A: Turn-Awareness Ablation (A0 Turn-Aware vs. A1 Turn-Unaware vs. A2 Node-A*)   │
│ - Exp C: Turn Penalty Sensitivity (C0 Zero, C1 Low, C2 Baseline, C3 High)            │
│ - Exp D: Bridge & Roundabout Factorial (2x2 orthogonal design: D1, D2, D3, D4)        │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Alternative Routing Benchmark (Experiment E)                                 │
│ - Perpendicular Offset vs. Raw Yen's KSP vs. Filtered Yen's KSP                       │
│ - 3 timing repetitions per corridor across the 25 OD corpus                           │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Stage 4: Statistical Synthesis & Publication Reporting                                │
│ - Compute descriptive statistics, Holm-Bonferroni corrections, and effect sizes       │
│ - Generate CSV and JSON structured datasets in `13_ablation_study/`                   │
│ - Author final synthesis report `phase_13_1_ablation_report.md`                       │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Final Recommendation & Halt Declaration

### 10.1 Review Summary
1. **Corpus Validated:** All 25 corridors resolve to distinct start/end nodes and form connected routes with valid snapping distances.
2. **Methodological Isolation:** Experiment B provides true single-factor isolation of road-class weights; Experiment C terminology is standardized; Experiment D bridge assignment semantics are confirmed.
3. **Statistical Rigor:** Multiple comparison corrections (Holm-Bonferroni), within-corridor runtime aggregation, and Pratt's Wilcoxon handling prevent pseudoreplication and FWER inflation.
4. **Codebase Protection:** No production code, test files, or benchmark artifacts have been modified.

### 10.2 Final Recommendation
**Recommendation:** **ACCEPTED & READY FOR PHASE 13.1 AUTHORIZATION**

**HALT DECLARATION:**  
In compliance with user instructions:
- **No ablation experiments have been executed.**
- **No production code or test files have been modified.**
- **Phase 13.1 will not begin until explicit authorization is granted.**
