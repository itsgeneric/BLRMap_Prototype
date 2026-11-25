# Section I (Paragraphs 4–6) Factual Claim and Evidentiary Audit (v1.1 Revised)

**Document:** [`paper1_introduction_draft_p4_p6_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p4_p6_audit.md)  
**Target Manuscript Draft:** [`paper1_introduction_draft_p4_p6_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p4_p6_v1.md)  
**Parent Outline:** [`paper1_introduction_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_outline_v1.md)  
**Parent Citation Map:** [`paper1_introduction_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_citation_map_v1.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **PHASE 5.4.2 REVISED AUDIT (COMPLETE)**

---

## 1. Sentence-by-Sentence Evidentiary Audit

Every sentence in the revised Paragraphs 4, 5, and 6 is audited below against verified publication sources, architectural blueprints, and frozen Phase 13.4 experimental artifacts.

---

### Paragraph 4: Research Gap (59 Words)

#### Sentence 4.1: Scoped Prior Literature Context
> *"While transportation route planning has been surveyed extensively regarding metric customization \cite{bast2016route}, two-wheeler studies such as Asvial et al. \cite{asvial2020entropy} have evaluated route suitability by post-hoc re-ranking pre-computed paths."*
- **Claim:** Transportation route planning literature surveys metric customization broadly, while two-wheeler routing studies (specifically Asvial et al.) evaluate route suitability by post-hoc re-ranking pre-computed paths.
- **Citation Scope Audit:**
  - `bast2016route` (Bast et al., *Algorithm Engineering*, 2016, DOI: [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2)):
    - *Classification:* **Contextual Survey.**
    - *Correction Applied:* Strictly framed around general route planning and metric customization. Removed previous implication that Bast et al. evaluated the exact combination of turn penalties and two-wheeler road-class impedance.
  - `asvial2020entropy` (Asvial et al., *IJACSA*, 11(7), pp. 438–445, 2020, DOI: [10.14569/IJACSA.2020.0110758](https://doi.org/10.14569/IJACSA.2020.0110758)):
    - *Passage Verification:* Section III-B (pp. 443–444: EBkSP formulation) and Section V-A (pp. 444–445).
    - *Classification:* **Direct Evidence.**
    - *Correction Applied:* Narrowed from broad generalization ("existing two-wheeler approaches frequently evaluate...") to describe specifically the documented method in Asvial et al. (post-hoc Entropy-TOPSIS re-ranking over pre-computed shortest paths without turn costs).
- **Restraint Boundary:** Confined strictly to documented evidence in the cited paper; zero unwarranted generalizations across un-surveyed literature.

#### Sentence 4.2: Scoped Formulation and Evaluation Motivation
> *"This motivates an integrated routing formulation combining turn-aware state-expanded $A^*$ search with configured two-wheeler road impedance, conditional heuristic correctness guarantees, and controlled metropolitan corridor evaluation on an urban road network."*
- **Claim:** The documented approaches motivate an integrated routing formulation combining turn-aware state-expanded $A^*$, configured two-wheeler road impedance, conditional heuristic correctness guarantees, and controlled metropolitan corridor evaluation on an urban road network.
- **Literature Boundary Verification:** 
  - Verified across [`paper1_literature_matrix.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_literature_matrix.csv).
  - Strictly avoids claiming that "limited research", "few studies", or "no studies" exist in the broader literature.
  - Frames the motivation directly around the technical integration and empirical evaluation undertaken in this paper.
  - Preserves the four core architectural elements: turn-aware state-expanded A* search, configured two-wheeler road impedance, conditional heuristic correctness guarantees, and controlled metropolitan corridor evaluation.

---

### Paragraph 5: Objectives and Technical Contributions (124 Words)

#### Sentence 5.1: Opening Framing
> *"We present a turn-aware routing framework with configured road impedance."*
- **Function:** Technical transition using restrained engineering terminology.

#### Contribution (1): Turn-Aware State-Expanded Search
> *"(1) formulating online state-expanded search over directed edge states $s=(u, v)$ evaluating discrete angular penalties during edge relaxation;"*
- **Implementation Source:** [`routing/algorithms.py#L520-L525`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L520-L525) and [`routing/algorithms.py#L658-L677`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L658-L677).
- **Verification:** States are tuples of node IDs `(prev_node, curr_node)` representing directed edge $(u, v) \in E$. Turn cost `_turn_penalty(graph, previous_node, current_node, next_node)` evaluated during edge relaxation without graph preprocessing.

#### Contribution (2): Configured Road-Class Impedance Model & Flyover Override
> *"(2) integrating a configured class-dependent road impedance model with a $0.80$ override for qualifying grade-separated main-road segments;"*
- **Implementation Source:** [`core/config.py#L61-L77`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py#L61-L77) and [`routing/algorithms.py#L309-L311`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L311).
- **Verification:** `TWO_WHEELER_ROAD_PENALTIES` assigns multipliers between $0.90$ and $4.0$. Flyover override assigns `penalty = 0.8` when `is_bridge` is truthy and `hw in MAIN_ROAD_TYPES`.
- **Terminology:** Uses "configured class-dependent road impedance model" strictly.

#### Contribution (3): Conditional Admissibility and Consistency Proofs
> *"(3) establishing conditional admissibility and consistency for a Haversine heuristic scaled by $0.80$ under $\mu(e) \ge 0.80$ and nonnegative turn penalties, satisfying classical $A^*$ optimality requirements \cite{hart1968formal};"*
- **Theoretical Source:** [`phase_3_3_corrected_mathematical_claims.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_3_corrected_mathematical_claims.md) (Theorems 1 & 2).
- **Citation Key Audit (`hart1968formal`):**
  - *Full Reference:* Hart, Nilsson, & Raphael, *IEEE Trans. Syst. Sci. Cybern.*, 1968.
  - *Classification:* **Foundational Theoretical Context.**
  - *Correction Applied:* Hart et al. (1968) is cited strictly for establishing the classical $A^*$ optimality foundations (that admissibility and monotonicity ensure optimal path finality without state reopening). The conditional derivation under $\mu(e) \ge 0.80$ and $P_{\text{turn}} \ge 0$ is explicitly framed as **this paper's own derivation**.
- **Verification:** Network audit across all 744,216 directed edges in [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) confirms $\min \mu(e) = 0.8000$.

#### Contribution (4): Controlled Empirical Evaluation on Bengaluru Road Network
> *"(4) controlled evaluation across 25 corridors on Bengaluru's 744,216-edge network, showing a $34.1\%$ reduction in mean sharp turns (A0 vs. A1: $21.44$ vs. $32.52$) and a $51.21$ percentage-point arterial exposure drop (B0 vs. B1: $13.84\%$ vs. $65.05\%$) with a $15.53\%$ physical route-distance increase ($7.65$ vs. $6.62\text{ km}$)."*
- **Experimental Ground-Truth Sources:**
  - Network scale: [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) ($|V| = 308,643$, $|E| = 744,216$ directed edges).
  - Corridor count: [`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json) ($N = 25$ OD pairs).
  - Turn reduction: [`statistical_test_results.csv#Row-2`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L2) ($32.52 \to 21.44$, $-11.08$ turns, $-34.0713\% \approx -34.1\%$, Pratt $W = 0.0$, $p_{\text{adj}} = 4.5 \times 10^{-5}$).
  - Arterial exposure drop: [`statistical_test_results.csv#Row-11`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L11) ($65.0524\% \to 13.8376\%$, $-51.2148\text{ pp} \approx -51.21\text{ pp}$, Pratt $W = 4.0$, $p_{\text{adj}} = 8.4 \times 10^{-5}$).
  - Physical distance increase: [`statistical_test_results.csv#Row-17`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L17) ($6.6196\text{ km} \to 7.6475\text{ km}$, $+1.0279\text{ km}$, $+15.5287\% \approx +15.53\%$, Pratt $W = 7.0$, $p_{\text{adj}} = 6.8 \times 10^{-5}$).
- **Verification:** All four quantitative findings match frozen artifacts to the exact decimal place.
- **Construct Boundary:** Distinguishes physical route distance from impedance cost. Completely avoids claiming safety improvements, travel-time savings, congestion reduction, or rider preference validation.

---

### Paragraph 6: Paper Organisation Roadmap (48 Words)

#### Sentence 6.1: Section Sequence and Contents
> *"The remainder of this paper is organized as follows: Section II surveys related work. Section III defines the problem formulation and configured impedance. Section IV presents the turn-aware algorithm, theoretical proofs, and complexity bounds. Section V describes experimental methodology, Section VI evaluates empirical ablations, and Section VII concludes."*
- **Blueprint Alignment:** Unchanged from approved draft. Matches [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md) exactly.

---

## 2. Granular Citation-Scope Audit for Specific References

### 2.1. Bast et al. (2016) — *Algorithm Engineering*
- **Full Reference:** H. Bast et al., "Route Planning in Transportation Networks," in *Algorithm Engineering: Selected Results and Surveys*, LNCS 9220, Springer, 2016, pp. 19–80. DOI: [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2).
- **Audited Scope:** Broad survey covering shortest-path speedup techniques, turn-cost modeling, and multi-metric customization trade-offs across transportation networks.
- **Correction Applied:** Bast et al. is cited strictly as a general survey of transportation route planning and metric customization. It is **not** cited as evidence that the specific combination of turn penalties and two-wheeler road-class impedance has been investigated.

### 2.2. Asvial et al. (2020) — *IJACSA*
- **Full Reference:** M. Asvial, M. F. G. Pandoyo, and A. S. Arifin, "Entropy-Based k Shortest-Path Routing for Motorcycles: A Simulated Case Study in Jakarta," *IJACSA*, vol. 11, no. 7, pp. 438–445, 2020. DOI: [10.14569/IJACSA.2020.0110758](https://doi.org/10.14569/IJACSA.2020.0110758).
- **Audited Scope:** Section III-B (pp. 443–444) and Section V-A (pp. 444–445). The authors generate $k$-shortest paths using standard algorithms with turn cost $=0$, and then apply an Entropy-TOPSIS multi-criteria re-ranking algorithm over those pre-computed paths.
- **Correction Applied:** Narrowed to refer specifically to Asvial et al.'s documented post-hoc re-ranking methodology. Purged the broad statement that "existing two-wheeler approaches frequently evaluate route attributes through post-hoc re-ranking".

### 2.3. Hart, Nilsson, & Raphael (1968) — *IEEE Trans. Syst. Sci. Cybern.*
- **Full Reference:** P. E. Hart, N. J. Nilsson, and B. Raphael, "A Formal Basis for the Heuristic Determination of Minimum Cost Paths," *IEEE Trans. Syst. Sci. Cybern.*, vol. SSC-4, no. 2, pp. 100–107, 1968. DOI: [10.1109/TSSC.1968.300136](https://doi.org/10.1109/TSSC.1968.300136).
- **Audited Scope:** Foundational mathematical proofs that an admissible ($h \le h^*$) and monotonically consistent heuristic guarantees that A* expands nodes in optimal order without requiring state reopening.
- **Correction Applied:** Clarified that the conditional admissibility and consistency proof for the $0.80$-scaled Haversine heuristic under $\mu(e) \ge 0.80$ and $P_{\text{turn}} \ge 0$ is **this paper's own derivation**. Hart et al. (1968) is cited strictly for the classical $A^*$ optimality requirements that this paper's derivation satisfies.

---

## 3. Summary Audit Checklist

| Audit Question | Audit Verdict | Evidence / Verification Note |
| :--- | :---: | :--- |
| **Total Section I Footprint in budget?** | **YES** | Exactly **467 words** (Approved Envelope: $450\text{--}470$ words). |
| **Paragraph 4 within budget?** | **YES** | Exactly **59 words** (Target Allocation: ~55–65 words). |
| **Paragraph 5 within budget?** | **YES** | Exactly **124 words** (Target Allocation: ~115 words). |
| **Paragraph 6 within budget?** | **YES** | Exactly **48 words** (Target Allocation: ~45 words). |
| **Broad research landscape claim avoided?** | **YES** | Removed "limited empirical research"; framed directly around this paper's motivation and integrated evaluation. |
| **Asvial et al. narrowed from generalization?** | **YES** | Confined strictly to Asvial et al.'s documented post-hoc re-ranking approach. |
| **Bast et al. restricted to general survey role?** | **YES** | Scoped strictly to general route planning and metric customization context. |
| **Hart et al. cited as foundation, not derivation?** | **YES** | Proof framed as this paper's own derivation satisfying classical A* conditions. |
| **All 4 numerical experimental results exact?** | **YES** | $-34.1\%$ turns, $-51.21\text{ pp}$ arterial, $+15.53\%$ distance ($7.65$ vs. $6.62\text{ km}$), 25 corridors, 744,216 edges. Exact match. |
| **Zero safety / accident / travel time claims?** | **YES** | 0 occurrences of prohibited claim types. |
| **Paper 2 alternative routing excluded?** | **YES** | Zero mention of alternative routes, Yen algorithm, or diversity. |

---

*Factual claim audit verified and completed under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
