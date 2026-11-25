# Phase 3.6 — Final Complexity Bounds and Claim Scope Correction

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.6 — Final Complexity Bound and Claim Scope Check  
**Target:** Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Date:** 2026-11-05  
**Document:** [`phase_3_6_final_complexity_correction.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_6_final_complexity_correction.md)  
**Parent Audits:** [`phase_3_5_final_validation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_5_final_validation.md), [`phase_3_4_final_complexity_derivation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_final_complexity_derivation.md)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE COMPLEXITY & SCOPE SPECIFICATION**

---

## 1. Re-Derivation of State-Transition and Heap Insertion Bounds

### 1.1 The State-Transition Cardinality ($|E_S|$)
In `two_wheeler_astar` ([`routing/algorithms.py#L460-L705`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L460-L705)), each search state is a directed edge $s = (u, v) \in E$, plus the synthetic initial state $(\text{None}, s_0)$.

A valid transition occurs from state $(u, v)$ to state $(v, w)$ across physical intersection $v$. For any physical vertex $v \in V$:
- Exactly $d_{\text{in}}(v)$ incoming states enter vertex $v$.
- Exactly $d_{\text{out}}(v)$ outgoing edges depart from vertex $v$.
- The number of valid transitions passing through vertex $v$ in the state-space line graph is $d_{\text{in}}(v) \cdot d_{\text{out}}(v)$.

Summing across all vertices $v \in V$, plus the $d_{\text{out}}(s_0)$ initial departure transitions from $s_0$:
$$|E_S| = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v)$$

### 1.2 Dual Algebraic Bounding: $|E| \cdot d_{\max}^{\text{out}}$ vs. $|E| \cdot d_{\max}^{\text{in}}$
Consider the summation $\sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v)$:

1. **State-Expansion (Departure) Perspective:**  
   When a state $(u, v)$ is popped for the first time with optimal cost, it examines all outgoing edges departing from $v$. The number of outgoing edges is $d_{\text{out}}(v) \le d_{\max}^{\text{out}}$.  
   Summing across all $|E|$ directed edge states:
   $$\sum_{(u, v) \in E} d_{\text{out}}(v) = \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v) \le d_{\max}^{\text{out}} \sum_{v \in V} d_{\text{in}}(v) = |E| \cdot d_{\max}^{\text{out}}$$
   *This directly proves that the total number of relaxation attempts across all optimal pops is bounded by $|E| \cdot d_{\max}^{\text{out}}$.*

2. **Target-State (Arrival) Perspective:**  
   Alternatively, consider a target state $(v, w) \in E$. State $(v, w)$ can only be relaxed when an incoming path arrives via one of vertex $v$'s predecessors $u$. The number of predecessors is $d_{\text{in}}(v) \le d_{\max}^{\text{in}}$.  
   Summing across all $|E|$ target states:
   $$\sum_{(v, w) \in E} d_{\text{in}}(v) = \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v) \le d_{\max}^{\text{in}} \sum_{v \in V} d_{\text{out}}(v) = |E| \cdot d_{\max}^{\text{in}}$$

3. **Exact Mathematical Relation:**  
   Both bounds are rigorous, and their combination yields the tightest general bound:
   $$|E_S| \le |E| \cdot \min(d_{\max}^{\text{in}}, d_{\max}^{\text{out}}) + d_{\max}^{\text{out}} \le |E| \cdot d_{\max}^{\text{out}} + d_{\max}^{\text{out}}$$

### 1.3 Maximum Successful Relaxations and Heap Insertions
- In `two_wheeler_astar`, a heap push occurs only when `next_state not in g_score or new_cost < g_score[next_state]`.
- Because subsequent stale pops of state $(u, v)$ retrieve the already minimized $g$-score, they evaluate candidate costs identical to the initial pop, causing `new_cost < g_score[next_state]` to evaluate strictly to `False`.
- Consequently, each state $(v, w)$ can be relaxed at most $d_{\text{in}}(v)$ times, and each optimal pop of state $(u, v)$ can push at most $d_{\text{out}}(v)$ entries.
- Therefore, the total number of successful heap insertions across the entire search is strictly bounded by:
  $$N_{\text{pushes}} \le 1 + |E_S| \le 1 + |E| \cdot d_{\max}^{\text{out}} + d_{\max}^{\text{out}} = \mathcal{O}(|E| \cdot d_{\max}^{\text{out}})$$
  (and symmetrically bounded by $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$).

