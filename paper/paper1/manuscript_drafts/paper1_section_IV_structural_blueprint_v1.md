# Section IV Structural Blueprint — Proposed Turn-Aware Routing Algorithm (v1.0)

**Document:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1 — Section IV Structural Planning and Mathematical Admissibility Evidence Map  
**Date:** 2026-11-06  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Parent Section III:** [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (Canonical Frozen Version 1.3)  
**Implementation References:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **AUTHORITATIVE SECTION IV STRUCTURAL BLUEPRINT (PLANNING ONLY — NO MANUSCRIPT PROSE DRAFTED)**

---

## 1. Executive Summary and Structural Objectives

Section IV of Paper 1 (*"IV. PROPOSED TURN-AWARE ROUTING ALGORITHM"*) specifies the state-expanded search algorithm, establishes formal proofs for heuristic admissibility and monotonic consistency, proves optimal state finality without reopening, and re-derives computational time and space complexity bounds grounded directly in the codebase implementation.

### 1.1 Physical Page Allocation and Layout on Page 3
In accordance with [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md), Section IV occupies **Page 3 in its entirety** (both Column 1 and Column 2):
- **Allocated Vertical Space:** Exactly 2.0 columns ($\approx 105\text{--}110$ lines per column, $\approx 210\text{--}220$ column-lines total).
- **Target Body Word Count:** **500–550 body words** (Strict tolerance: $480\text{--}560\text{ words}$).
- **Display Equation Quota:** Exactly **3 display equations**, numbered monotonically continuing from Section III as Equations (4), (5), and (6).
- **Float Policy:** Strictly **zero floating algorithm pseudocode boxes**. The search mechanics and mathematical guarantees are specified through compact mathematical prose and display equations, reclaiming $\approx 3.2\text{ inches}$ of vertical column height for rigorous proof exposition.
- **Section Boundary:** Section IV commences cleanly at the top of Page 3, Column 1, and terminates at the bottom of Page 3, Column 2, providing an exact transition to Section V (*Experimental Methodology*) on Page 4.

---

## 2. Four-Subsection Modular Structure

Section IV is divided into four compact, logically sequential subsections:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             SECTION IV: FOUR-SUBSECTION ARCHITECTURE                             │
├───────┬───────────────────────────────────────────┬──────────────┬───────────────┬───────────────┤
│ Sub#  │ Subsection Heading                        │ Word Budget  │ Equations     │ Layout Target │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-A  │ Turn-Aware State-Expanded Search          │ ~130 words   │ None          │ Page 3,       │
│       │ Architecture                              │              │               │ Col 1 Top     │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-B  │ Scaled Haversine Heuristic Formulation    │ ~100 words   │ Eq. (4)       │ Page 3,       │
│       │                                           │              │               │ Col 1 Mid-Bot │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-C  │ Admissibility and Consistency Proofs      │ ~170 words   │ Eq. (5),      │ Page 3,       │
│       │                                           │              │ Thm 1, Thm 2, │ Col 1 Bot &   │
│       │                                           │              │ Cor 1         │ Col 2 Top-Mid │
├───────┼───────────────────────────────────────────┼──────────────┼───────────────┼───────────────┤
│ IV-D  │ Computational Complexity Analysis         │ ~130 words   │ Eq. (6),      │ Page 3,       │
│       │                                           │              │ Assump A2,    │ Col 2 Bot     │
│       │                                           │              │ Thm 3         │               │
├───────┴───────────────────────────────────────────┼──────────────┴───────────────┴───────────────┤
│ TOTAL SECTION IV FOOTPRINT                        │ ~530 words   │ 3 Equations,  │ Exactly       │
│                                                   │              │ 0 Floats      │ 2.0 Columns   │
└───────────────────────────────────────────────────┴──────────────┴───────────────┴───────────────┘
```

---

## 3. Detailed Subsection Specifications

### Subsection IV-A: Turn-Aware State-Expanded Search Architecture

- **Technical Purpose:** Present the operational search algorithm executing on the effective simple directed graph $G = (V, E_s)$. Explain how heading context is maintained during search without materializing a full line graph, how the priority queue is structured, how parallel edges are collapsed, and how relaxation proceeds.
- **Mathematical Content:**
  - State representation $s = (u, v) \in S$, where $S = E_s \cup \{(\text{None}, s_0)\}$ ($|S| = |E_s| + 1 = 740,823$).
  - Priority queue $\mathcal{Q}$ stores 3-tuples $(f(s), \kappa, s)$, where $f(s) = g(s) + h(s)$ and $\kappa \in \mathbb{N}_0$ is a strict FIFO tie-breaker counter.
  - Tentative distance map $g(s)$ and backpointer map $\pi(s)$ indexed by directed edge states.
  - Successor expansion: Popping state $s = (u, v)$ generates transitions to $s' = (v, w)$ for all $(v, w) \in E_s$ via `graph.successors(v)`.
  - Parallel edge handling: For multi-edge pairs, effective traversal cost is the minimum complete impedance representative $c_{\min}(v, w) = \min_{k \in \mathcal{K}(v, w)} [\mu(v, w, k) \cdot \ell(v, w, k)]$.
  - Transition cost accrual: $c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w)$ matching Section III Eq. (3).
  - Relaxation update: If $s' \notin g$ or $g(s) + c(s, s') < g(s')$, record improved $g(s')$ and push $(g(s') + h(s'), \kappa, s')$ to $\mathcal{Q}$.
  - Termination: Immediate upon popping state $s$ whose current vertex is destination $t$ ($\text{head}(s) = t$). Backtrack path over $\pi$ to origin.
- **Required Equations:** None (relies on inline notation and cross-references to Section III Eq. 1–3).
- **Implementation Evidence:**
  - `start_state = (initial_previous_node, start_node)`: [`routing/algorithms.py#L522-L525`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L522-L525).
  - Tie-breaker counter: `counter = itertools.count()`: [`routing/algorithms.py#L533`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L533).
  - Priority queue operations: `heapq.heappush`, `heapq.heappop`: [`routing/algorithms.py#L537-L544`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L537-L544), [`L552-L554`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L552-L554), [`L693-L700`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L693-L700).
  - On-the-fly parallel edge collapse: `min(...)`: [`routing/algorithms.py#L645-L655`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L645-L655).
  - Turn penalty evaluation: `_turn_penalty`: [`routing/algorithms.py#L661-L666`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L661-L666).
  - Goal check on pop: `if current_node == end_node:`: [`routing/algorithms.py#L566`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L566).
- **Claims that can safely be made:**
  - In-place state evaluation avoids pre-computing or materializing the line graph $L(G)$.
  - Tie-breaker counter guarantees deterministic FIFO stability for equal $f$-scores.
  - Search terminates at the destination without incurring exit turn penalties.
- **Claims that must be avoided:**
  - Do NOT claim that Python `heapq` supports `decrease-key`.
  - Do NOT claim that stale heap entries are checked or pruned before entering the successor loop.
  - Do NOT claim that the state space includes multigraph edge keys (states are pairs $(u, v)$).
- **Suggested Word Budget:** **~130 words**.

---

### Subsection IV-B: Scaled Haversine Heuristic Formulation

- **Technical Purpose:** Formulate the goal-directed heuristic function $h(s)$ and establish the formal lower-bound scaling factor required by the configured road-impedance model.
- **Mathematical Content:**
  - Let $(\phi_v, \lambda_v)$ and $(\phi_t, \lambda_t)$ denote coordinates of intersection $v = \text{head}(s)$ and destination $t$.
  - Great-circle distance $D_{\text{haversine}}(v, t)$ computed via the Haversine formula on a spherical earth ($R = 6,371,000\text{ m}$).
  - State **Assumption A1 (Graph Multiplier Lower Bound):** Every effective directed edge $e \in E_s$ satisfies $\mu(e) \ge \mu_{\min} = 0.80$.
  - Formulate **Equation (4):**
    $$h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t), \quad \mu_{\min} = 0.80 \tag{4}$$
  - Destination vanishing condition: $h(s) = 0.0\text{ m}$ when $v = t$.
  - Synthetic root evaluation: For initial departure state $s_0^{\text{state}} = (\text{None}, s_0)$, $h(s_0^{\text{state}}) = \mu_{\min} \cdot D_{\text{haversine}}(s_0, t)$.
