# Section IV-C: Heuristic Admissibility and Consistency (Draft v1.0)

**Document:** [`paper1_section_IV_C_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_section_IV_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_outline_v1.md)  
**Parent Blueprint:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Parent Evidence Map:** [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.4)  
**Implementation Source:** [`routing/algorithms.py#L500-L513`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L500-L513), [`routing/graph_manager.py#L191-L217`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py#L191-L217)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.2-C STANDALONE DRAFT COMPLETE (AWAITING LEAD REVIEW)**  
**Effective Date:** 2026-11-06  

---

## Section IV: Turn-Aware A* Algorithm, Correctness and Complexity Analysis

\noindent\textbf{C. Heuristic Admissibility and Consistency:} Correctness rests on four conditions verified for the evaluated Bengaluru network: (i) edge multipliers satisfy $\mu(e) \ge 0.80$, (ii) turn penalties satisfy $P_{\text{turn}} \ge 0.0$, (iii) OSM-derived physical edge lengths satisfy $\ell(v,w) \ge D_{\text{haversine}}(v,w)$, and (iv) Haversine distance obeys the spherical triangle inequality $D_{\text{haversine}}(v,t) \le D_{\text{haversine}}(v,w) + D_{\text{haversine}}(w,t)$. Because every parallel link satisfies $\mu(v,w,k)\ell(v,w,k) \ge 0.80 D_{\text{haversine}}(v,w)$, minimum selection preserves this bound: $c_{\min}(v,w) = \min_k [\mu(v,w,k)\ell(v,w,k)] \ge 0.80 D_{\text{haversine}}(v,w)$. For transition $s=(u,v) \to s'=(v,w)$, consistency requires:
$$h(s) \le c(s,s') + h(s') \tag{5}$$
Multiplying the triangle inequality by $0.80$ gives $h(s) \le 0.80 D_{\text{haversine}}(v,w) + h(s')$. Since transition cost $c(s,s') = c_{\min}(v,w) + P_{\text{turn}}(u,v,w)$ adds nonnegative $P_{\text{turn}} \ge 0.0$ to $c_{\min}(v,w) \ge 0.80 D_{\text{haversine}}(v,w)$, we have $c(s,s') \ge 0.80 D_{\text{haversine}}(v,w)$, satisfying (5). For synthetic root $(\text{None}, s_0)$, departure penalty vanishes ($P_{\text{turn}}=0.0$) and the bound applies identically from vertex $s_0$. Summing (5) along any path to destination $t$ where $h(t)=0$ proves admissibility: $h(s)$ never exceeds optimal remaining impedance $C^*(s)$. Conditional on the verified multiplier floor and OSM geometry of the evaluated graph, consistency guarantees that each state is optimal upon first priority-queue extraction. State reopening is therefore unnecessary, though duplicate stale entries remain in the heap until popped.

---

## Subsection IV-C Word Count and Quality Audit

| Metric | Target Budget | Draft v1.0 Value | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Body Word Count (Whitespace Split, excl. Eq. 5)** | 150–190 words | **190 words** | **EXACT FIT (At Budget Boundary)** |
| **Body Word Count (LaTeX Math as Single Token)** | 140–180 words | **151 words** | **EXACT FIT (Within Budget)** |
| **Display Equations** | Exactly 1 | **1 (Equation 5)** | **COMPLIANT** |
| **Float Assets (Algorithms / Figures)** | 0 | **0** | **COMPLIANT (Reclaimed Vertical Space)** |

### Mathematical Content Verification Checklist
1. **Four Explicit Conditions:**
   - Multiplier floor: $\mu(e) \ge 0.80$ (dataset-verified: zero bridge-roundabout co-occurrences).
   - Nonnegative turn penalties: $P_{\text{turn}} \ge 0.0$ unconditionally from Section III Eq. (1).
   - OSM-derived physical length lower bound: $\ell(v,w) \ge D_{\text{haversine}}(v,w)$ via polyline chord inequality.
   - Metric space triangle inequality: $D_{\text{haversine}}(v,t) \le D_{\text{haversine}}(v,w) + D_{\text{haversine}}(w,t)$ on spherical earth.
2. **Parallel-Edge Collapsing Lower Bound:** Explicitly proven that taking the minimum over all multigraph candidates preserves $c_{\min}(v,w) \ge 0.80 D_{\text{haversine}}(v,w)$.
3. **Equation (5) Introduction:** Formal consistency inequality $h(s) \le c(s,s') + h(s')$ numbered monotonically continuing from Equation (4).
4. **Step-by-Step Consistency Proof:** Direct derivation combining scaled triangle inequality with $c(s,s') \ge c_{\min}(v,w) \ge 0.80 D_{\text{haversine}}(v,w)$.
5. **Synthetic Initial State Handling:** Formally accounts for $(\text{None}, s_0)$ with $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$.
6. **Path Induction to Admissibility:** Telescoping sum of consistent step bounds along optimal path to destination $t$ where $h(t)=0$, establishing $h(s) \le C^*(s)$.
7. **Empirical Scope Demarcation:** Explicitly stated as conditional on the verified multiplier floor and OSM geometry of the evaluated graph; does not claim universal validity for arbitrary networks.
8. **Algorithmic Consequence Precision:** Explains optimal first-extraction finality and justifies absence of state reopening, while accurately stating that duplicate stale entries remain in the heap until popped.

### Technical Restriction Compliance
- Does not assume the 0.80 multiplier floor is universal.
- Does not use "physical surveyed length" (uses "OSM-derived physical edge length").
- Does not confuse impedance cost with physical distance or travel time.
- Does not omit the parallel-edge minimum argument.
- Does not claim proof covers graphs with multipliers below 0.80.
- Does not draft IV-D or discuss asymptotic complexity.
- Does not modify approved IV-A, IV-B, or frozen Sections I–III.
- Does not modify code, graph data, or experimental datasets.
