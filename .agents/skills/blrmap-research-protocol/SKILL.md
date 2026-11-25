---
name: blrmap-research-protocol
description: >-
  Enforce research scope, architectural boundaries, mathematical consistency, and IEEE authoring standards for the BLRMap project. Use this skill when planning, drafting, reviewing, or revising manuscripts, conference papers, or literature reviews for Paper 1 (Turn-Aware State-Expanded A* and Two-Wheeler Road Impedance) or Paper 2 (Perpendicular Offset Alternative Routing and Commute Network Validation).
---

# BLRMap Research Protocol & Manuscript Authoring Standards

This skill governs the scholarly scope, mathematical definitions, architectural separation, and writing standards for the `BLRMap_Prototype` research initiative. All manuscripts, conference submissions (e.g., IEEE ITSC, IEEE VTC, IEEE INDICON), and academic reports must adhere strictly to the protocols defined herein.

---

## 1. Project Research Scope & Demarcation

The research addresses the systemic failure of automobile-oriented navigation engines (such as OSRM and commercial map services) in dense, congested South Asian cities. In mixed traffic environments like Bengaluru, two-wheelers possess unique kinematic properties (filtering through narrow spaces, maintaining mobility when arterials saturate), yet navigate under severe vulnerability to hazardous right-angle turns across opposing traffic.

All contributions across publications must adhere to this strict taxonomy:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 RESEARCH SCOPE TAXONOMY                                 │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────┤
│ Core Contributions (Paper 1) │ Supporting (Paper 2)         │ Empirical Ground Truth    │
│ • State-expanded turn-aware  │ • Perpendicular offset       │ • Saturated corridor      │
│   A* routing (s = (u, v))    │   lateral waypoint routing   │   bypass case study       │
│ • Haversine admissibility    │ • Bounded detour (<= 1.20)   │   (Kumar et al. [16])     │
│   proof (h = 0.8 * dist)     │   and overlap (<= 0.70)      │ • 25-corridor empirical   │
│ • Inverted road-class        │   candidate pruning          │   ablation on Bengaluru   │
│   impedance modeling         │ • Topological diversity      │   OpenStreetMap network   │
│ • Arterial bridge discount   │   evaluation vs. Yen's KSP   │                           │
│   (replaces road penalty)    │                              │                           │
│ • Monotonic turn sensitivity │                              │                           │
│   and Pareto trade-off knee  │                              │                           │
├──────────────────────────────┴──────────────────────────────┴───────────────────────────┤
│ Prohibited Over-Claims & Future Work                                                    │
│ • NO proprietary real-time deep learning traffic prediction (Kumar et al. is baseline) │
│ • NO live IoT edge-sensor streaming integration (Abbas et al. [13] is future work)     │
│ • NO claims of in-search queue filtering or unmeasured travel-time / safety savings     │
│ • NO claims of roundabout routing improvements (empirically invariant across corpus)    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Two-Paper Architecture Separation

The research is decoupled into two independent, self-contained IEEE conference papers:

### Paper 1: Algorithmic Foundations & Impedance Modeling
- **Title Focus:** Turn-Aware State-Expanded A* Routing and Multi-Attribute Road Impedance for Two-Wheelers in Mixed Urban Traffic.
- **Primary Domain:** Graph Algorithms, Path Optimization, Transportation Informatics.
- **Core Scope:**
  1. Dual-state graph representation tracking `state = (prev_node, curr_node)` in the priority queue without constructing a full line graph ($\mathcal{O}(|E|)$ memory footprint).
  2. Spherical coordinate deflection angle calculation ($\Delta \theta$) and vehicle-differentiated discrete turn penalties ($P_{\text{turn}} \in \{0\text{ m}, 8\text{ m}, 25\text{ m}\}$).
  3. Mathematical proof of Haversine heuristic lower-bound admissibility ($h(u) = 0.8 \cdot d_{\text{haversine}}(u, t) \le c^*(u, t)$).
  4. Mode-specific edge impedance modeling with inverted peak-hour road hierarchy.
  5. Arterial bridge/flyover replacement logic ($0.8\times$ replaces arterial penalty).
  6. Turn penalty sensitivity analysis across parameter tiers ($C_0 \to C_1 \to C_2 \to C_3$); multi-objective Pareto trade-off between physical distance ($f_1$) and sharp turns ($f_2$); formal designation of Baseline $C_2(25/8)$ as the empirical corpus-average trade-off knee.
