# Phase 3.6 — Itemized Final Complexity and Scope Correction Log

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.6 — Final Complexity Bound and Claim Scope Check  
**Target:** Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Date:** 2026-11-05  
**Document:** [`phase_3_6_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_6_correction_log.md)  
**Parent Logs:** [`phase_3_5_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_5_correction_log.md), [`phase_3_4_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_correction_log.md)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **FINAL AUTHORITATIVE AUDIT LOG**

---

## 1. Itemized Phase 3.6 Corrections

| Item # | Technical Domain | Prior Formulation (Phase 3.5) | Corrected Formulation (Phase 3.6) | Methodological & Mathematical Justification |
| :---: | :--- | :--- | :--- | :--- |
| **COR-3.6-01** | **Heap Insertion Bound Formulation** | Max insertions bounded primarily as $|E| \cdot d_{\max}^{\text{in}}$. | Expressed as dual bounds: $|E_S| \le |E| \cdot d_{\max}^{\text{out}}$ (from departure expansions) and $|E_S| \le |E| \cdot d_{\max}^{\text{in}}$ (from arrival relaxations), tightly bound as $|E| \cdot \min(d_{\max}^{\text{in}}, d_{\max}^{\text{out}}) \le |E| \cdot d_{\max}^{\text{out}}$. | From the perspective of search progression, each of the $|E|$ states $(u, v)$ expands at most $d_{\text{out}}(v) \le d_{\max}^{\text{out}}$ outgoing edges upon its optimal pop. Summing across $|E|$ states directly yields $|E| \cdot d_{\max}^{\text{out}}$. Both algebraic formulations are rigorously reconciled. |
| **COR-3.6-02** | **Heap Capacity & Logarithmic Cost** | $|\text{open\_set}|_{\max} \le |E| \cdot d_{\max}^{\text{in}}$, with $\log(|E| \cdot d_{\max}^{\text{in}})$. | $|\text{open\_set}|_{\max} \le 1 + d_{\max}^{\text{out}} + |E| \cdot d_{\max}^{\text{out}}$, with logarithmic operation cost $\mathcal{O}(\log |E| + \log d_{\max}^{\text{out}})$. | Accurately aligns the priority queue capacity and logarithmic factor with the departure expansion bound $|E| \cdot d_{\max}^{\text{out}}$. |
| **COR-3.6-03** | **General Graph Time Complexity** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \log |E| + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$ | $\mathcal{O}\left( |E| \cdot d_{\max}^{\text{out}} \cdot (\log |E| + \log d_{\max}^{\text{out}}) + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right)$, or $\mathcal{O}(|E| \cdot d_{\max} \log |E| + |E| \cdot d_{\max}^2)$ with $d_{\max} = \max(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$. | Full mathematical precision accounting for both heap pushes/pops and stale successor loop iterations in arbitrary directed graphs. Under bounded valence, simplifies strictly to $\mathcal{O}(|E| \log |E|)$. |
| **COR-3.6-04** | **Scope of Geometric Equivalence** | *"This establishes that the state-expanded graph formulation itself introduces zero geometric distortion..."* | Limited strictly to the benchmark corpus: *"Across the 25 evaluated metropolitan corridors, Condition A1 and Condition A2 produced identical node sequences, physical distances, and impedance costs (`route_A1 == route_A2` for $25 / 25$ corridors), confirming that state expansion introduced zero route deviation across the evaluated benchmark corpus."* | Prevents unproven universal claims regarding all theoretical road networks; grounds the assertion strictly and defensibly in the frozen experimental data. |

---

## 2. Invariant Data and Code Preservation Check

In strict adherence to the project protocol:
- **Codebase:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) and [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) remain completely unaltered.
- **Frozen Experimental Datasets:** All datasets, test tables, and report artifacts in `research/literature_survey/13_ablation_study/` remain 100% untouched.
- **Key Empirical Invariants:**
  - Turn reduction: $34.1\%$ ($-11.08$ sharp turns, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$).
  - Road impedance: $-51.21\text{ pp}$ arterial exposure ($p_{\text{adj}} = 8.4 \times 10^{-5}$), $+30.73\text{ pp}$ residential routing ($p_{\text{adj}} = 0.00015$).
  - Baseline runtime: Median $174.93\text{ ms}$ (IQR: $439.08\text{ ms}$, Mean: $382.98\text{ ms} \pm 464.48\text{ ms}$, Range: $1.01\text{--}1,829.18\text{ ms}$, $N=25, R=5$).
  - Metropolitan graph: $|V| = 308,643$, $|E| = 744,216$, $d_{\max}^{\text{in}} = 6, d_{\max}^{\text{out}} = 6$, $|E_S| = 2,103,894$, $\min \mu(e) = 0.8000$.

---

*Log verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
