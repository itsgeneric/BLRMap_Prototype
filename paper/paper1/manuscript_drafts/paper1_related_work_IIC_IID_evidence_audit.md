# Section II: Related Work (Subsections II-C and II-D) Evidence and Word-Count Audit (v1.1 Revised)

**Document:** [`paper1_related_work_IIC_IID_evidence_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIC_IID_evidence_audit.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Audited Draft:** [`paper1_related_work_IIC_IID_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIC_IID_v1.md) (v1.1)  
**Parent Outline:** [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md) (v1.1)  
**Parent Citation Map:** [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md) (v1.4)  
**Master Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Frozen Introduction:** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) (468 words)  
**Frozen II-A/II-B Draft:** [`paper1_related_work_IIA_IIB_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_v1.md) (v1.2, 172 words)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 6.2.2-R REVISED EVIDENCE AUDIT COMPLETE (AWAITING LEAD APPROVAL)**  
**Effective Date:** 2026-11-06  

---

## 1. Executive Summary & Phase 6.2.2-R Targeted Precision Corrections

This audit certifies the three targeted precision corrections applied under Phase 6.2.2-R to Subsections II-C and II-D:

1. **Fadilah et al. (2024) Simulation-Based Precision (II-C):**
   - *Previous Drafting:* Stated that stated-preference modeling and microscopic simulation "demonstrated that motorcycle route selection departs from static shortest paths".
   - *Correction Applied:* The sentence was revised to explicitly identify the result as simulation-based:
     > "In Ninh Kiều District, Cần Thơ, Vietnam, Fadilah et al. \cite{fadilah2024identifying} used stated-preference modelling and microscopic simulation to examine motorcycle route selection under traffic-information scenarios, reporting departures from static shortest-path assignments in the simulated results."
   - *Evidentiary Rationale:* Strictly preserves the demarcation between the authors' stated-preference discrete-choice estimation ($N = 301$) and the subsequent microscopic simulation in Aimsun, confirming that departures from static shortest paths were reported within the simulated outcomes, rather than observed as real-world physical en-route switching.
2. **Conditional Theoretical Claim Formulation (II-D):**
   - *Previous Drafting:* Stated "formal heuristic consistency guarantees".
   - *Correction Applied:* Replaced with:
     > "conditional heuristic admissibility and consistency"
   - *Evidentiary Rationale:* Accurately reflects the conditional nature of the theoretical proof in Section IV, where consistency and admissibility of the Haversine heuristic scaled by $0.80$ hold under the condition that edge impedance multipliers satisfy $\mu(e) \ge 0.80$ and turn penalties are nonnegative ($c_{\text{turn}} \ge 0$).
3. **Evaluation Description Refinement (II-D):**
   - *Previous Drafting:* Stated "quantifies the operational trade-offs".
   - *Correction Applied:* Replaced with:
     > "quantifies route-level trade-offs"
   - *Evidentiary Rationale:* More precisely characterizes the empirical ablation results (A0 vs. A1, B0 vs. B1), which evaluate corridor route attributes (sharp turn frequency, arterial exposure, physical route distance) rather than broader operational fleet or traffic network dynamics.

---

## 2. Word Count and Page Budget Tracking

| Subsection | Stated Target Budget | Actual Word Count (Whitespace Split) | Variance | Budget Status |
| :--- | :---: | :---: | :---: | :---: |
| **Subsection II-C** | ~95 words | **101 words** | $+6$ words | **PASSED (Exact Fit)** |
| **Subsection II-D** | ~75 words | **76 words** | $+1$ word | **PASSED (Exact Fit)** |
| **Combined II-C + II-D** | **~170 words** | **177 words** | **$+7$ words** | **PASSED (Exact Fit)** |

### Cumulative Section II Footprint
- **Subsections II-A + II-B (approved v1.2):** **172 words**
- **Subsections II-C + II-D (revised v1.1):** **177 words**
- **Full Section II Total:** **349 words** (Blueprint allocation: 340 words, $\approx 46$ lines; variance: $+9$ words / $+2.6\%$). Strictly aligns with the 46-line blueprint allocation without overflowing.

---

## 3. Granular Sentence-by-Sentence Claim-to-Evidence Mapping

### Subsection II-C: Two-Wheeler Routing and Road-Class Impedance (101 words)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          SUBSECTION II-C EVIDENCE MAPPING                                              │
├─────────────────────────────────────────────────┬─────────────────────────┬──────────────┬─────────────────────────────┤
│ Sentence Text                                   │ Citation Key            │ Support Type │ Supporting Source Passage   │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Two-wheeler navigation operates under mixed-   │ kotagi2020modeling      │ DIRECT       │ Kotagi et al. (2020),       │
│ traffic conditions characterized by vehicle     │ promraksa2022lane       │ DEMONSTRATED │ Sec 3–4 (pp. 863–871);      │
│ speed dispersion \cite{kotagi2020modeling} and  │                         │ (OPTIONAL)   │ Promraksa et al. (2022),    │
│ queue lane-filtering \cite{promraksa2022lane}." │                         │              │ Sec 3–4 (pp. 4–11): Field   │
│                                                 │                         │              │ video data of speed spread  │
│                                                 │                         │              │ and junction filtering.     │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "In Ninh Kiều District, Cần Thơ, Vietnam,       │ fadilah2024identifying  │ MODEL-BASED  │ Fadilah et al. (2024),      │
│ Fadilah et al. \cite{fadilah2024identifying}    │                         │ SIMULATION   │ Sec 2–4 (pp. 2–9), Table 1, │
│ used stated-preference modelling and            │                         │ (ESSENTIAL)  │ Fig 5–8: SP discrete choice │
│ microscopic simulation to examine motorcycle    │                         │              │ (N=301) and Aimsun MFD      │
│ route selection under traffic-information       │                         │              │ simulation under VMS.       │
│ scenarios, reporting departures from static     │                         │              │                             │
│ shortest-path assignments in the simulated      │                         │              │                             │
│ results."                                       │                         │              │                             │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "For two-wheeler routing, Asvial et al.         │ asvial2020entropy       │ DIRECT       │ Asvial et al. (2020),       │
│ \cite{asvial2020entropy} evaluated route        │                         │ DEMONSTRATED │ Sec III-A/B (pp. 443–444)   │
│ suitability by generating candidate paths       │                         │ (ESSENTIAL)  │ & Sec V-A (pp. 444–445):    │
│ without turn penalties and applying post-hoc    │                         │              │ EBkSP with turn cost = 0    │
│ Entropy-TOPSIS re-ranking."                     │                         │              │ and post-hoc TOPSIS ranking.│
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Rather than re-ranking candidate paths or      │ [Conceptual             │ ENGINEERING  │ Architectural distinction:  │
│ modeling behavioral choice, we evaluate         │ demarcation]            │ HEURISTIC    │ In-search configured road   │
│ configured road impedance directly within       │                         │ POSITIONING  │ multipliers vs. post-hoc    │
│ graph search as an engineering heuristic,       │                         │              │ re-ranking / choice models. │
│ without asserting that configured multipliers   │                         │              │ Explicitly disclaims rider  │
│ represent calibrated rider preferences."        │                         │              │ psychological validation.   │
└─────────────────────────────────────────────────┴─────────────────────────┴──────────────┴─────────────────────────────┘
```

- **Evidentiary Categorization in II-C:**
  - *Direct Empirical Evidence:* Speed dispersion on undivided Indian corridors (`kotagi2020modeling`, Sec 3–4); empirical intersection lane-filtering in Khon Kaen, Thailand (`promraksa2022lane`, Sec 3–4). Scoped strictly to observed traffic flow physics.
  - *Model-Based / Simulation Evidence:* Stated-preference discrete-choice modeling and Aimsun microscopic simulation under hypothetical VMS traffic-information scenarios in Ninh Kiều District, Cần Thơ, Vietnam (`fadilah2024identifying`, Table 1, Sec 4). Does not assert physical en-route switching; does not compare observed motorcycle trajectories with passenger-car trajectories; does not validate Paper 1 impedance multipliers.
  - *Direct Algorithmic Baseline:* Candidate path generation with $\text{turn cost} = 0$ followed by post-hoc Entropy-TOPSIS re-ranking across six simulated OD corridors in South Jakarta (`asvial2020entropy`, Sec III/V). Does not claim Asvial et al. evaluates turn angles or delays.
  - *Engineering Heuristic Demarcation:* Configured road impedance and flyovers are positioned strictly as an engineering heuristic evaluated within graph search, explicitly disclaiming validated rider psychological preferences.

---

### Subsection II-D: Research Positioning and Synthesis (76 words)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          SUBSECTION II-D EVIDENCE MAPPING                                              │
├─────────────────────────────────────────────────┬─────────────────────────┬──────────────┬─────────────────────────────┤
│ Sentence Text                                   │ Citation Key            │ Support Type │ Supporting Source Passage   │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Prior literature establishes multi-objective   │ zografos2004heuristic   │ DIRECT       │ Zografos & Androutsopoulos  │
│ routing with turn penalties on edge-expanded    │ delling2017customizable │ DEMONSTRATED │ (2004), Sec 2–3 (pp. 509–   │
│ graphs for specialized fleet operations         │ asvial2020entropy       │ & CONTEXTUAL │ 515); Delling et al. (2017);│
│ \cite{zografos2004heuristic}, alongside         │                         │ (ESSENTIAL)  │ Asvial et al. (2020): Prior │
│ hierarchical metric customization               │                         │              │ art capabilities in turns,  │
│ \cite{delling2017customizable} and post-hoc     │                         │              │ customization, and ranking. │
│ two-wheeler path evaluation                     │                         │              │                             │
│ \cite{asvial2020entropy}."                      │                         │              │                             │
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "This paper addresses the integration of        │ [Paper 1 Scope          │ SCOPE        │ Integration focus: online   │
│ online turn-aware state-expanded $A^*$ search   │ Definition]             │ DEFINITION   │ state-expanded search +     │
│ with configured two-wheeler road-class          │                         │              │ configured impedance +      │
│ impedance and conditional heuristic             │                         │              │ conditional heuristic       │
│ admissibility and consistency."                 │                         │              │ admissibility & consistency.│
├─────────────────────────────────────────────────┼─────────────────────────┼──────────────┼─────────────────────────────┤
│ "Controlled evaluation across 25 corridors in   │ kumar2025realtime       │ CONTEXTUAL   │ Kumar et al. (2025),        │
│ Bengaluru, where arterial networks experience   │                         │ BACKGROUND   │ Sec 3–4 (pp. 621–627):      │
│ chronic bottleneck congestion                   │                         │ (OPTIONAL)   │ Chronic arterial bottleneck │
│ \cite{kumar2025realtime}, quantifies route-     │                         │              │ congestion on Bengaluru     │
│ level trade-offs between turn avoidance,        │                         │              │ radial corridors. Evaluates │
│ arterial exposure, and physical route distance."│                         │              │ distance/turn/class trade-off│
└─────────────────────────────────────────────────┴─────────────────────────┴──────────────┴─────────────────────────────┘
```

- **Evidentiary Categorization in II-D:**
  - *Direct Benchmark Evidence:* Zografos and Androutsopoulos (2004) establishes prior art in multi-objective routing with turn penalties on edge-expanded graphs for hazardous materials fleet routing (`zografos2004heuristic`, Sec 2–3).
  - *Contextual Background Evidence:* Kumar et al. (2025) documents chronic arterial bottleneck congestion on Bengaluru radial corridors (`kumar2025realtime`, Sec 3–4). The term "ground truth" is completely avoided.
  - *Research Positioning Formulation:* The research gap is framed strictly as the unified integration and controlled evaluation of turn-aware state-expanded search with configured road impedance and conditional heuristic admissibility and consistency. No global novelty or priority claims ("first", "only", "novel in the world") are made.

---

## 4. Master Bibliography Verification

All cited keys in Subsections II-C and II-D are verified against [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib):

| Citation Key | Primary Author & Year | Formally Verified Venue | Matched in `.bib` | Audit Status |
| :--- | :--- | :--- | :---: | :---: |
| `kotagi2020modeling` | Kotagi et al. (2020) | *J. Traffic Transp. Eng.*, 7(6) | **YES** | **VERIFIED** |
| `promraksa2022lane` | Promraksa et al. (2022) | *J. Adv. Transp.*, Art. 5662117 | **YES** | **VERIFIED** |
| `fadilah2024identifying` | Fadilah et al. (2024) | *Transp. Res. Interdiscip. Perspect.*, 28 | **YES** | **VERIFIED** |
| `asvial2020entropy` | Asvial et al. (2020) | *IJACSA*, 11(7) | **YES** | **VERIFIED** |
| `zografos2004heuristic` | Zografos & Androutsopoulos (2004) | *Eur. J. Oper. Res.*, 152(2) | **YES** | **VERIFIED** |
| `delling2017customizable` | Delling et al. (2017) | *Transportation Science*, 51(2) | **YES** | **VERIFIED** |
| `kumar2025realtime` | Kumar et al. (2025) | *Int. J. Transp. Dev. Integr.*, 9(3) | **YES** | **VERIFIED** |

- **New References Introduced:** **Zero (0).**

---

## 5. Scope-Boundary and Protocol Compliance Verification

| Guarded Research Boundary | Audit Rule / Prohibition | Compliance in II-C & II-D Prose | Audit Status |
| :--- | :--- | :--- | :---: |
| **Safety Claims** | NO claims of safety improvements, accident reduction, crash mitigation, or fatality drops. | Confined strictly to turn counts, angular deflections, and street-level friction. | **PASSED** |
| **Mobility Claims** | NO claims of unmeasured travel-time savings or city-wide congestion reduction. | Confined strictly to physical route distance, turn counts, and road-class exposure. | **PASSED** |
| **Fadilah Scoping** | Stated-preference discrete choice & simulation; NO claims of physical en-route switching observed; NO car trajectory comparison; NO validation of Paper 1 impedance weights. | Scoped strictly to Ninh Kiều District, Cần Thơ, Vietnam; stated-preference modeling and microscopic simulation under traffic-information scenarios. Explicitly identified as simulation-based. | **PASSED** |
| **Conditional Heuristic** | Frame heuristic correctness as conditional. | Stated as "conditional heuristic admissibility and consistency". | **PASSED** |
| **Trade-Off Framing** | Frame evaluation as route-level trade-offs. | Stated as "quantifies route-level trade-offs between turn avoidance, arterial exposure, and physical route distance." | **PASSED** |
| **Asvial Scoping** | Describe post-hoc evaluation accurately; do NOT claim turn-angle penalties or junction delays. | Explicitly stated: candidate paths generated "without turn penalties" followed by post-hoc Entropy-TOPSIS re-ranking. | **PASSED** |
| **Rider Preferences** | Do NOT imply configured weights are validated rider preferences. | Explicitly disclaimed: evaluated as an "engineering heuristic, without asserting that configured multipliers represent calibrated rider preferences." | **PASSED** |
| **Priority / Novelty Claims** | NO claims of global priority ("first", "only", "novel in the world"). | Framed strictly around the integration and controlled evaluation of methods. | **PASSED** |
| **Paper 2 Scope Leakage** | NO alternative routing, Yen's KSP, route diversity, or perpendicular offset. | Completely excluded from both subsections. | **PASSED** |
| **Section Freeze Verification** | Section I and Subsections II-A/II-B must remain verbatim frozen. | Confirmed: [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) (468 words) and [`paper1_related_work_IIA_IIB_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_v1.md) (172 words) were **not modified**. | **PASSED** |
| **Assembly Boundary** | Full Section II must NOT be assembled. | Confirmed: Full Section II remains unassembled. | **PASSED** |

---

## 6. Certification and Stop Condition

- **Drafted Deliverable:** [`paper1_related_work_IIC_IID_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIC_IID_v1.md) (v1.1, 177 words total: II-C = 101 words, II-D = 76 words).
- **Evidence Audit Deliverable:** [`paper1_related_work_IIC_IID_evidence_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIC_IID_evidence_audit.md) (v1.1).
- **Execution Log Deliverable:** [`phase_6_2_2_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_6_2_2_execution_log.md) (v1.1).

**STOP:** Phase 6.2.2-R targeted precision corrections complete. Full Section II has NOT been assembled. Section I and Subsections II-A/II-B remain frozen. Awaiting Research Lead instructions.