- **Evaluation Baseline:** Node-based Dijkstra/A*, distance-only routing, unweighted road hierarchies.

### Paper 2: Alternative Routing & Empirical Network Validation
- **Title Focus:** Perpendicular Offset Alternative Routing and Empirical Arterial Bypass Validation on Bengaluru's Street Network.
- **Primary Domain:** Urban Commuter Systems, Route Diversification, Empirical Network Analysis.
- **Core Scope:**
  1. Algorithmic failure analysis of Yen's $K$-Shortest Paths in dense planar street grids (path cloning, single-block loop deviations sharing $>90\%$ of edges).
  2. Perpendicular lateral offset waypoint generation geometry ($\pm 90^\circ$ at $150\text{ m}, 300\text{ m}$ at chord fractions $0.33, 0.50, 0.67$).
  3. Multi-criteria candidate pruning: bounded detour ($\epsilon \le 1.20$) and limited edge overlap ($\gamma \le 0.70$).
  4. Metropolitan corpus evaluation across 25 representative Bengaluru commute corridors (88.0% success rate; explicit topological analysis of pinch-point corridor exclusions `OD_04`, `OD_15`, `OD_23`).
  5. Comparative benchmark against Yen's KSP and Filtered Yen on the approved 5-corridor subset ($4.49\times$ mean speedup, $12.4\times$ on long corridor `OD_01`, $2.48\times$ higher diversity).
  6. Empirical bottleneck bypass case study on Kumar et al. (2025) [16] ground-truth saturated corridors (Hosur Road, MG Road / Trinity Circle).
- **Evaluation Baseline:** Yen's KSP, Filtered Yen, Single-criterion shortest paths.

---

## 3. Verified Algorithmic Terminology & Technical Definitions

When drafting algorithms, descriptions, and analyses, use only the verified definitions below:

### 3.1 State-Expanded Search State
- An A* search state is an edge traversal $s = (u, v)$ where $u$ is the preceding node and $v$ is the current node.
- Priority queue entries are keyed as `(f_score, counter, current_node, prev_node)`.
- The closed set tracks `(prev_node, curr_node)` pairs to allow multiple visits to a physical intersection via distinct approach trajectories.

### 3.2 Spherical Deflection & Discrete Turn Penalties
- For trajectory $u \to v \to w$, let bearing $\theta_1 = \text{bearing}(u, v)$ and $\theta_2 = \text{bearing}(v, w)$ computed via forward azimuth spherical trigonometry.
- Deflection angle: $\Delta \theta = |\theta_2 - \theta_1| \pmod{360^\circ}$; normalized to $[0^\circ, 180^\circ]$.
- Discrete penalty assignment:
  $$P_{\text{turn}}(\Delta \theta) = \begin{cases} 25.0\text{ m} & \text{if } \Delta \theta \ge 60.0^\circ \quad (\text{Sharp / Opposing Maneuver}) \\ 8.0\text{ m} & \text{if } 30.0^\circ \le \Delta \theta < 60.0^\circ \quad (\text{Moderate Deflection}) \\ 0.0\text{ m} & \text{if } \Delta \theta < 30.0^\circ \quad (\text{Straight / Slight Deflection}) \end{cases}$$

### 3.3 Road Impedance Model
- Base edge impedance: $c_{\text{base}}(e) = \text{length}(e) \cdot p_{\text{base}}(\text{highway})$
- Inverted peak-hour road penalty hierarchy:
  - `motorway`: $4.00$
  - `trunk` / `trunk_link`: $3.00$
  - `primary` / `primary_link`: $2.20$
  - `secondary` / `secondary_link`: $1.50$
  - `tertiary` / `tertiary_link`: $1.20$
  - `residential`: $1.00$ (Neutral baseline)
  - `living_street`: $1.00$
  - `service` / `unclassified`: $0.90$ (Permitted narrow shortcut)

### 3.4 Bridge / Flyover Modifier (CRITICAL SPECIFICATION)
- **Implementation Reality:** The bridge modifier **replaces** the road-class penalty rather than multiplying it.
- **Exact Code Logic:**
  ```python
  if is_bridge and hw in MAIN_ROAD_TYPES:
      penalty = 0.8
  ```
