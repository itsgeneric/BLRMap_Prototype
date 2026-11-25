# Paper 1 Final Visual and Tabular Inventory

**Document:** [`paper1_final_visual_inventory.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_visual_inventory.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format)  
**Parent Audits:** [`paper1_figure_table_plan.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_figure_table_plan.md), [`paper1_blueprint_feasibility_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_blueprint_feasibility_audit.md), [`paper1_revised_six_page_budget.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_revised_six_page_budget.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE MINIMAL VISUAL SET**

---

## 1. Minimal Non-Redundant Visual Inventory

To prevent information duplication and ensure that the manuscript fits strictly within the 6.0-page budget, the visual inventory is streamlined to **exactly 3 figures and 2 tables**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FINAL VISUAL & TABULAR ASSET PORTFOLIO                          │
├─────────┬──────────────────────────────────────────┬───────────┬───────────────────────┤
│ Asset   │ Descriptive Title                        │ Placement │ Evidence Source       │
├─────────┼──────────────────────────────────────────┼───────────┼───────────────────────┤
│ Fig. 1  │ Algorithmic Trade-offs of Turn Awareness │ Sec. VI-A │ fig1_exp_a_tradeoffs  │
│ Fig. 2  │ Road-Class Exposure Under Impedance      │ Sec. VI-B │ fig2_exp_b_road_class │
│ Fig. 3  │ Turn Sensitivity & Empirical Pareto Knee │ Sec. VI-C │ fig3_exp_c_sensitiv   │
│ Table I │ Road-Class Multipliers & Flyover Factors │ Sec. III-B│ core/config.py        │
│ Table II│ Paired Statistical Hypothesis Results    │ Sec. VI-E │ statistical_test_res  │
└─────────┴──────────────────────────────────────────┴───────────┴───────────────────────┘
```

---

## 2. Itemized Specifications of Approved Assets

### 2.1 Figure 1: Algorithmic Trade-offs of Turn Awareness (Exp A)
- **Source:** [`research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png)
- **Section Placement:** Section VI-A, Page 4, Column 2.
- **Dimensions:** Width $3.5\text{ in}$ (Single Column), Height $2.5\text{ in}$.
- **Approved Caption:**  
  > *Fig. 1. Algorithmic trade-offs of turn awareness and state-space expansion (Experiment A, $N=25$ corridors): (a) Sharp turn maneuvers ($\ge 60^\circ$); (b) CPU execution runtime in milliseconds (log-scale); (c) Expanded search states. Turn-aware routing (A0) suppresses sharp turns by 34.1% relative to turn-unaware routing (A1) at a 4.28x median runtime overhead over standard node-level search (A2).*
- **Justification:** Essential visual proof that state-expanded turn penalties eliminate $11.08$ sharp turns per trip, while disentangling the $3.78\times$ expansion overhead from the $1.13\times$ turn evaluation overhead.

---

### 2.2 Figure 2: Road-Class Exposure Under Two-Wheeler Impedance (Exp B)
- **Source:** [`research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png)
- **Section Placement:** Section VI-B, Page 5, Column 1.
- **Dimensions:** Width $3.5\text{ in}$ (Single Column), Height $2.1\text{ in}$.
- **Approved Caption:**  
  > *Fig. 2. Metropolitan road-class exposure under two-wheeler road impedance weighting (Experiment B, $N=25$ corridors). Production weighting (B0) suppresses high-speed arterial exposure by 51.21 percentage points (13.84% vs 65.05%) while channeling travel onto lower-stress residential streets (+30.73 percentage points) relative to distance-neutral routing (B1).*
- **Justification:** Clearly depicts the inverted road hierarchy channelization without requiring lengthy descriptive text.

---

### 2.3 Figure 3: Turn-Penalty Sensitivity Response and Empirical Pareto Knee (Exp C)
- **Source:** [`research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png)
- **Section Placement:** Section VI-C, Page 5, Column 2.
- **Dimensions:** Width $3.5\text{ in}$ (Single Column), Height $2.1\text{ in}$.
- **Approved Caption:**  
  > *Fig. 3. Turn-penalty sensitivity response across penalty tiers $C_0$ ($0/0$) to $C_3$ ($50/16$) ($N=25$ corridors): (a) Monotonic reduction in sharp maneuvers; (b) Empirical distance–turn Pareto trade-off curve. Baseline $C_2$ ($25/8$) forms the empirical corpus-average trade-off knee, capturing 87.1% of maximum turn reduction while minimizing mean physical route distance (7.648 km).*
- **Justification:** Critical evidence demonstrating the non-dominated Pareto frontier $\{C_2, C_3\}$ and justifying the production baseline setting $C_2$ ($25/8$).

---

