# Section IV Equation and Notation Map — Proposed Turn-Aware Routing Algorithm (v1.0)

**Document:** [`paper1_section_IV_equation_and_notation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_equation_and_notation_map_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1 — Section IV Structural Planning and Mathematical Admissibility Evidence Map  
**Date:** 2026-11-06  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Section III:** [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (Version 1.3)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE MATHEMATICAL NOTATION & EQUATION SPECIFICATION**

---

## 1. Master Notation Glossary for Section IV

All notation strictly extends the foundational definitions established in Section III v1.3 ([`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md)) and aligns with [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py).

### 1.1 State-Space and Priority-Queue Variables

| Symbol | Mathematical Definition | Implementation Variable | Domain / Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| $G$ | Simple directed routing graph $(V, E_s)$ | `graph` | $|V| = 308,643, |E_s| = 740,822$ | Projected simple directed graph after parallel-edge collapse |
| $s$ | Search state: $s = (u, v)$ | `state = (previous_node, current_node)` | $s \in S$ | Directed edge arrival state; $u = \text{tail}(e), v = \text{head}(e)$ |
| $s_0^{\text{state}}$ | Synthetic departure state | `start_state = (None, start_node)` | $(\text{None}, s_0)$ | Initial departure state with no preceding trajectory |
| $S$ | State space | Implicit state space | $S = E_s \cup \{(\text{None}, s_0)\}$ | Total expanded search state space, $|S| = |E_s| + 1 = 740,823$ |
| $s \to s'$ | Directed transition | Loop over `graph.successors(v)` | $(u, v) \to (v, w)$ with $(v, w) \in E_s$ | Transition from incoming segment $(u, v)$ to outgoing segment $(v, w)$ |
| $E_S$ | State transition set | Explored transitions | $E_S \subseteq S \times S$ | Set of valid transitions; $|E_S| = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) d_{\text{out}}(v)$ |
| $g(s)$ | Tentative minimal cost from $s_0^{\text{state}}$ to $s$ | `g_score[state]` | $\mathbb{R}^+$ (effective meters, $m$) | Accumulated traversal and turn cost from origin to state $s$ |
| $h(s)$ | Heuristic estimate from $s$ to destination $t$ | `heuristic(current_node)` | $\mathbb{R}^+$ (effective meters, $m$) | Estimated remaining impedance cost from $\text{head}(s)$ to $t$ |
| $f(s)$ | Evaluation function: $f(s) = g(s) + h(s)$ | `priority` | $\mathbb{R}^+$ (effective meters, $m$) | Priority key value in min-heap |
| $\kappa$ | Unique tie-breaker sequence counter | `next(counter)` (`itertools.count()`) | $\mathbb{N}_0$ | Strictly monotonic integer ensuring FIFO stability on equal $f$-scores |
| $\mathcal{Q}$ | Priority queue min-heap | `open_set` (`heapq` list) | Collection of tuples $(f(s), \kappa, s)$ | Binary min-heap storing active frontier states |
| $\pi(s)$ | Predecessor backpointer | `came_from[state]` | $S$ | Preceding state along minimal discovered approach |

### 1.2 Heuristic and Distance Metrics

