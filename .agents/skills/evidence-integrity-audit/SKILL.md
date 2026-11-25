---
name: evidence-integrity-audit
description: >-
  Guard frozen experimental data, verify numerical consistency between raw outputs and manuscript text, and audit statistical reporting for the BLRMap project. Use this skill when auditing experimental claims, validating tables and figures, checking p-values and effect sizes, or reconciling manuscript text against frozen ablation datasets.
---

# BLRMap Evidence Integrity & Data Reconciliation Audit

This skill establishes automated procedures and verification rules to ensure that every factual, tabular, statistical, and graphical claim in BLRMap research papers reconciles with 100% fidelity against the officially frozen Phase 13.4 experimental dataset.

---

## 1. Frozen Experimental Artifact Protection

All experimental files in [`research/literature_survey/13_ablation_study/`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/) are **officially frozen as of Phase 13.4 (2026-11-05)** and must remain strictly read-only:

```
research/literature_survey/13_ablation_study/
├── stage_2b_full_ablation_results.json      [1,855 Timing Observations, 385 Cells]  <-- FROZEN READ-ONLY
├── statistical_analysis_results.json        [33 Paired Tests, 11 Families]           <-- FROZEN READ-ONLY
├── statistical_test_results.csv             [Summary Statistical Table]              <-- FROZEN READ-ONLY
├── runtime_comparisons.csv                  [Execution Latency Data]                 <-- FROZEN READ-ONLY
├── exp_a_corridor_metrics.csv               [Experiment A Metrics]                   <-- FROZEN READ-ONLY
├── exp_b_corridor_metrics.csv               [Experiment B Metrics]                   <-- FROZEN READ-ONLY
├── exp_c_corridor_metrics.csv               [Experiment C Metrics]                   <-- FROZEN READ-ONLY
├── exp_d_corridor_metrics.csv               [Experiment D Metrics]                   <-- FROZEN READ-ONLY
├── exp_e_corridor_metrics.csv               [Experiment E Metrics]                   <-- FROZEN READ-ONLY
├── phase_13_4_correction_and_freeze_report.md [Official Freeze Record]               <-- FROZEN READ-ONLY
└── figures/
    ├── fig1_exp_a_tradeoffs.png             [Admissibility Trade-offs]               <-- FROZEN READ-ONLY
    ├── fig2_exp_b_road_classes.png          [Road-Class Distribution]                <-- FROZEN READ-ONLY
    ├── fig3_exp_c_sensitivity.png           [Turn Penalty Sensitivity]               <-- FROZEN READ-ONLY
    └── fig4_exp_e_alternatives.png          [Alternative Routing Comparison]         <-- FROZEN READ-ONLY
```

### Protection Mandate:
- **No Harness Re-execution:** Do not run `run_full_stage2b_ablation.py` or any evaluation script without explicit user authorization.
- **No Data Mutation:** Never edit, regenerate, or overwrite any of the frozen JSON, CSV, or figure files.
- **Single Source of Truth:** All numerical assertions in manuscripts must trace directly to these files.

---

## 2. Claim Classification Framework

Every empirical assertion in a draft paper must be categorized under one of four integrity tiers:

| Integrity Tier | Operational Definition | Allowed Usage in Paper |
| :--- | :--- | :--- |
| **`VERIFIED`** | Direct, exact match with frozen data backed by statistically significant paired test ($p_{\text{adj}} < 0.05$ after Holm-Bonferroni correction on $N=25$). | Primary paper contribution, highlighted findings, abstract claims. |
| **`CONDITIONALLY USABLE`** | Empirically observed in frozen data, but restricted by bounded sample size (e.g., Family E benchmarks with $N=5$, where non-parametric power limits min $p = 0.0625$). | Permitted in comparative evaluation, provided the sample size ($N=5$) and power limitation are explicitly disclosed. |
| **`DESCRIPTIVE ONLY`** | Empirically observed physical phenomenon or invariant outcome without inferential statistical significance (e.g., zero route changes in roundabout ablation D2 vs D4; specific corridor geometry shifts in OD_04/OD_15). | Permitted in discussion and case-study descriptions; must NOT claim statistical significance or generalized optimality. |
| **`UNSUPPORTED`** | Unmeasured quantities (safety, accident reduction, travel-time savings, rider fatigue) or unverified theoretical code stubs (signal-based ETA discount). | **STRICTLY PROHIBITED**. Must be deleted or relocated to future work. |

