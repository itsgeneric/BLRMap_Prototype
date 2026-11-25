# Section III Structural Outline — Problem Formulation and Configured Road Impedance (v1.1)

**Document:** [`paper1_section_III_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_outline_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Two-Column `IEEEtran`)  
**Phase:** Phase 7.1-R — Multiplier Lower-Bound and Objective-Function Audit  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE SECTION III STRUCTURAL OUTLINE (PLANNING ONLY — NO PROSE DRAFTED)**

---

## 1. Section Architecture and Space Allocation

Section III defines the formal mathematical problem formulation, state representation, turn penalty mechanics, and two-wheeler road-class impedance modeling. It establishes the rigorous theoretical foundation required for the proposed turn-aware routing algorithm in Section IV.

- **Allocated Manuscript Space:** Page 2, Column 1 Bottom through Column 2 Full.
- **Target Body Text Word Count:** **470 words** (Strict range: $450\text{--}490\text{ words}$).
- **Display Equations:** Exactly 3 display equations (Eq. 1: Road Impedance Multiplier, Eq. 2: Discrete Turn Penalty, Eq. 3: State Transition Cost & Route Objective).
- **Float Assets:** Exactly 1 table (**Table I: Configured Road-Class Impedance Multipliers and Topological Modifiers**, $\approx 1.6\text{ in}$ vertical height, 6 rows).
- **Prose Drafting Status:** Strictly zero manuscript prose drafted; planning and structural blueprinting only.

---

## 2. Subsection Breakdown and Content Allocation

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           SECTION III: DETAILED CONTENT & WORD ALLOCATION                        │
├───────┬───────────────────────────────────────────┬──────────────┬───────────────┬───────────────┤
│ Sub#  │ Subsection Heading                        │ Word Budget  │ Assets / Eqns │ Column Layout │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ III-A │ Directed Road-Network Graph and Origin–   │ ~110 words   │ None          │ Page 2,       │
│       │ Destination Routing Problem               │              │               │ Col 1 Bottom  │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ III-B │ Directed Edge-State Representation        │ ~100 words   │ None          │ Page 2,       │
│       │                                           │              │               │ Col 2 Top     │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ III-C │ Angular Turn Deflection and Discrete      │ ~110 words   │ Eq. (2),      │ Page 2,       │
│       │ Maneuver Penalty Model                    │              │ Lemma 1       │ Col 2 Mid     │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ III-D │ Configured Road-Class Impedance and       │ ~150 words   │ Eq. (1),      │ Page 2,       │
│       │ Flyover Channelization                    │              │ Eq. (3),      │ Col 2 Bot &   │
│       │                                           │              │ Table I       │ Table Float   │
├───────┴───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ TOTAL SECTION III BUDGET                          │ 470 words    │ 3 Equations,  │ ~1.2 Columns  │
│                                                   │              │ 1 Table       │               │
└───────────────────────────────────────────────────┴──────────────┴───────────────┴───────────────┘
```

---

## 3. Subsection Planning Specifications

### Subsection III-A: Directed Road-Network Graph and Origin–Destination Routing Problem
- **Target Word Budget:** $\approx 110\text{ words}$.
- **Structural Purpose:** Establish the formal graph-theoretic base model and demarcate physical spatial distance from accumulated impedance cost.
- **Key Technical Elements to Cover:**
  1. Define the directed road-network graph $G = (V, E)$, where $V$ represents physical street intersections and roadway shape points, and $E \subseteq V \times V$ represents directed road segments.
  2. Define physical segment length $\ell(e) > 0$ in surveyed meters ($m$) and roadway attributes: functional highway classification $h(e) \in \mathcal{H}$, grade-separation attribute $\text{bridge}(e)$, and junction attribute $\text{junction}(e)$.
  3. Define the point-to-point origin–destination problem: given trip origin $s_0 \in V$ and destination $t \in V$, discover a connected directed path $P = \langle e_1, e_2, \dots, e_k \rangle$ connecting $s_0$ to $t$.
  4. Formally distinguish physical route distance $D(P) = \sum_{i=1}^k \ell(e_i)$ (measured strictly in physical meters, $m$) from the accumulated multi-attribute impedance cost $C(P)$ (measured strictly in effective impedance meters, $m$).
  5. Boundary guardrail: Explicitly clarify that $C(P)$ minimizes an effective traversal impedance objective incorporating turning penalties and road suitability, and does NOT represent measured physical travel time, queue delay, or fuel consumption.

### Subsection III-B: Directed Edge-State Representation
- **Target Word Budget:** $\approx 100\text{ words}$.
- **Structural Purpose:** Define the state-expanded search space tracking arriving predecessor segments to overcome non-Markovian turn costs.
- **Key Technical Elements to Cover:**
  1. Formulate the non-Markovian property: intersection turn penalties depend on the approach trajectory (predecessor segment $(u, v)$), violating the optimal substructure principle on standard vertex space $V$.
  2. Define the directed edge state $s = (u, v) \in E$, representing a vehicle actively positioned at vertex $v$ having arrived via directed roadway segment $(u, v)$.
  3. Define the synthetic initial start state $s_0^{\text{state}} = (\text{None}, s_0)$, representing departure from origin intersection $s_0$ prior to selecting an initial outgoing edge.
  4. Establish the exact state-space cardinality $|S| = |E| + 1$.
  5. Define valid state transitions: a directed transition from state $s = (u, v)$ to state $s' = (v', w)$ exists if and only if $v' = v$ and $(v, w) \in E$.
  6. Demarcation: State space and transition topology are defined here; the priority queue search algorithm, heap operations, and pruning mechanics are strictly deferred to Section IV.