### 1.4 Maximum Heap Capacity and Logarithmic Factor
- Because inserted entries remain in `open_set` until popped:
  $$|\text{open\_set}|_{\max} \le N_{\text{pushes}} \le 1 + |E| \cdot d_{\max}^{\text{out}} + d_{\max}^{\text{out}} = \mathcal{O}(|E| \cdot d_{\max}^{\text{out}})$$
- Each priority queue push and pop operation takes:
  $$\mathcal{O}(\log |\text{open\_set}|_{\max}) = \mathcal{O}(\log (|E| \cdot d_{\max}^{\text{out}})) = \mathcal{O}(\log |E| + \log d_{\max}^{\text{out}})$$
- Across at most $N_{\text{pushes}}$ insertions and removals, total heap operation time is:
  $$\mathcal{T}_{\text{heap}} = \mathcal{O}\left( |E| \cdot d_{\max}^{\text{out}} \cdot (\log |E| + \log d_{\max}^{\text{out}}) \right)$$

### 1.5 Stale-Entry Successor Iteration Bound
- Maximum total pops $\le N_{\text{pushes}} \le 1 + |E_S|$.
- First (optimal) pops of distinct reached states $\le |S| = |E| + 1$.
- Total stale pops $\le |E_S| - |E| \le |E| \cdot (d_{\max}^{\text{out}} - 1) + d_{\max}^{\text{out}}$.
- When a stale entry of state $(u, v)$ is popped, it iterates through all outgoing edges from physical vertex $v$, executing $d_{\text{out}}(v) \le d_{\max}^{\text{out}}$ loop iterations.
- Summing across all stale pops:
  $$I_{\text{stale}} \le (|E_S| - |E|) \cdot d_{\max}^{\text{out}} \le |E| \cdot (d_{\max}^{\text{out}} - 1) \cdot d_{\max}^{\text{out}}$$
  (or in terms of in-degree: $I_{\text{stale}} \le |E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$).
- Within each stale successor iteration, $\mathcal{O}(1)$ arithmetic is performed (distance lookup, turn penalty calculation, and failed relaxation check).
- Total CPU time consumed by stale successor iterations:
  $$\mathcal{T}_{\text{stale\_loop}} = \mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}}) = \mathcal{O}(|E| \cdot d_{\max}^2)$$

### 1.6 Unified Asymptotic Complexity Bounds

1. **General Directed Graphs:**
   - **Auxiliary Memory:** $\mathcal{O}(|E| \cdot d_{\max}^{\text{out}})$ (including binary min-heap).
   - **Worst-Case Time:** $\mathcal{O}\left( |E| \cdot d_{\max}^{\text{out}} \cdot (\log |E| + \log d_{\max}^{\text{out}}) + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right)$.
   - Expressed with $d_{\max} = \max(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$:
     $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E| \cdot d_{\max})$$
     $$\mathcal{T}_{\text{general}} = \mathcal{O}(|E| \cdot d_{\max} \log |E| + |E| \cdot d_{\max}^2)$$

2. **Bounded-Degree Spatial Road Networks ($d_{\max}^{\text{in}} = \mathcal{O}(1), d_{\max}^{\text{out}} = \mathcal{O}(1)$):**
   $$\mathcal{M}_{\text{road\_network}} = \mathcal{O}(|E|)$$
   $$\mathcal{T}_{\text{road\_network}} = \mathcal{O}(|E| \log |E|)$$

3. **Grounding in the Bengaluru Metropolitan Network ($|E| = 744,216$):**
   - Maximum in-degree: $d_{\max}^{\text{in}} = 6$; Maximum out-degree: $d_{\max}^{\text{out}} = 6$.
   - Mean degree: $\bar{d} = 2.41$.
   - Exact state-transition count: $|E_S| = 2,103,894$.
   - Transition expansion ratio: $|E_S| / |E| = 2.83$.
   - Maximum heap pushes: $\le 1 + 2,103,894 + 6 = 2,103,901 \approx 2.83 \cdot |E|$.
   - Maximum auxiliary memory: $\le 3,592,335$ items ($\le 4.83 \cdot |E|$).
   - Worst-case time is strictly bounded by $\mathcal{O}(|E| \log |E|)$.

---