- **Scholarly Description:** On grade-separated arterial structures (`bridge=yes` on primary, trunk, or motorway links), the elevated roadway is immune to ground-level intersection conflicts and roadside friction. The engine replaces the high arterial penalty ($2.2\text{--}4.0$) with an encouraging multiplier of $0.80$, effectively granting elevated flyovers priority over parallel surface streets.
- **Do Not Write:** Do not state that the bridge modifier multiplies the edge penalty ($c \cdot p \cdot 0.8$). It directly overrides the road-class penalty with $0.80$.

### 3.5 Roundabout Modifier (CRITICAL SPECIFICATION)
- **Implementation Reality:** Roundabout edges receive a $0.95$ multiplier: `penalty *= 0.95`.
- **Empirical Reality:** In Experiment D ($N=25$), toggling the roundabout modifier produced **zero route-geometry differences** across all 25 corridors ($25/25$ zero diffs, $p_{\text{adj}} = 1.0$). Only one corpus corridor (`OD_12`) traversed a roundabout ($62.98\text{ m}$).
- **Scholarly Description:** Document the roundabout modifier as a localized continuous-flow incentive that operates cleanly with demonstrated topological stability and zero spurious route alterations across the wider metropolitan network.
- **Prohibited Claim:** Do NOT claim a demonstrated network routing improvement from roundabouts.

### 3.6 Signal-Based ETA Calibration (CRITICAL SPECIFICATION)
- **Implementation Reality:** Standalone code stubs exist in `backend/routing/algorithms.py` (`count_filterable_junctions` and `apply_filtering_discount`), but they are completely uninvoked in production, uncalibrated against real-world travel time observations, and entirely unmeasured in the frozen Phase 13 ablation experiments.
- **Measurement Boundary:** Phase 13.4 explicitly restricted construct validity to physical distance, turn counts, road-class shares, Jaccard diversity, and CPU execution time. Travel-time savings and real-world ETAs were **not measured**.
- **Research Protocol Action:** **EXCLUDE** the signal-based ETA discount formula ($T_{\text{base}} \cdot 0.985^{N}$) and any claims of quantified travel-time reduction from both papers. If mentioned at all, discuss only as theoretical prior work (Promraksa et al. [1]) in Related Work, or as uncalibrated future work.

---

## 4. Mathematical Formulations & Assumptions

### 4.1 Graph Representation
Let directed graph $G = (V, E, \ell, \tau)$ represent the urban street network:
- $V$: Intersections and geometry shape points with coordinates $(\text{lat}_v, \text{lon}_v)$.
- $E \subseteq V \times V$: Directed roadway segments.
- $\ell: E \to \mathbb{R}^+$: Physical segment length in meters.
- $\tau: E \to \mathcal{T}$: OpenStreetMap roadway classifications.

### 4.2 Haversine Admissibility Guarantee
To guarantee that A* returns an optimal path with respect to the cost function without requiring re-openings, the heuristic function $h(u, t)$ must never overestimate the minimal cost from node $u$ to destination $t$:
$$h(u, t) \le c^*(u, t) \quad \forall u \in V$$
Because edge impedance incorporates modifiers with a minimum possible multiplier of $\mu_{\min} = 0.80$ (from the arterial bridge discount), the Euclidean/Haversine physical distance $d_{\text{haversine}}(u, t)$ must be scaled by this floor:
$$h(u, t) = 0.80 \cdot d_{\text{haversine}}(u, t)$$
**Proof Summary:** For any path $P = \langle e_1, e_2, \dots, e_k \rangle$ from $u$ to $t$:
$$c(P) = \sum_{i=1}^k \left( \ell(e_i) \cdot \mu(e_i) + P_{\text{turn}, i} \right) \ge \sum_{i=1}^k \ell(e_i) \cdot \mu_{\min} \ge 0.80 \sum_{i=1}^k \ell(e_i) \ge 0.80 \cdot d_{\text{haversine}}(u, t) = h(u, t)$$
Since $P_{\text{turn}} \ge 0$ everywhere, $h(u, t)$ is strictly admissible and consistent.

### 4.3 Multi-Objective Pareto Formulation (Turn Sensitivity)
In Experiment C, the path selection problem is evaluated as a bi-objective minimization:
$$\min_{\mathbf{x}} \; \left( f_1(\mathbf{x}), f_2(\mathbf{x}) \right)$$
where $f_1(\mathbf{x}) = \text{Physical Route Distance [km]}$ and $f_2(\mathbf{x}) = \text{Sharp Turn Maneuvers [count]} \; (\ge 60^\circ)$.
- Monotonic Turn Reduction across Corpus Means:
  - $C_0(0/0)$: $f_1 = 7.723\text{ km}$, $f_2 = 32.52\text{ turns}$
  - $C_1(12/4)$: $f_1 = 7.668\text{ km}$, $f_2 = 24.64\text{ turns}$
  - $C_2(25/8)$: $f_1 = 7.648\text{ km}$, $f_2 = 21.44\text{ turns}$
  - $C_3(50/16)$: $f_1 = 7.680\text{ km}$, $f_2 = 19.80\text{ turns}$
