# Phase 3.1 Correction and Audit Log

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.1 — Independent Literature, Novelty, and Numerical Audit  
**Date:** 2026-11-05  
**Governing Skills:** `blrmap-research-protocol`, `evidence-integrity-audit`  
**Document:** `research/paper1_literature/phase_3_1_correction_log.md`  
**Status:** Completed and Verified against Frozen Raw Evidence  

---

## 1. Executive Summary

In accordance with Phase 3.1 specifications, an independent, zero-assumption audit of the Phase 3 literature deliverables, numerical claims, citation records, and novelty assertions was conducted. 

The audit identified and resolved:
1. **One Critical Numerical Transposition:** In the Phase 3 summary narrative, statistical test values from Experiment B (arterial exposure) were inadvertently transposed onto Experiment A (sharp turns). Both values have been reconciled against the frozen raw CSV datasets.
2. **One Disqualified Citation:** The entry `borndorfer2018turndependent` was determined to be an unverified citation with an invalid DOI (`10.1007/978-3-642-12463-1_6` returning HTTP 404). It has been formally disqualified and replaced with the verified landmark foundations of Kirby & Potts (1969) and Winter (2002).
3. **One Corrected DOI:** The citation `zografos2004heuristic` originally cited an incorrect TRR article DOI (`10.3141/1882-04`, belonging to Tang & Miller-Hooks). It has been corrected to the authentic Crossref DOI: `10.1016/s0377-2217(03)00041-9` (*European Journal of Operational Research*, 2004).
4. **Heuristic Consistency vs. Admissibility Distinction:** Clarified the mathematical boundary between admissibility ($h(s) \le c^*(s)$) and consistency ($h(s) \le c(s, s') + h(s')$), formalizing node-reopening guarantees on state-expanded graphs.

---

## 2. Itemized Numerical Discrepancy Correction Table