## 2. Corrected Scope for Route Geometry Equivalence (A1 vs. A2)

### 2.1 Scope Correction
Prior draft iterations included the overly broad statement:
> *"This establishes that the state-expanded graph formulation itself introduces zero geometric distortion..."*

Under [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), claiming that state expansion universally introduces zero geometric distortion across all hypothetical road networks is an unproven generalization. In theoretical graphs with non-unique shortest paths, differences in tie-breaking could produce alternate optimal paths.

### 2.2 Corpus-Bounded Empirical Evidence
The frozen experimental data in [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) and [`phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md) establishes:
- Across all $25$ evaluated metropolitan corridors, Condition A1 (turn-unaware state-expanded $A^*$) and Condition A2 (standard vertex-space $A^*$) produced:
  1. **100% Identical Node Sequences:** `route_A1 == route_A2` for $25 / 25$ corridors.
  2. **Identical Route Distances:** $7.723\text{ km}$ mean across both conditions ($0.0\text{ m}$ difference).
  3. **Identical Sharp Turns:** $32.52$ mean turns across both conditions ($0$ difference).
  4. **Identical Impedance Costs:** $9,325.87$ mean cost across both conditions ($0.0$ difference).

### 2.3 Authoritative Scope-Bounded Statement for Paper 1
> **Corpus-Bounded Route Equivalence Statement:**  
> *"Across the 25 evaluated metropolitan corridors, turn-unaware state-expanded $A^*$ (Condition A1) and standard vertex-space $A^*$ (Condition A2) produced **identical node sequences, physical distances, and impedance costs** (`route_A1 == route_A2` for $25 / 25$ corridors). This confirms that state-space expansion introduced zero route deviation across the evaluated benchmark corpus, and establishes that the observed $34.1\%$ sharp-turn reduction (Condition A0 vs. A1: $21.44$ vs. $32.52$ turns, mean difference $-11.08$ turns, Holm-adjusted $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$, Hodges-Lehmann median difference $-9.50$ turns [$95\%\text{ CI: } -13.0, -7.0$]) is purely attributable to heading-dependent turn penalties."*

---

## 3. Summary of Corrections Applied in Phase 3.6

| Item # | Domain | Prior Phase 3.5 Formulation | Phase 3.6 Corrected Formulation | Protocol Justification |
| :---: | :--- | :--- | :--- | :--- |
| **COR-3.6-01** | **Heap Insertion Bound Formulation** | Bound expressed primarily as $|E| \cdot d_{\max}^{\text{in}}$. | Formulated dual bounds: $|E_S| \le |E| \cdot d_{\max}^{\text{out}}$ (from departure expansions) and $|E_S| \le |E| \cdot d_{\max}^{\text{in}}$ (from arrival relaxations), tightly expressed as $|E| \cdot \min(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$. | Reflects the exact source-code relaxation mechanism where $|E|$ states expand at most $d_{\text{out}}(v) \le d_{\max}^{\text{out}}$ outgoing edges. |
| **COR-3.6-02** | **Logarithmic Operation Factor** | $\mathcal{O}(\log |E| + \log d_{\max}^{\text{in}})$ | $\mathcal{O}(\log |E| + \log d_{\max}^{\text{out}})$ based on $|\text{open\_set}|_{\max} \le |E| \cdot d_{\max}^{\text{out}} + d_{\max}^{\text{out}} + 1$. | Correctly matches heap capacity to the departure insertion bound. |
| **COR-3.6-03** | **General Time Complexity** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \log |E| + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$ | $\mathcal{O}\left( |E| \cdot d_{\max}^{\text{out}} \cdot (\log |E| + \log d_{\max}^{\text{out}}) + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right)$, or $\mathcal{O}(|E| \cdot d_{\max} \log |E| + |E| \cdot d_{\max}^2)$. | Rigorously accounts for both heap operations and stale successor loop overhead. |
| **COR-3.6-04** | **Geometric Equivalence Scope** | *"The state-expanded graph formulation itself introduces zero geometric distortion..."* | Limited strictly to the benchmark evidence: *"Across the 25 evaluated metropolitan corridors, Condition A1 and Condition A2 produced identical node sequences, physical distances, and impedance costs (`route_A1 == route_A2` for $25 / 25$ corridors)."* | Prevents unproven universal generalization; bounds claim strictly to the empirical benchmark data. |

---

*Specification verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
