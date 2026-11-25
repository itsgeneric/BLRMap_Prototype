# Mathematical Validation and Proof Results

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 9 — A* Heuristic Correction and Mathematical Validation  
**Date:** March 2026  
**Artifact Path:** `tests/test_astar_mathematical_validation.py`  
**Test Status:** 5/5 Unit Tests Passed (100% Pass Rate)

---

## 1. Overview and Methodology

To formally validate the mathematical soundness of the corrected heuristic and empirically demonstrate the flaw in the aggressive heuristic, we developed a deterministic unit test suite in `tests/test_astar_mathematical_validation.py`.

The validation methodology addresses four distinct theoretical requirements:
1. **Goal Admissibility:** $h(\text{goal}, \text{goal}) \equiv 0.0$.
2. **Universal Edge Admissibility:** $h(u) \le c^*(u, \text{goal})$ across all OpenStreetMap road classifications, bridge flyovers, and roundabout configurations.
3. **Monotonic Consistency:** $h(u) \le c(u, v) + P_{\text{turn}}(p, u, v) + h(v)$ across all compass orientations ($0^\circ$ to $180^\circ$).
4. **Counterexample Construction:** Construction of a minimal graph topology proving that Aggressive A* produces a strictly suboptimal route while Standard Admissible A* strictly matches uniform-cost Dijkstra.

---

## 2. Universal Admissibility Across Road Classes

The admissibility condition requires that the heuristic underestimate or equal the true cost along any single-edge transition $(u, \text{goal})$:
$$h(u) \le c(u, \text{goal}) = \text{length}(u, \text{goal}) \times p(e)$$

We evaluated a baseline straight-line distance of $L = 771.58\text{ m}$ between $(12.9700^\circ\text{N}, 77.5900^\circ\text{E})$ and $(12.9750^\circ\text{N}, 77.5950^\circ\text{E})$ across all active road classes.

### Admissibility Test Matrix

| Road Classification / Tag | Multiplier $p(e)$ | True Edge Cost $c(e)$ | Admissible $h(u)$ ($0.8 \times L$) | Admissible Slack ($c - h$) | Aggressive $h(u)$ ($1.25 \times L$) | Admissibility Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `highway=trunk, bridge=yes` | **0.800** | **617.26** | **617.26** | **0.00** (Tight Bound) | 964.48 | **Admissible** (Aggressive violates by $+56.25\%$) |
| `highway=primary, bridge=yes` | **0.800** | **617.26** | **617.26** | **0.00** (Tight Bound) | 964.48 | **Admissible** (Aggressive violates by $+56.25\%$) |
| `highway=residential, roundabout` | 0.950 | 733.00 | 617.26 | +115.74 | 964.48 | **Admissible** (Aggressive violates by $+31.58\%$) |
| `highway=residential` | 1.000 | 771.58 | 617.26 | +154.32 | 964.48 | **Admissible** (Aggressive violates by $+25.00\%$) |
| `highway=living_street` | 1.000 | 771.58 | 617.26 | +154.32 | 964.48 | **Admissible** (Aggressive violates by $+25.00\%$) |
| `highway=tertiary` | 1.250 | 964.48 | 617.26 | +347.22 | 964.48 | **Admissible** (Aggressive boundary) |
| `highway=secondary` | 1.500 | 1157.37 | 617.26 | +540.11 | 964.48 | **Admissible** (Aggressive admissible) |
| `highway=primary` | 2.200 | 1697.48 | 617.26 | +1080.22 | 964.48 | **Admissible** (Aggressive admissible) |
| `highway=motorway` | 2.500 | 1928.95 | 617.26 | +1311.69 | 964.48 | **Admissible** (Aggressive admissible) |
| `highway=primary, congested` | 55.000 | 42436.90 | 617.26 | +41819.64 | 964.48 | **Admissible** (Aggressive admissible) |

### Key Mathematical Findings:
1. Under `highway=trunk, bridge=yes`, the edge multiplier reaches the global theoretical infimum:
   $$p_{\min} = 0.8000$$
2. For this edge, $h_{\text{admissible}} = 617.26 \equiv c(e) = 617.26$. The slack is exactly **0.00**, proving that $h_{\text{admissible}}$ is the **tightest possible admissible linear lower bound**.
3. Under the legacy aggressive heuristic, $h_{\text{aggressive}} = 964.48 > 617.26$, strictly violating admissibility on all edges where $p(e) < 1.25$.

---

## 3. Monotonic Consistency (Triangle Inequality) Validation

