# Paper 1 Final Authoritative Blueprint (v1.0 Frozen)

**Document:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Length:** Exactly 6.0 Pages Compiled Constraint (including figures, tables, and references)  
**Parent Blueprint:** [`paper1_structural_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_structural_blueprint.md), [`paper1_revised_six_page_budget.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_revised_six_page_budget.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **FROZEN & AUTHORITATIVE BLUEPRINT**

---

## 1. Executive Protocol and Measurement Boundary

In strict compliance with [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md) and [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), this document freezes the structural architecture of Paper 1. 

> [!IMPORTANT]
> **Construct Validity & Measurement Demarcation:**  
> The research evaluates purely measurable topological, physical, and computational quantities:
> - Physical route distance in meters ($m$).
> - Discrete vehicular turn deflections (sharp turns $\ge 60^\circ$, moderate turns $30^\circ\text{--}60^\circ$).
> - Road-class exposure percentages ($\%$ of route distance on primary, secondary, residential, service).
> - Elevated bridge traversal length in meters ($m$).
> - Single-threaded CPU execution runtime in milliseconds ($ms$).  
> **Strict Negative Constraint:** No collision, accident, trauma registry, police report, or hospital injury data was collected or analyzed. The paper will make **zero claims regarding safety improvements, accident rate reductions, collision risk mitigation, or real-world dynamic travel-time savings**.

---

## 2. Frozen Section-by-Section Structural Specification

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PAPER 1 FROZEN TOPOLOGICAL ARCHITECTURE                         │
├────────────────────┬────────────────────┬────────────────────┬─────────────────────────┤
│ PAGE 1             │ PAGE 2             │ PAGE 3             │ PAGE 4                  │
│ • Title & Abstract │ • II. Related Work │ • IV. Turn-Aware   │ • V. Experimental Setup │
│ • Index Terms      │   (Demarcation)    │   Search Algorithm │   (Graph, Corpus, &     │
│ • I. Introduction  │ • Table I: Road    │ • Theorems 1 & 2   │   Ablation Protocol)    │
│   (Context, Gap,   │   Impedance Map    │   (Proofs)         │ • VI. Results: Exp A    │
│   Contributions)   │ • III. Problem     │ • Corollary 1 &    │ • Fig. 1: Exp A Trade-  │
│ • II. Related Work │   Formulation &    │   Theorem 3        │   offs (Boxplots)       │
│   (Turn Costs &    │   Mathematical     │   (Complexity)     │                         │
│   Two-Wheelers)    │   Model            │                    │                         │
├────────────────────┴────────────────────┴────────────────────┴─────────────────────────┤
│ PAGE 5                                  │ PAGE 6                                       │
│ • VI. Results: Exp B (Road Classes)     │ • VII. Limitations & Construct Validity      │
│ • Fig. 2: Exp B Distribution (Bar Chart)│ • VII. Conclusion & Future Work              │
│ • VI. Results: Exp C (Turn Sensitivity) │ • Acknowledgment & Reproducibility Note      │
│ • Fig. 3: Exp C Pareto Knee Curve       │ • References (16 Audited IEEE Citations)     │
│ • VI. Results: Exp D (Bridge Discount)  │   (Flows from Page 6 Col 1 bottom into Col 2)│
│ • Table II: Paired Hypothesis Results   │                                              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Front Matter (Page 1, Top Span)
- **Title:** *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*
- **Authors & Affiliations:** Author names, Department of Computer Science & Engineering, Bengaluru, India.
- **Abstract (200 words, frozen target):**
  - *Context:* Powered two-wheelers represent over $70\%$ of vehicular volume in South Asian megacities, operating under mixed-traffic conditions with significant vehicular speed and size heterogeneity.
  - *Problem:* Conventional shortest-path navigation engines operate on dimensionless node graphs, ignoring vehicular heading changes and funneling motorcycles onto congested main roads.
  - *Method:* We present a turn-aware, state-expanded $A^*$ routing framework integrated with two-wheeler-specific road impedance modeling and elevated flyover channelization. The algorithm operates over directed edge states $s=(u, v)$, applying discrete angular heading penalties during search, guided by an admissible and monotonically consistent scaled Haversine heuristic ($h = 0.80 \cdot D_{\text{haversine}}$).
  - *Empirical Findings:* Evaluated across a 25-corridor metropolitan corpus on Bengaluru's 744,216-edge road network ($R=5$ repetitions per corridor), our engine eliminates $34.1\%$ of sharp maneuvers ($\ge 60^\circ$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$) and suppresses arterial road exposure by $51.21$ percentage points ($p_{\text{adj}} = 8.4 \times 10^{-5}$, $d_z = -1.7715$) at a median runtime of $174.93\text{ ms}$.
- **Index Terms:** Shortest path algorithms, state-expanded search, turn penalties, two-wheeler routing, road network impedance, urban mobility.

---

### Section I: Introduction (Page 1, Col 1 Bottom – Col 2 Top; 450 words)
- **Paragraph 1: Urban Mixed-Traffic Context (Literature-Grounded):**  
  Establish the operating environment of powered two-wheelers in South Asian cities (Bengaluru). Two-wheelers exhibit high agility and permeability through narrow corridors, but navigate in heterogeneous mixed traffic characterized by severe vehicular speed differentials and frequent un-signalized intersection crossings ([1], [2]).
- **Paragraph 2: Architectural Limitations of Automobile-Oriented Routing:**  
  Examine standard vertex-space shortest-path frameworks (e.g., standard Dijkstra and hierarchical speedup models calibrated for four-wheeled automobiles [4]). Because they model intersections as dimensionless scalar points, they cannot evaluate angular heading changes during search. In urban street networks, distance-optimal routing generates two distinct operational anomalies: (i) erratic zig-zag alleyway shortcuts with excessive turn maneuvers across conflicting traffic streams, or (ii) default channelization onto high-speed, saturated multi-lane arterials ([1], [3]). In our controlled baseline (Condition A2: standard vertex-space $A^*$), distance minimization generates an average of $32.52$ sharp turns per corridor.
- **Paragraph 3: The Research Gap:**  
  Existing turn-aware routing literature focuses either on static contraction hierarchies that lack dynamic metric flexibility, or on post-hoc multi-criteria ranking applied to pre-computed routes ([11]). A unified, exact, and computationally lightweight turn-aware routing framework tailored to two-wheeler road impedance on raw metropolitan networks is missing.
- **Paragraph 4: Itemized Contributions:**  
  1. *State-Expanded Turn-Aware Search:* Online $A^*$ search over directed edge states $s = (u, v)$ evaluating discrete angular heading penalties directly within edge relaxation.
  2. *Theoretical Admissibility & Consistency Guarantees:* Deductive proofs that the scaled Haversine heuristic ($h = 0.80 \cdot D_{\text{haversine}}$) is strictly admissible and monotonically consistent under explicit Assumption A1 ($\mu(e) \ge 0.80$), guaranteeing state finality without reopening.
  3. *Vehicle-Specific Road Impedance Model:* An empirical impedance function coupling inverted arterial penalties with grade-separated flyover overrides ($0.80\times$).
  4. *Metropolitan Empirical Ablation:* Controlled $N=25$ corridor ablation on Bengaluru's 744,216-edge network demonstrating $34.1\%$ sharp-turn reduction, $51.21\text{ pp}$ arterial exposure drop, and identifying the empirical Pareto trade-off knee ($C_2: 25/8$).

---

### Section II: Related Work (Page 1, Col 2 Bottom – Page 2, Col 1 Top; 340 words)
- **Subsection II-A: Turn Costs and Line-Graph State Expansion:**  
  Review line-graph state expansion and turn prohibitions (Kirby [5]; Winter [6]). Review speedup techniques (Geisberger & Vetter [7]; Delling et al. [8]; Bast et al. [9]), highlighting that static shortcut pre-computation limits metric customization for vehicle-specific road suitability.
- **Subsection II-B: Two-Wheeler Route Choice & Urban Impedance:**  
  Review motorcycle travel behavior and lane-filtering (Promraksa & Satiennam [1]; Kotagi et al. [2]; Das et al. [3]; Fadilah et al. [10]). Analyze multi-criteria routing attempts (Asvial et al. [11]; Zografos & Androutsopoulos [12]), highlighting the critical gap: treating turns post-hoc rather than within the search graph.
- **Subsection II-C: Heuristic Search and Scholarly Demarcation:**  
  Review heuristic foundations (Hart et al. [13]; Goldberg & Harrelson [14]; Boeing [15]). Demarcate our work: direct state-space expansion with a closed-form scaled spherical lower-bound heuristic evaluated on an un-contracted metropolitan network.

---

### Section III: Problem Formulation and Mathematical Model (Page 2, Col 1 Bottom – Col 2 Full; 470 words)
- **Subsection III-A: Metropolitan Road Network Graph:**  
  Directed multigraph $G = (V, E)$ with physical segment lengths $\ell(e) > 0$.
- **Subsection III-B: Two-Wheeler Impedance Function:**  
  $$\mu(e) = f_{\text{class}}(\text{hw}_e) \cdot m_{\text{bridge}}(e) \cdot m_{\text{rbt}}(e) \cdot m_{\text{surf}}(e) \tag{1}$$
  - *Table I:* Road-class penalties ($0.90\text{--}4.0$), flyover override ($0.80$), roundabout factor ($0.95$), and default fallbacks.
  - Detail flyover override: replaces base penalty with $0.80$ to channel routes onto grade-separated corridors.
- **Subsection III-C: Discrete Angular Turn Penalty Function:**  
  $$P_{\text{turn}}(u, v, w) = \begin{cases} 25.0 & \text{if } \Delta\theta \ge 60^\circ \\ 8.0 & \text{if } 30^\circ \le \Delta\theta < 60^\circ \\ 0.0 & \text{if } \Delta\theta < 30^\circ \text{ or } u = \text{None} \end{cases} \tag{2}$$
  - *Lemma 1 (Initial Departure Invariance):* $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$.
- **Subsection III-D: State Space and Transition Cost:**  
  State space $S = E \cup \{(\text{None}, s_0)\}$. State transition cost:
  $$c(s, s') = \ell(v, w) \cdot \mu(v, w) + P_{\text{turn}}(u, v, w) \tag{3}$$
  Note: $c(s, s') > 0$ strictly holds for all valid transitions.

---

### Section IV: Proposed Turn-Aware Routing Algorithm (Page 3 Full; 480 words)
- **Subsection IV-A: State-Expanded Search Architecture:**  
  State cardinality $|S| = |E| + 1$ and transition cardinality $|E_S| = d_{\text{out}}(s_0) + \sum_v d_{\text{in}}(v) d_{\text{out}}(v)$.
- **Subsection IV-B: Scaled Haversine Heuristic:**  
  $$h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t), \quad \mu_{\min} = 0.80 \tag{4}$$
- **Subsection IV-C: Formal Theoretical Proofs:**  
  - *Assumption A1 (Graph Multiplier Lower Bound):* $\forall e \in E, \mu(e) \ge 0.80$.  
  - *Theorem 1 (Conditional Admissibility):* Proof using spherical triangle inequality and $\mu_{\min}$ scaling ($h(s) \le c^*(s)$).  
  - *Theorem 2 (Conditional Monotonic Consistency):* Proof showing:
    $$h(s) \le c(s, s') + h(s') \tag{5}$$
  - *Corollary 1 (Optimal State Finality):* Monotonic consistency guarantees that each state $(u, v)$ is finalized on its first extraction from `open_set` without reopening. Physical vertices $v$ are expanded up to $d_{\text{in}}(v)$ times.
- **Subsection IV-D: Algorithmic Complexity under Physical Valence Bounds:**  
  - *Assumption A2 (Bounded Physical Junction Valence):* $d_{\max} \le c = \mathcal{O}(1)$.  
  - Binary min-heap without `decrease-key`: max heap insertions bounded by $|E| \cdot d_{\max}^{\text{out}}$, stale successor iterations bounded by $|E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$.  
  - *Theorem 3 (Complexity Bounds):*
    $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E| \cdot d_{\max}^{\text{out}}), \quad \mathcal{T}_{\text{general}} = \mathcal{O}\left( |E| \cdot d_{\max}^{\text{out}} \log(|E| \cdot d_{\max}^{\text{out}}) + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right) \tag{6}$$
    Under Assumption A2, bounds simplify to strictly $\mathcal{O}(|E|)$ memory and $\mathcal{O}(|E| \log |E|)$ time.
- **Mathematical Search Specification:** Detailed text-and-equation formulation replacing textbook pseudo-code.

---

### Section V: Experimental Setup and Methodology (Page 4, Col 1; 280 words)
- **Subsection V-A: Metropolitan Road Graph Environment:**  
  Bengaluru graph ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)): $|V| = 308,643$ nodes, $|E| = 744,216$ directed edges, maximum degree $6$, mean degree $2.41$, transition count $|E_S| = 2,103,894$ ($2.83\cdot |E|$). Single-threaded Python 3.13 / NetworkX 3.4.2 on Windows 11 Enterprise.