| Symbol | Mathematical Definition | Implementation Variable | Domain / Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| $(\phi_v, \lambda_v)$ | Geographic coordinates of node $v$ | `(graph.nodes[v]['y'], graph.nodes[v]['x'])` | Lat/Lon in decimal degrees ($^\circ$) | Spatial position of physical vertex $v$ |
| $D_{\text{haversine}}(v, t)$ | Great-circle chord distance on sphere | `haversine_m(lat_v, lon_v, lat_t, lon_t)` | $\mathbb{R}^+$ (physical meters, $m$) | Haversine distance between node $v$ and target node $t$ ($R = 6,371,000\text{ m}$) |
| $\mu_{\min}$ | Minimum impedance multiplier floor | `MIN_PENALTY_FLOOR` | Constant: $0.80$ ($[-]$) | Lower bound on effective edge impedance multiplier |
| $c(s, s')$ | Transition cost from $s=(u, v)$ to $s'=(v, w)$ | `edge_cost + turn_cost` | $\mathbb{R}^+$ (effective meters, $m$) | Outgoing edge impedance $c_{\min}(v, w)$ plus turn penalty $P_{\text{turn}}(u, v, w)$ |
| $c^*(s, t)$ | Exact optimal cost from $s$ to destination $t$ | Theoretical minimum | $\mathbb{R}^+$ (effective meters, $m$) | Minimal possible accumulated impedance cost from state $s$ to $t$ |

### 1.3 Graph Valence and Complexity Variables

| Symbol | Mathematical Definition | Empirical Value in Bengaluru | Theoretical Order | Description |
| :--- | :--- | :--- | :--- | :--- |
| $d_{\text{in}}(v)$ | In-degree of vertex $v$ | $\min = 0, \max = 6, \text{mean} = 2.41$ | Integer $\ge 0$ | Number of directed edges entering vertex $v$ |
| $d_{\text{out}}(v)$ | Out-degree of vertex $v$ | $\min = 0, \max = 6, \text{mean} = 2.41$ | Integer $\ge 0$ | Number of directed edges exiting vertex $v$ |
| $d_{\max}$ | Maximum physical vertex valence | $6$ | $\mathcal{O}(1)$ | Upper bound on junction in- and out-degrees under physical geometry |
| $\mathcal{M}$ | Space (memory) complexity | Peak heap size | $\mathcal{O}(|E_s|)$ | Maximum memory entries allocated during search |
| $\mathcal{T}$ | Time computational complexity | Elementary heap operations | $\mathcal{O}(|E_s| \log |E_s|)$ | Total execution time under binary min-heap operations |

---

## 2. Monotonic Equation Formulations

Continuing monotonically from Section III v1.3 (Equations 1–3), Section IV introduces Equations (4), (5), and (6).

### Equation (4): Scaled Haversine Heuristic Lower Bound
In Subsection IV-B, the goal-directed heuristic function $h(s)$ evaluated for state $s = (u, v)$ with respect to target destination $t$ is formulated as:

$$h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t), \quad \mu_{\min} = 0.80 \tag{4}$$

where $D_{\text{haversine}}(v, t)$ is the great-circle spatial distance between intersection coordinates $(\phi_v, \lambda_v)$ and $(\phi_t, \lambda_t)$. When $v = t$, $D_{\text{haversine}}(t, t) = 0$, giving $h(s) = 0.0\text{ m}$.

### Equation (5): Conditional Monotonic Consistency Condition
In Subsection IV-C, for any valid directed transition $s = (u, v) \to s' = (v, w)$ where $(v, w) \in E_s$, monotonic consistency requires that the heuristic satisfies the generalized triangle inequality:

$$h(s) \le c(s, s') + h(s') \tag{5}$$

where $c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w)$ is the edge-state transition cost defined in Equation (3).

### Equation (6): General and Valence-Bounded Algorithmic Complexity Bounds
In Subsection IV-D, the worst-case space complexity $\mathcal{M}$ and time complexity $\mathcal{T}$ of the state-expanded search operating with a binary min-heap without `decrease-key` are formulated as:

$$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}}), \quad \mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right) \tag{6}$$

Under bounded physical junction valence (Assumption A2, $d_{\max} = \mathcal{O}(1)$), Equation (6) reduces strictly to $\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|)$ space and $\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$ time.

---

## 3. Formal Mathematical Assertions, Theorems, and Corollaries

### Assumption A1: Graph Multiplier Lower Bound
**Statement:** Across the directed routing graph $G = (V, E_s)$, every effective edge traversal cost satisfies:
$$\mu(e) \ge \mu_{\min} = 0.80 \quad \forall e \in E_s$$
**Empirical Scope:** This condition is empirically verified across all 744,216 directed edge records of the Bengaluru metropolitan road network ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)), where zero edges co-occur with both arterial flyover (`bridge=yes`, $h \in \mathcal{H}_{\text{main}}$) and continuous-flow roundabout (`junction=roundabout`) tags.

---

### Theorem 1: Conditional Admissibility
**Statement:** Under Assumption A1, the scaled Haversine heuristic $h(s)$ defined in Equation (4) is strictly admissible; that is, for every state $s = (u, v) \in S$:
$$h(s) \le c^*(s, t)$$
where $c^*(s, t)$ is the minimal possible accumulated impedance cost from state $s$ to destination $t$.

