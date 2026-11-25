# Section II: Related Work (Subsections II-A and II-B) Evidence and Word-Count Audit (v1.2 Revised)

**Document:** [`paper1_related_work_IIA_IIB_evidence_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_evidence_audit.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Audited Draft:** [`paper1_related_work_IIA_IIB_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_v1.md) (v1.2)  
**Parent Outline:** [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md) (v1.1)  
**Parent Citation Map:** [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md) (v1.4)  
**Master Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Frozen Introduction:** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) (468 words)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 6.2.1-R2 REVISED EVIDENCE AUDIT COMPLETE (AWAITING LEAD APPROVAL)**  
**Effective Date:** 2026-11-06  

---

## 1. Executive Summary & Phase 6.2.1-R2 Historical Precision Correction

This audit certifies the final historical precision correction required by the Research Lead under Phase 6.2.1-R2:

- **Kirby and Potts (1969) Historical Claim Refinement (II-A):**
  - *Previous Wording:* "Turn restrictions and delays originated in macroscopic traffic assignment, where Kirby and Potts \cite{kirby1969minimum} expanded intersections into directed movement links to enforce turn prohibitions during tree-building."
  - *Evidentiary Issue:* The phrase "originated in macroscopic traffic assignment" asserted an unverified historical priority/origin claim about the emergence of turn modeling in the broader field.
  - *Approved Correction Applied:* Replaced with:  
    > "Movement-expanded representations have been used in macroscopic traffic assignment, where Kirby and Potts \cite{kirby1969minimum} expanded intersections into directed movement links to enforce turn prohibitions during tree-building."
  - *Source Verification:* Kirby and Potts (1969), Section 2 (pp. 398–401) and Section 3 (pp. 401–404), directly demonstrates the expansion of intersections into directed movement links to enforce turn prohibitions during tree-building in traffic assignment. The revised statement accurately describes this historical usage without claiming global disciplinary origin.

---

## 2. Word Count and Page Budget Verification

The word count for Subsection II-A remains exactly 89 words, as the replacement phrase matches the word count of the superseded text:

| Subsection | Stated Target Budget | Actual Word Count (Whitespace Split) | Variance | Budget Status |
| :--- | :---: | :---: | :---: | :---: |
| **Subsection II-A** | ~90 words | **89 words** | $-1$ word | **PASSED (Exact Fit)** |
| **Subsection II-B** | ~80 words | **83 words** | $+3$ words | **PASSED (Exact Fit)** |
| **Combined II-A + II-B** | **~170 words** | **172 words** | **$+2$ words** | **PASSED (Exact Fit)** |

---

## 3. Granular Sentence-by-Sentence Claim-to-Evidence Mapping

