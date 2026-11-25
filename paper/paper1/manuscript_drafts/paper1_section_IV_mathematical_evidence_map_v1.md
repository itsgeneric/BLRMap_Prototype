# Section IV Mathematical Evidence Map — Admissibility, Consistency, and Complexity Formulations (v1.4 Final Consistent)

**Document:** [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1-U — Final Complexity Evidence Consistency Audit  
**Date:** 2026-11-06  
**Parent Blueprint:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Parent Section III:** [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (Canonical Frozen Version 1.3)  
**Implementation Source:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py)  
**Audited Datasets:** [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl), [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv), [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE RECONCILED MATHEMATICAL EVIDENCE MAP (AUDITED AND RECONCILED)**

---

## 1. Mathematical Search Formulation and Disentangled Transition Notation

### 1.1 Fundamental Graph Definitions
Let the raw urban street network be represented as a directed multigraph $G_{\text{raw}} = (V, E_{\text{raw}})$:
- $|V| = 308,643$ vertices denoting roadway intersections and physical geometry shape points, each associated with spherical coordinates $(\phi_v, \lambda_v)$ in decimal degrees.
- $|E_{\text{raw}}| = 744,216$ directed edge records, where multiple directed edges may connect the same ordered pair of vertices $(u, v)$.
- Parallel edges: Exactly $3,379$ ordered vertex pairs share multiple parallel edges ($6,773$ edge records total, with a maximum multiplicity of $q_{\max} = 4$ edges between any single pair).

Because graph search resolves parallel edges between identical ordered pairs by selecting the minimum-impedance connection on-the-fly, routing operates over the canonical simple directed graph:
$$G = (V, E_s)$$
where $E_s \subseteq V \times V$ is the set of distinct adjacent ordered vertex pairs:
$$|E_s| = |E_{\text{raw}}| - 3,394 = 740,822$$

For each simple directed edge $(u, v) \in E_s$, the effective traversal cost is the minimum complete impedance representative across all parallel multigraph records $\mathcal{K}(u, v)$:
$$c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} \left[ \mu(u, v, k) \cdot \ell(u, v, k) \right]$$
where $\ell(u, v, k) > 0$ is surveyed physical length in metres, and $\mu(u, v, k)$ is the composite road-class multiplier defined in Section III Eq. (2).

### 1.2 State Representation and Exact Cardinality
To incorporate trajectory-dependent turn penalties without materializing the explicit dual line graph $L(G)$, the search space is formulated over directed edge states:
$$s = (u, v) \in E_s$$
representing arrival at vertex $v$ from predecessor vertex $u$. Search states contain no multigraph edge key $k$, as parallel connections are resolved by the minimum-impedance representative $c_{\min}(u, v)$.

Departure from the origin vertex $s_0 \in V$ is represented by a unique synthetic root state:
$$s_0^{\text{state}} = (\text{None}, s_0)$$
The complete state space is:
$$S = E_s \cup \{(\text{None}, s_0)\}$$
yielding an exact state cardinality of:
$$|S| = |E_s| + 1 = 740,822 + 1 = 740,823$$
This is strictly distinct from the $744,216$ raw multigraph edge records.

### 1.3 Disentangled Transition Notation
Let $d_{\text{in}}(v)$ and $d_{\text{out}}(v)$ denote the in-degree and out-degree of vertex $v \in V$ on the effective simple directed graph $G = (V, E_s)$:
$$d_{\text{in}}(v) = |\{u \in V : (u, v) \in E_s\}|, \quad d_{\text{out}}(v) = |\{w \in V : (v, w) \in E_s\}|$$
By the Handshaking Lemma on simple directed graphs:
$$\sum_{v \in V} d_{\text{in}}(v) = |E_s| = 740,822, \quad \sum_{v \in V} d_{\text{out}}(v) = |E_s| = 740,822$$

To prevent confusion between graph-wide topological transitions, query-specific root transitions, relaxation attempts, and actual heap operations, we define separate, unambiguous notation:

1. **Internal State Transitions ($T_{\text{internal}}$):**  
   The number of directed transitions between standard edge states $(u, v) \to (v, w)$ across all physical vertices $v \in V$:
   $$T_{\text{internal}} = \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v)$$
   - **Actual Algorithm Search Space ($G = (V, E_s)$):** Because `two_wheeler_astar` iterates distinct successor vertices via `for next_node in graph.successors(...)` and collapses parallel connections on-the-fly, the search operates strictly over the simple directed graph $G = (V, E_s)$. The actual number of internal transitions in the state space is:
     $$T_{\text{internal}}^{\text{simple}} = \sum_{v \in V} d_{\text{in}}^{\text{simple}}(v) \cdot d_{\text{out}}^{\text{simple}}(v) = \mathbf{2,087,155}$$
   - **Raw Multigraph Record Comparison ($G_{\text{raw}}$):** The value cited in Section III v1.3 and Phase 3.6 ($2,103,894$) evaluates the multigraph degree product $\sum_v d_{\text{in}}^{\text{raw}}(v) d_{\text{out}}^{\text{raw}}(v)$. This represents the exact count of transitions if each parallel edge record had been materialized as an independent search state. Because $d^{\text{raw}}(v) \ge d^{\text{simple}}(v)$ everywhere, $T_{\text{internal}}^{\text{raw}} = \mathbf{2,103,894}$ serves as a **conservative topological comparison** ($2,103,894 > 2,087,155$, difference of $16,739$). However, it is **not** the actual algorithm transition count and is not used to generate hybrid stale-pop quantities.
2. **Initial Departure Transitions ($T_{\text{initial}}$):**  
   The number of transitions departing from the synthetic root state $s_0^{\text{state}} = (\text{None}, s_0)$ to outgoing states $(s_0, w)$ for $w \in \text{succ}(s_0)$:
   $$T_{\text{initial}} = d_{\text{out}}(s_0)$$
   Since $d_{\text{out}}(s_0) \le d_{\max}^{\text{out}} \le 6$, $T_{\text{initial}} \in [0, 6]$.
