# Phase 13.4 — Independent Audit Corrections and Results Freeze Report

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 13.4 — Independent Audit Corrections and Results Freeze  
**Author:** Antigravity Autonomous Agent  
**Date:** 2026-11-05  
**Document:** [`phase_13_4_correction_and_freeze_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_4_correction_and_freeze_report.md)  
**Parent Phases:** Phase 13.1 Stage 2B Full Ablation Execution, Phase 13.3 Independent Audit (`ACCEPTED WITH CONDITIONS`)  
**Status:** **COMPLETED & EXPERIMENTAL RESULTS OFFICIALLY FROZEN**

---

## Executive Summary

Phase 13.3 independent audit verified the raw data integrity (1,855 timing observations across 385 cells and 25 corridors), statistical analysis (33 paired hypothesis tests across 11 families), and physical invariant metrics with zero computational errors, returning an overall verdict of **`ACCEPTED WITH CONDITIONS`**. 

Phase 13.4 fulfills all six mandatory conditions stipulated in the audit by:
1. Correcting all identified textual, tabular, and narrative transcription discrepancies in the consolidated report ([`phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md)).
2. Formalizing multi-objective Pareto terminology to designate Baseline C2 ($25/8$) as the **empirical corpus-average trade-off knee**, explicitly disclosing the non-dominated Pareto frontier ($\{C_2, C_3\}$) and individual corridor trade-off variations.
3. Updating publication Figure 4 ([`fig4_exp_e_alternatives.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig4_exp_e_alternatives.png)) to visibly disclose unequal sample sizes ($N=25$ for E1 vs. $N=5$ for E2/E3) directly on the category axis labels.
4. Confirming that raw experimental JSON datasets, CSV tables, and production codebase files remain **100% untouched and unchanged**.
5. Formally declaring the Phase 13 ablation results **FROZEN** for IEEE paper drafting.

---

## 1. Itemized Correction Table

All six identified discrepancies have been corrected in [`phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md). The table below documents the exact changes made:

| Item # | Affected Section | Original Text / Value | Corrected Text / Value | Source of Verification | Audit Justification |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **C-1** | Executive Summary (Item 5) & Section 6.1 | *"Perpendicular Offset (E1) achieves a 96.0% corridor success rate across all 25 corridors..."*<br/>*"Corridor Success Rate: 24 / 25 corridors (96.0%) generated $\ge 1$ surviving alternative..."* | *"Perpendicular Offset (E1) achieves an **88.0% corridor success rate (22 / 25 corridors)** across the metropolitan corpus..."*<br/>*"Corridor Success Rate: **22 / 25 corridors (88.0%)** generated $\ge 1$ surviving alternative satisfying $\text{max\_detour} \le 1.20$ and $\text{max\_overlap} \le 0.70$ (three corridors—`OD_04`, `OD_15`, and `OD_23`—yielded zero surviving alternatives due to strict detour thresholding on congested or barrier-constrained topologies)."* | `exp_e_corridor_metrics.csv`<br/>`stage_2b_full_ablation_results.json` | Corrects factual reporting error. Exactly 3 corridors produced 0 surviving alternatives; $25 - 3 = 22$ ($88.0\%$). |
| **C-2** | Section 6.3 (Table 6.3 Row `OD_04`) | `| **OD_04** | 8.81 km | 2 / 12 | 0.4851 | SUCCESS_FULL | 3 | 0.0399 | SUCCESS_FULL | 3 | 0.2931 | 75 | Successfully generated 3 alternatives |` | `| **OD_04** | 8.81 km | 0 / 12 | 0.0000 | SUCCESS_FULL | 3 | 0.0399 | SUCCESS_FULL | 3 | 0.2931 | 75 | E1 failed detour threshold; E3 purged 75 candidates |` | `stage_2b_full_ablation_results.json`<br/>`OD_04.experiments.Experiment_E.E1_Perpendicular_Offset` | Eliminates manual transcription error in Table 6.3. Under E1, OD_04 generated 0 surviving alternatives and 0.0000 diversity. |
| **C-3** | Section 6.4 (Paragraph 2 / Item 3) | *"In corridor OD_03 ... and OD_04 (Whitefield railway pinch point)... Perpendicular Offset achieved 0.5669 and 0.4851 diversity by routing along parallel arterial corridors."* | Replaced with separated diagnostic items for OD_03 and OD_04. Discloses that for OD_04, severe topological rail/lake pinch points caused all lateral offset candidates to exceed the $1.20$ detour tolerance ($+20\%$), yielding **`0` surviving alternatives** (`0 / 12`, diversity **`0.0000`**), while Filtered Yen purged 75 cloned candidates to discover 3 alternatives ($\mathcal{D} = 0.2931$). | `exp_e_corridor_metrics.csv`<br/>`stage_2b_full_ablation_results.json` | Aligns narrative discussion with verified empirical outcome taxonomy. |
| **C-4** | Section 6.2 (Table 6.2 Row `Mean Surviving Alts`) | `Mean Surviving Alts: E1 = 1.80 (Med: 2.0)` | `Mean Surviving Alts: E1 = 1.20 (Med: 1.0)` | `exp_e_corridor_metrics.csv` (N=5 subset: 0, 1, 0, 2, 3) | With OD_04 correctly evaluated as 0 surviving alternatives, the true 5-corridor mean is $(0 + 1 + 0 + 2 + 3)/5 = 1.20$, median = $1.0$. |
| **C-5** | Section 5.4 (Paragraph 1) | *"In corridors with major arterial flyovers (e.g. OD_08 Banashankari to Yeshwanthpur and OD_16 Bellandur to Whitefield), the flyover discount directly channels the route onto grade-separated elevated corridors."* | *"In corridors with major grade-separated arterial flyovers—specifically **OD_04 (Whitefield to Marathahalli)**, where bridge traversal jumped from $136.86\text{ m}$ to $742.48\text{ m}$ ($-645\text{ m}$ route distance), and **OD_15 (Yelahanka to Hebbal)**, where bridge traversal jumped from $562.66\text{ m}$ to $5,901.14\text{ m}$ along the Hebbal Elevated Expressway ($-2.15\text{ km}$ route distance)—the flyover discount directly channels routes onto grade-separated elevated infrastructure."* | `exp_d_corridor_metrics.csv`<br/>`stage_2b_full_ablation_results.json` | Replaces incorrect qualitative citations (`OD_08` and `OD_16` had 0 route change) with the actual corridors exhibiting flyover channelization (`OD_04` and `OD_15`). |
| **C-6** | Section 6.2 (Table 6.2 Row `Median Runtime [ms]`) | `Median Runtime [ms]: E1 = 8,215.05 (8.22 s)` | `Median Runtime [ms]: E1 = 8,842.72 (8.84 s)` | `exp_e_corridor_metrics.csv` (N=5 runtimes: 7.36s, 8.22s, 8.84s, 9.09s, 13.98s) | Corrects median runtime of the 5-corridor subset (8,215.05 was OD_02's individual runtime; the median of the 5 values is 8,842.72 ms). |

---

## 2. Multi-Objective Pareto Terminology Formalization

In accordance with Phase 13.4 specifications, the interpretation of Experiment C (Turn-Penalty Sensitivity Response) has been thoroughly reviewed and formalized to eliminate any ambiguity regarding Pareto optimality.

### 2.1 Theoretical and Empirical Framework
In multi-objective optimization, we seek to simultaneously minimize:
1. $f_1(\mathbf{x}) = \text{Physical Route Distance [km]}$
2. $f_2(\mathbf{x}) = \text{Sharp Turn Maneuvers [count]} \quad (\ge 60^\circ)$

The verified corpus-level means across all 25 metropolitan corridors are:
- $\mathbf{C_0}$ ($0 / 0$): $f_1 = 7.723\text{ km}$, $f_2 = 32.52\text{ turns}$
- $\mathbf{C_1}$ ($12 / 4$): $f_1 = 7.668\text{ km}$, $f_2 = 24.64\text{ turns}$
- $\mathbf{C_2}$ ($25 / 8$): $f_1 = 7.648\text{ km}$, $f_2 = 21.44\text{ turns}$
- $\mathbf{C_3}$ ($50 / 16$): $f_1 = 7.680\text{ km}$, $f_2 = 19.80\text{ turns}$

### 2.2 Formal Pareto Dominance Assessment
1. **Dominance Relations:**
   - $C_2 \succ C_0$: $C_2$ strictly dominates $C_0$ ($7.648 < 7.723\text{ km}$ and $21.44 < 32.52$ turns).
   - $C_2 \succ C_1$: $C_2$ strictly dominates $C_1$ ($7.648 < 7.668\text{ km}$ and $21.44 < 24.64$ turns).
   - $C_1 \succ C_0$: $C_1$ strictly dominates $C_0$ ($7.668 < 7.723\text{ km}$ and $24.64 < 32.52$ turns).
   - $C_2 \text{ vs. } C_3$: $C_2$ yields lower physical distance ($7.648 < 7.680\text{ km}$), whereas $C_3$ yields fewer sharp turns ($19.80 < 21.44$ turns). Neither dominates the other.
2. **Empirical Pareto Frontier:**
   $$\mathcal{P}_{\text{empirical}} = \{C_2, C_3\}$$
   Both $C_2$ and $C_3$ are mathematically non-dominated solutions on the empirical frontier.
3. **Identification of the "Trade-off Knee":**
   - Escalating penalties from $C_0 \to C_2$ operates in a **strictly synergistic regime**: sharp maneuvers drop by $-11.08$ turns ($-34.1\%$) while route distance *decreases* by $-75\text{ meters}$ (eliminating erratic alleyway shortcuts).
   - Escalating penalties further from $C_2 \to C_3$ enters an **adversarial trade-off regime**: eliminating an additional $-1.64$ sharp turns ($-7.6\%$) requires $+32.3\text{ meters}$ of detour ($+19.7\text{ m}$ per turn avoided).
   - Baseline $C_2$ captures $\frac{11.08}{12.72} = \mathbf{87.1\%}$ of the maximum possible maneuver reduction while anchoring the absolute global minimum physical route distance ($7.648\text{ km}$).
   - **Term Adopted:** Baseline $C_2$ ($25/8$) is designated strictly as the **"empirical corpus-average trade-off knee"**.
4. **Individual Corridor Variation Disclosed:**
   The consolidated report now explicitly discloses that universal dominance does not hold across all corridors:
   - $C_2$ strictly dominates $C_3$ on **8 / 25 corridors**.
   - $C_3$ strictly dominates $C_2$ on **7 / 25 corridors**.
   - $C_2$ and $C_3$ represent active distance-turn trade-offs on **5 / 25 corridors**.
   - $C_2$ and $C_3$ yield identical routes on **5 / 25 corridors**.

---

## 3. Publication Figure 4 Regeneration

### 3.1 Modification Details
In the original Phase 13.1 generation, Figure 4 displayed boxplots where Perpendicular Offset ($E1$) represented all $N=25$ corpus corridors, while Raw Yen ($E2$) and Filtered Yen ($E3$) represented only the approved $N=5$ benchmark corridors. The axis labels lacked explicit sample-size disclosures.

In accordance with Phase 13.4 requirements:
- The category labels in [`analyze_stage2b_results.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/analyze_stage2b_results.py) and the standalone generator script ([`regen_fig4.py`](file:///C:/Users/comps/.gemini/antigravity-cli/brain/b9cbc466-7622-4c61-8e3e-1f1a55185246/scratch/regen_fig4.py)) were updated to:
  ```python
  e_labels = [
      "E1: Offset (N=25)\n(Heuristic)",
      "E2: Raw Yen (N=5)\n(Exact Spur)",
      "E3: Filtered Yen (N=5)\n(70% Pruned)",
  ]
  ```
- Publication-quality Figure 4 ([`fig4_exp_e_alternatives.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig4_exp_e_alternatives.png)) was regenerated at 300 DPI.
- The underlying numerical data, boxplot medians, quartiles, whiskers, and fliers remain completely unchanged.
- Section 9.2 in the report was updated to state:  
  *"Boxplots comparing Execution Runtime (log-scale) and Pairwise Diversity between Perpendicular Offset ($N=25$), Raw Yen ($N=5$), and Filtered Yen ($N=5$). Sample sizes are explicitly disclosed on category axis labels."*

---

## 4. Post-Correction Verification & Integrity Audit

A comprehensive automated verification was performed to confirm that all corrections were accurately applied and that zero regressions or residual outdated values remain.

### 4.1 Residual String and Value Scan
An exhaustive scan of `phase_13_1_stage_2B_full_ablation_report.md` confirms:
- **`96.0%` / `96%`:** Exactly **0** occurrences.
- **`24 / 25` / `24/25`:** Exactly **0** occurrences.
- **`0.4851` (unsupported OD_04 diversity):** Exactly **0** occurrences.
- **`OD_08` / `OD_16` (in Section 5.4 bridge text):** Exactly **0** occurrences.
- **`Pareto-optimal knee` (without context):** Replaced with **`empirical corpus-average trade-off knee`**; mathematical frontier explicitly defined.
- **`88.0% (22 / 25 corridors)`:** Present and verified in Executive Summary and Section 6.1.
- **`OD_04 (0 / 12, 0.0000)`:** Present and verified in Table 6.3 and Section 6.4.
- **`Mean Surviving Alts = 1.20 (Med: 1.0)`:** Present and verified in Table 6.2.

### 4.2 Raw Experimental Dataset Preservation
An automated timestamp and checksum inspection confirms that the primary experimental outputs remain **100% unaltered**:

```
PRIMARY DATASET INTEGRITY CHECK
├─ stage_2b_full_ablation_results.json ── [UNTOUCHED] 924,405 bytes, LastWrite: 05-11-2026 13:45:05
├─ statistical_analysis_results.json ──── [UNTOUCHED]  52,505 bytes, LastWrite: 05-11-2026 13:46:00
├─ exp_a_corridor_metrics.csv ─────────── [UNTOUCHED]   8,156 bytes, LastWrite: 05-11-2026 13:45:59
├─ exp_b_corridor_metrics.csv ─────────── [UNTOUCHED]   8,549 bytes, LastWrite: 05-11-2026 13:45:59
├─ exp_c_corridor_metrics.csv ─────────── [UNTOUCHED]  10,346 bytes, LastWrite: 05-11-2026 13:45:59
├─ exp_d_corridor_metrics.csv ─────────── [UNTOUCHED]  11,856 bytes, LastWrite: 05-11-2026 13:45:59
├─ exp_e_corridor_metrics.csv ─────────── [UNTOUCHED]   5,923 bytes, LastWrite: 05-11-2026 13:45:59
├─ runtime_comparisons.csv ────────────── [UNTOUCHED]  32,260 bytes, LastWrite: 05-11-2026 13:45:59
└─ statistical_test_results.csv ───────── [UNTOUCHED]   5,901 bytes, LastWrite: 05-11-2026 13:45:59
```

### 4.3 Production Routing Codebase Status
- `core/config.py`: **Unmodified** (Last modified 2026-11-04 13:41:58).
- `routing/algorithms.py`: **Unmodified** (`TURN_PENALTY_SHARP = 25.0`, `TURN_PENALTY_MODERATE = 8.0`).
- `routing/graph_manager.py`: **Unmodified**.
- `api_server.py`: **Unmodified**.
- Historical benchmarks (`10_alternative_routing/`, `11_route_quality_evaluation/`, `12_robustness_testing/`): **Unmodified**.

---

## 5. Official Results Freeze Declaration

With the successful execution of Phase 13.4:

1. **Experimental Dataset Freeze:** All 1,855 timing observations, 385 evaluated cells, and metric distributions recorded in `stage_2b_full_ablation_results.json` and associated CSV tables are hereby declared **OFFICIALLY FROZEN**.
2. **Statistical Test Freeze:** All 33 paired hypothesis test statistics, Pratt-adjusted Wilcoxon p-values, Hodges-Lehmann median difference estimators, and step-down Holm-Bonferroni family decisions recorded in `statistical_test_results.csv` are **OFFICIALLY FROZEN**.
3. **Consolidated Report Freeze:** [`phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md) is fully reconciled, verified against raw ground truth, and **OFFICIALLY FROZEN**.
4. **Figure Freeze:** Publication Figures 1, 2, 3, and 4 in `figures/` are finalized, fully documented, and **OFFICIALLY FROZEN**.

---

## 6. Conclusion & Halt Declaration

In strict compliance with user instructions:
- **No further ablation experiments, parameter tuning, or code modifications will be executed.**
- **The Phase 13 Ablation Study is complete, fully audited, reconciled, and frozen.**
- **The system has halted awaiting your final paper-integration instructions.**
