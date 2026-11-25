# Phase 8.1-T Final Verification Log — Graph-Specific Complexity Verification and Multi-Tier Formulation

**Document:** [`phase_8_1_T_final_verification_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_T_final_verification_log.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1-T — Final Graph-Specific Complexity Verification  
**Date:** 2026-11-06  
**Audited Documents:**  
- Mathematical Evidence Map: [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.3 Reconciled and Verified)  
- Implementation Audit: [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) (v1.2 Reconciled and Verified)  
- Prior Reconciliation Log: [`phase_8_1_S_reconciliation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_S_reconciliation_log.md)  
- Frozen Section III: [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (Version 1.3 Canonical Frozen)  
**Implementation Grounding:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py), [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py)  
**Audited Datasets:** [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl), [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv), [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE FINAL VERIFICATION LOG (PHASE 8.1-T COMPLETED)**

---

## 1. Executive Summary & Verification Objectives

Phase 8.1-T was initiated to complete the final rigorous verification of graph-specific complexity figures for Section IV of Paper 1, addressing five specific research engineering requirements:
1. **Verify Effective Graph Degree Statistics:** Directly inspect the pickled metropolitan graph (`bengaluru_graph.pkl`) to compute exact degrees, Handshaking sums, transitions, and stale-pop base sums on the effective simple graph, verifying that this graph matches the successor iteration and parallel-edge collapse in `two_wheeler_astar`.
2. **Reconcile Transition Counts:** Determine the exact relationship between the simple directed graph internal transition count ($2,087,155$) and the earlier multigraph-based count ($2,103,894$). Prove whether the latter is an exact multigraph count, a conservative upper bound, or an error, and ensure multigraph counts are never misattributed as actual algorithm state transitions.
3. **Verify Stale-Pop and Successor-Loop Counts:** Re-calculate $E_{\text{stale}}$, $I_{\text{best}}$, $I_{\text{stale}}$, $I_{\text{total}}$, $N_{\text{insert}}$, and $N_{\text{remove}}$. Provide a rigorous, code-grounded proof of the origin extra term ($+20$) reported in the exact stale-loop summation ($3,799,611 + 20 = 3,799,631$).
4. **Verify Parallel-Edge Scanning Overhead:** Confirm $q_{\max} = 4$, document the empirical multiplicity distribution, verify the lack of caching/memoization, and prove that multiplicity is applied to the correct iteration bound.
5. **Codify Multi-Tier Complexity Recommendations:** Provide distinct, unambiguous expressions for (a) actual effective simple-graph search, (b) conservative degree-based upper bound, (c) general directed graphs, and (d) authoritative empirical runtime baseline.

All verifications were executed by direct in-memory inspection of `bengaluru_graph.pkl` and line-by-line tracing of `routing/algorithms.py`.

---

## 2. Task 1: Effective Graph Degree Statistics Verification

### 2.1 Direct In-Memory Inspection of `bengaluru_graph.pkl`
The serialized road network in `bengaluru_graph.pkl` is an instance of NetworkX `MultiDiGraph`. An exhaustive in-memory traversal of `_succ`, `_pred`, and `_node` was performed using Python 3.14 to extract topological statistics.

| Topological Metric | Mathematical Definition | Computed Value | Verification Status |
| :--- | :---: | :---: | :---: |
| **Physical Vertices ($|V|$)** | $\sum_{v \in V} 1$ | **$308,643$** | Verified exact |
| **Raw Multigraph Records ($|E_{\text{raw}}|$)** | $\sum_{u \in V} \sum_{v \in \text{succ}(u)} \|\mathcal{K}(u, v)\|$ | **$744,216$** | Verified exact |
| **Effective Simple Edges ($|E_s|$)** | $\sum_{u \in V} \|\text{succ}(u)\|$ | **$740,822$** | Verified exact |
| **Parallel Pairs** | $\|\{(u, v) : \|\mathcal{K}(u, v)\| > 1\}\|$ | **$3,379$** | Verified exact |
| **Excess Multigraph Records** | $|E_{\text{raw}}| - |E_s|$ | **$3,394$** | Verified exact |
| **Sum of Simple In-Degrees** | $\sum_{v \in V} d_{\text{in}}^{\text{simple}}(v)$ | **$740,822$** | Verified exact ($= |E_s|$) |
| **Sum of Simple Out-Degrees** | $\sum_{v \in V} d_{\text{out}}^{\text{simple}}(v)$ | **$740,822$** | Verified exact ($= |E_s|$) |
| **Maximum Simple In-Degree ($d_{\max}^{\text{in}}$)** | $\max_{v \in V} d_{\text{in}}^{\text{simple}}(v)$ | **$6$** | Verified exact |
| **Maximum Simple Out-Degree ($d_{\max}^{\text{out}}$)** | $\max_{v \in V} d_{\text{out}}^{\text{simple}}(v)$ | **$6$** | Verified exact |
| **Simple Internal Transitions** | $\sum_{v \in V} d_{\text{in}}^{\text{simple}}(v) \cdot d_{\text{out}}^{\text{simple}}(v)$ | **$2,087,155$** | Verified exact |
| **Simple Stale-Pop Base Sum** | $\sum_{u \in V} d_{\text{out}}^{\text{simple}}(u) \cdot \max(d_{\text{in}}^{\text{simple}}(u) - 1, 0)$ | **$1,346,333$** | Verified exact |

### 2.2 Proof of Algorithmic Alignment with Simple Graph $G = (V, E_s)$
In [`routing/algorithms.py#L607-L656`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L607-L656):
```python
for next_node in graph.successors(current_node):
    edge_data = graph.get_edge_data(current_node, next_node)
    if "length" in edge_data:
        edge_cost = two_wheeler_edge_cost(edge_data, ...)
    else:
        edge_cost = min(
            two_wheeler_edge_cost(data, ...)
            for data in edge_data.values()
        )
```
1. **Successor Expansion:** In NetworkX, `graph.successors(current_node)` yields the keys of dictionary `graph._succ[current_node]`. Even though `graph` is a `MultiDiGraph`, the keys of `_succ[current_node]` are unique successor vertices $w$. Each distinct neighbor is visited **exactly once** per successor loop.
2. **Parallel Edge Collapse:** Inside the loop, `get_edge_data(current_node, next_node)` retrieves all multigraph edge records $\mathcal{K}(\text{current\_node}, \text{next\_node})$. The `else` branch evaluates `two_wheeler_edge_cost` for each candidate record and collapses them to their minimum impedance representative:
   $$c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} \left[ \mu(u, v, k) \cdot \ell(u, v, k) \right]$$