3. **Total Query Transitions ($T_{\text{query}}$):**  
   The total number of valid directional state transitions available to a query rooted at origin $s_0$:
   $$T_{\text{query}} = T_{\text{internal}} + T_{\text{initial}} = \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v) + d_{\text{out}}(s_0)$$
   - **Actual Search Space on Simple Graph:** $T_{\text{query}}^{\text{simple}} \le 2,087,155 + 6 = \mathbf{2,087,161}$.
   - **Conservative Multigraph Record Comparison:** $T_{\text{query}}^{\text{raw}} \le 2,103,894 + 6 = \mathbf{2,103,900}$.

### 1.4 Strict Conceptual Demarcation

| Quantity / Entity | Mathematical Symbol | Graph-Wide Theoretical Bound (Simple Graph) | Conservative Degree-Based Bound ($d_{\max}=6$) | Implementation Entity |
| :--- | :---: | :---: | :---: | :--- |
| **Effective Directed Edges** | $|E_s|$ | $740,822$ | $740,822$ | Distinct adjacent node pairs $(u, v)$ with $c_{\min}(u, v)$ |
| **Search States** | $|S|$ | $740,823$ | $740,823$ | Unique keys in `g_score`: $E_s \cup \{(\text{None}, s_0)\}$ |
| **Internal Transitions** | $T_{\text{internal}}$ | $\mathbf{2,087,155}$ (exact sum) | $\le 4,444,932$ ($|E_s| \cdot 6$) | Line-graph directed edges: $\sum_v d_{\text{in}}(v) d_{\text{out}}(v)$ |
| **Initial Transitions** | $T_{\text{initial}}$ | $d_{\text{out}}(s_0) \le 6$ | $\le 6$ | Transitions from synthetic root $(\text{None}, s_0)$ |
| **Total Query Transitions** | $T_{\text{query}}$ | $\le \mathbf{2,087,161}$ | $\le 4,444,938$ | $T_{\text{internal}} + T_{\text{initial}}$ |
| **Max Stale State Pops** | $E_{\text{stale}}$ | $\le \mathbf{1,346,339}$ (proven bound) | $\le 3,704,116$ ($|E_s| \cdot 5 + 6$) | Duplicate heap entries extracted after first optimal pop |
| **Max Heap Insertions** | $N_{\text{insert}}$ | $\le \mathbf{2,087,162}$ | $\le 4,444,939$ | Calls to `heapq.heappush` ($1 + R_{\text{actual}}$) |
| **Max Heap Removals** | $N_{\text{remove}}$ | $\le \mathbf{2,087,162}$ | $\le 4,444,939$ | Calls to `heapq.heappop` (best pops $+$ stale pops) |
| **Successor Loop Iterations** | $I_{\text{total}}$ | $\le \mathbf{5,886,792}$ (exact sum bound) | $\le \mathbf{10,165,195}$ (deg-bound) | Iterations of `for next_node in graph.successors(...)` |
| **Max Parallel Multiplicity**| $q_{\max}$ | $4$ | $4$ | Max multiplicity scanned in `edge_data.values()` |
| **Peak Auxiliary Memory** | $\mathcal{M}_{\text{logical}}$ | $\le \mathbf{3,877,450}$ entries | $\le 3,877,450$ entries | Sum of logical entries in `open_set`, `g_score`, `came_from`, `visited` |
| **Raw Multigraph Records** | $|E_{\text{raw}}|$ | $744,216$ (context) | — | Uncollapsed multigraph records in `bengaluru_graph.pkl` |

---

## 2. Heuristic Function, Geometric Lower Bounds, and Correctness Proofs

### 2.1 Heuristic Formulation
The goal-directed heuristic function $h(s)$ evaluates the estimated minimal remaining traversal impedance from state $s = (u, v)$ to target destination $t \in V$:
$$h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t), \quad \mu_{\min} = 0.80 \tag{4}$$
where:
- $v = \text{head}(s)$ is the current physical intersection.
- $D_{\text{haversine}}(v, t)$ is the great-circle chord distance on a spherical earth ($R = 6,371,000\text{ m}$) between coordinates $(\phi_v, \lambda_v)$ and $(\phi_t, \lambda_t)$.
- $\mu_{\min} = 0.80$ is the minimum possible edge impedance multiplier floor (`MIN_PENALTY_FLOOR = 0.8` in `routing/algorithms.py#L28`).

### 2.2 Formal Mathematical Assumptions

The correctness proofs rest on four explicit, auditable assumptions:

#### Assumption A1: Multiplier Floor ($\mu(e) \ge 0.80$)
- **Formal Statement:** Across the operating road network, every effective edge $e \in E_s$ satisfies:
  $$\mu(e) \ge \mu_{\min} = 0.80$$
- **Dataset-Verified Limitation:** In `routing/algorithms.py#L309-L331`, arterial flyovers receive $0.80$ and roundabouts receive $\times 0.95$. If an edge had both tags, sequential evaluation would evaluate to $0.80 \times 0.95 = 0.76 < 0.80$. However, on the frozen Bengaluru dataset (`bengaluru_graph.pkl`), exhaustive attribute scanning verifies that **exactly zero** edges possess both tags simultaneously. The empirical minimum multiplier is strictly $0.80$. Assumption A1 is an empirically verified property of the evaluated network, not an axiomatic truth of arbitrary street graphs.

#### Assumption A2: Nonnegative Turn Penalties ($P_{\text{turn}} \ge 0$)
- **Formal Statement:** The turn penalty function defined in Section III Eq. (1) satisfies:
  $$P_{\text{turn}}(u, v, w) \ge 0.0 \quad \forall u, v, w \in V$$
- **Codebase Verification:** In `_turn_penalty` (`routing/algorithms.py#L146-L168`), returned penalties are strictly drawn from $\{0.0, 8.0, 25.0\}$, satisfying $P_{\text{turn}} \ge 0$ unconditionally.

#### Assumption A3: Physical Road Length Lower Bound ($\ell \ge D_{\text{haversine}}$)
- **Formal Statement:** For every directed edge $(v, w) \in E_s$, surveyed physical length $\ell(v, w)$ is lower-bounded by the great-circle chord distance between its endpoint coordinates:
  $$\ell(v, w) \ge D_{\text{haversine}}(v, w)$$
