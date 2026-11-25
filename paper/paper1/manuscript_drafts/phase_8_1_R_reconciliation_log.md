# Phase 8.1-R Execution Log: Mathematical Complexity and Heuristic Proof Reconciliation

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks (Paper 1)  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1-R — Mathematical Complexity and Heuristic Proof Reconciliation  
**Date:** 2026-11-06  
**Document:** [`phase_8_1_R_reconciliation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_R_reconciliation_log.md)  
**Role:** Research Algorithms Engineer and Mathematical Proof Auditor  
**Parent Phase:** Phase 8.1 ([`phase_8_1_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_execution_log.md))  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.1-R RECONCILIATION COMPLETE (AWAITING LEAD REVIEW)**

---

## 1. Executive Summary and Directives

Phase 8.1-R resolves all remaining mathematical ambiguities in the Phase 8.1 planning deliverables prior to authorizing Section IV manuscript drafting. 

Specifically, this phase establishes:
1. Complete mathematical proof steps for the geometric lower-bound assumption $\ell(u, v) \ge D_{\text{haversine}}(u, v)$, parallel-edge lower-bound invariance, synthetic root consistency, justification for zero state reopening, and goal extraction optimality in the absence of a stale-pop guard.
2. Disentangled transition notation separating internal transitions ($T_{\text{internal}}$), synthetic initial transitions ($T_{\text{initial}}$), and total query transitions ($T_{\text{query}}$).
3. Exact accounting of stale successor expansions, showing summations over node degrees before maximum-valence bounding.
4. Formal integration of uncached parallel-edge cost scanning ($q_{\max} = 4$).
5. Exact auxiliary memory bounds expressed in logical entries across all active structures.
6. A four-tier hierarchy of complexity statements distinguishing general graphs, bounded-valence networks, Bengaluru-specific graph-wide maxima, and observed per-query metrics.

All updates have been incorporated directly into:
- [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.1)
- [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) (v1.1)

Zero manuscript prose was drafted, no frozen assets were altered, and no code was modified.

---

## 2. Task 1: Heuristic Proof Validation and Geometric Grounding

