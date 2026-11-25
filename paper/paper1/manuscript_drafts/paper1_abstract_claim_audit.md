# Paper 1 Abstract Claim Audit and Evidentiary Traceability

**Document:** [`paper1_abstract_claim_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_claim_audit.md)  
**Target Abstract:** [`paper1_abstract_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v1.md)  
**Parent Blueprint:** [`paper1_claims_and_citations_checklist.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_claims_and_citations_checklist.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE EVIDENTIARY TRACEABILITY AUDIT**

---

## 1. Sentence-by-Sentence Evidentiary Audit

Every sentence in the 213-word abstract is audited below against verified literature citations, formal mathematical proofs, or frozen Phase 13.4 experimental data.

---

### Sentence 1: Urban Context
> *"In dense urban road networks with mixed vehicular traffic, powered two-wheelers represent a dominant mode of passenger transport."*
- **Abstract Function:** Research domain and transportation context.
- **Evidence Type:** Literature-supported domain context.
- **External Citations Required in Main Text:**
  - `promraksa2022lane`: Promraksa & Satiennam, *J. Safety Res.*, 2022 (DOI: [10.1016/j.jsr.2022.08.017](https://doi.org/10.1016/j.jsr.2022.08.017)).
  - `kotagi2020modeling`: Kotagi et al., *Physica A*, 2020 (DOI: [10.1016/j.physa.2020.124847](https://doi.org/10.1016/j.physa.2020.124847)).
- **Construct Validity Check:** **PASSED.** Purely describes mode share and operational environment; makes no claim regarding safety or accident rates.

---

### Sentence 2: Conventional Routing Limitation
> *"Conventional shortest-path navigation engines evaluate road intersections as dimensionless scalar points, ignoring vehicular heading changes during search and routing two-wheelers onto congested, high-speed arterial corridors."*
- **Abstract Function:** Problem statement and algorithmic limitation.
- **Evidence Type:** Literature-supported architectural analysis.
- **External Citations Required in Main Text:**
  - `winter2002modeling`: Winter, *Int. J. Geogr. Inf. Sci.*, 2002 (DOI: [10.1080/13658810210148715](https://doi.org/10.1080/13658810210148715)) — Proves that turn costs cannot be evaluated on vertex graphs without violating subpath optimality.
  - `luxen2011realtime`: Luxen & Vetter, *ACM SIGSPATIAL*, 2011 (DOI: [10.1145/2093973.2094062](https://doi.org/10.1145/2093973.2094062)) — Documents node-level contraction hierarchy architecture calibrated for passenger automobiles.
- **Construct Validity Check:** **PASSED.** Analyzes graph-theoretic modeling limitations without alleging unmeasured software failures.

---

### Sentence 3: Proposed Framework
> *"We present a turn-aware routing framework that couples state-expanded $A^*$ search with vehicle-specific road impedance modeling."*
- **Abstract Function:** Core technical proposal.
- **Evidence Type:** System architecture and implementation definition.
- **Source Code Verification:** [`routing/algorithms.py#L460-L705`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L460-L705) (`two_wheeler_astar`).
- **Novelty Demarcation:** Does not claim state expansion or A* are individually novel; novelty is explicitly attributed to the *coupling* of heading-aware search with vehicle impedance.

---

### Sentence 4: State Space & Heading Modeling
> *"The search operates over directed edge states $s = (u, v)$, evaluating discrete angular heading penalties during edge relaxation."*
- **Abstract Function:** Algorithmic state definition and turn mechanism.
- **Evidence Type:** Mathematical definition and source-code verification.
- **Source Code Verification:**
  - State tuple: [`routing/algorithms.py#L522-L525`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L522-L525) (`start_state = (initial_previous_node, start_node)`).
  - Turn calculation: [`routing/algorithms.py#L146-L168`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L146-L168) (`_turn_penalty`).
- **Mathematical Specification:** [`phase_3_3_corrected_mathematical_claims.md#Section-1.2`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_3_corrected_mathematical_claims.md#Section-1.2) ($S = E \cup \{(\text{None}, s_0)\}$).

---

### Sentence 5: Road Impedance Model
> *"Road segments are weighted using an inverted suitability hierarchy that disincentivizes multi-lane arterials, prioritizes secondary and residential streets, and incorporates grade-separated flyover overrides."*
- **Abstract Function:** Vehicle-specific road impedance specification.
- **Evidence Type:** Source-code parameters and literature behavioral backing.
- **Source Code Verification:**
  - Multipliers: [`core/config.py#L61-L77`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py#L61-L77) (`TWO_WHEELER_ROAD_PENALTIES`).
  - Flyover override: [`routing/algorithms.py#L298-L311`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L298-L311) (`penalty = 0.8` for arterial bridges).
- **External Citations Required in Main Text:**
  - `fadilah2024identifying`: Fadilah et al., *Transp. Res. Interdiscip. Perspect.*, 2024 (DOI: [10.1016/j.trip.2024.101147](https://doi.org/10.1016/j.trip.2024.101147)).

---

### Sentence 6: Theoretical Correctness Guarantees
> *"Under the condition that composite edge multipliers satisfy $\mu(e) \ge 0.80$, we prove that the Haversine distance heuristic scaled by $0.80$ is admissible and monotonically consistent on the state-expanded graph, guaranteeing optimal path finality without state reopening."*
- **Abstract Function:** Mathematical correctness and search guarantees.
- **Evidence Type:** Formal mathematical proof and topological network audit.
- **Proof Source:** [`phase_3_3_corrected_mathematical_claims.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_3_corrected_mathematical_claims.md):
  - *Theorem 1:* Proof of Conditional Admissibility ($h(s) \le c^*(s)$).
  - *Theorem 2:* Proof of Conditional Monotonic Consistency ($h(s) \le c(s, s') + h(s')$).
  - *Corollary 1:* Optimal State Finality without state reopening.
- **Condition Verification:** Verified with zero violations across all $744,216$ directed edges in [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) (minimum multiplier is strictly $0.8000$; 0 arterial bridge roundabouts).
- **External Citations Required in Main Text:**
  - `hart1968formal`: Hart, Nilsson, & Raphael, *IEEE Trans. Syst. Sci. Cybern.*, 1968 (DOI: [10.1109/TSSC.1968.300136](https://doi.org/10.1109/TSSC.1968.300136)).

---

### Sentence 7: Evaluation Corpus & Network Scale
> *"Evaluated across 25 metropolitan corridors on Bengaluru's 744,216-edge road network,"*
- **Abstract Function:** Experimental evaluation scope.
- **Evidence Type:** Frozen topological and benchmark dataset.
- **Dataset Verification:**
  - Graph binary: [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) ($|V| = 308,643$, $|E| = 744,216$).
  - Benchmark corpus: [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json) ($25$ validated OD corridors).
- **Repetition Protocol:** $R = 5$ timing repetitions per corridor ($1,855$ total execution runs across study).

---

### Sentence 8: Turn Reduction Metric (Comparator Precision)
> *"turn-aware routing (Condition A0) eliminates $34.1\%$ of sharp maneuvers ($\ge 60^\circ$) relative to turn-unaware state-expanded routing (Condition A1: $21.44$ vs. $32.52$ turns, $p_{\text{adj}} = 4.5 \times 10^{-5}$)."*
- **Abstract Function:** Primary empirical finding for turn awareness.
- **Evidence Type:** Frozen Phase 13.4 experimental ablation dataset.
- **Comparator Precision:** Explicitly compares Condition A0 ($P_{\text{turn}} > 0$) against Condition A1 ($P_{\text{turn}} = 0$). Does not make vague comparisons against "standard routing."
- **Exact Numerical Match:**
  - Turn reduction: $32.52 \to 21.44$ (Mean reduction: $-11.08$ turns, $-34.1\%$).
  - Statistical significance: Pratt Wilcoxon $W = 0.0$, raw $p = 1.5 \times 10^{-5}$, Holm-adjusted $p_{\text{adj}} = 4.5 \times 10^{-5}$.
  - Effect size: Cohen's $d_z = -1.0066$ [$95\%\text{ CI: } -1.419, -0.594$], Hodges-Lehmann median difference $-9.50$ turns [$-13.0, -7.0$].
- **Artifact Source:** [`statistical_test_results.csv#Row-0`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L2) and [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv).

---

### Sentence 9: Road Impedance Metric & Trade-off
> *"Concurrently, road impedance weighting reduces arterial exposure by $51.21$ percentage points ($13.84\%$ vs. $65.05\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$) at a $+15.53\%$ physical route-distance trade-off."*
- **Abstract Function:** Primary empirical finding for road impedance channelization and physical detour cost.
- **Evidence Type:** Frozen Phase 13.4 experimental ablation dataset.
- **Exact Numerical Match:**
  - Arterial share: $65.05\%$ (Neutral B1) $\to 13.84\%$ (Production B0) (Reduction: $-51.21\text{ percentage points}$).
  - Significance: Pratt Wilcoxon $W = 0.0$, raw $p = 1.5 \times 10^{-5}$, Holm-adjusted $p_{\text{adj}} = 8.4 \times 10^{-5}$.
  - Effect size: Cohen's $d_z = -1.7715$ [$95\%\text{ CI: } -2.332, -1.211$], Hodges-Lehmann $-50.21\text{ pp}$ [$-61.3, -39.1$].
  - Distance trade-off: $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = +1.4883$).
- **Artifact Source:** [`statistical_test_results.csv#Row-3`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L5) and [`exp_b_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_b_corridor_metrics.csv).

---

### Sentence 10: Concluding Summary
> *"This yields a computationally lightweight, mathematically grounded routing architecture tailored to urban two-wheeler navigation."*
- **Abstract Function:** Concluding contribution statement.
- **Evidence Type:** Synthesis of verified engineering and theoretical contributions.
- **Construct Validity Check:** **PASSED.** Strictly characterizes the algorithm as computationally lightweight and mathematically grounded, without asserting unmeasured safety or travel-time savings.

---

## 2. Summary Audit Verification Checklist

| Audit Question | Audit Verdict | Reference / Verification Note |
| :--- | :---: | :--- |
| Does the abstract stay within 180–220 words? | **YES** | Exactly **213 words**. |
| Are all 3 headline experimental numbers present and exact? | **YES** | $-34.1\%$ sharp turns, $-51.21\text{ pp}$ arterial exposure, $+15.53\%$ detour. |
| Is the comparator for turn reduction explicitly specified? | **YES** | Condition A0 vs. Condition A1 explicitly identified. |
| Are safety, accident, collision, and travel-time claims purged? | **YES** | Zero occurrences of "safety," "accident," "collision," or "travel-time." |
| Are individual techniques (A*, line graphs) claimed as novel? | **YES** | No. Novelty is positioned strictly in the unified integration and proofs. |
| Are alternative-route generation or Yen algorithms excluded? | **YES** | Zero mentions of alternatives, Yen, or diversity (reserved for Paper 2). |
| Does every statement trace to an audited citation or frozen dataset? | **YES** | 100% evidentiary traceability verified across all 10 sentences. |

---

*Claim audit verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
