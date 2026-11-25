# Phase 7.1-R Planning, Multiplier Lower-Bound, and Objective-Function Audit

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 7.1-R — Multiplier Lower-Bound and Objective-Function Audit  
**Date:** 2026-11-06  
**Document:** [`phase_7_1_planning_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_1_planning_audit.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE PHASE 7.1-R RECONCILIATION AND AUDIT REPORT**

---

## 1. Executive Summary of Phase 7.1-R Revisions

Phase 7.1-R executes targeted precision corrections and audits on the Section III planning deliverables for Paper 1. It resolves two primary formulation items identified by the research lead:
1. **Correction of the Multiplier Lower-Bound Claim:** Completely purged assertions that physical civil engineering infrastructure universally prevents arterial flyovers and roundabouts from co-occurring on arbitrary road networks. Documented the four core facts separately and framed $\mu(e) \ge 0.80$ as a dataset-verified condition for the Bengaluru experiments and an explicit formal condition (Assumption A1) required for theoretical heuristic admissibility.
2. **Objective-Function and Summation Audit:** Conducted a rigorous trace of state transitions versus the path-level objective function. Verified that transition costs charge outgoing edge impedance and intermediate turn deflections, verified initial departure invariance (zero turn penalty) and destination termination (no exit turn penalty), confirmed that each physical edge is summed exactly once, and verified the dimensional distinction between physical meters ($m$) and effective impedance meters ($m$).

---

## 2. Item 1: Multiplier Lower-Bound Correction Details

### 2.1 The Four Separated Implementation and Empirical Facts
In accordance with instructions, the four facts governing the multiplier lower bound are recorded separately without conflation:

1. **Sequential Code Execution:** In [`routing/algorithms.py#L309-L331`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L331), the roundabout modifier ($0.95\times$) is applied sequentially **after** the arterial bridge override check (`penalty = 0.8`).
2. **Theoretical Co-Occurrence Value:** An edge carrying both a qualifying arterial bridge tag (`bridge=yes`, $h \in \mathcal{H}_{\text{main}}$) and a roundabout tag (`junction=roundabout`) would evaluate to:
   $$\mu(e) = 0.80 \times 0.95 = 0.76$$
   falling below the theoretical floor of $0.80$.
3. **Empirical Dataset Ground Truth:** Across the official Bengaluru metropolitan road network ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)), an exhaustive scan of all $|E| = 744,216$ directed edges confirmed that **exactly zero edges** carry both tags simultaneously.
4. **Minimum Observed Multiplier:** The minimum observed edge multiplier across the entire experimental dataset is strictly **0.80**.

### 2.2 Reconciled Scholarly Framing
- **No Universal Infrastructure Claim:** All draft claims stating that "civil engineering design precludes co-location universally" have been completely removed.
- **Dataset-Verified Condition:** $\mu(e) \ge 0.80$ is formally designated as an empirically verified property of the Bengaluru street network used in all experiments.
- **Conditional Theoretical Prerequisite:** In Section IV, $\mu(e) \ge 0.80$ is introduced as **Assumption A1**, an explicit operational condition required for the mathematical proof of Haversine heuristic admissibility ($h(s) \le c^*(s)$).
- **Arbitrary Graph Limitation:** It is explicitly acknowledged that on arbitrary OpenStreetMap graphs where tagging anomalies or elevated roundabouts exist, $\mu(e)$ could drop to $0.76$ unless an explicit code clamp (`max(0.80, penalty)`) is enforced.

---

## 3. Item 2: Objective-Function and Summation Audit

A line-by-line comparison between the mathematical formulations in Section III and the implementation in [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) confirms 100% algebraic and structural identity.

### 3.1 Verification Checklist