---

## 3. Phase 13.4 Mandatory Correction Rules

During Phase 13.3 independent audit, six transcription and reporting discrepancies were identified and resolved in Phase 13.4. All drafted manuscripts must comply strictly with these six correction rules:

### Rule 1: E1 Corridor Success Rate is 88.0% (Item C-1)
- **Verified Value:** Perpendicular Offset (E1) achieves an **88.0% corridor success rate (22 / 25 corridors)** generating $\ge 1$ surviving alternative satisfying detour $\le 1.20$ and overlap $\le 0.70$.
- **Error Guard:** Never report $96.0\%$ or $24/25$ corridors. Exactly 3 corridors (`OD_04`, `OD_15`, `OD_23`) yielded zero surviving alternatives due to strict detour constraints on congested or barrier-constrained topologies.

### Rule 2: Corridor `OD_04` Outcome under E1 (Item C-2 & C-3)
- **Verified Value:** In corridor `OD_04` (Whitefield to Marathahalli, $8.81\text{ km}$), railway and lake pinch points caused all 12 candidate lateral waypoints to exceed the $1.20$ detour threshold ($+20\%$). E1 yielded **0 / 12 surviving alternatives** and **0.0000 diversity**. Filtered Yen discovered 3 alternatives ($\mathcal{D} = 0.2931$) after purging 75 cloned candidates.
- **Error Guard:** Never state that E1 discovered 2 surviving alternatives or achieved $0.4851$ diversity on `OD_04`.

### Rule 3: 5-Corridor Benchmark Mean Surviving Alternatives (Item C-4)
- **Verified Value:** Across the 5 approved benchmark corridors (`OD_01`–`OD_05`), E1 surviving counts are $0, 1, 0, 2, 3$. The true mean is **1.20 surviving alternatives (median 1.0)**.
- **Error Guard:** Never report a mean of $1.80$ or median of $2.0$.

### Rule 4: 5-Corridor Benchmark Median Runtime for E1 (Item C-6)
- **Verified Value:** Across the 5 benchmark corridors, E1 execution runtimes are $7.36\text{ s}$, $8.22\text{ s}$, $8.84\text{ s}$, $9.09\text{ s}$, and $13.98\text{ s}$. The true median runtime is **8,842.72 ms (8.84 s)**.
- **Error Guard:** Never report $8,215.05\text{ ms}$ ($8.22\text{ s}$) as the median (that was `OD_02`'s individual runtime).

### Rule 5: Flyover Channelization Ground-Truth Corridors (Item C-5)
- **Verified Value:** Flyover channelization occurs on **`OD_04`** (bridge traversal increased from $136.86\text{ m}$ to $742.48\text{ m}$, saving $645\text{ m}$ distance) and **`OD_15`** (bridge traversal jumped from $562.66\text{ m}$ to $5,901.14\text{ m}$ along Hebbal Elevated Expressway, saving $2.15\text{ km}$ distance).
- **Error Guard:** Never cite `OD_08` or `OD_16` as flyover channelization examples (both exhibited zero bridge traversal change in Experiment D).

### Rule 6: Figure 4 Sample Size Disclosure
- **Verified Value:** Publication Figure 4 must explicitly state sample sizes directly on its x-axis categories: `E1 (N=25)`, `E2 (N=5)`, `E3 (N=5)`.
- **Error Guard:** Never display comparative alternative routing bar charts without visible sample size indicators.

---

## 4. Statistical Protocol & Reporting Verification

The agent must audit all reported statistics against the established Phase 13.4 statistical protocol:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   PHASE 13.4 STATISTICAL AUDIT WORKFLOW                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Unit of Analysis: Corridor-level paired observations (N=25, or N=5)      │
│ 2. Primary Hypothesis Test: Pratt-adjusted Wilcoxon Signed-Rank Test        │
│    • Preserves zero-difference observations conservatively                  │
│ 3. Sensitivity Check: Standard Wilcoxon Zero-Drop Test ('wilcox')           │
│    • Must confirm that conclusions are invariant to zero handling           │
│ 4. Multiple Comparisons: Holm-Bonferroni Adjusted p-values (p_adj)         │
│    • Applied strictly within each experimental hypothesis family            │
│ 5. Effect Size: Cohen's d_z with 95% Confidence Intervals                   │
│    • Supplemented by Rank-Biserial correlation (r_rb)                       │
│ 6. Median Difference: Hodges-Lehmann Estimator with 95% CI                  │
│ 7. Parametric Test Rule: Paired t-tests are NOT mandated; any parametric    │
│    test requires an explicit normality justification (e.g. Shapiro-Wilk)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Statistical Truths in Frozen Dataset:
- **Experiment A (Turn Penalties, $N=25$):**
  - A1 ($25/8$) vs. A0 ($0/0$): Sharp turns reduced by $-11.08$ turns ($34.1\%$, $32.52 \to 21.44$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$). Distance overhead: $+1.42\%$ ($+107.0\text{ m}$, not significant, $p_{\text{adj}} = 0.528$).
- **Experiment B (Road Impedance, $N=25$):**
  - B0 (Production) vs. B1 (Neutral): Arterial exposure reduced by $-51.21$ percentage points ($13.84\%$ vs $65.05\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$). Residential share increased by $+30.73$ percentage points ($44.24\%$ vs $13.51\%$, $p_{\text{adj}} = 0.00015$). Detour overhead: $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}} = 8.4 \times 10^{-5}$).