- **Subsection V-B: 25-Corridor Metropolitan Benchmark Corpus:**  
  Geographically distributed OD pairs spanning short ($<4\text{ km}$), medium ($4\text{--}10\text{ km}$), and long cross-city ($>10\text{ km}$) corridors.
- **Subsection V-C: Controlled Factorial Ablation Matrix (Text Integration):**  
  Concise definition of the 4 experimental families:
  - *Exp A:* Turn awareness ($A_0$ turn-aware vs $A_1$ turn-unaware state-expanded vs $A_2$ node-level).
  - *Exp B:* Road impedance ($B_0$ two-wheeler vs $B_1$ neutral $1.0\times$ vs $B_2$ aggressive arterial).
  - *Exp C:* Sensitivity tiers ($C_0: 0/0 \to C_1: 12/4 \to C_2: 25/8 \to C_3: 50/16$).
  - *Exp D:* Grade-separated factorial ($D_1$ off/off $\to D_4$ on/on).
- **Subsection V-D: Statistical Inference Protocol:**  
  $R = 5$ repetitions per corridor and cell ($1,855$ total runs). Within-corridor median aggregation $\tilde{T}_i$. Non-parametric inferential protocol: Pratt-adjusted Wilcoxon signed-rank tests, Hodges-Lehmann median estimators, paired Cohen's $d_z$, and Holm-Bonferroni correction.

