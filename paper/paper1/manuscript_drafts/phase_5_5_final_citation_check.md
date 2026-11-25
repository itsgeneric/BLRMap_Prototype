# Phase 5.5: Final Citation-Scope Verification and Word Count Reconciliation

**Document:** [`phase_5_5_final_citation_check.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_5_final_citation_check.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Canonical Assembled File:** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md)  
**Investigated Source:** Bast et al. (2016) [`\cite{bast2016route}`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/papers/10_Bast_2016_Route_Planning_Survey.pdf)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUDIT REPORT COMPLETE (AWAITING APPROVAL)**  
**Date:** 2026-11-05  

---

## 1. Executive Summary

This report performs a granular evidentiary audit of the original publication text of Bast et al. (2016) to verify the citation scope of the following statement in Paragraph 3 of the Introduction:

> *"For metric customization, customizable hierarchies support multi-attribute cost updates \cite{bast2016route}..."*

The investigation inspected the complete 65-page primary source text ([`10_Bast_2016_Route_Planning_Survey.pdf`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/papers/10_Bast_2016_Route_Planning_Survey.pdf)). In addition, a rigorous whitespace tokenization audit reconciles the Section I word count and resolves the prior 467/468 discrepancy.

---

## 2. Evidentiary Audit of Bast et al. (2016)

### 2.1. Bibliographic Reference
- **Citation Key:** `bast2016route`
- **Full Reference:** H. Bast, D. Delling, A. Goldberg, M. Müller-Hannemann, T. Pajor, P. Sanders, D. Wagner, and R. F. Werneck, "Route Planning in Transportation Networks," in *Algorithm Engineering: Selected Results and Surveys*, LNCS vol. 9220, Springer, 2016, pp. 19–80. DOI: [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2).
- **Physical Artifact Audited:** [`research/literature_survey/papers/10_Bast_2016_Route_Planning_Survey.pdf`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/papers/10_Bast_2016_Route_Planning_Survey.pdf) (65 pages).

---

### 2.2. Task 2(a): Metric Customization in Customizable Route-Planning Hierarchies
- **Claim:** Customizable hierarchies support metric customization.
- **Passage-Level Evidence in Primary Source:**
  1. **Section 2.3: Separator-Based Techniques — Arc Separators (Customizable Route Planning), pp. 8–9:**
     > *"The recent Customizable Route Planning (CRP) [76, 77] algorithm uses a similar approach, but is specifically engineered to meet the requirements of real-world systems... using a three-phase approach: metric-independent preprocessing, metric-dependent customization, and queries... The first phase computes, besides the multilevel partition, the topology of the overlays... Note that the partition does not depend on the cost function. The second phase (which takes the cost function as input) computes the costs of the clique arcs... This yields customization times of about one second on a 12-core CPU, which is still fast enough for many scenarios."* (pp. 8–9).
  2. **Section 3.1: Experimental Results — Performance on Road Networks, pp. 25–26:**
     > *"Table 2 (reproduced from [77]) compares CH and CRP with and without turn costs, as well as for travel distances... The table reports metric-independent preprocessing and metric-dependent customization separately... CRP query times are very robust to the cost function and the presence of turns. Also, a new cost function can be applied in roughly 370ms, fast enough to even support user-specific cost functions. Customization times can be even reduced to 36ms with GPUs [87]... enabling realistic personalized driving directions on continental scale."* (pp. 25–26).
  3. **Section 3.1 / Table 1, p. 21:**
     > Cites *Customizable Contraction Hierarchies (CCH)* [107] by Dibbelt, Strasser, and Wagner (2014) as a hierarchical approach separating topology from metric customization.
- **Audit Verdict on Claim 2(a):** **DIRECTLY AND FULLY SUPPORTED.** Bast et al. (2016) explicitly details three-phase customizable architectures (CRP and CCH) where a fast metric-dependent customization phase incorporates dynamic edge costs and turn costs into pre-computed topologies.

---

### 2.3. Task 2(b): The Stronger Claim of "Multi-Attribute Cost Updates"
- **Claim:** Customizable hierarchies support *multi-attribute cost updates*.
- **Investigation of Primary Source Terminology:**
  - An exhaustive text search of the 65-page document for terms containing `multi-attribute` yielded **0 occurrences**.
  - Mentions of `multicriteria` occur in:
    - **Section 2.7: Extensions — Multicriteria Search (pp. 17–18):** Defines Pareto-optimal shortest paths where multiple criteria (e.g., travel time and monetary cost) are evaluated simultaneously using Multicriteria Label-Setting (MLS) algorithms.
    - **Section 4.1 & Section 5.3: Multimodal Multicriteria Optimization (pp. 31–35, 44–45):** Discusses multi-criteria Pareto optimization in public transit and multimodal networks (e.g., RAPTOR, MCR).
  - In contrast, customizable hierarchies (CRP and CCH) discussed in Sections 2.3 and 3.1 operate on a **single scalarized cost function per customization phase** (such as travel time with turn costs, distance, or a user-specific linear combination). They do not perform simultaneous multi-attribute Pareto tracking during customization.
- **Audit Verdict on Claim 2(b):** **NOT DIRECTLY SUPPORTED.** Citing Bast et al. (2016) for "multi-attribute cost updates" in the context of customizable hierarchies is an imprecise over-extension that conflates metric customization (updating a single scalarized cost function) with multicriteria/multi-attribute Pareto optimization.

---

### 2.4. Recommended Text Correction

To ensure 100% adherence to verified primary evidence, the narrower and strictly supported wording is recommended:

- **Current Manuscript Prose (Paragraph 3):**
  > *"For metric customization, customizable hierarchies support multi-attribute cost updates \cite{bast2016route}, while empirical studies observe that two-wheeler riders utilize lower-tier street classes differently than passenger cars \cite{fadilah2024identifying}."*
- **Recommended Narrower Prose (Paragraph 3):**
  > *"For metric customization, customizable hierarchies support flexible metric updates \cite{bast2016route}, while empirical studies observe that two-wheeler riders utilize lower-tier street classes differently than passenger cars \cite{fadilah2024identifying}."*

#### Precision Analysis of Replacement:
1. Replaces `"multi-attribute cost updates"` (unsupported) with `"flexible metric updates"` (directly supported by Bast et al., Section 2.3, p. 9 and Section 3.1, p. 25).
2. Word count impact:
   - `"multi-attribute cost updates"` = 3 tokens.
   - `"flexible metric updates"` = 3 tokens.
   - **Net Token Delta: 0 words.** Paragraph 3 and Section I word counts remain completely unchanged.
3. **Execution Directive Status:** The manuscript has **not** been modified yet, in strict compliance with instruction 4 (*"Do not modify the manuscript yet"*).

---

## 3. Section I Word Count Reconciliation

### 3.1. Consistent Whitespace-Based Tokenization
Using Python's standard string tokenization (`len(paragraph.split())`), where every contiguous sequence of non-whitespace characters constitutes a token:

| Paragraph | Approved Content / Function | Exact Whitespace Count | Stated Count in Drafts | Target Budget Allocation |
| :--- | :--- | :---: | :---: | :---: |
| **Paragraph 1** | Two-Wheeler Context & Heterogeneous Traffic | **73 words** | 73 words | ~70 words |
| **Paragraph 2** | Vertex Limitations & Directed Edge States | **81 words** | 80 words | ~80 words |
| **Paragraph 3** | Turn-Cost Formulations & Speedup Techniques | **83 words** | 83 words | ~85 words |
| **Paragraph 4** | Scoped Motivation & Integrated Formulation | **59 words** | 59 words | ~55–65 words |
| **Paragraph 5** | Four Theoretical & Empirical Contributions | **124 words** | 124 words | ~115 words |
| **Paragraph 6** | Paper Organisation Roadmap (Sections II–VII) | **48 words** | 48 words | ~45 words |
| **Grand Total** | **Complete Introduction Footprint** | **468 words** | **467 words** | **450–470 words** |

---

### 3.2. Explanation of the 467 vs. 468 Word Discrepancy
The 1-word discrepancy between the stated draft count (467 words) and the automated whitespace split count (468 words) originates exclusively in **Paragraph 2**:

- In Paragraph 2, the LaTeX math expression for a directed edge transition is formatted as:
  `$(v, w)$`
- Under manual or semantic counting, `$(v, w)$` represents a single mathematical edge symbol, yielding **80 words** for Paragraph 2.
- Under strict whitespace tokenization (`paragraph.split()`), the space after the comma causes Python to split the expression into two separate tokens:
  - Token 38: `$(v,`
  - Token 39: `w)$`
  This increases the whitespace count for Paragraph 2 from 80 to **81 words**.
- Similarly, `$s=(u, v)$` splits into `$s=(u,` and `v)$`, and `$(u, v),` splits into `$(u,` and `v),`. The baseline draft count treated one of these as an atomic unit.
- **Reconciliation Verdict:** Both counting conventions confirm that Section I remains strictly compliant with the approved IEEE conference budget:
  - **Standard Whitespace Split:** **468 words** (Target: 450–470 words, Delta: $+3$ words / $+0.6\%$).
  - **Symbol-Normalized Split:** **467 words** (Target: 450–470 words, Delta: $+2$ words / $+0.4\%$).

---

## 4. Constraint and Boundary Verification

- **Manuscript Text:** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) has NOT been modified.
- **Reference Integrity:** No new references introduced. `paper1_verified_references.bib` remains untouched.
- **Negative Audits:** Zero prohibited claims (safety, travel-time, congestion, rider psychology); zero Paper 2 content.
- **Stop Directive:** Section II (Related Work) has not been opened.

---

*Report prepared and certified under Phase 5.5 research integrity protocol. Awaiting research lead instruction to apply the recommended Paragraph 3 wording update.*
