# Section I: Introduction (Draft: Paragraphs 4–6, v1.1 Revised)

**Document:** [`paper1_introduction_draft_p4_p6_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p4_p6_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Parent Outline:** [`paper1_introduction_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_outline_v1.md)  
**Parent Citation Map:** [`paper1_introduction_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_citation_map_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 5.4.2 REVISED DRAFT (PARAGRAPHS 4–6)**

---

## Section I: Introduction (Prose Text: Paragraphs 4–6)

While transportation route planning has been surveyed extensively regarding metric customization \cite{bast2016route}, two-wheeler studies such as Asvial et al. \cite{asvial2020entropy} have evaluated route suitability by post-hoc re-ranking pre-computed paths. This motivates an integrated routing formulation combining turn-aware state-expanded $A^*$ search with configured two-wheeler road impedance, conditional heuristic correctness guarantees, and controlled metropolitan corridor evaluation on an urban road network.

We present a turn-aware routing framework with configured road impedance. The primary contributions are: (1) formulating online state-expanded search over directed edge states $s=(u, v)$ evaluating discrete angular penalties during edge relaxation; (2) integrating a configured class-dependent road impedance model with a $0.80$ override for qualifying grade-separated main-road segments; (3) establishing conditional admissibility and consistency for a Haversine heuristic scaled by $0.80$ under $\mu(e) \ge 0.80$ and nonnegative turn penalties, satisfying classical $A^*$ optimality requirements \cite{hart1968formal}; and (4) controlled evaluation across 25 corridors on Bengaluru's 744,216-edge network, showing a $34.1\%$ reduction in mean sharp turns (A0 vs. A1: $21.44$ vs. $32.52$) and a $51.21$ percentage-point arterial exposure drop (B0 vs. B1: $13.84\%$ vs. $65.05\%$) with a $15.53\%$ physical route-distance increase ($7.65$ vs. $6.62\text{ km}$).

The remainder of this paper is organized as follows: Section II surveys related work. Section III defines the problem formulation and configured impedance. Section IV presents the turn-aware algorithm, theoretical proofs, and complexity bounds. Section V describes experimental methodology, Section VI evaluates empirical ablations, and Section VII concludes.

---

## Word Count and Budget Analysis

- **Paragraph 4 (Research Gap):** Exactly **59 words** (Target Allocation: ~55–65 words; Delta: $+4$ words vs 55 target).
- **Paragraph 5 (Contributions):** Exactly **124 words** (Target Allocation: ~115 words; Delta: $+9$ words).
- **Paragraph 6 (Paper Organisation):** Exactly **48 words** (Target Allocation: ~45 words; Delta: $+3$ words).
- **Total Paragraphs 4–6 Word Count:** Exactly **231 words** (Target Allocation: ~215 words; Delta: $+16$ words).
- **Frozen Paragraphs 1–3 Word Count:** Exactly **236 words** (Frozen from Phase 5.4.1).
- **Complete Section I Footprint (P1–P6):** $236 + 231 = \mathbf{467\text{ words}}$ (Strictly within the approved $450\text{--}470$ word envelope).

---

*Drafted strictly within the allocated budget of `paper1_final_page_budget_v1.md` and verified under `blrmap-research-protocol` and `evidence-integrity-audit`.*