---

### Section VI: Experimental Results and Analysis (Page 4 Col 2 – Page 5 Full; 600 words)
- **Subsection VI-A: Turn Awareness and State-Expansion Trade-offs (Exp A):**  
  - Eliminates $11.08$ sharp turns ($-34.1\%$, $21.44$ vs $32.52$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$, Hodges-Lehmann $-9.50$).
  - *Corpus-Bounded Route Equivalence:* When $P_{\text{turn}} = 0$, Condition A1 and Condition A2 produce identical node sequences, physical distances ($7.723\text{ km}$), and impedance costs across all $25 / 25$ corridors.
  - *Runtime Overhead Breakdown:* State expansion incurs $3.78\times$ median runtime overhead ($154.69\text{ ms}$ vs $40.88\text{ ms}$); turn penalty heading evaluation incurs $1.13\times$ overhead ($174.93\text{ ms}$ vs $154.69\text{ ms}$), total $4.28\times$.
  - *Figure 1:* Boxplots of sharp turns, runtime, and expanded states across A0, A1, A2 ($N=25$).
- **Subsection VI-B: Road-Class Impedance Channelization (Exp B):**  
  - Arterial exposure suppressed by $51.21$ percentage points ($13.84\%$ vs $65.05\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, $d_z = -1.7715$).
  - Residential routing increased by $+30.73\text{ pp}$ ($44.24\%$ vs $13.51\%$, $p_{\text{adj}} = 0.00015$, $d_z = +1.5234$).
  - Detour overhead: $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}} = 8.4 \times 10^{-5}$).
  - *Figure 2:* Bar chart of road-class exposure distributions across B0, B1, B2.
