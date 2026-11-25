# Paper 1 Introduction Structural Outline (v1.2 Approved Plan)

**Document:** [`paper1_introduction_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_outline_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Allocated Budget:** Exactly 450 Words (Page 1, Column 1 Bottom & Column 2 Top)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **PHASE 5.3.2 FINAL APPROVED ARCHITECTURAL PLAN**

---

## 1. Structural Overview and Word Budget Allocation

The Introduction is organized into a cohesive six-paragraph narrative strictly allocated to **450 words**. This revised plan incorporates all Phase 5.3.2 final directives: framing the state-representation constraint without asserting subpath optimality violations, scoping the research gap strictly around unified integration without novelty overclaiming, and verifying citation passages.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                   SECTION I: FINAL INTRODUCTION STRUCTURAL SEQUENCE                     │
├───────────┬─────────────────────────────────────────────────────────────┬───────────────┤
│ Paragraph │ Thematic Focus                                              │ Word Budget   │
├───────────┼─────────────────────────────────────────────────────────────┼───────────────┤
│ Para 1    │ Urban Two-Wheeler Routing Context & Operational Environment │ 70 words      │
│ Para 2    │ Routing Formulation: Vertex State Limits & Arrival Context  │ 80 words      │
│ Para 3    │ Prior Work: Edge Expansion, Turn-Aware CH & Road Weighting  │ 85 words      │
│ Para 4    │ The Scoped Research Gap: Architectural & Empirical Synthesis│ 55 words      │
│ Para 5    │ Research Objectives and 4 Itemized Technical Contributions  │ 115 words     │
│ Para 6    │ Paper Organization and Document Roadmap                     │ 45 words      │
├───────────┴─────────────────────────────────────────────────────────────┼───────────────┤
│ TOTAL SECTION I WORD BUDGET                                             │ 450 words     │
└─────────────────────────────────────────────────────────────────────────┴───────────────┘
```

---

## 2. Paragraph-by-Paragraph Detailed Outline

### Paragraph 1: Urban Two-Wheeler Routing Context and Operational Environment (Budget: 70 words)
- **Thematic Function:** Introduces the urban transportation context and routing operational setting of powered two-wheelers.
- **Core Narrative:**
  - In dense South and Southeast Asian metropolitan road networks, powered two-wheelers constitute a dominant mode of passenger transport.
  - Two-wheelers navigate through heterogeneous mixed-traffic conditions across diverse street classes, operating alongside commercial, public, and private four-wheeled vehicles.
  - Metropolitan road networks, such as Bengaluru, experience recurrent arterial congestion and high corridor travel-time variability.
  - Conventional routing engines rely on automobile-oriented assumptions, providing paths that frequently fail to reflect the operational characteristics of two-wheeler movement across mixed road networks.
- **Construct Validity & Restraint Boundary:** Avoids unsupported assertions about traffic filtering benefits, congestion reduction, collision vulnerability, or rider psychology. Cites traffic composition and urban congestion strictly as documented operating context.
- **Target Citations:** `promraksa2022lane` [1], `kotagi2020modeling` [2], `kumar2025realtime` [16].

---

### Paragraph 2: Routing Formulation: Vertex State Limits and Arrival Context (Budget: 80 words)
- **Thematic Function:** Formulates the mathematical limitation of vertex-only search states when evaluating turn-dependent transition costs.
- **Core Narrative:**
  - Standard shortest-path algorithms typically formulate search over vertex-based road graphs $G=(V, E)$, tracking search states solely as physical vertices $v \in V$.
  - However, when transition costs depend on vehicular heading changes or turn angles, a vertex-only state representation is insufficient to encode incoming-edge-dependent transition costs.
  - Because the cost of traversing a successor edge $(v, w)$ depends on the specific incoming edge $(u, v)$ or arrival heading at intersection $v$, assigning scalar costs solely to vertices cannot distinguish between different arrival directions.
  - Retaining arrival-edge context—such as representing search states as directed edge states $s=(u, v)$—resolves this state-representation limitation by preserving the directional context required to evaluate discrete angular heading penalties during edge relaxation.
- **Construct Validity & Restraint Boundary:** Explicitly replaces any claim of "subpath optimality violations" with a precise formulation of state-representation insufficiency. Does not claim vertex-based algorithms are universally incapable of handling turns, but shows that edge context must be retained.
- **Target Citations:** `winter2002modeling` [6] (Sec. 3–4, pp. 348–356), `luxen2011realtime` [4], `das2019modeling` [3].

---

### Paragraph 3: Prior Work: Edge Expansion, Turn-Aware CH, and Road Weighting (Budget: 85 words)
- **Thematic Function:** Acknowledges established techniques in turn modeling, speedup hierarchies, and vehicle-specific routing, clearly separating them from this work.
- **Core Narrative:**
  - Edge-expanded networks and line-graph state spaces have a long history in traffic assignment and route planning for modeling turn prohibitions and delays (Kirby & Potts, 1969; Winter, 2002).
  - Advanced speedup techniques, notably Contraction Hierarchies, have been extended to incorporate turn costs through turn-expanded nodes and static shortcut construction (Geisberger & Vetter, 2011).
  - In parallel, customizable routing approaches address multi-metric road weighting (Delling et al., 2017; Bast et al., 2016), and empirical studies observe that two-wheeler riders utilize lower-tier street classes differently than passenger cars (Fadilah et al., 2024).
  - However, pre-computed shortcut hierarchies introduce preprocessing overhead when exploring non-standard, vehicle-specific turn-angle thresholds and multi-tiered road impedance combinations.
- **Construct Validity & Restraint Boundary:** Fully credits Kirby, Winter, and Geisberger & Vetter. Explicitly avoids describing Contraction Hierarchies as universally rigid or incapable of turn costs. Distinguishes our online, uncontracted state-expanded A* approach.
- **Target Citations:** `kirby1969minimum` [5], `winter2002modeling` [6], `geisberger2011efficient` [7] (Sec. 3–4, pp. 102–108), `fadilah2024identifying` [10], `bast2016route` [9].

---

### Paragraph 4: The Scoped Research Gap (Budget: 55 words)
- **Thematic Function:** Defines the narrow, evidence-supported research gap addressed by this paper.
- **Core Narrative:**
  - While turn penalties, heuristic search, and road-class weighting have been investigated individually, there is limited literature examining their unified integration and controlled empirical evaluation within a single online framework.
  - Specifically, two-wheeler routing studies frequently rely on post-hoc multi-attribute re-ranking of pre-computed paths (e.g., Asvial et al., 2020) rather than integrating turn penalties and road-class impedance directly into graph search.
  - A systematic integration combining turn-aware state-expanded $A^*$, a configured two-wheeler road impedance model, formal heuristic consistency arguments, and corridor-level empirical evaluation on a metropolitan network remains unaddressed.
- **Construct Validity & Restraint Boundary:** Strictly avoids claiming that this combination is the "first" or "only" framework, or that it has "never been attempted." Focuses squarely on the documented empirical gap between post-hoc re-ranking and integrated search.
- **Target Citations:** `asvial2020entropy` [11] (Sec. III-B & V-A, pp. 443–446), `bast2016route` [9].

---

### Paragraph 5: Research Objectives and Itemized Technical Contributions (Budget: 115 words)
- **Thematic Function:** Formulates the four verified contributions of the paper using restrained, approved terminology.
- **Core Narrative:**
  This paper presents a turn-aware routing framework that couples state-expanded $A^*$ search with a configured class-dependent road impedance model on metropolitan road networks. The primary contributions are:
  1. *Turn-Aware State-Expanded Search:* We formulate an online $A^*$ search over directed edge states $s=(u,v)$, evaluating discrete angular heading penalties directly during edge relaxation on uncontracted directed multigraphs without preprocessing.
  2. *Configured Road-Class Impedance Model:* We integrate a configured class-dependent road impedance model that weights major arterials relative to local streets, incorporating a $0.80$ override for qualifying grade-separated main-road segments.
  3. *Conditional Admissibility and Consistency Proof:* We formally prove that a Haversine heuristic scaled by $0.80$ is admissible and consistent when composite edge multipliers satisfy $\mu(e) \ge 0.80$ and turn penalties are nonnegative, ensuring optimal state finality without state reopening.
  4. *Controlled Metropolitan Evaluation:* We conduct a controlled ablation across 25 origin–destination corridors on Bengaluru's 744,216-edge network, demonstrating that turn awareness reduces mean sharp turns by $34.1\%$ ($32.52 \to 21.44$, $p_{\text{adj}} = 4.5\times 10^{-5}$) and configured impedance reduces arterial exposure by $51.21\text{ pp}$ ($65.05\% \to 13.84\%$, $p_{\text{adj}} = 8.4\times 10^{-5}$) at a $+15.53\%$ physical distance trade-off ($7.65$ vs. $6.62\text{ km}$) relative to neutral road-class impedance.
- **Construct Validity & Restraint Boundary:** Uses "configured class-dependent road impedance model" strictly. Completely excludes claims of safety, accident reduction, congestion reduction, travel-time savings, or rider preference validation.
- **Target Citations:** `hart1968formal` [13].

---

### Paragraph 6: Paper Organization Roadmap (Budget: 45 words)
- **Thematic Function:** Provides a structural roadmap for the remaining sections.
- **Core Narrative:**
  - Section II reviews related work on turn-cost modeling and two-wheeler route planning.
  - Section III establishes the problem formulation and configured impedance models.
  - Section IV details the turn-aware algorithm, formal heuristic proofs, and complexity bounds.
  - Section V describes the experimental setup and benchmark corpus.
  - Section VI analyzes empirical ablation results across the 25 metropolitan corridors.
  - Section VII discusses limitations and concludes the paper.
- **Target Citations:** None required.

---

## 3. Formatting and Float Budget Summary

- **Publication Figures:** 0 (Figures start in Section VI).
- **Publication Tables:** 0 (Table I placed in Section III).
- **Display Equations:** 0 (Equations placed in Sections III and IV).
- **Total Word Budget:** Exactly 450 words ($70 + 80 + 85 + 55 + 115 + 45$).
- **Allocated Layout:** Page 1, Column 1 Bottom and Column 2 Top.