3. **State Representation:** Directed edge-states are keyed by tuples `(previous_node, current_node)` without multigraph edge key $k$.
4. **Conclusion:** The state space explored by `two_wheeler_astar` is strictly isomorphic to the simple directed graph $G = (V, E_s)$, with state cardinality $|S| = |E_s| + 1 = 740,823$. Best pops execute exactly $|E_s|$ successor iterations, not $|E_{\text{raw}}|$.

---

## 3. Task 2: Reconciliation of Transition Counts ($2,087,155$ vs. $2,103,894$)

### 3.1 Mathematical Genesis of the Discrepancy
- **Simple Directed Graph Internal Transitions:**
  $$T_{\text{internal}}^{\text{simple}} = \sum_{v \in V} d_{\text{in}}^{\text{simple}}(v) \cdot d_{\text{out}}^{\text{simple}}(v) = \mathbf{2,087,155}$$
- **Raw Multigraph Internal Degree Product:**
  $$T_{\text{internal}}^{\text{raw}} = \sum_{v \in V} d_{\text{in}}^{\text{raw}}(v) \cdot d_{\text{out}}^{\text{raw}}(v) = \mathbf{2,103,894}$$
- **Difference:**
  $$\Delta T = T_{\text{internal}}^{\text{raw}} - T_{\text{internal}}^{\text{simple}} = 2,103,894 - 2,087,155 = \mathbf{16,739}$$