- **Graph Construction Verification:** In OpenStreetMap networks processed via OSMnx (`routing/graph_manager.py#L191-L217`), physical roadway length $\ell(v, w)$ is calculated as the cumulative geodesic distance along the polyline shape points $\langle p_0 = v, p_1, \dots, p_m = w \rangle$:
  $$\ell(v, w) = \sum_{j=1}^m D_{\text{haversine}}(p_{j-1}, p_j)$$
  By the Riemannian spherical triangle inequality on great-circle arcs:
  $$\sum_{j=1}^m D_{\text{haversine}}(p_{j-1}, p_j) \ge D_{\text{haversine}}(p_0, p_m) = D_{\text{haversine}}(v, w)$$
  For straight two-node segments where OSMnx removes intermediate shape points, $\ell(v, w) = D_{\text{haversine}}(v, w)$. Hence $\ell(v, w) \ge D_{\text{haversine}}(v, w)$ holds identically across all physical edges.

#### Assumption A4: Parallel-Edge Cost Invariance under Minimization
- **Formal Statement:** For any ordered vertex pair $(v, w) \in E_s$ with parallel multigraph candidates $\mathcal{K}(v, w)$:
  $$c_{\min}(v, w) = \min_{k \in \mathcal{K}(v, w)} [\mu(v, w, k) \cdot \ell(v, w, k)] \ge \mu_{\min} \cdot D_{\text{haversine}}(v, w)$$
- **Proof:** By A1, $\mu(v, w, k) \ge \mu_{\min} = 0.80$ for all candidates $k \in \mathcal{K}(v, w)$. By A3, $\ell(v, w, k) \ge D_{\text{haversine}}(v, w)$ for all candidates $k$. Thus:
  $$\mu(v, w, k) \cdot \ell(v, w, k) \ge \mu_{\min} \cdot D_{\text{haversine}}(v, w) \quad \forall k \in \mathcal{K}(v, w)$$
  Since every element of the set is bounded below by $\mu_{\min} D_{\text{haversine}}(v, w)$, the minimum over $k \in \mathcal{K}(v, w)$ is likewise lower-bounded by $\mu_{\min} D_{\text{haversine}}(v, w)$.

---

### 2.3 Detailed Step-by-Step Proofs

#### Theorem 1: Conditional Admissibility
**Statement:** Under Assumptions A1–A4, the scaled Haversine heuristic $h(s)$ defined in Equation (4) is strictly admissible; that is, for every state $s = (u, v) \in S$:
$$h(s) \le c^*(s, t)$$
where $c^*(s, t)$ is the minimal possible accumulated traversal cost from state $s$ to target destination $t$.

**Step-by-Step Proof:**
1. Let $P^* = \langle s = \sigma_0, \sigma_1, \dots, \sigma_m \rangle$ be an optimal path of directed states from $s = (u, v)$ to destination $t$, traversing physical vertex sequence $v_0, v_1, \dots, v_m$ where $v_0 = v$ and $v_m = t$.
2. By Section III Eq. (3), the accumulated traversal impedance of $P^*$ is:
   $$c^*(s, t) = C(P^*) = \sum_{i=1}^m c_{\min}(v_{i-1}, v_i) + \sum_{i=1}^{m-1} P_{\text{turn}}(v_{i-2}, v_{i-1}, v_i)$$
3. By Assumption A2, all turn penalties are nonnegative ($P_{\text{turn}} \ge 0.0$). Therefore:
   $$c^*(s, t) \ge \sum_{i=1}^m c_{\min}(v_{i-1}, v_i)$$
4. By Assumption A4, each effective segment satisfies $c_{\min}(v_{i-1}, v_i) \ge \mu_{\min} \cdot D_{\text{haversine}}(v_{i-1}, v_i)$ with $\mu_{\min} = 0.80$. Substituting this lower bound:
   $$c^*(s, t) \ge \mu_{\min} \sum_{i=1}^m D_{\text{haversine}}(v_{i-1}, v_i)$$
5. By the triangle inequality for great-circle geodesic distances on the Riemannian sphere:
   $$\sum_{i=1}^m D_{\text{haversine}}(v_{i-1}, v_i) \ge D_{\text{haversine}}(v_0, v_m) = D_{\text{haversine}}(v, t)$$
6. Multiplying both sides by positive scalar $\mu_{\min} = 0.80 > 0$:
   $$\mu_{\min} \sum_{i=1}^m D_{\text{haversine}}(v_{i-1}, v_i) \ge \mu_{\min} D_{\text{haversine}}(v, t)$$
7. Combining Steps 4 and 6:
   $$c^*(s, t) \ge \mu_{\min} D_{\text{haversine}}(v, t) = h(s)$$
8. Since $h(s) \le c^*(s, t)$ holds for all $s \in S$, the heuristic never overestimates the minimal remaining traversal cost to destination $t$. $\blacksquare$

---

#### Theorem 2: Conditional Monotonic Consistency
**Statement:** Under Assumptions A1–A4, the scaled Haversine heuristic $h(s)$ satisfies the monotonicity condition across every valid directed transition $s = (u, v) \to s' = (v, w)$ in $E_S$:
$$h(s) \le c(s, s') + h(s') \tag{5}$$
where $c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w)$ is the transition cost.

**Step-by-Step Proof:**
1. Consider valid state transition $s = (u, v) \to s' = (v, w)$ over simple directed edge $(v, w) \in E_s$.
2. By the spherical triangle inequality on coordinates $(\phi_v, \lambda_v)$, $(\phi_w, \lambda_w)$, and target destination $(\phi_t, \lambda_t)$:
   $$D_{\text{haversine}}(v, t) \le D_{\text{haversine}}(v, w) + D_{\text{haversine}}(w, t)$$
3. Multiplying both sides of the inequality by positive scalar $\mu_{\min} = 0.80$:
   $$\mu_{\min} D_{\text{haversine}}(v, t) \le \mu_{\min} D_{\text{haversine}}(v, w) + \mu_{\min} D_{\text{haversine}}(w, t)$$
