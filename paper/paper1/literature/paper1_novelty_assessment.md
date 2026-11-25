# Novelty Assessment for Paper 1

**Target Paper:** IEEE Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Governing Skills:** `blrmap-research-protocol`, `evidence-integrity-audit`  
**Date:** 2026-11-05  
**Document:** `research/paper1_literature/paper1_novelty_assessment.md`  
**Status:** Completed Novelty & Distinctiveness Audit

---

## 1. Comparative Analysis Against Closely Related Prior Work

To establish whether Paper 1 provides a sufficiently distinct contribution for an IEEE conference publication (e.g., IEEE ITSC, IEEE VTC, IEEE INDICON), we systematically compare our approach across nine technical dimensions against the five most closely related benchmark publications:

| Technical Dimension | Winter (2002) [6] | Geisberger & Vetter (2011) [7] | Delling et al. (2017) [8] | Asvial et al. (2020) [5] | **BLRMap Paper 1 (Our Work)** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Graph Representation** | Materialized line graph $L(G) = (V_L, E_L)$ | Edge-contracted hierarchy with localized turn tables | Multi-level nested overlay cells via PUNCH partitioning | Standard node-based primal graph in pgRouting | **Primal graph with implicit priority queue state $s=(u,v)$ ($\mathcal{O}(\vert E\vert)$ memory)** |
| **2. Search Algorithm** | Standard Dijkstra / A* on line graph | Bidirectional Dijkstra on contracted hierarchy | Bidirectional search on overlay graphs (CRP) | $k$-Shortest Paths (Yen's variant) with entropy balancing | **Turn-aware goal-directed A\* with dynamic predecessor tracking** |
| **3. Turn-Cost Formulation** | Static geometric turn angle delay penalties | Static turn tables baked into contraction shortcuts | Metric-customized cell boundary turn transition matrices | **Completely ignored ($\text{turn penalty} = 0$)** | **Discrete vehicle-differentiated deflection penalties ($0\text{m}, 8\text{m}, 25\text{m}$) computed on-the-fly** |
| **4. Road Impedance Formulation** | Unspecified / General GIS travel time | Automobile-centric functional hierarchy | Arbitrary linear scalarization of road attributes | Narrow road prioritization; static database link weights | **Inverted peak-hour hierarchy (residential 1.0 > primary 2.2 > motorway 4.0)** |
| **5. Infrastructure Modifiers** | None | Standard bridge / tunnel traversal times | Generalized attribute flags | None | **Bridge replacement modifier ($0.80$ overrides arterial penalty)** |
| **6. Heuristic Admissibility** | Admissible Euclidean bound on $L(G)$ | None (Dijkstra search without spatial heuristic) | None (Overlay Dijkstra without spatial heuristic) | Unverified; no formal admissibility analysis | **Strictly admissible scaled Haversine ($h(u) = 0.80 \cdot d_{\text{haversine}}(u,t) \le c^*(u,t)$)** |
| **7. Vehicle-Specific Focus** | General vehicles (cars, trucks) | Passenger cars on European highways | Multi-profile (commercial fleet, passenger cars) | Motorized two-wheelers in Jakarta | **Motorized two-wheelers in congested South Asian mixed traffic (Bengaluru)** |
| **8. Experimental Design** | Synthetic planar grid network simulations | Continental European road networks (~18M nodes) | North American & European networks (~50M edges) | 6 simulated OD pairs in South Jakarta | **25 real-world corridors across Bengaluru metropolitan network ($N=25$)** |
| **9. Evaluation Metrics** | Route length and zig-zag step counts | Query time (ms) and contraction preprocessing time | Customization time (ms) and query latency (ms) | Trip length, vehicle distribution variance, CPU time | **Sharp turn counts, road-class shares, flyover traversal, distance overhead, Pareto knee** |

---

## 2. Explicit Novelty Deconstruction

To maintain strict research integrity, we delineate our work into five clear categories:

### A. What Has Already Been Done (Prior Art)
1. **Edge-Based Turn Modeling:** Winter (2002) [6] established the mathematical theory of modeling turn costs via line graphs. Geisberger & Vetter (2011) [7] proved that edge transitions can be handled in hierarchical speedup techniques without full line graph materialization.
2. **Metric Customizability:** Delling et al. (2017) [8] established that customizable cost metrics can be applied to road networks to reflect vehicle profiles and user preferences.
3. **OpenStreetMap Network Extraction:** Boeing (2017) [14] and Luxen & Vetter (2011) [15] developed robust methods for extracting routable topological graphs and road classes from OpenStreetMap.
4. **Motorcycle OpenStreetMap Routing:** Asvial et al. (2020) [5] previously investigated using OpenStreetMap data for motorcycle route planning in a congested Southeast Asian megacity (Jakarta).
5. **Microscopic Kinematics in Mixed Traffic:** Promraksa et al. [1], Kotagi et al. [2], Das & Maurya [3], and Fadilah et al. [4] established empirical data on two-wheeler lane filtering, speed differentials, and route choices.

---

### B. What is Similar to Our Approach
1. **State-Space Expansion:** Like Kirby & Potts [16] and Winter [6], we recognize that turn costs require tracking the incoming edge to an intersection.
2. **OpenStreetMap-Based Graph Modeling:** Like Asvial et al. [5] and Luxen & Vetter [15], we extract road topologies, segment lengths, and functional highway classifications from OpenStreetMap.
3. **Exploitation of Secondary Roads:** Like Asvial et al. [5], our routing engine utilizes narrow residential and secondary streets to bypass arterial bottlenecks.

---

### C. What is Genuinely Different in Paper 1
1. **Dynamic Spherical Deflection in A\* Priority Queue:**  
   Unlike Winter [6] (which requires materializing a massive line graph with 3× to 5× memory overhead) and Geisberger & Vetter [7] (which freezes turn costs into static Contraction Hierarchy shortcuts), our engine computes spherical deflection angles $\Delta \theta$ dynamically on-the-fly from vertex coordinates during priority queue expansion, tracking states $s = (u, v)$ with an $\mathcal{O}(|E|)$ memory footprint and zero offline preprocessing.
2. **Vehicle-Differentiated Turn Thresholds for Two-Wheelers:**  
   Unlike car-centric turn models that penalize all tight corners equally, our discrete threshold model distinguishes maneuver physics:
   - Tight turns on residential streets ($30^\circ\text{--}60^\circ$) incur only an $8\text{ m}$ penalty because two-wheelers have negligible turning radii.
   - Hazardous turns across opposing traffic ($\ge 60^\circ$) incur a heavy $25\text{ m}$ penalty.
   - Crucially, this directly solves the fundamental flaw of Asvial et al. [5], who completely ignored turn penalties ($\text{turn cost} = 0$), producing erratic, turn-heavy paths.
3. **Formal Proof of Scaled Haversine Admissibility:**  
   When combining edge discounts (e.g., flyover modifier $\mu_{\min} = 0.80$) with non-negative turn penalties, an unscaled Haversine heuristic overestimates remaining path cost and breaks A\* admissibility. We provide a formal proof that scaling great-circle Haversine distance by the minimum penalty floor ($h(u) = 0.80 \cdot d_{\text{haversine}}(u, t)$) guarantees strict admissibility ($h(u) \le c^*(u, t)$) without requiring precomputed landmark bounds.
4. **Arterial Bridge Penalty Replacement:**  
   We implement an explicit structural modifier where `bridge=yes` on primary arterials replaces the heavy arterial penalty ($2.20\text{--}4.00$) with a preferred multiplier of $0.80$, effectively channeling two-wheelers onto elevated expressways while avoiding ground-level arterial congestion.
5. **Empirical Multi-Objective Pareto Sensitivity Validation:**  
   We provide a systematic sensitivity analysis across discrete penalty tiers ($C_0 \to C_1 \to C_2 \to C_3$) across 25 real-world corridors in Bengaluru, demonstrating monotonic sharp turn reduction ($32.52 \to 24.64 \to 21.44 \to 19.80$) and proving that Baseline $C_2(25/8)$ represents the empirical corpus-average trade-off knee.

---

### D. What CANNOT Reasonably Be Claimed as Novel
To prevent reviewer rejection, the following claims must **NEVER** be made:
- **DO NOT CLAIM** that edge-based state expansion or line graph routing is a newly invented algorithm. It is a recognized technique established by Kirby & Potts (1969) and Winter (2002).
- **DO NOT CLAIM** that road-class weighting on OpenStreetMap is novel. OSRM (Luxen & Vetter 2011) and GraphHopper have supported road penalty profiles for over a decade.
- **DO NOT CLAIM** that our road impedance weights are validated by rider preference surveys. Our weights are heuristic parameters derived from literature observations ([1]–[4]), not from primary stated-preference surveys.
- **DO NOT CLAIM** demonstrated improvements in commuter safety, accident rate reductions, or real-world fuel economy. These human and traffic factors were not directly measured.
- **DO NOT CLAIM** that the roundabout modifier improved network routing. Experiment D proved it was empirically invariant across all 25 corridors.
- **DO NOT CLAIM** an empirical signal-based queue filtering ETA calibration model. The code stubs are uninvoked and uncalibrated in the frozen experimental results.

---

### E. Contribution Strength Assessment

| Evaluation Criterion | Rating | Scholarly Justification |
| :--- | :---: | :--- |
| **Algorithmic Soundness** | **Strong** | The state-expanded A\* formulation is mathematically complete, respects graph theory invariants, and includes a rigorous proof of Haversine admissibility ($h = 0.80 \cdot d_{\text{haversine}}$). |
| **Domain Distinction** | **Strong** | Addresses a genuine real-world transportation informatics failure in South Asian megacities, directly overcoming the critical gap in Asvial et al. [5] (zero turn penalties) and OSRM [15] (car-centric arterial bias). |
| **Empirical Validation** | **Strong** | Validated on a metropolitan corpus of 25 real-world corridors in Bengaluru across 1,855 timing observations, backed by Pratt-adjusted Wilcoxon signed-rank tests with Holm-Bonferroni corrections ($p_{\text{adj}} < 0.001$). |
| **Theoretical Novelty** | **Moderate** | The underlying search algorithm combines existing concepts (state-expanded A\*, spherical deflection, A\* admissibility). The novelty lies in the *specific transportation formulation, heuristic proof, and empirical synthesis*, not in inventing a new general graph search class. |

---

## 3. Verdict on Paper 1

**Overall Contribution Rating:** **STRONG CONTRIBUTION (Defensible for IEEE Conference Publication)**

### Reasoning:
Paper 1 presents a cohesive, mathematically rigorous, fully implemented, and empirically frozen contribution. While neither state-expanded search nor road weighting is novel in isolation, their **principled synthesis into a two-wheeler-aware routing engine that enforces admissibility, models vehicle-differentiated discrete turn angles, selectively channels elevated flyovers, and empirically demonstrates Pareto trade-off optimality on 25 real-world Bengaluru corridors** provides a complete and publication-ready IEEE conference paper.