### 3.2 Formal Status of $2,103,894$
An audit of Phase 3.4, Phase 3.6, and Section III v1.3 demonstrates how $2,103,894$ was generated:
1. In NetworkX, calling `graph.in_degree(v)` and `graph.out_degree(v)` on a `MultiDiGraph` counts the total number of incoming and outgoing edge records (including parallel multigraph keys), returning $d^{\text{raw}}(v)$.
2. Evaluating $\sum_v \text{in\_degree}(v) \times \text{out\_degree}(v)$ across all nodes yielded $2,103,894$.
3. **Is it an exact count?** YES. It is the exact number of pairs of incoming and outgoing multigraph edge records traversing each vertex on $G_{\text{raw}}$. If parallel edges had been materialized as separate search states $(u, v, k_1)$ and $(u, v, k_2)$, there would have been exactly $2,103,894$ transitions.
4. **Is it a valid conservative upper bound?** YES. Because $d_{\text{in}}^{\text{raw}}(v) \ge d_{\text{in}}^{\text{simple}}(v)$ and $d_{\text{out}}^{\text{raw}}(v) \ge d_{\text{out}}^{\text{simple}}(v)$ for all $v \in V$, $T_{\text{internal}}^{\text{raw}} \ge T_{\text{internal}}^{\text{simple}}$ unconditionally. Any complexity bound derived from $2,103,894$ is mathematically sound and conservative.
5. **Is it the actual algorithm transition count?** **NO.** Because `two_wheeler_astar` collapses parallel edges on-the-fly and keys states by vertex pairs $(u, v) \in E_s$, the algorithm never explores parallel transitions. The actual internal transition count of the algorithm is strictly **$2,087,155$**.

---

## 4. Task 3: Stale-Pop and Successor-Loop Counts Verification

### 4.1 Stale-Pop Upper Bound ($E_{\text{stale}}$)
The governing formula derived in Phase 8.1-S is:
$$E_{\text{stale}} \le d_{\text{out}}(s_0) \cdot d_{\text{in}}(s_0) + \sum_{u \ne s_0} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0)$$
Algebraically rewriting across all $u \in V$:
$$E_{\text{stale}} \le \sum_{u \in V} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0) + d_{\text{out}}(s_0) \cdot \mathbb{I}(d_{\text{in}}(s_0) \ge 1)$$

- **Simple Graph Base Sum:** $\sum_{u \in V} d_{\text{out}}(u) \max(d_{\text{in}}(u) - 1, 0) = \mathbf{1,346,333}$.
- **Origin Adjustment:** For any node $s_0$, $d_{\text{out}}(s_0) \le 6$ and $\mathbb{I}(d_{\text{in}}(s_0) \ge 1) \le 1$. In `bengaluru_graph.pkl`, multiple nodes achieve $d_{\text{out}} = 6$ with $d_{\text{in}} = 6$ (e.g., node $432841717$). Thus, $\max_{s_0} [d_{\text{out}}(s_0) \mathbb{I}(d_{\text{in}}(s_0) \ge 1)] = 6$.
- **Exact Simple Graph Bound:**
  $$E_{\text{stale}}^{\text{simple}} \le 1,346,333 + 6 = \mathbf{1,346,339}$$
- **Conservative Multigraph Proxy Bound:**
  $$E_{\text{stale}}^{\text{raw}} \le 2,103,894 - 740,822 + 6 = \mathbf{1,363,078}$$

### 4.2 Exact Successor-Loop Breakdown and Origin $+20$ Provenance
When state $(u, v)$ is popped (whether best or stale), if $v \ne \text{end\_node}$, it iterates through all $d_{\text{out}}(v)$ successors.

1. **Best Successor Iterations ($I_{\text{best}}$):**
   $$I_{\text{best}} = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) d_{\text{out}}(v) = T_{\text{query}}^{\text{simple}} \le 2,087,155 + 6 = \mathbf{2,087,161}$$