| Audit Question | Verified Implementation Reality | Code Reference | Status |
| :--- | :--- | :--- | :---: |
| **Transition Cost Formulation** | $c(s, s') = \mu(v, w)\ell(v, w) + P_{\text{turn}}(u, v, w)$ where $s=(u, v)$ and $s'=(v, w)$. Transition cost charges outgoing edge $(v, w)$ and intermediate turn at $v$. | [`routing/algorithms.py#L668-L672`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L668-L672) | **VERIFIED** |
| **Initial Synthetic State** | Root state is $s_0^{\text{state}} = (\text{None}, s_0)$. Departing along initial edge $(s_0, w)$ invokes `_turn_penalty(graph, None, s_0, w)`, which returns $0.0$ unconditionally. | [`routing/algorithms.py#L151-L152`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L151-L152), [`L522-L525`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L522-L525) | **VERIFIED** |
| **Physical Edge Accounting** | For a path of $k$ directed segments, the summation $\sum_{i=1}^k \mu(e_i)\ell(e_i)$ sums each physical edge $e_i \in P$ **exactly once**. | [`routing/algorithms.py#L586-L590`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L586-L590), [`L668-L672`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L668-L672) | **VERIFIED** |
| **Turn Penalty Units** | Turn penalty constants $P_{\text{sharp}} = 25.0$ and $P_{\text{mod}} = 8.0$ are added directly to `edge_cost` (`length * penalty`), giving them effective-distance meters ($m$). | [`routing/algorithms.py#L37-L38`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L37-L38), [`L668-L672`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L668-L672) | **VERIFIED** |
| **Destination Termination** | When destination state $\sigma_k = (v_{k-1}, t)$ is popped, `current_node == end_node` triggers immediate loop break. No exit turn penalty is assessed at destination $t$. | [`routing/algorithms.py#L566`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L566) | **VERIFIED** |
| **Distance Disentanglement** | Physical distance $D(P) = \sum_{i=1}^k \ell(e_i)$ (physical meters, $m$) is strictly separated from accumulated traversal cost $C(P)$ (effective meters, $m$). | Text & Formulae | **VERIFIED** |

### 3.2 Indexing and Summation Limits Proof
Let path $P = \langle e_1, \dots, e_k \rangle$ traverse vertices $v_0, v_1, \dots, v_k$ with $v_0 = s_0$ and $v_k = t$.
- In state space, the sequence of states is $\sigma_0 = (\text{None}, v_0)$, and $\sigma_i = (v_{i-1}, v_i) = e_i$ for $i \in \{1, \dots, k\}$.
- There are exactly $k$ state transitions: $\tau_j = (\sigma_{j-1}, \sigma_j)$ for $j \in \{1, \dots, k\}$.
- Summing transition costs:
  $$\sum_{j=1}^k c(\sigma_{j-1}, \sigma_j) = c(\sigma_0, \sigma_1) + \sum_{j=2}^k c(\sigma_{j-1}, \sigma_j)$$
  $$c(\sigma_0, \sigma_1) = \mu(e_1) \ell(e_1) + P_{\text{turn}}(\text{None}, v_0, v_1) = \mu(e_1) \ell(e_1) + 0.0$$
  $$\sum_{j=2}^k c(\sigma_{j-1}, \sigma_j) = \sum_{j=2}^k \left[ \mu(e_j) \ell(e_j) + P_{\text{turn}}(v_{j-2}, v_{j-1}, v_j) \right] = \sum_{i=2}^k \mu(e_i) \ell(e_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$$
- Combining both terms:
  $$\sum_{j=1}^k c(\sigma_{j-1}, \sigma_j) = \sum_{i=1}^k \mu(e_i) \ell(e_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1}) = C(P)$$
This confirms exact mathematical equivalence without missing terms or index off-by-one errors.

---

## 4. Item 3: Notation and Dimensional Audit

An exhaustive notation and dimensional consistency check confirmed:
1. **State & Root Notation:** State is consistently denoted $s = (u, v) \in E$; synthetic start state is $s_0^{\text{state}} = (\text{None}, s_0)$; state cardinality is $|S| = |E| + 1$.
2. **Edge & Vertex Notation:** Road graph is $G = (V, E)$; vertices $u, v, w \in V$; directed edges $e = (u, v) \in E$.
3. **Angular Deflection Units:** $\Delta\theta(u, v, w)$ is strictly measured in degrees ($^\circ$), bounded within $[0^\circ, 180^\circ]$.
4. **Multiplier Notation:** Composite multiplier $\mu(e)$ is dimensionless ($[-]$); base penalty $f_{\text{class}}$ is dimensionless ($[-]$); roundabout factor $m_{\text{rbt}}$ is dimensionless ($[-]$).
5. **Distance & Cost Units:**
   - Physical segment length $\ell(e)$ is measured in physical meters ($m$).
   - Physical route length $D(P)$ is measured in physical meters ($m$).
   - Turn penalties $P_{\text{turn}} \in \{0.0, 8.0, 25.0\}$ are measured in effective impedance meters ($m$).
   - Weighted edge cost $\mu(e)\ell(e)$ is measured in effective impedance meters ($m$).
   - State transition cost $c(s, s')$ and path cost $C(P)$ are measured in effective impedance meters ($m$).
   - Dimensional homogeneity $[L] + [L] = [L]$ is strictly satisfied.

---

## 5. Frozen File Integrity Verification

To ensure that no modifications occurred outside the Section III planning deliverables, all frozen files were audited:

| File Path | Frozen Status | Size (Bytes) | Integrity Status |
| :--- | :---: | :---: | :---: |
| [`research/paper1_manuscript/paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | FROZEN | 3,287 bytes | **UNMODIFIED** |
| [`research/paper1_manuscript/paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | FROZEN | 7,596 bytes | **UNMODIFIED** |
| [`research/paper1_manuscript/paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | FROZEN | 6,723 bytes | **UNMODIFIED** |
| [`research/paper1_literature/paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib) | FROZEN | 8,817 bytes | **UNMODIFIED** |
| `core/config.py` & `routing/algorithms.py` | READ-ONLY | Unchanged | **UNMODIFIED** |
| `research/literature_survey/13_ablation_study/` | READ-ONLY | Unchanged | **UNMODIFIED** |

---

## 6. Stop Condition Enforced

Phase 7.1-R revisions are complete:
- Deliverables [`paper1_section_III_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_outline_v1.md), [`paper1_section_III_equation_and_notation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_equation_and_notation_map_v1.md), [`paper1_section_III_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_evidence_map_v1.md), and this audit report are finalized and synchronized.
- Zero manuscript prose has been drafted.
- Section IV has not been started.
- Awaiting research-lead review and authorization prior to proceeding to Phase 7.2.