### Subsection III-C: Angular Turn Deflection and Discrete Maneuver Penalty Model
- **Target Word Budget:** $\approx 110\text{ words}$.
- **Structural Purpose:** Define the geometric forward-azimuth deflection angle calculation and discrete penalty assignment.
- **Key Technical Elements to Cover:**
  1. Define incoming directed segment $e_{\text{in}} = (u, v)$ and outgoing directed segment $e_{\text{out}} = (v, w)$ at intersection $v \in V$.
  2. Formulate spherical forward azimuth bearings $\theta(u, v)$ and $\theta(v, w)$ using great-circle forward azimuth spherical trigonometry from node geographic coordinates $(\text{lat}, \text{lon})$.
  3. Formulate absolute angular deflection:
     $$\Delta\theta(u, v, w) = \min\left(|\theta(u, v) - \theta(v, w)|, \; 360^\circ - |\theta(u, v) - \theta(v, w)|\right) \in [0^\circ, 180^\circ]$$
  4. Define the discrete piecewise turn penalty function $P_{\text{turn}}(u, v, w)$ (Display Equation 2):
     $$P_{\text{turn}}(u, v, w) = \begin{cases} 25.0 & \text{if } u \ne \text{None} \text{ and } \Delta\theta(u, v, w) \ge 60.0^\circ \quad (\text{Sharp Turn / Opposing Maneuver}) \\ 8.0 & \text{if } u \ne \text{None} \text{ and } 30.0^\circ \le \Delta\theta(u, v, w) < 60.0^\circ \quad (\text{Moderate Deflection}) \\ 0.0 & \text{if } u = \text{None} \text{ or } \Delta\theta(u, v, w) < 30.0^\circ \quad (\text{Straight / Initial Departure}) \end{cases}$$
  5. State Lemma 1 (Initial Departure Invariance): $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$ for all outgoing initial transitions $(s_0, w) \in E$.
  6. Note units: Constants $25.0$ and $8.0$ are expressed in effective-distance meters ($m$).
  7. Boundary guardrail: Turn penalties are discrete cost penalties penalizing high-deflection maneuvers; they are strictly geometric conflict penalties and must NOT be described as safety ratings or validated accident reduction models.