4. By Equation (4), $h(s) = \mu_{\min} D_{\text{haversine}}(v, t)$ and $h(s') = \mu_{\min} D_{\text{haversine}}(w, t)$. Substituting:
   $$h(s) \le \mu_{\min} D_{\text{haversine}}(v, w) + h(s')$$
5. By Assumption A4, $c_{\min}(v, w) \ge \mu_{\min} D_{\text{haversine}}(v, w)$. Furthermore, transition cost includes turn penalty:
   $$c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w)$$
   Since $P_{\text{turn}}(u, v, w) \ge 0.0$ by Assumption A2:
   $$c(s, s') \ge c_{\min}(v, w) \ge \mu_{\min} D_{\text{haversine}}(v, w)$$
6. Substituting this lower bound into Step 4:
   $$h(s) \le c(s, s') + h(s')$$
7. **Synthetic Departure State Case:** For initial departure state $s_0^{\text{state}} = (\text{None}, s_0)$ transitioning to $s' = (s_0, w)$ for $(s_0, w) \in E_s$:
   $c(s_0^{\text{state}}, s') = c_{\min}(s_0, w) + P_{\text{turn}}(\text{None}, s_0, w) = c_{\min}(s_0, w) + 0.0 \ge \mu_{\min} D_{\text{haversine}}(s_0, w)$.
   Thus $h(s_0^{\text{state}}) \le c(s_0^{\text{state}}, s') + h(s')$ holds identically.
8. Therefore, $h(s)$ is monotonically consistent across all valid transitions in $E_S$. $\blacksquare$

---

#### Corollary 1: Optimal State Finality and Justification for Lack of State Reopening
**Statement:** Because $h(s)$ is monotonically consistent (Theorem 2), the sequence of evaluation values $f(s) = g(s) + h(s)$ of states extracted from the priority queue $\mathcal{Q}$ is monotonically non-decreasing. When any directed edge-state $s = (u, v)$ is extracted from $\mathcal{Q}$ for the first time, its accumulated cost $g(s)$ is strictly optimal:
$$g(s) = c^*(s_0^{\text{state}}, s)$$
Consequently:
1. **Justification of Implementation:** Any path to state $s$ discovered after its first extraction must have cost $g_{\text{later}}(s) \ge g(s)$. In the implementation relaxation check (`routing/algorithms.py#L681`):
   ```python
   if next_state not in g_score or new_cost < g_score[next_state]:
   ```
   `g_score[s]` already stores the optimal cost $g^*(s)$, so `new_cost < g_score[next_state]` strictly evaluates to `False`. The state is never re-inserted into $\mathcal{Q}$, and `g_score[s]` is never updated. This mathematically proves that **state reopening is unnecessary**, justifying the absence of state-reopening logic in `two_wheeler_astar`.
2. **Distinct Trajectory Visits:** An intersection vertex $v$ may be reached up to $d_{\text{in}}(v)$ times via distinct incoming trajectories $u$, but each discrete directional state $(u, v)$ is finalized exactly once.

---

#### Theorem 2.4: Safety of Goal Extraction without Stale-Entry Guard
**Statement:** In `two_wheeler_astar`, the goal condition `if current_node == end_node:` is evaluated immediately upon popping state $s = (u, v)$ from `open_set` (Line 566). The first extracted goal state is guaranteed to have optimal traversal cost, despite the absence of an explicit check to discard stale entries upon extraction.

**Proof:**
1. Let $s_{\text{goal}} = (u, \text{end\_node})$ be any state representing arrival at `end_node`.
2. By Equation (4), the heuristic vanishes at the destination:
   $$h(s_{\text{goal}}) = \mu_{\min} \cdot D_{\text{haversine}}(\text{end\_node}, \text{end\_node}) = 0.0\text{ m}$$
3. Therefore, for every goal entry in `open_set`, its priority key is simply its accumulated tentative cost:
   $$f(s_{\text{goal}}) = g(s_{\text{goal}}) + h(s_{\text{goal}}) = g(s_{\text{goal}})$$
4. Because `open_set` is a binary min-heap, it extracts entries in non-decreasing order of priority $f$.
5. Suppose multiple entries for goal states exist in `open_set` (e.g., discovering alternative paths to `end_node` via different predecessors or earlier non-optimal paths).
6. Any stale duplicate entry for a goal state was inserted earlier with a higher cost $g_{\text{stale}} > g^*$. Its priority was $f_{\text{stale}} = g_{\text{stale}} > g^*$.
7. The optimal path to `end_node` has cost $g^*$, giving priority $f^* = g^* < f_{\text{stale}}$.
8. By heap ordering, the entry with minimal priority $f^*$ is extracted **strictly before** any stale goal entry with $f_{\text{stale}} > f^*$.
9. Because the search terminates immediately upon extracting the first state with `current_node == end_node` (Lines 566–605), the search returns the path corresponding to $f^* = g^*$.
10. Therefore, goal extraction is provably safe and optimal, and stale goal entries are never erroneously accepted as the shortest path. $\blacksquare$

---

## 3. Rigorous Derivation of Stale Successor Expansions

### 3.1 Maximum Stale Pops per State and Graph-Wide Upper Bound
Let state $s = (u, v) \in E_s$ be a directed edge in the routing graph.
1. **States with $u \ne s_0$:**  
   State $(u, v)$ can only be relaxed when an incoming state $(x, u)$ is expanded, where $x \in \text{pred}(u)$. There are exactly $d_{\text{in}}(u)$ such predecessors.  
   Because stale pops of $(x, u)$ retrieve already-minimized $g$-scores and evaluate candidate costs identical to the first pop, `new_cost < g_score[(u, v)]` strictly evaluates to `False`. Thus, each incoming transition $(x, u) \to (u, v)$ can trigger at most **one** successful insertion of $(u, v)$.  
   Therefore, total insertions of state $(u, v)$ cannot exceed $d_{\text{in}}(u)$.  
   The first pop of $(u, v)$ is the optimal (best) pop. Subsequent pops are stale pops. Thus:
   $$\text{Stale pops of } (u, v) \le \max(d_{\text{in}}(u) - 1, 0)$$
   Summing across all $d_{\text{out}}(u)$ outgoing edges departing from vertex $u \ne s_0$:
   $$\sum_{v \in \text{succ}(u)} \text{Stale pops of } (u, v) \le d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0)$$
2. **States departing from origin $s_0$ ($u = s_0$):**  
   State $(s_0, v)$ can be reached from:
   - The synthetic root state $s_0^{\text{state}} = (\text{None}, s_0)$ (at most 1 insertion).
   - Any regular incoming states $(x, s_0)$ for $x \in \text{pred}(s_0)$ via cycles (at most $d_{\text{in}}(s_0)$ insertions).  
   Total insertions of $(s_0, v)$ cannot exceed $1 + d_{\text{in}}(s_0)$.  
   Stale pops of $(s_0, v)$ are at most $(1 + d_{\text{in}}(s_0)) - 1 = d_{\text{in}}(s_0)$.  
   Summing across all $d_{\text{out}}(s_0)$ outgoing edges from $s_0$:
   $$\sum_{v \in \text{succ}(s_0)} \text{Stale pops of } (s_0, v) \le d_{\text{out}}(s_0) \cdot d_{\text{in}}(s_0)$$
3. **Synthetic Root State $s_0^{\text{state}}$:**  
   Inserted once at initialization and popped at most once. Stale pops $= 0$.
4. **Complete Graph-Wide Stale Pop Bound ($E_{\text{stale}}$):**  
   Summing across all states in $S$:
   $$E_{\text{stale}} \le d_{\text{out}}(s_0) \cdot d_{\text{in}}(s_0) + \sum_{u \ne s_0} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0)$$
   Algebraically, since $d_{\text{in}}(s_0) - \max(d_{\text{in}}(s_0) - 1, 0) = \mathbb{I}(d_{\text{in}}(s_0) \ge 1) \le 1$:
   $$E_{\text{stale}} \le \sum_{u \in V} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0) + d_{\text{out}}(s_0) \cdot \mathbb{I}(d_{\text{in}}(s_0) \ge 1)$$

