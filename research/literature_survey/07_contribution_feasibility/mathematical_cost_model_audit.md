# Mathematical Cost Model and Heuristic Admissibility Audit

**Project Title:** GIS-Based Intelligent Navigation and Path Optimization Framework: Self-Calibrating, Two-Wheeler-Aware Routing for Bengaluru  
**Stage:** Phase 7 – Contribution Feasibility and Research Scope Decision  
**Document:** `research/literature_survey/07_contribution_feasibility/mathematical_cost_model_audit.md`  
**Date:** 2026-11-03  
**Audited Files:** `routing/algorithms.py`, `core/config.py`, `routing/graph_manager.py`  

---

## 1. Executive Summary

This document presents a rigorous mathematical and dimensional audit of the path-cost formulations, turn-penalty calculations, and A\* heuristic functions implemented in `routing/algorithms.py`.

### Critical Audit Findings:
1. **Critical Heuristic Admissibility Violation:** The A\* heuristic in `two_wheeler_astar` (L. 489) divides Haversine distance by `MIN_PENALTY_FLOOR = 0.8`, which multiplies the heuristic by $1.25$. This strictly overestimates true remaining path cost whenever edges have penalties $\le 1.0$, **violating A\* admissibility and consistency**.
2. **Physical Dimensionality:** The edge cost is computed as $\text{length} \times \text{penalty}$ (dimension of meters $[L]$). Turn penalties are added as scalar values ($8.0$, $25.0$), meaning they are dimensionally evaluated in **virtual distance meters**, not temporal seconds.
3. **Multiplier Directions:** All road classification penalties, flyover bonuses, roundabout discounts, and congestion multipliers are applied in the mathematically intended direction.
4. **Parameter Status:** All numerical parameters (turn penalties, thresholds, filtering factors, split offsets) are currently uncalibrated heuristic constants requiring formal sensitivity analysis.

---

## 2. Dimensional Analysis of the Implemented Cost Function

In `routing/algorithms.py`, when relaxing an outgoing edge $(u, v)$ with incoming node $p$ (`previous_node`), the traversal cost is calculated across lines 579–616:

$$\text{new\_cost} = \text{current\_cost} + c(u, v) + P_{turn}(p, u, v)$$

### 2.1 Edge Cost Calculation: $c(u, v)$
In `two_wheeler_edge_cost()` (L. 261–343):
$$c(u, v) = \text{length}(u, v) \cdot M(u, v)$$
* **Physical Dimension of $\text{length}(u, v)$:** Road length extracted from OpenStreetMap line geometry, measured in **meters** ($[L]$).
* **Physical Dimension of $M(u, v)$:** Dimensionless scaling factor ($[1]$), computed as:
  $$M(u, v) = p_{base}(hw) \cdot M_{bridge} \cdot M_{roundabout} \cdot M_{surface} \cdot M_{congested}$$
  - $p_{base}(hw) \in [0.9, 4.0]$: Base road classification penalty (`service: 0.9`, `residential: 1.0`, `secondary: 1.5`, `primary: 2.2`, `motorway: 4.0`).
  - $M_{bridge} = 0.8$: Flyover bonus applied if `bridge` tag exists on a main road.
  - $M_{roundabout} = 0.95$: Roundabout traversal bonus.
  - $M_{surface} \ge 1.0$: Surface roughness penalty factor from `graph_mgr.get_surface_penalty(u, v)`.
  - $M_{congested} = 25.0$: Dynamic impedance penalty applied if $u \in \text{congested\_nodes}$ or $v \in \text{congested\_nodes}$.
* **Resulting Unit:** $c(u, v)$ has the physical dimension of **meters** ($[L]$). It represents an "effective virtual distance" reflecting travel resistance.

### 2.2 Turn Penalty Calculation: $P_{turn}(p, u, v)$
In `_turn_penalty()` (L. 141–163):
$$P_{turn}(p, u, v) = \begin{cases} 0.0 & \Delta \theta < 30.0^\circ \\ 8.0 & 30.0^\circ \le \Delta \theta < 60.0^\circ \\ 25.0 & \Delta \theta \ge 60.0^\circ \end{cases}$$
* **Dimensional Consistency:** Line 30 of `algorithms.py` explicitly notes: `# Penalty is expressed in the same cost units as road length.`
* Because $P_{turn}$ is added directly to $c(u, v)$ in line 614:
  $$\text{new\_cost} = \text{current\_cost} + c(u, v) + P_{turn}$$
  $P_{turn}$ **must possess the dimension of meters ($[L]$)**.
* **Interpretation:** A sharp turn ($\ge 60^\circ$) penalizes the path by adding an equivalent virtual distance of $25.0\text{ m}$. A moderate turn ($30^\circ–60^\circ$) adds $8.0\text{ m}$.
* **Academic Correction:** Previous literature review drafts occasionally referred to turn penalties as seconds ($8\text{ s}, 25\text{ s}$). This is mathematically incorrect under the implemented code and must be strictly formalized in the paper as **equivalent virtual detour distance in meters**.

