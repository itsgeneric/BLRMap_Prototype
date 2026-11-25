# Experimental Protocol: Alternative Routing Diversity & Performance Benchmark

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 10 — Alternative Route Generation, Diversity Filtering & Yen's KSP Comparison  
**Date:** March 2026  
**Artifact Paths:** `experiments/benchmark_alternative_routing.py`, `tests/test_alternative_routing.py`  

---

## 1. Experimental Objectives

This benchmark protocol provides a fair, reproducible, and mathematically rigorous comparative evaluation between two distinct alternative route generation paradigms on a large-scale real-world road network:

1. **Perpendicular-Offset Via-Node Generation (Proposed):**  
   Projects orthogonal lateral waypoints ($150\text{ m}, 300\text{ m}$) across journey chord fractions ($0.33, 0.50, 0.67$) and stitches two-leg turn-aware A* searches, subject to a 70% physical edge overlap filter and a 1.20 detour cap.
2. **Yen's K-Shortest Paths (State-Expanded Baseline):**  
   Classical deviation algorithm (Yen, 1971 [17]; Asvial et al., 2020 [5]) adapted to state-expanded turn-aware routing, evaluating up to $K=4$ shortest simple paths under an identical 1.20 detour cap.

### Research Questions Addressed:
- **RQ1 (Corridor Independence):** Does perpendicular-offset via-node generation discover independent secondary corridors, or does it merely produce minor arterial variations?
- **RQ2 (The Plateau Problem in Yen's KSP):** Does Yen's algorithm suffer from the theoretical "plateau problem" on the Bengaluru street grid, producing paths with $>80\%$ sharing?
- **RQ3 (Filtering Efficacy):** What percentage of candidate routes survive when a 70% physical edge-overlap threshold is strictly enforced?
- **RQ4 (Computational Efficiency):** What is the algorithmic runtime trade-off between the two approaches across varying corridor lengths?

---

## 2. Experimental Dataset: 25 Metropolitan Bengaluru Corridors

To ensure representative coverage of the metropolitan area of Bengaluru, 25 origin-destination pairs were selected spanning diverse functional contexts:
- **Radial Arterials:** Connecting residential suburbs to the Central Business District (CBD).
- **Ring Road Commutes:** Navigating Outer Ring Road (ORR) and Intermediate Ring Road (IRR) tech corridors.
- **Dense Historic Grids:** Navigating historic grid patterns in Basavanagudi, Jayanagar, and Malleshwaram.
- **Peripheral Diagonal Links:** Traversing cross-city commutes with multi-flyover and service road alternatives.
- **Corridor Distance Range:** Spanning from $1.35\text{ km}$ (Richmond Town to Brigade Road) to $15.04\text{ km}$ (Bellandur to Whitefield), with an average journey distance of $7.1\text{ km}$.

### Corridor Inventory Table

| ID | Corridor Name | Origin Lat, Lng | Destination Lat, Lng | Journey Character | Typical Distance |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **OD_01** | BNMIT to MG Road | 12.9237, 77.5714 | 12.9756, 77.6066 | South suburban residential to CBD core | ~10.1 km |
| **OD_02** | Koramangala to Indiranagar | 12.9352, 77.6245 | 12.9719, 77.6412 | Intermediate Ring Road tech hub connector | ~6.4 km |
| **OD_03** | Electronic City to Silk Board | 12.8452, 77.6602 | 12.9176, 77.6238 | Elevated expressway vs. service road arterial | ~9.5 km |
| **OD_04** | Whitefield to Marathahalli | 12.9698, 77.7500 | 12.9569, 77.7011 | Eastern tech corridor with heavy arterial friction | ~8.8 km |
| **OD_05** | Hebbal to Majestic | 13.0358, 77.5970 | 12.9767, 77.5713 | North-South trunk arterial traversing flyovers | ~9.9 km |
| **OD_06** | Jayanagar 4th to Malleshwaram | 12.9250, 77.5838 | 13.0031, 77.5643 | Cross-city transit through central bottleneck | ~12.5 km |
| **OD_07** | HSR Layout to Bellandur | 12.9121, 77.6446 | 12.9304, 77.6784 | Suburban collector bordering Outer Ring Road | ~5.8 km |
| **OD_08** | Banashankari to Yeshwanthpur | 12.9255, 77.5468 | 13.0285, 77.5409 | Major diagonal commute across western arterials | ~14.6 km |
| **OD_09** | Rajajinagar to Commercial St | 12.9915, 77.5523 | 12.9822, 77.6083 | Dense mixed-use commercial and residential grid | ~8.3 km |
| **OD_10** | BTM Layout to Domlur | 12.9166, 77.6101 | 12.9609, 77.6387 | Ring-road bypass with intermediate flyovers | ~7.8 km |
| **OD_11** | Basavanagudi to Ulsoor | 12.9416, 77.5738 | 12.9818, 77.6284 | Historic south-central to eastern lake hub | ~11.4 km |
| **OD_12** | Frazer Town to Shivajinagar | 12.9982, 77.6145 | 12.9856, 77.6006 | Historic Cantonment commercial grid | ~2.7 km |
| **OD_13** | JP Nagar 6th to Koramangala | 12.9063, 77.5855 | 12.9352, 77.6245 | South suburban connector across residential lanes | ~7.9 km |
| **OD_14** | Vijayanagar to Majestic | 12.9719, 77.5306 | 12.9767, 77.5713 | Western radial arterial into railway transit core | ~7.2 km |
| **OD_15** | Yelahanka to Hebbal | 13.1007, 77.5963 | 13.0358, 77.5970 | Northern express highway corridor | ~8.7 km |
| **OD_16** | Bellandur to Whitefield | 12.9304, 77.6784 | 12.9698, 77.7500 | Major Outer Ring Road to ITPL corridor | ~15.0 km |
| **OD_17** | Malleshwaram to Rajajinagar | 13.0031, 77.5643 | 12.9915, 77.5523 | Short western grid arterial link | ~3.4 km |
| **OD_18** | Indiranagar to MG Road | 12.9719, 77.6412 | 12.9756, 77.6066 | Eastern metro corridor along Old Airport Road | ~5.9 km |
| **OD_19** | Silk Board to BTM 2nd Stage | 12.9176, 77.6238 | 12.9166, 77.6101 | Bottleneck junction bypass link | ~2.0 km |
| **OD_20** | Kengeri to Satellite Bus Station | 12.9081, 77.4852 | 12.9536, 77.5432 | Far south-western expressway corridor | ~12.3 km |
| **OD_21** | RT Nagar to Cantonment | 13.0238, 77.5936 | 12.9935, 77.6001 | North-central residential to cantonment | ~5.0 km |
| **OD_22** | Marathahalli to HAL Airport Rd | 12.9569, 77.7011 | 12.9609, 77.6582 | Primary eastern arterial commute | ~7.7 km |
| **OD_23** | Richmond Town to Brigade Road | 12.9667, 77.6015 | 12.9733, 77.6074 | Ultra-dense CBD shopping grid | ~1.4 km |
| **OD_24** | Banaswadi to Kammanahalli | 13.0142, 77.6519 | 13.0094, 77.6367 | North-eastern suburb connector | ~2.4 km |
| **OD_25** | Padmanabhanagar to Gandhi Bazaar | 12.9180, 77.5576 | 12.9463, 77.5694 | Traditional south Bengaluru market corridor | ~4.6 km |

---

## 3. Strict Fair Evaluation Controls

To eliminate confounding variables and ensure complete academic fairness:
1. **Identical Road Graph:** Both algorithms execute on the same compiled NetworkX `MultiDiGraph` (`bengaluru_graph.pkl`, 744,216 directed edges).
2. **Identical Snapped Nodes:** Origin and destination coordinates are snapped once via `ox.nearest_nodes()`, and the identical integer node IDs $(s, t)$ are passed to both algorithms.
3. **Identical Edge Cost Function:** Both algorithms use `two_wheeler_edge_cost()` with standard penalties (`main_road_penalty=1.5, inner_road_multiplier=0.9`).
4. **Identical Turn Penalties:** Both algorithms evaluate `_turn_penalty()` with identical sharp ($+25.0$) and moderate ($+8.0$) turn penalties.
5. **Identical Path Costing:** Final route costs are computed via `path_cost()`.
6. **Identical Detour Constraint:** Both algorithms enforce `max_detour = 1.20` (detour ratio $\le 1.20$).
7. **Identical Target Count:** Both algorithms attempt to discover up to 3 alternative routes ($K=4$ total routes including primary).

---

## 4. Evaluation Metrics and Quantitative Formulas

For every evaluated corridor, nine distinct performance metrics are recorded:

1. **Number of Valid Alternatives Generated ($K_{\text{valid}}$):**  
   Number of alternatives surviving all filtering constraints ($0 \le K_{\text{valid}} \le 3$).
2. **Physical Route Distance ($L$ in km):**  
   Physical distance calculated via `calc_route_distance(G, route)`.
3. **Total Turn-Aware Impedance Cost ($C$):**  
   Computed via `path_cost(G, route, graph_mgr, penalties)`.
4. **Detour Ratio Relative to Primary Route ($\epsilon$):**  
   $$\text{DetourRatio}(P_{\text{alt}}) = \frac{\text{Length}(P_{\text{alt}})}{\text{Length}(P_{\text{primary}})}$$
5. **Percentage of Shared Edges with Primary Route ($\gamma$ in %):**  
   $$\text{Overlap}(P_{\text{primary}}, P_{\text{alt}}) = \frac{\sum_{e \in E(P_{\text{primary}}) \cap E(P_{\text{alt}})} \text{length}(e)}{\text{Length}(P_{\text{alt}})} \times 100\%$$
6. **Jaccard Edge Similarity ($J$):**  
   $$J(P_{\text{primary}}, P_{\text{alt}}) = \frac{\text{SharedEdgeLength}}{\text{Length}(P_{\text{primary}}) + \text{Length}(P_{\text{alt}}) - \text{SharedEdgeLength}}$$
7. **Average Pairwise Route Diversity ($\Delta$):**  
   $$\Delta = 1.0 - \frac{1}{\binom{M}{2}} \sum_{0 \le i < j < M} J(P_i, P_j)$$
8. **Algorithmic Execution Time ($T$ in ms):**  
   Total end-to-end runtime measured via `time.perf_counter()`.
9. **Candidate Generation & Rejection Counts:**  
   Total candidate paths explored, broken down by rejection reason (`exact_duplicate`, `detour_exceeded`, `overlap_exceeded`, `invalid_disconnected`).

---

## 5. Automated Data Archival

All raw experimental measurements are permanently exported in two open formats:
- **`research/literature_survey/10_alternative_routing/alternative_routing_raw.json`:**  
  Full hierarchical data with start/end node IDs, candidate breakdowns, individual route metrics, and diagnostic rejection counts.
- **`research/literature_survey/10_alternative_routing/alternative_routing_raw.csv`:**  
  Tabular dataset containing one row per individual route (Primary, Alt_1, Alt_2, Alt_3) for statistical aggregation and plotting in LaTeX / matplotlib.