### Subsection II-A: Shortest-Path Routing and Turn-Aware State Representations (89 words)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          SUBSECTION II-A EVIDENCE MAPPING                                              │
├─────────────────────────────────────────────────┬─────────────────────────┬──────────────┬─────────────────────────────┤
│ Sentence Text                                   │ Citation Key            │ Support Type │ Supporting Source Passage   │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Movement-expanded representations have been    │ kirby1969minimum        │ DIRECT       │ Kirby & Potts (1969),       │
│ used in macroscopic traffic assignment, where   │                         │ DEMONSTRATED │ Sec 2 (pp. 398–401) &       │
│ Kirby and Potts \cite{kirby1969minimum}         │                         │ (ESSENTIAL)  │ Sec 3 (pp. 401–404):        │
│ expanded intersections into directed movement   │                         │              │ Movement-expanded networks  │
│ links to enforce turn prohibitions during       │                         │              │ for turn prohibitions in    │
│ tree-building."                                 │                         │              │ assignment tree-building.   │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "For shortest-path planning, Winter             │ winter2002modeling      │ DIRECT       │ Winter (2002),              │
│ \cite{winter2002modeling} formalized dual line  │                         │ DEMONSTRATED │ Sec 3 (pp. 348–352) &       │
│ graphs, showing that treating directed edges    │                         │ (ESSENTIAL)  │ Sec 4 (pp. 353–356):        │
│ as vertices allows transition costs between     │                         │              │ Dual line-graph formulation │
│ consecutive segments to reflect turn            │                         │              │ mapping directed edges to   │
│ characteristics."                               │                         │              │ vertices to evaluate turns. │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "While macroscopic assignment models compute    │ [Methodological         │ METHOD       │ Kirby & Potts (1969) Sec 4  │
│ aggregate flows over pre-expanded networks,     │ distinction]            │ SYNTHESIS    │ (aggregate assignment) vs.  │
│ point-to-point algorithms can evaluate turn     │                         │ (CONTEXTUAL) │ point-to-point shortest-path│
│ penalties directly during traversal."           │                         │              │ traversal algorithms.       │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Geisberger and Vetter \cite{geisberger2011     │ geisberger2011efficient │ DIRECT       │ Geisberger & Vetter (2011), │
│ efficient} analyzed point-to-point turn-aware   │                         │ DEMONSTRATED │ Sec 1–3 (pp. 100–105):      │
│ routing, evaluating trade-offs between          │                         │ (ESSENTIAL)  │ Analysis of edge-based      │
│ expanded edge graphs and compact node           │                         │              │ graphs vs. compact node     │
│ representations."                               │                         │              │ representations with turns. │
└─────────────────────────────────────────────────┴─────────────────────────┴──────────────┴─────────────────────────────┘
```

---

### Subsection II-B: Hierarchical Routing and Metric Customization (83 words)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          SUBSECTION II-B EVIDENCE MAPPING                                              │
├─────────────────────────────────────────────────┬─────────────────────────┬──────────────┬─────────────────────────────┤
│ Sentence Text                                   │ Citation Key            │ Support Type │ Supporting Source Passage   │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Hierarchical speedup techniques accelerate     │ bast2016route           │ CONTEXTUAL   │ Bast et al. (2016),         │
│ routing queries by pre-computing shortcuts      │                         │ SURVEY       │ Sec 2.4 (pp. 9–11) &        │
│ over base road networks \cite{bast2016route}."  │                         │ (ESSENTIAL)  │ Sec 3.1 (pp. 25–26):        │
│                                                 │                         │              │ Overview of speedup via     │
│                                                 │                         │              │ pre-computed shortcut tiers.│
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "For turn-dependent routing, Geisberger and     │ geisberger2011efficient │ DIRECT       │ Geisberger & Vetter (2011), │
│ Vetter \cite{geisberger2011efficient} extended  │                         │ DEMONSTRATED │ Sec 3–4 (pp. 102–108):      │
│ Contraction Hierarchies, constructing shortcuts │                         │ (ESSENTIAL)  │ Augmented node contraction; │
│ that account for turn costs across contracted   │                         │              │ shortcuts constructed to    │
│ nodes."                                         │                         │              │ respect junction turn costs.│
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "To support metric updates without repeating    │ delling2017customizable │ DIRECT       │ Delling et al. (2017),      │
│ full preprocessing, Customizable Route Planning │ bast2016route           │ DEMONSTRATED │ Sec 2–4 (pp. 568–582);      │
│ \cite{delling2017customizable} and customizable │                         │ (ESSENTIAL)  │ Bast et al. (2016), Sec 2.3 │
│ hierarchies \cite{bast2016route} decouple       │                         │              │ (pp. 8–9): Decoupling       │
│ metric-independent partitioning from a fast     │                         │              │ topology from customization.│
│ customization phase."                           │                         │              │                             │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Where vehicle-specific impedance and flyover   │ [Architectural          │ DESIGN       │ Comparative architectural   │
│ overrides are configured directly,              │ positioning]            │ POSITIONING  │ trade-off between hierarchy │
│ uncontracted state-expanded search provides an  │                         │ (CONTEXTUAL) │ customization phases and    │
│ alternative engineering trade-off that operates │                         │              │ uncontracted search on base │
│ on base graphs without intermediate             │                         │              │ graphs with static costs.   │
│ customization."                                 │                         │              │                             │
└─────────────────────────────────────────────────┴─────────────────────────┴──────────────┴─────────────────────────────┘
```

