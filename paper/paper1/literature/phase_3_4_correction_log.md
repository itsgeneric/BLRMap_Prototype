# Phase 3.4 — Itemized Claim Wording and Complexity Correction Log

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.4 — Final Complexity and Claim Wording Corrections  
**Target:** Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Date:** 2026-11-05  
**Document:** [`phase_3_4_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_correction_log.md)  
**Parent Audits:** [`phase_3_2_complexity_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_2_complexity_audit.md), [`phase_3_3_claim_boundary_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_3_claim_boundary_audit.md), [`phase_3_4_final_complexity_derivation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_final_complexity_derivation.md)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **FINAL AUDIT TRAIL AND RECONCILIATION**

---

## Executive Summary

Phase 3.4 completes the comprehensive verification of Paper 1's technical claims, mathematical proofs, algorithmic complexity bounds, and experimental comparative language. This log documents every specific modification made to reconcile preliminary draft statements with source-code reality and the frozen Phase 13.4 experimental ablation datasets.

---

## 1. Itemized Correction Matrix

| Item # | Target Domain | Preliminary / Unqualified Wording | Corrected Authoritative Wording | Source of Verification | Audit Justification |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **COR-01** | **Heuristic Terminology** | *"The scaled Haversine heuristic is strictly admissible..."* | *"The scaled Haversine heuristic is **admissible** ($h(s) \le c^*(s)$)..."* | Hart, Nilsson, & Raphael (1968); Russell & Norvig | In standard computer science and artificial intelligence literature, admissibility requires weak inequality ($h(n) \le c^*(n)$). The phrase "strictly admissible" erroneously implies strict inequality ($h(n) < c^*(n)$), which contradicts the goal state identity $h(t) = c^*(t) = 0$. |
| **COR-02** | **Heuristic Lower-Bound Condition** | *"Heuristic admissibility holds unconditionally for road networks."* | *"Heuristic admissibility is guaranteed under the condition that composite edge multipliers satisfy $\mu(e) \ge 0.80$ (verified across all 744,216 directed edges in the Bengaluru network)."* | [`routing/algorithms.py#L309-L331`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L331); [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) | Sequential execution allows bridge ($0.80$) and roundabout ($0.95$) modifiers to compound to $0.76$ if both tags coexist. While zero instances exist in Bengaluru, the mathematical theorem must be stated conditionally on Assumption A1 ($\mu(e) \ge 0.80$). |
| **COR-03** | **State Space Finality vs Multiplicity** | *"Intersection nodes are never reopened."* | *"Directed edge states $(u, v)$ are finalized upon initial heap extraction without reopening; physical intersections $v$ are expanded up to $\text{in-deg}(v)$ times across distinct arrival headings."* | [`routing/algorithms.py#L482-L485`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L482-L485); Theorem 2 and Corollary 1 | Avoids confusing state-space finality with physical node expansions. Multi-arrival expansion of physical intersections is the intended mechanism of state-expanded routing, not an algorithmic defect. |
| **COR-04** | **Priority Queue & Memory Complexity** | *"Auxiliary memory is unconditionally $\mathcal{O}(\|E\|)$."* | *"Auxiliary memory is $\mathcal{O}(\|E\| \cdot d_{\max}^{\text{in}})$ in general directed graphs, and strictly $\mathcal{O}(\|E\|)$ on spatial road networks where physical junction valence is bounded ($d_{\max} = \mathcal{O}(1)$)."* | [`routing/algorithms.py#L536-L700`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L536-L700); [`phase_3_4_final_complexity_derivation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_final_complexity_derivation.md) | Python's standard `heapq` lacks an addressable `decrease-key` operation. Multiple entries for a single state can coexist in `open_set`, bounded by in-degree valence. The $\mathcal{O}(\|E\|)$ bound holds strictly under Assumption A2 ($d_{\max} = \mathcal{O}(1)$). |
| **COR-05** | **Stale Pop Iteration Accounting** | *"Stale entries are purged from the priority queue."* | *"Stale entries are not filtered at pop time and execute successor iterations (bounded by $\|E\| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$); they are lazily suppressed from generating further pushes because relaxation checks fail against previously minimized $g$-scores."* | [`routing/algorithms.py#L552-L682`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L552-L682) | Code contains no `if priority > g_score: continue` guard. Stale entries consume pop cycles and iterate through graph successors, but perform $\mathcal{O}(1)$ work per iteration and push zero new entries. Asymptotic time remains $\mathcal{O}(\|E\| \log \|E\|)$ under bounded valence. |
| **COR-06** | **Experimental Comparator Precision** | *"Turn-aware A* eliminates 34.1% of sharp turns relative to standard routing."* | *"Turn-aware state-expanded A* (Condition A0) eliminates 34.1% of sharp maneuvers ($\ge 60^\circ$) relative to **turn-unaware state-expanded routing (Condition A1)**: $21.44$ vs $32.52$ turns ($p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$)."* | [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv); [`phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md) | Replaces ambiguous "standard routing" with the exact experimental condition (A1). Note that A1 and A2 (node-level A*) produce 100% geometrically identical routes ($25/25$ zero diffs, $p=1.0$), making A1 the exact paired control isolating the turn penalty. |
| **COR-07** | **Baseline Runtime Figure** | *"The routing engine operates with an average runtime of 187.62 ms."* | *"The production turn-aware engine operates with a **median runtime of $174.93\text{ ms}$** (IQR: $439.08\text{ ms}$, mean: $382.98\text{ ms} \pm 464.48\text{ ms}$) across 25 corridors."* | [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv); [`exp_d_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv) | $187.62\text{ ms}$ belongs to ablated condition D1 (`Bridge Off, Roundabout Off`) in Experiment D. Production baseline A0 is strictly $174.93\text{ ms}$ median. |
| **COR-08** | **Runtime Skewness Attribution** | *"Runtime right-skewness is caused by $\mathcal{O}(R^2)$ search-area growth."* | *"Runtimes exhibit a heavily right-skewed empirical distribution across distance tiers (Short: $1.01\text{--}18.42\text{ ms}$; Medium: $110.50\text{--}245.80\text{ ms}$; Long: $850.12\text{--}1,829.18\text{ ms}$), methodologically mandating non-parametric median and Wilcoxon reporting."* | [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv); Protocol Phase 13.4 | Under research integrity protocols, attributing skewness to $\mathcal{O}(R^2)$ spatial expansion without empirical spatial search-cone profiling is an unverified hypothesis. The distribution must be reported strictly as an empirical measurement. |

---

## 2. Summary of Frozen Experimental Evidence Preserved

All frozen experimental figures from Phase 13.4 remain strictly preserved without alteration:
- **Experiment A ($N=25$ Corridors, $R=5$ Repetitions):**
  - A0 Sharp Turns: Mean $21.44$, Median $18.00$
  - A1 Sharp Turns: Mean $32.52$, Median $31.00$
  - A2 Sharp Turns: Mean $32.52$, Median $31.00$
  - Sharp Turn Reduction: $-11.08$ turns ($-34.1\%$), Pratt Wilcoxon $W = 0.0$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$, Hodges-Lehmann $-9.50$ turns [$-13.0, -7.0$]
  - A1 vs A2 Geometric Route Difference: **$0 / 25$ differences ($100\%$ identity, $p_{\text{adj}} = 1.0000$)**
  - A0 Median Runtime: **$174.93\text{ ms}$** (IQR: $439.08\text{ ms}$, Mean: $382.98\text{ ms}$)
  - A1 Median Runtime: **$154.69\text{ ms}$** (Mean: $341.63\text{ ms}$)
  - A2 Median Runtime: **$40.88\text{ ms}$** (Mean: $88.25\text{ ms}$)
  - State Expansion Runtime Ratio (A1 vs A2): **$3.78\times$ median overhead**
  - Turn Evaluation Runtime Ratio (A0 vs A1): **$1.13\times$ median overhead**
  - Total Production Runtime Ratio (A0 vs A2): **$4.28\times$ median overhead**
- **Experiment B ($N=25$ Corridors, $R=5$ Repetitions):**
  - Arterial Road Exposure: $65.05\%$ (Neutral B1) $\to$ $13.84\%$ (Production B0) ($-51.21\text{ pp}$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$)
  - Residential Road Exposure: $13.51\%$ (Neutral B1) $\to$ $44.24\%$ (Production B0) ($+30.73\text{ pp}$, $p_{\text{adj}} = 0.00015$, Cohen's $d_z = +1.5234$)
  - Detour Overhead: $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = +1.4883$)
- **Experiment C ($N=25$ Corridors, $R=5$ Repetitions):**
  - Sharp Turns across Tiers: $C_0 (0/0) = 32.52 \to C_1 (12/4) = 24.64 \to C_2 (25/8) = 21.44 \to C_3 (50/16) = 19.80$
  - Baseline C2 ($25/8$): Designated strictly as the **"empirical corpus-average trade-off knee"**, capturing $87.1\%$ of maneuver reduction while minimizing mean route distance ($7.648\text{ km}$). Non-dominated Pareto frontier is $\{C_2, C_3\}$.
- **Experiment D ($N=25$ Corridors, $R=5$ Repetitions):**
  - Elevated Bridge Traversal: $159.68\text{ m} \to 397.44\text{ m}$ ($+148.9\%$, distance reduction $-111.6\text{ m}$), concentrated on Hebbal (`OD_15`) and Whitefield (`OD_04`) flyovers.
  - Roundabout Modifier: $0$ route geometry shifts across non-roundabout corridors.

---

*Log verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
