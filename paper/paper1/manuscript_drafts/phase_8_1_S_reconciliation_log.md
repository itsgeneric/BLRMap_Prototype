# Phase 8.1-S Reconciliation Log — Stale-Pop Upper Bound and Runtime Evidence Reconciliation

**Document:** [`phase_8_1_S_reconciliation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_S_reconciliation_log.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1-S — Stale-Pop Bound and Runtime Evidence Reconciliation  
**Date:** 2026-11-06  
**Audited Documents:**  
- Mathematical Evidence Map: [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.2 Reconciled)  
- Implementation Audit: [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) (v1.1 Reconciled)  
- Prior Reconciliation Log: [`phase_8_1_R_reconciliation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_R_reconciliation_log.md)  
- Section IV Structural Blueprint: [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
- Frozen Section III: [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (Version 1.3 Canonical Frozen)  
**Implementation Grounding:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py), [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py)  
**Audited Datasets:** [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl), [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv), [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE RECONCILIATION LOG (PHASE 8.1-S COMPLETED)**

---

## 1. Executive Summary & Audit Objectives

Following the completion of Phase 8.1 (Structural Planning and Implementation Audit) and Phase 8.1-R (Mathematical Complexity and Heuristic Proof Reconciliation), two critical ambiguities remained in the Section IV mathematical foundation:
1. **Stale-Pop Bound and Successor-Loop Iteration Discrepancies:**
   - The formula previously used for stale heap-entry upper bounds ($\sum_v d_{\text{in}}(v)(d_{\text{out}}(v) - 1)$) was a global net difference that paired $(-1)$ with destination out-degree rather than approach in-degree, unphysically allowed dead ends to generate negative terms, and omitted the origin root departure bonus.
   - An internal arithmetic contradiction existed in Phase 8.1-R wherein $I_{\text{stale}} \le 10,519,506$ was derived by subtracting unmultiplied transitions ($T_{\text{query}} = 2,103,900$) from a total iteration figure ($12,623,406$) where best pops had already been multiplied by $d_{\max}^{\text{out}} = 6$, creating an inconsistent mixed arithmetic quantity.
2. **Runtime Metric Provenance Discrepancy:**
   - Phase 8.1 and 8.1-R reported latency numbers ($117.84\text{ ms}$ mean and $103.7\text{ ms}$ median) that were not present in the frozen experimental records, conflicting with the frozen Phase 13.4 / Phase 3.6 A0 production baseline ($382.98\text{ ms}$ mean, $174.93\text{ ms}$ median, IQR $439.08\text{ ms}$, range $1.01\text{--}1,829.18\text{ ms}$ on $N=25, R=5$).

Phase 8.1-S was executed to rigorously resolve both issues at the mathematical, algorithmic, and empirical levels before authorizing Section IV manuscript drafting. All findings, step-by-step derivations, corrected counts, and provenance trails are codified herein.

---

## 2. Task 1: Re-Derivation and Mathematical Proof of the Stale-Pop Upper Bound

### 2.1 State Reachability and Strict Relaxation Mechanics
In `two_wheeler_astar` ([`routing/algorithms.py#L681`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L681)), an edge-state $s = (u, v) \in E_s$ is inserted into `open_set` via `heapq.heappush` if and only if:
```python
if next_state not in g_score or new_cost < g_score[next_state]:
```
Because the algorithm maintains no handle to heap entries, decrease-key is simulated by re-inserting state $(u, v)$ with its updated key (`counter`, `priority`), leaving the prior, higher-cost entry in the binary min-heap.

We establish the maximum number of times $(u, v)$ can satisfy this condition:

1. **Predecessor Ingress for Regular States ($u \ne s_0$):**
   - State $(u, v)$ can only be reached when an incoming predecessor state $(x, u)$ is expanded, where $x \in \text{pred}(u)$.
   - There are exactly $d_{\text{in}}(u)$ distinct predecessor nodes in the simple graph $G = (V, E_s)$.
   - By Theorem 2 (Monotonic Consistency), when the first pop of state $(x, u)$ occurs, it retrieves the optimal cost $g^*(x, u)$ and evaluates transition cost:
     $$c((x, u), (u, v)) = c_{\min}(u, v) + P_{\text{turn}}(x, u, v)$$
     This triggers at most **one** successful insertion of $(u, v)$ into `open_set`.
   - Any subsequent pop of $(x, u)$ is a stale pop. Because $g$-scores are monotonic, the stale pop extracts a higher cost $g_{\text{stale}}(x, u) > g^*(x, u)$. When it evaluates candidate cost `new_cost = g_score[current_state] + edge_cost + turn_cost`, `g_score[current_state]` still holds the optimal cost $g^*(x, u)$, reproducing the identical candidate cost previously written to `g_score[(u, v)]`. Thus `new_cost < g_score[(u, v)]` strictly evaluates to `False`.
   - Therefore, each predecessor $x \in \text{pred}(u)$ can trigger at most **one** heap insertion of $(u, v)$.
   - Total insertions of state $(u, v) \le d_{\text{in}}(u)$.

2. **Best Pop vs. Stale Pops for $(u, v)$ ($u \ne s_0$):**
   - The first time $(u, v)$ is popped from `open_set`, it represents the optimal path to $(u, v)$ (the "best pop").
   - Any subsequent pop of $(u, v)$ is a stale duplicate entry ("stale pop").
   - Therefore:
     $$\text{Stale pops of } (u, v) \le \max(d_{\text{in}}(u) - 1, 0)$$
   - Summing across all $d_{\text{out}}(u)$ outgoing edges departing from vertex $u \ne s_0$:
     $$\sum_{v \in \text{succ}(u)} \text{Stale pops of } (u, v) \le d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0)$$

3. **Origin Departure States ($u = s_0$):**
   - Outgoing states $(s_0, v)$ can be reached from two sources:
     a) The synthetic root state $s_0^{\text{state}} = (\text{None}, s_0)$ at initialization (at most 1 insertion).  
     b) Incoming cycle predecessor states $(x, s_0)$ for $x \in \text{pred}(s_0)$ (at most $d_{\text{in}}(s_0)$ insertions).
   - Total insertions of $(s_0, v) \le 1 + d_{\text{in}}(s_0)$.
   - Stale pops of $(s_0, v) \le (1 + d_{\text{in}}(s_0)) - 1 = d_{\text{in}}(s_0)$.
   - Summing across all $d_{\text{out}}(s_0)$ outgoing edges from $s_0$:
     $$\sum_{v \in \text{succ}(s_0)} \text{Stale pops of } (s_0, v) \le d_{\text{out}}(s_0) \cdot d_{\text{in}}(s_0)$$