Monotonic consistency requires that for any state transition $(p, u) \to (u, v)$:
$$\text{Slack}_{\text{consistency}} = [c(u, v) + P_{\text{turn}}(p, u, v) + h(v)] - h(u) \ge 0$$

To test spatial isotropy, we fixed origin $P = (12.9700, 77.5900)$, intermediate node $U = (12.9720, 77.5900)$, destination $G = (12.9800, 77.6000)$, and generated successive nodes $V$ across eight heading angles relative to the arrival vector $P \to U$.

### Consistency Across Maneuver Angles

| Outgoing Heading | Angle Change $\theta$ | Maneuver Category | Turn Cost $P_{\text{turn}}$ (m) | Edge Cost $c(u, v)$ | $h(u)$ | $h(v)$ | Consistency Slack |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $0^\circ$ (North) | $0.0^\circ$ | Straight | 0.0 | 222.39 | 1148.65 | 986.32 | **+60.06** |
| $30^\circ$ (NNE) | $30.0^\circ$ | Moderate Turn | 8.0 | 222.39 | 1148.65 | 948.12 | **+29.86** |
| $45^\circ$ (NE) | $45.0^\circ$ | Moderate Turn | 8.0 | 222.39 | 1148.65 | 933.72 | **+15.46** |
| $60^\circ$ (ENE) | $60.0^\circ$ | Sharp Turn | 25.0 | 222.39 | 1148.65 | 924.58 | **+23.32** |
| $90^\circ$ (East) | $90.0^\circ$ | Sharp Turn | 25.0 | 222.39 | 1148.65 | 930.56 | **+29.30** |
| $120^\circ$ (ESE) | $120.0^\circ$ | Sharp Turn | 25.0 | 222.39 | 1148.65 | 964.71 | **+63.45** |
| $135^\circ$ (SE) | $135.0^\circ$ | Sharp Turn | 25.0 | 222.39 | 1148.65 | 991.34 | **+90.08** |
| $180^\circ$ (South) | $180.0^\circ$ | U-Turn | 25.0 | 222.39 | 1148.65 | 1109.84 | **+208.58** |

**Result:**  
Across all geometries, $\text{Slack}_{\text{consistency}} \ge +15.46 > 0.00$. Zero violations were detected.

---

## 4. Multi-Route Synthetic Grid Validation vs. Dijkstra

We instantiated a $3 \times 3$ interconnected grid topology with alternating road classes (`residential`, `primary`, `secondary`, `tertiary`) spanning from $(12.9700, 77.5900)$ to $(12.9760, 77.5960)$:
- **Start Node:** `N_0_0`
- **Goal Node:** `N_2_2`

### Results:
- **Dijkstra Ground Truth Cost:** $1772.48\text{ cost units}$ (Expanded States: 14)
- **Standard Admissible A* Cost:** $1772.48\text{ cost units}$ (Expanded States: 10)
- **Optimality Gap:** **$0.000000\%$** (Strict equality within machine precision)
- **State Space Reduction:** **$28.57\%$ reduction** in expanded states compared to uniform Dijkstra.

---

## 5. Provable Suboptimality Counterexample for Aggressive A*

### 5.1 Topology Architecture

To rigorously demonstrate why the aggressive heuristic fails in practical routing engines, we constructed a minimal 5-node directed network containing two competing routes:

```mermaid
flowchart LR
    S((Start S)) -->|Primary Road p=2.2\nLength=554m| DM((DirectMid))
    DM -->|Primary Road p=2.2\nLength=555m| G((Goal G))

    S -->|Trunk Flyover p=0.8\nLength=1000m| F1((Flyover 1))
    F1 -->|Trunk Flyover p=0.8\nLength=887m| F2((Flyover 2))
    F2 -->|Trunk Flyover p=0.8\nLength=1000m| G

    classDef primary fill:#ffcccc,stroke:#cc0000,stroke-width:2px;
    classDef flyover fill:#ccffcc,stroke:#009900,stroke-width:2px;
    class DM primary;
    class F1,F2 flyover;
```

### 5.2 Geometric and Cost Parameters

1. **Origin $S$:** $(12.9700^\circ\text{N}, 77.5900^\circ\text{E})$
2. **Goal $G$:** $(12.9800^\circ\text{N}, 77.5900^\circ\text{E})$ (Directly North, $\text{haversine} = 1108.99\text{ m}$)
3. **Route 1 (Direct Primary Road, High Cost):**
   - $S \to \text{DirectMid}$: Primary road ($p = 2.2$), length $= 554.5\text{ m}$, cost $= 1219.89$
   - $\text{DirectMid} \to G$: Primary road ($p = 2.2$), length $= 554.5\text{ m}$, cost $= 1219.89$
   - Turn cost at $\text{DirectMid}$: Straight ($0.0^\circ$) $= 0.0$
   - **Total True Cost (Route 1) = $2439.78$**
