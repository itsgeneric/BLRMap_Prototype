# Phase 8.3-B Freeze Log: Section V Canonical Freeze

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.3-B3 — Section V Finalisation and Freeze  
**Date:** 2026-11-06  
**Document:** [`phase_8_3_B_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_B_freeze_log.md)  
**Canonical Frozen File:** [`paper1_section_V_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_V_draft_v1.md) (Version 1.0 Frozen)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **SECTION V CANONICAL MANUSCRIPT FROZEN (APPROVED BY RESEARCH LEAD)**  

---

## 1. Formal Freeze Declaration

By explicit decision of the Research Lead, Section V of Paper 1 (*Experimental Setup and Methodology*) has completed precision drafting, distance-basis verification, and final editorial refinement. Section V is hereby declared **CANONICALLY FROZEN** (Version 1.0).

The canonical frozen file is located at:
- [`research/paper1_manuscript/paper1_section_V_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_V_draft_v1.md)

Under project research protocol and version-control governance, **no further modifications, rewrites, refactorings, or word substitutions may be made to this file without explicit written authorization from the Research Lead.**

---

## 2. Canonical Frozen Text

```markdown
## V. EXPERIMENTAL SETUP AND METHODOLOGY

### A. Urban Road Network and OD Corridor Corpus

The empirical evaluation is conducted on an OpenStreetMap road network of Bengaluru modelled as a directed graph with 308,643 vertices, 744,216 raw directed multigraph edge records, and 740,822 distinct ordered adjacent node pairs following parallel-edge collapse. Benchmarks are evaluated across 25 origin–destination corridors, with physical route distances ranging from 1.35 km to 15.82 km across the turn-unaware reference configurations (A1, A2, and C0); the individual corridor serves as the primary unit of analysis.

### B. Benchmark Configurations and Execution Protocol

Four experimental suites evaluate routing behavior across the corridor corpus. Experiment A compares turn-aware state-expanded routing against turn-unaware state expansion and a node-level reference. Experiment B benchmarks production road-class impedance against neutral hierarchy weights and physical shortest paths. Experiment C tests sensitivity across four discrete turn-penalty tiers. Experiment D assesses topological bridge and roundabout modifiers under a 2×2 factorial design. Each corridor–configuration combination is evaluated across five execution repetitions, with elapsed wall-clock runtime recorded using `time.perf_counter()`, producing 1,750 execution observations across 350 experimental cells.

### C. Statistical Analysis

For each configuration, per-corridor observations are aggregated using within-corridor medians across the five execution repetitions before paired corridor-level comparisons ($N=25$). Inferential hypothesis testing employs two-sided Wilcoxon signed-rank tests with Pratt correction for zero differences, controlling family-wise error rates via Holm–Bonferroni step-down adjustments within each comparison family. Effect sizes are reported using matched-pairs Cohen's $d_z$ with 95% confidence intervals and Hodges–Lehmann paired median difference estimates with 95% confidence intervals, where reported.
```

---

## 3. Cryptographic Fingerprint and Word Count Specification

- **Canonical File Path:** [`research/paper1_manuscript/paper1_section_V_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_V_draft_v1.md)
- **SHA-256 Digest:** `C3330EB0E42D0BCABE6D2AAB16461B9B12BED701886F5B815BA82D5815185DD6`
- **Word-Count Convention:** Strict whitespace-delimited word counting (`string.split()`) applied exclusively to prose body text, excluding markdown headings (`##`, `###`), metadata blocks, and equations.
- **Subsection Breakdown:**
  - **Subsection V-A:** 73 words
  - **Subsection V-B:** 84 words
  - **Subsection V-C:** 70 words
  - **Cumulative Section V Body Word Count:** **227 words**
- **Budget Compliance:** The target allocation was ~220 words. The final count of 227 words (+7 words, +3.1%) accommodates the mathematically precise attribution of distance bounds to the turn-unaware reference configurations ($A_1, A_2, C_0$), preserving total methodological rigor while fitting comfortably within the 6.0-page IEEE conference layout.

---

## 4. Evidence Sources Used

The factual claims, parameters, and methods in Section V are strictly grounded in authoritative project artifacts:
1. **Network Topology:** OpenStreetMap Bengaluru serialized graph `bengaluru_graph.pkl` and [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) ($|V|=308,643, |E|=744,216, |E_s|=740,822$).
2. **Corridor Corpus:** 25 origin–destination corridors across short, medium, and long categories ([`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv)).
3. **Distance Range Verification:** Minimum physical distance $1.353\text{ km}$ (OD_23) and maximum physical distance $15.818\text{ km}$ (OD_08) under turn-unaware routing configurations ($A_1, A_2, C_0$, $P_{\text{turn}}=0$), as documented in Table 2.1 of [`phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md).
4. **Execution Harness:** [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py) (five execution repetitions per cell, wall-clock timing via `time.perf_counter()`, 350 experimental cells yielding 1,750 observations across Experiments A–D).
5. **Statistical Analysis Protocol:** [`analyze_stage2b_results.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/analyze_stage2b_results.py) and [`statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv) (within-corridor median aggregation, paired Wilcoxon signed-rank test with Pratt zero handling, Holm–Bonferroni step-down correction, matched-pairs Cohen's $d_z$ with 95% CIs, and Hodges–Lehmann paired median difference estimates with 95% CIs).
6. **Parent Architectural Blueprint:** [`phase_8_3_A_experimental_evidence_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_A_experimental_evidence_blueprint.md) (v1.6 Audited).

---

## 5. Explicit Preservation of Sections I–IV and Baselines

All previously approved and frozen sections remain byte-for-byte identical and unmodified, verified by cryptographic hash matching:

| Section | Canonical File | Status | Expected SHA-256 | Actual SHA-256 | Verification |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Abstract** | [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | FROZEN | `67272764F7DA...334DB142` | `67272764F7DA...334DB142` | **MATCH** |
| **Section I** | [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | FROZEN | `3271BE72BA4A...1B64141` | `3271BE72BA4A...1B64141` | **MATCH** |
| **Section II** | [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | FROZEN | `839C1D5936F7...2CA21BA` | `839C1D5936F7...2CA21BA` | **MATCH** |
| **Section III** | [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) | FROZEN | `CEE2B6A495D0...3692C9061` | `CEE2B6A495D0...3692C9061` | **MATCH** |
| **Section IV-A** | [`paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md) | FROZEN | `8B86B3722895...6C3D7CEE` | `8B86B3722895...6C3D7CEE` | **MATCH** |
| **Section IV-B** | [`paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md) | FROZEN | `CB88AC8A9263...7EDEFEB6` | `CB88AC8A9263...7EDEFEB6` | **MATCH** |
| **Section IV-C** | [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md) | FROZEN | `08262BE23D74...8FCC4C1` | `08262BE23D74...8FCC4C1` | **MATCH** |
| **Section IV-D** | [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md) | FROZEN | `B1A07D5CD095...E83EC772` | `B1A07D5CD095...E83EC772` | **MATCH** |

---

## 6. Stop Condition Compliance

Section V is hereby locked. Section VI has NOT been drafted, and the full manuscript has NOT been assembled. Standing by for Research Lead authorization of **Phase 8.3-C: Section VI (Experimental Results and Discussion) Architecture & Drafting**.
