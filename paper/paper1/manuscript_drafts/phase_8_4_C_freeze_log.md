# Phase 8.4-C Freeze Log: Section VII Canonical Freeze

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.4-C — Formal Freeze of Section VII  
**Date:** 2026-11-07  
**Document:** [`phase_8_4_C_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_4_C_freeze_log.md)  
**Canonical Frozen File:** [`paper1_section_VII_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VII_draft_v1.md)  
**Approved Version:** Section VII Draft v1.1  
**Approved SHA-256 Digest:** `7B65C133DB600739DDCA4BB029B4CCF49DDEA7F43D961FA863CD230B21297EDB`  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **SECTION VII CANONICAL MANUSCRIPT FROZEN (APPROVED BY RESEARCH LEAD)**  

---

## 1. Formal Freeze Declaration

By explicit authorization of the Research Lead, Section VII of Paper 1 (*Conclusion and Future Work*) has completed architecture design, evidence mapping, initial drafting, five targeted precision revisions (Phase 8.4-B-R1), and cryptographic verification. Section VII Draft v1.1 is hereby declared **CANONICALLY FROZEN**.

The canonical frozen file is located at:
- [`research/paper1_manuscript/paper1_section_VII_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VII_draft_v1.md)

Under project research protocol and version-control governance, **no further modifications, edits, word substitutions, or refactorings may be made to this file without explicit authorization from the Research Lead.**

---

## 2. Scope of Frozen Material

The frozen scope comprises the complete body prose spanning the approved four-paragraph architecture:
- **Paragraph 1:** Algorithmic contributions, state-expanded formulation $s = (u, v)$, road-class-dependent impedance modelling, and Theorem 1 Haversine heuristic conditional admissibility ($\mu(e) \ge 0.80$ qualified on Bengaluru graph).
- **Paragraph 2:** Key empirical ablation synthesis across Experiments A–D:
  - Experiment A: $34.1\%$ sharp-turn reduction ($p_{\text{adj}} = 4.5 \times 10^{-5}$) with median runtime increasing from $154.69$ to $174.93\text{ ms}$.
  - Experiment B: $51.21$ percentage-point arterial exposure reduction ($p_{\text{adj}} = 8.4 \times 10^{-5}$) with a $15.53\%$ increase in mean physical route distance ($p_{\text{adj}} = 6.8 \times 10^{-5}$).
  - Experiment C: Configuration $C_2$ captures $87.1\%$ of maximum observed turn reduction as an empirical corpus-average trade-off knee.
  - Experiment D: Grade-separated bridge modifiers shifted routes on two corridors (OD_04: $-645\text{ m}$; OD_15: $-2.15\text{ km}$; 23 unchanged), whereas roundabout modifiers produced zero geometric changes across all 25 corridors.
- **Paragraph 3:** Methodological limitations and research boundaries:
  - Evaluated on single OpenStreetMap Bengaluru network across 25 corridors.
  - Real-world journey times were not collected; travel-time reduction was not demonstrated; configured impedance scales algorithmic search costs, distinct from physical distance or travel time.
  - Sharp-turn counts represent geometric manoeuvre measures and do not establish safety improvements or accident reduction.
  - Multipliers lack behavioral rider calibration.
  - Actual search-objective costs were not retained in Experiment D.
- **Paragraph 4:** Concrete future research directions:
  - Testing parameter transferability and heuristic bounds across diverse urban topologies.
  - Empirical calibration using GPS trajectories and rider choice data.
  - Collecting real-world journey times to evaluate whether the framework achieves its intended practical objective of time-efficient travel.
  - Incorporating dynamic traffic, slope gradients, and vehicle-specific constraints.

---

## 3. Canonical Frozen Text

The complete, unabridged, and canonical text of Section VII from [`paper1_section_VII_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VII_draft_v1.md) is recorded below:

