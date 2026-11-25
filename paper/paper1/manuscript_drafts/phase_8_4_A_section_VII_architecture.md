# Phase 8.4-A: Section VII Architecture and Evidence Mapping (v1.1 Corrected)

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (Standard IEEE Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.4-A-R1 — Section VII Architecture Correction  
**Document:** [`phase_8_4_A_section_VII_architecture.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_4_A_section_VII_architecture.md)  
**Status:** ARCHITECTURE REVISED (Awaiting Research Lead Approval)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  

---

## 1. Architectural Overview & Allocation Budget

Section VII (*Conclusion and Future Work*) serves as the closing section of Paper 1. In IEEE conference format (6.0 pages max), Section VII provides a rigorous, evidence-grounded synthesis of the paper's theoretical contributions and empirical findings while maintaining scientific neutrality, explicitly acknowledging empirical boundaries, and charting concrete future research directions.

### Target Word Allocation Budget
- **Approved Section VII Target Allocation:** **~245 words** (math-as-single-token).
- **Proposed Paragraph Structure:** 4 targeted paragraphs.
- **Budget Distribution:**
  - **Paragraph 1: Core Contributions & Theoretical Guarantees:** ~60 words
  - **Paragraph 2: Key Empirical Ablation Findings:** ~75 words
  - **Paragraph 3: Methodological & Empirical Limitations:** ~60 words
  - **Paragraph 4: Future Research Directions:** ~50 words
  - **Total Architecture Budget:** **245 words**

---

## 2. Proposed Paragraph Structure and Purpose

### Paragraph 1: Core Contributions & Theoretical Guarantees
- **Target Allocation:** ~60 words
- **Purpose:** Synthesize the primary algorithmic, modeling, and theoretical contributions of Paper 1 without hyperbole.
- **Key Elements to Cover:**
  1. *State-Expanded Turn-Aware Search:* Formulation of directed edge states $s = (u, v) \in E_s$ enabling exact turn-angle evaluations ($\theta \in [0^\circ, 180^\circ]$) without auxiliary path-history memory.
  2. *Two-Wheeler Road-Class Impedance:* Road-class-dependent impedance modelling function $f_{\text{class}}$ differentiating street categories to reflect urban two-wheeler traversal preferences, coupled with topological modifiers.
  3. *Conditional Heuristic Admissibility:* Theorem 1 establishing that scaled Haversine heuristic $h(u, v) = \mu_{\min} \cdot \text{hav}(u, d)$ is strictly admissible and consistent, conditioned on the lower bound $\mu(e) \ge \mu_{\min} = 0.80$.
- **Scientific Guardrails:** State explicitly that $\mu(e) \ge 0.80$ is a dataset-verified lower bound verified specifically for the evaluated Bengaluru road network graph, not an unconditional or universal property of arbitrary road graphs.

### Paragraph 2: Key Empirical Ablation Findings
- **Target Allocation:** ~75 words
- **Purpose:** Summarize the primary empirical outcomes across Experiments A–D evaluated over the 25 origin–destination corridors.
- **Key Elements to Cover:**
  1. *Turn Reduction (Exp A):* Turn-aware search ($A_0$) achieves a statistically significant $34.1\%$ reduction in sharp turns ($\ge 60^\circ$) relative to turn-unaware search ($A_1$) ($32.52 \to 21.44$, $p_{\text{adj}} = 4.5 \times 10^{-5}$), with measured runtime overhead ($174.93$ vs. $154.69\text{ ms}$).
  2. *Hierarchy Realignment & Detour Trade-off (Exp B):* Production impedance ($B_0$) drops arterial exposure by $51.21$ percentage points ($65.05\% \to 13.84\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$) and expands residential share by $+30.73$ pp ($p_{\text{adj}} = 1.5 \times 10^{-4}$), at the cost of an observed physical detour of $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}} = 6.8 \times 10^{-5}$).
  3. *Sensitivity & Trade-off Knee (Exp C):* Monotonic sharp-turn reduction across tiers $C_0 \to C_3$, with baseline $C_2$ ($25/8\text{ m}$) capturing $87.1\%$ of maximum turn reduction at minimum corpus mean distance ($7.648\text{ km}$), beyond which $C_3$ exhibits diminishing returns ($+19.7\text{ m}$ per turn avoided).
  4. *Topological Modifiers (Exp D):* Bridge activation ($0.80$) altered routes on only two corridors (OD_04: approximately $-645\text{ m}$; OD_15: approximately $-2.15\text{ km}$ physical distance), with 23 of 25 corridors remaining unchanged ($23/25$ zeros); roundabout activation ($0.95$) produced zero route-geometry or physical-distance changes across all 25 corridors ($25/25$ zeros; OD_06 traversed $62.98\text{ m}$).
- **Scientific Guardrails:** Characterize $C_2$ strictly as an empirical corpus-average trade-off knee (supported by corridor breakdown: 8 dominate, 7 dominated, 5 trade-offs, 5 ties), not a globally optimal configuration.

### Paragraph 3: Methodological & Empirical Limitations
- **Target Allocation:** ~60 words
- **Purpose:** Transparently delineate the boundary conditions, unmeasured variables, and methodological constraints of the study.
- **Key Elements to Acknowledge:**
  1. *Corpus & Topology Boundaries:* Evaluated on a single urban network (OpenStreetMap Bengaluru, 308,643 vertices, 740,822 collapsed directed edges) across 25 origin–destination corridors.
  2. *Algorithmic Impedance vs. Travel-Time Measurements:* Configured road impedance and turn penalties are algorithmic weights within the search objective; the current experiments did not collect real-world journey-time measurements, so travel-time reduction has not been experimentally demonstrated.
  3. *Geometric Proxy vs. Safety:* Sharp-turn suppression ($\ge 60^\circ$) serves as a geometric proxy for maneuver complexity and junction exposure, not an empirical measurement of rider safety or accident reduction.
  4. *Lack of Behavioral Validation:* Multipliers reflect heuristic domain engineering rather than calibrated discrete-choice rider preference models.
  5. *Experiment D Objective Costs:* Actual configured search-objective costs for Experiment D were not retained by the evaluation harness; post-hoc standardized production scoring evaluated restored production weights and must not be presented as the actual Experiment D search objective.

### Paragraph 4: Future Research Directions
- **Target Allocation:** ~50 words
- **Purpose:** Propose concrete, technically grounded avenues for extending the research based directly on the identified limitations and the framework's overarching practical objective.
- **Key Elements to Cover:**
  1. *Broader Geographic Validation:* Testing across diverse urban topographies and road network morphologies to evaluate heuristic bounds and parameter transferability.
  2. *Empirical Behavioral Calibration:* Calibrating road weights and penalty tiers against observed two-wheeler GPS trajectories and rider preference surveys.
  3. *Real-World Travel-Time & Traffic Validation:* Collecting real-world journey-time measurements and traffic observations to evaluate whether the framework's intended practical objective of more time-efficient two-wheeler journeys is achieved in practice.
  4. *Vehicle-Specific Constraints:* Incorporating engine displacement limitations, gradient penalties, and dynamic traffic observations into the impedance model.
- **Scientific Guardrails:** Explicitly connect future work to the intended travel-time objective while clearly framing these evaluations as unperformed future research.

---

## 3. Evidence and Numerical Findings Mapping

Every assertion in the proposed Section VII architecture is linked to audited project evidence from Sections III–VI and canonical experimental outputs:

| Topic / Claim | Supporting Evidence / Source Artifact | Audited Canonical Numbers |
| :--- | :--- | :--- |
| **State-Expanded Search Formulation** | `paper1_section_IV_A_draft_v2.md` | State $s = (u, v) \in E_s$, branching factor $\le d_{\max}^{\text{out}}$, exact turn-cost evaluation without auxiliary path memory. |
| **Road-Class-Dependent Impedance Model** | `paper1_section_III_v1.md`, Table I | $f_{\text{class}} \in [0.90, 2.50]$ (residential $0.90$, trunk $2.50$), bridge modifier $0.80$, roundabout modifier $0.95$. |
| **Theorem 1 Conditional Admissibility** | `paper1_section_IV_C_draft_v2.md` | $h(u, v) = \mu_{\min} \cdot \text{hav}(u, d)$ with $\mu_{\min} = 0.80$ is consistent and admissible given graph lower bound $\mu(e) \ge 0.80$. |
| **Bengaluru Graph Bound Verification** | `paper1_section_III_v1.md`, `core/config.py` | 308,643 nodes, 740,822 edges; zero bridge-roundabout co-occurrences; $\mu(e) \ge 0.80$ verified on Bengaluru graph. |
| **Exp A: Turn Reduction** | `statistical_test_results.csv#L2` | $A_0$ vs. $A_1$: $32.52 \to 21.44$ sharp turns ($-34.1\%$, mean diff $-11.08$, Pratt $W=0.0$, $p_{\text{adj}}=4.5 \times 10^{-5}$, $d_z=-1.0066$). |
| **Exp A: Invariance & Measured Runtimes** | `statistical_test_results.csv#L4,L5,L7` | $A_1$ vs. $A_2$ turn test: diff $0.00$, $p_{\text{adj}}=1.000$; geometry $25/25$ zeros; runtime $A_1-A_2$ $+253.38\text{ ms}$, $A_0-A_1$ $+41.35\text{ ms}$. |
| **Exp B: Arterial/Residential Reallocation** | `statistical_test_results.csv#L8,L9` | $B_0$ vs. $B_1$: arterial $-51.21$ pp ($65.05\% \to 13.84\%$, $p_{\text{adj}}=8.4 \times 10^{-5}$); residential $+30.73$ pp ($13.51\% \to 44.24\%$, $p_{\text{adj}}=1.5 \times 10^{-4}$). |
| **Exp B: Physical Detour Trade-off** | `statistical_test_results.csv#L11,L14` | $B_0$ vs. $B_1$ distance: $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}}=6.8 \times 10^{-5}$); $B_0$ vs. $B_2$ arterial share $-45.51$ pp ($p_{\text{adj}}=8.4 \times 10^{-5}$). |
| **Exp C: Monotonic Sensitivity & Knee** | `statistical_test_results.csv#L20-L25` | Sharp turns decline: $C_0=32.52 \to C_1=24.64 \to C_2=21.44 \to C_3=19.80$; $C_2$ captures $87.1\%$ turn reduction; $C_2 \to C_3$ $+19.7\text{ m}$/turn. |
| **Exp C: Corpus Trade-off Knee Designation** | `phase_13_4_freeze_report.md` | Corridor breakdown: $C_2$ dominates on 8, $C_3$ dominates on 7, 5 trade-offs, 5 ties (corpus knee, not global optimum). |
| **Exp D: Bridge Routing Shifts** | `exp_d_corridor_metrics.csv` | Routes changed on only OD_04 ($-645\text{ m}$) and OD_15 ($-2.15\text{ km}$); 23/25 unchanged; $D_3-D_4$ cost diff $+120.92$, $p_{\text{adj}}=0.4722$. |
| **Exp D: Roundabout Invariance** | `exp_d_corridor_metrics.csv`, `stats#L27` | Route and distance $25/25$ zeros; OD_06 traversed $62.98\text{ m}$; post-hoc standardized cost diff $0.00$, Pratt $W=0.0$, $p_{\text{adj}}=1.000$ (outside Table II). |
| **Exp D: Cost Non-Retention** | `phase_8_3_C2_freeze_log.md` | Actual configured search-objective costs not retained; post-hoc standardized production scoring evaluated restored production weights. |

