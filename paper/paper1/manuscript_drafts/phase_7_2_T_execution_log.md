# Phase 7.2-T Execution Log: Targeted Section III Technical Corrections

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 7.2-T — Targeted Section III Technical Corrections  
**Date:** 2026-11-06  
**Document:** [`phase_7_2_T_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_T_execution_log.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 7.2-T EXECUTION COMPLETE (AWAITING LEAD APPROVAL)**  

---

## 1. Overview and Operational Directives

Phase 7.2-T applied the approved technical and mathematical corrections identified in Phase 7.2-S to Section III of Paper 1.

The modifications were executed strictly within the approved boundaries:
- Revised manuscript text: [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (v1.2).
- Updated audit report: [`paper1_section_III_draft_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_draft_audit.md) (v1.2).
- Zero changes to the implementation codebase, graph data, experimental results, Abstract, Introduction, Related Work, or bibliography.
- Zero drafting of Section IV.

---

## 2. Detailed Record of Substantive Corrections

### Correction 1: Graph Representation and State Cardinality (Issue 1)
- **Problem Resolved:** The draft previously described the routing graph as a multigraph $G = (V, E)$ and claimed $|S| = |E| + 1 = 744,217$, ignoring the fact that the routing implementation tracks states by ordered node pairs $(u, v)$ without edge keys.
- **Implementation Reality Grounded:**
  - Raw OpenStreetMap graph: NetworkX `MultiDiGraph` $G_{\text{raw}} = (V, E_{\text{raw}})$ with $|V| = 308,643$ and $|E_{\text{raw}}| = 744,216$ directed edge records.
  - Parallel edges: $3,379$ ordered node pairs share multiple edges ($6,773$ edge records; max 4 per pair).
  - Effective routing graph: Simple directed graph $G = (V, E_s)$ over distinct ordered adjacent pairs, containing $|E_s| = 740,822$ edges.
  - On-the-fly parallel edge collapse:
    $$c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} \left[ \mu(u, v, k) \cdot \ell(u, v, k) \right]$$
  - State space: $S = E_s \cup \{(\text{None}, s_0)\}$.
  - State cardinality: Exactly $|S| = |E_s| + 1 = 740,822 + 1 = 740,823$.
  - The $744,216$ multigraph edge records are no longer called distinct search states.

### Correction 2: Table I Restructuring and Roundabout Decoupling (Issue 2)
- **Problem Resolved:** Table I previously placed the $0.95\times$ roundabout modifier only in the "Permissive Street" row, creating the false impression that roundabouts only apply to permissive streets.
- **Table Restructuring:**
  - **Part A (Base Road-Class Impedance):** Displays $f_{\text{class}}$ for Arterial Trunk/Highway ($3.00\text{--}4.00$), Primary ($2.00\text{--}2.20$), Secondary ($1.40\text{--}1.50$), Tertiary ($1.10\text{--}1.15$), Residential ($1.00$), and Permissive Street ($0.90\text{--}0.95$).
  - **Part B (Topological Modifiers):**
    - Grade-Separated Flyover: Replaces $f_{\text{class}}$ with $0.80$ on $\mathcal{H}_{\text{main}}$.
    - Continuous-Flow Roundabout: Applies $\times 0.95$ across **all classes** carrying `junction=roundabout` (yielding effective multipliers down to $0.855$).
    - Theoretical Co-occurrence: Explicitly documents $0.80 \times 0.95 = 0.76$ for the combined case, while confirming zero occurrences in the Bengaluru corpus (minimum observed $= 0.80$).

### Correction 3: Turn-Angle and Bearing Definition (Issue 3)
- **Problem Resolved:** The turn-angle definition previously did not distinguish between chord-based initial forward azimuths and tangent junction turning angles, and lacked explicit exclusion of internal polyline shape points.
- **Implementation Reality Grounded:**
  - $\theta(u, v)$ is the initial forward azimuth from node $u$ to node $v$, evaluated at endpoint $u$.
  - $\theta(v, w)$ is the initial forward azimuth from node $v$ to node $w$, evaluated at endpoint $v$.
  - Both are computed from node endpoint coordinates $(\phi, \lambda)$.
  - Internal roadway polyline shape points are explicitly stated as not evaluated.
  - Angular deflection $\Delta\theta(u, v, w)$ is formally defined as the smaller angular difference between the initial forward azimuths of endpoint-to-endpoint chords $(u, v)$ and $(v, w)$.
  - Purged all claims of "geodesically exact tangent deflections," "curvature filtering," or "lane-level conflict detection."