- **Experiment C (Turn Sensitivity, $N=25$):**
  - Monotonic turn count progression: $C_0(32.52) \to C_1(24.64) \to C_2(21.44) \to C_3(19.80)$.
  - $C_2$ captures $87.1\%$ of $C_3$'s turn reduction while maintaining minimal average distance ($7.648\text{ km}$).
- **Experiment D (Bridge & Roundabouts, $N=25$):**
  - Bridge discount increases flyover traversal from $159.68\text{ m}$ to $397.44\text{ m}$ ($+148.9\%$, $p_{\text{adj}} = 0.0039$).
  - Roundabout modifier produces zero differences on $25/25$ corridors ($p_{\text{adj}} = 1.0$).
- **Experiment E (Alternative Routing, $N=5$ Subset):**
  - E1 runs $4.49\times$ faster on mean ($9.50\text{ s}$ vs $42.61\text{ s}$) and $12.4\times$ faster on `OD_01` ($13.98\text{ s}$ vs $173.58\text{ s}$) than Yen's KSP.
  - Descriptive reporting only; non-parametric power at $N=5$ cannot achieve $p < 0.05$ (minimum possible Wilcoxon two-sided $p = 0.0625$).

---

## 5. Automated Data Reconciliation Checklist

Before approving any section, table, or figure for manuscript inclusion, execute this verification checklist:

1. **Table Cell Cross-Check:** Does every cell in the manuscript table match the corresponding entry in `statistical_test_results.csv` or `stage_2b_full_ablation_results.json`?
2. **Unit Consistency:** Are distance units unambiguously labeled (meters vs. kilometers)? Are runtimes explicitly distinguished (milliseconds vs. seconds)?
3. **P-Value Labeling:** Are reported $p$-values explicitly identified as Holm-Bonferroni adjusted ($p_{\text{adj}}$) or raw?
4. **Sample Size Labeling:** Is the number of evaluated corridors ($N=25$ or $N=5$) explicitly specified in every table caption and figure label?
5. **Rounding Protocol:** Verify rounding adheres to IEEE guidelines (distances to 2 or 3 decimal places; percentages to 1 or 2 decimal places; p-values in scientific notation if $< 0.001$).
6. **No Phantom Claims:** Verify that no claim of fuel reduction, travel time savings, or safety enhancement appears anywhere in the text.