- **Required Equations:** **Equation (4)**.
- **Implementation Evidence:**
  - `MIN_PENALTY_FLOOR = 0.8`: [`routing/algorithms.py#L28`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L28).
  - `haversine_m`: [`routing/algorithms.py#L45-L60`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L45-L60).
  - `heuristic(node)` with `heuristic_mode="admissible"`: [`routing/algorithms.py#L500-L513`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L500-L513).
- **Claims that can safely be made:**
  - $h(s)$ scales physical great-circle distance by the minimum possible impedance multiplier ($\mu_{\min} = 0.80$).
  - Assumption A1 is empirically verified for the frozen Bengaluru road graph, where zero bridge-roundabout co-occurrences exist among 744,216 directed edge records.
- **Claims that must be avoided:**
  - Do NOT claim that $\mu(e) \ge 0.80$ is a universal physical law of all possible road networks (it is an empirical property of the Bengaluru dataset and an explicit prerequisite for the proof).
  - Do NOT confuse the admissible mode ($h = 0.80 \cdot D$) with the aggressive legacy mode ($h = D / 0.80 = 1.25 \cdot D$).
- **Suggested Word Budget:** **~100 words**.

---

### Subsection IV-C: Admissibility and Consistency Proofs

- **Technical Purpose:** Provide rigorous mathematical proofs of conditional admissibility (Theorem 1), monotonic consistency (Theorem 2), and optimal state finality without reopening (Corollary 1).
- **Mathematical Content:**
  - **Theorem 1 (Conditional Admissibility):**
    - For any path $P = \langle s_0^{\text{state}}, s_1, \dots, s_k \rangle$ from state $s = (u, v)$ to destination $t$ with vertices $v_0 = v, v_1, \dots, v_k = t$:
      $$C(P) = \sum_{i=1}^k c_{\min}(v_{i-1}, v_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$$
    - Because turn penalties are nonnegative ($P_{\text{turn}} \ge 0.0$ by Section III Eq. 1):
      $$C(P) \ge \sum_{i=1}^k c_{\min}(v_{i-1}, v_i)$$
    - For each physical segment, surveyed length $\ell(v_{i-1}, v_i)$ lower-bounds the great-circle chord: $\ell(v_{i-1}, v_i) \ge D_{\text{haversine}}(v_{i-1}, v_i)$.
    - Under Assumption A1, $c_{\min}(v_{i-1}, v_i) \ge \mu_{\min} \ell(v_{i-1}, v_i) \ge \mu_{\min} D_{\text{haversine}}(v_{i-1}, v_i)$.
    - By the spherical triangle inequality: $\sum_{i=1}^k D_{\text{haversine}}(v_{i-1}, v_i) \ge D_{\text{haversine}}(v, t)$.
    - Hence $C(P) \ge \mu_{\min} D_{\text{haversine}}(v, t) = h(s)$. Taking the infimum over all valid paths establishes $h(s) \le c^*(s, t)$.
  - **Theorem 2 (Conditional Monotonic Consistency):**
    - For any transition $s = (u, v) \to s' = (v, w)$ over $(v, w) \in E_s$, by the spherical triangle inequality:
      $$D_{\text{haversine}}(v, t) \le D_{\text{haversine}}(v, w) + D_{\text{haversine}}(w, t)$$
    - Multiplying by $\mu_{\min} = 0.80 > 0$:
      $$\mu_{\min} D_{\text{haversine}}(v, t) \le \mu_{\min} D_{\text{haversine}}(v, w) + \mu_{\min} D_{\text{haversine}}(w, t)$$
    - Since $c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w) \ge \mu_{\min} \ell(v, w) \ge \mu_{\min} D_{\text{haversine}}(v, w)$, substitution yields **Equation (5)**:
      $$h(s) \le c(s, s') + h(s') \tag{5}$$
    - Holds identically for synthetic departure state $s_0^{\text{state}} = (\text{None}, s_0)$ since $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$.
  - **Corollary 1 (Optimal State Finality):**
    - Monotonic consistency guarantees that extracted evaluation costs $f(s)$ are non-decreasing.
    - When state $s = (u, v)$ is first extracted from $\mathcal{Q}$, $g(s) = c^*(s_0^{\text{state}}, s)$ is provably minimal and optimal.
    - Zero state reopenings are required: no state $(u, v)$ ever receives a strictly smaller $g$-score on subsequent extractions.
