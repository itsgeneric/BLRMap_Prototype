# Phase 3.5 — Final Technical and Mathematical Wording Validation

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.5 — Final Technical Wording Validation  
**Target:** Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Date:** 2026-11-05  
**Document:** [`phase_3_5_final_validation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_5_final_validation.md)  
**Parent Audits:** [`phase_3_4_final_complexity_derivation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_final_complexity_derivation.md), [`phase_3_4_final_claims_table.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_final_claims_table.csv), [`phase_3_4_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_correction_log.md)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **VALIDATED & AUTHORITATIVE**

---

## Executive Summary

Phase 3.5 conducts the final technical and epistemological validation of the Paper 1 claims before freezing the research documentation. It rigorously resolves three remaining formulation issues:
1. **Heap Complexity and Conservative Logarithmic Factor:** Fully accounts for the maximum heap capacity $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$ in the logarithmic operation cost $\mathcal{O}(\log(|E| \cdot d_{\max}^{\text{in}}))$, and provides an exact, implementation-grounded proof of why stale pops cannot cause subsequent successful relaxations.
2. **Statistical Language Disentanglement:** Replaces the imprecise assertion that skewness "mathematically mandates Wilcoxon reporting" with language that properly separates empirical runtime skewness, robust descriptive statistics (median and IQR), and the pre-specified paired non-parametric hypothesis testing protocol (Pratt-adjusted Wilcoxon, Hodges-Lehmann, and Holm-Bonferroni).
3. **Deterministic Route Equivalence (A1 vs. A2):** Replaces the redundant citation of $p_{\text{adj}} = 1.0000$ with a direct factual statement of deterministic geometric identity across all $25 / 25$ corridors.

---

## 1. Task 1 — Rigorous Heap Complexity and Stale-Entry Dynamics

### 1.1 Maximum Heap Size and Conservative Logarithmic Factor
In `two_wheeler_astar` ([`routing/algorithms.py#L536-L700`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L536-L700)), the priority queue `open_set` is managed using Python's standard `heapq` module without an addressable `decrease-key` operation.

1. **Total Heap Insertions ($N_{\text{pushes}}$):**  
   Every entry pushed into `open_set` corresponds to either:
   - The initial origin state $(\text{None}, s_0)$ ($1$ insertion).
   - A successful relaxation of edge $(v, w)$ to state $(v, w)$ when `new_cost < g_score[next_state]`.  
   Because state $(v, w)$ can only be relaxed when an incoming state into $v$ is popped, and there are $d_{\text{in}}(v)$ incoming edges to $v$, edge $(v, w)$ can be successfully relaxed at most $d_{\text{in}}(v)$ times.  
   Summing across all edges $(v, w) \in E$, plus initial departure transitions:
   $$N_{\text{pushes}} \le 1 + d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v) \le 1 + d_{\max}^{\text{out}} + |E| \cdot d_{\max}^{\text{in}}$$
2. **Maximum Simultaneous Heap Size ($|\text{open\_set}|_{\max}$):**  
   Because entries remain in the heap until popped, the maximum heap size is bounded by total pushes:
   $$|\text{open\_set}|_{\max} \le N_{\text{pushes}} \le 1 + d_{\max}^{\text{out}} + |E| \cdot d_{\max}^{\text{in}} = \mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$$
3. **Conservative Logarithmic Factor:**  
   Each `heappop` and `heappush` operation on a heap of size up to $|\text{open\_set}|_{\max}$ requires time proportional to:
   $$\mathcal{O}(\log |\text{open\_set}|_{\max}) = \mathcal{O}(\log (|E| \cdot d_{\max}^{\text{in}})) = \mathcal{O}(\log |E| + \log d_{\max}^{\text{in}})$$
   Across at most $N_{\text{pushes}}$ insertions and $N_{\text{pushes}}$ removals, total priority queue operation time is:
   $$\mathcal{T}_{\text{heap}} = \mathcal{O}\left( |E| \cdot d_{\max}^{\text{in}} \cdot (\log |E| + \log d_{\max}^{\text{in}}) \right)$$

### 1.2 Stale-Entry Invariance: Why Stale Pops Cannot Cause Further Relaxations
When a stale entry for state $(u, v)$ is popped:
1. `current_cost = g_score[state]` retrieves the value currently stored in the hash map.
2. Because the entry being popped is stale, a strictly lower cost $g^*(u, v) < g_{\text{stale}}(u, v)$ was already processed during an earlier pop of $(u, v)$.
3. During that earlier optimal pop, all outgoing edges $(v, w) \in \text{successors}(v)$ were relaxed, setting:
   $$g_{\text{score}}[(v, w)] \le g^*(u, v) + c_{\text{edge}}(v, w) + P_{\text{turn}}(u, v, w)$$