### Subsection III-D: Configured Road-Class Impedance and Flyover Channelization
- **Target Word Budget:** $\approx 150\text{ words}$.
- **Structural Purpose:** Define the multi-attribute edge impedance multiplier $\mu(e)$, the arterial bridge override, and the unified state transition cost $c(s, s')$.
- **Key Technical Elements to Cover:**
  1. Formulate the composite edge multiplier $\mu(e)$ (Display Equation 1):
     $$\mu(e) = \begin{cases} 0.80 \cdot m_{\text{rbt}}(e) & \text{if } \text{bridge}(e) = \text{True} \text{ and } h(e) \in \mathcal{H}_{\text{main}} \\ f_{\text{class}}(h(e)) \cdot m_{\text{rbt}}(e) & \text{otherwise} \end{cases}$$
  2. Detail the configured road-class hierarchy $f_{\text{class}}(h(e))$ reflecting two-wheeler suitability in mixed traffic:
     - Congested arterials penalised: Motorway ($4.0$), Trunk ($3.0$), Primary ($2.2$), Secondary ($1.5$).
     - Intermediate links: Tertiary ($1.15$), Tertiary Link ($1.1$), Secondary Link ($1.4$), Primary Link ($2.0$), Trunk Link ($2.5$).
     - Permissive local network: Residential ($1.0$, neutral baseline), Unclassified ($1.0$), Living Street ($0.95$), Service ($0.90$).
  3. Detail the Grade-Separated Arterial Bridge / Flyover Override:
     - On qualifying arterial segments ($h(e) \in \mathcal{H}_{\text{main}}$), an elevated structure (`bridge=yes`) **replaces** the heavy arterial penalty with $0.80$, effectively granting elevated flyovers priority over ground-level surface congestion.
     - Crucial specification: Emphasize that $0.80$ **replaces** the arterial multiplier, rather than multiplying it ($f_{\text{class}} \cdot 0.80$ is incorrect).
  4. Detail Roundabout Modifier and Lower-Bound Qualification (Audited Framing):
     - The implementation applies the continuous-flow roundabout factor $m_{\text{rbt}}(e) = 0.95$ sequentially after the bridge override check.
     - A qualifying bridge edge with a roundabout tag would therefore evaluate to $0.80 \times 0.95 = 0.76$.
     - Across the evaluated Bengaluru experimental dataset ($|E| = 744,216$), zero edges contain both tags simultaneously.
     - The minimum observed multiplier across this specific dataset is strictly $0.80$.
     - **Epistemological Framing:** $\mu(e) \ge 0.80$ is framed as a **dataset-verified condition** for the Bengaluru network in current experiments and a **formal prerequisite condition (Assumption A1)** required for theoretical heuristic admissibility. It is NOT claimed to hold unconditionally for arbitrary input graphs.
  5. Define the Unified State Transition Cost and Total Path Objective (Display Equation 3):
     $$c(s, s') = \mu(v, w) \cdot \ell(v, w) + P_{\text{turn}}(u, v, w)$$
     $$C(P) = \sum_{i=1}^k \mu(e_i) \cdot \ell(e_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$$
     where $s = (u, v)$ and $s' = (v, w)$. Transition cost $c(s, s')$ charges the edge impedance of outgoing segment $(v, w)$ and the turn maneuver cost at intermediate node $v$.
     Across path $P = \langle e_1, \dots, e_k \rangle$, each physical edge $e_i = (v_{i-1}, v_i)$ is charged exactly once for edge impedance, and each intermediate junction $v_1, \dots, v_{k-1}$ is charged exactly once for its turn deflection, with $P_{\text{turn}}(\text{None}, v_0, v_1) = 0.0$ at departure and zero turn cost assessed at destination $t = v_k$.
  6. Present Table I: Formal tabular specification of configured weights, topological modifiers, and functional descriptions.
  7. Boundary guardrail: Configured multipliers are engineering parameters designed for vehicle channelization, NOT empirically fitted econometric utilities or validated rider preferences.

---

## 4. Planned Float Asset: Table I Specification

- **Table Caption:** `TABLE I: CONFIGURED ROAD-CLASS IMPEDANCE MULTIPLIERS AND TOPOLOGICAL MODIFIERS`
- **Target Height:** $\approx 1.6\text{ in}$ (Single-Column Float).
- **Layout Structure (6 Rows):**

| Functional Category | Highway Classification Tag ($h(e)$) | Base Weight ($f_{\text{class}}$) | Modifier Condition | Net Multiplier ($\mu$) | Design Intent / Operational Role |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **High Arterial** | `motorway`, `trunk`, `primary` | $2.20\text{--}4.00$ | Standard surface | $2.20\text{--}4.00$ | Heavily penalized due to multi-lane congestion & conflict |
| **Grade-Separated** | `bridge=yes` on $\mathcal{H}_{\text{main}}$ | $2.20\text{--}4.00$ | **Replaced by 0.80** | **0.80** | Prioritised elevated flow; bypasses surface friction |
| **Secondary Corridor** | `secondary`, `secondary_link` | $1.40\text{--}1.50$ | Standard surface | $1.40\text{--}1.50$ | Moderately penalized connecting collectors |
| **Intermediate Collector** | `tertiary`, `tertiary_link` | $1.10\text{--}1.15$ | Standard surface | $1.10\text{--}1.15$ | Mildly penalized neighborhood distributor |
| **Local / Residential** | `residential`, `unclassified` | $1.00$ | Neutral baseline | $1.00$ | Favored baseline for agile two-wheeler traversal |
| **Permissive / Narrow** | `living_street`, `service` | $0.90\text{--}0.95$ | Roundabout: $\times 0.95$ | $0.855\text{--}0.95$ | Encouraged narrow alleys, access roads, and roundabouts |

---

## 5. Scope Demarcation and Guardrails

1. **Strictly Section III Only:**
   - Section IV materials (scaled Haversine heuristic proof, Theorem 1 admissibility, Theorem 2 consistency, Theorem 3 complexity derivations, and priority queue search pseudo-code/specification) are strictly excluded from Section III.
2. **Strictly Planning Only:**
   - No manuscript prose drafted in this phase.
   - All drafting is reserved for Phase 7.2 following research lead review.
3. **No Over-Claims:**
   - No safety, accident reduction, or fatality claims.
   - No travel-time savings, dynamic queue filtering, or real-time speed predictions.
   - Multipliers must be described as configured engineering penalties, not empirical behavioral preferences.
   - Lower bound $\mu(e) \ge 0.80$ is framed as dataset-verified on Bengaluru and an explicit operational condition (Assumption A1), not a universal law for arbitrary graphs.
