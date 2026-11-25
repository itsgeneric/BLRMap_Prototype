# Phase 5.5: Section I (Introduction) Assembly Integrity and Evidentiary Audit

**Document:** [`phase_5_5_assembly_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_5_assembly_audit.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Canonical Assembled File:** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md)  
**Source Drafts:** [`paper1_introduction_draft_p1_p3_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p1_p3_v1.md) and [`paper1_introduction_draft_p4_p6_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p4_p6_v1.md)  
**Prior Audits:** [`paper1_introduction_draft_p1_p3_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p1_p3_audit.md) and [`paper1_introduction_draft_p4_p6_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p4_p6_audit.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Master Bib:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 5.5 AUDIT COMPLETE (VERIFIED IMMUTABLE)**

---

## 1. Executive Summary

In Phase 5.5, the six independently developed and reviewed Introduction paragraphs have been assembled into the canonical section file [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md). This audit independently evaluates the assembled text for:
1. Bit-level verbatim identity against source drafts.
2. Word count compliance against the approved IEEE 450–470 word envelope.
3. Master bibliography consistency across all 12 in-text citation keys.
4. Structural conformity of the roadmap against the approved Paper 1 blueprint.
5. Strict exclusion of unverified claims (safety, travel-time, congestion) and Paper 2 scope leakage.

---

## 2. Paragraph-by-Paragraph Verbatim Identity and Replacement Audit

Automated string verification confirmed character-for-character identity between each source draft paragraph and the canonical assembled file, with Paragraph 3 incorporating only the single approved Phase 5.5 citation-scope replacement:

| Para | Approved Source File | Source Length (chars) | Target Length (chars) | Status | Diff / Discrepancies |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **P1** | `paper1_introduction_draft_p1_p3_v1.md` (L15) | 664 | 664 | **EXACT MATCH** | 0 discrepancies |
| **P2** | `paper1_introduction_draft_p1_p3_v1.md` (L17) | 709 | 709 | **EXACT MATCH** | 0 discrepancies |
| **P3** | `paper1_introduction_draft_p1_p3_v1.md` (L19) | 808 | 803 | **APPROVED REPLACEMENT** | Exactly one approved replacement: `"multi-attribute cost updates"` $\to$ `"flexible metric updates"`. 0 other differences. |
| **P4** | `paper1_introduction_draft_p4_p6_v1.md` (L15) | 523 | 523 | **EXACT MATCH** | 0 discrepancies |
| **P5** | `paper1_introduction_draft_p4_p6_v1.md` (L17) | 961 | 961 | **EXACT MATCH** | 0 discrepancies |
| **P6** | `paper1_introduction_draft_p4_p6_v1.md` (L19) | 359 | 359 | **EXACT MATCH** | 0 discrepancies |

**Verdict:** Absolute verbatim preservation achieved across all six paragraphs, with Paragraph 3 modified strictly by the approved citation-scope correction.

---

## 3. Word Count and Budget Analysis

Word counts were measured using two standard methods to guarantee reproducibility:
- **Method 1 (Standard Whitespace Split):** Direct string tokenization via whitespace separation.
- **Method 2 (Draft-Stated / Symbol-Normalized Count):** Treats embedded mathematical tuples such as `$(v, w)$` as atomic mathematical expressions.

| Paragraph | Primary Thematic Function | Method 1 (Split) | Method 2 (Stated) | Target Allocation | Budget Compliance |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Paragraph 1** | Two-Wheeler Urban Context & Heterogeneous Traffic | **73 words** | 73 words | ~70 words | $+3$ words |
| **Paragraph 2** | Vertex-State Limitations & Directed Edge States | **81 words** | 80 words | ~80 words | $+1$ word |
| **Paragraph 3** | Prior Turn-Cost Approaches & Speedup Hierarchy | **83 words** | 83 words | ~85 words | $-2$ words |
| *Subtotal P1–P3* | *Problem Context & State-Space Foundations* | *237 words* | *236 words* | *~235 words* | *+1 to +2 words* |
| **Paragraph 4** | Scoped Motivation & Integrated Formulation | **59 words** | 59 words | ~55–65 words | Nominal |
| **Paragraph 5** | Four Core Theoretical and Empirical Contributions | **124 words** | 124 words | ~115 words | $+9$ words |
| **Paragraph 6** | Paper Organisation Roadmap (Sections II–VII) | **48 words** | 48 words | ~45 words | $+3$ words |
| *Subtotal P4–P6* | *Motivation, Contributions & Roadmap* | *231 words* | *231 words* | *~215 words* | *+16 words* |
| **Total Section I** | **Complete Introduction Footprint** | **468 words** | **467 words** | **450–470 words** | **IN BUDGET (0.0% dev)** |

**Budget Verdict:** The total Section I footprint (467–468 words) fits strictly within the approved 450–470 word envelope defined in `paper1_final_page_budget_v1.md`.

---

## 4. Master Bibliography Traceability and Citation Verification

Every citation key appearing in `paper1_introduction_v1.md` was cross-referenced against [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib).

| Key | In-Text Occurrence | Publication Venue / Year | Cited Passage / Role in Manuscript | Bib Status |
| :--- | :---: | :--- | :--- | :---: |
| `promraksa2022lane` | Paragraph 1 | *Accid. Anal. Prev.*, 2022 | Thailand motorcycle vehicle registration share | **VERIFIED** |
| `kotagi2020modeling` | Paragraph 1 | *Transp. Res. Part A*, 2020 | Speed dispersion in mixed traffic on undivided roads | **VERIFIED** |
| `kumar2025realtime` | Paragraph 1 | *Eng. Sci. Tech.*, 2025 | Bengaluru arterial bottleneck congestion & variability | **VERIFIED** |
| `luxen2011realtime` | Paragraph 2 | *ACM SIGSPATIAL*, 2011 | Conventional vertex-state shortest-path baseline | **VERIFIED** |
| `das2019modeling` | Paragraph 2 | *Transp. Res. Part F*, 2019 | Heading transitions and intersection maneuvers | **VERIFIED** |
| `winter2002modeling` | Paragraphs 2, 3 | *Int. J. Geogr. Inf. Sci.*, 2002 | Directed edge states $s=(u,v)$; line graphs (pp. 446–450) | **VERIFIED** |
| `kirby1969minimum` | Paragraph 3 | *Transp. Res.*, 1969 | Movement-expanded state spaces in traffic assignment | **VERIFIED** |
| `geisberger2011efficient` | Paragraph 3 | *ACM Trans. Algorithms*, 2011 | Turn-expanded core nodes in Contraction Hierarchies | **VERIFIED** |
| `bast2016route` | Paragraphs 3, 4 | *Algorithm Engineering*, 2016 | Survey of route planning & metric customization; supports flexible metric updates (Sections 2.3 & 3.1), not simultaneous multi-attribute Pareto optimization | **VERIFIED** |
| `fadilah2024identifying` | Paragraph 3 | *ISPRS Int. J. Geo-Inf.*, 2024 | Motorcycle GPS tracking & lower-tier street usage | **VERIFIED** |
| `asvial2020entropy` | Paragraph 4 | *IJACSA*, 2020 | Post-hoc Entropy-TOPSIS re-ranking on Jakarta corridors | **VERIFIED** |
| `hart1968formal` | Paragraph 5 | *IEEE Trans. SSC*, 1968 | Classical $A^*$ heuristic admissibility and monotonicity | **VERIFIED** |

- Total unique citation keys in Section I: **12 keys**.
- Total keys present in `paper1_verified_references.bib`: **17 keys**.
- Missing, broken, or substituted citation keys: **0**.
- **Verdict:** 100% citation traceability confirmed.

### 4.1. Citation-Scope Audit for Bast et al. (2016)
- **Primary Source Examined:** [`10_Bast_2016_Route_Planning_Survey.pdf`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/papers/10_Bast_2016_Route_Planning_Survey.pdf) (65 pages).
- **Supported Scope:** Section 2.3 (pp. 8–9) and Section 3.1 (pp. 25–26) directly substantiate that customizable hierarchies (such as Customizable Route Planning, CRP, and Customizable Contraction Hierarchies, CCH) support fast metric customization and flexible metric updates (e.g., incorporating dynamic costs and turn penalties on fixed partitions/topologies).
- **Unsupported Scope:** Bast et al. treats multicriteria optimization separately in Section 2.7 (pp. 17–18) and Sections 4.1/5.3 for Pareto-optimal searches. Customizable hierarchies in Bast et al. do not perform simultaneous multi-attribute Pareto tracking during customization. Citing Bast et al. for *"multi-attribute cost updates"* was therefore narrowed to *"flexible metric updates"*, fully aligning manuscript prose with verified primary evidence without changing word counts.

---

## 5. Structural Roadmap Verification against Paper 1 Blueprint

Paragraph 6 outlines the structure of Paper 1 as follows:
> *"The remainder of this paper is organized as follows: Section II surveys related work. Section III defines the problem formulation and configured impedance. Section IV presents the turn-aware algorithm, theoretical proofs, and complexity bounds. Section V describes experimental methodology, Section VI evaluates empirical ablations, and Section VII concludes."*

This matches [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md) exactly:
- **Section II:** Related Work (340 words)
- **Section III:** Problem Formulation and Mathematical Model (470 words)
- **Section IV:** Proposed Turn-Aware Routing Algorithm (480 words)
- **Section V:** Experimental Setup and Methodology (280 words)
- **Section VI:** Experimental Results and Analysis (600 words)
- **Section VII:** Limitations, Discussion, and Conclusion (510 words)

**Verdict:** 100% structural alignment with manuscript architecture.

---

## 6. Research Protocol and Boundary Audit

Automated keyword scanning verified that zero prohibited claims or scope leaks appear in the assembled Introduction:

1. **Safety Claims:**
   - Mentions of "safety", "accident reduction", "crash mitigation", "fatalities", "risk elimination": **0 occurrences**.
2. **Mobility Benefit Claims:**
   - Mentions of "travel-time savings", "congestion reduction", "faster commutes": **0 occurrences**.
3. **Rider Behavior / Psychological Claims:**
   - Mentions of "validated rider preferences", "driver psychology", "optimal rider choices": **0 occurrences**. (Impedance is strictly characterized as a *"configured class-dependent road impedance model"*).
4. **Priority Claims:**
   - Mentions of "first", "only", "novel in the world", "unprecedented": **0 occurrences**.
5. **Paper 2 Scope Leakage:**
   - Mentions of "alternative route", "diversity", "perpendicular offset", "Yen's algorithm", "choice set": **0 occurrences**.

---

## 7. Numerical Verification of Experimental Data (Paragraph 5)

All numerical metrics in Paragraph 5 were audited against frozen Phase 13.4 experimental outputs:

| Metric Reported in Prose | Numerical Claim in P5 | Ground-Truth File / Row | Verified Experimental Value | Accuracy |
| :--- | :---: | :--- | :---: | :---: |
| Sharp Turns (A0 vs. A1) | $21.44$ vs. $32.52$ ($-34.1\%$) | `statistical_test_results.csv` (Row 2) | Mean: $32.52 \to 21.44$ ($-34.07\%$, $p_{\text{adj}} = 4.5\times 10^{-5}$) | **EXACT** |
| Arterial Exposure (B0 vs. B1) | $13.84\%$ vs. $65.05\%$ ($-51.21\text{ pp}$) | `statistical_test_results.csv` (Row 11) | Mean: $65.05\% \to 13.84\%$ ($-51.2148\text{ pp}$, $p_{\text{adj}} = 8.4\times 10^{-5}$) | **EXACT** |
| Route Distance (B0 vs. B1) | $7.65$ vs. $6.62\text{ km}$ ($+15.53\%$) | `statistical_test_results.csv` (Row 17) | Mean: $6.6196 \to 7.6475\text{ km}$ ($+15.53\%$, $p_{\text{adj}} = 6.8\times 10^{-5}$) | **EXACT** |
| Evaluation Corridors | $25$ corridors | `stage_2b_full_ablation_results.json` | $N = 25$ OD corridor pairs | **EXACT** |
| Directed Road Edges | $744,216$ edges | `bengaluru_graph.pkl` network audit | $|E| = 744,216$ directed edges ($|V| = 308,643$) | **EXACT** |

---

## 8. Final Audit Verdict

The assembled Section I text in [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) satisfies all requirements of the IEEE authoring standards, `blrmap-research-protocol`, and `evidence-integrity-audit`. The text is fully verified, mathematically consistent, traceable to primary sources, and ready to be frozen.