- Formal Dominance Relations:
  - $C_2 \succ C_0$ and $C_2 \succ C_1$ (strictly dominates on both objectives).
  - Non-dominated Pareto frontier: $\mathcal{P} = \{C_2, C_3\}$.
  - $C_2(25/8)$ represents the **empirical corpus-average trade-off knee**, achieving 87.1% of the maximum turn reduction while minimizing physical travel distance.

---

## 5. Literature Governance & Citation Integrity

### 5.1 Master Bibliography Preservation
The 16 references compiled in [`master_bibliography.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/master_bibliography.bib) represent the audited, DOI-verified foundation of the project:
- *Pillar 1 (Two-Wheeler Dynamics):* Promraksa et al. [1], Kotagi et al. [2], Das & Maurya [3], Fadilah et al. [4], Asvial et al. [5].
- *Pillar 2 (Turn-Aware Routing):* Winter [6], Geisberger & Vetter [7].
- *Pillar 3 (Customizable Cost & Diversity):* Delling et al. [8], Abraham et al. [9], Bast et al. [10].
- *Pillar 4 (Clustering & Congestion):* Lee et al. [11], Du et al. [12], Abbas et al. [13].
- *Pillar 5 (OSM & Urban Baselines):* Boeing [14], Luxen & Vetter [15], Kumar et al. [16].

### 5.2 Rules for Introducing New Literature
Future literature research is permitted and encouraged under these strict conditions:
1. Every new reference must be independently verified for bibliographic completeness: Authors, Title, Journal/Conference, Volume, Number, Pages, Year, and DOI.
2. Disqualified papers (such as Mojaveri & Faragó 2021, which addressed computer network packet routing) must never be re-introduced.
3. Every citation must directly support an architectural, algorithmic, or empirical assertion.

---

## 6. IEEE Manuscript Writing Standards

All draft sections must adhere to IEEE style guidelines and sound like authoritative human scholarship:

1. **De-AI Writing Enforcement:** Apply `humanizer` rules to eliminate robotic mannerisms:
   - No staged openers ("Let's dive into...", "Here's what you need to know").
   - No dramatic one-line closers ("That distinction matters.", "That is the real win.").
   - No forced triads ("fast, reliable, and scalable").
   - No decorative bolding on list items or headings.
   - No inflated rhetoric ("stands as an enduring testament", "groundbreaking milestone").
   - Replace em dashes (—) and en dashes (–) with commas, colons, or clean sentence structures.
2. **Transparent Sample Size Disclosures:**
   - Any discussion of Experiment E must explicitly disclose: $N=25$ corridors for Perpendicular Offset (E1); $N=5$ corridors for Yen's KSP (E2) and Filtered Yen (E3).
   - Figure 4 axis labels must state: `E1 (N=25)`, `E2 (N=5)`, `E3 (N=5)`.
3. **Objective Tone & Delimitations:**
   - Clearly state that evaluation is conducted on OpenStreetMap graph models of Bengaluru.
   - Acknowledge that turn deflection angles are derived from roadway geometry vectors and do not capture dynamic physical obstructions or active police diversions.

---

## 7. Prohibited Claims & Boundary Guardrails

The following claims are strictly prohibited in all project manuscripts:
- **PROHIBITED:** Claiming a proprietary deep learning traffic prediction model. (Kumar et al. [16] is the published baseline).
- **PROHIBITED:** Claiming real-time streaming analytics or IoT sensor infrastructure. (Abbas et al. [13] is cited as future work).
- **PROHIBITED:** Claiming demonstrated real-world travel-time savings, fuel efficiency gains, accident reductions, or safety enhancements.
- **PROHIBITED:** Claiming the roundabout modifier improved routing on the evaluated corpus (it was empirically invariant across all 25 corridors).
- **PROHIBITED:** Claiming that signal-based queue filtering ETA discount was empirically calibrated or verified.
- **PROHIBITED:** Stating that the bridge modifier multiplies edge penalty (it replaces main road penalty with 0.8).
