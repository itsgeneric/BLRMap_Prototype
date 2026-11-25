# Phase 8.3-A Evidence Blueprint: Experimental Evaluation Evidence Mapping and Section Architecture (v1.6 Audited)

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.3-A6 — Experiment D Search-Time vs. Post-Hoc Metric Audit  
**Date:** 2026-11-06  
**Document:** [`phase_8_3_A_experimental_evidence_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_A_experimental_evidence_blueprint.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Parent Figure/Table Plan:** [`paper1_figure_table_plan.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_figure_table_plan.md)  
**Authoritative Experimental Source:** [`research/literature_survey/13_ablation_study/`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/) (Frozen Phase 13.4 Dataset)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUDITED EXPERIMENTAL EVIDENCE BLUEPRINT (READY FOR RESEARCH-LEAD APPROVAL)**  

---

## 1. Executive Summary & Governance Scope

Phase 8.3-A establishes the traceable mathematical, statistical, and architectural blueprint for the empirical evaluation components of Paper 1:
- **Section V:** Experimental Setup & Methodology (~220 words)
- **Section VI:** Experimental Results & Analysis (~510 words)

This audited blueprint (v1.6) incorporates all Phase 8.3-A6 measurement-validity audit resolutions:
1. **Modifier Implementation Mechanics:** Codebase verification of [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L294-L327) and [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L248-L270) establishes the exact evaluation sequence in `two_wheeler_edge_cost`:
   - Bridge override is evaluated first: if `bridge=yes` on a main road (`motorway`, `trunk`, `primary`), `penalty` is assigned to $0.80$ (replacement).
   - Roundabout modifier is evaluated second: if `junction=roundabout`, `penalty` is multiplied by $0.95$ (`penalty *= rbt_mult`).
   - If an edge were both a bridge and a roundabout on a main road, the effective penalty would be $0.80 \times 0.95 = 0.76$.