- **Required Equations:** **Equation (5)**.
- **Implementation Evidence:**
  - Nonnegative turn penalties: [`routing/algorithms.py#L161-L167`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L161-L167).
  - Absence of state-reopening logic (no closed-set removal loop): [`routing/algorithms.py#L552-L613`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L552-L613).
- **Claims that can safely be made:**
  - $h(s)$ is provably admissible and consistent under the stated assumptions.
  - State-expanded $A^*$ with scaled Haversine heuristic guarantees exact shortest-path optimality with respect to the cost objective $C(P)$.
- **Claims that must be avoided:**
  - Do NOT claim that A* guarantees travel-time optimality (the objective $C(P)$ minimizes configured impedance and turn penalties, not measured time).
  - Do NOT claim that consistency holds if $\mu(e) < 0.80$ (e.g., if bridge and roundabout co-occurred).
- **Suggested Word Budget:** **~170 words**.

---

### Subsection IV-D: Computational Complexity Analysis

- **Technical Purpose:** Derive exact worst-case time and space complexity bounds from the actual codebase mechanics (binary min-heap without `decrease-key`, duplicate pushes, and unfiltered stale pops), both for general directed graphs and under bounded physical junction valence.
- **Mathematical Content:**
  - **State and Transition Cardinality:**
    - Distinct states: $|S| = |E_s| + 1 = 740,823$.
    - State transitions: $|E_S| = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v) \le |E_s| \cdot \min(d_{\max}^{\text{in}}, d_{\max}^{\text{out}}) + d_{\max}^{\text{out}}$. (In Bengaluru, $\sum d_{\text{in}} d_{\text{out}} = 2,103,894 \approx 2.84 \cdot |E_s|$).
  - **Relaxation and Heap Insertions:**
    - In `heapq`, relaxation pushes duplicate entries into $\mathcal{Q}$.
    - State $(v, w)$ can only be relaxed when reached via predecessor $u \in \text{pred}(v)$.
    - Each transition $(u, v) \to (v, w)$ can successfully relax $(v, w)$ at most once (subsequent stale pops of $(u, v)$ retrieve the same minimized $g$-score and strictly fail `new_cost < g_score[next_state]`).
    - Total heap pushes across the search: $N_{\text{pushes}} \le 1 + |E_S| \le 1 + |E_s| \cdot d_{\max}^{\text{out}} + d_{\max}^{\text{out}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}})$.
  - **Heap Operations Time:**
    - Peak heap size: $|\mathcal{Q}|_{\max} \le N_{\text{pushes}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}})$.
    - Logarithmic factor per push/pop: $\mathcal{O}(\log(|E_s| \cdot d_{\max}^{\text{out}}))$.
    - Total heap time: $\mathcal{T}_{\text{heap}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}))$.
  - **Stale Pop Successor Evaluation Overhead:**
    - Total pops $\le N_{\text{pushes}} \le 1 + |E_S|$.
    - The implementation does not skip stale entries before the successor loop.
    - When a stale entry for $(u, v)$ is popped, it iterates through all $d_{\text{out}}(v)$ successors, evaluating parallel-edge min-costs ($K_{\max} \le 4 = \mathcal{O}(1)$) and turn penalties in $\mathcal{O}(1)$ time before failing relaxation.
    - Total successor iterations across all pops: $I_{\text{total}} \le (1 + |E_S|) \cdot d_{\max}^{\text{out}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$.
  - **General Bounds Formulation (Equation 6):**
    $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}}), \quad \mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right) \tag{6}$$
  - **Assumption A2 (Bounded Physical Junction Valence):**
    - In terrestrial street networks, spatial geometry bounds intersection degree: $\max_{v \in V} \{ d_{\text{in}}(v), d_{\text{out}}(v) \} \le d_{\max} = \mathcal{O}(1)$. (In Bengaluru, $d_{\max}^{\text{in}} = d_{\max}^{\text{out}} = 6$, mean degree $\bar{d} = 2.41$).
  - **Theorem 3 (Valence-Bounded Complexity):**
    - Under Assumption A2 ($d_{\max} = \mathcal{O}(1)$), Equation (6) reduces strictly to:
      $$\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|), \quad \mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$$
    - Proves that turn-aware state expansion achieves the same asymptotic linear-logarithmic time and linear space complexity as classical node-based $A^*$ on road networks.