4. **Synthetic Root State ($s_0^{\text{state}}$):**
   - State $(\text{None}, s_0)$ is pushed exactly once at initialization ([`routing/algorithms.py#L538`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L538)).
   - It is popped at most once during search initialization. Stale pops $= 0$.

### 2.2 Proven Graph-Wide Stale Pop Upper Bound
Summing over all states in $S = E_s \cup \{(\text{None}, s_0)\}$:
$$E_{\text{stale}} \le d_{\text{out}}(s_0) \cdot d_{\text{in}}(s_0) + \sum_{u \ne s_0} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0) \tag{1}$$

Since $d_{\text{in}}(s_0) - \max(d_{\text{in}}(s_0) - 1, 0) = \mathbb{I}(d_{\text{in}}(s_0) \ge 1)$, this can be written equivalently across all $u \in V$:
$$E_{\text{stale}} \le \sum_{u \in V} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0) + d_{\text{out}}(s_0) \cdot \mathbb{I}(d_{\text{in}}(s_0) \ge 1) \tag{2}$$
Because $d_{\text{out}}(s_0) \le d_{\max}^{\text{out}} \le 6$ and $\mathbb{I}(d_{\text{in}}(s_0) \ge 1) \le 1$, the origin adjustment term is bounded by:
$$d_{\text{out}}(s_0) \cdot \mathbb{I}(d_{\text{in}}(s_0) \ge 1) \le 6$$

### 2.3 Mathematical Comparison with the Earlier Expression
The earlier formulation in Phase 8.1 / Phase 3.6 was:
$$E_{\text{earlier}} = \sum_{v \in V} d_{\text{in}}(v) \cdot (d_{\text{out}}(v) - 1) = T_{\text{internal}} - |E_s|$$

An exhaustive mathematical and topological comparison reveals why the earlier expression is flawed:
1. **Incorrect Degree Association:**  
   The earlier expression paired the subtraction $(-1)$ with the destination's out-degree $d_{\text{out}}(v)$. However, relaxation opportunities and multiple heap insertions of an edge $(u, v)$ are driven by incoming paths to $u$, which is governed by the approach vertex's in-degree $d_{\text{in}}(u)$, not $v$'s out-degree.