### 2.1 Physical Edge Length Lower Bound ($\ell \ge D_{\text{haversine}}$)
- **Codebase Source:** In [`routing/graph_manager.py#L191-L217`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py#L191-L217), graph edges are loaded from OpenStreetMap via OSMnx.
- **Geometric Derivation:** For any roadway segment $(v, w)$, the surveyed roadway length $\ell(v, w)$ is calculated as the sum of geodesic distances along its polyline shape points $\langle p_0 = v, p_1, \dots, p_m = w \rangle$:
  $$\ell(v, w) = \sum_{j=1}^m D_{\text{haversine}}(p_{j-1}, p_j)$$
  By the Riemannian spherical triangle inequality on the sphere:
  $$\sum_{j=1}^m D_{\text{haversine}}(p_{j-1}, p_j) \ge D_{\text{haversine}}(p_0, p_m) = D_{\text{haversine}}(v, w)$$
  For straight two-node segments where OSMnx removes intermediate points, $\ell(v, w) = D_{\text{haversine}}(v, w)$.
  Thus, $\ell(v, w) \ge D_{\text{haversine}}(v, w)$ is an exact physical and geometric property of terrestrial road networks.

### 2.2 Parallel-Edge Cost Invariance under Minimization
- In [`routing/algorithms.py#L645-L655`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L645-L655), parallel edges are resolved by:
  $$c_{\min}(v, w) = \min_{k \in \mathcal{K}(v, w)} [\mu(v, w, k) \cdot \ell(v, w, k)]$$
  Since every parallel edge candidate $k$ satisfies $\mu(v, w, k) \ge 0.80$ (Assumption A1) and $\ell(v, w, k) \ge D_{\text{haversine}}(v, w)$ (Assumption A3):
  $$\mu(v, w, k) \cdot \ell(v, w, k) \ge 0.80 \cdot D_{\text{haversine}}(v, w) \quad \forall k \in \mathcal{K}(v, w)$$
  The minimum of a set of values all lower-bounded by $0.80 D_{\text{haversine}}$ is itself lower-bounded by $0.80 D_{\text{haversine}}$.

### 2.3 Monotonic Consistency for Synthetic Initial State
- Root state: $s_0^{\text{state}} = (\text{None}, s_0)$.
- Heuristic: $h(s_0^{\text{state}}) = 0.80 \cdot D_{\text{haversine}}(s_0, t)$.
- For transition $s_0^{\text{state}} \to s' = (s_0, w)$ over $(s_0, w) \in E_s$:
  - By [`routing/algorithms.py#L151-L152`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L151-L152), $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$.
  - Transition cost: $c(s_0^{\text{state}}, s') = c_{\min}(s_0, w) + 0.0 \ge 0.80 \cdot D_{\text{haversine}}(s_0, w)$.
  - By spherical triangle inequality: $D_{\text{haversine}}(s_0, t) \le D_{\text{haversine}}(s_0, w) + D_{\text{haversine}}(w, t)$.
  - Multiplying by $0.80$: $h(s_0^{\text{state}}) \le c(s_0^{\text{state}}, s') + h(s')$.
  - Consistency holds identically for root departure.

### 2.4 Justification of Lack of State Reopening
- Under monotonic consistency (Theorem 2), the sequence of popped $f$-scores is non-decreasing.
- The first time state $s = (u, v)$ is popped from `open_set`, $g(s) = g^*(s)$ is provably minimal and optimal.
- Any subsequent candidate path to $s$ examined during search has cost $g_{\text{later}}(s) \ge g^*(s)$.
- In `two_wheeler_astar` ([`L681`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L681)), `new_cost < g_score[next_state]` strictly evaluates to `False`.
- State $s$ is never re-inserted into `open_set`, and `g_score[s]` is never updated.
- Therefore, state reopening logic is completely unnecessary, mathematically justifying the implementation.

### 2.5 Safety of Goal Extraction without Stale-Pop Guard
- In [`routing/algorithms.py#L566`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L566), the search terminates immediately upon popping any state with `current_node == end_node`.
- Because $h(\text{end\_node}) = 0.0$, the priority of any goal state in `open_set` is its accumulated cost: $f(s_{\text{goal}}) = g(s_{\text{goal}})$.
- Since `open_set` is a min-heap, it pops entries in non-decreasing order of $f$.
- The optimal path entry has minimal priority $f^* = g^*$. Any stale duplicate goal entry was pushed earlier with a higher cost $g_{\text{stale}} > g^*$, giving $f_{\text{stale}} > f^*$.
- Therefore, the optimal goal entry is popped **strictly before** any stale goal entry.
- Because the loop halts immediately upon the first goal pop, stale goal entries are never erroneously returned.

---

## 3. Task 2: Transition and Heap Notation Disentanglement

The notation has been updated across all deliverables to eliminate conflation between transitions, relaxations, and heap operations:

1. **Definitions:**
   $$T_{\text{internal}} = \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v) = 2,103,894$$
   $$T_{\text{initial}} = d_{\text{out}}(s_0) \le 6$$
   $$T_{\text{query}} = T_{\text{internal}} + T_{\text{initial}} \le 2,103,900$$
2. **Individual State Insertion Bound:**
   - For state $(v, w) \in E_s$: relaxed only via predecessors $u \in \text{pred}(v)$. Each predecessor transitions at most once during its optimal pop. Thus:
     $$\text{Insertions}((v, w)) \le d_{\text{in}}(v) \le d_{\max}^{\text{in}} \le 6$$
   - For synthetic root $s_0^{\text{state}}$: inserted exactly once at initialization ($\text{Insertions} = 1$).
   - For origin departures $(s_0, w)$: can be relaxed from root ($1$) and via cycle predecessors ($d_{\text{in}}(s_0)$): $\le 1 + d_{\text{in}}(s_0) \le 7$.
3. **Successful Relaxation Upper Bound ($R_{\max}$):**
   - Each transition in $T_{\text{query}}$ can successfully relax a state at most once.
   - $R_{\max} \le T_{\text{query}} = T_{\text{internal}} + T_{\text{initial}} \le 2,103,900$.
4. **Total Heap Insertion Upper Bound ($N_{\text{insert}}$):**
   - Initial root insertion ($1$) plus successful relaxations ($R_{\text{actual}} \le R_{\max}$):
     $$N_{\text{insert}} = 1 + R_{\text{actual}} \le 1 + T_{\text{query}} \le 2,103,901$$
5. **Total Heap Removal Upper Bound ($N_{\text{remove}}$):**
   - Total removals cannot exceed total insertions:
     $$N_{\text{remove}} \le N_{\text{insert}} \le 1 + T_{\text{query}} \le 2,103,901$$

---

## 4. Task 3: Exact Derivation of Stale Successor Expansions

In `two_wheeler_astar` ([`L552–L613`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L552-L613)), stale pops are not filtered before expanding neighbors:
1. **Best State Pops:** $E_{\text{best}} \le |S| = |E_s| + 1 = 740,823$.
2. **Stale State Pops:**
   $$E_{\text{stale}} \le N_{\text{remove}} - |S| \le T_{\text{query}} + 1 - (|E_s| + 1) = T_{\text{internal}} + T_{\text{initial}} - |E_s|$$
   Writing the summation over in-degrees:
   $$E_{\text{stale}} \le T_{\text{initial}} + \sum_{v \in V} d_{\text{in}}(v) \cdot (d_{\text{out}}(v) - 1)$$
   For Bengaluru: $E_{\text{stale}} \le 6 + 2,103,894 - 740,822 = 1,363,078$.
3. **Total Successor-Loop Iterations ($I_{\text{total}}$):**
   Let $k(u, v) \le d_{\text{in}}(u)$ denote the number of times state $(u, v)$ is popped.
   $$I_{\text{total}} = d_{\text{out}}(s_0) + \sum_{(u, v) \in E_s} k(u, v) \cdot d_{\text{out}}(v)$$
   Separating into best and stale iterations:
   $$I_{\text{best}} = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) d_{\text{out}}(v) = T_{\text{query}} \le 2,103,900$$
   $$I_{\text{stale}} = \sum_{(u, v) \in E_s} (k(u, v) - 1) \cdot d_{\text{out}}(v) \le \sum_{(u, v) \in E_s} (d_{\text{in}}(u) - 1) \cdot d_{\text{out}}(v)$$
   Bounding by maximum out-degree:
   $$I_{\text{total}} \le (1 + T_{\text{query}}) \cdot d_{\max}^{\text{out}} \le 2,103,901 \times 6 = 12,623,406$$