---

## 3. Mathematical Audit of A\* Heuristic Admissibility and Consistency

### 3.1 Theoretical Requirements (Bast et al. [10])
For goal-directed A\* to guarantee shortest-path optimality on a graph with non-negative edge costs $c(u, v) \ge 0$, the heuristic potential function $h(u)$ must be:
1. **Admissible:** It must never overestimate the true minimum cost from vertex $u$ to target $t$:
   $$h(u) \le c^*(u, t) \quad \forall u \in V$$
2. **Consistent (Monotonic):** For every edge $(u, v) \in E$, the heuristic must satisfy the triangle inequality:
   $$h(u) \le c(u, v) + h(v)$$

### 3.2 Evaluation of the Implemented Heuristic in `two_wheeler_astar`
In `routing/algorithms.py` (L. 480–490):
```python
def heuristic(node):
    return (
        haversine_m(
            graph.nodes[node]["y"], graph.nodes[node]["x"],
            graph.nodes[end_node]["y"], graph.nodes[end_node]["x"]
        )
        / MIN_PENALTY_FLOOR
    )
```
where line 23 defines:
```python
MIN_PENALTY_FLOOR = 0.8
```

### 3.3 Proof of Inadmissibility
1. **Division Effect:** Dividing by $0.8$ is algebraically identical to multiplying by $1.25$:
   $$h(u) = \frac{\text{haversine\_m}(u, t)}{0.8} = 1.25 \times \text{haversine\_m}(u, t)$$
2. **Counterexample (Flyover / Bridge):**  
   Suppose there exists a straight bridge/flyover connecting node $u$ directly to destination $t$ with physical length $1000\text{ m}$.  
   Since it is a flyover, its edge penalty is $M(u, t) = 0.8$, and $P_{turn} = 0$.  
   The true cost of traversing this edge is:
   $$c^*(u, t) = 1000\text{ m} \times 0.8 = 800\text{ m}$$
   However, the implemented heuristic evaluates:
   $$h(u) = 1.25 \times \text{haversine\_m}(u, t) = 1.25 \times 1000\text{ m} = 1250\text{ m}$$
   Here:
   $$h(u) = 1250\text{ m} > 800\text{ m} = c^*(u, t)$$
   **The heuristic overestimates the true remaining cost by $56.25\%$ ($1250 / 800 = 1.5625$).**

3. **Counterexample (Residential Road):**  
   Consider a straight residential street connecting $u$ and $t$ of length $1000\text{ m}$ with baseline penalty $1.0$.  
   True cost: $c^*(u, t) = 1000\text{ m} \times 1.0 = 1000\text{ m}$.  
   Implemented heuristic: $h(u) = 1.25 \times 1000\text{ m} = 1250\text{ m}$.  
   Again, $h(u) > c^*(u, t)$, violating admissibility.

4. **Root Cause Analysis:**  
   The developer confused speed-based heuristic division with distance-based cost scaling:
   - In time-based routing where cost is travel time $t = \text{dist} / v$, dividing by maximum network speed ($v_{max}$) yields a smaller, admissible lower bound on time.
   - In distance-impedance routing where cost is $\text{dist} \times p$, dividing by a fractional penalty floor ($0.8$) scales the heuristic *upward*, producing an inflated value that breaks admissibility.

### 3.4 Mathematical Remedy
To guarantee strict admissibility and consistency, the lower bound heuristic must multiply by the minimum penalty floor:
$$h_{corrected}(u) = \text{haversine\_m}(u, t) \times \text{MIN\_PENALTY\_FLOOR} = 0.8 \times \text{haversine\_m}(u, t)$$
*Proof:* Because for any path $P$ from $u$ to $t$:
$$\text{cost}(P) = \sum_{e \in P} \text{length}(e) \cdot M(e) + P_{turn} \ge 0.8 \sum_{e \in P} \text{length}(e) \ge 0.8 \times \text{haversine\_m}(u, t)$$
This holds for all possible paths, strictly restoring mathematical admissibility ($h(u) \le c^*(u, t)$) and monotonicity.

---

## 4. Multiplier Direction and Integration Verification

| Multiplier Variable | Value Range | Code Implementation | Mathematical Effect on Cost | Intended Transportation Objective | Verification Status |
| :--- | :---: | :--- | :--- | :--- | :---: |
| `motorway` | 4.0 | `TWO_WHEELER_ROAD_PENALTIES` | Inflates cost $4.0\times$ | Strongly deters two-wheelers from high-speed highways | **Correct** |
| `primary` | 2.2 | `TWO_WHEELER_ROAD_PENALTIES` | Inflates cost $2.2\times$ | Penalizes car-congested radial arterials | **Correct** |
| `residential` | 1.0 | `TWO_WHEELER_ROAD_PENALTIES` | Baseline cost $1.0\times$ | Standard traversal cost | **Correct** |
| `living_street` | 0.95 | `TWO_WHEELER_ROAD_PENALTIES` | Discounts cost $0.95\times$ | Encourages low-stress local corridors | **Correct** |
| `service` | 0.9 | `TWO_WHEELER_ROAD_PENALTIES` | Discounts cost $0.90\times$ | Encourages accessible service alleys | **Correct** |
| `bridge` (Main roads) | 0.8 | `two_wheeler_edge_cost` L. 305 | Discounts cost to $0.8\times$ | Prioritizes grade-separated flyovers bypassing ground queues | **Correct** |
| `roundabout` | 0.95 | `two_wheeler_edge_cost` L. 323 | Multiplies penalty by $0.95\times$ | Favors continuous roundabout flow over intersection stops | **Correct** |
| `congested_nodes` | 25.0 | `two_wheeler_edge_cost` L. 315 | Multiplies penalty by $25.0\times$ | Creates massive repellent around saturated bottleneck nodes | **Correct** |