### 3.2 Audit of Earlier Formulations and Removal of the Multigraph Stale-Pop Proxy

#### 1. Flaws in the Early Difference Formulation
The formulation initially proposed in Phase 8.1 was:
$$\sum_v d_{\text{in}}(v) \cdot (d_{\text{out}}(v) - 1) = T_{\text{internal}} - |E_s|$$
Audit reveals three critical defects:
1. **Incorrect Degree Pairing:** It paired $(-1)$ with the destination's out-degree $d_{\text{out}}(v)$, whereas relaxation opportunities and multiple heap insertions of an edge $(u, v)$ are governed by incoming paths to $u$, which depends on the approach vertex's in-degree $d_{\text{in}}(u)$.
2. **Failure on Source Vertices:** The algebraic identity $\sum_u d_{\text{out}}(u)(d_{\text{in}}(u) - 1) = T_{\text{internal}} - |E|$ lacks the non-negative truncation operator $\max(\cdot, 0)$. On general directed graphs containing source vertices ($d_{\text{in}}(u) = 0$ with $d_{\text{out}}(u) > 0$), $(d_{\text{in}}(u) - 1) = -1 < 0$, which generates negative terms that unphysically cancel positive stale counts. In such graphs, $T_{\text{internal}} - |E|$ is strictly *less* than the true stale bound $\sum_u d_{\text{out}}(u) \max(d_{\text{in}}(u)-1, 0)$, invalidating it as a general conservative upper bound.
3. **Omission of Origin Departure:** It omitted the $+d_{\text{out}}(s_0)$ initial departure bonus.

#### 2. Formal Rejection of the Multigraph Stale-Pop Proxy ($T_{\text{internal\_raw}} - |E_s| + 6 = 1,363,078$)
In Phase 8.1-S, an alternative proxy $E_{\text{stale\_raw}} \le T_{\text{internal\_raw}} - |E_s| + 6 = 1,363,078$ was considered.
A rigorous mathematical audit establishes that this proxy cannot be derived from multigraph principles:
- It is an ad-hoc hybrid that subtracts the simple-graph edge count ($|E_s| = 740,822$) from the multigraph degree product ($T_{\text{internal\_raw}} = 2,103,894$).
- On the multigraph itself, the consistent subtraction would be $T_{\text{internal\_raw}} - |E_{\text{raw}}| = 2,103,894 - 744,216 = 1,359,678$.
- More fundamentally, because `two_wheeler_astar` collapses parallel edges on-the-fly and keys states strictly by vertex pairs $(u, v) \in E_s$, multigraph parallel records never materialize as distinct search states or duplicate heap pushes.
- **Audit Action:** The proxy $E_{\text{stale\_raw}} \le 1,363,078$ and its derived loop iteration bound ($10,282,368$) are **formally removed** from the authoritative evidence map.

#### 3. Authoritative Reconciled Stale-Pop Bound
The authoritative stale-pop upper bound is anchored exclusively on the proven simple-graph reachability formulation:
$$E_{\text{stale}} \le \sum_{u \in V} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0) + d_{\text{out}}(s_0) \cdot \mathbb{I}(d_{\text{in}}(s_0) \ge 1)$$
- Simple graph topological base sum: $\sum_u d_{\text{out}}(u) \max(d_{\text{in}}(u) - 1, 0) = \mathbf{1,346,333}$.
- Origin adjustment term: $\max_{s_0} [d_{\text{out}}(s_0) \mathbb{I}(d_{\text{in}}(s_0) \ge 1)] = \mathbf{6}$.
- **Authoritative Graph-Wide Theoretical Upper Bound:**
  $$E_{\text{stale}} \le 1,346,333 + 6 = \mathbf{1,346,339} \text{ stale extractions}$$

---

### 3.3 Successor Loop Iteration Accounting ($I_{\text{best}}, I_{\text{stale}}, I_{\text{total}}$)

When state $(u, v)$ is popped (whether best or stale), if $v \ne \text{end\_node}$, it executes $d_{\text{out}}(v)$ loop iterations in `for next_node in graph.successors(current_node)`.

1. **Best Successor Iterations ($I_{\text{best}}$):**  
   Best pops expand each reachable state at most once:
   $$I_{\text{best}} = d_{\text{out}}(s_0) + \sum_{(u, v) \in E_s} d_{\text{out}}(v) = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) d_{\text{out}}(v) = T_{\text{query}}^{\text{simple}}$$
   $$I_{\text{best}} \le 2,087,155 + 6 = \mathbf{2,087,161}$$