**Proof:**
1. Let $P^* = \langle s = \sigma_0, \sigma_1, \dots, \sigma_m \rangle$ be an optimal path of directed states from $s = (u, v_0)$ to destination $t$, traversing vertices $v_0, v_1, \dots, v_m$ with $v_0 = v$ and $v_m = t$.
2. By Equation (3), the total accumulated cost of $P^*$ is:
   $$c^*(s, t) = C(P^*) = \sum_{i=1}^m c_{\min}(v_{i-1}, v_i) + \sum_{i=1}^{m-1} P_{\text{turn}}(v_{i-2}, v_{i-1}, v_i)$$
3. By definition, turn penalties are non-negative ($P_{\text{turn}} \ge 0.0\text{ m}$ everywhere). Therefore:
   $$c^*(s, t) \ge \sum_{i=1}^m c_{\min}(v_{i-1}, v_i)$$
4. By definition, $c_{\min}(v_{i-1}, v_i) = \min_{k \in \mathcal{K}} [\mu(v_{i-1}, v_i, k) \cdot \ell(v_{i-1}, v_i, k)]$. Under Assumption A1, $\mu(e) \ge \mu_{\min} = 0.80$ for all edges. Thus:
   $$c_{\min}(v_{i-1}, v_i) \ge \mu_{\min} \cdot \ell_{\min}(v_{i-1}, v_i)$$
5. The physical roadway length $\ell(v_{i-1}, v_i)$ between two intersections is lower-bounded by the great-circle chord distance between their respective spatial coordinates: $\ell(v_{i-1}, v_i) \ge D_{\text{haversine}}(v_{i-1}, v_i)$. Therefore:
   $$c^*(s, t) \ge \mu_{\min} \sum_{i=1}^m D_{\text{haversine}}(v_{i-1}, v_i)$$
6. By the spherical triangle inequality of great-circle arcs on a Riemannian sphere:
   $$\sum_{i=1}^m D_{\text{haversine}}(v_{i-1}, v_i) \ge D_{\text{haversine}}(v_0, v_m) = D_{\text{haversine}}(v, t)$$
7. Substituting back:
   $$c^*(s, t) \ge \mu_{\min} \cdot D_{\text{haversine}}(v, t) = h(s)$$
This proves $h(s) \le c^*(s, t)$, establishing conditional admissibility. $\blacksquare$

---

### Theorem 2: Conditional Monotonic Consistency
**Statement:** Under Assumption A1, the scaled Haversine heuristic $h(s)$ satisfies the monotonicity condition (Equation 5) across every valid directed transition $s = (u, v) \to s' = (v, w)$ in $E_S$:
$$h(s) \le c(s, s') + h(s')$$

**Proof:**
1. Consider state $s = (u, v)$ and successor state $s' = (v, w)$ connected by effective edge $(v, w) \in E_s$.
2. By the spherical triangle inequality on coordinates $(\phi_v, \lambda_v)$, $(\phi_w, \lambda_w)$, and target $(\phi_t, \lambda_t)$:
   $$D_{\text{haversine}}(v, t) \le D_{\text{haversine}}(v, w) + D_{\text{haversine}}(w, t)$$
3. Multiplying both sides by positive scalar $\mu_{\min} = 0.80 > 0$:
   $$\mu_{\min} D_{\text{haversine}}(v, t) \le \mu_{\min} D_{\text{haversine}}(v, w) + \mu_{\min} D_{\text{haversine}}(w, t)$$
