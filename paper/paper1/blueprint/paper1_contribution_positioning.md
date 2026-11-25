# Paper 1 Contribution and Novelty Positioning

**Document:** [`paper1_contribution_positioning.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_contribution_positioning.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE SCHOLARLY POSITIONING**

---

## 1. Problem Formulation and Research Gap

### 1.1 The Urban Research Problem
In rapidly expanding South Asian megacities (e.g., Bengaluru, India), powered two-wheelers constitute over $70\%$ of active motorized traffic. While two-wheelers possess superior kinematic agility and permeability through narrow corridors, riders face severe safety vulnerabilities in mixed, un-signalized traffic environments. Two primary operational factors dominate this vulnerability:
1. **Crossing Conflicts at Intersections:** Sharp, high-angle turns ($\ge 60^\circ$) across conflicting oncoming vehicular flows without dedicated turning phases.
2. **Arterial Speed Disparities:** Prolonged exposure on high-speed, saturated multi-lane arterial corridors where motorcycles share lanes with heavy buses and commercial vehicles.

### 1.2 The Existing Algorithmic Research Gap
Current navigation architectures fail to address this operational reality:
- **Node-Space Shortest-Path Engines (OSRM, standard Dijkstra/A\*):** Model road networks as vertex-attributed graphs where intersection nodes are dimensionless points. Because turns are transitions between edges rather than vertex properties, these engines cannot penalize turning maneuvers during search. Consequently, distance minimization generates erratic zig-zag alley shortcuts with numerous hazardous right-angle turns.
- **Hierarchical Pre-computation Speedup Techniques (Contraction Hierarchies, CCH):** Achieve sub-millisecond query times by building static contraction shortcuts based on automobile travel-time hierarchies. These hierarchies rigidly prioritize high-speed motorways and arterials, funnelling two-wheelers onto congested, high-stress corridors while lacking metric flexibility for vehicle-specific impedance.
- **Post-Hoc Multi-Criteria Routing:** Studies attempting two-wheeler route planning (e.g., Asvial et al., 2020) rely on multi-attribute decision-making (TOPSIS/Entropy) applied to pre-computed routes, lacking online heading awareness and failing to optimize turn geometry within the core graph search.

**The Concrete Gap:** There is an absence of an exact, admissible, and computationally lightweight turn-aware routing framework tailored specifically to two-wheeler impedance on raw metropolitan networks that can be executed locally without heavy preprocessing.

---

## 2. Itemized Manuscript Contributions

To satisfy IEEE standards of intellectual honesty, we clearly distinguish our contributions into technical, mathematical, and empirical domains:

### 2.1 Main Technical Contribution
- **Unified Turn-Aware State-Expanded Engine:** We design and implement a locally controlled, point-to-point two-wheeler routing engine operating over the directed edge state space $S = E \cup \{(\text{None}, s_0)\}$. The engine calculates discrete angular heading deflections $\Delta\theta$ directly from spherical node coordinates during edge relaxation, applying calibrated physical turn penalties ($P_{\text{sharp}} = 25.0\text{ m}, P_{\text{mod}} = 8.0\text{ m}$) directly within the graph search.

### 2.2 Supporting Mathematical Contribution
- **Conditional Admissibility and Monotonic Consistency Proofs:** We provide formal deductive proofs that the great-circle Haversine distance scaled by the minimum road multiplier ($\mu_{\min} = 0.80$),  
  $$h(s) = 0.80 \cdot D_{\text{haversine}}(v, t),$$  
  is strictly admissible ($h(s) \le c^*(s)$) and monotonically consistent ($h(s) \le c(s, s') + h(s')$) on state space $S$, conditioned on Assumption A1 ($\mu(e) \ge 0.80$). This mathematically guarantees that states $(u, v)$ are finalized on their first heap extraction without requiring state reopening.
- **Valence-Bounded Asymptotic Complexity:** We derive the exact priority queue dynamics in the absence of `decrease-key`, proving that under bounded physical intersection valence (Assumption A2: $d_{\max} = \mathcal{O}(1)$), auxiliary memory is strictly $\mathcal{O}(|E|)$ and worst-case execution time is strictly $\mathcal{O}(|E| \log |E|)$.

### 2.3 Empirical Contribution
- **Metropolitan Benchmark Ablation:** We evaluate the routing engine across 25 validated corridors spanning short, medium, and long distances on a 744,216-edge in-memory NetworkX graph of Bengaluru ($1,855$ total execution runs):
  1. *Turn Elimination:* Eliminates $34.1\%$ of sharp maneuvers ($21.44$ vs $32.52$ turns, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$).
  2. *Corpus-Bounded Route Equivalence:* Proves that when turn penalties are zeroed ($P=0$), state-expanded search (Condition A1) and standard node-level search (Condition A2) produce identical node sequences, physical distances ($7.723\text{ km}$), and impedance costs across all $25 / 25$ corridors.
  3. *Arterial Suppression:* Inverted two-wheeler road impedance suppresses arterial exposure by $51.21$ percentage points ($13.84\%$ vs $65.05\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, $d_z = -1.7715$) while increasing residential routing by $+30.73\text{ pp}$.
  4. *Pareto Trade-off Knee:* Identifies baseline $C_2$ ($25/8$) as the empirical corpus-average trade-off knee, capturing $87.1\%$ of maximum turn reduction while minimizing mean physical distance ($7.648\text{ km}$).
  5. *Flyover Channelization:* Establishes that the $0.80\times$ arterial bridge discount increases elevated bridge traversal by $+148.9\%$ ($-111.6\text{ m}$ route distance).

---

## 3. Demarcation from Established Prior Work

The manuscript will explicitly cite and credit prior foundational work, avoiding any claim that individual algorithmic components are novel:

| Algorithmic Component | Established Prior Work Cited | What is Already Known | Our Specific Integration & Contribution |
| :--- | :--- | :--- | :--- |
| **Line-Graph State Expansion** | Kirby (1969); Winter (2002) | Turn costs require edge-based or line-graph states $(u, v)$ to maintain Markovian property. | Applied to raw OpenStreetMap metropolitan road network without pre-processing shortcuts; parameterized with discrete vehicular heading thresholds. |
| **Heuristic Search & Admissibility** | Hart, Nilsson, & Raphael (1968); Goldberg & Harrelson (2005) | Euclidean/Haversine distance is a lower bound for physical distance on planar graphs. | Scaled lower-bound proof ($0.80 \cdot D_{\text{haversine}}$) under composite impedance modifiers; formal verification that Assumption A1 holds on Bengaluru's 744,216 edges. |
| **Road-Class Impedance Weighting** | Promraksa & Satiennam (2022); Fadilah et al. (2024) | Motorcycles cut through residential streets to avoid congested arterials. | Operationalized into an inverted weighting matrix with elevated arterial flyover overrides ($0.80$) that channel routes away from surface intersections. |
| **Multi-Criteria Route Evaluation** | Zografos & Androutsopoulos (2004); Asvial et al. (2020) | Multi-criteria optimization evaluates distance vs. comfort/stress trade-offs. | Formalization of the empirical Pareto frontier $\{C_2, C_3\}$ and identification of the corpus-average trade-off knee ($C_2: 25/8$). |

---

## 4. Prohibited Over-Claims & Scientific Boundaries

To preserve strict construct validity under [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md) and [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), the manuscript will explicitly disclaim the following:

1. **NO Safety or Accident Reduction Claims:**  
   The study measures purely physical distance ($m$), discrete turn counts ($\ge 60^\circ, 30^\circ\text{--}60^\circ$), and road-class shares ($\%$). No collision, trauma registry, police accident, or hospital injury data was collected or analyzed. The paper will not claim that the routes "improve rider safety" or "reduce accident rates."
2. **NO Real-World Dynamic Travel-Time Claims:**  
   The study evaluates computational CPU execution runtime ($ms$) and static network impedance. No real-world GPS probe telemetry, floating car data, or dynamic congestion feeds were evaluated. The paper will not claim real-world travel-time savings.
3. **NO Roundabout Routing Improvement Claims:**  
   In Experiment D, the roundabout modifier produced $0$ route geometry changes across the 25 evaluated corridors. The paper will report this honestly as an operational invariance rather than claiming an empirical routing improvement.
4. **NO Alternative Route Generation Claims:**  
   All alternative-route generation methods, lateral waypoint offsets, and topological diversity benchmarks (Experiment E) belong strictly to **Paper 2**. Paper 1 focuses exclusively on point-to-point optimal routing, impedance modeling, and turn sensitivity.

---

*Positioning verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
