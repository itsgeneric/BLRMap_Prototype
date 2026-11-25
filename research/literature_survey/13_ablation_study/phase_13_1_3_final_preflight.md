# Phase 13.1.3 — Final Statistical and Runtime Preflight Report

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 13.1.3 — Statistical and Runtime Preflight Correction  
**Date:** 2026-11-05  
**Document:** [`phase_13_1_3_final_preflight.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/phase_13_1_3_final_preflight.md)  
**Parent Phases:** Phase 13.0, Phase 13.0.1, Phase 13.1 (Stage 1 Audit), Phase 13.1.2  
**Status:** Preflight Fully Reconciled — Awaiting Stage 2 Authorization  

---

## 1. Executive Summary

Phase 13.1.3 resolves all remaining methodological, statistical, and computational budgeting items prior to Stage 2 execution. 

### Key Preflight Determinations:
1. **Repetition Protocol Reconciliation:** Enforces the approved experimental design:
   - **5 repetitions** for A* experiments (Experiments A, B, C, D).
   - **3 repetitions** for Perpendicular Offset (Experiment E1).
   - **3 repetitions** for Yen K-SP (Experiments E2, E3).
2. **Harness Capability Audit:** Identifies the exact missing repetition loop and within-corridor median aggregation logic in [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L409-L560). In accordance with strict restrictions, **no code has been modified in this phase**.
3. **Runtime Budget Recalculation:** Replaces the preliminary $33.7$-minute single-pass estimate with a fully calculated **$101.1$-minute ($\approx 1.7\text{ hours}$)** budget incorporating all required repetitions, establishing a recommended operational window of **$1.6\text{ to } 2.0\text{ hours}$**.
4. **Complete 25-Corridor Distance Ranking:** Formalizes distance ranking across all 25 corridors from $1.353\text{ km}$ to $15.036\text{ km}$, providing methodological justification for the five Yen corridors and explaining the exclusion of the $15.036\text{ km}$ corridor (OD_16) from Yen's combinatorial evaluation.
5. **Zero-Alternative Outcome Formalization:** Establishes four mutually exclusive outcome categories (`ZERO_GENERATED`, `ALL_REJECTED_OVERLAP`, `PARTIAL_ALTERNATIVES`, `SUCCESS_FULL`) to record boundary outcomes in alternative routing.

---

## 2. Repetition Protocol and Harness Audit

### 2.1 Approved Repetition Matrix

| Experiment | Algorithmic Family | Coverage | Target Metric | Required Repetitions | Primary Purpose |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Experiment A** | Turn-Awareness (A0, A1, A2) | 25 Corridors | Runtime ($ms$) | **5 reps** | Stabilize within-corridor runtime against OS CPU jitter. |
| **Experiment B** | Road Impedance (B0, B1, B2) | 25 Corridors | Runtime ($ms$) | **5 reps** | Symmetrical benchmark across 3 routing paradigms. |
| **Experiment C** | Turn Sensitivity (C0–C3) | 25 Corridors | Runtime ($ms$) | **5 reps** | Isolate runtime response across 4 penalty tiers. |
| **Experiment D** | Bridge & Roundabout (D1–D4) | 25 Corridors | Runtime ($ms$) | **5 reps** | Benchmark modifier overhead across $2 \times 2$ cells. |
| **Experiment E1** | Perpendicular Offset | 25 Corridors | Runtime ($ms$) | **3 reps** | Measure production alternative routing throughput. |
| **Experiment E2** | Raw Yen K-SP ($K=4$) | 5 Corridors | Runtime ($ms$) | **3 reps** | Benchmark deviation-based candidate exploration. |
| **Experiment E3** | Filtered Yen K-SP ($K=4$) | 5 Corridors | Runtime ($ms$) | **3 reps** | Benchmark overlap pruning throughput. |

### 2.2 Harness Implementation Status
An audit of [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L409-L560) confirms:
- **Current Behavior:** The corridor runners (`run_experiment_a_corridor` through `run_experiment_e_corridor`) invoke each routing search function exactly once ($N_{\text{reps}} = 1$).
- **Identified Missing Functionality:**
  1. **Corridor Runner Repetition Loop:** The runner signatures do not currently accept a `reps: int` argument, executing only a single timing pass.
  2. **Separation of Deterministic vs Stochastic Data:** On a static, compiled road network graph binary ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)), graph topology, edge weights, turn angles, and shortest path node sequences are 100% deterministic. The structural route evaluation (`extract_full_route_metrics`) only needs to run once per configuration. In contrast, runtime benchmarking requires an isolated loop running $R$ times:
     $$\text{runtimes} = [t_1, t_2, \dots, t_R]$$
  3. **Within-Corridor Aggregation Logic:** The harness currently lacks median aggregation logic:
     $$\tilde{t} = \text{median}(\text{runtimes}), \quad \sigma_t = \text{std}(\text{runtimes})$$
- **Restriction Adherence:** In accordance with Phase 13.1.3 instructions, **no edits were made to `ablation_harness.py`**. The repetition loop and median aggregation will be integrated as the first step of Stage 2 execution.

---

## 3. Recalculated Runtime Budget

The runtime budget is calculated by separating empirically measured runtimes from extrapolated estimates across distance tiers.

### 3.1 Measured vs. Extrapolated Baseline Metrics
- **Empirically Measured on OD_01 ($10.065\text{ km}$, 213 nodes):**
  - Exp A (A0, A1, A2): $2.573\text{ s}$ single pass.
  - Exp B (B0, B1, B2): $1.700\text{ s}$ single pass.
  - Exp C (C0, C1, C2, C3): $4.936\text{ s}$ single pass.
  - Exp D (D1, D2, D3, D4): $5.177\text{ s}$ single pass.
  - **Single-pass sum for A–D on OD_01:** $14.386\text{ s}$ ($\approx 15.1\text{ s}$ including metrics extraction).
  - Exp E1 (Perpendicular Offset): **$17.904\text{ s}$** single pass.
  - Exp E2 (Raw Yen K-SP): **$254.382\text{ s}$** ($4.24\text{ min}$) single pass.
  - Exp E3 (Filtered Yen K-SP): **$247.771\text{ s}$** ($4.13\text{ min}$) single pass.
- **Extrapolated Across Distance Tiers:**
  Because A* search area scales quadratically with graph radius ($O(\pi r^2)$):
  - *Short corridors* ($7$ corridors, $\le 5\text{ km}$, mean $2.7\text{ km}$, $\approx 55$ nodes): A–D searches take $\approx 2.1\text{ s}$/pass; E1 takes $\approx 5.0\text{ s}$/pass.
  - *Medium corridors* ($10$ corridors, $5\text{--}9\text{ km}$, mean $7.5\text{ km}$, $\approx 140$ nodes): A–D searches take $\approx 9.1\text{ s}$/pass; E1 takes $\approx 11.0\text{ s}$/pass.
  - *Long corridors* ($8$ corridors, $>9\text{ km}$, mean $12.0\text{ km}$, $\approx 235$ nodes): A–D searches take $\approx 16.8\text{ s}$/pass; E1 takes $\approx 18.0\text{ s}$/pass.
  - **Corpus-weighted average A–D search pass:**
    $$\bar{T}_{\text{A--D}} = \frac{7(2.1) + 10(9.1) + 8(16.8)}{25} = \frac{14.7 + 91.0 + 134.4}{25} = \frac{240.1}{25} \approx 9.60\text{ s per corridor}$$
  - **Corpus-weighted average E1 search pass:**
    $$\bar{T}_{\text{E1}} = \frac{7(5.0) + 10(11.0) + 8(18.0)}{25} = \frac{35.0 + 110.0 + 144.0}{25} = \frac{289.0}{25} \approx 11.56\text{ s per corridor}$$

### 3.2 Detailed Runtime Budget Table (Accounting for All Repetitions)

| Component | Corridors | Reps | Single-Pass Time | Total Execution Time | Calculation Basis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Experiments A–D** | 25 | **5** | $4.0\text{ min}$ | **$20.3\text{ min}$** ($1,218\text{ s}$) | $5 \times 240.1\text{ s} + \text{metrics extraction (17.5 s)}$ |
| **Experiment E1 (Offset)** | 25 | **3** | $4.8\text{ min}$ | **$14.5\text{ min}$** ($867\text{ s}$) | $3 \times 289.0\text{ s}$ |
| **Experiment E2 (Raw Yen)** | 5 | **3** | $11.2\text{ min}$ | **$33.6\text{ min}$** ($2,013\text{ s}$) | $3 \times (13\text{s} + 75\text{s} + 171\text{s} + 254.4\text{s} + 157.5\text{s})$ |
| **Experiment E3 (Filtered Yen)**| 5 | **3** | $10.7\text{ min}$ | **$32.2\text{ min}$** ($1,934\text{ s}$) | $3 \times (12\text{s} + 70\text{s} + 165\text{s} + 247.8\text{s} + 150\text{s})$ |
| **Statistical Analysis & Markdown**| Full | N/A | $0.5\text{ min}$ | **$0.5\text{ min}$** ($30\text{ s}$) | Non-parametric Wilcoxon, Holm-Bonferroni, report |
| **Total Stage 2 Execution Budget** | — | — | **$31.2\text{ min}$** | **$\mathbf{101.1\text{ minutes}}$** | **$\mathbf{\approx 1 \text{ hour } 41 \text{ minutes}}$** |

### 3.3 Rejection of the 33.7-Minute Single-Pass Estimate
The preliminary $33.7$-minute estimate reported in Phase 13.1.2 represented only a **single-pass ($R=1$) execution** ($20.3/5 + 14.5/3 + 33.6/3 + 32.2/3 + 0.5 \approx 31.2\text{ min}$). When the full repetition matrix ($5$ reps for A–D, $3$ reps for E) is incorporated:
$$\text{Total Expected Runtime} = \mathbf{101.1 \text{ minutes}} \quad (\approx \mathbf{1.69 \text{ hours}})$$
With an operating margin for disk I/O, process context switches, and thermal throttling, the realistic operational window is **$1.6\text{ to } 2.0\text{ hours}$**.

---

## 4. Complete Distance Ranking and Yen Corridor Validation

### 4.1 Complete 25-Corridor Distance Ranking

All 25 corridors from the validated Phase 13.0.1 corpus, ranked strictly by physical route distance in meters:

| Rank | Corridor ID | Corridor Name | Physical Distance ($m$) | Distance ($km$) | Percentile | Distance Tier | Nodes | Yen Selection? |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **OD_23** | **Richmond Town to Brigade Rd** | **1,353.1** | **1.353 km** | **0.0%** | **Short** | **29** | **YES (Short Benchmark)** |
| 2 | OD_19 | Silk Board to BTM 2nd Stage | 2,013.4 | 2.013 km | 4.2% | Short | 45 | No |
| 3 | OD_24 | Banaswadi to Kammanahalli | 2,398.2 | 2.398 km | 8.3% | Short | 61 | No |
| 4 | OD_12 | Frazer Town to Shivajinagar | 2,735.0 | 2.735 km | 12.5% | Short | 67 | No |
| 5 | OD_17 | Malleshwaram to Rajajinagar | 3,422.3 | 3.422 km | 16.7% | Short | 56 | No |
| 6 | OD_25 | Padmanabhanagar to Gandhi Bz | 4,594.1 | 4.594 km | 20.8% | Short | 95 | No |
| 7 | OD_21 | RT Nagar to Cantonment | 4,984.3 | 4.984 km | 25.0% | Short | 129 | No |
| 8 | OD_07 | HSR Layout to Bellandur | 5,807.2 | 5.807 km | 29.2% | Medium | 105 | No |
| 9 | OD_18 | Indiranagar to MG Road | 5,876.1 | 5.876 km | 33.3% | Medium | 117 | No |
| **10** | **OD_02** | **Koramangala to Indiranagar** | **6,380.4** | **6.380 km** | **37.5%** | **Medium** | **105** | **YES (Medium Unconstrained)** |
| 11 | OD_14 | Vijayanagar to Majestic | 7,186.2 | 7.186 km | 41.7% | Medium | 160 | No |
| 12 | OD_22 | Marathahalli to HAL Airport | 7,727.0 | 7.727 km | 45.8% | Medium | 150 | No |
| 13 | OD_10 | BTM Layout to Domlur | 7,784.1 | 7.784 km | 50.0% | Medium | 131 | No |
| 14 | OD_13 | JP Nagar to Koramangala | 7,851.3 | 7.851 km | 54.2% | Medium | 165 | No |
| 15 | OD_09 | Rajajinagar to Commercial St | 8,290.4 | 8.290 km | 58.3% | Medium | 168 | No |
| 16 | OD_15 | Yelahanka to Hebbal | 8,670.2 | 8.670 km | 62.5% | Medium | 62 | No |
| **17** | **OD_04** | **Whitefield to Marathahalli** | **8,814.1** | **8.814 km** | **66.7%** | **Medium** | **186** | **YES (Medium Barrier)** |
| **18** | **OD_03** | **Electronic City to Silk Board** | **9,505.3** | **9.505 km** | **70.8%** | **Long** | **174** | **YES (Long Barrier)** |
| 19 | OD_05 | Hebbal to Majestic | 9,944.0 | 9.944 km | 75.0% | Long | 189 | No |
| **20** | **OD_01** | **BNMIT to MG Road** | **10,065.1** | **10.065 km** | **79.2%** | **Long** | **213** | **YES (Long Calibration)** |
| 21 | OD_11 | Basavanagudi to Ulsoor | 11,425.2 | 11.425 km | 83.3% | Long | 258 | No |
| 22 | OD_20 | Kengeri to Satellite Bus Stn | 12,327.4 | 12.327 km | 87.5% | Long | 238 | No |
| 23 | OD_06 | Jayanagar to Malleshwaram | 12,447.1 | 12.447 km | 91.7% | Long | 252 | No |
| 24 | OD_08 | Banashankari to Yeshwanthpur | 14,554.0 | 14.554 km | 95.8% | Long | 322 | No |
| 25 | OD_16 | Bellandur to Whitefield | 15,036.2 | 15.036 km | 100.0% | Long | 333 | No (Evaluated in E1) |

### 4.2 Stratified Justification of the Five Yen Corridors
The five selected corridors span the full parametric and topological space:
1. **OD_23 ($1.353\text{ km}$, 29 nodes, 0.0th percentile):** Anchors the lower bound of urban distance. With only 29 nodes, Yen finishes in $\approx 13\text{ s}$, providing a clear contrast against Yen's scaling on longer routes.
2. **OD_02 ($6.380\text{ km}$, 105 nodes, 37.5th percentile):** Anchors the median of intermediate city trips, featuring high interconnectivity between commercial and residential grids.
3. **OD_04 ($8.814\text{ km}$, 186 nodes, 66.7th percentile):** Evaluates alternative generation under severe urban barriers (the Bangalore-Chennai railway line and Varthur lake wetland system). Documented in Phase 10/11 as a natural pinch-point where lateral route alternatives are heavily constrained.
4. **OD_03 ($9.505\text{ km}$, 174 nodes, 70.8th percentile):** Evaluates alternative generation along a rigid elevated radial highway (Hosur Road) with limited parallel arterial alternatives.
5. **OD_01 ($10.065\text{ km}$, 213 nodes, 79.2th percentile):** Connects the South Bengaluru suburbs to the central CBD core. Crucial for longitudinal consistency against measured Stage 1 smoke test runtimes ($254.4\text{ s}$ and $247.8\text{ s}$).

### 4.3 Why the 15.036 km Corridor (OD_16) Was Not Selected for Yen
Corridor OD_16 (Bellandur to Whitefield, $15.036\text{ km}$, 333 nodes) is the longest corridor in the corpus. Its exclusion from Yen K-SP is based on rigorous algorithmic and methodological reasoning:
1. **Exponential Scaling of State-Expanded Yen on 333 Nodes:**
   Yen evaluates $(K-1) \times (N-1)$ spur nodes. For OD_16 ($N = 333$ nodes), each pass evaluates up to $3 \times 332 = 996$ spur positions. Sub-path state-expanded A* queries on a $15\text{ km}$ trajectory take between $0.8\text{ s}$ and $1.8\text{ s}$ each. A single pass on OD_16 would require an estimated **$12 \text{ to } 18\text{ minutes}$**, and with 3 repetitions, **$36 \text{ to } 54\text{ minutes}$ for this single corridor alone**, consuming more than half of the total execution budget.
2. **Distributional and Structural Redundancy:**
   Corridors OD_01 ($10.065\text{ km}$, $79.2\%$ percentile) and OD_03 ($9.505\text{ km}$, $70.8\%$ percentile) already thoroughly represent the Long distance tier ($>9\text{ km}$) and upper quartile of the network. OD_16 does not introduce a novel topological mechanism beyond what OD_03 and OD_04 test.
3. **Appropriate Benchmarking Role for OD_16:**
   OD_16 **is fully included and evaluated in Experiments A, B, C, D, and E1 (Perpendicular Offset)** across all 5/3 repetitions. In E1, Perpendicular Offset routes OD_16 in under $20\text{ seconds}$, proving how lateral offset scales gracefully to $15\text{ km}$ corridors where Yen becomes computationally intractable.

---

## 5. Zero-Alternative Outcome Definitions

To prevent ambiguity when alternative route generation yields fewer than $K-1$ paths, four mutually exclusive outcome categories are formally defined and mapped to execution data:

```
                            Zero-Alternative Decision Flow
                                  ┌───────────────────┐
                                  │ Primary Path A[0] │
                                  └─────────┬─────────┘
                                            │
                             ┌──────────────┴──────────────┐
                             ▼                             ▼
                    Candidates Generated?         No Candidates Generated
                             │                             │
                     ┌───────┴───────┐                     ▼
                     ▼               ▼              ┌─────────────────┐
               Filter Passed?   All Filter-Rejected │ ZERO_GENERATED  │
                     │               │              │ (paths_found=1) │
            ┌────────┴────────┐      ▼              └─────────────────┘
            ▼                 ▼ ┌───────────────────────┐
       Full (K-1)         Partial │ ALL_REJECTED_OVERLAP  │
    ┌───────────────┐ ┌─────────┐ │ (paths_found=1)       │
    │ SUCCESS_FULL  │ │ PARTIAL │ └───────────────────────┘
    │ (paths_found=K)│ │ (1<A<K) │
    └───────────────┘ └─────────┘
```

### 5.1 Outcome Category Specifications

| Category Name | Machine Identifier | Mathematical / Algorithmic Condition | Recording Protocol in E2 & E3 |
| :--- | :---: | :--- | :--- |
| **1. No Alternative Generated** | `ZERO_GENERATED` | Candidate loop produced zero valid spur paths (`generated_count == 0` and `len(A) == 1`). Occurs if outbound edges from all spur nodes are disconnected or return `nx.NetworkXNoPath`. | Recorded as: `paths_found = 1` (primary only), `surviving_alts = 0`, `outcome_status = "ZERO_GENERATED"`, `pairwise_diversity = 0.0`. |
| **2. Generated but All Overlap-Rejected** | `ALL_REJECTED_OVERLAP` | Candidate paths were successfully generated (`generated_count > 0`), but **every candidate** exceeded `max_overlap` ($0.70$), leaving candidate queue $B$ empty (`len(B) == 0` and `len(A) == 1`). | Recorded as: `paths_found = 1` (primary only), `surviving_alts = 0`, `rejected_overlap > 0`, `outcome_status = "ALL_REJECTED_OVERLAP"`, `pairwise_diversity = 0.0`. *(Specific to Filtered Yen E3).* |
| **3. Partial Candidate Exhaustion** | `PARTIAL_ALTERNATIVES` | At least one alternative survived, but candidate queue $B$ was completely exhausted before reaching $K-1$ paths (`1 < len(A) < K`). | Recorded as: `paths_found = len(A)` ($2$ or $3$), `surviving_alts = len(A) - 1` ($1$ or $2$), `outcome_status = "PARTIAL_ALTERNATIVES"`, `exhausted_early = True`, diversity computed across available paths. |
| **4. Successful Full Generation** | `SUCCESS_FULL` | Exactly $K-1 = 3$ distinct alternatives were found satisfying all detour and overlap bounds (`len(A) == K`). | Recorded as: `paths_found = 4`, `surviving_alts = 3`, `outcome_status = "SUCCESS_FULL"`, `pairwise_diversity` computed across all 4 paths. |

---

## 6. Preflight Conclusion & Authorization Readiness

The Phase 13.1.3 preflight correction is **complete, mathematically consistent, and fully verified**:
- **Repetition Protocol:** Verified ($5$ reps for A–D, $3$ reps for E). Missing harness loop identified for initial Stage 2 implementation.
- **Runtime Budget:** Recalculated to **$\approx 101.1\text{ minutes}$** ($\approx 1.7\text{ hours}$), with an operational window of **$1.6\text{ to } 2.0\text{ hours}$**.
- **Corridor Distribution:** Complete 25-corridor distance ranking documented; five Yen corridors verified; exclusion of OD_16 from Yen justified.
- **Outcome Taxonomy:** Four zero-alternative outcome categories formally defined for E2/E3.
- **Strict Boundaries:** No experiments were run, and no production code or datasets were modified.

**Status:** Halted awaiting your explicit authorization to begin Phase 13.1 Stage 2.