2. **Unphysical Negative Terms for Dead-End Nodes:**  
   For any cul-de-sac or terminal node where $d_{\text{out}}(v) = 0$ but $d_{\text{in}}(v) \ge 1$, the earlier term evaluated to $d_{\text{in}}(v) \times (0 - 1) = -d_{\text{in}}(v)$. This generated unphysical negative quantities that artificially offset positive stale counts at other intersections. The correct formulation includes the truncation operator $\max(d_{\text{in}}(u) - 1, 0)$, ensuring that nodes with $d_{\text{in}}(u) \le 1$ contribute 0 rather than negative values.
3. **Omission of Origin Root Departure Term:**  
   The earlier formula failed to account for the fact that outgoing edges from origin $s_0$ receive an initial entry from $(\text{None}, s_0)$ plus potential re-insertions from incoming cyclic edges, creating an extra $+d_{\text{out}}(s_0)$ relaxation potential.

### 2.4 Recomputed Concrete Values on Bengaluru Network (`bengaluru_graph.pkl`)
Executing exact graph inspection on `bengaluru_graph.pkl` ($|V| = 308,643, |E_{\text{raw}}| = 744,216, |E_s| = 740,822$):
- Simple graph topological summation:
  $$\sum_{u \in V} d_{\text{out}}(u) \cdot \max(d_{\text{in}}(u) - 1, 0) = \mathbf{1,346,333}$$
- Origin bonus term: $\max_{s_0} [d_{\text{out}}(s_0) \mathbb{I}(d_{\text{in}}(s_0) \ge 1)] \le 6$.
- **Reconciled Effective Simple Graph Bound:**
  $$E_{\text{stale}} \le 1,346,333 + 6 = \mathbf{1,346,339}$$
- Under raw multigraph record upper bound ($T_{\text{raw}} - |E_s| + 6$):
  $$E_{\text{stale}} \le 2,103,894 - 740,822 + 6 = \mathbf{1,363,078}$$

---

## 3. Task 2: Successor Loop Iteration Arithmetic Reconciliation

### 3.1 Audit of Previously Reported Figures
In Phase 8.1-R, the following quantities were reported:
- Stale pop bound: $E_{\text{stale}} \le 1,363,078$
- Best loop iterations: $I_{\text{best}} \le 2,103,900$
- Stale loop iterations: $I_{\text{stale}} \le 10,519,506$
- Total loop iterations: $I_{\text{total}} \le 12,623,406$

### 3.2 Identification of the Arithmetic Discrepancy
An audit of the arithmetic reveals two significant contradictions:
1. **Contradiction A (Degree-bounded multiplication mismatch):**  
   If $E_{\text{stale}} \le 1,363,078$ and the network maximum out-degree is $d_{\max}^{\text{out}} = 6$, then multiplying the stale pops by the maximum branching factor yields:
   $$1,363,078 \times 6 = \mathbf{8,178,468} \ne 10,519,506$$
   The reported $10,519,506$ exceeded the degree-bounded maximum by $2,341,038$ iterations.
2. **Contradiction B (Root cause tracing):**  
   Tracing how $12,623,406$ was originally obtained:
   $$12,623,406 = (1 + 2,103,900) \times 6 = N_{\text{remove}} \times 6$$
   In this crude calculation, **all** heap removals (both best pops and stale pops) were multiplied by $d_{\max}^{\text{out}} = 6$.
   Then, $I_{\text{stale}}$ was calculated by subtracting $I_{\text{best}}$:
   $$I_{\text{stale}} = 12,623,406 - 2,103,900 = 10,519,506$$
   This was an arithmetic error: $2,103,900$ was subtracted as an **unmultiplied** quantity from a total in which best pops had already been multiplied by 6 ($|S| \times 6 = 4,444,938$).

### 3.3 Reconciled Arithmetic Formulations
The loop iteration mechanics in `routing/algorithms.py#L607` expand `for next_node in graph.successors(current_node)`. When state $(u, v)$ is popped (whether best or stale), if $v \ne \text{end\_node}$, it executes exactly $d_{\text{out}}(v)$ loop iterations.

1. **Best Successor Iterations ($I_{\text{best}}$):**  
   Each reachable state is expanded at most once as a best pop:
   $$I_{\text{best}} = d_{\text{out}}(s_0) + \sum_{(u, v) \in E_s} d_{\text{out}}(v) = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) d_{\text{out}}(v) = T_{\text{query}}$$
   - Simple graph: $I_{\text{best}} \le 2,087,155 + 6 = \mathbf{2,087,161}$.
   - Multigraph transition bound: $I_{\text{best}} \le 2,103,894 + 6 = \mathbf{2,103,900}$.

