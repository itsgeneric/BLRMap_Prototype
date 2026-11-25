# Empirical Benchmark Results: Three-Way Heuristic Search Comparison on the Bengaluru Road Network

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 9 — A* Heuristic Correction and Mathematical Validation  
**Date:** March 2026  
**Network Dataset:** `bengaluru_graph.pkl` (308,643 Nodes, 744,216 Directed Edges)  
**Corridors Evaluated:** 10 Diverse Real-World Commuter Corridors (Totaling 93.6 km)  
**Raw Data Source:** `research/literature_survey/09_astar_correction/heuristic_benchmark_raw.json`  

---

## 1. Executive Summary

This report delivers a rigorous empirical comparison between three path-finding configurations executed on the real-world OpenStreetMap road network of Bengaluru, India:
1. **Uniform-Cost Dijkstra Search ($h = 0.0$):** Theoretical ground truth for shortest-cost paths.
2. **Standard Admissible A* Search ($h = 0.8 \times \text{haversine}$):** The proposed mathematically admissible formulation.
3. **Aggressive A* Search ($h = 1.25 \times \text{haversine}$):** The legacy overestimating formulation.

The benchmark demonstrates three definitive findings:
1. **$100\%$ Optimality Preservation for Admissible A*:** Standard Admissible A* achieved an **exact $0.0000\%$ optimality gap** across all 10 evaluated urban corridors, discovering paths with identical total impedance costs to uniform Dijkstra.
2. **Substantial Search Space Reduction:** Standard Admissible A* reduced the number of expanded search states by **$64.4\%$ on average** relative to Dijkstra (expanding $38,766$ states vs. $108,963$ states), achieving a **$3.22\times$ runtime speedup** ($599.07\text{ ms}$ vs. $1,927.23\text{ ms}$).
3. **Empirical Suboptimality of Aggressive A*:** While Aggressive A* achieved a further $36.6\%$ reduction in expanded states over Admissible A*, it produced **demonstrably suboptimal paths in $30\%$ of the real-world corridors** tested (OD_06: $+0.174\%$, OD_09: $+0.067\%$, OD_10: $+0.437\%$), confirming that its admissibility violation leads to real-world route degradation.

---

## 2. Experimental Setup and Corridor Selection

Ten origin-destination pairs were selected across the metropolitan region of Bengaluru to capture representative variations in road hierarchy, junction density, arterial bypasses, and elevated flyover structures:

1. **OD_01 (BNMIT to MG Road, 10.07 km):** South suburban residential to Central Business District core.
2. **OD_02 (Koramangala to Indiranagar, 6.38 km):** Dense commercial and residential tech hub connector across Inner Ring Road.
3. **OD_03 (Electronic City to Silk Board, 9.50 km):** High-volume arterial corridor with parallel elevated expressway and surface service roads.
4. **OD_04 (Whitefield to Marathahalli, 8.81 km):** Suburban tech corridor with heavy mid-block congestion.
5. **OD_05 (Hebbal to Majestic, 9.94 km):** North-South trunk arterial traversing the Hebbal and Palace Guttahalli flyovers.
6. **OD_06 (Jayanagar 4th Block to Malleshwaram, 12.45 km):** Cross-city journey through historic grid-pattern corridors and central bottlenecks.
7. **OD_07 (HSR Layout to Bellandur, 5.81 km):** High-density suburban collector link bordering Outer Ring Road.
8. **OD_08 (Banashankari to Yeshwanthpur, 14.55 km):** Major diagonal peripheral commute across western arterial roads.
9. **OD_09 (Rajajinagar to Commercial Street, 8.29 km):** Dense mixed-use commercial and residential grid.
10. **OD_10 (BTM Layout to Domlur, 7.78 km):** Intermediate ring-road corridor with flyovers and intermediate signalized intersections.

---

## 3. Comprehensive Benchmark Results

The table below presents the primary metrics recorded across all 30 full-scale graph routing executions.