2. **Stale Successor Iterations ($I_{\text{stale}}$) — Full Proof of $3,799,611 + 20$:**
   Each state $(u, v)$ has at most $\max(d_{\text{in}}(u)-1, 0)$ stale pops (for $u \ne s_0$). When popped, it executes $d_{\text{out}}(v)$ iterations. Summing over all $v \in \text{succ}(u)$:
   $$\text{Iterations from stale pops of outgoing edges of } u \le \max(d_{\text{in}}(u)-1, 0) \sum_{v \in \text{succ}(u)} d_{\text{out}}(v)$$
   - **Base Network Sum:** Summing across all $u \in V$ on `bengaluru_graph.pkl`:
     $$\sum_{u \in V} \max(d_{\text{in}}(u)-1, 0) \sum_{v \in \text{succ}(u)} d_{\text{out}}(v) = \mathbf{3,799,611}$$
   - **Origin Additional Stale Loop Iterations ($+20$):**  
     For origin $s_0$, outgoing state $(s_0, v)$ can be inserted from $(\text{None}, s_0)$ plus up to $d_{\text{in}}(s_0)$ incoming cycle edges. When $d_{\text{in}}(s_0) \ge 1$, $(s_0, v)$ has $d_{\text{in}}(s_0)$ stale pops rather than $\max(d_{\text{in}}(s_0)-1, 0)$, yielding **1 extra stale pop** per outgoing edge $(s_0, v)$.  
     Each extra stale pop of $(s_0, v)$ executes $d_{\text{out}}(v)$ loop iterations.  
     Therefore, the extra loop iterations contributed by origin $s_0$ are:
     $$\Delta I_{\text{origin}}(s_0) = \mathbb{I}(d_{\text{in}}(s_0) \ge 1) \sum_{v \in \text{succ}(s_0)} d_{\text{out}}(v)$$
     An exhaustive search over all $308,643$ nodes in `bengaluru_graph.pkl` reveals:
     - The maximum value of $\sum_{v \in \text{succ}(s_0)} d_{\text{out}}(v)$ among all nodes with $d_{\text{in}}(s_0) \ge 1$ occurs at **node ID `2246770321`**.
     - Node `2246770321` has $d_{\text{out}} = 6$ and $d_{\text{in}} = 6$.
     - Its 6 successor vertices have out-degrees: $[3, 3, 3, 3, 3, 5]$.
     - Sum of successor out-degrees: $3 + 3 + 3 + 3 + 3 + 5 = \mathbf{20}$.
     - Thus, $\max_{s_0} \Delta I_{\text{origin}}(s_0) = \mathbf{20}$.
   - **Exact Stale Loop Iteration Bound:**
     $$I_{\text{stale},\text{exact}} = 3,799,611 + 20 = \mathbf{3,799,631}$$
3. **Total Exact Successor-Loop Iterations:**
   $$I_{\text{total},\text{exact}} = I_{\text{best}} + I_{\text{stale},\text{exact}} \le 2,087,161 + 3,799,631 = \mathbf{5,886,792}$$

### 4.3 Comparison with Degree-Bounded and Multigraph Proxies

| Iteration / Operation Metric | Simple Graph (Exact Sum) | Simple Graph ($d_{\max}^{\text{out}} = 6$) | Multigraph Proxy Bound | Crude Global Bound ($N_{\text{remove}} \times 6$) |
| :--- | :---: | :---: | :---: | :---: |
| **Best Iterations ($I_{\text{best}}$)** | $\le 2,087,161$ | $\le 2,087,161$ | $\le 2,103,900$ | — |
| **Stale Iterations ($I_{\text{stale}}$)** | $\mathbf{3,799,631}$ | $\le 8,078,034$ | $\le 8,178,468$ | — |
| **Total Iterations ($I_{\text{total}}$)** | $\mathbf{5,886,792}$ | $\le \mathbf{10,165,195}$ | $\le \mathbf{10,282,368}$ | $\le \mathbf{12,623,406}$ |
| **Heap Insertions ($N_{\text{insert}}$)** | $\le \mathbf{2,087,162}$ | $\le 2,087,162$ | $\le 2,103,901$ | $\le 2,103,901$ |
| **Heap Removals ($N_{\text{remove}}$)** | $\le \mathbf{2,087,162}$ | $\le 2,087,162$ | $\le 2,103,901$ | $\le 2,103,901$ |
| **Peak Logical Memory ($\mathcal{M}$)** | $\le \mathbf{3,877,450}$ entries | $\le 3,877,450$ entries | $\le 3,894,189$ entries | $\le 3,894,189$ entries |

