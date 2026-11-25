# Section IV Structural Outline — Proposed Turn-Aware Routing Algorithm (v1.0)

**Document:** [`paper1_section_IV_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_outline_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1 — Section IV Structural Planning and Mathematical Admissibility Evidence Map  
**Date:** 2026-11-06  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE SECTION IV STRUCTURAL OUTLINE (PLANNING ONLY — NO PROSE DRAFTED)**

---

## 1. Section Architecture and Space Allocation

Section IV details the proposed turn-aware state-expanded $A^*$ search algorithm, proves the conditional admissibility and monotonic consistency of the scaled Haversine heuristic, establishes optimal state finality without reopening, and derives formal computational complexity bounds under bounded physical junction valence.

* **Allocated Manuscript Space:** Page 3 Full (Column 1 and Column 2).
* **Target Body Text Word Count:** **480 words** (Strict range: $460\text{--}500\text{ words}$).
* **Display Equations:** Exactly 3 display equations:
  * **Equation (4):** Scaled Haversine Heuristic Lower Bound ($h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t)$).
  * **Equation (5):** Conditional Monotonic Consistency Condition ($h(s) \le c(s, s') + h(s')$).
  * **Equation (6):** General and Valence-Bounded Algorithmic Complexity Bounds ($\mathcal{M}, \mathcal{T}$).
* **Float Policy:** Strictly zero floating algorithm pseudo-code boxes (conforming to the master blueprint visual inventory, saving $\approx 3.2\text{ in}$ vertical space; search logic is specified rigorously via inline mathematical prose and formal display equations).
* **Prose Drafting Status:** Strictly zero manuscript prose drafted; planning and structural blueprinting only.

---

## 2. Subsection Breakdown and Word Budget Allocation

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           SECTION IV: DETAILED CONTENT & WORD ALLOCATION                         │
├───────┬───────────────────────────────────────────┬──────────────┬───────────────┬───────────────┤
│ Sub#  │ Subsection Heading                        │ Word Budget  │ Assets / Eqns │ Column Layout │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-A  │ State-Expanded Search Architecture and    │ ~110 words   │ None          │ Page 3,       │
│       │ Priority-Queue Formulation                │              │               │ Col 1 Top     │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-B  │ Scaled Haversine Heuristic Formulation    │ ~90 words    │ Eq. (4)       │ Page 3,       │
│       │                                           │              │               │ Col 1 Mid-Bot │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-C  │ Formal Optimality and Consistency Proofs  │ ~160 words   │ Eq. (5),      │ Page 3,       │
│       │ (Admissibility, Monotonicity, Finality)   │              │ Thm 1, 2,     │ Col 1 Bot &   │
│       │                                           │              │ Cor 1         │ Col 2 Top-Mid │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-D  │ Algorithmic Complexity under Physical     │ ~120 words   │ Eq. (6),      │ Page 3,       │
│       │ Junction Valence Bounds                   │              │ Assump A2,    │ Col 2 Bot     │
│       │                                           │              │ Thm 3         │               │
├───────┴───────────────────────────────────────────┼──────────────┴───────────────┴───────────────┤
│ TOTAL SECTION IV BUDGET                           │ 480 words    │ 3 Equations,  │ Exactly       │
│                                                   │              │ 0 Floats      │ 2.0 Columns   │
└───────────────────────────────────────────────────┴──────────────┴───────────────┴───────────────┘
```

---

## 3. Subsection Content Blueprints

### Subsection IV-A: State-Expanded Search Architecture and Priority-Queue Formulation
* **Focus:** Transition from classical node-based search to directed edge-state routing without full line-graph construction.
* **Core Elements:**
  * Define state tracking tuple $s = (u, v) \in E_s$ where $u = \text{tail}(e)$ and $v = \text{head}(e)$, representing arrival at intersection $v$ via incoming road segment $(u, v)$.
  * Root state initialization with synthetic departure state $s_0^{\text{state}} = (\text{None}, s_0)$, providing cardinality $|S| = |E_s| + 1 = 740,823$.
  * Successor transition generation: for current state $s = (u, v)$, outbound valid transitions advance to $s' = (v, w)$ for all $(v, w) \in E_s$, exploring transition space $E_S$.
  * Min-heap priority key structure: ordered tuple $(f(s), \kappa, s)$ where $f(s) = g(s) + h(s)$ and $\kappa \in \mathbb{N}$ is a monotonically incremented tie-breaking counter ensuring strict FIFO stability.
  * Explicit note: In-place state evaluation avoids building the explicit line graph $L(G)$, preserving an $\mathcal{O}(|E_s|)$ operational memory footprint.

### Subsection IV-B: Scaled Haversine Heuristic Formulation
* **Focus:** Mathematical derivation of the goal-directed heuristic lower bound.
* **Core Elements:**
  * Define $D_{\text{haversine}}(v, t)$ as the spherical great-circle chord distance between the physical coordinates $(\phi_v, \lambda_v)$ of vertex $v = \text{head}(s)$ and target destination $t = (\phi_t, \lambda_t)$.
  * State **Assumption A1 (Graph Multiplier Lower Bound):** Across the operating road network, every directed edge $e \in E_s$ satisfies $\mu(e) \ge \mu_{\min} = 0.80$ (empirically confirmed across the 744,216 edge records of Bengaluru).
  * State **Equation (4):**
    $$h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t) \tag{4}$$
  * State destination vanishing property: $h(s) = 0$ when $v = t$.

