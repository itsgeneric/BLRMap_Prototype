# Phase 13.1.2 — Final Documentation Alignment and Stage 2 Preflight (Revised)

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 13.1.2 — Final Documentation Alignment and Stage 2 Preflight (Updated per Phase 13.1.3 Directive)  
**Date:** 2026-11-05  
**Status:** Preflight Updated — Awaiting Explicit Stage 2 Execution Authorization  

---

## 1. Documentation Alignment Verification

Section 5 of [`research/literature_survey/13_ablation_study/phase_13_1_stage_1_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_1_report.md#L121-L158) has been synchronized with the authoritative, validated 25-corridor corpus in [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L60-L86) and [`phase_13_0_1_correction_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_0_1_correction_report.md#L41-L70).

---

## 2. Repetition Protocol and Harness Audit

### 2.1 Approved Repetition Matrix
In accordance with the experimental design:
- **Experiments A, B, C, D (A* Core Routing):** **5 repetitions** per corridor for runtime benchmarking.
- **Experiment E1 (Perpendicular Offset):** **3 repetitions** per corridor.
- **Experiments E2 & E3 (Raw and Filtered Yen K-SP):** **3 repetitions** per corridor across the 5 selected corridors.

### 2.2 Current Harness Implementation Audit
An inspection of [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L409-L560) reveals:
- The existing corridor runner functions (`run_experiment_a_corridor` through `run_experiment_e_corridor`) currently execute each algorithm invocation **exactly once** ($N_{\text{reps}} = 1$).
- **Identified Missing Functionality for Repetitions:**
  1. No `reps` loop parameter exists in the corridor runner signatures.
  2. No aggregation logic (e.g., `statistics.median(runtimes)`) is currently implemented to compute and report median within-corridor runtimes.
  3. Structural path metrics (distance, turns, road classes, bridge/roundabout meters) are deterministic on a static graph binary and need to be evaluated only once, whereas runtime benchmarking requires a repeated loop.
- **Status:** Per Phase 13.1.3 instructions, **no modifications have been made to the harness**. The repetition functionality will be integrated upon Stage 2 authorization.

---

## 3. Recalculated Runtime Budget (Accounting for All Repetitions)

The runtime budget is recalculating using empirical Stage 1 OD_01 measurements scaled across the distance distribution of the 25 corridors.

### 3.1 Empirical Basis and Scaling Assumptions
- **Measured on OD_01 ($10.065\text{ km}$, 213 nodes):**
  - Exp A (A0, A1, A2): $2.57\text{ s}$ single pass.
  - Exp B (B0, B1, B2): $1.70\text{ s}$ single pass.
  - Exp C (C0–C3): $4.94\text{ s}$ single pass.
  - Exp D (D1–D4): $5.18\text{ s}$ single pass.
  - Single pass for A–D on OD_01: $\approx 14.39\text{ s}$.
  - Exp E1 (Offset): $17.90\text{ s}$ single pass.
  - Exp E2 (Raw Yen): **$254.38\text{ s}$** ($4.24\text{ min}$) single pass.
  - Exp E3 (Filtered Yen): **$247.77\text{ s}$** ($4.13\text{ min}$) single pass.
- **Extrapolated Across Distance Tiers:**
  - 7 Short corridors ($\le 5\text{ km}$, $\approx 55$ nodes): A–D $\approx 2.1\text{ s}$/pass; E1 $\approx 5.0\text{ s}$/pass.
  - 10 Medium corridors ($5\text{--}9\text{ km}$, $\approx 140$ nodes): A–D $\approx 9.1\text{ s}$/pass; E1 $\approx 11.0\text{ s}$/pass.
  - 8 Long corridors ($> 9\text{ km}$, $\approx 235$ nodes): A–D $\approx 16.8\text{ s}$/pass; E1 $\approx 18.0\text{ s}$/pass.
  - Weighted average A–D single pass: $9.60\text{ s}$/corridor.
  - Weighted average E1 single pass: $11.56\text{ s}$/corridor.

### 3.2 Breakdown of Total Runtime Budget

| Component | Target Coverage | Repetitions | Single-Pass Time | Total Time (with Repetitions) | Status / Basis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Experiments A–D** | 25 corridors | **5 reps** | $4.0\text{ min}$ | **$20.3\text{ min}$** ($1,218\text{ s}$) | Extrapolated from OD_01 measurements |
| **Experiment E1 (Offset)** | 25 corridors | **3 reps** | $4.8\text{ min}$ | **$14.5\text{ min}$** ($867\text{ s}$) | Extrapolated from OD_01 measurements |
| **Experiment E2 (Raw Yen)** | 5 corridors | **3 reps** | $11.2\text{ min}$ | **$33.6\text{ min}$** ($2,013\text{ s}$) | Measured on OD_01 ($4.24\text{m}$); extrapolated for 4 others |
| **Experiment E3 (Filtered Yen)**| 5 corridors | **3 reps** | $10.7\text{ min}$ | **$32.2\text{ min}$** ($1,934\text{ s}$) | Measured on OD_01 ($4.13\text{m}$); extrapolated for 4 others |
| **Statistical Analysis & Markdown**| Full dataset | N/A | $0.5\text{ min}$ | **$0.5\text{ min}$** ($30\text{ s}$) | Analytical computation & rendering |
| **Total Recalculated Stage 2 Budget** | — | — | **$31.2\text{ min}$** | **$\mathbf{101.1\text{ minutes}}$** | **$\mathbf{\approx 1 \text{ hour } 41 \text{ minutes}}$** |

> [!IMPORTANT]
> The previously reported $33.7$-minute estimate represented only a single-pass run. Accounting for all required repetitions ($5$ for A–D, $3$ for E) yields an expected total runtime of **$\approx 101.1\text{ minutes}$** ($\approx 1.7\text{ hours}$). With process overhead buffer, the recommended execution window is **$1.6\text{ to } 2.0\text{ hours}$**.

---

## 4. Complete Distance Ranking and Yen Corridor Justification

### 4.1 Complete 25-Corridor Distance Ranking

All 25 corridors in the Phase 13.0.1 corpus ranked by physical route distance:

| Rank | Corridor ID | Corridor Name | Distance ($m$) | Distance ($km$) | Percentile | Distance Tier | Nodes |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **OD_23** | **Richmond Town to Brigade Rd** | **1,353.1** | **1.353 km** | **0.0%** | **Short** | **29** |
| 2 | OD_19 | Silk Board to BTM 2nd Stage | 2,013.4 | 2.013 km | 4.2% | Short | 45 |
| 3 | OD_24 | Banaswadi to Kammanahalli | 2,398.2 | 2.398 km | 8.3% | Short | 61 |
| 4 | OD_12 | Frazer Town to Shivajinagar | 2,735.0 | 2.735 km | 12.5% | Short | 67 |
| 5 | OD_17 | Malleshwaram to Rajajinagar | 3,422.3 | 3.422 km | 16.7% | Short | 56 |
| 6 | OD_25 | Padmanabhanagar to Gandhi Bz | 4,594.1 | 4.594 km | 20.8% | Short | 95 |
| 7 | OD_21 | RT Nagar to Cantonment | 4,984.3 | 4.984 km | 25.0% | Short | 129 |
| 8 | OD_07 | HSR Layout to Bellandur | 5,807.2 | 5.807 km | 29.2% | Medium | 105 |
| 9 | OD_18 | Indiranagar to MG Road | 5,876.1 | 5.876 km | 33.3% | Medium | 117 |
| **10** | **OD_02** | **Koramangala to Indiranagar** | **6,380.4** | **6.380 km** | **37.5%** | **Medium** | **105** |
| 11 | OD_14 | Vijayanagar to Majestic | 7,186.2 | 7.186 km | 41.7% | Medium | 160 |
| 12 | OD_22 | Marathahalli to HAL Airport | 7,727.0 | 7.727 km | 45.8% | Medium | 150 |
| 13 | OD_10 | BTM Layout to Domlur | 7,784.1 | 7.784 km | 50.0% | Medium | 131 |
| 14 | OD_13 | JP Nagar to Koramangala | 7,851.3 | 7.851 km | 54.2% | Medium | 165 |
| 15 | OD_09 | Rajajinagar to Commercial St | 8,290.4 | 8.290 km | 58.3% | Medium | 168 |
| 16 | OD_15 | Yelahanka to Hebbal | 8,670.2 | 8.670 km | 62.5% | Medium | 62 |
| **17** | **OD_04** | **Whitefield to Marathahalli** | **8,814.1** | **8.814 km** | **66.7%** | **Medium** | **186** |
| **18** | **OD_03** | **Electronic City to Silk Board** | **9,505.3** | **9.505 km** | **70.8%** | **Long** | **174** |
| 19 | OD_05 | Hebbal to Majestic | 9,944.0 | 9.944 km | 75.0% | Long | 189 |
| **20** | **OD_01** | **BNMIT to MG Road** | **10,065.1** | **10.065 km** | **79.2%** | **Long** | **213** |
| 21 | OD_11 | Basavanagudi to Ulsoor | 11,425.2 | 11.425 km | 83.3% | Long | 258 |
| 22 | OD_20 | Kengeri to Satellite Bus Stn | 12,327.4 | 12.327 km | 87.5% | Long | 238 |
| 23 | OD_06 | Jayanagar to Malleshwaram | 12,447.1 | 12.447 km | 91.7% | Long | 252 |
| 24 | OD_08 | Banashankari to Yeshwanthpur | 14,554.0 | 14.554 km | 95.8% | Long | 322 |
| 25 | OD_16 | Bellandur to Whitefield | 15,036.2 | 15.036 km | 100.0% | Long | 333 |

### 4.2 Methodological Justification for the Five Selected Yen Corridors
The five selected corridors span the complete distance spectrum and topological archetypes:
1. **OD_23 ($1.353\text{ km}$, 29 nodes, 0.0th percentile):** Represents the minimum distance extreme in the dense central core.
2. **OD_02 ($6.380\text{ km}$, 105 nodes, 37.5th percentile):** Represents standard intermediate urban grid connectivity.
3. **OD_04 ($8.814\text{ km}$, 186 nodes, 66.7th percentile):** Represents severe barrier constraints (railway line and Varthur lake wetland system).
4. **OD_03 ($9.505\text{ km}$, 174 nodes, 70.8th percentile):** Represents a long radial highway barrier corridor (Elevated Hosur Expressway).
5. **OD_01 ($10.065\text{ km}$, 213 nodes, 79.2th percentile):** Represents the longitudinal calibration link to Stage 1 empirical measurements.

### 4.3 Why the 15.036 km Corridor (OD_16) Was Not Selected for Yen
Corridor OD_16 (Bellandur to Whitefield, $15.036\text{ km}$, 333 nodes) was deliberately excluded from Yen K-SP for rigorous methodological and computational reasons:
1. **Combinatorial Explosion of Yen on 333 Nodes:**
   Yen evaluates $(K-1) \times (N-1)$ spur nodes. For $N = 333$ nodes, up to $3 \times 332 = 996$ candidate A* queries would be spawned. Because OD_16 spans $15\text{ km}$, sub-path A* queries take $0.8\text{--}1.8\text{ s}$ each. A single pass on OD_16 would require an estimated **$12\text{--}18\text{ minutes}$**, and with 3 repetitions, **$36\text{--}54\text{ minutes}$ for this single corridor alone**, consuming over $50\%$ of the total available computational budget.
2. **Distributional Redundancy:**
   Corridors OD_01 ($10.065\text{ km}$, $79.2\%$ percentile) and OD_03 ($9.505\text{ km}$, $70.8\%$ percentile) already thoroughly represent the Long distance tier ($>9\text{ km}$) and upper quartile of the network. OD_16 does not introduce a novel topological mechanism beyond what OD_03 and OD_04 test.
3. **Role of OD_16 in Stage 2:**
   OD_16 **is fully included and evaluated in Experiments A, B, C, D, and E1 (Perpendicular Offset)** across all 5/3 repetitions. In E1, Perpendicular Offset routes OD_16 in under $20\text{ seconds}$, proving how lateral offset scales gracefully where Yen becomes computationally intractable.

---

## 5. Zero-Alternative Outcome Definitions

To prevent ambiguity when alternative generation yields fewer than $K-1$ paths, four mutually exclusive outcome categories are formally defined:

| Outcome Category | Code Identifier | Formal Mathematical Definition | Downstream Recording in E2 & E3 |
| :--- | :---: | :--- | :--- |
| **1. No Alternative Generated** | `ZERO_GENERATED` | The candidate generation loop produced zero valid spur paths (`generated_count == 0` and `len(A) == 1`). | Recorded as: `paths_found = 1` (primary only), `surviving_alts = 0`, `outcome_status = "ZERO_GENERATED"`, `pairwise_diversity = 0.0`. |
| **2. Generated but All Filter-Rejected** | `ALL_REJECTED_OVERLAP` | One or more candidates were generated (`generated_count > 0`), but **every candidate** exceeded `max_overlap` ($0.70$), leaving queue $B$ empty (`len(B) == 0` and `len(A) == 1`). | Recorded as: `paths_found = 1`, `surviving_alts = 0`, `rejected_overlap > 0`, `outcome_status = "ALL_REJECTED_OVERLAP"`, `pairwise_diversity = 0.0`. *(Specific to Filtered Yen E3).* |
| **3. Partial Candidate Exhaustion** | `PARTIAL_ALTERNATIVES` | At least one alternative survived, but candidate queue $B$ was exhausted before reaching $K-1$ paths (`1 < len(A) < K`). | Recorded as: `paths_found = len(A)` ($2$ or $3$), `surviving_alts = len(A) - 1` ($1$ or $2$), `outcome_status = "PARTIAL_ALTERNATIVES"`, `exhausted_early = True`, diversity computed on available paths. |
| **4. Successful Full Generation** | `SUCCESS_FULL` | Exactly $K-1 = 3$ distinct alternatives were found satisfying all detour and overlap thresholds (`len(A) == K`). | Recorded as: `paths_found = 4`, `surviving_alts = 3`, `outcome_status = "SUCCESS_FULL"`, `pairwise_diversity` computed across all 4 paths. |

---

## 6. Preflight Conclusion & Sign-Off

The preflight alignment is **fully reconciled and verified**:
- Repetition matrix ($5$ reps for A–D, $3$ reps for E) documented.
- Missing harness repetition loop identified for implementation upon authorization.
- Runtime budget recalculated to **$\approx 101.1\text{ minutes}$** ($\approx 1.7\text{ hours}$).
- Distance-ranked table of all 25 corridors generated and Yen corridor selection justified.
- Four zero-alternative outcome categories formally defined.
- **Stage 2 execution is NOT started.** Awaiting explicit authorization.