### Correction 4: Road-Impedance Wording Polish (Issue 4)
- **Problem Resolved:** Purged 5 instances of teleological or unsupported phrasing:
  1. Line 31: *"two-wheeler routing preferences"* $\to$ **"To incorporate vehicle-specific street hierarchy weighting into graph traversal..."**
  2. Line 36: *"penalize congested arterials"* $\to$ **"...assign higher configured traversal costs to arterial corridors while favoring lower-tier local streets."**
  3. Line 36: *"prioritising grade-separated movement"* $\to$ **"...lowering configured traversal cost along grade-separated infrastructure."**
  4. Line 29: *"penalizing sharp cross-traffic turns"* $\to$ **"penalizing sharp angular deflections ($\ge 60.0^\circ$) and moderate course deflections ($30.0^\circ \le \Delta\theta < 60.0^\circ$)..."**
  5. Line 29: *"while filtering minor roadway curvature"* $\to$ **"...while assigning zero penalty to slight course deviations below $30.0^\circ$."**

### Correction 5: Objective Function and Minimum Edge Cost Integration (Issue 5)
- **Formulation Grounding:**
  - Transition cost over $E_s$:
    $$c(s, s') = c_{\min}(v, w) + P_{\text{turn}}(u, v, w)$$
  - Path-level objective over $E_s$:
    $$C(P) = \sum_{i=1}^k c_{\min}(v_{i-1}, v_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$$
  - Each traversed physical edge $e_i \in E_s$ is charged exactly once via $c_{\min}$, and each intermediate intersection turn is charged exactly once. Initial departure and destination termination contribute zero turn penalty.
  - Units verified: Physical distance $D(P)$ in physical metres ($m$); traversal impedance $C(P)$ in effective metres ($m$).

---

## 3. Revised Word Count Analysis

| Subsection | Target Budget | Revised Count (v1.2) | Variance vs Target | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **III-A** | ~110 words | **128 words** | $+18\text{ words}$ ($+16.4\%$) | Multigraph vs simple graph definition and $c_{\min}$ formula |
| **III-B** | ~100 words | **113 words** | $+13\text{ words}$ ($+13.0\%$) | Exact state cardinality $|S| = |E_s|+1 = 740,823$ definition |
| **III-C** | ~110 words | **114 words** | $+4\text{ words}$ ($+3.6\%$) | Endpoint-to-endpoint chord deflection definition |
| **III-D** | ~150 words | **174 words** | $+24\text{ words}$ ($+16.0\%$) | Decoupled modifier explanation and $c_{\min}$ summation |
| **Total Body Text** | **~470 words** | **529 words** | $\mathbf{+59\text{ words}}$ ($\mathbf{+12.5\%}$) | **Controlled mathematical expansion** |

The $+59$-word expansion is modest (+12.5%) and directly reflects the necessary mathematical definitions requested by the research lead. In standard IEEE two-column typesetting, 529 words consume $\approx 62$ lines of body text, which fits comfortably within the $1.35$ columns allocated on Page 2 (Column 1 bottom plus Column 2 full) without spilling over into Section IV on Page 3.

---

## 4. Frozen File Verification

All frozen research assets remain bitwise unmodified:
- `paper1_abstract_v2.md`: Untouched (3,287 bytes).
- `paper1_introduction_v1.md`: Untouched (7,596 bytes).
- `paper1_related_work_v1.md`: Untouched (6,723 bytes).
- `paper1_verified_references.bib`: Untouched (8,817 bytes).
- `core/config.py` & `routing/algorithms.py`: Untouched.
- `bengaluru_graph.pkl`: Untouched.

---

## 5. Stop Condition Enforced

Phase 7.2-T corrections have been applied and documented. Section III is not automatically frozen. Section IV has not been started. Awaiting research lead review and authorization.