2. **Stale Successor Iterations ($I_{\text{stale}}$):**  
   - **Exact In-Memory Graph Summation:**  
     Weighting each state's stale pop bound by its exact head out-degree:
     $$I_{\text{stale},\text{exact}} \le \sum_{u \in V} \max(d_{\text{in}}(u) - 1, 0) \cdot \left(\sum_{v \in \text{succ}(u)} d_{\text{out}}(v)\right) + \max_{s_0} \left[ \mathbb{I}(d_{\text{in}}(s_0) \ge 1) \cdot \sum_{v \in \text{succ}(s_0)} d_{\text{out}}(v) \right]$$
     Evaluating on `bengaluru_graph.pkl`:
     $$I_{\text{stale},\text{exact}} = 3,799,611 + 20 = \mathbf{3,799,631}$$
   - **Degree-Bounded Upper Bound ($d_{\max}^{\text{out}} = 6$):**  
     - Effective simple graph: $I_{\text{stale}} \le 1,346,339 \times 6 = \mathbf{8,078,034}$.
     - Multigraph bound: $I_{\text{stale}} \le 1,363,078 \times 6 = \mathbf{8,178,468}$.

3. **Total Successor Iterations ($I_{\text{total}} = I_{\text{best}} + I_{\text{stale}}$):**  
   - **Exact Bengaluru Summation:**
     $$I_{\text{total},\text{exact}} = 2,087,161 + 3,799,631 = \mathbf{5,886,792}$$
   - **Degree-Bounded on Simple Graph:**
     $$I_{\text{total}} \le 2,087,161 + 8,078,034 = \mathbf{10,165,195}$$
   - **Degree-Bounded under Multigraph Transitions:**
     $$I_{\text{total}} \le 2,103,900 + 8,178,468 = \mathbf{10,282,368}$$
   - **Crude Global Bound ($N_{\text{remove}} \times 6$):**
     $$I_{\text{total}} \le 2,103,901 \times 6 = \mathbf{12,623,406}$$

All arithmetic is now fully reconciled and free of contradictions.

---

## 4. Task 3: Heap Operations and Search Cardinality Disentanglement

To ensure that Section IV prose never conflates transitions, relaxations, heap insertions, heap removals, stale pops, and loop iterations, the exact bounds are codified below:

| Operation / Entity | Mathematical Notation | Simple Graph Value | Multigraph Bound | Implementation Grounding |
| :--- | :---: | :---: | :---: | :--- |
| **Search States** | $\|S\| = \|E_s\| + 1$ | $740,823$ | $740,823$ | `len(g_score)` at complete graph saturation |
| **Internal Transitions** | $T_{\text{internal}}$ | $2,087,155$ | $2,103,894$ | $\sum_v d_{\text{in}}(v) d_{\text{out}}(v)$ |
| **Initial Transitions** | $T_{\text{initial}}$ | $d_{\text{out}}(s_0) \le 6$ | $d_{\text{out}}(s_0) \le 6$ | Transitions departing $(\text{None}, s_0)$ |
| **Total Transitions** | $T_{\text{query}}$ | $\le 2,087,161$ | $\le 2,103,900$ | $T_{\text{internal}} + T_{\text{initial}}$ |
| **Successful Relaxations** | $R_{\text{actual}}$ | $\le 2,087,161$ | $\le 2,103,900$ | Times `new_cost < g_score[next_state]` evaluates `True` |
| **Heap Insertions** | $N_{\text{insert}}$ | $\le 2,087,162$ | $\le 2,103,901$ | Calls to `heapq.heappush`: $1 + R_{\text{actual}}$ |
| **Heap Removals** | $N_{\text{remove}}$ | $\le 2,087,162$ | $\le 2,103,901$ | Calls to `heapq.heappop`: Best pops $+$ Stale pops |
| **Best State Pops** | $N_{\text{best}}$ | $\le 740,823$ | $\le 740,823$ | First extraction of each state ($g$-score finalized) |
| **Stale State Pops** | $E_{\text{stale}}$ | $\le 1,346,339$ | $\le 1,363,078$ | Subsequent extractions of previously finalized states |
| **Successor Iterations** | $I_{\text{total}}$ | $5,886,792$ (exact) | $\le 10,282,368$ (deg-bound) | Total executions of `for next_node in successors` |
| **Max Parallel Multiplicity**| $q_{\max}$ | $4$ | $4$ | Max multigraph edges between any node pair |
| **Peak Auxiliary Memory** | $\mathcal{M}_{\text{logical}}$ | $\le 3,894,189$ entries | $\le 3,894,189$ entries | Sum of entries in `open_set`, `g_score`, `came_from`, `visited_nodes` |

