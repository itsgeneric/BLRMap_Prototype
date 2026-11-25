# Paper 1 Figure and Table Plan

**Document:** [`paper1_figure_table_plan.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_figure_table_plan.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE VISUAL AND TABULAR SPECIFICATION**

---

## 1. Inventory of Selected Publication Figures

All selected figures exist in high-resolution ($300\text{ DPI}$) PNG format within [`research/literature_survey/13_ablation_study/figures/`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/). Zero new figures are required.

### Figure 1: Algorithmic Trade-offs of Turn Awareness and State Expansion
- **Source File:** [`research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png)
- **Section Placement:** Section VI-A (Results: Experiment A), Page 4, Column 2.
- **Physical Sizing:** Single Column Width ($3.5\text{ in}$), Height $\approx 2.6\text{ in}$.
- **Proposed IEEE Caption:**  
  > *Fig. 1. Algorithmic trade-offs of turn awareness and state-space expansion (Experiment A, $N=25$ corridors): (a) Sharp turn maneuvers ($\ge 60^\circ$); (b) CPU execution runtime in milliseconds (log-scale); (c) Expanded search states. Turn-aware routing (A0) suppresses sharp turns by 34.1% relative to turn-unaware routing (A1) at a 4.28x median runtime overhead over standard node-level search (A2).*
- **Scientific Takeaway:** Visually demonstrates that tracking arriving edges eliminates $11.08$ sharp turns per trip, while disentangling the $3.78\times$ runtime overhead of state expansion from the modest $1.13\times$ overhead of trigonometric heading evaluations.
- **Modification Status:** **Use As-Is**. Frozen, verified, and 300 DPI publication-ready.

---

### Figure 2: Road-Class Exposure Under Two-Wheeler Impedance
- **Source File:** [`research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png)
- **Section Placement:** Section VI-B (Results: Experiment B), Page 5, Column 1.
- **Physical Sizing:** Single Column Width ($3.5\text{ in}$), Height $\approx 2.2\text{ in}$.
- **Proposed IEEE Caption:**  
  > *Fig. 2. Metropolitan road-class exposure under two-wheeler road impedance weighting (Experiment B, $N=25$ corridors). Production weighting (B0) suppresses high-speed arterial exposure by 51.21 percentage points (13.84% vs 65.05%) while channeling travel onto lower-stress residential streets (+30.73 percentage points) relative to distance-neutral routing (B1).*
- **Scientific Takeaway:** Provides clear, empirical evidence of inverted hierarchy channelization: motorcycles are safely diverted from dangerous, multi-lane arterials onto lower-stress inner-city corridors at a minor $+15.53\%$ detour penalty.
- **Modification Status:** **Use As-Is**. Frozen, verified, and 300 DPI publication-ready.

---

### Figure 3: Turn-Penalty Sensitivity Response and Empirical Pareto Knee
- **Source File:** [`research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png)
- **Section Placement:** Section VI-C (Results: Experiment C), Page 5, Column 2.
- **Physical Sizing:** Single Column Width ($3.5\text{ in}$), Height $\approx 2.2\text{ in}$.
- **Proposed IEEE Caption:**  
  > *Fig. 3. Turn-penalty sensitivity response across penalty tiers $C_0$ ($0/0$) to $C_3$ ($50/16$) ($N=25$ corridors): (a) Monotonic reduction in sharp maneuvers; (b) Empirical distance–turn Pareto trade-off curve. Baseline $C_2$ ($25/8$) forms the empirical corpus-average trade-off knee, capturing 87.1% of maximum turn reduction while minimizing mean physical route distance (7.648 km).*
- **Scientific Takeaway:** Shows strict monotonic reduction in turn maneuvers as penalties scale, proving that baseline $C_2$ ($25/8$) anchors the non-dominated Pareto knee before diminishing returns set in at $C_3$.
- **Modification Status:** **Use As-Is**. Frozen, verified, and 300 DPI publication-ready.

---

## 2. Inventory of Publication Tables

### Table I: Two-Wheeler Road-Class Impedance and Modifier Specifications
- **Data Source:** [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) and [`routing/algorithms.py#L266-L348`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L266-L348).
- **Section Placement:** Section III-B (Impedance Model), Page 2, Column 1.
- **Physical Sizing:** Single Column Width ($3.5\text{ in}$), Height $\approx 1.8\text{ in}$.
- **Proposed Table Content:**

| Road Hierarchy Class | OSM Highway Tag (`hw`) | Base Penalty Multiplier | Operational Rationale |
| :--- | :--- | :---: | :--- |
| **Arterial / Express** | `motorway`, `trunk`, `primary` | $2.2\text{--}4.0$ | Heavy mixed traffic, high collision risk |
| **Secondary Arterial** | `secondary`, `tertiary` | $1.15\text{--}1.5$ | Moderate traffic flow, intermediate suitability |
| **Local / Residential** | `residential`, `living_street` | $0.95\text{--}1.0$ | Low vehicular speeds, high rider suitability |
| **Narrow Service** | `service` | $0.90$ | High two-wheeler agility and permeability |
| **Arterial Flyover** | `bridge=yes` & `hw in MAIN_ROAD` | **$0.80$** (Override) | Grade-separated, signal-free corridor bypass |
| **Roundabout** | `junction=roundabout` | **$0.95\times$** (Multiplier) | Continuous circular vehicular flow |
| **Default Fallback** | Unclassified / Missing Tag | $1.00$ | Neutral fallback baseline |