| Corridor ID & Name | Distance (km) | Dijkstra Cost | Admissible A* Cost | Aggressive A* Cost | Dijkstra States | Admissible States | Aggressive States | Dijkstra Time (ms) | Admissible Time (ms) | Aggressive Time (ms) | Admissible Opt Gap (%) | Aggressive Opt Gap (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **OD_01: BNMIT to MG Road** | 10.07 | 12,652.51 | 12,652.51 | 12,652.51 | 169,313 | 64,076 | 34,609 | 4,831.50 | 1,004.08 | 509.62 | **0.000%** | **0.000%** |
| **OD_02: Koramangala to Indiranagar** | 6.38 | 6,460.97 | 6,460.97 | 6,460.97 | 25,735 | 8,677 | 4,573 | 386.42 | 128.12 | 69.49 | **0.000%** | **0.000%** |
| **OD_03: Electronic City to Silk Board** | 9.50 | 11,204.93 | 11,204.93 | 11,204.93 | 59,213 | 17,612 | 3,515 | 890.48 | 264.99 | 48.00 | **0.000%** | **0.000%** |
| **OD_04: Whitefield to Marathahalli** | 8.81 | 11,468.77 | 11,468.77 | 11,468.77 | 27,860 | 12,396 | 7,937 | 385.25 | 166.64 | 108.32 | **0.000%** | **0.000%** |
| **OD_05: Hebbal to Majestic** | 9.94 | 11,536.13 | 11,536.13 | 11,536.13 | 115,783 | 37,764 | 18,602 | 1,866.91 | 569.39 | 279.03 | **0.000%** | **0.000%** |
| **OD_06: Jayanagar to Malleshwaram** | 12.45 | 14,153.24 | 14,153.24 | **14,177.89** | 193,295 | 71,735 | 40,348 | 3,139.88 | 1,099.40 | 649.34 | **0.000%** | **+0.174%** |
| **OD_07: HSR Layout to Bellandur** | 5.81 | 6,505.39 | 6,505.39 | 6,505.39 | 20,457 | 4,707 | 2,021 | 293.91 | 75.85 | 36.35 | **0.000%** | **0.000%** |
| **OD_08: Banashankari to Yeshwanthpur** | 14.55 | 18,507.46 | 18,507.46 | 18,507.46 | 294,000 | 129,619 | 112,501 | 4,662.01 | 2,070.12 | 1,766.47 | **0.000%** | **0.000%** |
| **OD_09: Rajajinagar to Commercial St** | 8.29 | 9,199.77 | 9,199.77 | **9,205.97** | 106,948 | 25,311 | 14,808 | 1,652.48 | 380.01 | 239.43 | **0.000%** | **+0.067%** |
| **OD_10: BTM Layout to Domlur** | 7.78 | 9,337.40 | 9,337.40 | **9,378.20** | 77,028 | 15,766 | 6,964 | 1,163.49 | 232.11 | 102.41 | **0.000%** | **+0.437%** |

---

## 4. Aggregate Performance Comparison

The table below summarizes the macroscopic metrics across the entire 10-corridor benchmark suite:

| Performance Metric | Uniform Dijkstra ($h=0$) | Standard Admissible A* ($h=0.8\times$) | Aggressive A* ($h=1.25\times$) |
| :--- | :---: | :---: | :---: |
| **Mean Route Cost** | 11,102.66 | 11,102.66 | 11,109.82 |
| **Mean Physical Distance** | 9.36 km | 9.36 km | 9.36 km |
| **Mean Expanded States** | 108,963.2 | 38,766.3 | 24,587.8 |
| **State Reduction vs. Dijkstra** | Baseline ($0.0\%$) | **$-64.4\%$** | **$-77.4\%$** |
| **State Reduction vs. Admissible** | N/A | Baseline ($0.0\%$) | $-36.6\%$ |
| **Mean Search Runtime** | 1,927.23 ms | 599.07 ms | 380.85 ms |
| **Runtime Speedup vs. Dijkstra** | $1.00\times$ | **$3.22\times$** | **$5.06\times$** |
| **Mean Optimality Gap** | $0.0000\%$ | **$0.0000\%$** | **$+0.0678\%$** |
| **Maximum Optimality Gap** | $0.0000\%$ | **$0.0000\%$** | **$+0.4370\%$** |
| **Corridors with Suboptimal Output** | 0 / 10 ($0\%$) | **0 / 10 ($0\%$)** | **3 / 10 ($30\%$)** |

---

## 5. Detailed Analysis of Divergence Corridors

The benchmark confirmed that Aggressive A* converged on strictly suboptimal routes in three real-world corridors:

### 5.1 Case Study 1: OD_10 (BTM Layout to Domlur)
- **Dijkstra Cost:** $9,337.40$ (Distance: $7.78\text{ km}$)
- **Admissible A* Cost:** $9,337.40$ (Distance: $7.78\text{ km}$, 15,766 states)
- **Aggressive A* Cost:** $9,378.20$ (Distance: $7.88\text{ km}$, 6,964 states)
- **Optimality Gap:** **$+0.437\%$** (Cost penalty: $+40.80$ impedance units, $+100\text{ m}$ detour)
- **Underlying Cause:** Along the corridor connecting BTM to Domlur via the Intermediate Ring Road, the route reaches an interchange with multiple parallel options: an elevated bypass road with higher straight-line alignment versus a surface street with intermediate turn transitions. The aggressive heuristic ($1.25\times$) over-penalized the slight geometric curvature of the lower-cost inner route, causing the search to lock into an inferior arterial alignment.

### 5.2 Case Study 2: OD_06 (Jayanagar 4th Block to Malleshwaram)
- **Dijkstra Cost:** $14,153.24$ (Distance: $12.45\text{ km}$)
- **Admissible A* Cost:** $14,153.24$ (Distance: $12.45\text{ km}$, 71,735 states)
- **Aggressive A* Cost:** $14,177.89$ (Distance: $12.40\text{ km}$, 40,348 states)
- **Optimality Gap:** **$+0.174\%$** (Cost penalty: $+24.65$ impedance units)
- **Underlying Cause:** Interestingly, Aggressive A* selected a path that was $50\text{ m}$ shorter in physical length ($12.40\text{ km}$ vs. $12.45\text{ km}$), but had a higher total impedance cost due to navigating primary road segments carrying severe two-wheeler traffic penalties ($p = 2.2$) rather than inner-road corridors ($p = 0.9$). Because the aggressive heuristic measures Euclidean proximity, it greedily favoured the geometrically straight primary road, missing the superior inner-road routing discovered by Admissible A*.

### 5.3 Case Study 3: OD_09 (Rajajinagar to Commercial Street)
- **Dijkstra Cost:** $9,199.77$ (Distance: $8.29\text{ km}$)
- **Admissible A* Cost:** $9,199.77$ (Distance: $8.29\text{ km}$, 25,311 states)
- **Aggressive A* Cost:** $9,205.97$ (Distance: $8.27\text{ km}$, 14,808 states)
- **Optimality Gap:** **$+0.067\%$** (Cost penalty: $+6.20$ impedance units)
- **Underlying Cause:** Similar to OD_06, Aggressive A* prematurely pruned an inner collector turn sequence in favour of an arterial segment that had a direct compass heading toward Commercial Street.

---

## 6. Academic and Publication Insights

These empirical results provide critical material for the methodology and evaluation sections of the conference paper:

1. **Defensibility of Proposed Contribution:**  
   The project can rigorously claim that its turn-aware, state-expanded A* routing engine operates under an admissible and consistent heuristic that delivers mathematically optimal routes on OpenStreetMap graphs.
2. **Characterization of Heuristic Trade-offs:**  
   Rather than discarding the aggressive heuristic, it can be framed as an **experimental $\epsilon$-admissible search variant**. The paper can report:
   > *"While the standard admissible heuristic guarantees strictly optimal routing with a 64.4% reduction in expanded search states, an aggressive variant ($h = 1.25 \times \text{haversine}$) achieves a 77.4% state reduction at the cost of bounded suboptimality (mean gap: 0.068%, max gap: 0.437%)."*
3. **Reproducibility:**  
   All raw benchmark data, node IDs, coordinates, and timing breakdowns are permanently archived in `research/literature_survey/09_astar_correction/heuristic_benchmark_raw.json` for independent peer review.