---

## 5. Task 4: Runtime Metric Provenance Audit and Baseline Restoration

### 5.1 Investigation of the $117.84\text{ ms} / 103.7\text{ ms}$ Discrepancy
Phase 8.1 and Phase 8.1-R cited a mean execution latency of $117.84\text{ ms}$ and a median of $103.7\text{ ms}$. An exhaustive forensic scan was conducted across all project directories:
1. Grepping all CSV, JSON, and Markdown files in `research/literature_survey/13_ablation_study/`:
   - `exp_a_corridor_metrics.csv`
   - `exp_b_runtime_breakdown.csv`
   - `stage_2b_full_ablation_results.json`
   - `phase_13_1_stage_2B_full_ablation_report.md`
   - `phase_13_3_independent_audit_report.md`
   - `phase_3_6_final_complexity_correction.md`
2. **Finding:** The numbers $117.84$ and $103.7$ **do not appear anywhere** in any experimental result file, test output, or ablation log.
3. **Classification:** The figures $117.84\text{ ms}$ and $103.7\text{ ms}$ are **UNVERIFIED / SYNTHETIC ARTIFACTS** erroneously introduced during intermediate drafting notes.
4. **Action:** Both figures have been **completely purged** from the mathematical evidence map and implementation audit.

### 5.2 Authoritative Frozen Ground-Truth Production Baseline
The authoritative empirical runtime baseline for Paper 1 is the **Condition A0 Turn-Aware Production Engine**, frozen in Phase 13.4 and audited in Phase 3.6:
- **Canonical Data Sources:**
  - Raw per-corridor CSV: [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv)
  - Raw JSON metrics: [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json)
  - Frozen Stage 2B Report: [`phase_13_1_stage_2B_full_ablation_report.md#L94`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md#L94)
  - Independent Audit Report: [`phase_13_3_independent_audit_report.md#L93`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_3_independent_audit_report.md#L93)
  - Phase 3.6 Correction Log: [`phase_3_6_final_complexity_correction.md#L33`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_6_final_complexity_correction.md#L33)

- **Experimental Configuration:**
  - **Sample Size:** $N = 25$ representative Bengaluru metropolitan commute corridors spanning short, medium, and long-range routes.
  - **Repetitions:** $R = 5$ repetitions per corridor (125 query evaluations total).
  - **Hardware / Platform:** Frozen benchmarking workstation, Python 3.10+, single-threaded in-memory execution.
  - **Timing Boundary:** In-function CPU execution time of `two_wheeler_astar` via `time.perf_counter()`, strictly isolating graph search from disk loading and graph deserialization.
  - **Engine Parameters (Condition A0):** Turn penalties active ($P_{\text{sharp}} = 25.0\text{ s}, P_{\text{mod}} = 8.0\text{ s}$), full composite road impedance active ($\mu \in [0.80, 1.60]$).

- **Frozen Empirical Metrics:**
  - **Median Execution Latency:** **$174.93\text{ ms}$**
  - **Interquartile Range (IQR):** **$439.08\text{ ms}$** ($Q_1 = 40.18\text{ ms}, Q_3 = 479.26\text{ ms}$)
  - **Mean Execution Latency:** **$382.98\text{ ms} \pm 464.48\text{ ms}$**
  - **Observed Range:** **$1.01\text{ ms}$** (shortest local connector) to **$1,829.18\text{ ms}$** (longest diagonal metropolitan commute).
  - **Distribution Skewness:** Mean / Median ratio $= 382.98 / 174.93 = 2.19\times$. This severe right-skewness is caused by long-distance arterial corridors expanding $\mathcal{O}(R^2)$ search envelopes. It rigorously justifies reporting median/IQR and using non-parametric Wilcoxon signed-rank tests for statistical comparisons.

---

## 6. Task 5: Revised Four-Tier Complexity Statements

The finalized complexity statements for Section IV are structured across four formal tiers:

### Tier 1: General Directed Graphs (Equation 6)
- **Scope:** Arbitrary directed graphs without bounded degrees, utilizing binary min-heap without decrease-key and dynamic parallel-edge minimization.
- **Formulation:**
  $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}} + |V|) \text{ logical entries}$$
  $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + q_{\max} \cdot |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right)$$
  With $d_{\max} = \max(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$:
  $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max} \log |E_s| + q_{\max} \cdot |E_s| \cdot d_{\max}^2 \right)$$