2. **Stale Successor Iterations ($I_{\text{stale}}$):**  
   - **Graph-Wide Theoretical Bound (via Exact Degree Summation):** Each stale pop of $(u, v)$ executes $d_{\text{out}}(v)$ iterations:
     $$I_{\text{stale},\text{exact\_sum}} \le \sum_{u \in V} \max(d_{\text{in}}(u) - 1, 0) \cdot \left(\sum_{v \in \text{succ}(u)} d_{\text{out}}(v)\right) + \max_{s_0: d_{\text{in}}(s_0) \ge 1} \left[ \sum_{v \in \text{succ}(s_0)} d_{\text{out}}(v) \right]$$
     Evaluating across the Bengaluru network:
     - The base network summation over all $u \in V$ is:
       $$\sum_{u \in V} \max(d_{\text{in}}(u) - 1, 0) \cdot \left(\sum_{v \in \text{succ}(u)} d_{\text{out}}(v)\right) = \mathbf{3,799,611}$$
     - The origin adjustment term represents the additional stale pops of $(s_0, v)$ when $d_{\text{in}}(s_0) \ge 1$ (due to incoming cycle edges pushing through $s_0$). Each such additional stale pop executes $d_{\text{out}}(v)$ loop iterations. In `bengaluru_graph.pkl`, the maximum sum of successor out-degrees for any node with $d_{\text{in}} \ge 1$ is attained at vertex $s_0 = 2246770321$ ($d_{\text{out}}=6, d_{\text{in}}=6$), whose 6 successor nodes have out-degrees $[3, 3, 3, 3, 3, 5]$, summing to exactly:
       $$\sum_{v \in \text{succ}(2246770321)} d_{\text{out}}(v) = 3 + 3 + 3 + 3 + 3 + 5 = \mathbf{20}$$
     - Adding this origin worst-case adjustment:
       $$I_{\text{stale},\text{exact\_sum}} = 3,799,611 + 20 = \mathbf{3,799,631}$$
   - **Conservative Degree-Bounded Bound ($d_{\max}^{\text{out}} = 6$):**  
     Bounding each stale pop by the network maximum out-degree:
     $$I_{\text{stale}} \le E_{\text{stale}} \times 6 = 1,346,339 \times 6 = \mathbf{8,078,034}$$
3. **Total Successor Iterations ($I_{\text{total}} = I_{\text{best}} + I_{\text{stale}}$):**  
   - **Graph-Wide Theoretical Upper Bound (via Exact Degree Summation):**
     $$I_{\text{total},\text{exact\_sum}} = 2,087,161 + 3,799,631 = \mathbf{5,886,792}$$
     *(Note: This represents the theoretical graph-wide bound if a worst-case query saturated every reachable state and exhausted all potential stale pops. It must NOT be described as an observed individual-query iteration count).*
   - **Conservative Degree-Bounded Bound on Simple Graph ($d_{\max}^{\text{out}} = 6$):**
     $$I_{\text{total}} \le 2,087,161 + 8,078,034 = \mathbf{10,165,195}$$
   - **Crude Global Upper Bound ($N_{\text{remove}} \times 6$):**
     $$I_{\text{total}} \le 2,087,162 \times 6 = \mathbf{12,522,972}$$

---

## 4. Parallel-Edge Cost Scanning Complexity

In `routing/algorithms.py#L623-L656`:
```python
edge_data = graph.get_edge_data(current_node, next_node)
if "length" in edge_data:
    edge_cost = two_wheeler_edge_cost(edge_data, ...)
else:
    edge_cost = min(
        two_wheeler_edge_cost(data, ...)
        for data in edge_data.values()
    )
```

1. **Multiplicity Bound and Distribution:**  
   Across the 740,822 effective edge pairs in `bengaluru_graph.pkl`, parallel multiplicity satisfies:
   $$q(v, w) = |\mathcal{K}(v, w)| \le q_{\max} = 4$$
   The empirical distribution across all 740,822 ordered vertex pairs is:
   - $q = 1$: $737,443$ pairs ($99.54\%$, single edge)
   - $q = 2$: $3,365$ pairs ($0.45\%$, dual parallel edges)
   - $q = 3$: $13$ pairs ($0.0018\%$, triple parallel edges)
   - $q = 4$: $1$ pair ($0.0001\%$, quadruple parallel edges)
   Total parallel pairs: $3,379$ pairs containing $6,773$ edge records ($3,394$ excess multigraph edges).
2. **Evaluation Mechanics and Lack of Caching:**  
   There is **no caching, memoization, or precomputed edge-cost table**.
   Every time directed edge $(v, w)$ is examined in the successor loop, `edge_data.values()` is dynamically scanned, executing $q(v, w) \le q_{\max}$ evaluations of `two_wheeler_edge_cost`.
3. **Per-Iteration and Total Scanning Overhead:**  
   Each call to `two_wheeler_edge_cost` performs $\mathcal{O}(1)$ dictionary lookups and floating-point multiplications.
   Cost per successor iteration is $\mathcal{O}(q(v, w)) \le \mathcal{O}(q_{\max})$.
   Total edge-evaluation operations across all $I_{\text{total}}$ successor iterations:
   $$\mathcal{T}_{\text{edge\_eval}} \le \sum_{\text{iterations}} q(v, w) \le q_{\max} \cdot I_{\text{total}}$$
   - Using exact simple-graph iterations ($I_{\text{total},\text{exact}} = 5,886,792$):
     $$\mathcal{T}_{\text{edge\_eval}} \le 4 \times 5,886,792 = \mathbf{23,547,168} \text{ evaluations}$$
     (In practice, because $>99.5\%$ of edges have $q=1$, the expected evaluations are within $\sim 1.005 \times I_{\text{total}}$).
   - Using degree-bounded simple-graph iterations ($I_{\text{total}} \le 10,165,195$):
     $$\mathcal{T}_{\text{edge\_eval}} \le 4 \times 10,165,195 = \mathbf{40,660,780} \text{ evaluations}$$
   - In general asymptotic terms:
     $$\mathcal{T}_{\text{edge\_eval}} = \mathcal{O}\left( q_{\max} \cdot (1 + T_{\text{query}}) \cdot d_{\max}^{\text{out}} \right) = \mathcal{O}(q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$$
   In Bengaluru, $q_{\max} = 4 = \mathcal{O}(1)$, so parallel-edge scanning introduces a small constant factor without altering the asymptotic time complexity.

---

## 5. Auxiliary Memory Bound (Logical Entries)

The persistent per-query data structures instantiated in `two_wheeler_astar` are strictly enumerated below:

| Data Structure | Code Reference | Stored Data Type | Maximum Logical Entries | Authoritative Simple Graph Bound | Multigraph Comparison Proxy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `open_set` | [`L535`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L535) | 3-tuple `(priority, counter, state)` | $N_{\text{insert}} \le 1 + T_{\text{query}}$ | $\le \mathbf{2,087,162}$ entries | $\le 2,103,901$ entries |
| `g_score` | [`L527`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L527) | `dict`: `state` $\to$ `float` | $|S| = |E_s| + 1$ | $\le \mathbf{740,823}$ entries | $\le 740,823$ entries |
| `came_from` | [`L531`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L531) | `dict`: `state` $\to$ `state` | $|S| - 1 = |E_s|$ | $\le \mathbf{740,822}$ entries | $\le 740,822$ entries |
| `visited_nodes` | [`L547`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L547) | `set`: `node_id` | $|V|$ | $\le \mathbf{308,643}$ entries | $\le 308,643$ entries |
| Scalar Counters | [`L533-L548`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L533-L548) | `counter`, `expanded_states`, etc. | $\mathcal{O}(1)$ scalars | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ |

> [!IMPORTANT]
> **Logical Entries vs. Measured Bytes:**  
> These bounds represent **counts of discrete logical elements** (heap 3-tuples, dictionary key-value entries, and set integer members), not measured bytes in memory. Physical RAM consumption in CPython includes object headers, pointer arrays, and hash-table overhead. Asymptotically, physical memory is bounded by $\mathcal{O}(\mathcal{M}_{\text{logical}}) = \mathcal{O}(|E_s|)$ on bounded-degree graphs.

### 5.1 Total Logical Entry Upper Bound
Summing across all persistent structures:
$$\mathcal{M}_{\text{logical}} = |\text{open\_set}|_{\max} + |\text{g\_score}|_{\max} + |\text{came\_from}|_{\max} + |\text{visited\_nodes}|_{\max}$$
$$\mathcal{M}_{\text{logical}} \le (1 + T_{\text{query}}) + (|E_s| + 1) + |E_s| + |V| = 2|E_s| + |V| + 2 + T_{\text{query}}$$
Using $T_{\text{query}} \le |E_s| \cdot d_{\max}^{\text{out}} + d_{\max}^{\text{out}}$:
$$\mathcal{M}_{\text{logical}} \le |E_s| \cdot (2 + d_{\max}^{\text{out}}) + |V| + d_{\max}^{\text{out}} + 2 = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} + |V|)$$