4. By definition from Equation (4), $h(s) = \mu_{\min} D_{\text{haversine}}(v, t)$ and $h(s') = \mu_{\min} D_{\text{haversine}}(w, t)$. Thus:
   $$h(s) \le \mu_{\min} D_{\text{haversine}}(v, w) + h(s')$$
5. The physical segment length satisfies $\ell(v, w) \ge D_{\text{haversine}}(v, w)$. Under Assumption A1, $\mu(v, w) \ge \mu_{\min}$. Therefore:
   $$c_{\min}(v, w) \ge \mu_{\min} \ell(v, w) \ge \mu_{\min} D_{\text{haversine}}(v, w)$$
6. Furthermore, transition cost includes turn penalty $c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w)$. Since $P_{\text{turn}}(u, v, w) \ge 0$:
   $$c(s, s') \ge c_{\min}(v, w) \ge \mu_{\min} D_{\text{haversine}}(v, w)$$
7. Substituting this lower bound into Step 4 yields:
   $$h(s) \le c(s, s') + h(s')$$
This proves that $h(s)$ is conditionally monotonic and consistent everywhere on $E_S$. $\blacksquare$

---

### Corollary 1: Optimal State Finality
**Statement:** Because $h(s)$ is monotonically consistent (Theorem 2), the sequence of evaluation values $f(s) = g(s) + h(s)$ of states extracted from the priority queue $\mathcal{Q}$ is monotonically non-decreasing. When any directed edge-state $s = (u, v)$ is extracted from $\mathcal{Q}$ for the first time, its accumulated cost $g(s)$ is strictly optimal ($g(s) = c^*(s_0^{\text{state}}, s)$). Consequently:
1. No state $s = (u, v)$ is ever reopened or updated once extracted.
2. A physical vertex $v$ may be expanded across distinct incoming trajectories up to its in-degree $d_{\text{in}}(v)$, but each discrete directional state $(u, v)$ is finalized at most once.

---

### Assumption A2: Bounded Physical Junction Valence
**Statement:** In terrestrial urban street networks, physical space and safety geometry impose a strict upper bound on the number of intersecting roadways incident to any single physical vertex $v \in V$:
$$\max_{v \in V} \{ d_{\text{in}}(v), d_{\text{out}}(v) \} \le d_{\max} = \mathcal{O}(1)$$
**Empirical Ground Truth:** In the Bengaluru metropolitan graph ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)), $d_{\max} = 6$, and mean degree is $\bar{d} = 2.41$, verifying that vertex valence is strictly bounded by a small constant.

---

### Theorem 3: Algorithmic Complexity Bounds
**Statement:** Let routing operate over simple directed graph $G = (V, E_s)$ using a binary min-heap without `decrease-key`. Under Assumption A2, the state-expanded search achieves worst-case space complexity $\mathcal{M} = \mathcal{O}(|E_s|)$ and time complexity $\mathcal{T} = \mathcal{O}(|E_s| \log |E_s|)$.

**Proof:**
1. **Transition Cardinality:** The number of directed state transitions is:
   $$|E_S| = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v)$$
   Under Assumption A2, $d_{\text{out}}(v) \le d_{\max} = \mathcal{O}(1)$. Factoring out the bound:
   $$|E_S| \le d_{\max} + d_{\max} \sum_{v \in V} d_{\text{in}}(v) = d_{\max} (1 + |E_s|) = \mathcal{O}(|E_s|)$$
   (In Bengaluru, $|E_S| = 2,103,894 \approx 2.84 \cdot |E_s|$).
2. **Space Complexity $\mathcal{M}$:**
   In a binary min-heap without `decrease-key`, a successor state $s' = (v, w)$ is inserted into `open_set` whenever a strictly shorter path to $s'$ is discovered. Since state $(v, w)$ has exactly $d_{\text{in}}(v)$ incoming transitions, it can be pushed at most $d_{\text{in}}(v) \le d_{\max}^{\text{in}}$ times.
   Total heap insertions across all states are bounded by $|E_S| \le |E_s| \cdot d_{\max}^{\text{out}}$.
   The dictionary `g_score` stores at most $|S| = |E_s| + 1$ keys.
   Thus, peak space complexity is:
   $$\mathcal{M} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}}) = \mathcal{O}(|E_s|)$$
3. **Time Complexity $\mathcal{T}$:**
   - Total priority queue insertions: $N_{\text{push}} \le |E_S| = \mathcal{O}(|E_s|)$.
   - Each `heappush` and `heappop` operation on a heap of size $\le N_{\text{push}}$ costs $\mathcal{O}(\log N_{\text{push}}) = \mathcal{O}(\log |E_s|)$ time.
   - Total priority queue extraction cost: $\mathcal{O}(|E_S| \log |E_S|) = \mathcal{O}(|E_s| \log |E_s|)$.
   - Successor examination: When state $(u, v)$ is popped, it iterates through $d_{\text{out}}(v)$ successors. Summed over all extractions (including stale entries), total successor evaluations are at most:
     $$\sum_{s \in \mathcal{Q}_{\text{popped}}} d_{\text{out}}(\text{head}(s)) \le |E_S| \cdot d_{\max}^{\text{out}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}}) = \mathcal{O}(|E_s|)$$
   - Combining heap operations and successor edge evaluations:
     $$\mathcal{T} = \mathcal{O}(|E_s| \log |E_s| + |E_s|) = \mathcal{O}(|E_s| \log |E_s|)$$
This rigorously proves that turn awareness incurs zero asymptotic overhead beyond classical node-based $A^*$ on road networks. $\blacksquare$