### Tier 2: Bounded-Valence Urban Networks (Theorem 3)
- **Scope:** Terrestrial urban street networks.
- **Governing Axiom:** Bounded physical junction valence: $d_{\max}^{\text{in}} = \mathcal{O}(1)$, $d_{\max}^{\text{out}} = \mathcal{O}(1)$, and parallel edge multiplicity $q_{\max} = \mathcal{O}(1)$.
- **Formulation:**
  $$\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|) \text{ logical entries}$$
  $$\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$$

### Tier 3: Concrete Bengaluru Graph-Wide Upper Bound
- **Scope:** Worst-case search saturating the entire road network of Bengaluru (`bengaluru_graph.pkl`, $|V| = 308,643$, $|E_s| = 740,822$, $d_{\max} = 6$, $q_{\max} = 4$).
- **Quantities:**
  - State space: $|S| = 740,823$
  - Query transitions: $T_{\text{query}} \le 2,087,161$ (simple graph) / $2,103,900$ (multigraph record bound)
  - Heap insertions: $N_{\text{insert}} \le 2,087,162$ (simple) / $2,103,901$ (multigraph)
  - Heap removals: $N_{\text{remove}} \le 2,087,162$ (simple) / $2,103,901$ (multigraph)
  - Stale pops: $E_{\text{stale}} \le 1,346,339$ (simple) / $1,363,078$ (multigraph)
  - Successor loop iterations: $I_{\text{total},\text{exact}} = 5,886,792$ (exact) / $\le 10,282,368$ (degree-bounded)
  - Memory footprint: $\mathcal{M}_{\text{Bengaluru}} \le 3,894,189$ logical entries ($\le 5.26 \cdot |E_s|$)

### Tier 4: Authoritative Empirical Runtime Baseline
- **Scope:** Practical commute routing performance across $N = 25$ real-world corridors ($R = 5$ repetitions).
- **Quantities:**
  - **Median Latency:** **$174.93\text{ ms}$** (IQR: **$439.08\text{ ms}$**)
  - **Mean Latency:** **$382.98\text{ ms} \pm 464.48\text{ ms}$**
  - **Range:** **$1.01\text{ ms}$** to **$1,829.18\text{ ms}$**
  - **Right-skewness:** $2.19\times$ mean/median ratio

---

## 7. Blueprint Alignment and Deliverables Verification

### 7.1 Structural Blueprint Alignment
The Section IV structural blueprint ([`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)) was reviewed against the reconciled findings. Because the blueprint defines structural headings, paragraph purposes, and proof objectives at an architectural level without hardcoding the superseded intermediate numbers, **no modifications to the structural blueprint are required**. The blueprint remains 100% compliant with the reconciled evidence map.

### 7.2 Deliverables Status Matrix

| Phase 8.1-S Deliverable | File Path | Version / Status | File Size | Description |
| :--- | :--- | :---: | :---: | :--- |
| **Deliverable 1** | [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) | v1.2 Reconciled | 34,906 bytes | Complete mathematical proofs, corrected transition notation, reconciled stale-pop bounds, uncached parallel edge scanning, logical memory bounds, and restored frozen runtime baseline. |
| **Deliverable 2** | [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md) | v1.1 Reconciled | 16,733 bytes | Reconstructed `two_wheeler_astar` execution trace, parallel-edge scanning analysis, proof of goal extraction safety without stale guards, and memory bounds audit. |
| **Deliverable 3** | [`phase_8_1_S_reconciliation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_S_reconciliation_log.md) | v1.0 Authoritative Record | Current File | Exhaustive audit log documenting the mathematical proofs, arithmetic corrections, runtime provenance audit, and four-tier complexity statements. |

---

## 8. Strict Stop Condition Compliance

In strict compliance with research protocol and governance constraints:
- **Zero manuscript paragraphs have been drafted for Section IV.**
- **No changes have been made to frozen manuscript files** (`paper1_abstract_v2.md`, `paper1_introduction_v1.md`, `paper1_related_work_v1.md`, `paper1_section_III_v1.md`).
- **No modifications have been made to source code or graph datasets.**
- **No new evaluation experiments were executed.**
- **Phase 8.2 (Section IV Drafting) will NOT begin until explicit Research Lead authorization is granted.**