For the Bengaluru network:
- **Authoritative Simple Graph Search Space:**
  $$\mathcal{M}_{\text{Bengaluru}}^{\text{actual}} \le 2,087,162 + 740,823 + 740,822 + 308,643 = \mathbf{3,877,450} \text{ logical entries}$$
  Notice: $3,877,450 / 740,822 \approx 5.234 \cdot |E_s|$.
- **Conservative Multigraph Comparison Proxy:**
  $$\mathcal{M}_{\text{Bengaluru}}^{\text{raw\_proxy}} \le 2,103,901 + 740,823 + 740,822 + 308,643 = \mathbf{3,894,189} \text{ logical entries}$$
  Notice: $3,894,189 / 740,822 \approx 5.257 \cdot |E_s|$. This value is retained solely to show the impact if multigraph degree product transitions are substituted into the priority queue push bound.

---

## 6. Revised Four-Tier Complexity Statements and Runtime Provenance

### 6.1 Statement 1: General Directed Graphs (Equation 6)
- **Scope:** Arbitrary directed graphs without bounded degrees, utilizing binary min-heap without `decrease-key`, with on-the-fly parallel edge resolution ($q_{\max}$).
- **Assumptions:** Finite directed graph $G = (V, E_s)$.
- **Mathematical Formulations:**
  $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} + |V|) \text{ logical entries}$$
  $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right) \tag{6}$$
  With $d_{\max} = \max(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$:
  $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max} \log(|E_s| \cdot d_{\max}) + q_{\max} \cdot |E_s| \cdot d_{\max}^2 \right)$$
  - The first term represents priority queue maintenance: at most $\mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}})$ insertions and removals of best and stale states on a min-heap of size $\le \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}})$.
  - The second term represents successor-loop expansions across best and stale duplicate pops ($\mathcal{O}(|E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$ iterations), turn penalty evaluation ($\mathcal{O}(1)$), and dynamic parallel-edge cost scanning ($q(v, w) \le q_{\max}$).

### 6.2 Statement 2: Bounded-Valence Urban Road Networks (Theorem 3)
- **Scope:** Terrestrial urban road networks.
- **Governing Structural Axioms:**
  1. **Assumption A2.1 (Bounded Physical Junction Valence):** $d_{\max}^{\text{in}} = \mathcal{O}(1)$ and $d_{\max}^{\text{out}} = \mathcal{O}(1)$ (in Bengaluru, $d_{\max} \le 6$).
  2. **Assumption A2.2 (Bounded Parallel Edge Multiplicity):** $q_{\max} = \mathcal{O}(1)$ (in Bengaluru, $q_{\max} \le 4$).
- **Mathematical Bound:**
  Under Assumptions A2.1 and A2.2, because $d_{\max} = \mathcal{O}(1)$ and $q_{\max} = \mathcal{O}(1)$, the logarithmic factor simplifies to $\log(|E_s| \cdot \mathcal{O}(1)) = \mathcal{O}(\log |E_s|)$, and the quadratic degree product collapses to $\mathcal{O}(|E_s|)$:
  $$\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|) \text{ logical entries}, \quad \mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$$

### 6.3 Statement 3: Concrete Bengaluru Graph-Wide Bounds

- **Scope:** Worst-case search saturating the entire road network of Bengaluru (`bengaluru_graph.pkl`, $|V| = 308,643, |E_s| = 740,822, d_{\max} = 6, q_{\max} = 4$).
- **Actual Search Space on Effective Simple Graph ($G = (V, E_s)$):**
  - Distinct search states: $|S| = |E_s| + 1 = \mathbf{740,823}$.
  - State transitions: $T_{\text{internal}}^{\text{simple}} = \mathbf{2,087,155}, \; T_{\text{query}}^{\text{simple}} \le 2,087,155 + 6 = \mathbf{2,087,161}$.
  - Maximum heap insertions: $N_{\text{insert}} \le 1 + T_{\text{query}}^{\text{simple}} = \mathbf{2,087,162}$.
  - Maximum heap removals: $N_{\text{remove}} = N_{\text{insert}} \le \mathbf{2,087,162}$.
  - Optimal state pops: $N_{\text{best}} \le |S| = \mathbf{740,823}$.
  - Stale state pops: $E_{\text{stale}} \le 1,346,333 + 6 = \mathbf{1,346,339}$.
  - Successor loop iterations:
    - Best pops: $I_{\text{best}} \le \mathbf{2,087,161}$.
    - Stale pops (via exact degree summation): $I_{\text{stale},\text{exact\_sum}} = 3,799,611 + 20 = \mathbf{3,799,631}$.
    - **Graph-Wide Theoretical Upper Bound (via Exact Degree Summation):**
      $$I_{\text{total},\text{exact\_sum}} = 2,087,161 + 3,799,631 = \mathbf{5,886,792} \text{ iterations}$$
      *(Theoretical saturation bound; not an observed or individual-query count).*
  - Peak auxiliary memory: $\mathcal{M}_{\text{actual}} \le \mathbf{3,877,450} \text{ logical entries}$ ($5.234 \times |E_s|$).