---

## 4. Strict Construct-Validity and Research-Integrity Guardrails

To preserve absolute academic rigor and avoid unverified claims, Section VII architecture and drafting strictly enforce the following boundaries:

1. **Safety Claims:** ZERO assertions of accident reduction, rider safety improvement, hazard elimination, or cognitive comfort. Sharp turns are described strictly as geometric junction-exposure proxies.
2. **Travel-Time Distinction (Three-Part Framework):**
   - *Intended Project Objective:* Travel-time efficiency is recognized as an overarching practical motivation and intended objective of two-wheeler routing. The conclusion may state that the proposed framework is intended to support more time-efficient two-wheeler journeys and that this potential warrants further evaluation.
   - *Current Measured Outcomes:* The current experiments measured static network metrics (street-hierarchy shares, turn counts, physical route distances, and search runtimes). Real-world journey-time measurements were not collected. Therefore, travel-time reduction has NOT been experimentally demonstrated.
   - *Future Validation Required:* Real-world travel-time benefits, dynamic traffic delays, and congestion bypass efficacy are explicitly positioned as requiring future empirical validation with real-world journey-time data.
3. **Behavioral Claims:** ZERO claims that routing weights reflect calibrated or validated rider choice models.
4. **Generalizability Limits:** The $\mu(e) \ge 0.80$ lower bound is explicitly framed as a dataset-verified property of the Bengaluru network, not an unconditional or universal graph property.
5. **Optimality Limits:** Penalty configuration $C_2$ ($25/8\text{ m}$) is described strictly as an empirical corpus-average trade-off knee across the 25 corridors, not a globally optimal configuration.
6. **Cost Impact Limits:** Experiment D is not claimed to demonstrate a measured search-objective cost reduction; non-retention is acknowledged, post-hoc standardized scoring is not conflated with the configured search objective, and post-hoc non-significance is stated neutrally.
7. **Paper Demarcation:** Experiment E, lateral waypoint routing, and alternative path generation are completely excluded (reserved exclusively for Paper 2).

---

## 5. Frozen Manuscript Cryptographic Verification

All ten canonical manuscript sections and preceding freeze logs remain byte-identical:

| Canonical Manuscript Unit | Canonical File Path | Verified SHA-256 Digest | Status |
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

---

## 6. Research Lead Action Requested

The corrected Section VII architecture is complete and ready for your review.

In accordance with Phase 8.4-A-R1 protocol:
- Section VII manuscript prose has **NOT** been drafted.
- No files outside `phase_8_4_A_section_VII_architecture.md` have been modified.
- All previously frozen files remain byte-for-byte identical.

Please review the revised architecture and indicate approval to proceed to Phase 8.4-B (Section VII Manuscript Prose Drafting).
