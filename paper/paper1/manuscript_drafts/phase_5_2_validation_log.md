# Phase 5.2 — Abstract Validation Log

**Document:** [`phase_5_2_validation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_2_validation_log.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE PHASE 5.2 LOG (UPDATED)**

---

## 1. Summary of Checks Performed

| Category | Target / Artifact Inspected | Tool / Verification Method | Result |
| :--- | :--- | :--- | :---: |
| **Network Scale** | [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) | Programmatic NetworkX audit of graph binary | $|V| = 308,643$, $|E| = 744,216$ directed edges (`MultiDiGraph`). Exact match. |
| **Corridor Sample** | [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json) | Programmatic JSON inspection (`total_corridors`) | Exactly 25 validated OD pairs. Exact match. |
| **Turn Metrics (A0 vs. A1)** | [`statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv)<br/>[`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) | Paired comparison verification | A0 mean $= 21.44$, A1 mean $= 32.52$, Diff $= -11.08$ ($-34.07\% \approx -34.1\%$), Pratt $W = 0.0$, $p_{\text{adj}} = 4.5\times 10^{-5}$, $d_z = -1.0066$. Exact match. |
| **Arterial Exposure (B0 vs. B1)** | [`statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv)<br/>[`exp_b_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_b_corridor_metrics.csv) | Paired comparison verification | B0 mean $= 13.84\%$, B1 mean $= 65.05\%$, Diff $= -51.21\text{ pp}$, Pratt $W = 4.0$, $p_{\text{adj}} = 8.4\times 10^{-5}$, $d_z = -1.7715$. Exact match. |
| **Physical Distance (B0 vs. B1)** | [`statistical_test_results.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv)<br/>[`exp_b_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_b_corridor_metrics.csv) | Paired comparison verification | B0 mean $= 7.6475\text{ km}$, B1 mean $= 6.6196\text{ km}$, Diff $= +1.0279\text{ km}$ ($+15.5287\% \approx +15.53\%$). Pratt $W = 7.0$, $p_{\text{adj}} = 6.8\times 10^{-5}$, $d_z = +0.9246$. Exact match. |
| **Implementation Structure** | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) | Code inspection of lines 510–690 | State tuple `(prev_node, curr_node)`, turn penalties evaluated during edge relaxation, flyover override `penalty = 0.8` on `MAIN_ROAD_TYPES`. |
| **Configuration Values** | [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) | Parameter lookup in lines 50–85 | Multipliers $0.90\text{--}4.0$. Floor multiplier $\min \mu(e) = 0.80$. |
| **Literature Alignment** | Master Bibliography | Full-text verification of Winter (2002), Luxen & Vetter (2011), Fadilah et al. (2024), Hart et al. (1968) | All citations directly support attributed statements; zero ungrounded safety/travel-time claims. |

---

## 2. Discrepancies Reconciled and Directed Text Adjustments

### 2.1. Baseline for 15.53% Route-Distance Increase
- **Finding:** Inspection of `exp_b_corridor_metrics.csv` confirms:
  - B0 vs. B1 (Neutral Road-Class): $(7.6475 - 6.6196) / 6.6196 = \mathbf{+15.53\%}$ ($+1.028\text{ km}$).
  - B0 vs. B2 (Physical Shortest Path): $(7.6475 - 6.5774) / 6.5774 = \mathbf{+16.27\%}$ ($+1.070\text{ km}$).
- **Resolution:** The $+15.53\%$ figure is unequivocally relative to Condition B1. Explicit values `(7.65 vs. 6.62 km)` are reported to prevent baseline ambiguity.

### 2.2. Intermediate Log Typo in Phase 3.4 Notes
- **Finding:** In `phase_3_4_correction_log.md` and `paper1_claims_and_citations_checklist.md`, the values $d_z = +1.4883$ and $p_{\text{adj}} = 8.4\times 10^{-5}$ had been erroneously noted for the distance metric.
- **Reconciliation:** The ground truth in `statistical_test_results.csv` confirms:
  - $p_{\text{adj}} = 8.4\times 10^{-5}$ and $d_z = -1.7715$ belong strictly to `Family_B_Arterial`.
  - For `Family_B_Distance`, the true values are Holm-adjusted $p_{\text{adj}} = 6.8\times 10^{-5}$ and paired Cohen's $d_z = +0.9246$ [$95\%\text{ CI: } +0.5118, +1.3374$].

### 2.3. Research Lead Directives Incorporated (Post-Audit):
1. **Replacement 1:** Replaced *"vehicle-specific road preferences"* with *"vehicle-specific road impedance"*. Purges behavioral assumptions and enforces exact engineering terminology.
2. **Replacement 2:** Replaced *"Road segments are assigned class-dependent impedance weights, with an additional modifier for grade-separated flyovers."* with *"Road segments are assigned class-dependent impedance weights, with a 0.80 override for qualifying grade-separated main-road segments."* Accurately reflects both the numerical value ($0.80$), assignment override behavior, and road-type restriction (`MAIN_ROAD_TYPES`).
3. **Replacement 3:** Replaced premise with *"When composite edge multipliers satisfy $\mu(e) \ge 0.80$ and turn penalties are nonnegative, we establish..."* Explicitly states the non-negativity condition ($P_{\text{turn}} \ge 0$) required for A* admissibility and consistency proofs.

---

## 3. Final Deliverables State

- [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) — 208 words, fully compliant with IEEE format.
- [`paper1_abstract_claim_audit_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_claim_audit_v2.md) — 10-claim verification table and literature matrix.
- [`phase_5_2_validation_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_2_validation_log.md) — Authoritative validation log.