- **Conservative Degree-Based Upper Bounds ($d_{\max}^{\text{out}} = 6$):**
  - Degree-bounded stale loop iterations: $I_{\text{stale}} \le 1,346,339 \times 6 = \mathbf{8,078,034}$.
  - Degree-bounded total iterations on simple graph: $I_{\text{total}} \le 2,087,161 + 8,078,034 = \mathbf{10,165,195}$.
  - Crude global bound ($N_{\text{remove}} \times 6$): $\le 2,087,162 \times 6 = \mathbf{12,522,972}$.
  - Multigraph comparison proxy for memory: $\mathcal{M}_{\text{raw\_proxy}} \le \mathbf{3,894,189} \text{ logical entries}$ ($5.257 \times |E_s|$).

### 6.4 Statement 4: Authoritative Frozen Empirical Runtime Baseline
- **Audit Action:** The unverified numbers previously cited ($117.84\text{ ms}$ mean, $103.7\text{ ms}$ median) have been **completely purged** from this evidence map as they do not exist in the frozen experimental data.
- **Authoritative Ground-Truth Baseline (Condition A0 Production Engine):**
  - **Source Files:** [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv), [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json), [`phase_13_1_stage_2B_full_ablation_report.md#L94`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md#L94).
  - **Sample Configuration:** $N = 25$ representative Bengaluru metropolitan commute corridors, $R = 5$ repetitions per corridor (125 runs total).
  - **Timing Boundary:** In-function CPU execution time of `two_wheeler_astar` via `time.perf_counter()` (excluding disk I/O and graph loading).
  - **Frozen Baseline Metrics:**
    - **Median Execution Latency:** **$174.93\text{ ms}$** (IQR: **$439.08\text{ ms}$**).
    - **Mean Execution Latency:** **$382.98\text{ ms} \pm 464.48\text{ ms}$**.
    - **Observed Range:** **$1.01\text{ ms}$** to **$1,829.18\text{ ms}$**.
  - **Distribution Characteristics:** Heavily right-skewed ($2.19\times$ mean-to-median ratio) due to long-distance commute corridors exploring $\mathcal{O}(R^2)$ search envelopes, methodologically validating non-parametric Wilcoxon analysis and median reporting.
- **Empirical Priority-Queue Pop/Expansion Events (Condition A0 Search Scope):**
  - **Implementation Counter Provenance and Pop Logic:** In [`two_wheeler_astar`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L550-L558), the counter `expanded_states` (initialized at [`L546`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L546)) increments at [`L556`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L556) immediately following `heapq.heappop(open_set)` for every heap pop without filtering stale duplicates. Therefore, figures reported under the CSV column `expanded_states` in [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) measure **empirical priority-queue pop/expansion events** rather than unique states expanded.
  - **Empirical Measurement Range ($N = 25$ Metropolitan Commute Corridors):**
    - **Observed Pop Events Range:** **$119$ to $129,619$ priority-queue pop events** across the 25 evaluated corridors (minimum: $119$ pop events on OD_21, Domlur to Indiranagar, 1.6 km; maximum: $129,619$ pop events on OD_05, Whitefield to Electronic City, 21.6 km).
    - **State-Space Denominator:** $|S| = |E_s| + 1 = \mathbf{740,823}$.
    - **Pop-to-State Ratio:** Bounded by **$0.016\%\text{ to }17.50\%$** when evaluated strictly as the ratio of pop-event counts divided by the theoretical state-space cardinality ($740,823$). These ratios represent pop-event counts normalized by state-space size, not percentages of unique states visited.
  - **Methodological Characterization:** These measurements represent empirical priority-queue pop/expansion events under goal-directed heuristic guidance ($h(s) = 0.80 \cdot D_{\text{haversine}}$), which directs exploration toward the target destination without imposing an artificial geographical boundary. They are strictly distinct from theoretical graph-wide saturation bounds ($|S| = 740,823$ or $I_{\text{total}} \le 5,886,792$).

---

## 7. Master Equation Catalog for Section IV

| Eq# | Formal Mathematical Expression | Context / Purpose | Implementation Grounding |
| :---: | :--- | :--- | :--- |
| **(4)** | $h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t), \quad \mu_{\min} = 0.80$ | Scaled Haversine Heuristic Lower Bound | `routing/algorithms.py#L500-L513` (`MIN_PENALTY_FLOOR = 0.8`) |
| **(5)** | $h(s) \le c(s, s') + h(s')$ | Monotonic Consistency Condition | `routing/algorithms.py#L668-L672` (`new_cost = current_cost + edge_cost + turn_cost`) |
| **(6)** | $\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| d_{\max}^{\text{out}}), \; \mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| d_{\max}^{\text{out}} \log(|E_s| d_{\max}^{\text{out}}) + q_{\max} |E_s| d_{\max}^{\text{in}} d_{\max}^{\text{out}} \right)$ | General Min-Heap Complexity Bounds | Grounded in binary min-heap without `decrease-key`, duplicate pushes, and uncached parallel scanning |

---

## 8. Stop Condition Compliance

This reconciled evidence map establishes mathematical definitions, proofs, and complexity bounds only. In strict accordance with research governance, zero manuscript paragraphs have been drafted. Current file timestamps and byte lengths match the recorded freeze metadata. Current SHA-256 fingerprints have been recorded for future integrity comparisons; historical byte-for-byte identity cannot be independently established from the available freeze records. Phase 8.2 will commence only upon explicit Research Lead review and approval.