---

## 5. Task 4: Parallel-Edge Scanning Verification

### 5.1 Multiplicity Grounding in `bengaluru_graph.pkl`
An exhaustive census of edge multiplicities between adjacent vertex pairs in `bengaluru_graph.pkl` confirms:

| Multiplicity ($q$) | Ordered Vertex Pairs | Percentage of Pairs | Total Multigraph Edge Records | Excess Records ($q - 1$) |
| :---: | :---: | :---: | :---: | :---: |
| $q = 1$ | $737,443$ | $99.544\%$ | $737,443$ | $0$ |
| $q = 2$ | $3,365$ | $0.454\%$ | $6,730$ | $3,365$ |
| $q = 3$ | $13$ | $0.0018\%$ | $39$ | $26$ |
| $q = 4$ | $1$ | $0.0001\%$ | $4$ | $3$ |
| **Total** | **$740,822$** | **$100.0\%$** | **$744,216$** | **$3,394$** |

- Maximum parallel edge multiplicity: **$q_{\max} = 4$**.
- Exactly $1$ ordered vertex pair possesses $4$ parallel edges.
- Exactly $3,379$ ordered pairs possess multiple edges ($6,773$ edge records total).

### 5.2 Dynamic Evaluation and Lack of Caching
Inspection of `routing/algorithms.py#L623-L656` confirms:
1. **Zero Caching:** There is no memoization, hash table, or precomputation of parallel-edge costs. Every time directed edge $(v, w)$ is examined in the successor loop, `graph.get_edge_data(v, w)` is queried dynamically.
2. **Dynamic Generator:** When $q(v, w) > 1$, `min(two_wheeler_edge_cost(data, ...) for data in edge_data.values())` dynamically evaluates `two_wheeler_edge_cost` $q(v, w)$ times.
3. **Application to Iteration Bounds:** Because edge scanning occurs inside `for next_node in graph.successors(current_node)`, the multiplicity factor applies directly to the successor loop iteration count:
   $$\mathcal{T}_{\text{edge\_eval}} = \sum_{\text{iterations}} q(v, w) \le q_{\max} \cdot I_{\text{total}}$$
   - Worst-case full-graph evaluation under exact iterations:
     $$\mathcal{T}_{\text{edge\_eval}} \le 4 \times 5,886,792 = \mathbf{23,547,168} \text{ evaluations}$$
   - Under degree-bounded simple iterations:
     $$\mathcal{T}_{\text{edge\_eval}} \le 4 \times 10,165,195 = \mathbf{40,660,780} \text{ evaluations}$$
   - In practice, because $99.544\%$ of pairs have $q = 1$, expected edge evaluations are within $\sim 1.005 \times I_{\text{total}}$.
   - Because $q_{\max} = 4 = \mathcal{O}(1)$, parallel-edge scanning introduces a small constant factor without altering the asymptotic $\mathcal{O}(|E_s| \log |E_s|)$ complexity.

---

## 6. Task 5: Final Multi-Tier Complexity Recommendations

To eliminate any potential ambiguity in Section IV drafting, complexity formulations are codified across four distinct tiers:

### Tier 1: Actual Effective Simple-Graph Search (Bengaluru Exact)
- **Scope:** Exact search space executed by `two_wheeler_astar` on the Bengaluru metropolitan road network ($G = (V, E_s)$).
- **Formulation:**
  - State space: $|S| = |E_s| + 1 = \mathbf{740,823}$.
  - Search transitions: $T_{\text{internal}}^{\text{simple}} = \mathbf{2,087,155}, \; T_{\text{query}}^{\text{simple}} \le \mathbf{2,087,161}$.
  - Heap operations: $N_{\text{insert}} = N_{\text{remove}} \le 1 + T_{\text{query}}^{\text{simple}} = \mathbf{2,087,162}$.
  - Stale state extractions: $E_{\text{stale}} \le 1,346,333 + 6 = \mathbf{1,346,339}$.
  - Successor loop iterations: $I_{\text{total},\text{exact}} = 2,087,161 + 3,799,631 = \mathbf{5,886,792}$.
  - Peak auxiliary memory: $\mathcal{M}_{\text{actual}} \le \mathbf{3,877,450} \text{ logical entries}$ ($5.234 \times |E_s|$).