### 2.4 Table I: Road-Class Impedance Multipliers and Flyover Override Factors
- **Source:** [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) and [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py).
- **Section Placement:** Section III-B, Page 2, Column 1.
- **Dimensions:** Width $3.5\text{ in}$ (Single Column), Height $1.6\text{ in}$ (6 compact rows).
- **Approved Content:**

| Road Hierarchy Class | OSM Highway Key (`hw`) | Base Penalty | Two-Wheeler Operational Rationale |
| :--- | :--- | :---: | :--- |
| **Arterial / Express** | `motorway`, `trunk`, `primary` | $2.2\text{--}4.0$ | Heavy mixed traffic, high collision risk |
| **Secondary Arterial** | `secondary`, `tertiary` | $1.15\text{--}1.5$ | Intermediate traffic density and speed |
| **Residential / Living** | `residential`, `living_street` | $0.95\text{--}1.0$ | Low vehicular speeds, high rider suitability |
| **Service Alley** | `service` | $0.90$ | High permeability, narrow access |
| **Arterial Flyover** | `bridge=yes` & `hw in MAIN_ROAD` | **$0.80$** (Override) | Grade-separated, signal-free bypass |
| **Roundabout / Default**| `junction=roundabout` / fallback | $0.95\times$ / $1.0$ | Continuous flow / neutral fallback |

---

### 2.5 Table II: Paired Inferential Statistical Hypothesis Test Results
- **Source:** [`research/literature_survey/13_ablation_study/statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv).
- **Section Placement:** Section VI-E, Page 5, Column 2.
- **Dimensions:** Width $3.5\text{ in}$ (Single Column), Height $2.1\text{ in}$ (7 rows $\times$ 8 columns).
- **Approved Content:**

| Comparison | Target Metric | Mean Diff | Wilcoxon $W$ | Holm $p_{\text{adj}}$ | Cohen's $d_z$ [95% CI] | Hodges-Lehmann [95% CI] | Significant? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$A_0$ vs $A_1$** | Sharp Turns | $-11.08$ | $0.0$ | **$4.5 \times 10^{-5}$** | $-1.0066$ [$-1.42, -0.59$] | $-9.50$ [$-13.0, -7.0$] | **YES** |
| **$A_0$ vs $A_2$** | Sharp Turns | $-11.08$ | $0.0$ | **$4.5 \times 10^{-5}$** | $-1.0066$ [$-1.42, -0.59$] | $-9.50$ [$-13.0, -7.0$] | **YES** |
| **$A_0$ vs $A_1$** | Runtime [ms] | $+41.35$ | $17.0$ | **$1.2 \times 10^{-5}$** | $+0.7947$ [$+0.38, +1.21$] | $+30.43$ [$+12.3, +59.5$] | **YES** |
| **$A_1$ vs $A_2$** | Runtime [ms] | $+253.38$ | $0.0$ | **$< 10^{-6}$** | $+0.8115$ [$+0.40, +1.22$] | $+185.10$ [$+91.0, +335.5$] | **YES** |
| **$B_0$ vs $B_1$** | Arterial Share %| $-51.21$ | $0.0$ | **$8.4 \times 10^{-5}$** | $-1.7715$ [$-2.33, -1.21$] | $-50.21$ [$-61.3, -39.1$] | **YES** |
| **$B_0$ vs $B_1$** | Residential % | $+30.73$ | $1.0$ | **$0.00015$** | $+1.5234$ [$+1.01, +2.04$] | $+29.45$ [$+21.2, +38.6$] | **YES** |
| **$D_4$ vs $D_1$** | Bridge Traversal | $+237.76\text{ m}$| $0.0$ | **$0.0019$** | $+0.7420$ [$+0.33, +1.15$] | $+124.50$ [$+45.0, +420.0$] | **YES** |

---

## 3. Deliberately Omitted Assets and Consolidation Rationale

1. **Omission of Algorithm 1 Float Box:**  
   - *Rationale:* Eliminating the 28-line pseudo-code box saves $280\text{ pt}$ ($0.45\text{ column}$). The state transition equations $s = (u, v) \to s' = (v, w)$, cost formulation $c(s, s') = \ell \cdot \mu + P_{\text{turn}}$, and heuristic function $h(s) = 0.80 \cdot D_{\text{haversine}}$ already specify the algorithm with complete mathematical precision in Section IV.
2. **Omission of Phase 4.1 Table II (Ablation Matrix):**  
   - *Rationale:* Table II duplicated information present in Section V text and Table II (Statistical Results). Merging its condition definitions ($A_0\text{--}A_2, B_0\text{--}B_2, C_0\text{--}C_3, D_1\text{--}D_4$) directly into Section V text saves $160\text{ pt}$ ($0.25\text{ column}$).
3. **Exclusion of Figure 4 (Alternative Routing):**  
   - *Rationale:* Figure 4 reports Perpendicular Offset and Yen's $K$-SP alternative routing metrics, which belong strictly to **Paper 2**.

---

*Visual inventory finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