### Subsection IV-C: Formal Optimality and Consistency Proofs
* **Focus:** Rigorous mathematical proofs guaranteeing exact optimal solution discovery without state reopening.
* **Core Elements:**
  * **Theorem 1 (Conditional Admissibility):**
    * For any valid path $P = \langle s_1, s_2, \dots, s_k \rangle$ from state $s$ to $t$, cumulative impedance satisfies $C(P) \ge \sum_{i=1}^k c_{\min}(v_{i-1}, v_i) \ge \mu_{\min} \sum_{i=1}^k \ell(v_{i-1}, v_i) \ge \mu_{\min} D_{\text{haversine}}(v, t) = h(s)$.
    * Since $P_{\text{turn}} \ge 0$ unconditionally, $h(s) \le c^*(s, t)$, proving $h$ never overestimates minimal remaining traversal cost.
  * **Theorem 2 (Conditional Monotonic Consistency):**
    * For any valid transition $s = (u, v) \to s' = (v, w)$, the triangle inequality on the sphere dictates $D_{\text{haversine}}(v, t) \le D_{\text{haversine}}(v, w) + D_{\text{haversine}}(w, t)$.
    * Multiplying by $\mu_{\min} = 0.80$ yields $\mu_{\min} D_{\text{haversine}}(v, t) \le \mu_{\min} D_{\text{haversine}}(v, w) + \mu_{\min} D_{\text{haversine}}(w, t)$.
    * Since $c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w) \ge \mu_{\min} \ell(v, w) \ge \mu_{\min} D_{\text{haversine}}(v, w)$, substitution establishes **Equation (5)**:
      $$h(s) \le c(s, s') + h(s') \tag{5}$$
  * **Corollary 1 (Optimal State Finality):**
    * Monotonic consistency guarantees that extracted state costs $f(s)$ are monotonically non-decreasing.
    * When state $s = (u, v)$ is first extracted from `open_set`, $g(s) = c^*(s_0^{\text{state}}, s)$ is provably minimal and optimal.
    * No edge state $(u, v)$ is ever reopened or updated once extracted.
    * Physical vertex $v$ may be expanded up to $d_{\text{in}}(v)$ times via distinct incoming approaches, but each directional state is finalized exactly once.

### Subsection IV-D: Algorithmic Complexity under Physical Valence Bounds
* **Focus:** Asymptotic time and memory complexity analysis reflecting actual min-heap mechanics.
* **Core Elements:**
  * **Assumption A2 (Bounded Physical Junction Valence):** In physical planar/near-planar street topologies, intersection degree is strictly bounded by constant physical geometry: $\max_{v \in V} \{ d_{\text{in}}(v), d_{\text{out}}(v) \} \le d_{\max} = \mathcal{O}(1)$. (In Bengaluru, $\max d = 6$, mean $\bar{d} = 2.41$).
  * Min-heap mechanics without `decrease-key`: Successor relaxations push duplicate entries into the priority queue, bounded by at most $d_{\text{in}}(v)$ insertions per directed edge state.
  * Total heap insertions bounded by $|E_S| \le |E_s| \cdot d_{\max}^{\text{out}}$.
  * **Theorem 3 (General and Valence-Bounded Complexity Bounds):**
    * Derive general expression:
      $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}}), \quad \mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right) \tag{6}$$
    * Under physical street valence bounds (Assumption A2, $d_{\max} = \mathcal{O}(1)$), simplify directly to:
      $$\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|), \quad \mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$$
  * Concluding insight: Proves that turn-awareness introduces zero asymptotic penalty over standard node-based $A^*$, achieving exact turn-penalized shortest paths in linear-logarithmic time.

---

## 4. Rigorous IEEE Presentation and De-AI Compliance
1. **Direct Mathematical Exposition:** No introductory filler, robotic meta-commentary, or rhetorical hype.
2. **Strict Sentence Mechanics:** Zero em dashes (—) or en dashes (–); replaced with clean colons, commas, or structured subordination.
3. **Punctuation of Mathematics:** All display equations punctuated as grammatical clauses.
4. **Notation Invariance:** Symbol definitions strictly mirror Section III v1.3 ([`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md)).