---

## 4. Master Bibliography Verification

All cited keys in Subsections II-A and II-B are verified against [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib):

| Citation Key | Primary Author & Year | Formally Verified Venue | Matched in `.bib` | Audit Status |
| :--- | :--- | :--- | :---: | :---: |
| `kirby1969minimum` | Kirby & Potts (1969) | *Transportation Research*, 3(3) | **YES** | **VERIFIED** |
| `winter2002modeling` | Winter (2002) | *GeoInformatica*, 6(4) | **YES** | **VERIFIED** |
| `geisberger2011efficient` | Geisberger & Vetter (2011) | *Proc. SEA*, LNCS 6630 | **YES** | **VERIFIED** |
| `bast2016route` | Bast et al. (2016) | *Algorithm Engineering*, LNCS 9220 | **YES** | **VERIFIED** |
| `delling2017customizable` | Delling et al. (2017) | *Transportation Science*, 51(2) | **YES** | **VERIFIED** |

- **New References Introduced:** **Zero (0).**

---

## 5. Scope-Boundary and Protocol Compliance Verification

| Guarded Research Boundary | Audit Rule / Prohibition | Compliance in Revised II-A & II-B Prose | Audit Status |
| :--- | :--- | :--- | :---: |
| **Origin / Priority Claims** | NO claims that turn modeling or movement-expanded networks originated in traffic assignment. | Reframed strictly to: "Movement-expanded representations have been used in macroscopic traffic assignment..." | **PASSED** |
| **Safety Claims** | NO claims of safety improvements, accident reduction, crash mitigation, or fatality drops. | Confined strictly to turn angles, restrictions, and graph topology. | **PASSED** |
| **Mobility Claims** | NO claims of unmeasured travel-time savings or city-wide congestion reduction. | Confined strictly to query acceleration and traversal. | **PASSED** |
| **Hierarchical Bias** | Do NOT portray hierarchical methods as inherently rigid or uncontracted search as superior. | Explicitly credited CRP/CCH fast metric customization; framed uncontracted search as an alternative engineering trade-off. | **PASSED** |
| **Real-Time Claims** | Do NOT imply real-time cost updates in this paper. | Purged all dynamic cost references; scoped strictly to configured vehicle-specific costs. | **PASSED** |
| **Paper 2 Scope Leakage** | NO alternative routing, Yen's KSP, route diversity, or perpendicular offset. | Completely excluded from both subsections. | **PASSED** |
| **Introduction Freeze** | Section I must remain verbatim frozen. | Confirmed: [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) was **not modified** (468 words). | **PASSED** |
| **Staged Boundary** | Subsections II-C and II-D must NOT be drafted. | Confirmed: Only II-A and II-B drafted; II-C and II-D remain unwritten. | **PASSED** |

---

## 6. Certification and Stop Condition

- **Drafted Deliverable:** [`paper1_related_work_IIA_IIB_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_v1.md) (v1.2, 172 words total: II-A = 89 words, II-B = 83 words).
- **Evidence Audit Deliverable:** [`paper1_related_work_IIA_IIB_evidence_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_evidence_audit.md) (v1.2).
- **Execution Log Deliverable:** [`phase_6_2_1_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_6_2_1_execution_log.md) (v1.2).

**STOP:** Phase 6.2.1-R2 correction complete. Subsections II-C and II-D have NOT been drafted. Full Section II has NOT been assembled. Section I remains frozen. Awaiting Research Lead instructions.