2. **Roundabout Inventory and Correction of Corridor Discrepancy:** Direct inspection of [`exp_d_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv) confirms that **OD_06 (Jayanagar 4th Block to Malleshwaram)** is the **sole corridor** in the 25-corridor corpus that traverses roundabout infrastructure, with exactly **$62.98\text{ m}$** ($0.51\%$ of route distance). **OD_12 (Frazer Town to Shivajinagar)** contains **$0.0\text{ m}$** of roundabout infrastructure. All previous typographical references attributing the $62.98\text{ m}$ roundabout segment to OD_12 are formally corrected to OD_06.
3. **Four-Tier Metric Classification & Search-Objective Capture Verification:** Code execution audit of [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L662-L670) and [`ablation_metrics.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_metrics.py#L278-L353) establishes the rigorous classification of all Experiment D metrics:
   - **Class A (Search-time configuration-dependent cost):** **NONE RETAINED.** While `two_wheeler_astar` computed accumulated search objective cost $g(\text{goal})$ (`res["cost"]`), line 667 of `ablation_harness.py` discarded this value and passed only `res["route"]` to metric extraction. Configured search objective costs were **not retained** in CSV or JSON outputs; no unrecorded search costs may be reconstructed or claimed.
   - **Class B (Route geometry / physical route measurement):** `distance_km`, `bridge_length_m`, `bridge_pct`, `roundabout_length_m`, `roundabout_pct`. Evaluated directly on the returned vertex sequence `res["route"]`.
   - **Class C (Post-hoc standardized production score):** `impedance_cost`. Evaluated via `calc_post_hoc_path_cost` **outside** `scoped_ablation_context`, using restored default production penalties (bridge 0.8, roundabout 0.95, turn 25/8).
   - **Class D (Runtime measurement):** `runtime_ms`. Measured elapsed wall-clock latency across $R=5$ repetitions via `time.perf_counter()`.
4. **Resolution of Invariance vs. Cost on $D_2$ vs. $D_4$:** On OD_06, a $5\%$ discount on $62.98\text{ m}$ represents only $\approx 3.15\text{--}4.73$ impedance units out of $14,153.24$ ($\approx 0.025\%$), insufficient to trigger alternate path branches. Across all 25 corridors, route geometry is 100% invariant ($25/25$ identical node sequences). Because post-hoc standardized scoring evaluates those identical node sequences with fixed production weights, post-hoc `impedance_cost` is identical ($25/25$ zero differences, $p_{\text{adj}} = 1.0000$). This test reflects **complete route-geometry invariance under standardized scoring**, not an empirical finding of zero search-objective cost shift.
5. **Metric-by-Metric Equivalence Assessment between $(D_1 - D_2)$ and $(D_3 - D_4)$:** Recomputation reveals that $(D_1 - D_2)$ and $(D_3 - D_4)$ are **exactly equivalent** in route geometry ($25/25$ identical routes), physical distance ($23/25$ zeros, OD_04: $+0.645\text{ km}$, OD_15: $+2.146\text{ km}$), bridge traversal distance ($23/25$ zeros, OD_04: $-605.6\text{ m}$, OD_15: $-5,338.5\text{ m}$), roundabout traversal distance ($25/25$ zeros), and post-hoc standardized cost ($23/25$ zeros, OD_04: $+266.20$, OD_15: $+2,756.75$). However, execution runtime (`runtime_ms`) is **not equivalent** due to experimental timing jitter.
6. **Grounded Bridge Interpretation:** OpenStreetMap `bridge=yes` segments are traversed on **19 of the 25 corridors** under baseline routing ($D_1$). The $0.80$ modifier alters route selection on only **2 of those 19 corridors** (OD_04 and OD_15), while 23 corridors remain completely unchanged ($p_{\text{adj}} = 0.4722$). All overgeneralized claims have been purged.
7. **Table II Experiment D Decision:** In Table II, $D_3$ vs. $D_4$ is accurately labeled as **Post-Hoc Standardized Impedance Cost** (mean diff $+120.92$, $p_{\text{adj}} = 0.4722$). $D_2$ vs. $D_4$ is excluded from Table II and reported exclusively in Section VI-D text and extended records, establishing a strictly streamlined 10-test primary table.

---

## 2. Task 1: Authoritative Experimental Evidence Inventory

The following authoritative, frozen project artifacts contain the full empirical evidence base for Paper 1. No data values have been inferred, extrapolated, or synthesized.

| # | Artifact Filename & Relative Path | Evidence Contained | Data Classification | Authoritative Status | Limitations & Boundary Disclosures |
| :-: | :--- | :--- | :--- | :---: | :--- |
| **E-1** | [`research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json) | Complete execution records for all 1,855 timing observations across 385 experimental cells and 25 corridors. | Raw JSON Data | **Authoritative Primary Source** | Single-machine Windows 11 Enterprise environment; single-threaded execution benchmark. |
| **E-2** | [`research/literature_survey/13_ablation_study/statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv) | Summary table of 33 paired hypothesis tests across 11 families: Wilcoxon Pratt $W$, raw $p$, Holm $p_{\text{adj}}$, $t$-stat, Cohen's $d_z$ with 95% CI, rank-biserial $r$, Hodges-Lehmann with 95% CI, zero differences count. | Processed Statistical Output | **Authoritative Inferential Source** | Rows 2–28 govern Paper 1 (Families A–D, 27 tests). Rows 29–34 represent Family E (Paper 2) and are excluded. |
| **E-3** | [`research/literature_survey/13_ablation_study/statistical_analysis_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_analysis_results.json) | Detailed JSON structure containing complete test statistics, Shapiro-Wilk normality outputs, and bootstrap distributions. | Processed Statistical Output | **Authoritative Secondary Source** | Confirms non-normality across metrics, justifying non-parametric Wilcoxon tests. |
| **E-4** | [`research/literature_survey/13_ablation_study/runtime_comparisons.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/runtime_comparisons.csv) | Per-corridor median runtimes and individual repetition lists (`raw_runtimes_ms`) for all 385 cells ($R=5$ for Exp A–D, $R=3$ for Exp E). | Processed Runtime Output | **Authoritative Latency Source** | Isolated algorithmic pathfinding execution only; measured via `time.perf_counter()`; excludes network loading. |
| **E-5** | [`research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) | Per-corridor metrics for Exp A (A0, A1, A2): runtime, expanded states, distance, impedance cost, sharp turns, moderate turns, total turns. | Processed Metrics Table | **Authoritative Exp A Source** | Expanded states metric represents priority-queue pop events, not unique topological nodes. |
| **E-6** | [`research/literature_survey/13_ablation_study/exp_b_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_b_corridor_metrics.csv) | Per-corridor metrics for Exp B (B0, B1, B2): runtime, distance, impedance cost, arterial %, collector %, residential %, service %. | Processed Metrics Table | **Authoritative Exp B Source** | Road classes derived from OSM highway tags; unclassified segments fall back to neutral multiplier. |
| **E-7** | [`research/literature_survey/13_ablation_study/exp_c_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_c_corridor_metrics.csv) | Per-corridor metrics for Exp C (C0, C1, C2, C3): runtime, distance, impedance cost, sharp turns, moderate turns, total turns. | Processed Metrics Table | **Authoritative Exp C Source** | Four discrete penalty tiers evaluated ($0/0, 12/4, 25/8, 50/16$); continuous parameter space not sampled. |
| **E-8** | [`research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv) | Per-corridor metrics for Exp D (D1, D2, D3, D4): runtime, distance, impedance cost, bridge length, bridge %, roundabout length, roundabout %. | Processed Metrics Table | **Authoritative Exp D Source** | Evaluates tagged OpenStreetMap `bridge=yes` and `junction=roundabout` features. The `impedance_cost` metric is a post-hoc standardized production score evaluated outside the scoped context; search-time objective costs were not retained. |
| **E-9** | [`research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md) | Consolidated technical report containing descriptive tables (means, medians, std, IQRs), paired tests, and detailed analytical findings. | Technical Report | **Authoritative Comprehensive Report** | Incorporates all Phase 13.4 post-audit textual corrections. |
| **E-10** | [`research/literature_survey/13_ablation_study/phase_13_4_correction_and_freeze_report.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_4_correction_and_freeze_report.md) | Audit correction and freeze log. Formalizes Pareto trade-off terminology and documents corridor-level dominance breakdowns. | Governance & Audit Report | **Authoritative Governance Reference** | Confirms frozen status of the entire ablation dataset as of 2026-11-05. |
| **E-11** | [`research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png) | High-resolution ($300\text{ DPI}$) 3-panel publication figure: (a) Sharp turns, (b) Wall-clock runtime log scale, (c) Expanded states. | Visualization (PNG) | **Authoritative Publication Asset** | Verified and publication-ready. |
| **E-12** | [`research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png) | High-resolution ($300\text{ DPI}$) 2-panel publication figure: (a) Stacked road-class composition, (b) Arterial vs. residential exposure shift. | Visualization (PNG) | **Authoritative Publication Asset** | Verified and publication-ready. |
| **E-13** | [`research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png) | High-resolution ($300\text{ DPI}$) 2-panel publication figure: (a) Monotonic sharp turn reduction, (b) Distance–turn empirical Pareto curve. | Visualization (PNG) | **Authoritative Publication Asset** | Verified and publication-ready. |
| **E-14** | `bengaluru_graph.pkl` & `core/config.py` | Serialized road graph ($|V|=308,643, |E|=744,216, |E_s|=740,822$) and production impedance configuration values. | Code / Data Binary | **Authoritative Metadata Source** | Source network extracted from OpenStreetMap (2026). |
| **E-X1** | [`research/literature_survey/13_ablation_study/exp_e_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_e_corridor_metrics.csv) | Per-corridor alternative routing metrics (Offset, Raw Yen, Filtered Yen). | Processed Metrics Table | **EXCLUDED FROM PAPER 1** | Belongs exclusively to Paper 2. |
| **E-X2** | [`research/literature_survey/13_ablation_study/figures/fig4_exp_e_alternatives.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig4_exp_e_alternatives.png) | Publication Figure 4 comparing alternative route runtimes and diversity indices. | Visualization (PNG) | **EXCLUDED FROM PAPER 1** | Belongs exclusively to Paper 2. |
| **E-X3** | Phase 3 Preliminary Timing Reports | Preliminary timing benchmarks (e.g., $117.84\text{ ms}$ mean, $103.7\text{ ms}$ median, or D1 $187.62\text{ ms}$ baseline conflations). | Preliminary Reports | **SUPERSEDED** | Replaced by frozen Phase 13.4 Stage 2B dataset ($R=5$ repetitions). |

---

## 3. Task 2: Result-to-Claim Traceability Matrix (Precise Empirical Phrasing)

### 3.1 Experiment A: Turn Awareness and State-Expansion Ablation

| Comparison | Proposed Scientific Claim | Exact Numerical Evidence | Statistical Evidence | Source File & Location | Permitted Interpretation | Strictly Prohibited Claims |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A0 vs. A1** | Turn-aware search reduces sharp-turn count ($\ge 60^\circ$) by $34.1\%$ relative to turn-unaware search. | Sharp turns drop from **$32.52$ (med: $31.0$)** under A1 to **$21.44$ (med: $18.0$)** under A0 (**$-34.1\%$**, mean diff: **$-11.08$**). | Wilcoxon Pratt $W = 0.0$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$ [$-1.42, -0.59$], Hodges-Lehmann: **$-9.50$** [$-13.0, -7.0$]. | `statistical_test_results.csv#L2`<br/>`exp_a_corridor_metrics.csv` | Incorporating discrete turn penalties into state-expanded search eliminates an average of $11.08$ sharp heading deflections ($\ge 60^\circ$) per trip across the 25 corridors. | **NO CLAIMS** of accident reduction, crash rate mitigation, rider safety enhancements, cognitive ease, or calibrated comfort utilities. Do not use "maneuver suppression". |
| **A1 vs. A2** | State expansion produces zero difference in sharp-turn count when turn penalties are inactive. | **$0.00\text{ difference}$** in sharp turns ($32.52$), total turns ($40.56$), distance ($7.723\text{ km}$), and impedance ($9,325.87$) across all 25 corridors. | Zero diffs: **$25 / 25$ corridors**, Wilcoxon Pratt $W = 0.0$, $p_{\text{adj}} = 1.0000$, Cohen's $d_z = 0.0000$. | `statistical_test_results.csv#L4`<br/>`exp_a_corridor_metrics.csv` | Directed edge-state expansion produces identical sharp-turn counts to node-level search when turn penalties are nullified. | Do not claim that A1 and A2 have identical memory structures, heap operation counts, or computational footprints. |
| **A1 vs. A2** | Edge-state expansion increases median wall-clock runtime by a factor of $3.78\times$ over node-level search. | Median wall-clock runtime increases from **$40.88\text{ ms}$** (A2) to **$154.69\text{ ms}$** (A1) (**$3.78\times$ increase**, mean diff: **$+253.38\text{ ms}$**). Expanded states increase from $5,747$ to $12,136$ ($2.11\times$). | Wilcoxon Pratt $W = 0.0$, $p_{\text{adj}} < 10^{-6}$, Cohen's $d_z = +0.8115$ [$+0.40, +1.22$], Hodges-Lehmann: **$+185.10\text{ ms}$** [$+91.0, +335.5$]. | `statistical_test_results.csv#L7`<br/>`exp_a_corridor_metrics.csv` | Expanding the search space from vertices to directed edges incurs a measurable $\approx 3.8\times$ elapsed execution latency factor resulting from priority-queue size expansion. | Do not present theoretical saturation limits ($5.88\text{M}$ iterations) as measured runtime latencies. Do not describe wall-clock time as CPU time. |
| **A0 vs. A1** | Turn-penalty heading evaluations add an incremental $+13.1\%$ ($+20.24\text{ ms}$) median wall-clock runtime over state expansion without turn penalties. | Median wall-clock runtime increases from **$154.69\text{ ms}$** (A1) to **$174.93\text{ ms}$** (A0) (**$+13.1\%$ overhead**, $+20.24\text{ ms}$ median shift, mean diff: **$+41.35\text{ ms}$**). | Wilcoxon Pratt $W = 17.0$, $p_{\text{adj}} = 1.2 \times 10^{-5}$, Cohen's $d_z = +0.7947$ [$+0.38, +1.21$], Hodges-Lehmann: **$+30.43\text{ ms}$** [$+12.3, +59.5$]. | `statistical_test_results.csv#L5`<br/>`exp_a_corridor_metrics.csv` | Trigonometric azimuth difference calculations and piecewise penalty evaluations account for $+20.24\text{ ms}$ of median elapsed pathfinding latency beyond edge-state tracking. | Do not cite superseded preliminary timing figures ($117.84\text{ ms}$ or $103.7\text{ ms}$). Do not describe $+41.35\text{ ms}$ mean as "negligible" or "minimal". |

---

### 3.2 Experiment B: Road-Class Impedance Ablation

| Comparison | Proposed Scientific Claim | Exact Numerical Evidence | Statistical Evidence | Source File & Location | Permitted Interpretation | Strictly Prohibited Claims |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B0 vs. B1** | Two-wheeler hierarchy weighting reduces arterial street exposure by $51.21$ percentage points relative to neutral weighting. | Arterial street share drops from **$65.05\%$ (med: $67.4\%$)** under neutral weights to **$13.84\%$ (med: $8.6\%$)** under production B0 (**$-51.21$ percentage points**). | Wilcoxon Pratt $W = 4.0$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$ [$-2.18, -1.36$], Hodges-Lehmann: **$-54.55\%$** [$-64.03, -40.62$]. | `statistical_test_results.csv#L11`<br/>`exp_b_corridor_metrics.csv` | Applying a $1.5\times$ penalty multiplier to arterial links decreases the proportion of route distance traversing motorways, trunks, and primary roads by $51.21$ percentage points. | **NO CLAIMS** of reduced vehicle emissions, reduced collision probabilities, reduced traffic congestion, or improved travel speeds. Do not use "arterial suppression". |
| **B0 vs. B1** | Two-wheeler hierarchy weighting increases residential street exposure by $+30.73$ percentage points relative to neutral weighting. | Residential street share increases from **$13.51\%$ (med: $9.5\%$)** in B1 to **$44.24\%$ (med: $44.7\%$)** in B0 (**$+30.73$ percentage points**). | Wilcoxon Pratt $W = 9.0$, $p_{\text{adj}} = 1.5 \times 10^{-4}$, Cohen's $d_z = +1.5234$ [$+1.11, +1.94$], Hodges-Lehmann: **$+31.30\%$** [$+21.90, +41.05$]. | `statistical_test_results.csv#L14`<br/>`exp_b_corridor_metrics.csv` | Applying a $0.90\text{--}1.00\times$ multiplier shifts optimal path selection toward residential and living street classifications, increasing residential distance proportion to $44.24\%$. | Do not claim that residential roads are quieter, safer, less stressful, or preferred by riders based on unmeasured psychological criteria. Do not use "traffic diversion". |
| **B0 vs. B1** | Arterial avoidance incurs an average $+15.53\%$ ($+1.028\text{ km}$) physical distance increase relative to neutral road-class weighting. | Mean physical distance increases from **$6.620\text{ km}$** (B1) to **$7.648\text{ km}$** (B0) (**$+1.028\text{ km}$**, **$+15.53\%$ detour overhead**). | Wilcoxon Pratt $W = 7.0$, $p_{\text{adj}} = 6.8 \times 10^{-5}$, Cohen's $d_z = +0.9246$ [$+0.51, +1.34$], Hodges-Lehmann: **$+0.86\text{ km}$** [$+0.48, +1.38$]. | `statistical_test_results.csv#L17`<br/>`exp_b_corridor_metrics.csv` | Shifting routes away from direct arterial corridors requires an average of $1.028\text{ km}$ ($+15.53\%$) of additional physical travel distance across the evaluated corpus. | Do not characterize $+1.028\text{ km}$ as "modest" or "negligible". Do not describe this detour as producing "travel time savings" or lower fuel consumption. |
| **B0 vs. B2** | Impedance weighting shifts paths away from physical shortest distance baselines. | Relative to physical shortest paths (B2, $6.577\text{ km}$), B0 increases distance by **$+1.070\text{ km}$ ($+16.27\%$)**, decreases arterial share by **$-45.51\text{ pp}$**, and increases residential share by **$+24.79\text{ pp}$**. | Wilcoxon Pratt $W = 0.0$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = +0.9853$ [$+0.57, +1.40$], Hodges-Lehmann: **$+0.92\text{ km}$** [$+0.56, +1.38$]. | `statistical_test_results.csv#L12,L15,L18`<br/>`exp_b_corridor_metrics.csv` | Unweighted distance minimization concentrates $59.35\%$ of travel on arterials; two-wheeler weighting reallocates $44.24\%$ to residential streets at a $+16.27\%$ distance trade-off. | Do not claim that physical shortest paths are unsafe or illegal. |

---

### 3.3 Experiment C: Turn-Penalty Sensitivity Response

| Comparison | Proposed Scientific Claim | Exact Numerical Evidence | Statistical Evidence | Source File & Location | Permitted Interpretation | Strictly Prohibited Claims |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Monotonicity (C0–C3)** | Sharp-turn maneuvers decline monotonically across increasing penalty tiers. | Corpus-wide mean sharp turns: $C_0 = \mathbf{32.52} \to C_1 = \mathbf{24.64} \to C_2 = \mathbf{21.44} \to C_3 = \mathbf{19.80}$. Total turns: $40.56 \to 32.32 \to 29.48 \to 27.88$. | Paired comparisons vs. C2: $C_0$ ($p_{\text{adj}} = 4.5 \times 10^{-5}$), $C_1$ ($p_{\text{adj}} = 1.0 \times 10^{-4}$), $C_3$ ($p_{\text{adj}} = 1.1 \times 10^{-4}$). | `statistical_test_results.csv#L20-L25`<br/>`exp_c_corridor_metrics.csv` | Increasing the turn-penalty parameter values results in a monotonic reduction in geometric course deflections across the evaluated network. | Do not claim that higher penalties eliminate all turns or that zero turns is an achievable or desirable real-world routing goal. |
| **C0 vs. C2 (Note: Identical Contrast to A0 vs. A1)** | Baseline turn penalties ($25/8$) reduce sharp turns relative to zero penalties. | Mean sharp turns drop from **$32.52$ ($C_0$)** to **$21.44$ ($C_2$)** (mean diff: **$+11.08$** when testing $C_0 - C_2$; or **$-11.08$** when testing $C_2 - C_0$). | Wilcoxon Pratt $W = 0.0$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = +1.0066$, Hodges-Lehmann: **$+9.50\text{ turns}$**. | `statistical_test_results.csv#L20`<br/>`exp_c_corridor_metrics.csv` | Moving from zero to baseline penalties yields a simultaneous reduction in both sharp turns ($-11.08$) and physical route distance ($-75\text{ m}$) on corpus averages. | **DO NOT DUPLICATE IN TABLE II.** This is mathematically identical to $A_0$ vs. $A_1$. Do not infer unverified mechanisms ("erratic alleyway zigzags"). |
| **C1 vs. C2 (Intermediate Tier)** | Halving penalties below baseline allows an intermediate increase in sharp turns. | Moving from $C_2$ ($25/8$) to $C_1$ ($12/4$) increases mean sharp turns from **$21.44$ to $24.64$** (mean diff: **$+3.20$**). $7/25$ corridors exhibit zero difference. | Wilcoxon Pratt $W = 0.0$, $p_{\text{adj}} = 1.02 \times 10^{-4}$, Cohen's $d_z = +1.0818$ [$+0.669, +1.495$], Hodges-Lehmann: **$+3.00\text{ turns}$** [$+2.0, +4.5$]. | `statistical_test_results.csv#L21`<br/>`exp_c_corridor_metrics.csv` | Halving penalty values allows an average of $3.20$ additional sharp turns per corridor across the corpus. Relegated to supplementary archive. | Do not present $C_1$ as an optimal configuration or calibrated setting. |
| **C2 vs. C3 (Diminishing Returns)** | Escalating beyond baseline penalties produces diminishing turn reductions at the expense of route distance. | Moving from C2 ($25/8$) to C3 ($50/16$) yields an incremental reduction of **$-1.64\text{ sharp turns}$ ($-7.6\%$)** while increasing physical route distance by **$+32.3\text{ m}$ ($+19.7\text{ m}$ per turn avoided)**. | Wilcoxon Pratt $W = 0.0$, $p_{\text{adj}} = 1.1 \times 10^{-4}$, Cohen's $d_z = -1.0393$, Hodges-Lehmann: **$-1.50\text{ turns}$**. | `statistical_test_results.csv#L22`<br/>`exp_c_corridor_metrics.csv` | Further doubling penalty parameters forces detours around remaining junctions, yielding diminishing marginal turn reduction per meter of additional travel distance. | Do not claim C3 is unviable or invalid; both C2 and C3 are non-dominated on the empirical Pareto frontier. |
| **Trade-off Knee** | Baseline C2 ($25/8$) represents the empirical corpus-average trade-off knee. | C2 dominates C0 and C1 on corpus averages; both C2 and C3 are non-dominated on the empirical frontier $\mathcal{P} = \{C_2, C_3\}$. C2 captures **$87.1\%$** of maximum turn reduction while minimizing mean distance ($7.648\text{ km}$). | Non-dominated set: $\{C_2, C_3\}$. Corridor breakdown: C2 dominates C3 in 8 corridors; C3 dominates C2 in 7 corridors; 5 active trade-offs; 5 ties. | `phase_13_4_correction_and_freeze_report.md#Section-2`<br/>`exp_c_corridor_metrics.csv` | C2 represents an empirical trade-off knee on corpus averages. Individual corridor trade-offs vary depending on local street connectivity. | **MUST NOT CLAIM** that C2 is a universal mathematical optimum, universally superior across all corridors, or calibrated to rider psychology. |

---

### 3.4 Experiment D: Topological Modifiers (Bridge and Roundabout Factorial Audit)

#### 3.4.1 Configuration Matrix and Modifier Evaluation Sequence
Inspection of [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L248-L270) and [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L294-L327) confirms the configuration matrix and in-code evaluation sequence:
- **$D_1$:** Bridge Off (`"disabled"`), Roundabout Off (`1.0`)
- **$D_2$:** Bridge On (`"production"`, $0.80$ assignment), Roundabout Off (`1.0`)
- **$D_3$:** Bridge Off (`"disabled"`), Roundabout On (`0.95` multiplier)
- **$D_4$:** Bridge On (`"production"`, $0.80$ assignment), Roundabout On (`0.95` multiplier) [Production Control]

In `two_wheeler_edge_cost`, the modifiers are sequenced sequentially:
1. `bridge_mode`: If active (`"production"`) and `edge_data.get("bridge")` is valid on a main road (`motorway`, `trunk`, `primary`), `penalty = 0.80` overrides the baseline hierarchy penalty.
2. `roundabout_multiplier`: If active and `edge_data.get("junction") == "roundabout"`, `penalty *= rbt_mult` multiplies the current penalty by $0.95$.
3. Resulting edge cost: `length * penalty`. If an edge is both a bridge and a roundabout on a main road, the effective penalty is $0.80 \times 0.95 = 0.76$.

#### 3.4.2 Comprehensive Metric Classification & Execution Trace (Classes A, B, C, D)
Every metric recorded in [`exp_d_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv) and [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json) is mapped to its measurement class and exact execution point:

| Metric Name | Measurement Class | Responsible Function & Execution Location | Description & Measurement Context |
| :--- | :---: | :--- | :--- |
| **Search Objective Cost $g(\text{goal})$** | **Class A** | `two_wheeler_astar` (`routing/algorithms.py#L597`) | **NOT RETAINED.** Generated during graph search inside `scoped_ablation_context`, returned as `res["cost"]`, but dropped at `ablation_harness.py#L667`. Not saved in dataset. |
| `distance_km` | **Class B** | `calc_route_distance` (`ablation_metrics.py#L53-L63`, called at `#L337`) | Evaluates physical route distance by summing edge lengths along `res["route"]`. Divided by $1000.0$ at `#L347`. Pure physical route geometry measurement. |
| `bridge_length_m` | **Class B** | `analyze_bridge_exposure` (`ablation_metrics.py#L192-L239`, called at `#L341`) | Sums physical length of traversed edges where OpenStreetMap `bridge` tag is present along `res["route"]`. Pure physical route attribute. |
| `bridge_pct` | **Class B** | `analyze_bridge_exposure` (`ablation_metrics.py#L236`) | Percentage of physical route distance on bridge edges: `(bridge_length / denom) * 100.0`. Pure physical route attribute. |
| `roundabout_length_m` | **Class B** | `analyze_roundabout_exposure` (`ablation_metrics.py#L241-L275`, called at `#L342`) | Sums physical length of traversed edges where OpenStreetMap `junction == "roundabout"` along `res["route"]`. Pure physical route attribute. |
| `roundabout_pct` | **Class B** | `analyze_roundabout_exposure` (`ablation_metrics.py#L273`) | Percentage of physical route distance on roundabout edges: `(roundabout_length / denom) * 100.0`. Pure physical route attribute. |
| `impedance_cost` | **Class C** | `calc_post_hoc_path_cost` (`ablation_metrics.py#L278-L316`, called at `#L338`) | **Post-hoc standardized score.** Evaluated in `ablation_harness.py#L667` **outside** `scoped_ablation_context`. Evaluates `res["route"]` under fixed production penalties ($25/8$ turns, bridge $0.80$, roundabout $0.95$). |
| `runtime_ms` | **Class D** | `time.perf_counter()` (`ablation_harness.py#L664-L666`, aggregated at `#L668`) | Elapsed wall-clock search time across $R=5$ repetitions. Aggregated via within-corridor median $\tilde{T}_i$. |

#### 3.4.3 Search-Time Objective Cost Capture Verification
Inspection of [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L662-L670) confirms the exact data handling flow:
```python
with scoped_ablation_context(..., bridge_mode=b_mode, roundabout_multiplier=r_mult, ...):
    for _ in range(reps):
        t0 = time.perf_counter()
        res = two_wheeler_astar(G, s_node, e_node, graph_mgr, penalties=production_penalties, return_metrics=True)
        raw_runtimes.append(round((time.perf_counter() - t0) * 1000.0, 2))
m = extract_full_route_metrics(G, res["route"], graph_mgr, production_penalties)
```
1. **Search Objective Dropped:** `two_wheeler_astar` returns a dictionary containing `res["cost"]` representing the search-time accumulated path cost $g(\text{goal})$ evaluated under the active configuration (`b_mode`, `r_mult`). However, line 667 passes only `res["route"]` (the sequence of node IDs) into `extract_full_route_metrics` and ignores `res["cost"]`.
2. **Post-Hoc Scoring Restoration:** `extract_full_route_metrics` is invoked **outside** the `with scoped_ablation_context` block. The context manager's `__exit__` method has already restored standard production functions. Consequently, `calc_post_hoc_path_cost` recalculates cost from scratch on the returned node sequence using the **restored default production weights** (bridge active at 0.8, roundabout active at 0.95, turns at 25/8).
3. **Data Storage Audit:** Inspection of [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json) confirms that the keys stored under each Experiment D cell are:
   `['node_count', 'distance_m', 'distance_km', 'impedance_cost', 'turns', 'road_classes', 'bridge', 'roundabout', 'runtime_ms', 'raw_runtimes_ms']`.
   The search-time objective cost was **not retained** in either the JSON archive or `exp_d_corridor_metrics.csv`.
4. **Audit Mandates:**
   - The manuscript must explicitly state that `impedance_cost` in Experiment D is a post-hoc standardized production score, not the search objective.
   - The configured search-objective cost was **not retained** in the experimental dataset.
   - Authors must not reconstruct, estimate, or invent unrecorded search-objective statistics.
   - Authors must not imply that post-hoc standardized scoring is equivalent to the search-time objective.

#### 3.4.4 Reassessment of All Four Controlled Comparisons
The four factorial comparisons are audited across all six physical and computational dimensions:

| Comparison | Evaluated Factor | Route Geometry (`res["route"]`) | Physical Distance (`distance_km`) | Bridge Traversal (`bridge_length_m`) | Roundabout Traversal (`roundabout_length_m`) | Post-Hoc Standardized Impedance Cost (`impedance_cost`) | Actual Search Objective ($g(\text{goal})$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$D_1$ vs. $D_2$** | Isolated Bridge Modifier (Roundabout Off) | Changes on 2/25 corridors (OD_04, OD_15); 23/25 corridors 100% identical. | 23/25 zeros. OD_04: $-0.645\text{ km}$, OD_15: $-2.146\text{ km}$. Mean $\Delta$: $+0.1116\text{ km}$. | 23/25 zeros. OD_04: $+605.6\text{ m}$, OD_15: $+5,338.5\text{ m}$. Mean $\Delta$: $-237.76\text{ m}$. | 25/25 zeros. Invariant across all corridors (OD_06 has $62.98\text{ m}$ in both). | 23/25 zeros. OD_04: $+266.20$, OD_15: $+2,756.75$. Mean $\Delta$: $+120.92$, $p_{\text{adj}} = 0.4722$. | **Not retained.** $D_1$ searched without bridge discount; $D_2$ searched with bridge discount. |
| **$D_1$ vs. $D_3$** | Isolated Roundabout Modifier (Bridge Off) | **100% Invariant.** All 25 corridors produce identical node sequences. | **25/25 zeros.** All corridors have $0.000\text{ km}$ paired difference. | **25/25 zeros.** All corridors have $0.0\text{ m}$ paired difference. | **25/25 zeros.** All corridors have $0.0\text{ m}$ paired difference (OD_06 has $62.98\text{ m}$ in both). | **25/25 zeros.** Standardized production scoring on identical paths yields identical scores ($0.00$ diff). | **Not retained.** On OD_06, $D_3$ search discounted $62.98\text{ m}$ by $5\%$ ($\approx 3.15\text{--}4.73$ units); other 24 corridors identical. |
| **$D_2$ vs. $D_4$** | Roundabout Modifier (Bridge On Baseline) | **100% Invariant.** All 25 corridors produce identical node sequences. | **25/25 zeros.** All corridors have $0.000\text{ km}$ paired difference. | **25/25 zeros.** All corridors have $0.0\text{ m}$ paired difference. | **25/25 zeros.** All corridors have $0.0\text{ m}$ paired difference (OD_06 has $62.98\text{ m}$ in both). | **25/25 zeros.** Standardized production scoring on identical paths yields $0.00$ diff ($p_{\text{adj}} = 1.0000$). | **Not retained.** On OD_06, $D_4$ search discounted $62.98\text{ m}$ by $5\%$; other 24 corridors identical. |
| **$D_3$ vs. $D_4$** | Bridge Modifier (Roundabout On Baseline) | Changes on 2/25 corridors (OD_04, OD_15); 23/25 corridors 100% identical. | 23/25 zeros. OD_04: $+0.645\text{ km}$, OD_15: $+2.146\text{ km}$. Mean $\Delta$: $+0.1116\text{ km}$. | 23/25 zeros. OD_04: $-605.6\text{ m}$, OD_15: $-5,338.5\text{ m}$. Mean $\Delta$: $-237.76\text{ m}$. | 25/25 zeros. Invariant across all corridors (OD_06 has $62.98\text{ m}$ in both). | 23/25 zeros. OD_04: $+266.20$, OD_15: $+2,756.75$. Mean $\Delta$: $+120.92$, $p_{\text{adj}} = 0.4722$. | **Not retained.** $D_3$ searched without bridge discount; $D_4$ searched with bridge discount. |

#### 3.4.5 Metric-by-Metric Equivalence Audit: $(D_1 - D_2)$ vs. $(D_3 - D_4)$
An exhaustive comparison across all 25 corridors yields the following per-metric equivalence breakdown:

| Metric Evaluated | Mismatches in Paired Deltas | Non-Zero Differences | Mean Delta ($D_1 - D_2$) | Mean Delta ($D_3 - D_4$) | Equivalence Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Route Geometry** | **0 / 25** | 2 / 25 | Identical sequences | Identical sequences | **EXACTLY EQUIVALENT** |
| **Physical Distance (`distance_km`)** | **0 / 25** | 2 / 25 | $+0.1116\text{ km}$ | $+0.1116\text{ km}$ | **EXACTLY EQUIVALENT** |
| **Post-Hoc Cost (`impedance_cost`)** | **0 / 25** | 2 / 25 | $+120.9180$ | $+120.9180$ | **EXACTLY EQUIVALENT** |
| **Bridge Traversal (`bridge_length_m`)**| **0 / 25** | 2 / 25 | $-237.7640\text{ m}$ | $-237.7640\text{ m}$ | **EXACTLY EQUIVALENT** |
| **Roundabout Traversal (`roundabout_length_m`)**| **0 / 25** | 0 / 25 | $0.0000\text{ m}$ | $0.0000\text{ m}$ | **EXACTLY EQUIVALENT** |
| **Execution Runtime (`runtime_ms`)** | **25 / 25** | 25 / 25 | $+1.8224\text{ ms}$ | $+0.7660\text{ ms}$ | **NOT EQUIVALENT (Timing Jitter)** |

*Auditing Note:* While topological, geometric, distance, and post-hoc cost metrics are strictly equivalent between $(D_1 - D_2)$ and $(D_3 - D_4)$, the execution runtimes differ due to independent timing measurements. They must not be described as "bitwise identical" without restricting that statement to the non-timing metrics.

#### 3.4.6 Roundabout Inventory & Route Geometry Invariance (OD_06 Resolution)
Across all 25 corridors in [`exp_d_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_d_corridor_metrics.csv):
- **OD_06 (Jayanagar 4th Block to Malleshwaram):** Verified as the **sole corridor** in the entire corpus with non-zero roundabout traversal:
  - $D_1$: `roundabout_length_m = 62.98 m` ($0.51\%$), distance: $12.447\text{ km}$, post-hoc cost: $14,153.24$
  - $D_2$: `roundabout_length_m = 62.98 m` ($0.51\%$), distance: $12.447\text{ km}$, post-hoc cost: $14,153.24$
  - $D_3$: `roundabout_length_m = 62.98 m` ($0.51\%$), distance: $12.447\text{ km}$, post-hoc cost: $14,153.24$
  - $D_4$: `roundabout_length_m = 62.98 m` ($0.51\%$), distance: $12.447\text{ km}$, post-hoc cost: $14,153.24$
- **OD_12 (Frazer Town to Shivajinagar):** Verified to contain **$0.0\text{ m}$ ($0.0\%$)** roundabout infrastructure across all four configurations.
- **Corridor Geometry Invariance:** The node sequence `route` on OD_06 is 100% identical across $D_1, D_2, D_3, D_4$. The $5\%$ discount on $62.98\text{ m}$ represents $\approx 3.15\text{--}4.73$ impedance units ($\approx 0.025\%$), which does not trigger any alternate path branch in A* search.
- **Post-Hoc Scoring Explanation:** In [`ablation_harness.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/ablation_harness.py#L667), `extract_full_route_metrics` executes post-hoc scoring (`calc_post_hoc_path_cost`) using standard production scoring rules outside the scoped context. Because the node sequence is identical, the post-hoc standardized impedance cost is identical ($14,153.24$) across all four configurations.

#### 3.4.7 Grounded Empirical Interpretation of Bridge Modifier
- **Prevalence of Bridge Infrastructure in Baseline Routing:** OpenStreetMap `bridge=yes` segments are traversed on **19 of the 25 corridors** under baseline routing ($D_1$).
- **Selective Corridor Impact:** Enabling the $0.80$ bridge modifier alters route selection on only **2 of those 19 corridors** (OD_04 and OD_15). On OD_04, bridge traversal expands from $136.9\text{ m} \to 742.5\text{ m}$ (shortening route distance by $-645\text{ m}$); on OD_15, bridge traversal expands from $562.7\text{ m} \to 5,901.1\text{ m}$ (shortening route distance by $-2.15\text{ km}$).
- **Corpus Invariance:** On the other 17 corridors with existing bridge segments, and on the 6 corridors without bridges, the optimal route is completely unaffected ($23/25$ zero differences, $0.00\text{ shift}$).
- **Strictly Grounded Interpretation:** The bridge modifier does not alter paths wherever grade-separated infrastructure exists; rather, it produces route shifts only in isolated corridors where elevated links provide a substantially lower-impedance alternative that overcomes local network penalties. Across the corpus as a whole, the post-hoc standardized impedance cost shift is not statistically significant ($p_{\text{adj}} = 0.4722$). No inferences regarding travel speed, delay, congestion mitigation, or rider safety can be supported.

---

## 4. Task 3: Table and Figure Plan & Table II Specification

### 4.1 Publication Figures (All Existing, 300 DPI, Single-Column Width)
1. **Figure 1 (Experiment A):** [`research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png) (Sharp turns, wall-clock runtime log scale, expanded states). Single column ($3.5\text{ in}$ width, $\approx 2.5\text{ in}$ height). Page 4, Column 2.
2. **Figure 2 (Experiment B):** [`research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png) (Stacked road hierarchy shares, arterial vs. residential exposure shift). Single column ($3.5\text{ in}$ width, $\approx 2.1\text{ in}$ height). Page 5, Column 1.
3. **Figure 3 (Experiment C):** [`research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png) (Monotonic sharp turn reduction boxplot, distance–turn empirical Pareto curve). Single column ($3.5\text{ in}$ width, $\approx 2.1\text{ in}$ height). Page 5, Column 2.

---

### 4.2 Table II Deduplication, Metric Rectification, and Test Selection

#### 4.2.1 Deduplication Analysis:
In preliminary drafts, Table II included both:
- Test 1: $A_0$ vs. $A_1$ (Sharp Turns): baseline $(25/8)$ vs. zero $(0/0)$, mean diff $-11.08$, $p_{\text{adj}} = 4.5 \times 10^{-5}$.
- Test 9: $C_0$ vs. $C_2$ (Sharp Turns): zero $(0/0)$ vs. baseline $(25/8)$, mean diff $+11.08$, $p_{\text{adj}} = 4.5 \times 10^{-5}$.
These two tests evaluate the exact same physical configuration contrast with treatment and control inverted. Retaining both represents duplicate reporting. $C_0$ vs. $C_2$ is formally purged from Table II.

#### 4.2.2 Experiment D Metric Rectification and Disposition Decision:
1. **$D_3$ vs. $D_4$ Metric Rectification:** In [`statistical_test_results.csv#L28`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L28), the tested metric is `impedance_cost`. As established in Section 3.4.2, this is a **post-hoc standardized production score** evaluated outside the scoped context, rather than the search objective. To eliminate ambiguity with elapsed travel time or unrecorded search costs, this outcome is explicitly labeled as **Post-Hoc Standardized Impedance Cost** (Mean Diff: $+120.92$, Pratt $W = 0.0$, Holm $p_{\text{adj}} = 0.4722$, Cohen's $d_z = +0.2192$, Hodges-Lehmann: $0.00$). The disclosure that actual configured search-objective costs were not retained is strictly preserved.
2. **$D_2$ vs. $D_4$ Disposition Decision:** In `statistical_test_results.csv#L27`, the recorded test on `impedance_cost` yielded $25/25$ zero differences ($p_{\text{adj}} = 1.0000$) solely because route geometry was 100% identical ($25/25$ identical node sequences), and post-hoc standardized scoring evaluated those identical paths under the restored production formula.
   - **Approved Primary Structure (10 Primary Tests):** $D_2$ vs. $D_4$ is excluded from Table II and reported exclusively in the Section VI-D text and extended evaluation records. Complete route-geometry invariance and physical-distance invariance ($0.000\text{ km}$, $25/25$ zeros) across all 25 corridors are descriptive findings from corridor metrics. Holm-adjusted $p_{\text{adj}} = 1.000$ applies strictly to the post-hoc standardized impedance-cost comparison ($W=0.0$). Excluding this test establishes Table II at exactly 10 rows (8 significant, 2 non-significant), saving $\approx 9.5\text{ pt}$ ($\approx 0.13\text{ in}$) of vertical space and eliminating potential reader confusion between post-hoc scoring and search-time cost. (Exploratory 11-row variants were formally discarded per Research Lead directive).

#### 4.2.3 Primary 10 Tests Selected for Table II (Recommended Main-Paper Selection):
1. **$A_0$ vs. $A_1$ (Sharp Turns):** Mean diff: $-11.08$, Holm $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$, Hodges-Lehmann: $-9.50$.  
   *Inclusion Rationale:* Core claim establishing turn-aware heading deflection reduction ($\ge 60^\circ$).
2. **$A_1$ vs. $A_2$ (Sharp Turns):** Mean diff: $0.00$, Holm $p_{\text{adj}} = 1.000$, Cohen's $d_z = 0.0000$, Hodges-Lehmann: $0.00$.  
   *Inclusion Rationale:* Confirms zero difference in sharp-turn count ($\ge 60^\circ$) between edge-state expansion and node-level search when turn penalties are inactive ($25/25$ zero differences).
3. **$A_0$ vs. $A_1$ (Wall-Clock Runtime):** Mean diff: $+41.35\text{ ms}$, Holm $p_{\text{adj}} = 1.2 \times 10^{-5}$, Cohen's $d_z = +0.7947$, Hodges-Lehmann: $+30.43\text{ ms}$.  
   *Inclusion Rationale:* Isolates the arithmetic turn-penalty evaluation latency overhead.
4. **$A_1$ vs. $A_2$ (Wall-Clock Runtime):** Mean diff: $+253.38\text{ ms}$, Holm $p_{\text{adj}} < 10^{-6}$, Cohen's $d_z = +0.8115$, Hodges-Lehmann: $+185.10\text{ ms}$.  
   *Inclusion Rationale:* Confirms that edge-state expansion is the primary driver of execution runtime latency.
5. **$B_0$ vs. $B_1$ (Arterial Share):** Mean diff: $-51.21\%$, Holm $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$, Hodges-Lehmann: $-54.55\%$.  
   *Inclusion Rationale:* Core street-hierarchy result demonstrating arterial exposure reduction.
6. **$B_0$ vs. $B_1$ (Residential Share):** Mean diff: $+30.73\%$, Holm $p_{\text{adj}} = 1.5 \times 10^{-4}$, Cohen's $d_z = +1.5234$, Hodges-Lehmann: $+31.30\%$.  
   *Inclusion Rationale:* Core result quantifying reallocation of travel distance to lower-tier residential streets.
7. **$B_0$ vs. $B_1$ (Physical Distance):** Mean diff: $+1.028\text{ km}$, Holm $p_{\text{adj}} = 6.8 \times 10^{-5}$, Cohen's $d_z = +0.9246$, Hodges-Lehmann: $+0.86\text{ km}$.  
   *Inclusion Rationale:* Establishes the physical detour trade-off incurred to avoid arterial links.
8. **$B_0$ vs. $B_2$ (Arterial Share):** Mean diff: $-45.51\%$, Holm $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.5862$, Hodges-Lehmann: $-46.31\%$.  
   *Inclusion Rationale:* Contrasts production impedance against the unweighted physical shortest path baseline.
9. **$C_3$ vs. $C_2$ (Sharp Turns):** Mean diff: $-1.64$, Holm $p_{\text{adj}} = 1.1 \times 10^{-4}$, Cohen's $d_z = -1.0393$, Hodges-Lehmann: $-1.50$.  
   *Inclusion Rationale:* Demonstrates diminishing returns of aggressive turn penalties ($50/16$) relative to baseline.
10. **$D_3$ vs. $D_4$ (Post-Hoc Standardized Impedance Cost):** Mean diff: $+120.92$, Holm $p_{\text{adj}} = 0.4722$, Cohen's $d_z = +0.2192$, Hodges-Lehmann: $0.00$.  
    *Inclusion Rationale:* Direct single-factor controlled comparison of the bridge modifier under production baseline (roundabout active); evaluates post-hoc standardized cost of the alternative routes found under the bridge modifier and confirms bridge effect is corridor-specific and not statistically significant corpus-wide ($23/25$ zero diffs). Actual configured search-objective costs were not retained.

---

### 4.3 Physical Feasibility and Layout Design for Single-Column `IEEEtran` Table II

In the IEEE two-column conference format, the maximum printable column width `\columnwidth` is **$3.5\text{ inches}$** ($21.0\text{ picas}$ or **$252\text{ pt}$**).
A 6-column table displaying full confidence intervals (e.g., `Hodges-Lehmann [95% CI]`) requires $\approx 328\text{ pt}$, producing an **Overfull `\hbox` of $+76\text{ pt}$** ($1.05\text{ inches}$).

**Compilation Reality Disclosure:** Single-column compatibility is structurally planned and verified by column width calculations. However, exact physical fit cannot be proven without compiling the actual `IEEEtran` document.

#### Option 1 (Recommended Primary Main-Paper Format: 5 Columns, 10 Rows):
Removes the wide confidence interval column from the print table, reporting the Wilcoxon test statistic and Holm-adjusted $p$-value directly in the table, while stating Hodges-Lehmann median estimators in Section VI text.

```latex
\begin{table}[t]
\caption{Primary Paired Inferential Hypothesis Test Results ($N=25$ Corridors)}
\label{tab:statistical_results}
\centering
\footnotesize
\setlength{\tabcolsep}{2.2pt}
\begin{tabular}{llccc}
\hline
\textbf{Comparison} & \textbf{Outcome Metric} & \textbf{Mean Diff.} & \textbf{Wilcoxon $W$} & \textbf{Holm $p_{\mathrm{adj}}$} \\
\hline
$A_0$ vs $A_1$ & Sharp Turns ($\ge 60^\circ$) & $-11.08$ & $0.0$ & $\mathbf{4.5 \times 10^{-5}}$ \\
$A_1$ vs $A_2$ & Sharp Turns ($\ge 60^\circ$) & $0.00$ & $0.0$ & $1.000$ \\
$A_0$ vs $A_1$ & Wall-Clock Runtime [ms] & $+41.35$ & $17.0$ & $\mathbf{1.2 \times 10^{-5}}$ \\
$A_1$ vs $A_2$ & Wall-Clock Runtime [ms] & $+253.38$ & $0.0$ & $\mathbf{< 10^{-6}}$ \\
$B_0$ vs $B_1$ & Arterial Share [\%] & $-51.21$ & $4.0$ & $\mathbf{8.4 \times 10^{-5}}$ \\
$B_0$ vs $B_1$ & Residential Share [\%] & $+30.73$ & $9.0$ & $\mathbf{1.5 \times 10^{-4}}$ \\
$B_0$ vs $B_1$ & Physical Distance [km] & $+1.028$ & $7.0$ & $\mathbf{6.8 \times 10^{-5}}$ \\
$B_0$ vs $B_2$ & Arterial Share [\%] & $-45.51$ & $4.0$ & $\mathbf{8.4 \times 10^{-5}}$ \\
$C_3$ vs $C_2$ & Sharp Turns ($\ge 60^\circ$) & $-1.64$ & $0.0$ & $\mathbf{1.1 \times 10^{-4}}$ \\
$D_3$ vs $D_4$ & Post-Hoc Standardized Impedance Cost & $+120.92$ & $0.0$ & $0.4722$ \\
\hline
\multicolumn{5}{p{3.3in}}{\scriptsize \textit{Note:} Paired Wilcoxon signed-rank tests with Pratt zero-difference correction across $N=25$ independent corridors (8 significant, 2 non-significant). Bold values indicate statistical significance ($p_{\mathrm{adj}} < 0.05$). The $A_1$ vs. $A_2$ test strictly evaluates sharp-turn counts ($p_{\mathrm{adj}} = 1.000$); complete route-geometry and physical-distance invariance ($25/25$ zeros) are separate descriptive corridor-level findings. Metric label "Post-Hoc Standardized Impedance Cost" evaluates paths under restored standard production scoring; actual configured search-objective costs were not retained by the harness. Route-geometry and physical-distance invariance across all 25 corridors for the roundabout modifier ($D_2$ vs. $D_4$, $25/25$ zeros) are separate descriptive findings from corridor metrics detailed in Section~VI-D.}
\end{tabular}
\end{table}
```
*Physical dimensions:* Width $\approx 220\text{ pt} \le 252\text{ pt}$ ($3.05\text{ in}$). Vertical height $\approx 12\text{ lines} \times 9.5\text{ pt} \approx 115\text{ pt} \approx 1.60\text{ inches}$. Provisionally satisfies the allocated $2.1\text{ in}$ vertical footprint on Page 5, Column 2, subject to actual LaTeX compilation verification.

#### Option 1-Alt (Superseded 11-Row Format — Formally Discarded):
*Disposition:* Formally discarded per Research Lead directive to preserve the strict 10-row primary structure. Table II contains exactly 10 rows (8 significant, 2 non-significant). $D_2$ vs. $D_4$ is excluded from Table II and reported exclusively as an additional non-Table-II test in Section VI-D text and extended records.

#### Option 2 (Alternative Compact Main-Paper Format: 6 Columns with Point Estimators, 10 Rows):
Includes the Hodges-Lehmann point estimate (`HL Med.`) as a single numeric scalar without wide brackets:

```latex
\begin{table}[t]
\caption{Primary Paired Inferential Hypothesis Test Results ($N=25$ Corridors)}
\label{tab:statistical_results_compact}
\centering
\scriptsize
\setlength{\tabcolsep}{1.6pt}
\begin{tabular}{llcccc}
\hline
\textbf{Comp.} & \textbf{Outcome Metric} & \textbf{Mean $\Delta$} & \textbf{$W$} & \textbf{Holm $p_{\mathrm{adj}}$} & \textbf{HL Med.} \\
\hline
$A_0$ vs $A_1$ & Sharp Turns ($\ge 60^\circ$) & $-11.08$ & $0.0$ & $\mathbf{4.5 \times 10^{-5}}$ & $-9.50$ \\
$A_1$ vs $A_2$ & Sharp Turns ($\ge 60^\circ$) & $0.00$ & $0.0$ & $1.000$ & $0.00$ \\
$A_0$ vs $A_1$ & Wall-Clock Runtime [ms] & $+41.35$ & $17.0$ & $\mathbf{1.2 \times 10^{-5}}$ & $+30.43$ \\
$A_1$ vs $A_2$ & Wall-Clock Runtime [ms] & $+253.38$ & $0.0$ & $\mathbf{< 10^{-6}}$ & $+185.10$ \\
$B_0$ vs $B_1$ & Arterial Share [\%] & $-51.21$ & $4.0$ & $\mathbf{8.4 \times 10^{-5}}$ & $-54.55$ \\
$B_0$ vs $B_1$ & Residential Share [\%] & $+30.73$ & $9.0$ & $\mathbf{1.5 \times 10^{-4}}$ & $+31.30$ \\
$B_0$ vs $B_1$ & Physical Distance [km] & $+1.028$ & $7.0$ & $\mathbf{6.8 \times 10^{-5}}$ & $+0.86$ \\
$B_0$ vs $B_2$ & Arterial Share [\%] & $-45.51$ & $4.0$ & $\mathbf{8.4 \times 10^{-5}}$ & $-46.31$ \\
$C_3$ vs $C_2$ & Sharp Turns ($\ge 60^\circ$) & $-1.64$ & $0.0$ & $\mathbf{1.1 \times 10^{-4}}$ & $-1.50$ \\
$D_3$ vs $D_4$ & Post-Hoc Standardized Impedance Cost & $+120.92$ & $0.0$ & $0.4722$ & $0.00$ \\
\hline
\multicolumn{6}{p{3.3in}}{\tiny \textit{Note:} HL Med. is the Hodges-Lehmann median difference estimator. The $A_1$ vs. $A_2$ test strictly evaluates sharp-turn counts ($p_{\mathrm{adj}} = 1.000$); route-geometry and distance invariance are separate descriptive corridor-level findings. Post-Hoc Standardized Impedance Cost evaluates paths under standard production scoring; actual configured search-objective costs were not retained. Complete descriptive route invariance findings are documented in the text.}
\end{tabular}
\end{table}
```
*Physical dimensions:* Width $\approx 238\text{ pt} \le 252\text{ pt}$ ($3.30\text{ in}$). Vertical height $\approx 1.70\text{ inches}$, subject to actual LaTeX compilation verification.

---

### 4.4 Detailed Statistics Allocation Matrix

To maintain transparency while fitting within the 6-page ceiling, statistical metrics are allocated across evaluation tiers:

| Statistic / Metric Type | Main-Paper Table II | Section VI Body Text | Extended Analysis Records |
| :--- | :---: | :---: | :---: |
| Paired Comparison & Outcome Metric | **YES** | YES | YES |
| Sample Size ($N=25$) | Caption | YES | YES |
| Mean Paired Difference | **YES** | YES | YES |
| Wilcoxon Signed-Rank Stat ($W$) | **YES** | Selected | YES |
| Holm-Bonferroni Adjusted $p$ ($p_{\text{adj}}$) | **YES** | YES | YES |
| Hodges-Lehmann Median Estimate | Option 2 Only | YES | YES |
| Hodges-Lehmann 95% Confidence Interval | NO (Width Constraint) | YES | **YES** |
| Parametric Cohen's $d_z$ with 95% CI | NO (Width Constraint) | Selected | **YES** |
| Paired $t$-statistic & Raw $p$-values | NO | NO | **YES** |
| Rank-Biserial Correlation ($r_{rb}$) | NO | NO | **YES** |
| Wilcox Zero-Drop Sensitivity Statistics | NO | NO | **YES** |

---

### 4.5 Secondary Hypothesis Tests Excluded from Main-Paper Table II

Under the recommended 10-test primary table structure, 17 secondary hypothesis tests from the project's statistical evaluation battery are excluded from main-paper Table II:

1. `Family_A_Turns`: $A_0$ vs. $A_2$ (Sharp Turns, $-11.08$, $p_{\text{adj}} = 4.5 \times 10^{-5}$). *Disposition:* Redundant with $A_0$ vs. $A_1$, as $A_1$ and $A_2$ are geometrically identical ($25/25$ zero differences).
2. `Family_A_Runtime`: $A_0$ vs. $A_2$ (Runtime, $+294.73\text{ ms}$, $p_{\text{adj}} < 10^{-6}$). *Disposition:* Composite test combining state expansion and penalty calculation; individual factors are isolated in Table II ($A_1$ vs. $A_2$ and $A_0$ vs. $A_1$).
3. `Family_A_Expansions`: $A_0$ vs. $A_1$ (Expanded States, $+2,876.52$, $p_{\text{adj}} = 1.5 \times 10^{-5}$). *Disposition:* Secondary algorithmic metric; execution latency is directly captured by runtime in Table II.
4. `Family_A_Expansions`: $A_0$ vs. $A_2$ (Expanded States, $+16,396.52$, $p_{\text{adj}} < 10^{-6}$). *Disposition:* Secondary algorithmic metric; captured by composite runtime.
5. `Family_A_Expansions`: $A_1$ vs. $A_2$ (Expanded States, $+13,520.00$, $p_{\text{adj}} < 10^{-6}$). *Disposition:* Secondary algorithmic metric; captured by $A_1$ vs. $A_2$ runtime in Table II.
6. `Family_B_Arterial`: $B_1$ vs. $B_2$ (Arterial Share, $+5.70\%$, $p_{\text{adj}} = 0.0443$). *Disposition:* Contrast between two control baselines (neutral weights vs. unweighted shortest path); secondary to production comparisons.
7. `Family_B_Residential`: $B_0$ vs. $B_2$ (Residential Share, $+24.79\%$, $p_{\text{adj}} = 1.98 \times 10^{-4}$). *Disposition:* Secondary comparison against shortest distance; primary comparison against neutral weights ($B_0$ vs. $B_1$) is reported in Table II.
8. `Family_B_Residential`: $B_1$ vs. $B_2$ (Residential Share, $-5.94\%$, $p_{\text{adj}} = 0.0017$). *Disposition:* Contrast between two control baselines; secondary interest.
9. `Family_B_Distance`: $B_0$ vs. $B_2$ (Distance, $+1.070\text{ km}$, $p_{\text{adj}} = 4.5 \times 10^{-5}$). *Disposition:* Confirms detour relative to shortest path; primary detour trade-off against neutral weights ($B_0$ vs. $B_1$, $+1.028\text{ km}$) is reported in Table II.
10. `Family_B_Distance`: $B_1$ vs. $B_2$ (Distance, $+0.042\text{ km}$, $p_{\text{adj}} = 0.0004$). *Disposition:* Minor difference ($+42\text{ m}$) between neutral and shortest controls.
11. `Family_C_SharpTurns`: $C_0$ vs. $C_2$ (Sharp Turns, $+11.08$, $p_{\text{adj}} = 4.5 \times 10^{-5}$). *Disposition:* Redundant duplicate of $A_0$ vs. $A_1$ (identical data contrast with inverted treatment/control assignment).
12. `Family_C_SharpTurns`: $C_1$ vs. $C_2$ (Sharp Turns, $+3.20$, $p_{\text{adj}} = 1.02 \times 10^{-4}$). *Disposition:* Intermediate sensitivity tier ($12/4$); full sensitivity trajectory is communicated via Figure 3.
13. `Family_C_TotalTurns`: $C_0$ vs. $C_2$ (Total Turns, $+11.08$, $p_{\text{adj}} = 4.2 \times 10^{-5}$). *Disposition:* Redundant with Sharp Turns ($C_0$ vs. $C_2$) because moderate turns are invariant at $8.04$ across both configurations.
14. `Family_C_TotalTurns`: $C_1$ vs. $C_2$ (Total Turns, $+2.84$, $p_{\text{adj}} = 1.44 \times 10^{-4}$). *Disposition:* Redundant with Sharp Turns ($C_1$ vs. $C_2$).
15. `Family_C_TotalTurns`: $C_3$ vs. $C_2$ (Total Turns, $-1.60$, $p_{\text{adj}} = 1.44 \times 10^{-4}$). *Disposition:* Redundant with Sharp Turns ($C_3$ vs. $C_2$).
16. `Family_D_Cost`: $D_1$ vs. $D_4$ (Post-Hoc Standardized Impedance Cost, $+120.92$, $p_{\text{adj}} = 0.4722$). *Disposition:* Dual-factor composite comparison (both bridge and roundabout vary simultaneously); the isolated single-factor comparison ($D_3$ vs. $D_4$) is reported in Table II. Actual configured search-objective costs were not retained by the harness.
17. `Family_D_Cost`: $D_2$ vs. $D_4$ (Post-Hoc Standardized Impedance Cost, $0.00$, $p_{\text{adj}} = 1.0000$). *Disposition:* Reflects identical post-hoc standardized scoring on identical paths; complete route-geometry and physical distance invariance ($0.000\text{ km}$, $25/25$ zero differences) are descriptive findings from corridor metrics, not inferential test outcomes; thoroughly detailed in Section VI-D text.

---

## 5. Task 4: Experimental Evaluation Section Outline

### Section V: EXPERIMENTAL SETUP AND BENCHMARK METHODOLOGY (~220 words)
- **V-A. Urban Road Network Model and Evaluation Corpus:**
  - OpenStreetMap graph of Bengaluru ($|V|=308,643$ nodes, $|E|=744,216$ directed multigraph edges, $|E_s|=740,822$ effective simple links).
  - Validated $N=25$ origin–destination corridor corpus representing real-world metropolitan commuting corridors (spanning $1.35\text{ km}$ to $15.82\text{ km}$; short, medium, and long categories across diverse road topologies).
- **V-B. Benchmark Execution Protocol and Aggregation Rules:**
  - Controlled single-threaded execution environment (Python 3.13 on Windows 11 Enterprise).
  - Repetition matrix: $R=5$ independent timing repetitions per corridor and configuration ($1,750$ runs across Experiments A–D) using `time.perf_counter()` to record wall-clock elapsed execution time.
  - Aggregation: Within-corridor median $\tilde{T}_i$ recorded to suppress OS scheduling jitter; the individual OD corridor ($N=25$) serves as the independent statistical unit of analysis.
- **V-C. Non-Parametric Inferential Statistical Framework:**
  - Non-parametric paired Wilcoxon signed-rank test with Pratt zero-difference handling (due to non-normal metric distributions verified by Shapiro-Wilk).
  - Family-wise error rate controlled via Holm-Bonferroni step-down adjustment ($p_{\text{adj}}$) applied within each hypothesis family.
  - Effect sizes reported via parametric Cohen's $d_z$ with 95% confidence intervals and non-parametric Hodges-Lehmann median difference estimator with 95% confidence intervals.

---

### Section VI: EXPERIMENTAL RESULTS AND DISCUSSION (~510 words)
- **VI-A. Experiment A: Turn Awareness and State-Expansion Trade-offs (Fig. 1, ~155 words):**
  - Turn reduction: A0 eliminates an average of $11.08$ sharp turns per trip relative to A1 and A2 ($21.44$ vs. $32.52$, $-34.1\%$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$).
  - Sharp-turn inferential test ($A_1$ vs. $A_2$): State expansion with inactive turn penalties produces zero paired difference in sharp-turn counts across all corridors (mean diff: $0.00$ turns, Pratt $W = 0.0$, Holm-adjusted $p_{\text{adj}} = 1.000$, Cohen's $d_z = 0.0000$, $25/25$ zero differences).
  - Descriptive route-geometry and distance invariance ($A_1$ vs. $A_2$): As a separate descriptive finding from corridor metrics, $A_1$ and $A_2$ produce $100\%$ identical vertex sequences and physical route distances across all $25$ corridors ($25/25$ zero distance differences, $0.000\text{ km}$ diff); the inferential $p$-value applies strictly to sharp-turn counts.
  - Measured runtime latency: Across the $N=25$ corridor-level medians, $A_0$ execution runtime spans from $1.01\text{ ms}$ to $1,829.18\text{ ms}$ (mean: $382.98\text{ ms}$, sample std: $464.48\text{ ms}$, median: $174.93\text{ ms}$, $Q_1$: $68.15\text{ ms}$, $Q_3$: $507.23\text{ ms}$, $\text{IQR}$: $439.08\text{ ms}$). Latency overhead is cleanly partitioned into: (i) edge-state expansion overhead ($A_1$ vs. $A_2$, $3.78\times$ median runtime increase, $154.69\text{ ms}$ vs. $40.88\text{ ms}$, mean diff $+253.38\text{ ms}$, $p_{\text{adj}} < 10^{-6}$, $d_z = +0.8115$), and (ii) incremental turn-aware scoring overhead ($A_0$ vs. $A_1$, $+13.1\%$ median increase, $174.93\text{ ms}$ vs. $154.69\text{ ms}$, mean diff $+41.35\text{ ms}$, $p_{\text{adj}} = 1.2 \times 10^{-5}$, $d_z = +0.7947$). No universal sub-second completion is claimed across all corridors.
- **VI-B. Experiment B: Road-Class Impedance and Street-Hierarchy Allocation (Fig. 2, ~115 words):**
  - Arterial reduction: Production weights (B0) decrease arterial exposure by $51.21$ percentage points ($13.84\%$ vs. $65.05\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, $d_z = -1.7715$).
  - Residential allocation: Increases residential street share by $+30.73$ percentage points ($44.24\%$ vs. $13.51\%$, $p_{\text{adj}} = 1.5 \times 10^{-4}$, $d_z = +1.5234$).
  - Detour cost: Incurs a $+15.53\%$ ($+1.028\text{ km}$) physical distance increase over neutral shortest paths.
- **VI-C. Experiment C: Turn-Penalty Sensitivity and Empirical Trade-off Knee (Fig. 3, ~115 words):**
  - Monotonic turn reduction across penalty tiers ($0/0 \to 12/4 \to 25/8 \to 50/16$ yielding $32.52 \to 24.64 \to 21.44 \to 19.80$ sharp turns; all paired tests $p_{\text{adj}} \le 1.1 \times 10^{-4}$).
  - Simultaneous turn and distance reduction: Moving from $C_0 \to C_2$ reduces sharp turns by $11.08$ while shortening route distance by $75\text{ m}$.
  - Diminishing returns: Moving from $C_2 \to C_3$ reduces turns by only $1.64$ while adding $+32.3\text{ m}$ of detour ($+19.7\text{ m}$ per turn avoided).
  - Empirical knee designation: Baseline $C_2$ ($25/8$) is described strictly as the empirical corpus-average trade-off knee. At the corpus level, $C_2$ captures $87.1\%$ of maximum observed turn reduction ($11.08 / 12.72$ turns) at the minimum observed corpus mean distance of $7.648\text{ km}$. Moving beyond $C_2$ to $C_3$ yields diminishing returns ($1.64$ fewer turns at $+32.3\text{ m}$ detour, or $+19.7\text{ m}$ per turn). Individual corridor variation is explicitly disclosed: $C_2$ dominates $C_3$ in 8 corridors, $C_3$ dominates $C_2$ in 7 corridors, with 5 trade-offs and 5 ties; no universal Pareto optimality or universal dominance is claimed.
- **VI-D. Experiment D: Topological Modifiers (Bridge and Roundabout Effects, ~65 words):**
  - Bridge flyover discount ($D_3$ vs. $D_4$): OpenStreetMap bridges exist on 19 of 25 corridors; enabling the $0.80$ modifier alters route geometry on only 2 corridors (OD_04: $136.9 \to 742.5\text{ m}$ bridge, distance $-645\text{ m}$; OD_15: $562.7 \to 5,901.1\text{ m}$ bridge, distance $-2.15\text{ km}$), which are descriptive findings from corridor metrics. On the remaining 23 corridors, route geometries are completely unchanged ($23/25$ zeros). Holm-adjusted $p_{\text{adj}} = 0.4722$ applies strictly to the Post-Hoc Standardized Impedance Cost comparison (mean diff $+120.92$, $W=0.0$), which is not statistically significant corpus-wide.
  - Roundabout modifier invariance ($D_2$ vs. $D_4$): The roundabout modifier produced no observed route-geometry or physical-distance change across the 25 evaluated corridors ($25/25$ zero differences on both metrics), which are descriptive findings from corridor metrics. Roundabout infrastructure exists solely on OD_06 ($62.98\text{ m}$ observed traversal length). Holm-adjusted $p_{\text{adj}} = 1.000$ applies strictly to the corresponding post-hoc standardized impedance cost comparison (mean diff $0.00$, $W=0.0$). Because actual configured search-objective costs were not retained, no inference is made regarding the modifier's effect on search-objective cost.
  - Search objective disclosure: Actual configured search-objective costs were not retained by the harness; reported costs reflect post-hoc standardized production scoring evaluated outside the scoped context.
- **VI-E. Primary Inferential Hypothesis Test Summary (Table II, ~60 words):**
  - Cross-family synthesis and structured presentation of the primary inferential evaluation battery (Table II, exactly 10 tests across 6 families: 8 statistically significant, 2 non-significant), explicitly organized into distinct groups:
    - (i) Eight statistically significant primary comparisons in Table II (all yielding $p_{\text{adj}} \le 1.5 \times 10^{-4}$): $A_0$ vs. $A_1$ sharp turns, $A_1$ vs. $A_2$ wall-clock runtime, $A_0$ vs. $A_1$ wall-clock runtime, $B_0$ vs. $B_1$ arterial share, $B_0$ vs. $B_1$ residential share, $B_0$ vs. $B_1$ physical distance, $B_0$ vs. $B_2$ arterial share, and $C_3$ vs. $C_2$ sharp turns;
    - (ii) Two non-significant primary comparisons in Table II: $A_1$ vs. $A_2$ sharp-turn counts (mean diff $0.00$ turns, Pratt $W = 0.0$, Holm $p_{\text{adj}} = 1.000$, Cohen's $d_z = 0.0000$) and $D_3$ vs. $D_4$ post-hoc standardized impedance cost (mean diff $+120.92$, Pratt $W = 0.0$, Holm $p_{\text{adj}} = 0.4722$, Cohen's $d_z = +0.2192$);
    - (iii) Separate descriptive route-invariance findings: complete route-geometry and physical-distance invariance across all 25 corridors for $A_1$ vs. $A_2$ ($25/25$ identical node sequences, $0.000\text{ km}$ diff) and for $D_2$ vs. $D_4$ ($25/25$ identical node sequences, $0.000\text{ km}$ diff); and
    - (iv) Additional non-Table-II inferential result: $D_2$ vs. $D_4$ post-hoc standardized impedance cost (mean diff $0.00$, Pratt $W = 0.0$, Holm $p_{\text{adj}} = 1.000$, Cohen's $d_z = 0.0000$), reported exclusively in Section VI-D text and extended evaluation records; this inferential test is not counted among the 10 primary Table II tests, and its $p$-value applies strictly to post-hoc standardized production scoring on identical paths, not to route geometry or physical distance. Secondary exploratory analyses remain outside the scope of the primary manuscript table.

---

## 6. Task 5: Six-Page Layout and Reconciled Word Budget

### 6.1 Explicit Arithmetic Reconciliation

The frozen and proposed section allocations are reconciled strictly against the 6.0-page IEEE conference format:

```
========================================================================================
EXPLICIT WORD BUDGET ARITHMETIC RECONCILIATION
========================================================================================

1. ESTABLISHED FROZEN MANUSCRIPT COUNTS:
   - Abstract:               208 words (plus index terms = ~220 words banner)
   - Section I:              468 words
   - Section II:             349 words
   - Section III:            529 words
   - Section IV:             529 words
   -------------------------------------------------------------------------------------
   SUBTOTAL FROZEN BODY TEXT (Sections I–IV): 1,875 words

2. PROPOSED REMAINING SECTION ALLOCATIONS:
   - Section V (Experimental Setup & Methodology):        220 words
   - Section VI (Experimental Results & Discussion):       510 words
   - Section VII (Discussion, Limitations & Conclusion):   245 words
   -------------------------------------------------------------------------------------
   SUBTOTAL REMAINING BODY TEXT (Sections V–VII): 975 words

3. CUMULATIVE MANUSCRIPT COUNTS:
   Total Body Text (Sections I–VII): 1,875 + 975 = 2,850 words
   Total Manuscript Words (including 208-word Abstract): 2,850 + 208 = 3,058 words

4. NON-BODY SPACE ALLOCATION (COLUMN-EQUIVALENTS ACROSS 12 COLUMNS):
   - Title, Authors, Abstract Banner (Page 1 top across Cols 1–2): ~1.00 col equiv.
   - References (16 Audited Citations, 52 lines):                  ~0.95 col equiv. (~350 words equiv.)
   - Display Equations (6 Eqs: 3 in III, 3 in IV):                ~0.50 col equiv. (~150 words equiv.)
   - Table I (Road Multipliers, Page 2, 1.6 in):                  ~0.17 col equiv. (~60 words equiv.)
   - Figure 1 (Exp A Plot, Page 4, 2.5 in):                       ~0.27 col equiv. (~95 words equiv.)
   - Figure 2 (Exp B Plot, Page 5, 2.1 in):                       ~0.23 col equiv. (~80 words equiv.)
   - Figure 3 (Exp C Plot, Page 5, 2.1 in):                       ~0.23 col equiv. (~80 words equiv.)
   - Table II (Statistical Table, Page 5, 1.7–1.9 in):            ~0.23 col equiv. (~80 words equiv.)
   -------------------------------------------------------------------------------------
   TOTAL NON-BODY LAYOUT SPACE:                                   ~3.58 columns

5. NET BODY TEXT SPACE AVAILABLE:
   12.0 Total Columns - 3.58 Non-Body Columns = 8.42 Columns
   Estimated Column Capacity: ~330–350 words per column (subject to LaTeX compilation)
   RECONCILED BUDGET TARGET: 2,850 words (Accounts for all body words exactly once)
========================================================================================
```

---

### 6.2 Page-by-Page and Column-by-Column Allocation Matrix

Every body word is accounted for exactly once across the 12 columns of the manuscript:

| Page & Col | Section / Content Component | Body Words | Non-Body Layout Asset | Column Footprint Description |
| :---: | :--- | :---: | :--- | :--- |
| **Page 1, Col 1** | **Section I: Introduction**<br/>(Opening Context, Domain Challenges, Problem Formulation) | **220 words** | Title Block, Authors, Abstract (208 w), Index Terms (spanning Cols 1–2, $\approx 2.2\text{ in}$) | Banner occupies top portion of page; lower portion contains the first 220 words of Section I body text. |
| **Page 1, Col 2** | **Section I: Introduction** (Contributions finish, 248 w)<br/>**Section II: Related Work** (Routing baselines start, 100 w) | **348 words** | None | Sec I concludes (220 + 248 = 468 w); Sec II begins. |
| **Page 2, Col 1** | **Section II: Related Work** (Demarcation finish, 249 w)<br/>**Section III: Problem Formulation** (Graph model, 180 w) | **429 words** | None | Sec II concludes (total 349 w); Sec III begins. |
| **Page 2, Col 2** | **Section III: Problem Formulation** (Turns, Multipliers, 349 w) | **349 words** | Table I ($\approx 1.6\text{ in}$), Display Eqs. (1)–(3) | Sec III concludes (total 529 w) with Table I and 3 equations. |
| **Page 3, Col 1** | **Section IV-A:** Search Architecture (129 w)<br/>**Section IV-B:** Heuristic Formulation (90 w) | **219 words** | Display Equation (4) | Covers search graph and heuristic definition with Eq. (4). |
| **Page 3, Col 2** | **Section IV-C:** Correctness Proofs (185 w)<br/>**Section IV-D:** Complexity Analysis (125 w) | **310 words** | Display Equations (5), (6) | Sec IV concludes (total 529 w) with proof and complexity. |
| **Page 4, Col 1** | **Section V:** Experimental Setup & Protocol (220 w)<br/>**Section VI-A:** Experiment A (Turn Awareness, 100 w) | **320 words** | None | Sec V complete (220 w); Exp A results begin. |
| **Page 4, Col 2** | **Section VI-A:** Experiment A (Trade-offs & Latency, 60 w) | **60 words** | **Figure 1** (Exp A 3-panel plot, $\approx 2.5\text{ in}$) | Fig. 1 occupies top; Sec VI-A concludes (total 160 w). |
| **Page 5, Col 1** | **Section VI-B:** Experiment B (Road Classes, 120 w)<br/>**Section VI-C:** Experiment C (Sensitivity start, 60 w) | **180 words** | **Figure 2** (Exp B 2-panel plot, $\approx 2.1\text{ in}$) | Fig. 2 occupies top; Sec VI-B concludes; Exp C begins. |
| **Page 5, Col 2** | **Section VI-C:** Experiment C (Pareto Knee, 60 w)<br/>**Section VI-D:** Experiment D (Modifiers, 70 w)<br/>**Section VI-E:** Statistical Summary (40 w) | **170 words** | **Figure 3** ($\approx 2.1\text{ in}$), **Table II** ($\approx 1.7\text{--}1.9\text{ in}$) | Fig. 3 and Table II embedded; Sec VI concludes (total 510 w). |
| **Page 6, Col 1** | **Section VII:** Discussion, Limitations, and Conclusion | **245 words** | None ($\approx 0.45\text{ col}$ vertical buffer) | Sec VII terminates cleanly, providing vertical buffer headroom. |
| **Page 6, Col 2** | **References** (16 Audited Citations in standard IEEE format) | **0 words** | 16 BibTeX entries ($\approx 52\text{ lines}$) | References fill Column 12 completely. |
| **TOTALS** | **12 Columns across 6 Pages** | **2,850 words** | **3 Figs, 2 Tables, 6 Eqs, Banner, Refs** | **All 2,850 body words accounted for exactly once.** |

---

### 6.3 Compilation Feasibility and Trimming Protocol
- **Compilation Reality Disclosure & Physical Fit Qualification:** All page and column positions, line heights, and layout footprints reported herein are provisional structural estimates based on column arithmetic. Definitive physical fit cannot be claimed without compiling the actual `IEEEtran` LaTeX manuscript, as typographic glue, float placement queues, widow/orphan penalties, equation padding, and BibTeX entry line breaks govern final compiled height. Full compilation and typographic verification is established as a mandatory validation step prior to final manuscript freeze.
- **Safety Margin:** By allocating only $245\text{ words}$ to Section VII on Page 6, Column 1, the manuscript establishes $\approx 0.40\text{ column}$ of vertical buffer headroom on Page 6, ensuring that any slight overflow from Pages 4–5 will be absorbed without spilling onto Page 7.
- **Pre-Ranked Trimming Protocol:** If initial compilation overflows Page 6, text will be shortened strictly in accordance with the frozen trimming sequence from [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md):
  1. Condense Section II related work speedup background ($-50\text{ words}$).
  2. Condense Section VII future work discussion ($-40\text{ words}$).
  3. Inline Equation (1) and Equation (4) into body text ($-40\text{ words equiv.}$).

---

## 7. Task 6: Rigorous Integrity and Scope Audit

This audit explicitly cross-checks the blueprint against all project governance rules:

1. **Zero Experiment E Contamination:**
   - No data from `exp_e_corridor_metrics.csv` or `fig4_exp_e_alternatives.png` is included.
   - No mention of Perpendicular Offset alternative routing, candidate pruning ratios, pairwise Jaccard diversity, or Yen's $K$-SP runtimes.
   - Status: **VERIFIED 100% EXCLUDED**.
2. **Timing Artifact Purging and Baseline Verification:**
   - A0 baseline runtime is strictly established as **median $174.93\text{ ms}$** (mean $382.98\text{ ms}$, IQR $439.08\text{ ms}$) from `exp_a_corridor_metrics.csv` and Table 2.2 of the full ablation report.
   - The $187.62\text{ ms}$ figure is correctly identified as belonging exclusively to **Experiment D Cell D1** (Bridge Off, Roundabout Off) and is **NOT** applied to A0.
   - Preliminary timing artifacts ($117.84\text{ ms}$ mean, $103.7\text{ ms}$ median) from superseded exploratory runs are **completely excluded**.
   - Status: **VERIFIED CORRECT**.
3. **Statistical Integrity & Unit of Analysis:**
   - The individual OD corridor ($N=25$) is strictly maintained as the statistical unit of analysis.
   - $R=5$ timing repetitions per cell are aggregated via median selection ($\tilde{T}_i$) before paired hypothesis testing, preventing pseudoreplication.
   - Status: **VERIFIED COMPLIANT**.
4. **Demarcation of Theory vs. Experiment:**
   - Theoretical saturation limits derived in Section IV ($5,886,792$ iterations and $3,877,450$ logical entries) are strictly separated from empirical query performance ($119$–$129,619$ queue pops; $174.93\text{ ms}$ median latency).
   - Status: **VERIFIED COMPLIANT**.
5. **Construct Validity Guardrails & Neutral Tone:**
   - No claims of rider safety improvements, accident rate reductions, congestion mitigation, dynamic travel-time prediction, or calibrated psychological utility models appear in this blueprint.
   - Subjective language ("maneuver suppression", "diversion", "proves", "incentivizes") is completely purged.
   - Status: **VERIFIED ZERO OVER-CLAIMS & STRICT SCIENTIFIC NEUTRALITY**.

---

## 8. Status & Stop Condition Compliance

- **Current Status:** **AUDITED EXPERIMENTAL EVIDENCE BLUEPRINT (v1.6 Audited)**
- **Phase 8.3-A6 Audit Findings:**
  1. Exact modifier implementation and execution order verified from codebase (`routing/algorithms.py#L294-L327`).
  2. Roundabout inventory confirmed: OD_06 is the sole corridor with roundabouts ($62.98\text{ m}$); OD_12 is verified to have $0.0\text{ m}$.
  3. Comprehensive metric classification established across Classes A, B, C, D with explicit responsible functions and execution traces.
  4. Search-time objective capture verified: $g(\text{goal})$ (`res["cost"]`) was dropped by `ablation_harness.py#L667` outside scoped context and not retained in CSV/JSON outputs. No unrecorded search-objective costs are claimed or reconstructed.
  5. Metric distinction enforced: `impedance_cost` in Experiment D is explicitly designated as a post-hoc standardized production score, not the search-time objective.
  6. All four Experiment D controlled comparisons ($D_1$–$D_2$, $D_1$–$D_3$, $D_2$–$D_4$, $D_3$–$D_4$) audited across all six physical and computational dimensions.
  7. Table II rectified: $D_3$ vs. $D_4$ labeled accurately as Post-Hoc Standardized Impedance Cost ($+120.92$, $p_{\text{adj}} = 0.4722$); $D_2$ vs. $D_4$ moved to Section VI-D text and Supplementary Archive in recommended 10-test primary table (with complete descriptive route invariance findings).
  8. Frozen manuscript sections preserved byte-for-byte with verified SHA-256 hashes.
- **Next Action for Research Lead:**
  - Review and approve the Phase 8.3-A6 Audited Evidence Blueprint.
  - Authorize progression to **Phase 8.3-B: Section V (Experimental Setup & Methodology) Manuscript Prose Drafting**.

---

### Stop Condition Compliance:
This phase is planning, data verification, and evidence mapping only. No manuscript prose was drafted, no experimental datasets or CSVs were modified, no new figures were generated, frozen sections and freeze logs were preserved byte-for-byte, and the full manuscript was not assembled. Standing by for Research Lead review.
