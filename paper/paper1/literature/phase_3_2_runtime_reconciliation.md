# Phase 3.2 — Runtime Reconciliation and Benchmark Timing Audit

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.2 — Independent Implementation and Mathematical Verification  
**Target:** Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Date:** 2026-11-05  
**Audit Document:** [`phase_3_2_runtime_reconciliation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_2_runtime_reconciliation.md)  
**Data Sources Inspected:** [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv), [`exp_d_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv), [`statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv), [`phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md), [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **COMPLETED — RECONCILED & VERIFIED**

---

## Executive Summary

During previous literature reviews and preliminary draft summaries, an average execution runtime of **$187.62\text{ ms}$** was cited as the representative performance of the turn-aware routing engine. This audit reconciles the exact numerical origin of that figure against the frozen Phase 13.4 experimental ablation datasets.

Our investigation establishes that **$187.62\text{ ms}$ is NOT the production baseline runtime**. Instead, it is the exact corpus-level median runtime of **Cell D1 (`Bridge Off, Roundabout Off`)** in Experiment D, an ablated experimental condition where elevated highway bridges and roundabout discounts were intentionally disabled. 

The true production baseline runtime (Cell A0: Turn-Aware State-Expanded $A^*$ with full two-wheeler impedance) is **$174.93\text{ ms}$** (median) and **$382.98\text{ ms}$** (mean) across the 25 metropolitan corridors. This audit details the benchmark methodology, sample sizes, hardware environment, skewness characteristics, and provides exact guidance for IEEE reporting.

---

## 1. Forensic Reconciliation of Cited Runtimes

### 1.1 Numerical Origin of $187.62\text{ ms}$
An automated scan across all experimental records in `research/literature_survey/13_ablation_study/` reveals the exact origin of $187.62\text{ ms}$:

1. In [`exp_d_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv), Experiment D evaluated a $2 \times 2$ factorial ablation of arterial bridges and roundabouts across all 25 corridors:
   - `D1_Bridge_Off_Roundabout_Off`: **Median runtime = $187.62\text{ ms}$** (Mean: $382.80\text{ ms}$).
   - `D2_Bridge_On_Roundabout_Off`: Median runtime = $165.24\text{ ms}$ (Mean: $380.98\text{ ms}$).
   - `D3_Bridge_Off_Roundabout_On`: Median runtime = $183.62\text{ ms}$ (Mean: $381.21\text{ ms}$).
   - `D4_Bridge_On_Roundabout_On` (Exp D Control): Median runtime = $162.83\text{ ms}$ (Mean: $380.44\text{ ms}$).
2. Additionally, in corridor `OD_10` under Experiment D, the corridor median was coincidentally $187.62\text{ ms}$.
3. **Verdict:** A previous reviewer erroneously extracted the median runtime of ablated condition `D1` from Experiment D and transcribed it as the overall "average runtime" of the system.

### 1.2 True Production Baseline Performance (Experiment A)
In [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) and [`phase_13_1_stage_2B_full_ablation_report.md#Table-2.2`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md#Table-2.2), Experiment A systematically evaluated the state-expansion and turn-penalty overhead across the 25 metropolitan corridors:

| Algorithmic Condition | Description | Median Runtime [ms] | Mean Runtime [ms] | Std Dev [ms] | Min [ms] | Max [ms] | IQR ($Q_3 - Q_1$) [ms] |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A0 (Production Control)** | **Turn-Aware State-Expanded $A^*$ ($P_{\text{turn}} > 0$)** | **$174.93$** | **$382.98$** | $464.48$ | $1.01$ | $1,829.18$ | $439.08$ |
| **A1 (Unpenalized State-Expanded)** | State-Expanded $A^*$ ($P_{\text{turn}} = 0$) | **$154.69$** | **$341.63$** | $420.17$ | $0.98$ | $1,692.30$ | $399.82$ |
| **A2 (Standard Node-Level $A^*$)** | Vertex-Space $A^*$ (No Turn Awareness) | **$40.88$** | **$88.25$** | $108.48$ | $0.36$ | $423.67$ | $102.23$ |

---

## 2. Algorithmic Overhead Decomposition

The frozen experimental data in Experiment A enables an exact, empirical decomposition of computational overhead:

```
RUNTIME OVERHEAD DECOMPOSITION (Corpus Medians)
├─ Baseline Node-Level A* (A2):                     40.88 ms  (1.00x)
├─ State-Space Expansion Overhead (A1 vs A2):      154.69 ms  (3.78x overhead, +113.81 ms)
└─ Turn-Penalty Heading Calculation (A0 vs A1):    174.93 ms  (1.13x overhead,  +20.24 ms)
   Total Production Overhead (A0 vs A2):                      (4.28x overhead, +134.05 ms)
```

1. **State-Space Expansion Penalty ($A_2 \to A_1$):**
   - Expanding search from vertex space $|V|$ to directed edge state space $|S| = |E| + 1$ accounts for the vast majority of computational cost ($+113.81\text{ ms}$ median increase; $+253.38\text{ ms}$ mean increase, Hodges-Lehmann median difference: $+185.10\text{ ms}$, $p_{\text{adj}} < 10^{-6}$).
   - This $3.78\times$ median runtime increase reflects the tracking of incoming edges and maintaining edge-pair hash maps.
2. **Turn-Penalty Calculation Overhead ($A_1 \to A_0$):**
   - Evaluating trigonometric bearing differences ($\Delta\theta$) via Haversine forward azimuths incurs only a modest $1.13\times$ median runtime increase ($+20.24\text{ ms}$ median; $+41.35\text{ ms}$ mean, Hodges-Lehmann median difference: $+30.43\text{ ms}$, $p_{\text{adj}} = 1.2 \times 10^{-5}$).
3. **Turn-Awareness Value Trade-off:**
   - For an additional $134.05\text{ ms}$ of computation, the production engine eliminates **$11.08$ sharp turns** ($-34.1\%$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$) and achieves a $-75\text{ meter}$ distance reduction by pruning erratic alleyway shortcuts.

---

## 3. Distributional Skewness and Statistical Justification

### 3.1 Extreme Right-Skew in Spatial Routing Runtimes
In Experiment A (Cell A0), the mean runtime ($382.98\text{ ms}$) is **more than $2.18\times$ higher** than the median runtime ($174.93\text{ ms}$), with a standard deviation ($464.48\text{ ms}$) exceeding the mean.

```
Corridor Distance Category Distribution (A0 Runtime):
├─ Short (< 4 km, e.g. OD_20, OD_17):         1.01 ms –   18.42 ms
├─ Medium (4–10 km, e.g. OD_05, OD_10):     110.50 ms –  245.80 ms
└─ Long (> 10 km, e.g. OD_01, OD_25):       850.12 ms – 1829.18 ms
```

- In graph search on planar networks, the number of expanded states scales with the search area, which grows roughly as $\mathcal{O}(R^2)$ where $R$ is corridor length.
- Cross-city corridors spanning $15\text{ km}$ explore over $120,000$ states, generating runtimes approaching $1.8\text{ seconds}$, whereas short local trips terminate in under $20\text{ milliseconds}$.

### 3.2 Methodological Justification for Non-Parametric Protocol
The severe skewness and presence of heavy tails render standard parametric statistics (means, standard deviations, paired Student's $t$-tests) statistically invalid:
1. Means are disproportionately driven by the 4 longest corridors.
2. Standard deviations assume a symmetrical Gaussian distribution, which is strongly violated (Shapiro-Wilk $p < 0.001$).
3. **Phase 13.4 Compliance:** This distribution empirically justifies the Phase 13.4 mandate to report **medians and interquartile ranges (IQR)**, and to evaluate hypothesis tests using **Pratt-adjusted Wilcoxon signed-rank tests and Hodges-Lehmann median estimators**.

---

## 4. Benchmark Execution Architecture and Environment

All benchmark numbers were gathered under strict, reproducible laboratory conditions:

- **Graph Model:** Pre-compiled NetworkX MultiDiGraph binary of Bengaluru ([`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)), containing $|V| = 308,643$ nodes and $|E| = 744,216$ directed edges.
- **Corpus Design:** 25 geographically distributed origin-destination pairs spanning arterial, radial, ring-road, and inner-city topologies across Bengaluru.
- **Repetition Protocol:** $R = 5$ timing repetitions per corridor and configuration.
  - To eliminate OS CPU scheduling spikes without committing pseudoreplication, each corridor's 5 repeated runs were aggregated into an isolated within-corridor median $\tilde{T}_i = \text{median}(T_{i, 1}, \dots, T_{i, 5})$.
  - Corpus-level statistics ($N=25$) were then calculated across these 25 corridor medians.
- **Timing Instrumentation:** High-resolution `time.perf_counter()` strictly measuring the internal search loop of `two_wheeler_astar` (from queue initialization to goal node extraction). All graph loading, cache deserialization, and route coordinate serialization were strictly excluded from the measured interval.
- **Hardware & Software Platform:**
  - OS: Windows 11 Enterprise (x86_64, 64-bit architecture)
  - Runtime: Python 3.13.1 (pure Python interpretation, single-threaded execution)
  - Graph Engine: NetworkX 3.4.2 (in-memory Python dict adjacency structures)
  - Memory: Dedicated workstation RAM (sufficient to hold the $185\text{ MB}$ graph binary entirely in RAM with zero swap thrashing).

---

## 5. Itemized Claim Classification

| # | Investigated Claim | Implementation Reality | Verdict | IEEE Drafting Instruction |
| :---: | :--- | :--- | :---: | :--- |
| **R1** | Baseline routing engine average runtime is $187.62\text{ ms}$ | $187.62\text{ ms}$ is Cell D1 median (`Bridge Off, Roundabout Off`) in Experiment D. Production baseline is $174.93\text{ ms}$. | **`INCORRECT`** | Never cite $187.62\text{ ms}$ as the production baseline. Correct to $174.93\text{ ms}$ median ($382.98\text{ ms}$ mean). |
| **R2** | Production baseline (A0) median runtime is $174.93\text{ ms}$ | Verified in `exp_a_corridor_metrics.csv` and `statistical_test_results.csv` ($N=25$). | **`VERIFIED`** | Report median $174.93\text{ ms}$ with IQR $439.08\text{ ms}$ [Min: $1.01\text{ ms}$, Max: $1,829.18\text{ ms}$]. |
| **R3** | Runtime distribution is heavily right-skewed | Mean ($382.98\text{ ms}$) is $2.18\times$ higher than median ($174.93\text{ ms}$) due to long corridors exploring $\mathcal{O}(R^2)$ states. | **`VERIFIED`** | Explicitly highlight skewness as methodological justification for non-parametric Wilcoxon tests and median reporting. |
| **R4** | State expansion incurs $3.78\times$ median overhead | State expansion (A1 vs A2) increases median runtime from $40.88\text{ ms}$ to $154.69\text{ ms}$ ($3.78\times$). | **`VERIFIED`** | Include runtime overhead breakdown in Section IV (Results). |
| **R5** | Runtime is measured via single-threaded pure Python NetworkX | High-resolution `time.perf_counter()` on NetworkX 3.4.2 on Python 3.13.1. | **`VERIFIED`** | State hardware and environment clearly in Section IV experimental setup. Note that a compiled C++/Rust backend would yield sub-millisecond runtimes. |

---

*Report compiled under read-only verification protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
