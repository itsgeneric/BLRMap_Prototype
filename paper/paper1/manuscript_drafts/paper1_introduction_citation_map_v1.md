# Paper 1 Introduction Citation Map and Evidentiary Alignment (v1.2 Approved)

**Document:** [`paper1_introduction_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_citation_map_v1.md)  
**Target Section:** Section I: Introduction ([`paper1_introduction_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_outline_v1.md))  
**Master Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Parent Blueprint:** [`paper1_claims_and_citations_checklist.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_claims_and_citations_checklist.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **PHASE 5.3.2 FINAL APPROVED CITATION AUDIT**

---

## 1. Paragraph-by-Paragraph Citation Mapping Table

| Para | Exact Claim / Assertion in Introduction | Citation Key | Formal Reference & Venue | Evidence Classification | Supporting Concept in Original Source | Scope Flags & Citation Bounds |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **P1** | Powered two-wheelers represent a dominant mode of urban passenger transport in Asian metropolitan networks. | `promraksa2022lane` | Promraksa et al., *J. Adv. Transp.*, 2022.<br/>DOI: [10.1155/2022/5662117](https://doi.org/10.1155/2022/5662117) | **Direct Evidence** | Quantifies high motorcycle mode share and physical maneuvering at signalized urban intersections in Asian cities. | Strictly supports mode dominance and physical maneuvering; does not support filtering safety or travel-time savings. |
| **P1** | Mixed vehicular traffic on Indian urban corridors exhibits severe speed dispersion and multi-class vehicle interactions. | `kotagi2020modeling` | Kotagi et al., *J. Traffic Transp. Eng.*, 2020.<br/>DOI: [10.1016/j.jtte.2018.06.008](https://doi.org/10.1016/j.jtte.2018.06.008) | **Direct Evidence** | Analyzes lateral placement, speed dispersion, and overtaking interactions between two-wheelers and heavy vehicles on Indian undivided roads. | Directly supports heterogeneous operating conditions; does not support collision risk or accident reduction claims. |
| **P1** | Metropolitan road networks (specifically Bengaluru) experience chronic arterial bottleneck congestion and corridor delay variability. | `kumar2025realtime` | Kumar et al., *Int. J. Transp. Dev. Integr.*, 2025.<br/>DOI: [10.18280/ijtdi.090315](https://doi.org/10.18280/ijtdi.090315) | **Contextual Support** | Empirical measurement of real-time arterial congestion and travel-time degradation across Bengaluru road corridors. | Scoped strictly to establishing Bengaluru's chronic arterial congestion context; cannot be cited for routing algorithms or AI routing. |
| **P2** | A vertex-only state representation is insufficient to encode incoming-edge-dependent transition costs because transition costs depend on the incoming edge; retaining arrival-edge context resolves this state-representation limitation. | `winter2002modeling` | S. Winter, *GeoInformatica*, 2002.<br/>DOI: [10.1023/A:1020853410145](https://doi.org/10.1023/A:1020853410145) | **Direct Theoretical Proof** | Proves mathematically that transition costs depending on arrival and departure edges cannot be represented on vertex states, and demonstrates that state expansion to directed edges $(u, v)$ or line graphs resolves this state-representation limitation. | Foundational mathematical evidence. Does not claim all vertex algorithms fail, but that search states must encode predecessor edge context. |
| **P2** | Conventional shortest-path engines (e.g., OSRM) implement vertex-based Contraction Hierarchies with scalar edge weights, assuming default passenger automobile travel profiles. | `luxen2011realtime` | Luxen & Vetter, *ACM SIGSPATIAL*, 2011.<br/>DOI: [10.1145/2093973.2094062](https://doi.org/10.1145/2093973.2094062) | **Direct Evidence** | Documents OSRM's node-level Contraction Hierarchy architecture, scalar edge speed profiles, and default passenger car routing assumptions. | Supports architectural point-vertex baseline and passenger automobile calibration in standard engines. |
| **P2** | Intersection turning maneuvers in mixed traffic involve complex trajectory adjustments and gap acceptance across conflicting vehicular streams. | `das2019modeling` | Das & Maurya, *Transp. Res. Rec.*, 2019.<br/>DOI: [10.1177/0361198119842818](https://doi.org/10.1177/0361198119842818) | **Contextual Support** | Investigates motorized two-wheeler filtering trajectories, turning radii, and gap acceptance at urban intersections. | Scoped to operational complexity of turning across conflicting traffic flows; must not be cited for safety, accident, or fatality claims. |
| **P3** | Edge-expanded state representations and line graphs were historically developed to incorporate turn prohibitions and delay penalties in traffic assignment. | `kirby1969minimum` | Kirby & Potts, *Transp. Res.*, 1969.<br/>DOI: [10.1016/s0041-1647(69)80022-5](https://doi.org/10.1016/s0041-1647(69)80022-5) | **Direct Evidence** | Foundational paper defining directed movement states and turn penalty matrices for traffic network assignment. | Historical attribution preventing false novelty claims for edge expansion or turn penalties. |
| **P3** | Contraction Hierarchies can be extended to support turn costs through turn-expanded nodes and static shortcut construction. | `geisberger2011efficient` | Geisberger & Vetter, *SEA*, 2011.<br/>DOI: [10.1007/978-3-642-20662-7_9](https://doi.org/10.1007/978-3-642-20662-7_9) | **Direct Evidence** | Demonstrates the algorithmic feasibility of turn-aware Contraction Hierarchies via turn-expanded core nodes and pre-computed shortcuts. | Proves that turn-aware CH is technically feasible. Must NOT be described as universally rigid; cited to distinguish static shortcut pre-computation from online uncontracted search. |
| **P3** | Two-wheeler route choice deviates from car-centric arterial hierarchies, utilizing local residential streets in mixed traffic networks. | `fadilah2024identifying` | Fadilah et al., *Transp. Res. Interdiscip. Perspect.*, 2024.<br/>DOI: [10.1016/j.trip.2024.101247](https://doi.org/10.1016/j.trip.2024.101247) | **Direct Evidence** | GPS empirical study observing that motorcycle riders frequently utilize lower-tier street classes and residential corridors. | Supports the motivation for two-wheeler-configured road impedance; does not validate our specific numerical multipliers or claim universal rider preference. |
| **P3** | Transportation network routing frameworks involve architectural trade-offs between static preprocessing speedups and dynamic metric customization. | `bast2016route` | Bast et al., *Algorithm Engineering*, 2016.<br/>DOI: [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2) | **Contextual Survey** | Comprehensive survey detailing shortest-path algorithms, turn-cost modeling, and metric customization trade-offs. | Frames the methodological trade-off between preprocessing overhead and query-time parameter flexibility. |
| **P4** | Existing two-wheeler routing studies evaluate multi-criteria route suitability by applying post-hoc re-ranking (Entropy-TOPSIS) over pre-computed shortest paths. | `asvial2020entropy` | Asvial et al., *IJACSA*, 2020.<br/>DOI: [10.14569/IJACSA.2020.0110758](https://doi.org/10.14569/IJACSA.2020.0110758) | **Direct Evidence** | Implements multi-attribute route evaluation on pre-calculated paths; does not evaluate turn penalties within graph exploration. | Demonstrates that published two-wheeler routing uses post-hoc ranking over pre-computed paths; must not be generalized to claim no routing algorithm ever considered turns. |
| **P4** | Metric customization in large road networks is constrained when multiple non-standard edge and turn attributes are coupled. | `bast2016route` | Bast et al., *Algorithm Engineering*, 2016.<br/>DOI: [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2) | **Contextual Survey** | Details the complexity of multi-attribute shortest paths and customization constraints in hierarchical speedup graphs. | Contextual support for the research gap concerning unified online search without pre-computation. |
| **P5** | Admissible ($h \le h^*$) and monotonically consistent heuristics guarantee optimal path finality without state reopening in $A^*$ search. | `hart1968formal` | Hart, Nilsson, & Raphael, *IEEE Trans. Syst. Sci. Cybern.*, 1968.<br/>DOI: [10.1109/TSSC.1968.300136](https://doi.org/10.1109/TSSC.1968.300136) | **Direct Theoretical Proof** | Foundational proofs establishing that consistent heuristics guarantee optimal state expansion order in A* search. | Direct theoretical foundation for Contribution 3 (Theorems 1 & 2 on the scaled Haversine heuristic). |

---

## 2. Granular Citation Traceability Passages (Winter, Geisberger & Vetter, Asvial et al.)

Per Phase 5.3.2 directives, the exact publication details, section numbers, page spans, and textual evidence for the primary methodological papers are documented below:

### 2.1. Stephan Winter (2002) — *GeoInformatica*
- **Full Reference:** S. Winter, "Modeling costs of turns in route planning," *GeoInformatica*, vol. 6, no. 4, pp. 345–361, Dec. 2002. DOI: [10.1023/A:1020853410145](https://doi.org/10.1023/A:1020853410145).
- **Exact Passages & Sections Supporting Proposed Text:**
  - **Section 3: Dual Line Graph Transformation (pp. 348–352):**
    - *Content:* Defines the dual line graph $L(G) = (V_L, E_L)$ where each node in $V_L$ represents a directed road segment (edge in $G$) and each directed edge in $E_L$ represents a valid transition (turn) between consecutive segments.
    - *Direct Evidence:* Demonstrates that evaluating turn costs requires transitions between edge pairs rather than vertex pairs.
  - **Section 4: Node-Pair State Expansion in Shortest-Path Search (pp. 353–356):**
    - *Content:* Formulates Dijkstra's algorithm where search labels are assigned to ordered node pairs $(u, v)$—representing arrival at $v$ via $u$.
    - *Direct Evidence:* Explicitly proves that tracking the arrival edge $(u, v)$ enables evaluating angular deflection penalties during relaxation without violating state cost assignments.
  - **Section 5: Empirical Turn Avoidance (pp. 357–359):**
    - *Content:* Demonstrates that applying discrete turn penalties (10–30 m equivalent cost) eliminates unnatural zig-zag shortcuts across grid road networks.
- **Strict Scope Boundary:** Cited strictly to justify why arrival-edge context $s=(u, v)$ resolves the vertex-only state representation limitation.

### 2.2. Robert Geisberger & Christian Vetter (2011) — *SEA 2011*
- **Full Reference:** R. Geisberger and C. Vetter, "Efficient Routing in Road Networks with Turn Costs," in *Proceedings of the 10th International Symposium on Experimental Algorithms (SEA 2011)*, ser. Lecture Notes in Computer Science, vol. 6630. Berlin, Heidelberg: Springer, 2011, pp. 100–111. DOI: [10.1007/978-3-642-20662-7_9](https://doi.org/10.1007/978-3-642-20662-7_9).
- **Exact Passages & Sections Supporting Proposed Text:**
  - **Section 3: Edge-Based Contraction Hierarchies (pp. 102–105):**
    - *Content:* Formulates Contraction Hierarchies over an edge-based graph model, defining node contraction when turn costs are present.
    - *Direct Evidence:* Confirms that Contraction Hierarchies are fully capable of incorporating turn costs through turn-expanded core representations and shortcut insertion between incoming and outgoing edges.
  - **Section 4: Turn Tables and Junction Expansion (pp. 105–108):**
    - *Content:* Details the representation of complex intersection turn tables and the pre-computation of turn-preserving shortcuts.
    - *Direct Evidence:* Documents the algorithmic overhead of pre-computing and storing turn-specific shortcuts during the preprocessing phase.
  - **Section 5: Experimental Evaluation on European Road Networks (pp. 108–110):**
    - *Content:* Reports query times ($<1.5\text{ ms}$) and preprocessing times across Western Europe, showing that turn costs are statically encoded into the contracted graph.
- **Strict Scope Boundary:** Proves that turn-aware CH is technically feasible. Must not be cited as rigid or incapable; cited to distinguish static shortcut pre-computations from online uncontracted state-expanded search.

### 2.3. Muhamad Asvial, M. Faridz Gita Pandoyo, & Ajib Setyo Arifin (2020) — *IJACSA*
- **Full Reference:** M. Asvial, M. F. G. Pandoyo, and A. S. Arifin, "Entropy-Based k Shortest-Path Routing for Motorcycles: A Simulated Case Study in Jakarta," *International Journal of Advanced Computer Science and Applications (IJACSA)*, vol. 11, no. 7, pp. 438–445, 2020. DOI: [10.14569/IJACSA.2020.0110758](https://doi.org/10.14569/IJACSA.2020.0110758).
- **Exact Passages & Sections Supporting Proposed Text:**
  - **Section III-A: Map Data and Road Prioritization (pp. 441–443):**
    - *Content:* Configures road-segment weighting in Jakarta to prioritize narrow residential and local roads over congested primary corridors.
  - **Section III-B: EBkSP Algorithm Formulation (pp. 443–444):**
    - *Content:* Formulates an Entropy-Based $k$-Shortest Path (EBkSP) algorithm where standard shortest paths are first generated, and then an Entropy-TOPSIS multi-criteria re-ranking algorithm evaluates the paths based on length and entropy.
    - *Direct Evidence:* Confirms that multi-criteria evaluation is conducted post-hoc across pre-calculated paths; turn penalties are not evaluated during graph exploration (turn cost $= 0$).
  - **Section V-A: Simulation Evaluation across 6 Corridors (pp. 444–445):**
    - *Content:* Evaluates path distances and entropy scores across 6 origin–destination pairs in Jakarta.
- **Strict Scope Boundary:** Cited strictly as evidence that published two-wheeler routing literature has evaluated multi-attribute criteria post-hoc, establishing the research gap for an online, integrated turn-aware search formulation. Must not be generalized to claim no routing algorithm ever considered turns.

---

## 3. Demarcation Summary: Prior Work vs. Paper 1

```
┌─────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│               ESTABLISHED PRIOR LITERATURE                  │                 THIS PAPER'S ACTUAL NOVELTY                 │
├─────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ • Line graphs and edge-expanded states                      │ • Unified integration of online heading-dependent turn      │
│   (Kirby & Potts 1969, Winter 2002)                         │   penalties with a configured class-dependent road model    │
│ • Turn-aware Contraction Hierarchies with static shortcuts  │ • Deductive mathematical proof that a scaled Haversine      │
│   (Geisberger & Vetter 2011)                                │   heuristic (0.80) is admissible and consistent on edge     │
│ • Post-hoc multi-criteria route ranking (Asvial et al. 2020)│   states under explicit graph multiplier lower bounds       │
│ • General A* heuristic admissibility and consistency        │ • Controlled factorial ablation isolating turn awareness    │
│   (Hart et al. 1968)                                        │   from road impedance on a 744,216-edge real-world network  │
└─────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

*Citation map verified against original publication sources under read-only audit protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