4. **Relaxation Opportunities vs. Actual Relaxations:**
   - Total evaluations in loop: $I_{\text{total}} \le 12,623,406$.
   - Successful relaxation opportunities: $I_{\text{best}} = T_{\text{query}} \le 2,103,900$. (Stale pops strictly fail `new_cost < g_score[next_state]`).
   - Actual successful relaxations: $R_{\text{actual}} \le T_{\text{query}} \le 2,103,900$.

---

## 5. Task 4: Parallel-Edge Cost Scanning Complexity

- **Multiplicity:** Max parallel multiplicity on `bengaluru_graph.pkl` is $q_{\max} = 4$.
- **Implementation Reality:** In [`routing/algorithms.py#L645-L655`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L645-L655), `min(two_wheeler_edge_cost(...) for data in edge_data.values())` is dynamically evaluated on every successor iteration without caching.
- **Complexity:** Evaluating edge cost takes $\mathcal{O}(q(v, w)) \le \mathcal{O}(q_{\max})$ operations per iteration.
- Total parallel scanning overhead:
  $$\mathcal{T}_{\text{edge\_eval}} = \mathcal{O}(q_{\max} \cdot I_{\text{total}}) = \mathcal{O}\left( q_{\max} \cdot (1 + T_{\text{query}}) \cdot d_{\max}^{\text{out}} \right) = \mathcal{O}(q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$$
  Since $q_{\max} \le 4 = \mathcal{O}(1)$, it scales loop time by at most $4\times$, preserving $\mathcal{O}(|E_s|)$ time on bounded-valence road networks.

---

## 6. Task 5: Logical-Entry Memory Bounds

The persistent structures instantiated in `two_wheeler_astar` are audited as follows:
- `open_set`: $\le N_{\text{insert}} \le 1 + T_{\text{query}} \le 2,103,901$ entries.
- `g_score`: $\le |S| = |E_s| + 1 \le 740,823$ entries.
- `came_from`: $\le |E_s| \le 740,822$ entries.
- `visited_nodes`: $\le |V| \le 308,643$ entries.
- **Total Peak Logical Entries:**
  $$\mathcal{M}_{\text{logical}} \le (1 + T_{\text{query}}) + (|E_s| + 1) + |E_s| + |V| = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} + |V|)$$
  For Bengaluru:
  $$\mathcal{M}_{\text{Bengaluru}} \le 2,103,901 + 740,823 + 740,822 + 308,643 = 3,894,189 \text{ logical entries}$$
  Notice: $3,894,189 / 740,822 \approx 5.257 \cdot |E_s|$, proving exact $\mathcal{O}(|E_s|)$ memory scaling.