4. When the stale entry is popped later, `current_cost` is retrieved as $g^*(u, v)$ (the current value in `g_score`), NOT the stale priority value.
5. In the successor loop, the candidate cost evaluated is:
   $$\text{new\_cost} = g^*(u, v) + c_{\text{edge}}(v, w) + P_{\text{turn}}(u, v, w)$$
6. The relaxation condition is:
   ```python
   if next_state not in g_score or new_cost < g_score[next_state]:
   ```
7. Since `next_state` is already present in `g_score` and `g_score[next_state]` is already $\le \text{new\_cost}$, `new_cost < g_score[next_state]` evaluates **strictly to `False`** for all outgoing edges.
8. **Mathematical Invariant:** Stale entries can **never trigger a successful relaxation or push a new entry into `open_set`**.

### 1.3 Exact Stale Successor Iteration Bound
Although stale pops cannot trigger heap pushes, lines 611–673 of [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) execute the successor loop for every popped entry:
- Each state $(u, v) \in E$ is pushed at most $d_{\text{in}}(u)$ times.
- Exactly one pop of $(u, v)$ is the optimal (first) expansion.
- At most $d_{\text{in}}(u) - 1$ pops of state $(u, v)$ are stale entries.
- Each stale pop of state $(u, v)$ examines all outgoing edges from physical vertex $v$, executing $d_{\text{out}}(v)$ loop iterations.
- Summing across all directed edges $(u, v) \in E$:
  $$I_{\text{stale}} \le \sum_{(u, v) \in E} (d_{\text{in}}(u) - 1) \cdot d_{\text{out}}(v) \le |E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$$
- Within each stale loop iteration, edge attributes, surface modifiers, and turn angles are evaluated ($\mathcal{O}(1)$ arithmetic), followed by a failed hash-map inequality check ($\mathcal{O}(1)$).
- Total CPU time spent in stale successor iterations is strictly:
  $$\mathcal{T}_{\text{stale\_loop}} = \mathcal{O}(|E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}) = \mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$$

### 1.4 Unified Time and Memory Complexity
Combining heap operations and stale successor iterations:
$$\mathcal{T}_{\text{total}} = \mathcal{O}\left( |E| \cdot d_{\max}^{\text{in}} \cdot (\log |E| + \log d_{\max}^{\text{in}}) + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right)$$
$$\mathcal{M}_{\text{total}} = \mathcal{O}\left( |E| \cdot d_{\max}^{\text{in}} \right)$$

Under **Assumption A2** (bounded road-network junction valence, $d_{\max} \le c = \mathcal{O}(1)$):
$$\log d_{\max}^{\text{in}} = \mathcal{O}(1), \quad d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} = \mathcal{O}(1)$$
$$\mathcal{T}_{\text{road\_network}} = \mathcal{O}(|E| \log |E|)$$
$$\mathcal{M}_{\text{road\_network}} = \mathcal{O}(|E|)$$

**Grounding in Bengaluru Road Network ($|E| = 744,216$):**
- $d_{\max}^{\text{in}} = 6$, $d_{\max}^{\text{out}} = 6$ (mean degree $2.41$).
- Transition expansion ratio: $|E_S| / |E| = 2.83$ ($2,103,894$ transitions).
- Stale successor iterations are bounded by $I_{\text{stale}} \le 744,216 \times 5 \times 6 = 22,326,480$ iterations (empirical expectation: $\approx 1.36 \times 10^6 \times 2.41 \approx 3.28 \times 10^6 \approx 4.4 \cdot |E|$).
- The $\mathcal{O}(|E| \log |E|)$ time bound and $\mathcal{O}(|E|)$ memory bound hold with complete mathematical rigor.

---

## 2. Task 2 — Statistical Reporting and Disentangled Wording

### 2.1 Flaw in Prior Phrasing
Prior draft text stated:
> *"The empirical runtime distribution is heavily right-skewed... methodologically mandating non-parametric median and Wilcoxon reporting."*

This phrasing was scientifically imprecise:
- Skewness alone does not "mathematically mandate" Wilcoxon testing.
- Wilcoxon signed-rank tests test for shifts in paired population distributions under arbitrary continuous distributions, while medians and IQRs are descriptive statistics chosen for robustness against heavy tails.

### 2.2 Disentangled Authoritative Formulation
The paper will clearly separate description from hypothesis testing:

1. **Empirical Distribution Description:**  
   *"Across the 25 metropolitan corridors, execution runtimes exhibit an empirically observed right-skewed distribution across corridor distance tiers (Short corridors $< 4\text{ km}$: $1.01\text{--}18.42\text{ ms}$; Medium corridors $4\text{--}10\text{ km}$: $110.50\text{--}245.80\text{ ms}$; Long cross-city corridors $> 10\text{ km}$: $850.12\text{--}1,829.18\text{ ms}$)."*