---

### Table II: Controlled Factorial Ablation Experimental Design
- **Data Source:** [`research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md#Table-1.1`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/phase_13_1_stage_2B_full_ablation_report.md#Table-1.1).
- **Section Placement:** Section V-C (Ablation Matrix), Page 4, Column 1.
- **Physical Sizing:** Single Column Width ($3.5\text{ in}$), Height $\approx 2.0\text{ in}$.
- **Proposed Table Content:**

| Experiment ID | Focus Domain | Evaluated Conditions | Sample Size | Primary Target Metrics |
| :---: | :--- | :--- | :---: | :--- |
| **Exp A** | Turn Awareness & State Expansion | $A_0$ (Turn-Aware Control), $A_1$ ($P_{\text{turn}}=0$), $A_2$ (Node-Level) | $N=25, R=5$ | Sharp turns, CPU runtime, expanded states |
| **Exp B** | Road-Class Impedance Weighting | $B_0$ (Two-Wheeler), $B_1$ (Neutral $1.0\times$), $B_2$ (Aggressive Arterial) | $N=25, R=5$ | Arterial %, Residential %, Detour distance |
| **Exp C** | Turn-Penalty Sensitivity Response | $C_0$ ($0/0$), $C_1$ ($12/4$), $C_2$ ($25/8$), $C_3$ ($50/16$) | $N=25, R=5$ | Sharp turns, route distance, Pareto knee |
| **Exp D** | Grade-Separated Infrastructure | $D_1$ (Off/Off), $D_2$ (Bridge On), $D_3$ (Rbt On), $D_4$ (Control) | $N=25, R=5$ | Bridge traversal length, distance change |

---

### Table III: Paired Inferential Statistical Hypothesis Test Results
- **Data Source:** [`research/literature_survey/13_ablation_study/statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv).
- **Section Placement:** Section VI (Results Summary), Page 5, Column 2.
- **Physical Sizing:** Single Column Width ($3.5\text{ in}$), Height $\approx 2.2\text{ in}$.
- **Proposed Table Content:**

| Family & Pair | Target Metric | Mean Diff | Wilcoxon Pratt $W$ | Holm $p_{\text{adj}}$ | Cohen's $d_z$ [95% CI] | Hodges-Lehmann [95% CI] | Significant? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$A_0$ vs $A_1$** | Sharp Turns | $-11.08$ | $0.0$ | **$4.5 \times 10^{-5}$** | $-1.0066$ [$-1.42, -0.59$] | $-9.50$ [$-13.0, -7.0$] | **YES** |
| **$A_0$ vs $A_2$** | Sharp Turns | $-11.08$ | $0.0$ | **$4.5 \times 10^{-5}$** | $-1.0066$ [$-1.42, -0.59$] | $-9.50$ [$-13.0, -7.0$] | **YES** |
| **$A_0$ vs $A_1$** | Runtime [ms] | $+41.35$ | $17.0$ | **$1.2 \times 10^{-5}$** | $+0.7947$ [$+0.38, +1.21$] | $+30.43$ [$+12.3, +59.5$] | **YES** |
| **$A_1$ vs $A_2$** | Runtime [ms] | $+253.38$ | $0.0$ | **$< 10^{-6}$** | $+0.8115$ [$+0.40, +1.22$] | $+185.10$ [$+91.0, +335.5$] | **YES** |
| **$B_0$ vs $B_1$** | Arterial Share %| $-51.21$ | $0.0$ | **$8.4 \times 10^{-5}$** | $-1.7715$ [$-2.33, -1.21$] | $-50.21$ [$-61.3, -39.1$] | **YES** |
| **$B_0$ vs $B_1$** | Residential % | $+30.73$ | $1.0$ | **$0.00015$** | $+1.5234$ [$+1.01, +2.04$] | $+29.45$ [$+21.2, +38.6$] | **YES** |
| **$D_4$ vs $D_1$** | Bridge Traversal | $+237.76\text{ m}$| $0.0$ | **$0.0019$** | $+0.7420$ [$+0.33, +1.15$] | $+124.50$ [$+45.0, +420.0$] | **YES** |

---

## 3. Strict Boundary: Exclusion of Figure 4 (Reserved for Paper 2)

- **Excluded Asset:** [`research/literature_survey/13_ablation_study/figures/fig4_exp_e_alternatives.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig4_exp_e_alternatives.png) (Experiment E: Perpendicular Offset vs. Raw Yen vs. Filtered Yen).
- **Justification for Exclusion:**  
  Figure 4 reports alternative-route generation metrics (pairwise Jaccard diversity, candidate pruning, and $K$-shortest-path runtimes). In strict accordance with [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), alternative routing is the core contribution of **Paper 2**. Including Figure 4 in Paper 1 would blur publication boundaries and violate research scope partitioning.

---

*Plan verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