---

## 5. Comprehensive Parameter Justification and Calibration Audit

The table below catalogs all 12 configurable parameters in the routing engine, auditing their empirical justification and calibration status:

| Parameter Name | File & Line Reference | Current Code Value | Origin / Justification in Codebase | Empirical Literature Grounding | Scientific Calibration Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MIN_PENALTY_FLOOR` | `algorithms.py:23` | `0.8` | Minimum possible edge multiplier (flyover bonus) | Bridge flyover bypass assumption | **Formula Bug:** Must multiply, not divide |
| `TURN_PENALTY_SHARP` | `algorithms.py:32` | `25.0` (meters) | Virtual detour penalty for sharp turn ($\ge 60^\circ$) | Geisberger & Vetter [7] (qualitative concept) | **Uncalibrated:** Heuristic estimate; requires sensitivity test (10m–50m) |
| `TURN_PENALTY_MODERATE` | `algorithms.py:33` | `8.0` (meters) | Virtual detour penalty for moderate turn ($30^\circ–60^\circ$) | Geisberger & Vetter [7] (qualitative concept) | **Uncalibrated:** Heuristic estimate; requires sensitivity test (5m–15m) |
| `TURN_THRESHOLD_MODERATE` | `algorithms.py:36` | `30.0` (degrees) | Noise filtering threshold to ignore road curves | Standard GIS deflection threshold | **Reasonable baseline:** Filters minor road bends |
| `TURN_THRESHOLD_SHARP` | `algorithms.py:37` | `60.0` (degrees) | Threshold distinguishing real turns from curves | Standard highway geometry threshold | **Reasonable baseline:** Distinguishes genuine maneuvers |
| `FILTER_DISCOUNT_PER_JUNCTION` | `config.py:79` | `0.985` | Compounding discount per signalized multi-lane junction | Promraksa et al. [1] queue-filtering concept | **Uncalibrated:** Standalone helper; not called in A\* |
| `FILTER_DISCOUNT_FLOOR` | `config.py:80` | `0.85` | Maximum compounding discount limit ($15\%$ max discount) | Engineering safety boundary | **Uncalibrated:** Reasonable bound, but unverified |
| `MIN_LANES_FOR_FILTERING` | `config.py:81` | `2` (lanes) | Minimum approach lanes for vehicle filtering | Promraksa et al. [1] ($0.75\text{ m}$ lateral clearance) | **Empirically Justified:** $\ge 2$ lanes required for queue rows |
| `Congestion Multiplier` | `algorithms.py:315` | `25.0` | Saturated node impedance multiplier | Abbas et al. [13] dynamic penalty concept | **Uncalibrated:** Arbitrary constant; requires sensitivity test ($5\times–50\times$) |
| `DEFAULT_ROUTE_SPLIT_FRACTIONS` | `config.py:82` | `(0.33, 0.5, 0.67)` | Chord fractions for perpendicular offset projection | Abraham et al. [9] via-node concept | **Heuristic:** Covers 1st, 2nd, and 3rd trip segments |
| `offsets_m` | `algorithms.py:759` | `(150, 300)` (meters) | Lateral perpendicular offset distances | Urban neighborhood block width in Bengaluru | **Heuristic:** Reflects typical Bangalore block offsets |
| `DETOUR_TOLERANCE` | `config.py:83` | `1.20` ($20\%$ max detour) | Bounded detour cap for candidate alternative routes | Abraham et al. [9] bounded detour criterion ($\epsilon \le 0.20$) | **Empirically Justified:** Standard bound in route planning |

---

## 6. Audit Conclusion and Technical Action Items

1. **Mandatory Mathematical Correction:** In `routing/algorithms.py:489`, the heuristic formula must be corrected from `/ MIN_PENALTY_FLOOR` to `* MIN_PENALTY_FLOOR` (multiplying Haversine distance by $0.8$) before conducting benchmark experiments to guarantee mathematical admissibility.
2. **Formalize Units in Paper:** All turn penalties must be declared in **meters of virtual detour impedance**, eliminating temporal second descriptions from the methodology.
3. **Parameter Transparency:** In the conference paper, all 12 parameters must be explicitly presented as **initial heuristic calibration baselines requiring sensitivity analysis**, rather than claiming they are pre-validated optimal constants.
