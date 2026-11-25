# Phase 4.3 — Final Paper 1 Blueprint Freeze Log

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 4.3 — Final Paper 1 Blueprint Freeze  
**Target:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Date:** 2026-11-05  
**Document:** [`phase_4_3_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/phase_4_3_freeze_log.md)  
**Parent Logs:** [`phase_3_6_correction_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_6_correction_log.md), [`paper1_blueprint_feasibility_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_blueprint_feasibility_audit.md)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **OFFICIAL BLUEPRINT FREEZE DECLARATION**

---

## 1. Executive Summary

Phase 4.3 executes the final review and formal freeze of the manuscript blueprint for Paper 1. All structural, feasibility, typographical, and claim boundary corrections identified in Phases 4.1 and 4.2 have been audited and incorporated into the authoritative v1.0 specifications. 

The manuscript blueprint is now **OFFICIALLY FROZEN** for Phase 5 (Manuscript Authoring).

---

## 2. Itemized Freeze Actions and Reconciliations

| Action ID | Domain | Prior Phase 4.2 Formulation | Final Phase 4.3 Frozen Formulation | Protocol & Scientific Justification |
| :---: | :--- | :--- | :--- | :--- |
| **FRZ-01** | **Safety & Collision Removal** | Contained passing references linking arterial exposure to "collision vulnerability" and "rider safety." | **Completely purged.** The introduction frames mixed traffic purely in terms of physical traffic engineering operational characteristics: turning maneuver counts across mixed traffic streams, and speed differentials on multi-lane arterials ([1], [2]). | Under [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), our study measured zero collision, trauma, or accident data. Implying our routes improve safety violates construct validity. |
| **FRZ-02** | **Literature Gap Demarcation** | Replaced the imprecise phrase *"zero empirical gaps"* from early notes. | Disentangled into three rigorous categories: (1) verified experimental evidence (frozen 25-corridor ablation); (2) literature-supported algorithmic gap (lack of turn-aware heuristic search coupled with vehicle impedance); (3) remaining limitations (compound 0.76 theoretical floor, single-city empirical scope, unmeasured dynamic congestion). | Merely freezing experimental results does not eliminate scientific limitations or prove universal generalizability. |
| **FRZ-03** | **Six-Page Budget Targets** | Proposed 3,550 words + 7 floats (infeasible in IEEE 2-column format). | Frozen targets: **$\approx 2,850\text{ body words}$**, $\approx 220$ abstract words, 3 figures, 2 tables, 6 display equations, 16 references. Total footprint: $\approx 3,420\text{ words equivalent}$. | Guarantees that compiled LaTeX PDF terminates on Page 6 without spilling into Page 7. |
| **FRZ-04** | **Emergency Trimming Protocol** | Undefined float reduction during compilation. | Established a pre-ranked 5-step emergency trimming sequence providing up to $320\text{ words equivalent}$ ($0.75\text{ column}$) of headroom if compiled layout exceeds 6.0 pages. | Ensures deterministic, non-destructive layout adjustment during LaTeX typesetting. |
| **FRZ-05** | **Claims & Citations Traceability** | Narrative claims lacked formal external vs. internal categorization. | Generated [`paper1_claims_and_citations_checklist.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_claims_and_citations_checklist.md) separating 16 external literature claims (anchored to verified BibTeX keys) from 10 internal experimental claims (anchored to frozen Phase 13.4 CSV artifacts). | Enforces strict evidentiary traceability for every sentence drafted in Phase 5. |

---

## 3. Preservation of Codebase and Frozen Artifacts

In strict adherence to the project protocol:
- **Codebase Preserved:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) and [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) remain 100% untouched.
- **Frozen Experimental Datasets Preserved:** All raw JSON, CSV, and report files in `research/literature_survey/13_ablation_study/` remain 100% unaltered.
- **Master Bibliography Preserved:** [`research/paper1_literature/paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib) remains completely intact.
- **Paper 2 Boundary Enforced:** Figure 4 (`fig4_exp_e_alternatives.png`) and Abraham et al. (`abraham2013alternative`) remain strictly excluded from Paper 1 and reserved exclusively for Paper 2.

---

## 4. Declaration of Freeze

The following documents constitute the **frozen authoritative baseline** for Paper 1 authoring:
1. **Structural Specification:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)
2. **Page & Space Allocation:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)
3. **Traceability Checklist:** [`paper1_claims_and_citations_checklist.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_claims_and_citations_checklist.md)
4. **Visual & Tabular Inventory:** [`paper1_final_visual_inventory.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_visual_inventory.md)
5. **Verified Citations:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)

*Blueprint freeze officially declared under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