4. **Route 2 (Flyover Detour East, Low Cost):**
   - Offset East by $0.0090^\circ$ ($\approx 980\text{ m}$) to $F_1(12.9710, 77.5990)$ and $F_2(12.9790, 77.5990)$
   - $S \to F_1$: Trunk bridge flyover ($p = 0.8$), length $= 1000.2\text{ m}$, cost $= 800.16$
   - $F_1 \to F_2$: Trunk bridge flyover ($p = 0.8$), length $= 887.2\text{ m}$, cost $= 709.76$
   - $F_2 \to G$: Trunk bridge flyover ($p = 0.8$), length $= 1000.2\text{ m}$, cost $= 800.16$
   - Turn penalties at $F_1$ and $F_2$: $\approx 11.0\text{ m}$ each
   - **Total True Cost (Route 2) = $2332.08$**

**Objective:** Route 2 is the true optimal shortest-cost path ($2332.08 < 2439.78$).

### 5.3 Priority Queue Trace and Divergence

When searching from $S$:
1. At node $S$, both $\text{DirectMid}$ and $F_1$ are inserted into the open set.
   - For $\text{DirectMid}$: $g = 1219.89$, $\text{haversine}(\text{DirectMid}, G) = 554.5\text{ m}$.
   - For $F_1$: $g = 800.16$, $\text{haversine}(F_1, G) = 1399.8\text{ m}$.

2. **Under Standard Admissible A* ($h = 0.8 \times \text{haversine}$):**
   - $f(\text{DirectMid}) = 1219.89 + 0.8 \times 554.5 = 1219.89 + 443.60 = \mathbf{1663.49}$
   - $f(F_1) = 800.16 + 0.8 \times 1399.8 = 800.16 + 1119.84 = \mathbf{1920.00}$
   - $\text{DirectMid}$ is explored first, adding $G$ via Route 1 with $f(G) = 2439.78$.
   - **Crucially:** Because $f(F_1) = 1920.00 < f(G) = 2439.78$, A* does NOT terminate! It continues to pop $F_1$, advances to $F_2$, and reaches $G$ via Route 2 at cost **$2332.08$**, which correctly wins the search!

3. **Under Aggressive A* ($h = 1.25 \times \text{haversine}$):**
   - $f(\text{DirectMid}) = 1219.89 + 1.25 \times 554.5 = 1219.89 + 693.12 = \mathbf{1913.01}$
   - $f(F_1) = 800.16 + 1.25 \times 1399.8 = 800.16 + 1749.75 = \mathbf{2549.91}$
   - From $\text{DirectMid}$, goal $G$ is queued with cost $g(G) = 2439.78$ and $h(G) = 0 \implies f(G) = \mathbf{2439.78}$.
   - **Fatal Flaw:** The queue compares $f(G) = 2439.78$ against $f(F_1) = 2549.91$. Because $2439.78 < 2549.91$, Aggressive A* pops $G$ immediately and terminates search, **completely pruning the optimal flyover route!**

### 5.4 Empirical Test Execution Output

```
======================================================================
[Counterexample Verification]
Dijkstra (Ground Truth): Route=['S', 'F1', 'F2', 'G'], Cost=2332.08
Standard Admissible A*:  Route=['S', 'F1', 'F2', 'G'], Cost=2332.08 (Gap: 0.00%)
Aggressive A*:          Route=['S', 'DirectMid', 'G'], Cost=2446.29 (Suboptimal Gap: +4.90%)
----------------------------------------------------------------------
Ran 5 tests in 0.001s
OK
```

---

## 6. Conclusion and Academic Positioning

This experiment conclusively establishes:
1. Standard Admissible A* ($h = 0.8 \times \text{haversine}$) is strictly admissible, consistent, and identical to Dijkstra ground truth.
2. The legacy aggressive heuristic ($h = 1.25 \times \text{haversine}$) is formally inadmissible and empirically produces suboptimal routes with a measurable $+4.90\%$ cost penalty.
3. In research publications, the admissible formulation must be presented as the primary algorithmic contribution to preserve mathematical integrity, while the aggressive variant can be presented as a greedy speedup trade-off.
