# Phase 3.5 — Itemized Technical Wording and Mathematical Correction Log

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.5 — Final Technical Wording Validation  
**Target:** Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Date:** 2026-11-05  
**Document:** [`phase_3_5_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_5_correction_log.md)  
**Parent Logs:** [`phase_3_4_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_correction_log.md), [`phase_3_3_claim_boundary_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_3_claim_boundary_audit.md)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE RECONCILIATION RECORD**

---

## 1. Itemized Phase 3.5 Corrections

| Item # | Technical Domain | Prior Formulation (Phase 3.4) | Corrected Formulation (Phase 3.5) | Methodological & Scientific Justification |
| :---: | :--- | :--- | :--- | :--- |
| **COR-3.5-01** | **Heap Operation Complexity** | $\mathcal{O}(|E| \cdot d_{\max} \log |E|)$ | $\mathcal{O}\left( |E| \cdot d_{\max}^{\text{in}} \cdot (\log |E| + \log d_{\max}^{\text{in}}) \right)$ | Fully accounts for maximum heap capacity $|\text{open\_set}|_{\max} \le |E| \cdot d_{\max}^{\text{in}} + d_{\max}^{\text{out}} + 1$. Each heap operation takes $\mathcal{O}(\log(|E| \cdot d_{\max}^{\text{in}}))$. Under bounded valence ($d_{\max} = \mathcal{O}(1)$), this simplifies strictly to $\mathcal{O}(|E| \log |E|)$. |
| **COR-3.5-02** | **Stale-Entry Invariance Proof** | Stale entries iterate successors without causing new pushes. | Derived formal step-by-step proof that because `current_cost` is already minimized, candidate cost evaluates identically to the earlier optimal pop, causing `new_cost < g_score[next_state]` to evaluate strictly to `False`. | Explains why stale entries add $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$ successor checks but zero heap insertions. |
| **COR-3.5-03** | **Statistical Phrasing on Runtime Skew** | *"The empirical runtime distribution is heavily right-skewed... methodologically mandating non-parametric median and Wilcoxon reporting."* | Disentangled into three precise statements: (1) empirically observed right-skew across distance tiers; (2) median and IQR chosen as robust descriptive metrics; (3) Pratt-adjusted Wilcoxon signed-rank test chosen for paired testing without assuming normality. | Skewness in descriptive data does not mathematically mandate a specific hypothesis test. The protocol's use of Wilcoxon testing is a pre-specified inferential choice for paired corridor comparisons under non-normal data. |
| **COR-3.5-04** | **Geometric Equivalence (A1 vs. A2)** | *"When turn penalties are zeroed, state-expanded A* (A1) and node-level A* (A2) produce 100% mathematically identical route geometries ($p_{\text{adj}} = 1.0000$)..."* | *"When turn penalties are inactive ($P_{\text{turn}} = 0$), state-expanded A* (Condition A1) and standard vertex-space A* (Condition A2) produce identical route geometries (identical node sequences, physical distances, and impedance costs) across all 25 evaluated corridors."* | $p_{\text{adj}} = 1.0000$ was computed on a degenerate zero-difference vector of turn counts. Deterministic equality of discrete vertex sequences across the corpus (`route_A1 == route_A2` for $25 / 25$ corridors) is reported directly as a deterministic identity without redundant $p$-value citation. |

---

## 2. Integrity and Data Preservation Summary

In strict compliance with [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md):
- **Source Code Integrity:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) and [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) remain 100% untouched.
- **Frozen Experimental Datasets:** All raw JSON, CSV, and summary reports in `research/literature_survey/13_ablation_study/` remain 100% untouched and preserved.
- **Statistical Invariants:** 
  - Turn reduction: $34.1\%$ ($-11.08$ sharp turns, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$, Hodges-Lehmann $-9.50$ turns).
  - Road-class impedance: $-51.21\text{ pp}$ arterial exposure ($p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$), $+30.73\text{ pp}$ residential routing ($p_{\text{adj}} = 0.00015$).
  - Runtime baseline: Median $174.93\text{ ms}$, IQR $439.08\text{ ms}$, Mean $382.98\text{ ms} \pm 464.48\text{ ms}$, Range $1.01\text{--}1,829.18\text{ ms}$ across $N=25$ corridors ($R=5$ repetitions).
  - Graph Topology: $|V| = 308,643$, $|E| = 744,216$, $d_{\max}^{\text{in}} = 6$, $d_{\max}^{\text{out}} = 6$, $|E_S| = 2,103,894$, $\min \mu(e) = 0.8000$.

---

*Log verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