- **Required Equations:** **Equation (6)**.
- **Implementation Evidence:**
  - Duplicate push logic: [`routing/algorithms.py#L679-L700`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L679-L700).
  - Unchecked stale pop loop execution: [`routing/algorithms.py#L552-L613`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L552-L613).
  - Bounded parallel edges ($K_{\max} \le 4$): [`routing/algorithms.py#L645-L655`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L645-L655).
- **Claims that can safely be made:**
  - Duplicate heap entries cannot exceed the state transition count $|E_S|$.
  - Under bounded physical degree, memory is strictly $\mathcal{O}(|E_s|)$ and runtime is $\mathcal{O}(|E_s| \log |E_s|)$.
  - Bengaluru graph exhibits maximum degree 6, validating Assumption A2.
- **Claims that must be avoided:**
  - Do NOT claim that stale entries are skipped in $\mathcal{O}(1)$ before expanding successors.
  - Do NOT claim $\mathcal{O}(|E_s| \log |E_s|)$ for arbitrary directed graphs without the bounded degree assumption.
- **Suggested Word Budget:** **~130 words**.

---

## 4. Float and Pseudocode Policy

- **Policy Recommendation:** **NO PSEUDOCODE FLOAT BOX**.
- **Justification:**
  1. A standard IEEE algorithm float box (e.g., using `algorithmicx` or `algorithm2e`) consumes approximately $3.0\text{--}3.5\text{ vertical column inches}$ ($\approx 35\text{--}40$ lines of text), which would displace over 200 words of necessary theoretical and complexity exposition on Page 3.
  2. The algorithmic mechanics of state-expanded $A^*$ are standard variations of Dijkstra/A* on line graphs, fully and precisely described by the 3 display equations and compact prose.
  3. Omitting the float box preserves the exact visual balance planned in [`paper1_final_visual_inventory.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_visual_inventory.md) and [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md).

---

## 5. Cross-Referencing and Section Redundancy Prevention

To stay strictly within the 500–550 word budget, Section IV must avoid re-defining symbols established in Section III:
- **Do Not Re-Define:** $G_{\text{raw}}, V, E_s, \theta, \Delta\theta(u, v, w), P_{\text{turn}}, \mu(e), f_{\text{class}}, c_{\min}(u, v), c(s, s'), C(P)$.
- **Direct Cross-References to Use:**
  - Refer to Section III Eq. (1) for turn penalties $P_{\text{turn}}$.
  - Refer to Section III Eq. (2) and Table I for composite multipliers $\mu(e)$.
  - Refer to Section III Eq. (3) for transition cost $c(s, s')$ and path objective $C(P)$.
  - Refer to Section III for state space definition $S = E_s \cup \{(\text{None}, s_0)\}$ and cardinality $|S| = 740,823$.

---

## 6. Stop Condition Compliance

This blueprint provides structural planning and mathematical mapping only. In strict accordance with research protocols, zero manuscript prose has been drafted. Phase 8.2 will draft the manuscript prose only after Research Lead review and formal authorization.