The numerical values reported in the Phase 3 summary were cross-checked directly against [`statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv) and [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json):

| Item ID | Comparison Family | Metric | Erroneous Value in Phase 3 Text | Correct Value from Frozen Raw Evidence | Frozen Source Reference | Nature of Discrepancy & Resolution |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **CORR-1** | **Family A (Turn Penalties, A0 vs A1)** | Sharp Turn Reduction | $-11.08$ turns ($p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$) | **$-11.08$ turns ($34.1\%$, $32.52 \to 21.44$)**<br/>**$p_{\text{adj}} = 4.5 \times 10^{-5}$**<br/>**Cohen's $d_z = -1.0066$** (95% CI: $[-1.4194, -0.5938]$)<br/>Wilcoxon $W = 0.0, r_{\text{rb}} = -1.0$<br/>Hodges-Lehmann = $-9.5$ turns | `statistical_test_results.csv` Row 2 (`Family_A_Turns`, `A0 vs A1`) | **Transposition Error Corrected:** Phase 3 summary text inadvertently copied $p_{\text{adj}}$ ($8.4 \times 10^{-5}$) and $d_z$ ($-1.7715$) from Family B onto Family A. The true $d_z$ is $-1.0066$ and $p_{\text{adj}}$ is $4.5 \times 10^{-5}$. Corrected in `paper1_research_gap.md` and `evidence-integrity-audit/SKILL.md`. |
| **CORR-2** | **Family B (Road Impedance, B0 vs B1)** | Arterial Exposure Reduction | $-51.21$ percentage points ($p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$) | **$-51.21$ percentage points ($65.05\% \to 13.84\%$)**<br/>**$p_{\text{adj}} = 8.4 \times 10^{-5}$**<br/>**Cohen's $d_z = -1.7715$** (95% CI: $[-2.1843, -1.3588]$)<br/>Wilcoxon $W = 4.0, r_{\text{rb}} = -0.9921$<br/>Hodges-Lehmann = $-54.55$ pp | `statistical_test_results.csv` Row 11 (`Family_B_Arterial`, `B0 vs B1`) | **Verified Accurate:** Values match frozen CSV table with 100% agreement. |
| **CORR-3** | **Family B (Road Impedance, B0 vs B1)** | Residential Share Increase | $+30.73$ percentage points ($p_{\text{adj}} = 0.00015$) | **$+30.73$ percentage points ($13.51\% \to 44.24\%$)**<br/>**$p_{\text{adj}} = 0.00015$**<br/>**Cohen's $d_z = +1.5234$**<br/>Hodges-Lehmann = $+30.82$ pp | `statistical_test_results.csv` Row 14 (`Family_B_Residential`, `B0 vs B1`) | **Verified Accurate:** Values match frozen CSV table with 100% agreement. |
| **CORR-4** | **Family C (Turn Sensitivity Knee, C2 vs C0)** | Sharp Turn Reduction & Trade-off Knee | Baseline C2 captures 87.1% of C3 turn reduction | **Monotonic Turn Counts:**<br/>$C_0(32.52) \to C_1(24.64) \to C_2(21.44) \to C_3(19.80)$<br/>$C_0 \to C_2$ reduction: $11.08$ turns ($p_{\text{adj}} = 4.5 \times 10^{-5}$)<br/>Max reduction ($C_0 \to C_3$): $12.72$ turns<br/>Ratio: $11.08 / 12.72 = \mathbf{87.1\%}$<br/>Average distance: $C_2 = 7.648\text{ km}$ | `statistical_test_results.csv` Rows 20–22; `stage_2b_full_ablation_results.json` | **Verified Accurate:** Confirms Baseline $C_2(25/8)$ as the empirical corpus-average trade-off knee. |

---

## 3. Bibliographic Integrity Audit and Disqualification Record

All 17 citations compiled in Phase 3 were audited against the public Crossref REST API:

### Disqualified Entry: `borndorfer2018turndependent`
- **Claimed Citation:** Ralf Borndörfer, Christian Liebchen, Hanno Schülldorf, Thomas Swarat, *"Turn-Dependent Shortest Path Problems"*, in *Algorithmic Approaches to Transit Transport*, Springer, 2018.
- **Audit Finding:** The queried DOI `10.1007/978-3-642-12463-1_6` returned `HTTP 404 Not Found` on Crossref. Direct keyword query across Crossref, Google Scholar, and DBLP confirmed that no book or chapter with this title, author combination, and DOI exists.
- **Action Taken:** Formally **DISQUALIFIED**. Removed from active bibliography. Foundational state-expansion authority is attributed to the authentic peer-reviewed literature: Kirby & Potts (1969) [DOI: `10.1016/s0041-1647(69)80022-5`] and Winter (2002) [DOI: `10.1023/A:1020853410145`].

### Corrected Entry: `zografos2004heuristic`
- **Original Citation:** Konstantinos G. Zografos and Konstantinos N. Androutsopoulos, *"A Heuristic Algorithm for Solving Hazardous Materials Routing Problems with Turn Penalties"*, TRR, DOI: `10.3141/1882-04`.
- **Audit Finding:** Crossref metadata for DOI `10.3141/1882-04` revealed that this DOI actually belongs to an entirely different article: Tang & Miller-Hooks, *"Approximate Procedures for Probabilistic Traveling Salesperson Problem"*. Zografos & Androutsopoulos's true peer-reviewed journal paper on hazardous routing with turn penalties was published in *European Journal of Operational Research* (2004).
- **Action Taken:** Corrected in BibTeX to:
  - *Title:* "A heuristic algorithm for solving hazardous materials distribution problems"
  - *Journal:* *European Journal of Operational Research*, Vol. 152, No. 2, pp. 507–519, 2004.
  - *Authentic DOI:* `10.1016/s0377-2217(03)00041-9` (Crossref Verified).

### Resolved Identifier: `goldberg2005computing`
- **Original Citation:** Andrew V. Goldberg and Chris Harrelson, *"Computing the Shortest Path: A\* Search Meets Graph Theory"*, SODA 2005, DOI: `10.5555/1070432.1070455`.
- **Audit Finding:** The prefix `10.5555` is an internal ACM Digital Library handle, not a registered Crossref DOI (hence Crossref returns 404). However, the publication is an authentic, highly cited landmark paper presented at the 16th ACM-SIAM Symposium on Discrete Algorithms (SODA '05), pages 156–165.
- **Action Taken:** Verified authentic. Added explicit note in BibTeX and CSV documenting the ACM DL identifier.

---

## 4. Summary of Affected Documents Updated

1. [`research/paper1_literature/paper1_research_gap.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_research_gap.md): Corrected Line 53 to reflect true Experiment A values: $-11.08$ sharp turns ($34.1\%$), $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$.
2. [`.agents/skills/evidence-integrity-audit/SKILL.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md): Corrected Line 111 to reflect true Experiment A values: $-11.08$ sharp turns ($34.1\%$), $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$.
3. [`research/paper1_literature/paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib): Disqualified Borndörfer et al.; corrected Zografos & Androutsopoulos DOI and title; verified all 16 active entries against Crossref.
4. [`research/paper1_literature/paper1_literature_matrix.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_literature_matrix.csv): Updated entries with Crossref-verified bibliographic metadata.
