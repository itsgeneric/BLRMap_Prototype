# Section VII: Conclusion and Future Work (Draft v1.1)

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (Standard IEEE Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.4-B-R1 — Targeted Section VII Revisions  
**Document:** [`paper1_section_VII_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VII_draft_v1.md)  
**Source Architecture:** [`phase_8_4_A_section_VII_architecture.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_4_A_section_VII_architecture.md) (v1.1 Audited & Approved)  
**Status:** REVISED DRAFT v1.1 (Awaiting Research Lead Approval)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  

---

## VII. CONCLUSION AND FUTURE WORK

This study developed a state-expanded, turn-aware A* routing framework for two-wheeler routing on urban road networks. Directed edge states $s = (u, v)$ enable exact turn-cost evaluation without auxiliary path memory. Traversal costs are governed by road-class-dependent impedance modelling. Scaled by $\mu_{\min} = 0.80$, the Haversine heuristic is admissible and consistent under Theorem 1, conditioned on the lower bound $\mu(e) \ge 0.80$ verified on the evaluated Bengaluru graph.

Across 25 corridors, empirical ablations demonstrated marked routing shifts. Turn-aware search reduced sharp turns by $34.1\%$ relative to turn-unaware expansion ($p_{\text{adj}} = 4.5 \times 10^{-5}$) with median runtime increasing from $154.69$ to $174.93\text{ ms}$. Road-class impedance lowered arterial exposure by $51.21$ percentage points ($p_{\text{adj}} = 8.4 \times 10^{-5}$) with a $15.53\%$ increase in mean physical route distance ($p_{\text{adj}} = 6.8 \times 10^{-5}$). Configuration $C_2$ captured $87.1\%$ of the maximum observed turn reduction as an empirical corpus-average trade-off knee. Bridges shifted routes on two corridors (OD_04 and OD_15; 23 unchanged), while roundabouts produced zero geometric changes across all 25 corridors.

Methodological boundaries qualify these findings. Evaluations were restricted to Bengaluru's street network across 25 corridors. Lacking real-world journey-time measurements, travel-time reduction was not demonstrated; configured impedance scales algorithmic search costs, distinct from physical distance or travel time. Sharp-turn counts represent geometric manoeuvre measures and do not establish safety improvements or accident reduction. Multipliers lack behavioral rider calibration, and Experiment D search-objective costs were not retained.

Future work will evaluate the framework across diverse topologies to assess parameter transferability and heuristic bounds. Penalty weights will be calibrated using empirical GPS trajectories and rider choices. Collecting real-world journey times will evaluate whether the framework achieves its intended practical objective of time-efficient travel. Finally, incorporating dynamic traffic, gradients, and vehicle-specific constraints remains open.

---

## Word Count and Allocation Audit

The table below summarizes the paragraph-level and cumulative word counts for the Section VII body prose (excluding section title, markdown headings, dividers, and audit tables):

| Paragraph | Primary Thematic Content | Target Budget | Math as Single Token | Whitespace Word Count | Budget Variance (Math Token) | Compliance Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Paragraph 1** | Contributions, state expansion, impedance, Theorem 1 admissibility | ~60 words | **61 words** | 68 words | $+1\text{ word}$ ($+1.7\%$) | **ALIGNED** |
| **Paragraph 2** | Empirical findings: Exp A (-34.1%), Exp B (-51.21 pp), Exp C ($C_2$ knee), Exp D | ~75 words | **86 words** | 99 words | $+11\text{ words}$ ($+14.7\%$) | **ALIGNED** |
| **Paragraph 3** | Methodological limitations: network scope, travel-time demarcation, proxy metrics | ~60 words | **65 words** | 65 words | $+5\text{ words}$ ($+8.3\%$) | **ALIGNED** |
| **Paragraph 4** | Future directions: transferability, GPS calibration, real-world travel time, vehicle constraints | ~50 words | **55 words** | 55 words | $+5\text{ words}$ ($+10.0\%$) | **ALIGNED** |
| **Total Body** | **Complete Section VII Body Prose** | **~245 words** | **267 words** | **287 words** | **$+22\text{ words}$ ($+9.0\%$)** | **WITHIN BUDGET** |

---

## Evidence-Grounding and Audit Checklist

| Item / Claim | Canonical Supporting Source | Audited Value / Citation | Verification Status |
| :--- | :--- | :--- | :---: |
| **State-Expanded Search** | Section IV-A (`paper1_section_IV_A_draft_v2.md`) | $s = (u, v) \in E_s$, exact turn cost without path history | **VERIFIED** |
| **Road-Class Impedance** | Section III (`paper1_section_III_v1.md`, Table I) | Road-class-dependent impedance modelling ($0.90\text{--}2.50$) | **VERIFIED** |
| **Theorem 1 Admissibility** | Section IV-C (`paper1_section_IV_C_draft_v2.md`) | $h(u, v) = \mu_{\min} \cdot \text{hav}(u, d)$ with $\mu_{\min} = 0.80$ | **VERIFIED** |
| **Heuristic Bound Qualification** | Section III, `core/config.py` | $\mu(e) \ge 0.80$ verified on Bengaluru graph, not universal | **VERIFIED** |
| **Exp A Turn Reduction** | `statistical_test_results.csv#L2` | $-34.1\%$, mean diff $-11.08$, Pratt $W=0.0$, $p_{\text{adj}}=4.5 \times 10^{-5}$ | **VERIFIED** |
| **Exp A Runtime Overhead** | `statistical_test_results.csv#L4` | Median runtime increasing from $154.69$ to $174.93\text{ ms}$, $p_{\text{adj}}=1.2 \times 10^{-5}$ | **VERIFIED** |
| **Exp B Arterial Reduction** | `statistical_test_results.csv#L8` | $-51.21$ percentage points ($65.05\% \to 13.84\%$), $p_{\text{adj}}=8.4 \times 10^{-5}$ | **VERIFIED** |
| **Exp B Physical Detour** | `statistical_test_results.csv#L11` | $+15.53\%$ increase in mean physical route distance ($+1.028\text{ km}$), $p_{\text{adj}}=6.8 \times 10^{-5}$ | **VERIFIED** |
| **Exp C Knee Designation** | `statistical_test_results.csv#L20-L25` | $C_2$ captured $87.1\%$ of maximum observed turn reduction, empirical corpus knee | **VERIFIED** |
| **Exp D Bridge Shifts** | `exp_d_corridor_metrics.csv` | Shifted on OD_04 ($-645\text{ m}$) and OD_15 ($-2.15\text{ km}$); 23 unchanged | **VERIFIED** |
| **Exp D Roundabout Invariance** | `exp_d_corridor_metrics.csv` | $25/25$ zero geometry/distance differences across all corridors | **VERIFIED** |
| **Exp D Cost Non-Retention** | Section VI-D (`paper1_section_VI_draft_v4.md`) | Actual configured search-objective costs not retained by harness | **VERIFIED** |
| **Travel-Time Demarcation** | Phase 8.4-A-R1 Directive | Intended objective stated; unmeasured empirically; distinct from distance | **VERIFIED** |
| **Safety Demarcation** | Phase 13.4 Protocol | Geometric manoeuvre measures, do not establish safety or accident reduction | **VERIFIED** |
| **Behavioral Demarcation** | Phase 13.4 Protocol | Multipliers lack behavioral discrete-choice rider calibration | **VERIFIED** |
| **Demarcation vs. Paper 2** | `blrmap-research-protocol` | Exp E, perpendicular offset, and alternative routing excluded | **VERIFIED** |

---

## Preceding Frozen Manuscript Cryptographic Hash Verification

| Manuscript Section | Canonical Path | Verified SHA-256 Digest | Status |
| :--- | :--- | :--- | :---: |
| **Abstract** | [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | **FROZEN** |
| **Section I** | [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | **FROZEN** |
| **Section II** | [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | **FROZEN** |
| **Section III** | [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | **FROZEN** |
| **Section IV-A** | [`paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md) | `8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE` | **FROZEN** |
| **Section IV-B** | [`paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md) | `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6` | **FROZEN** |
| **Section IV-C** | [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md) | `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1` | **FROZEN** |
| **Section IV-D** | [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md) | `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772` | **FROZEN** |
| **Section V** | [`paper1_section_V_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_V_draft_v1.md) | `C3330EB0E42D0BCABE6D2AAB16461B9B12BED701886F5B815BA82D5815185DD6` | **FROZEN** |
| **Section VI** | [`paper1_section_VI_draft_v4.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VI_draft_v4.md) | `C6F31CAFD830F4EFE2419D4A6466132FFD66BC07771244B1902C0D321A6510DE` | **FROZEN** |
| **Freeze Log V** | [`phase_8_3_B_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_B_freeze_log.md) | `53BCF6DAF9137E5A98131FECDF57905399122CD5FD8356196E9BA9D6F3BFF3DB` | **FROZEN** |
| **Freeze Log VI** | [`phase_8_3_C2_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_C2_freeze_log.md) | `625E7BFE4A98703232E6CB8A14738396BF6D7C5FFE84BEA272683F016A929489` | **FROZEN** |
| **Section VII Architecture** | [`phase_8_4_A_section_VII_architecture.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_4_A_section_VII_architecture.md) | `8DF6EA0CF38B769A4978FDB872225856D78E59F43D490A2A38D2489054D44288` | **APPROVED** |
