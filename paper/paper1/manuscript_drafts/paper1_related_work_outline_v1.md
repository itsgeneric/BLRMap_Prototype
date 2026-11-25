# Section II: Related Work Outline and Structural Plan (v1.1 Refined)

**Document:** [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md) (Allocated: **340 words**)  
**Companion Documents:** [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md), [`phase_6_1_planning_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_6_1_planning_audit.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 6.1.1 REFINED PLANNING OUTLINE (AWAITING LEAD APPROVAL)**  

---

## 1. Executive Structural Overview & Record of Changes

### 1.1. Record of Changes from v1.0 (Phase 6.1.1 Refinement)
1. **Area II-A (Turn-Aware Representations):** Removed repetition of the scalar vertex-state limitation already introduced in Section I. Focused squarely on the scholarly progression: historical movement-expanded networks for traffic assignment (Kirby & Potts, 1969), dual line graphs (Winter, 2002), turn prohibitions, and the progression to online label-setting shortest-path algorithms.
2. **Area II-B (Hierarchical Routing & Customization):** Purged all statements implying that hierarchical methods are universally rigid or that uncontracted search is superior. Accurately framed Customizable Route Planning (Delling et al., 2017) and customizable hierarchies (Bast et al., 2016) as supporting fast metric customization. Positioned uncontracted search strictly as an alternative engineering trade-off for dynamic, localized cost modifications.
3. **Area II-C (Two-Wheeler Impedance):** Explicitly partitioned literature into four non-overlapping categories: (i) empirical traffic flow (Kotagi et al., Promraksa et al.); (ii) empirical rider street usage (Fadilah et al.); (iii) motorcycle routing and post-hoc re-ranking (Asvial et al.); and (iv) our configured heuristic road impedance model. Prohibited any implication that empirical choice studies validate our specific numerical weights.
4. **Area II-D (Positioning & Citations):** Re-evaluated citations: dropped `hart1968formal` (relocated to Section IV theoretical analysis) and `goldberg2005computing` (landmark ALT not relevant to this work). Retained `zografos2004heuristic` strictly for comparing multi-objective routing on edge-expanded graphs. Structured the synthesis around established methods vs. this paper's specific integration and controlled evaluation.
5. **Typographic Style:** Formally confirmed the recommendation of four bold run-in paragraph headers (`\noindent\textbf{...:}`) to eliminate the 10-line vertical penalty of `\subsection` commands.

---

### 1.2. Section II Structural Architecture (340 Words Total)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        SECTION II REFINED STRUCTURAL ALLOCATION                         │
├────────┬─────────────────────────────────────────────┬────────────┬─────────────────────┤
│ Area   │ Thematic Scope                              │ Word Target│ Retained Citations  │
├────────┼─────────────────────────────────────────────┼────────────┼─────────────────────┤
│ II-A   │ Movement-Expanded & Turn-Aware Routing      │   ~90 words│ Kirby & Potts (1969)│
│        │ • Historical movement-expanded assignments  │            │ Winter (2002)       │
│        │ • Dual line graphs & edge-state transitions │            │                     │
│        │ • Prohibitions, penalties & online search   │            │                     │
├────────┼─────────────────────────────────────────────┼────────────┼─────────────────────┤
│ II-B   │ Hierarchical Routing & Metric Customization │   ~80 words│ Luxen & Vetter (2011│
│        │ • Contraction Hierarchies & turn tables     │            │ Geisberger (2011)   │
│        │ • Customizable Route Planning (CRP / CCH)   │            │ Delling et al. (2017│
│        │ • Preprocessing vs. query customization     │            │ Bast et al. (2016)  │
├────────┼─────────────────────────────────────────────┼────────────┼─────────────────────┤
│ II-C   │ Two-Wheeler Routing & Road-Class Impedance  │   ~95 words│ Promraksa (2022)    │
│        │ • Mixed-traffic flow & lane filtering       │            │ Kotagi et al. (2020)│
│        │ • Empirical lower-tier street utilization   │            │ Fadilah et al. (2024│
│        │ • Post-hoc ranking vs. in-search impedance  │            │ Asvial et al. (2020)│
├────────┼─────────────────────────────────────────────┼────────────┼─────────────────────┤
│ II-D   │ Research Positioning & Synthesis            │   ~75 words│ Zografos (2004)     │
│        │ • Prior capabilities & multi-criteria art   │            │ Kumar et al. (2025) │
│        │ • Scope of Paper 1 integration & evaluation │            │                     │
│        │ • Zero priority or global novelty claims    │            │                     │
├────────┴─────────────────────────────────────────────┴────────────┴─────────────────────┤
│ TOTAL SECTION II PLANNED WORD COUNT                  │   340 words│ (Strict Budget Match│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Paragraph-by-Paragraph Detailed Content Plan

### Area II-A: Movement-Expanded State Spaces and Turn-Aware Routing
- **Target Word Budget:** Exactly **~90 words**.
- **Thematic Purpose:** Trace the scholarly progression of turn modeling from macroscopic traffic assignment to online shortest-path routing, without repeating the vertex-state limitation introduced in Section I.
- **Detailed Content Progression:**
  1. *Historical Traffic Assignment:* Incorporating turn-dependent costs and restrictions was historically introduced in macroscopic traffic assignment. Kirby and Potts \cite{kirby1969minimum} formulated movement-expanded networks where intersections are expanded into directed movement nodes to enforce turn prohibitions and junction delays during tree-building.
  2. *Line Graphs and Shortest Paths:* In route planning, Winter \cite{winter2002modeling} formalized dual line-graph transformations $L(G) = (V_L, E_L)$, where edges become vertices and original junction transitions become directed arcs. This formulation demonstrated that assigning penalties to turn angles eliminates unrealistic zig-zag maneuvers through street grids.
  3. *Progression to Online Search:* While traffic assignment models computed static equilibrium paths across pre-expanded movement networks offline, subsequent algorithmic research demonstrated that state expansion can be evaluated dynamically within label-setting priority queues, defining search states over directed edge transitions $(u, v)$ without materializing the full line graph.
- **Wording Cautions & Boundaries:**
  - Do *not* repeat the mathematical explanation of why vertex states fail (already established in Section I, Paragraph 2).
  - Clearly distinguish offline traffic-assignment tree building from dynamic online shortest-path search.
- **Transition to II-B:** While state-expanded search addresses turn awareness on base graphs, continental-scale route planning led to hierarchical speedup techniques with distinct architectural trade-offs.

---

### Area II-B: Hierarchical Routing and Metric Customization
- **Target Word Budget:** Exactly **~80 words**.
- **Thematic Purpose:** Review hierarchical speedup techniques (Contraction Hierarchies, CRP), turn-aware extensions, and the balance between preprocessing overhead and metric customization.
- **Detailed Content Progression:**
  1. *Contraction Hierarchies & Turn Costs:* Speedup techniques accelerate shortest-path queries by orders of magnitude. The Open Source Routing Machine (OSRM) \cite{luxen2011realtime} implements node-based Contraction Hierarchies (CH) calibrated for automobile travel. Geisberger and Vetter \cite{geisberger2011efficient} extended CH to turn-dependent routing using turn-expanded core nodes and pre-computed shortcut construction, statically incorporating turn tables into shortcuts during preprocessing.
  2. *Customizable Hierarchies:* To support changing edge weights without repeating full hierarchical preprocessing, Customizable Route Planning (CRP) \cite{delling2017customizable} and Customizable Contraction Hierarchies (CCH) \cite{bast2016route} separate metric-independent topology partitioning from a fast metric customization phase. These techniques demonstrate that hierarchical methods can flexibly accommodate updated cost functions on fixed network partitions.
  3. *Trade-Offs for Configurable Routing:* Hierarchical speedup techniques achieve sub-millisecond query latencies on static continental graphs, but require a distinct customization step whenever cost metrics or turn models change. For localized metropolitan networks where vehicle-specific impedance and flyover overrides are configured dynamically, uncontracted state-expanded search offers an alternative engineering trade-off that operates directly on the base graph without intermediate customization phases.
- **Wording Cautions & Boundaries:**
  - Strictly avoid implying that hierarchical methods are universally rigid or incapable of metric customization; explicitly acknowledge that CRP and CCH support fast customization.
  - Do *not* claim that uncontracted search is superior to hierarchical methods.
  - Do *not* cite Delling et al. (2017) as proof that uncontracted search is an immediate dynamic alternative; cite it strictly for customizable routing and metric updates.
- **Transition to II-C:** In parallel with graph-search algorithms, vehicle-specific navigation requires modeling how different transport modes interact with urban road classes.

---

### Area II-C: Two-Wheeler Routing and Road-Class Impedance
- **Target Word Budget:** Exactly **~95 words**.
- **Thematic Purpose:** Review empirical mixed-traffic observations, empirical motorcycle route choice, and motorcycle routing algorithms, clearly distinguishing observed behavior from heuristic impedance modeling.
- **Detailed Content Progression:**
  1. *Empirical Traffic-Flow Observations:* In dense Asian cities, motorcycles constitute a prominent share of urban traffic \cite{promraksa2022lane}. Empirical observations document severe speed dispersion between two-wheelers and passenger vehicles on undivided urban roads \cite{kotagi2020modeling}, as well as distinct lane-filtering dynamics through queue bottlenecks \cite{promraksa2022lane}.
  2. *Empirical Route-Choice Behavior:* Empirical discrete-choice surveys by Fadilah et al. \cite{fadilah2024identifying} observe that motorcycle riders actively choose lower-tier residential and local streets to bypass congested arterial bottlenecks, demonstrating street-class utilization patterns distinct from automobile drivers.
  3. *Motorcycle Routing Algorithms & Post-Hoc Evaluation:* Despite these empirical observations, existing two-wheeler routing frameworks rarely evaluate road impedance within turn-aware search. Asvial et al. \cite{asvial2020entropy} formulated motorcycle routing using $k$-shortest paths generated without turn penalties ($\text{turn cost} = 0$), followed by post-hoc Entropy-TOPSIS multi-criteria re-ranking over pre-computed candidate paths.
  4. *Conceptual Distinction:* In this paper, we formulate a configured class-dependent road impedance model with a flyover override directly within graph relaxation. This model serves as an engineering heuristic to evaluate operational trade-offs, distinct from empirical choice modeling, and does not claim to represent validated rider psychological preferences.
- **Wording Cautions & Boundaries:**
  - Explicitly preserve the 4-way distinction: (i) traffic-flow observations; (ii) empirical choice surveys; (iii) routing algorithms / post-hoc re-ranking; (iv) configured impedance model.
  - Prohibit any statement implying that Fadilah et al. or Promraksa et al. validate our numerical impedance multipliers ($0.90\text{--}4.00$).
  - Avoid any claims about safety, accident reduction, travel-time savings, or congestion reduction.
- **Transition to II-D:** These intersecting domains highlight the need to position our unified algorithmic framework against prior literature.

---

### Area II-D: Research Positioning and Synthesis
- **Target Word Budget:** Exactly **~75 words**.
- **Thematic Purpose:** Delineate established capabilities from prior literature, explain this paper's specific integration, and state the controlled evaluation scope without making priority or novelty claims.
- **Detailed Content Progression:**
  1. *Established Capabilities in Prior Art:* Prior literature establishes movement-expanded state spaces for turn modeling \cite{kirby1969minimum}, \cite{winter2002modeling}, customizable routing hierarchies for flexible cost updates \cite{delling2017customizable}, \cite{bast2016route}, empirical evidence of motorcycle street-class diversion \cite{fadilah2024identifying}, and multi-objective routing incorporating turn penalties on edge-expanded graphs for specialized fleet operations \cite{zografos2004heuristic}.
  2. *Paper 1 Integration and Scope:* This paper focuses on the specific integration of online turn-aware state-expanded $A^*$ search over directed edge states $s=(u, v)$ evaluating discrete angular deflection penalties on-the-fly, a configured two-wheeler road impedance model with grade-separated flyover overrides, and formal proof of conditional heuristic consistency.
  3. *Controlled Evaluation:* We evaluate this framework across 25 corridors on Bengaluru's 744,216-edge network under chronic arterial bottleneck congestion \cite{kumar2025realtime}, quantifying the empirical trade-offs between sharp turn avoidance, arterial exposure, and physical route distance.
- **Wording Cautions & Boundaries:**
  - Citations dropped: `hart1968formal` (reserved for Section IV) and `goldberg2005computing` (landmark ALT not relevant).
  - Citation retained: `zografos2004heuristic` (used strictly for comparing multi-objective routing with turn penalties on edge-expanded graphs).
  - Zero priority or global novelty assertions ("first", "only", "novel in the world").
  - Zero Paper 2 alternative-routing terms (Yen's KSP, route diversity, perpendicular offset).

---

## 3. Typographic Layout and Budget Summary

- **Heading Style:** Four continuous paragraphs with bold run-in headers (`\noindent\textbf{...:}`) to ensure zero vertical line penalty.
- **Planned Word Budget:**
  - Area II-A: 90 words
  - Area II-B: 80 words
  - Area II-C: 95 words
  - Area II-D: 75 words
  - **Total Planned Section II:** **340 words** (Exact 100% budget match).

---

*Refined outline completed under Phase 6.1.1 protocol. Ready for Research Lead review.*