2. **Descriptive Metric Choice:**  
   *"Due to the heavy right tail of route lengths and computational runtimes, corridor-level performance is summarized using the median and interquartile range (IQR: $439.08\text{ ms}$; median: $174.93\text{ ms}$; mean: $382.98\text{ ms} \pm 464.48\text{ ms}$) to provide robust measures of central tendency and dispersion unaffected by extreme long-corridor values."*
3. **Paired Inferential Testing Protocol:**  
   *"To evaluate paired algorithmic differences across the 25 matched corridors without assuming distributional normality, hypothesis testing was conducted using Pratt-adjusted Wilcoxon signed-rank tests, with effect magnitudes estimated via Hodges-Lehmann median differences and paired Cohen's $d_z$, controlling family-wise error rates across comparisons via Holm-Bonferroni correction."*

---

## 3. Task 3 — Geometric Equivalence Formulation (A1 vs. A2)

### 3.1 Clarification of the Evidence
In Experiment A:
- Condition A1: Turn-unaware state-expanded $A^*$ ($P_{\text{turn}} = 0$, operating on directed edge states $(u, v)$).
- Condition A2: Turn-unaware node-level $A^*$ (operating on physical vertex space $V$).

The frozen experimental results ([`phase_13_1_stage_2B_full_ablation_report.md#Section-2`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md#Section-2)) establish that across all 25 corridors:
- Route vertex sequences are **100% identical** (`route_A1 == route_A2` for $25 / 25$ corridors).
- Physical route distances are identical ($7.723\text{ km}$ mean across both conditions).
- Sharp turn counts are identical ($32.52$ mean across both conditions).
- Accumulated impedance costs are identical ($9,325.87$ mean across both conditions).

### 3.2 Removal of Redundant Hypothesis Test Citation
Because route identity is a **deterministic equality of discrete vertex sequences** across the entire corpus, citing a hypothesis test $p$-value ($p_{\text{adj}} = 1.0000$, which was computed on the degenerate zero-difference vector of sharp turns) is redundant and methodologically awkward.

### 3.3 Authoritative Formulation for Paper 1
> **Geometric Equivalence Statement:**  
> *"When turn penalties are inactive ($P_{\text{turn}} = 0$), state-expanded $A^*$ (Condition A1) and standard vertex-space $A^*$ (Condition A2) produce identical route geometries (identical node sequences, physical distances, and impedance costs) across all 25 evaluated corridors. This establishes that the state-expanded graph formulation itself introduces zero geometric distortion, and that the observed $34.1\%$ sharp-turn reduction (Condition A0 vs. A1: $21.44$ vs. $32.52$ turns, mean difference $-11.08$ turns, Holm-adjusted $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$) is purely attributable to turn-penalty evaluation."*

---

## 4. Itemized Summary of Corrections Applied in Phase 3.5

| Issue # | Domain | Prior Phase 3.4 Formulation | Phase 3.5 Validated Formulation | Protocol Justification |
| :---: | :--- | :--- | :--- | :--- |
| **VAL-01** | **Heap Operation Complexity** | $\mathcal{O}(|E| \cdot d_{\max} \log |E|)$ | $\mathcal{O}\left( |E| \cdot d_{\max}^{\text{in}} \cdot (\log |E| + \log d_{\max}^{\text{in}}) \right)$ | Accounts for the conservative logarithmic factor based on maximum heap capacity $|\text{open\_set}|_{\max} \le |E| \cdot d_{\max}^{\text{in}}$. Simplifies to $\mathcal{O}(|E| \log |E|)$ under bounded valence. |
| **VAL-02** | **Stale Pop Dynamics** | Stale entries iterate successors bounded by $|E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$. | Proved that stale entries cannot cause further relaxations because `current_cost` is already minimized, evaluating `new_cost < g_score[next]` strictly to `False`. | Explains why stale entries add $\mathcal{O}(|E|)$ work but zero heap insertions. |
| **VAL-03** | **Statistical Phrasing** | *"Methodologically mandating non-parametric median and Wilcoxon reporting."* | Separated observed empirical skew, robust descriptive statistics (median/IQR), and the pre-specified paired non-parametric testing protocol. | Eliminates implication that skewness mathematically mandates a specific hypothesis test. |
| **VAL-04** | **A1 vs A2 Equivalence** | Cited $p_{\text{adj}} = 1.0000$ for route equivalence. | Directly reports deterministic identity of vertex sequences, distances, and impedance costs across $25 / 25$ corridors. | Deterministic sequence equality should not be conflated with a degenerate Wilcoxon test. |

---

*Specification verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