```markdown
## VII. CONCLUSION AND FUTURE WORK

This study developed a state-expanded, turn-aware A* routing framework for two-wheeler routing on urban road networks. Directed edge states $s = (u, v)$ enable exact turn-cost evaluation without auxiliary path memory. Traversal costs are governed by road-class-dependent impedance modelling. Scaled by $\mu_{\min} = 0.80$, the Haversine heuristic is admissible and consistent under Theorem 1, conditioned on the lower bound $\mu(e) \ge 0.80$ verified on the evaluated Bengaluru graph.

Across 25 corridors, empirical ablations demonstrated marked routing shifts. Turn-aware search reduced sharp turns by $34.1\%$ relative to turn-unaware expansion ($p_{\text{adj}} = 4.5 \times 10^{-5}$) with median runtime increasing from $154.69$ to $174.93\text{ ms}$. Road-class impedance lowered arterial exposure by $51.21$ percentage points ($p_{\text{adj}} = 8.4 \times 10^{-5}$) with a $15.53\%$ increase in mean physical route distance ($p_{\text{adj}} = 6.8 \times 10^{-5}$). Configuration $C_2$ captured $87.1\%$ of the maximum observed turn reduction as an empirical corpus-average trade-off knee. Bridges shifted routes on two corridors (OD_04 and OD_15; 23 unchanged), while roundabouts produced zero geometric changes across all 25 corridors.

Methodological boundaries qualify these findings. Evaluations were restricted to Bengaluru's street network across 25 corridors. Lacking real-world journey-time measurements, travel-time reduction was not demonstrated; configured impedance scales algorithmic search costs, distinct from physical distance or travel time. Sharp-turn counts represent geometric manoeuvre measures and do not establish safety improvements or accident reduction. Multipliers lack behavioral rider calibration, and Experiment D search-objective costs were not retained.

Future work will evaluate the framework across diverse topologies to assess parameter transferability and heuristic bounds. Penalty weights will be calibrated using empirical GPS trajectories and rider choices. Collecting real-world journey times will evaluate whether the framework achieves its intended practical objective of time-efficient travel. Finally, incorporating dynamic traffic, gradients, and vehicle-specific constraints remains open.
```

---

## 4. Cryptographic Fingerprint and Word Count Specification

- **Canonical File Path:** [`research/paper1_manuscript/paper1_section_VII_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VII_draft_v1.md)
- **Verified SHA-256 Digest:** `7B65C133DB600739DDCA4BB029B4CCF49DDEA7F43D961FA863CD230B21297EDB`
- **Total Body Math-as-Single-Token Word Count:** **267 words**
- **Total Body Whitespace Word Count:** **287 words**
- **Structure:** Exactly 4 paragraphs

### Detailed Paragraph Word-Count Accounting
Counting scope covers prose strictly within Section VII body, excluding markdown headings, dividers, and audit tables:

| Paragraph | Primary Thematic Content | Target Budget | Math as Single Token | Whitespace Word Count | Budget Variance (Math Token) | Compliance Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Paragraph 1** | Contributions, state expansion, impedance, Theorem 1 admissibility | ~60 words | **61 words** | 68 words | $+1\text{ word}$ ($+1.7\%$) | **EXACT FIT** |
| **Paragraph 2** | Empirical findings: Exp A (-34.1%), Exp B (-51.21 pp), Exp C ($C_2$ knee), Exp D | ~75 words | **86 words** | 99 words | $+11\text{ words}$ ($+14.7\%$) | **ALIGNED** |
| **Paragraph 3** | Methodological limitations: network scope, travel-time demarcation, proxy metrics | ~60 words | **65 words** | 65 words | $+5\text{ words}$ ($+8.3\%$) | **ALIGNED** |
| **Paragraph 4** | Future directions: transferability, GPS calibration, real-world travel time, vehicle constraints | ~50 words | **55 words** | 55 words | $+5\text{ words}$ ($+10.0\%$) | **ALIGNED** |
| **Total Body** | **Complete Section VII Body Prose** | **~245 words** | **267 words** | **287 words** | **$+22\text{ words}$ ($+9.0\%$)** | **WITHIN BUDGET** |

---

## 5. Frozen Integrity Verification of Preceding Manuscript Sections

All previously approved and frozen sections, as well as preceding freeze logs and the Section VII architecture file, remain byte-for-byte identical and unmodified, verified by cryptographic SHA-256 hash matching:

| Manuscript Unit | Canonical File Path | Status | Expected Canonical SHA-256 | Actual Verified SHA-256 | Verification |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Abstract** | [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | FROZEN | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | **MATCH** |
| **Section I** | [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | FROZEN | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | **MATCH** |
| **Section II** | [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | FROZEN | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | **MATCH** |
| **Section III** | [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) | FROZEN | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | **MATCH** |
| **Section IV-A** | [`paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md) | FROZEN | `8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE` | `8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE` | **MATCH** |
| **Section IV-B** | [`paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md) | FROZEN | `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6` | `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6` | **MATCH** |
| **Section IV-C** | [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md) | FROZEN | `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1` | `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1` | **MATCH** |
| **Section IV-D** | [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md) | FROZEN | `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772` | `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772` | **MATCH** |
| **Section V** | [`paper1_section_V_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_V_draft_v1.md) | FROZEN | `C3330EB0E42D0BCABE6D2AAB16461B9B12BED701886F5B815BA82D5815185DD6` | `C3330EB0E42D0BCABE6D2AAB16461B9B12BED701886F5B815BA82D5815185DD6` | **MATCH** |
| **Section VI** | [`paper1_section_VI_draft_v4.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VI_draft_v4.md) | FROZEN | `C6F31CAFD830F4EFE2419D4A6466132FFD66BC07771244B1902C0D321A6510DE` | `C6F31CAFD830F4EFE2419D4A6466132FFD66BC07771244B1902C0D321A6510DE` | **MATCH** |
| **Freeze Log V** | [`phase_8_3_B_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_B_freeze_log.md) | FROZEN | `53BCF6DAF9137E5A98131FECDF57905399122CD5FD8356196E9BA9D6F3BFF3DB` | `53BCF6DAF9137E5A98131FECDF57905399122CD5FD8356196E9BA9D6F3BFF3DB` | **MATCH** |
| **Freeze Log VI** | [`phase_8_3_C2_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_C2_freeze_log.md) | FROZEN | `625E7BFE4A98703232E6CB8A14738396BF6D7C5FFE84BEA272683F016A929489` | `625E7BFE4A98703232E6CB8A14738396BF6D7C5FFE84BEA272683F016A929489` | **MATCH** |
| **Section VII Architecture** | [`phase_8_4_A_section_VII_architecture.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_4_A_section_VII_architecture.md) | APPROVED | `8DF6EA0CF38B769A4978FDB872225856D78E59F43D490A2A38D2489054D44288` | `8DF6EA0CF38B769A4978FDB872225856D78E59F43D490A2A38D2489054D44288` | **MATCH** |

