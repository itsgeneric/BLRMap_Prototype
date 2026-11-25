# Section IV-B: Scaled Haversine Heuristic Formulation (Draft v1.0)

**Document:** [`paper1_section_IV_B_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_section_IV_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_outline_v1.md)  
**Parent Blueprint:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Parent Evidence Map:** [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.4)  
**Implementation Source:** [`routing/algorithms.py#L500-L513`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L500-L513) (`MIN_PENALTY_FLOOR = 0.8`)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.2-B STANDALONE DRAFT COMPLETE (AWAITING LEAD REVIEW)**  
**Effective Date:** 2026-11-06  

---

## Section IV: Turn-Aware A* Algorithm, Correctness and Complexity Analysis

\noindent\textbf{B. Scaled Haversine Heuristic Formulation:} To guide search toward destination $t \in V$, the heuristic function $h(s)$ estimates remaining traversal impedance from state $s=(u,v)$ using the coordinates of current physical vertex $v$. For synthetic initial state $(\text{None}, s_0)$, this vertex evaluates to $s_0$. The function estimates remaining impedance cost, distinct from physical distance or travel time, by scaling great-circle Haversine distance $D_{\text{haversine}}(v,t)$ by the minimum composite road multiplier:
$$h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t) = 0.80 \cdot D_{\text{haversine}}(v, t) \tag{4}$$
Here, $\mu_{\min} = 0.80$ corresponds to the 0.80 override for qualifying grade-separated main-road segments (Table~I), representing an empirically verified lower bound on the evaluated Bengaluru graph rather than a universal road-network constant. At the destination vertex, straight-line distance vanishes and $h(s) = 0.0$.

---

## Subsection IV-B Word Count and Quality Audit

| Metric | Target Budget | Draft v1.0 Value | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Body Word Count (Whitespace Split, excl. Eq. 4)** | 90–110 words | **106 words** | **EXACT FIT (Within Budget)** |
| **Body Word Count (LaTeX Math as Single Token)** | 85–105 words | **99 words** | **EXACT FIT (Within Budget)** |
| **Display Equations** | Exactly 1 | **1 (Equation 4)** | **COMPLIANT** |
| **Float Assets (Algorithms / Figures)** | 0 | **0** | **COMPLIANT (Reclaimed Vertical Space)** |

### Content Verification Checklist
1. **Edge-based state heuristic definition:** Defined for state $s=(u,v)$ referencing physical arrival vertex $v$ and destination $t$.
2. **Minimum composite edge multiplier:** Grounded in $\mu_{\min} = 0.80$ (`MIN_PENALTY_FLOOR` in `routing/algorithms.py#L28`).
3. **Equation (4) Introduction:** Explicitly introduced continuing numbering monotonically from Section III Eq. (1)–(3).
4. **Impedance estimation mechanism:** Explains straight-line Haversine distance scaled by the minimum observed composite multiplier, distinct from physical distance and travel time.
5. **Destination vanishing condition:** Explicitly specifies $h(s) = 0.0$ when $v = t$.
6. **Synthetic root handling:** Explicitly states that for $(\text{None}, s_0)$, the physical vertex evaluates to $s_0$.
7. **Empirical boundary demarcation:** Explicitly documents that $\mu_{\min} = 0.80$ is an empirically verified property of the evaluated Bengaluru graph, not a universal road-network constant.

### Identification of Assumptions Requiring Proof in Section IV-C
The formulation in Equation (4) relies on four underlying mathematical conditions whose proofs and implications are strictly reserved for Section IV-C:
1. **Assumption A1 (Multiplier Floor):** $\mu(e) \ge \mu_{\min} = 0.80$ across all edges $e \in E_s$ (dataset-verified: zero bridge-roundabout co-occurrences).
2. **Assumption A2 (Nonnegative Turn Penalties):** $P_{\text{turn}}(u, v, w) \ge 0.0$ for all transitions (enforced unconditionally by Section III Eq. 1).
3. **Assumption A3 (Physical Road Length Lower Bound):** OSM-derived physical edge length $\ell(v, w) \ge D_{\text{haversine}}(v, w)$ for every edge in $E_s$. Physical segment length extracted from OpenStreetMap roadway geometry is lower-bounded by the great-circle chord distance between its endpoint coordinates, without implying independent surveying or field measurement.
4. **Metric Space Triangle Inequality:** $D_{\text{haversine}}(v, t) \le D_{\text{haversine}}(v, w) + D_{\text{haversine}}(w, t)$ on the spherical surface.
These conditions will be synthesized in Section IV-C to formally prove conditional admissibility (Theorem 1) and monotonic consistency (Theorem 2).