---

## 7. Task 6: Revised Four-Tier Complexity Statements

1. **General Directed Graphs (Equation 6):**
   $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} + |V|) \text{ entries}$$
   $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right) \tag{6}$$
   With $d_{\max} = \max(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$:
   $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max} \log |E_s| + q_{\max} \cdot |E_s| \cdot d_{\max}^2 \right)$$
2. **Bounded-Valence Urban Networks (Assumption A2, Theorem 3):**
   Under $d_{\max} = \mathcal{O}(1)$ and $q_{\max} = \mathcal{O}(1)$:
   $$\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|) \text{ logical entries}, \quad \mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$$
3. **Bengaluru Graph-Wide Worst-Case Upper Bound:**
   - $|S| = 740,823$ states.
   - $T_{\text{query}} \le 2,103,900$ transitions.
   - $N_{\text{insert}} \le 2,103,901$ pushes.
   - $I_{\text{total}} \le 12,623,406$ successor loop iterations.
   - Auxiliary memory $\le 3,894,189$ logical entries.
4. **Observed Per-Query Operational Metrics (Corpus Benchmark):**
   Across the 25 evaluation corridors:
   - Mean runtime: $117.84\text{ ms}$ (median $103.7\text{ ms}$).
   - Mean expanded states: $\approx 5,200$ ($< 0.7\%$ of $|S|$).
   - Mean explored transitions: $\approx 14,800$ ($< 0.7\%$ of $T_{\text{query}}$).

---

## 8. Structural Blueprint Assessment

- The original structural blueprint ([`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)) was evaluated against these reconciled formulations.
- **Finding:** The four-subsection layout (IV-A: Search Architecture; IV-B: Scaled Heuristic; IV-C: Admissibility & Consistency; IV-D: Complexity) and the 500–550 body word budget accommodate all reconciled formulations perfectly.
- In Subsection IV-D, Equation (6) now incorporates $q_{\max}$ in the second term ($q_{\max} |E_s| d_{\max}^{\text{in}} d_{\max}^{\text{out}}$), providing mathematical completeness without altering layout boundaries.
- No structural reorganization is required.

---

## 9. Deliverables Inventory and Strict Stop Condition

All three required deliverables for Phase 8.1-R are complete:
1. **Updated Evidence Map:** [`research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.1)
2. **Updated Implementation Audit:** [`research/paper1_manuscript/phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) (v1.1)
3. **Reconciliation Log:** [`research/paper1_manuscript/phase_8_1_R_reconciliation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_R_reconciliation_log.md)

### Strict Stop Conditions Enforced:
- Zero Section IV manuscript prose has been drafted.
- Frozen Sections I, II, and III remain bitwise untouched.
- Source code, serialized graphs, and experimental data remain bitwise untouched.
- Zero experiments were executed.
- Phase 8.2 has not been started.
- Mathematical proofs await formal Research Lead review and approval.