- **Subsection VI-C: Turn Penalty Sensitivity and Empirical Pareto Knee (Exp C):**  
  - Monotonic turn reduction across tiers: $32.52 \to 24.64 \to 21.44 \to 19.80$.
  - Pareto frontier $\{C_2, C_3\}$; Baseline $C_2$ ($25/8$) represents the **empirical corpus-average trade-off knee**, capturing $87.1\%$ of turn reduction while minimizing mean route distance ($7.648\text{ km}$).
  - *Figure 3:* Sensitivity curve and Pareto frontier plot.
- **Subsection VI-D: Grade-Separated Flyover Traversal (Exp D):**  
  - Arterial bridge traversal increases by $+148.9\%$ ($159.68\text{ m} \to 397.44\text{ m}$, $-111.6\text{ m}$ distance), localized to Hebbal (`OD_15`) and Whitefield (`OD_04`) flyovers. Roundabout modifier operates with zero spurious deviations.
- **Subsection VI-E: Execution Runtime and Scalability:**  
  - Production baseline median runtime: $174.93\text{ ms}$ (IQR $439.08\text{ ms}$, mean $382.98\text{ ms} \pm 464.48\text{ ms}$, range $1.01\text{--}1,829.18\text{ ms}$).
  - Discussion of empirical right-skew across distance tiers.
  - *Table II (Statistical Results):* Complete Wilcoxon Pratt, Holm $p_{\text{adj}}$, Cohen's $d_z$, and Hodges-Lehmann summary table.

---

### Section VII: Limitations, Discussion, and Conclusion (Page 6, Col 1; 510 words)
- **Subsection VII-A: Construct Validity and Scope Limitations:**  
  Explicitly state that results evaluate physical distance, discrete turn counts, road-class shares, bridge exposure, and CPU runtimes. No safety or dynamic travel-time claims are made.
- **Subsection VII-B: Algorithmic and Generalizability Limitations:**  
  - Sequential bridge-roundabout modifier theoretical floor ($0.76$) on arbitrary graphs.
  - Dependence of linear memory on bounded physical intersection valence ($d_{\max} \le 6$).
  - Empirical evaluation confined to Bengaluru metropolitan network.
  - Single-threaded Python interpretation (noting compiled backends would yield sub-millisecond execution).
- **Subsection VII-C: Conclusion:**  
  Reiterate core contributions: state-expanded heading modeling, conditional admissibility and consistency proofs, multi-attribute two-wheeler impedance, and empirical Pareto trade-off knee.
- **Acknowledgment & Data Availability:** Note on frozen artifact reproducibility.

---

### References (Page 6, Col 1 Bottom – Col 2 Full; ~350 words equivalent)
- Exactly 16 audited, peer-reviewed citations formatted in standard IEEE style.

---

*Blueprint v1.0 frozen under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
