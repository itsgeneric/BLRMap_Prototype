# Phase 5.3 — Introduction Planning Log (v1.2 Approved)

**Document:** [`phase_5_3_planning_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_3_planning_log.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE PHASE 5.3.2 LOG**

---

## 1. Summary of Phase 5.3.2 Final Directives and Actions

Following the research lead's structural approval in Phase 5.3.2, three final refinements were incorporated into the Introduction planning artifacts:

1. **Paragraph 2 State-Representation Wording Refinement:**
   - *Previous Phrasing:* Asserted that vertex-only routing "violates Bellman's subpath optimality".
   - *Refined Phrasing:* Replaced with the mathematically precise explanation that a vertex-only state representation is insufficient to encode incoming-edge-dependent transition costs, and that retaining arrival-edge context—such as representing search states as directed edge states $s=(u,v)$—resolves this state-representation limitation.
   - *Outcome:* Prevents overbroad mathematical assertions while clearly framing the graph-theoretic state-space requirement.

2. **Paragraph 4 Narrowly Scoped Research Gap:**
   - *Refined Phrasing:* Kept the research gap strictly focused on the systematic integration of:
     - Turn-aware state-expanded $A^*$;
     - Configured two-wheeler-oriented road-class impedance;
     - Conditional heuristic admissibility and consistency proofs; and
     - Controlled metropolitan corridor-level empirical evaluation.
   - *Outcome:* Strictly avoids claiming that this is the "first" or "only" framework, or that it has "never been attempted."

3. **Granular Citation Traceability Passages:**
   - Added exhaustive passage-level and section-level documentation in [`paper1_introduction_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_citation_map_v1.md) for:
     - **Winter (2002):** Section 3 (pp. 348–352: dual line graph transformation); Section 4 (pp. 353–356: node-pair state expansion in Dijkstra); Section 5 (pp. 357–359: turn penalty elimination of zig-zag routes).
     - **Geisberger and Vetter (2011):** Section 3 (pp. 102–105: edge-based CH formulation); Section 4 (pp. 105–108: junction turn tables and shortcut construction); Section 5 (pp. 108–110: European road network benchmarks and preprocessing overhead).
     - **Asvial et al. (2020):** Section III-A (pp. 441–443: narrow road prioritization); Section III-B (pp. 443–444: EBkSP algorithm formulation with post-hoc Entropy-TOPSIS ranking); Section V-A (pp. 444–445: 6 OD corridor simulations confirming turn cost $= 0$).

---

## 2. Word Budget Compliance Verification

The revised allocation strictly matches the mandated 450-word budget across the six paragraphs:

| Paragraph | Topic Focus | Target Words | Status |
| :---: | :--- | :---: | :---: |
| **P1** | Urban Two-Wheeler Context & Operating Setting | 70 words | **Compliant** |
| **P2** | Routing Formulation & State-Representation Limits | 80 words | **Compliant** |
| **P3** | Prior Work: Line Graphs, Turn CH & Road Models | 85 words | **Compliant** |
| **P4** | Scoped Research Gap: Architectural & Empirical Integration | 55 words | **Compliant** |
| **P5** | Research Objectives & 4 Itemized Contributions | 115 words | **Compliant** |
| **P6** | Paper Organization Roadmap | 45 words | **Compliant** |
| **TOTAL** | **Section I Target Word Budget** | **450 words** | **Exactly 450 words** |

---

## 3. Deliverables Status and Stop Condition Compliance

All three Section I planning documents are finalized in `research/paper1_manuscript/`:
1. [`paper1_introduction_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_outline_v1.md) — Structural outline incorporating all final corrections.
2. [`paper1_introduction_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_citation_map_v1.md) — Comprehensive citation map with granular page/section citations for Winter (2002), Geisberger & Vetter (2011), and Asvial et al. (2020).
3. [`phase_5_3_planning_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_3_planning_log.md) — Authoritative audit log.

**Stop Condition Compliance:**
- No Introduction prose has been drafted.
- Frozen abstract v2.0 remains untouched.
- Frozen experimental datasets, figures, and bibliography remain untouched.
- Section II has not been opened.
- Phase 5.3 is fully planned and ready for prose drafting upon authorization.
