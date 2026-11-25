# Phase 8.1-U Final Consistency Log — Terminology, Mathematical Bound, and Memory Accounting Audit

**Document:** [`phase_8_1_U_final_consistency_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_U_final_consistency_log.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1-U — Final Complexity Evidence Consistency Audit  
**Date:** 2026-11-06  
**Audited Documents:**  
- Mathematical Evidence Map: [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.4 Final Consistent)  
- Implementation Audit: [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) (v1.3 Reconciled and Verified)  
- Prior Verification Logs: [`phase_8_1_T_final_verification_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_T_final_verification_log.md), [`phase_8_1_S_reconciliation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_S_reconciliation_log.md)  
- Frozen Section III: [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (Version 1.3 Canonical Frozen)  
**Implementation Grounding:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py), [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py)  
**Audited Datasets:** [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl), [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv), [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE FINAL CONSISTENCY AUDIT LOG (PHASE 8.1-U COMPLETED)**

---

## 1. Executive Summary & Audit Objectives

Phase 8.1-U was executed to resolve the final four mathematical, terminological, and memory-accounting issues in the Section IV preparation deliverables:
1. **Multigraph Stale-Pop Proxy Audit:** Formally investigate whether $E_{\text{stale\_raw}} \le T_{\text{internal\_raw}} - |E_s| + 6$ can be mathematically proven as a conservative upper bound, determine its validity on general graphs with source vertices, and establish why the authoritative evidence map must anchor strictly on the simple-graph formulation.
2. **Terminology Harmonization:** Review every description of theoretical bounds versus query-level operations. Ensure that the figure $5,886,792$ is never described as an observed or exact individual-query iteration count, but strictly as a **"Graph-Wide Theoretical Upper Bound (via Exact Degree Summation)"** under full-graph search saturation.
3. **Memory Accounting Reconciliation:** Enumerate all persistent per-query data structures in `two_wheeler_astar`, verify the derivation of $3,877,450$ logical entries for the effective simple graph, explain the provenance of $3,894,189$ as a multigraph push comparison proxy, and explicitly confirm that these bounds represent logical entries, not physical memory bytes.
4. **Asymptotic Expression Verification:** Verify that the general complexity expression $\mathcal{T}_{\text{general}}$ correctly accounts for priority queue maintenance (heap pushes/pops of best and stale states) and successor loop expansion with on-the-fly parallel-edge minimization ($q_{\max}$). Prove that quasilinear time and linear memory follow strictly under explicit constant-degree and constant-multiplicity assumptions.

All findings, proofs, and updated catalog definitions are codified herein.

---

## 2. Task 1: Investigation and Formal Rejection of the Multigraph Stale-Pop Proxy

### 2.1 Investigation of the Expression $E_{\text{stale\_raw}} \le T_{\text{internal\_raw}} - |E_s| + 6$
In Phase 8.1-S, an alternative proxy expression was proposed:
$$E_{\text{stale\_raw}} \le T_{\text{internal\_raw}} - |E_s| + 6 = 2,103,894 - 740,822 + 6 = 1,363,078$$

To determine whether this is a mathematically valid conservative upper bound, we inspect its derivation from graph degree definitions:

1. **Cardinally Inconsistent Subtraction:**
   - $T_{\text{internal\_raw}} = \sum_{v \in V} d_{\text{in}}^{\text{raw}}(v) d_{\text{out}}^{\text{raw}}(v) = 2,103,894$ evaluates the product of raw multigraph edge records.
   - $|E_s| = 740,822$ is the cardinality of simple directed edges on $G = (V, E_s)$.
   - The expression subtracts simple directed edges from multigraph edge record pairs. If evaluated consistently on the multigraph:
     $$\sum_{u \in V} d_{\text{out}}^{\text{raw}}(u)(d_{\text{in}}^{\text{raw}}(u) - 1) = T_{\text{internal\_raw}} - |E_{\text{raw}}| = 2,103,894 - 744,216 = 1,359,678$$
     The figure $1,363,078$ was an ad-hoc hybrid created by substituting $|E_s|$ instead of $|E_{\text{raw}}|$ (a difference of $3,394$ parallel edge records).

2. **Mathematical Failure on General Graphs with Source Vertices:**
   - Consider the identity:
     $$\sum_{u \in V} d_{\text{out}}(u)(d_{\text{in}}(u) - 1) = \sum_{u \in V} d_{\text{in}}(u) d_{\text{out}}(u) - \sum_{u \in V} d_{\text{out}}(u) = T_{\text{internal}} - |E|$$
   - The true stale-pop upper bound derived from state reachability contains the non-negative truncation operator:
     $$\sum_{u \in V} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0)$$
   - On general directed graphs containing source vertices ($u \in V$ such that $d_{\text{in}}(u) = 0$ but $d_{\text{out}}(u) > 0$):
     $$\max(d_{\text{in}}(u) - 1, 0) = \max(0 - 1, 0) = 0$$
     However, the unclamped term evaluates to:
     $$d_{\text{out}}(u)(d_{\text{in}}(u) - 1) = d_{\text{out}}(u)(0 - 1) = -d_{\text{out}}(u) < 0$$
   - When summing across all vertices, source vertices contribute unphysical negative values, causing $T_{\text{internal}} - |E|$ to be strictly **smaller** than the true stale bound:
     $$\sum_{u \in V} d_{\text{out}}(u)(d_{\text{in}}(u) - 1) = \sum_{u \in V} d_{\text{out}}(u) \max(d_{\text{in}}(u) - 1, 0) - \sum_{u: d_{\text{in}}(u)=0} d_{\text{out}}(u)$$
   - Therefore, $T_{\text{internal}} - |E|$ is **not a valid conservative upper bound** across general directed graphs.
   - While on the specific Bengaluru dataset there happen to be zero source vertices ($d_{\text{in}}(u) \ge 1$ for all nodes with $d_{\text{out}}(u) > 0$), an algebraic formula cannot be adopted into formal proof text if its validity relies on coincidental absence of source nodes while using an inconsistent cardinality mix.

3. **Algorithmic Disconnect:**
   - Because `two_wheeler_astar` collapses parallel edges on-the-fly and keys search states strictly by vertex pairs $(u, v) \in E_s$, multigraph edge records never materialize as independent search states or priority queue entries.

### 2.2 Formal Audit Decision
* **Action:** The proxy $E_{\text{stale\_raw}} \le 1,363,078$ and its derived loop iteration bound ($10,282,368$) are **formally removed** from the Section IV mathematical evidence map and implementation audit.
* **Authoritative Grounding:** The stale-pop bound is anchored strictly and exclusively on the proven simple-graph reachability formulation:
  $$E_{\text{stale}} \le \sum_{u \in V} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0) + d_{\text{out}}(s_0) \cdot \mathbb{I}(d_{\text{in}}(s_0) \ge 1) \le 1,346,333 + 6 = \mathbf{1,346,339}$$
* **Retention of $2,103,894$:** The multigraph transition count $T_{\text{internal}}^{\text{raw}} = 2,103,894$ is retained strictly as a historical conservative topological comparison ($2,103,894 \ge 2,087,155$), showing that previous Section III multigraph figures provide an upper bound on topological transitions without affecting the algorithm's actual search state space.

---

## 3. Task 2: Terminology Harmonization and Conceptual Demarcation

To prevent misinterpreting theoretical graph-wide bounds as operational runtime counts, the terminology across all deliverables is codified into four rigorous categories:

### Category A: Exact Graph-Derived Topological Degree Sums
Direct mathematical summations over the adjacency structure of $G = (V, E_s)$ in `bengaluru_graph.pkl`:
- In-degree sum: $\sum_v d_{\text{in}}(v) = |E_s| = \mathbf{740,822}$
- Out-degree sum: $\sum_v d_{\text{out}}(v) = |E_s| = \mathbf{740,822}$
- Simple internal transitions: $\sum_v d_{\text{in}}(v) d_{\text{out}}(v) = \mathbf{2,087,155}$
- Simple stale-pop base sum: $\sum_u d_{\text{out}}(u) \max(d_{\text{in}}(u)-1, 0) = \mathbf{1,346,333}$
- Stale successor iteration base sum: $\sum_u \max(d_{\text{in}}(u)-1, 0) \sum_{v \in \text{succ}(u)} d_{\text{out}}(v) = \mathbf{3,799,611}$
- Origin worst-case iteration adjustment: $\max_{s_0: d_{\text{in}}(s_0) \ge 1} \sum_{v \in \text{succ}(s_0)} d_{\text{out}}(v) = \mathbf{20}$ (at node `2246770321`)

### Category B: Graph-Wide Theoretical Upper Bounds (via Exact Degree Summation)
Theoretical bounds representing worst-case search saturation if a query expanded every reachable state and exhausted all possible stale duplicate pops across the entire metropolitan network:
- Query transitions: $T_{\text{query}}^{\text{simple}} \le 2,087,155 + 6 = \mathbf{2,087,161}$
- Stale state extractions: $E_{\text{stale}} \le 1,346,333 + 6 = \mathbf{1,346,339}$
- Total successor-loop iterations:
  $$I_{\text{total},\text{exact\_sum}} = 2,087,161 + 3,799,631 = \mathbf{5,886,792} \text{ iterations}$$
- Peak auxiliary memory: $\mathcal{M}_{\text{actual}} \le \mathbf{3,877,450} \text{ logical entries}$

> [!WARNING]
> **Strict Semantic Mandate on $5,886,792$:**  
> The figure $5,886,792$ must **NEVER** be described as an "observed count", an "actual count", or the iterations of an individual query. It is a **theoretical graph-wide upper bound** derived from exact degree summation under hypothetical full-network saturation.

### Category C: Conservative Degree-Based Upper Bounds
Coarse closed-form bounds obtained by replacing individual vertex degrees with network maximum out-degree ($d_{\max}^{\text{out}} = 6$):
- Stale loop iterations: $I_{\text{stale}} \le 1,346,339 \times 6 = \mathbf{8,078,034}$
- Total loop iterations: $I_{\text{total}} \le 2,087,161 + 8,078,034 = \mathbf{10,165,195}$
- Crude global bound ($N_{\text{remove}} \times 6$): $(1 + 2,087,161) \times 6 = \mathbf{12,522,972}$

### Category D: Actual Individual-Query Operations in Practice
Operations executed during real-world origin-destination queries:
- Goal-directed A* with heuristic $h(s) = 0.80 \cdot D_{\text{haversine}}$ evaluates states directed toward the destination, expanding only a subset of the graph rather than saturating the entire metropolitan network. This goal-directed pruning avoids exploring the full state space without imposing an artificial geographical search boundary.
- **Empirical Query-Level Priority-Queue Pop Events (Condition A0 Production Engine):**
  - **Queue-Pop Mechanism & Counter Provenance:** In [`two_wheeler_astar`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L550-L558), the counter `expanded_states` increments at line 556 immediately upon popping an element via `heapq.heappop(open_set)` for every heap pop, including stale duplicate entries. Therefore, figures reported under the CSV column `expanded_states` in [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) measure **empirical priority-queue pop/expansion events** rather than unique states expanded.
  - Across the $25$ evaluated metropolitan corridors:
    - Observed pop events range: **$119\text{ to }129,619$ priority-queue pop events** (minimum: $119$ pop events on OD_21, Domlur to Indiranagar, 1.6 km; maximum: $129,619$ pop events on OD_05, Whitefield to Electronic City, 21.6 km).
    - State-space denominator: **$|S| = 740,823$**.
    - Pop-to-state ratio range: **$0.016\%\text{ to }17.50\%$**, defined strictly as pop-event counts divided by the theoretical state-space cardinality ($740,823$). These ratios do not represent percentages of unique states visited.
  - These measurements reflect individual query-level exploration under heuristic guidance, strictly distinct from theoretical graph-wide saturation bounds.
- The practical operational latency is empirically characterized by the frozen Condition A0 baseline: **$174.93\text{ ms}$ median**, **$382.98\text{ ms}$ mean** ($N = 25, R = 5$, range $1.01\text{--}1,829.18\text{ ms}$).

---

## 4. Task 3: Memory Reconciliation (Logical Entries vs. Measured Bytes)

### 4.1 Exhaustive Enumeration of Persistent Per-Query Structures
A line-by-line inspection of [`two_wheeler_astar`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L460-L705) identifies exactly five persistent structures allocated during search execution:

1. `open_set` ([`L535`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L535)):
   - Type: Python `list` organized as a binary min-heap via `heapq`.
   - Stored element: 3-tuple `(priority, counter, state)`.
   - Maximum elements present at any time cannot exceed total heap pushes $N_{\text{insert}}$.
   - $N_{\text{insert}} = 1 + R_{\text{actual}} \le 1 + T_{\text{query}}^{\text{simple}} \le \mathbf{2,087,162}$ logical entries.
2. `g_score` ([`L527`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L527)):
   - Type: Python `dict` mapping `state` tuple `(prev_node, curr_node)` to `float` cost.
   - Keyed by reachable directed edge states $S = E_s \cup \{(\text{None}, s_0)\}$.
   - Maximum elements: $|S| = |E_s| + 1 = \mathbf{740,823}$ logical entries.
3. `came_from` ([`L531`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L531)):
   - Type: Python `dict` mapping `next_state` tuple to predecessor `state` tuple.
   - The synthetic root $(\text{None}, s_0)$ is never a `next_state`. Only edge states $(u, v) \in E_s$ are inserted.
   - Maximum elements: $|E_s| = \mathbf{740,822}$ logical entries.
4. `visited_nodes` ([`L547`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L547)):
   - Type: Python `set` storing physical node integer IDs `current_node`.
   - Updated at line 558: `visited_nodes.add(current_node)`.
   - Maximum elements: bounded by total physical intersections $|V| = \mathbf{308,643}$ logical entries.
5. Scalar Tracking Counters ([`L533-L548`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L533-L548)):
   - Variables: `expanded_states` (`int`), `explored_transitions` (`int`), `start_time` (`float`), `counter` (`itertools.count`).
   - $\mathcal{O}(1)$ primitive scalars that do not scale with graph size.

Temporary path reconstruction structures (`states = []`, `route = []`, `deduped_route = []`) are allocated only upon goal termination, storing $\mathcal{O}(k)$ entries ($k \ll |V|$ path length), and do not scale with graph saturation.

### 4.2 Derivation of Logical-Entry Bounds
- **Authoritative Simple-Graph Bound ($3,877,450$ entries):**
  $$\mathcal{M}_{\text{actual}} \le |\text{open\_set}|_{\max} + |\text{g\_score}|_{\max} + |\text{came\_from}|_{\max} + |\text{visited\_nodes}|_{\max}$$
  $$\mathcal{M}_{\text{actual}} \le 2,087,162 + 740,823 + 740,822 + 308,643 = \mathbf{3,877,450} \text{ logical entries}$$
  Normalized: $3,877,450 / 740,822 \approx 5.234 \times |E_s|$.
- **Multigraph Comparison Alternative ($3,894,189$ entries):**
  $$\mathcal{M}_{\text{raw\_proxy}} \le 2,103,901 + 740,823 + 740,822 + 308,643 = \mathbf{3,894,189} \text{ logical entries}$$
  Normalized: $3,894,189 / 740,822 \approx 5.257 \cdot |E_s|$.
  This figure arose solely by substituting $N_{\text{insert}} \le 1 + T_{\text{raw}} = 2,103,901$ into `open_set`.

### 4.3 Confirmation of Logical Entries vs. Measured Bytes
Both $3,877,450$ and $3,894,189$ are strictly counts of **stored logical elements** (heap tuples, dictionary key-value entries, and set integer members). They are **not measured RAM bytes**. In 64-bit CPython:
- A Python tuple `(float, int, tuple)` occupies $\sim 64\text{ bytes}$ plus child objects.
- A dict key-value entry occupies $\sim 24\text{--}48\text{ bytes}$ in compact dict hash tables.
- A set entry occupies $\sim 8\text{ bytes}$ in hash buckets plus integer objects.
Actual RAM footprint scales as $\mathcal{O}(\mathcal{M}_{\text{logical}}) = \mathcal{O}(|E_s|)$ on bounded-valence road networks, confirming linear auxiliary space.

---

## 5. Task 4: Final Asymptotic Complexity Expression Verification

### 5.1 General Directed Graphs (Unbounded Valence, Equation 6)
On arbitrary directed graphs $G = (V, E_s)$ with arbitrary degrees and parallel multiplicity $q_{\max}$:
$$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} + |V|) \text{ logical entries}$$
$$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right) \tag{6}$$
Setting $d_{\max} = \max(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$:
$$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max} \log(|E_s| \cdot d_{\max}) + q_{\max} \cdot |E_s| \cdot d_{\max}^2 \right)$$

**Verification of Component Terms:**
1. **Priority Queue Maintenance:** At most $N_{\text{insert}} \le |E_s| \cdot d_{\max}^{\text{out}} + d_{\max}^{\text{out}}$ pushes and pops of best and stale states. Each binary min-heap operation on a heap of size $\le N_{\text{insert}}$ takes $\mathcal{O}(\log(|E_s| \cdot d_{\max}^{\text{out}}))$. Total heap cost: $\mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}))$.
2. **Successor Loop Iterations:** Each state popped (best or stale) executes up to $d_{\max}^{\text{out}}$ iterations. With at most $\mathcal{O}(|E_s| \cdot d_{\max}^{\text{in}})$ stale pops, total loop iterations are $\mathcal{O}(|E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$.
3. **Turn Penalty Computation:** Inside each iteration, angle and bearing calculations execute in $\mathcal{O}(1)$ time.
4. **Dynamic Parallel-Edge Minimization:** Inside each iteration, `edge_data.values()` is scanned dynamically across $q(v, w) \le q_{\max}$ candidates in $\mathcal{O}(q_{\max})$ operations. Total scanning overhead: $\mathcal{O}(q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$.

### 5.2 Bounded-Valence Urban Road Networks (Theorem 3)
The linear-space and quasilinear-time conclusions follow **strictly under explicit structural axioms**:
- **Assumption A2.1 (Bounded Physical Junction Valence):**  
  $$d_{\max}^{\text{in}} = \mathcal{O}(1), \quad d_{\max}^{\text{out}} = \mathcal{O}(1)$$
  (Empirically verified in Bengaluru: $d_{\max}^{\text{in}} \le 6, d_{\max}^{\text{out}} \le 6$).
- **Assumption A2.2 (Bounded Parallel Edge Multiplicity):**  
  $$q_{\max} = \mathcal{O}(1)$$
  (Empirically verified in Bengaluru: $q_{\max} = 4$).

Under Assumptions A2.1 and A2.2:
- $\log(|E_s| \cdot d_{\max}^{\text{out}}) = \log |E_s| + \mathcal{O}(1) = \mathcal{O}(\log |E_s|)$.
- $|E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) = \mathcal{O}(|E_s| \log |E_s|)$.
- $q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} = \mathcal{O}(|E_s|)$.
- Auxiliary memory: $|E_s| \cdot d_{\max}^{\text{out}} + |V| = \mathcal{O}(|E_s|)$.

Therefore:
$$\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|), \quad \mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|)$$
This mathematically proves that the bounded-valence conclusion holds if and only if junction degree and parallel multiplicity are bounded by constants.

---

## 6. Deliverables Verification Matrix

| Phase 8.1 Deliverable | File Path | Status | Verification Summary |
| :--- | :--- | :---: | :--- |
| **Mathematical Evidence Map** | [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) | v1.4 Final Consistent | Purged invalid $1,363,078$ and $10,282,368$ proxies. Corrected terminology for $5,886,792$ graph-wide bound. Anchored memory to $3,877,450$ logical entries. Rigorous multi-tier asymptotic formulations. |
| **Implementation Audit** | [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) | v1.3 Reconciled and Verified | Enumerated all persistent per-query structures. Reconciled logical entries vs. bytes. Updated successor iteration bounds and crude global bound ($12,522,972$). |
| **Consistency Log** | [`phase_8_1_U_final_consistency_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_U_final_consistency_log.md) | Current File | Authoritative record of Phase 8.1-U audit resolutions, mathematical proofs of proxy rejection, terminology demarcation, and memory accounting. |

