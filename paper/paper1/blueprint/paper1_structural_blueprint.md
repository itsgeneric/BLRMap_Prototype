# Paper 1 Structural Blueprint

**Document:** [`paper1_structural_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_structural_blueprint.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Length:** Exactly 6.0 Pages (including references, figures, and tables)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE STRUCTURAL SPECIFICATION**

---

## Complete Manuscript Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PAPER 1 SIX-PAGE TOPOLOGICAL LAYOUT                             │
├────────────────────┬────────────────────┬────────────────────┬─────────────────────────┤
│ PAGE 1             │ PAGE 2             │ PAGE 3             │ PAGE 4                  │
│ • Title & Abstract │ • II. Related Work │ • IV. Turn-Aware   │ • V. Experimental Setup │
│ • Index Terms      │   (Conclusion)     │   A* Algorithm     │   & Benchmark Corpus    │
│ • I. Introduction  │ • Table I: Road    │ • Theorems 1 & 2   │ • Table II: Ablation    │
│   (Context, Gap,   │   Impedance Map    │   (Proofs)         │   Factorial Matrix      │
│   Contributions)   │ • III. Problem     │ • Theorem 3        │ • VI. Results: Exp A    │
│ • II. Related Work │   Formulation &    │   (Complexity)     │ • Fig. 1: Exp A Trade-  │
│   (Turn Costs &    │   Mathematical     │ • Algorithm 1:     │   offs (Boxplots)       │
│   Two-Wheelers)    │   Model            │   Pseudo-code      │                         │
├────────────────────┴────────────────────┴────────────────────┴─────────────────────────┤
│ PAGE 5                                  │ PAGE 6                                       │
│ • VI. Results: Exp B (Road Classes)     │ • VII. Limitations & Discussion              │
│ • Fig. 2: Exp B Distribution            │ • VII. Conclusion & Future Work              │
│ • VI. Results: Exp C (Turn Sensitivity) │ • Acknowledgment & Data Availability         │
│ • Fig. 3: Exp C Pareto Knee Curve       │ • References (15–16 Audited IEEE Citations)  │
│ • VI. Results: Exp D (Bridge/Rbt)       │                                              │
│ • Table III: Paired Statistical Results │                                              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Section-by-Section Blueprint

### Front Matter (Page 1, Top Span)
- **Title:** *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*
- **Authors & Affiliations:** Author names, Department of Computer Science & Engineering, Bengaluru, India.
- **Abstract (180–200 words):**
  - *Context:* Two-wheelers dominate urban transport in developing Asian megacities but suffer high vulnerability at sharp intersection turns and on high-speed arterials.
  - *Gap:* Conventional shortest-path navigation engines operate on dimensionless node graphs, ignoring vehicular heading changes and funneling motorcycles onto congested main roads.
  - *Method:* We propose a turn-aware, state-expanded $A^*$ search framework integrated with two-wheeler-specific road impedance modeling and elevated flyover channelization. The search operates over directed edge states $s=(u, v)$, with an admissible and consistent scaled Haversine heuristic ($h = 0.80 \cdot D_{\text{haversine}}$).
  - *Results:* Evaluated on a 25-corridor metropolitan corpus on Bengaluru's 744,216-edge road network ($R=5$ repetitions), our engine eliminates $34.1\%$ of sharp maneuvers ($\ge 60^\circ$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$) and suppresses arterial road exposure by $51.21$ percentage points ($p_{\text{adj}} = 8.4 \times 10^{-5}$, $d_z = -1.7715$) at a median runtime of $174.93\text{ ms}$.
- **Index Terms:** Shortest path algorithms, state-expanded search, turn penalties, two-wheeler routing, road network impedance, urban mobility.

---

### Section I: Introduction (Page 1, Col 1 Bottom – Col 2 Top)
- **Paragraph 1: Motivation & Urban Mixed Traffic Context.**  
  Introduce two-wheeler travel dynamics in South Asian cities (Bengaluru). Two-wheelers represent $>70\%$ of vehicular volume, exhibiting unique kinematic capabilities (filtering, agility) coupled with acute vulnerability to conflicting cross-traffic maneuvers at un-signalized intersections.
- **Paragraph 2: Failure of Automobile-Oriented Routing.**  
  Examine standard shortest-path engines (OSRM, Dijkstra/A* on vertex space $V$). They evaluate intersections as dimensionless scalar points, ignoring the cost of vehicular heading deflections. Consequently, engines generate erratic zig-zag alley shortcuts with numerous hazardous right-angle turns across opposing traffic, or default to saturated arterials.
- **Paragraph 3: Research Gap.**  
  Existing turn-aware algorithms rely either on computationally heavy Contraction Hierarchies with car-centric metric pre-computation, or on heuristic multi-criteria ranking that ignores heading geometry during search. An exact, admissible, and computationally lightweight turn-aware routing framework tailored to two-wheeler impedance on raw metropolitan networks is missing.
- **Paragraph 4: Itemized Contributions.**  
  Formally state the four contributions of this paper:
  1. *State-Expanded Turn-Aware Search:* Formulation of $A^*$ over directed edge pairs $s = (u, v)$ evaluating discrete angular heading penalties during search.
  2. *Admissibility & Consistency Guarantees:* Deductive proof of conditional admissibility and monotonic consistency for the scaled Haversine heuristic ($h = 0.80 \cdot D_{\text{haversine}}$), ensuring optimal state finality without reopening.
  3. *Vehicle-Specific Road Impedance Model:* Empirical impedance function combining inverted arterial penalties with grade-separated flyover discounts ($0.80\times$).
  4. *Metropolitan Empirical Ablation:* Controlled $N=25$ corridor ablation on Bengaluru's 744,216-edge network demonstrating $34.1\%$ sharp-turn reduction, $51.21\text{ pp}$ arterial exposure reduction, and identifying the empirical Pareto trade-off knee ($C_2: 25/8$).

---

### Section II: Related Work (Page 1, Col 2 Bottom – Page 2, Col 1 Top)
- **Subsection II-A: Turn-Cost Shortest Path Routing.**  
  Review line-graph state expansion and turn-prohibition literature (Kirby 1969; Winter 2002). Contrast with speedup techniques (Geisberger & Vetter 2011; Delling et al. 2017; Bast et al. 2016). Highlight that pre-processed hierarchies lack dynamic metric flexibility for vehicle-specific road preferences.
- **Subsection II-B: Two-Wheeler Route Choice & Urban Impedance.**  
  Review motorcycle travel behavior and gap acceptance in mixed traffic (Promraksa & Satiennam 2022; Kotagi et al. 2020; Das et al. 2019; Fadilah et al. 2024). Analyze multi-criteria routing attempts (Asvial et al. 2020) and point out their critical limitation: treating turns post-hoc rather than within the search graph.
- **Subsection II-C: Heuristic Admissibility & Search Bounds.**  
  Review A* heuristic foundations (Hart et al. 1968), landmark heuristics (Goldberg & Harrelson 2005), and spatial street graph extraction (Boeing 2017). Establish our demarcation: direct state-space expansion with a closed-form scaled spherical lower-bound heuristic.

---

### Section III: Problem Formulation and Mathematical Model (Page 2, Col 1 Bottom – Col 2 Full)
- **Subsection III-A: Metropolitan Road Network.**  
  Formal definition of directed multigraph $G = (V, E)$ with physical surveyed segment lengths $\ell(e) > 0$.
- **Subsection III-B: Two-Wheeler Impedance Function.**  
  Define composite edge multiplier $\mu(e) = f_{\text{class}}(\text{hw}_e) \cdot m_{\text{bridge}}(e) \cdot m_{\text{rbt}}(e) \cdot m_{\text{surf}}(e)$.  
  - *Table I:* Road-class penalties ($0.90$ to $4.0$), flyover override ($0.80$), roundabout factor ($0.95$), and default fallback values.
  - Note on flyover override: replaces arterial penalty with $0.80$ to channel routes onto grade-separated corridors.
- **Subsection III-C: Angular Turn Penalty Function.**  
  Formulate discrete turn penalty $P_{\text{turn}}(u, v, w)$ based on bearing difference $\Delta\theta$:
  $$P_{\text{turn}}(u, v, w) = \begin{cases} 25.0 & \text{if } \Delta\theta \ge 60^\circ \\ 8.0 & \text{if } 30^\circ \le \Delta\theta < 60^\circ \\ 0.0 & \text{if } \Delta\theta < 30^\circ \text{ or } u = \text{None} \end{cases}$$
  - *Lemma 1 (Initial Departure Invariance):* $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$.
- **Subsection III-D: State Space and Transition Cost.**  
  State space $S = E \cup \{(\text{None}, s_0)\}$. Transition cost $c(s, s') = \ell(v, w) \cdot \mu(v, w) + P_{\text{turn}}(u, v, w)$. Note $c(s, s') > 0$.

---

### Section IV: Proposed Turn-Aware Routing Algorithm (Page 3 Full)
- **Subsection IV-A: State-Expanded A\* Search Architecture.**  
  Explain queue mechanics, hash-map tracking (`g_score`, `came_from`), and state transitions.  
  Explain state cardinality $|S| = |E| + 1$ and transition cardinality $|E_S| = \sum_v d_{\text{in}}(v) d_{\text{out}}(v)$.
- **Subsection IV-B: Scaled Haversine Heuristic.**  
  Define $h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t)$, where $\mu_{\min} = 0.80$.
- **Subsection IV-C: Formal Theoretical Proofs.**  
  - *Assumption A1 (Graph Multiplier Lower Bound):* $\forall e \in E, \mu(e) \ge 0.80$.  
  - *Theorem 1 (Conditional Admissibility):* Proof using spherical triangle inequality and $\mu_{\min}$ scaling ($h(s) \le c^*(s)$).  
  - *Theorem 2 (Conditional Monotonic Consistency):* Proof showing $h(s) \le c(s, s') + h(s')$.  
  - *Corollary 1 (Optimal State Finality):* Monotonic consistency guarantees that each state $(u, v)$ is finalized on its first extraction from `open_set` without reopening. Clarify that physical vertices $v$ are expanded up to $d_{\text{in}}(v)$ times.
- **Subsection IV-D: Algorithmic Complexity under Physical Valence Bounds.**  
  - *Assumption A2 (Bounded Physical Junction Valence):* $d_{\max} = \mathcal{O}(1)$.  
  - Analyze priority queue without `decrease-key`: max heap insertions bounded by $|E| \cdot d_{\max}^{\text{out}}$, stale successor iterations bounded by $|E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$.  
  - State Theorem 3: General bounds vs. spatial network bounds ($\mathcal{O}(|E|)$ memory, $\mathcal{O}(|E| \log |E|)$ time).
- **Subsection IV-E: Algorithmic Pseudo-code.**  
  - *Algorithm 1:* Formal pseudo-code box for `two_wheeler_astar`.

---

### Section V: Experimental Setup and Methodology (Page 4, Col 1)
- **Subsection V-A: Metropolitan Road Graph Environment.**  
  OpenStreetMap extraction of Bengaluru via OSMnx ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)): $|V| = 308,643$ nodes, $|E| = 744,216$ directed edges, maximum in/out degree $6$, mean degree $2.41$. Single-threaded Python 3.13 / NetworkX 3.4.2 environment on Windows 11 Enterprise.
- **Subsection V-B: 25-Corridor Metropolitan Benchmark Corpus.**  
  Corpus selection spanning radial arterials, ring-road connectors, inner-city grids, and peripheral links. Distance tiers: Short ($<4\text{ km}$), Medium ($4\text{--}10\text{ km}$), and Long ($>10\text{ km}$).
- **Subsection V-C: Controlled Factorial Ablation Matrix.**  
  - *Table II:* Experimental conditions:
    - Experiment A: $A_0$ (Turn-Aware, $P>0$) vs $A_1$ (Turn-Unaware, $P=0$) vs $A_2$ (Node-Level).
    - Experiment B: $B_0$ (Two-Wheeler) vs $B_1$ (Neutral) vs $B_2$ (Aggressive).
    - Experiment C: Sensitivity tiers $C_0 (0/0) \to C_1 (12/4) \to C_2 (25/8) \to C_3 (50/16)$.
    - Experiment D: $2 \times 2$ Bridge and Roundabout factorial ($D_1 \dots D_4$).
- **Subsection V-D: Statistical Inference Protocol.**  
  $R = 5$ repetitions per corridor and cell ($1,855$ total timing runs). Within-corridor median aggregation $\tilde{T}_i$. Non-parametric inferential testing: Pratt-adjusted Wilcoxon signed-rank test, Hodges-Lehmann median difference estimators, paired Cohen's $d_z$, and Holm-Bonferroni family-wise error control.

---

### Section VI: Experimental Results and Analysis (Page 4 Col 2 – Page 5 Full)
- **Subsection VI-A: Turn Awareness and State-Expansion Trade-offs (Exp A).**  
  - *Turn Elimination:* Reduction of $11.08$ sharp turns ($-34.1\%$, $21.44$ vs $32.52$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$, Hodges-Lehmann $-9.50$).
  - *Corpus-Bounded Route Equivalence:* When $P_{\text{turn}} = 0$, Condition A1 and Condition A2 produce identical vertex sequences, physical distances ($7.723\text{ km}$), and impedance costs across all $25 / 25$ corridors.
  - *Overhead Decomposition:* State expansion incurs $3.78\times$ median runtime overhead ($154.69\text{ ms}$ vs $40.88\text{ ms}$); turn penalty heading evaluation incurs $1.13\times$ overhead ($174.93\text{ ms}$ vs $154.69\text{ ms}$), total $4.28\times$.
  - *Figure 1:* Boxplots of sharp turns, runtime, and expanded states across A0, A1, A2 ($N=25$).
- **Subsection VI-B: Road-Class Impedance Channelization (Exp B).**  
  - Arterial exposure suppressed by $51.21$ percentage points ($13.84\%$ vs $65.05\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, $d_z = -1.7715$).
  - Residential routing increased by $+30.73\text{ pp}$ ($44.24\%$ vs $13.51\%$, $p_{\text{adj}} = 0.00015$, $d_z = +1.5234$).
  - Physical distance detour overhead: $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}} = 8.4 \times 10^{-5}$).
  - *Figure 2:* Bar chart of road-class percentage distributions across B0, B1, B2.
- **Subsection VI-C: Turn Penalty Sensitivity and Empirical Pareto Knee (Exp C).**  
  - Monotonic sharp-turn reduction across tiers: $32.52 \to 24.64 \to 21.44 \to 19.80$.
  - Formal Pareto analysis: $\{C_2, C_3\}$ form the non-dominated empirical frontier.
  - Baseline $C_2$ ($25/8$) identified as the **empirical corpus-average trade-off knee**, capturing $87.1\%$ of maneuver reduction while minimizing mean route distance ($7.648\text{ km}$).
  - *Figure 3:* Sensitivity curve and Pareto frontier plot.
- **Subsection VI-D: Grade-Separated Flyover Discounting (Exp D).**  
  - Arterial bridge traversal increases by $+148.9\%$ ($159.68\text{ m} \to 397.44\text{ m}$, $-111.6\text{ m}$ distance), localized to Hebbal (`OD_15`) and Whitefield (`OD_04`) flyovers.
  - Roundabout modifier operates cleanly with zero spurious deviations on non-roundabout corridors.
- **Subsection VI-E: Execution Runtime and Scalability.**  
  - Production baseline median runtime: $174.93\text{ ms}$ (IQR $439.08\text{ ms}$, mean $382.98\text{ ms} \pm 464.48\text{ ms}$, range $1.01\text{--}1,829.18\text{ ms}$).
  - Discussion of empirical right-skew across distance tiers.
  - *Table III:* Comprehensive paired statistical hypothesis results table.

---

### Section VII: Limitations, Discussion, and Conclusion (Page 6, Col 1)
- **Subsection VII-A: Construct Validity and Scope Limitations.**  
  Explicitly disclose measurement boundaries: results evaluate purely physical distance, discrete turn angles, road-class shares, bridge exposure, and CPU runtimes. No claims of real-world travel-time savings, safety improvements, or accident reductions are made.
- **Subsection VII-B: Algorithmic and Data Limitations.**  
  - Compound bridge-roundabout theoretical multiplier ($0.76$) on arbitrary OSM graphs.
  - Absence of addressable min-heap with `decrease-key`.
  - Single-threaded Python execution (noting that compiled C++/Rust implementations would yield sub-millisecond runtimes).
- **Subsection VII-C: Conclusion.**  
  Reiterate core contributions: state-expanded heading modeling, conditional admissibility and consistency proofs, multi-attribute two-wheeler impedance, and empirical Pareto trade-off knee.
- **Acknowledgment & Data Availability:** Note on frozen artifact reproducibility.

---

### References (Page 6, Col 1 Bottom – Col 2 Full)
- 15–16 audited, peer-reviewed citations formatted in standard IEEE style.

---

*Structural blueprint finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