### Tier 2: Conservative Degree-Based Upper Bounds
- **Scope:** Closed-form bounds using maximum junction valence ($d_{\max}^{\text{out}} = 6, d_{\max}^{\text{in}} = 6$).
- **Formulation:**
  - Degree-bounded stale loop iterations: $I_{\text{stale}} \le 1,346,339 \times 6 = \mathbf{8,078,034}$.
  - Degree-bounded total iterations on simple graph: $I_{\text{total}} \le 2,087,161 + 8,078,034 = \mathbf{10,165,195}$.
  - Degree-bounded total iterations under multigraph proxy: $I_{\text{total}} \le 2,103,900 + 8,178,468 = \mathbf{10,282,368}$.
  - Crude global bound ($N_{\text{remove}} \times 6$): $\le \mathbf{12,623,406}$.
  - Peak memory under multigraph transition bound: $\mathcal{M}_{\text{raw}} \le \mathbf{3,894,189} \text{ logical entries}$ ($5.257 \times |E_s|$).

### Tier 3: General Directed Graphs and Urban Networks (Asymptotic Formulations)
- **General Directed Graphs (Unbounded Valence, Equation 6):**
  $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} + |V|) \text{ entries}$$
  $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right)$$
- **Bounded-Valence Urban Street Networks (Theorem 3):**
  Under Assumption A2 ($d_{\max}^{\text{in}} = \mathcal{O}(1), d_{\max}^{\text{out}} = \mathcal{O}(1), q_{\max} = \mathcal{O}(1)$):
  $$\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|), \quad \mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$$

### Tier 4: Authoritative Frozen Empirical Runtime Baseline
- **Scope:** Real-world corridor performance under Condition A0 Turn-Aware Production Engine ($N = 25$ corridors, $R = 5$ repetitions, 125 runs total).
- **Canonical Metrics:**
  - **Median Latency:** **$174.93\text{ ms}$** (IQR: **$439.08\text{ ms}$**; $Q_1 = 40.18\text{ ms}, Q_3 = 479.26\text{ ms}$)
  - **Mean Latency:** **$382.98\text{ ms} \pm 464.48\text{ ms}$**
  - **Observed Range:** **$1.01\text{ ms}$** to **$1,829.18\text{ ms}$**
  - **Right-skewness:** $2.19\times$ mean-to-median ratio, validating non-parametric Wilcoxon analysis.

---

## 7. Task 6: Deliverables Verification

| Phase 8.1-T Deliverable | File Path | Version / Status | File Size | Description |
| :--- | :--- | :---: | :---: | :--- |
| **Deliverable 1** | [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) | v1.3 Reconciled and Verified | 37,214 bytes | Complete mathematical proofs, reconciled simple vs. multigraph transitions, exact origin $+20$ proof, parallel multiplicity distribution, and multi-tier complexity bounds. |
| **Deliverable 2** | [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) | v1.2 Reconciled and Verified | 17,645 bytes | Code-level reconstruction of `two_wheeler_astar`, simple graph loop iterations, exact origin loop adjustments, and auxiliary memory bounds. |
| **Deliverable 3** | [`phase_8_1_T_final_verification_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_T_final_verification_log.md) | v1.0 Authoritative Record | Current File | Authoritative record of Phase 8.1-T graph verification, degree statistics, transition count reconciliation, stale loop derivation, and parallel-edge analysis. |

---

## 8. Strict Stop Condition Compliance

In strict compliance with research governance constraints:
- **Zero manuscript paragraphs have been drafted for Section IV.**
- **No changes have been made to frozen manuscript files** (`paper1_abstract_v2.md`, `paper1_introduction_v1.md`, `paper1_related_work_v1.md`, `paper1_section_III_v1.md`).
- **No changes have been made to bibliography or outline files.**
- **No source code or graph datasets have been modified.**
- **No new evaluation experiments were run.**
- **Phase 8.2 (Section IV Drafting) will NOT begin until explicit Research Lead authorization is granted.**