---

## 6. Research Boundaries and Stop Condition Compliance

1. **Experimental Data and Code Integrity:** Zero modifications made to source code, execution harnesses, raw trajectory CSVs, statistical test results, or publication figures.
2. **Experiment E Demarcation:** Experiment E, perpendicular lateral offset waypoint generation, candidate path pruning, and topological diversity benchmarks vs. Yen's KSP remain strictly excluded from Paper 1 and reserved exclusively for Paper 2.
3. **Compilation Boundaries:** Full manuscript assembly and compilation into `paper1_main.tex` have **NOT** been performed.
4. **Active Freeze:** Section VII is formally declared frozen as of this document.

---

## 7. Next Phase Readiness

All seven manuscript sections (Abstract through Section VII) are now formally approved and canonically frozen:
- **Abstract:** Frozen v2.0 (`67272764F7DA...`)
- **Section I (Introduction):** Frozen v1.0 (`3271BE72BA4A...`)
- **Section II (Related Work):** Frozen v1.0 (`839C1D5936F7...`)
- **Section III (Problem Formulation & System Architecture):** Frozen v1.0 (`CEE2B6A495D0...`)
- **Section IV (Turn-Aware A* Algorithm, Correctness & Complexity):** Frozen v2.0 (`8B86B3722895...`, `CB88AC8A9263...`, `08262BE23D74...`, `B1A07D5CD095...`)
- **Section V (Experimental Setup & Methodology):** Frozen v1.0 (`C3330EB0E42D...`)
- **Section VI (Experimental Results and Discussion):** Frozen v4.0 (`C6F31CAFD830...`)
- **Section VII (Conclusion and Future Work):** Frozen v1.1 (`7B65C133DB60...`)

Standing by for Research Lead instructions regarding:
- **Phase 8.5:** Full Manuscript Assembly, Global Citation Reconciliation, and Final IEEEtran Compilation into `paper1_main.tex`.


---

## 8. Supplementary Integrity Verification: Phase 8.2 Section IV Freeze Log (Phase 8.4-C-R1)

Pursuant to Research Lead directive Phase 8.4-C-R1, the Phase 8.2 Section IV freeze log was audited to complete global freeze-log traceability:

- **Target File:** [`research/paper1_manuscript/phase_8_2_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_2_freeze_log.md)
- **Recomputed SHA-256 Digest:** `BA41DBAACE8F86CCA28BD9E774FFF6981BA9BFBF3DD75D3E0C46797C1508CB79`
- **Historical Expected Hash Availability:** No previous expected SHA-256 hash was historically recorded for this freeze-log file in subsequent logs (`phase_8_3_B_freeze_log.md` or `phase_8_3_C2_freeze_log.md`).
- **Verification Result:** Canonical file located, read-only integrity confirmed, and canonical SHA-256 baseline established (`BA41DBAACE8F86CCA28BD9E774FFF6981BA9BFBF3DD75D3E0C46797C1508CB79`). The file contains verified frozen hashes for Section IV subsections IV-A through IV-D (`8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE`, `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6`, `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1`, `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772`).
- **Manuscript Invariance Confirmation:** Neither `phase_8_2_freeze_log.md` nor any manuscript section (I–VII) was modified during this verification check.