---

## 7. Strict Stop Condition Compliance

In strict compliance with research governance constraints:
- **Zero manuscript paragraphs have been drafted for Section IV.**
- **No changes have been made to frozen manuscript files** (`paper1_abstract_v2.md`, `paper1_introduction_v1.md`, `paper1_related_work_v1.md`, `paper1_section_III_v1.md`). Current file timestamps and byte lengths match the recorded freeze metadata. Current SHA-256 fingerprints have been recorded for future integrity comparisons; historical byte-for-byte identity cannot be independently established from the available freeze records. Recorded current fingerprints and historical metadata values:
  - `paper1_abstract_v2.md`: `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` (3,287 bytes, frozen 05-11-2026 21:28:52)
  - `paper1_introduction_v1.md`: `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` (7,596 bytes, frozen 05-11-2026 23:04:07)
  - `paper1_related_work_v1.md`: `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` (6,723 bytes, frozen 06-11-2026 00:46:14)
  - `paper1_section_III_v1.md`: `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` (10,963 bytes, frozen 06-11-2026 01:34:46)
- **No changes have been made to structural blueprint, bibliography, or outline files.**
- **No source code or graph datasets have been modified.**
- **No new evaluation experiments were run.**
- **Phase 8.2 (Section IV Manuscript Drafting) will NOT begin until explicit Research Lead authorization is granted.**
