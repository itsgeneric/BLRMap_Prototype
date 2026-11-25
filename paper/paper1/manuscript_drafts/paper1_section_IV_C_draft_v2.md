# Section IV-C: Heuristic Admissibility and Consistency (Draft v2.0 - Compressed)

**Document:** [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_section_IV_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_outline_v1.md)  
**Parent Blueprint:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Predecessor Draft:** [`paper1_section_IV_C_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v1.md) (190 words)  
**Implementation Source:** [`routing/algorithms.py#L500-L513`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L500-L513), [`routing/graph_manager.py#L191-L217`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py#L191-L217)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.2-E COMPRESSED DRAFT COMPLETE (AWAITING LEAD REVIEW)**  
**Effective Date:** 2026-11-06  

---

## Section IV: Turn-Aware A* Algorithm, Correctness and Complexity Analysis

\noindent\textbf{C. Heuristic Admissibility and Consistency:} Correctness rests on four conditions verified for the evaluated Bengaluru network: (i) edge multipliers satisfy $\mu(e) \ge 0.80$, (ii) turn penalties satisfy $P_{\text{turn}} \ge 0.0$, (iii) OSM-derived physical edge lengths satisfy $\ell(v,w) \ge D_{\text{haversine}}(v,w)$, and (iv) Haversine distance obeys spherical triangle inequality $D_{\text{haversine}}(v,t) \le D_{\text{haversine}}(v,w) + D_{\text{haversine}}(w,t)$. Because every parallel link satisfies $\mu(v,w,k)\ell(v,w,k) \ge 0.80 D_{\text{haversine}}(v,w)$, minimum selection preserves this bound: $c_{\min}(v,w) = \min_k [\mu(v,w,k)\ell(v,w,k)] \ge 0.80 D_{\text{haversine}}(v,w)$. For transition $s=(u,v) \to s'=(v,w)$, consistency requires:
$$h(s) \le c(s,s') + h(s') \tag{5}$$
Scaling the triangle inequality by $0.80$ gives $h(s) \le 0.80 D_{\text{haversine}}(v,w) + h(s')$. Because $c(s,s') = c_{\min}(v,w) + P_{\text{turn}}(u,v,w)$ adds nonnegative $P_{\text{turn}} \ge 0.0$ to $c_{\min}(v,w) \ge 0.80 D_{\text{haversine}}(v,w)$, we have $c(s,s') \ge 0.80 D_{\text{haversine}}(v,w)$, satisfying (5). For synthetic root $(\text{None}, s_0)$, departure penalty vanishes ($P_{\text{turn}}=0.0$) and the bound holds from $s_0$. Summing (5) along any path to destination $t$ where $h(t)=0$ proves admissibility: $h(s)$ never exceeds optimal remaining impedance $C^*(s)$. Conditional on the verified multiplier floor and OSM geometry of the evaluated graph, consistency guarantees optimality when a state's current-best queue entry is first extracted. Older duplicate entries may still be popped and processed later; state reopening is unnecessary.

---

## Subsection IV-C Word Count and Quality Audit

| Metric | Target Budget | Draft v1.0 | Draft v2.0 Value | Variance | Compliance Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Body Word Count (Whitespace Split, excl. Eq. 5)** | 150–190 words | 190 words | **185 words** | $-5\text{ words}$ | **EXACT FIT (Within Budget)** |
| **Body Word Count (LaTeX Math as Single Token)** | 140–180 words | 151 words | **146 words** | $-5\text{ words}$ | **EXACT FIT (Within Budget)** |
| **Display Equations** | Exactly 1 | 1 | **1 (Equation 5)** | $0$ | **COMPLIANT** |
| **Float Assets (Algorithms / Figures)** | 0 | 0 | **0** | $0$ | **COMPLIANT** |

### Mathematical Preservation Checklist
- **Four Explicit Conditions:** Retains conditions (i) $\mu(e) \ge 0.80$, (ii) $P_{\text{turn}} \ge 0.0$, (iii) OSM-derived physical edge length $\ell(v,w) \ge D_{\text{haversine}}(v,w)$, and (iv) spherical triangle inequality.
- **Parallel-Edge Minimum Preservation:** Retains explicit proof that minimum selection over candidate keys preserves $c_{\min}(v,w) \ge 0.80 D_{\text{haversine}}(v,w)$.
- **Equation (5):** Retains $h(s) \le c(s,s') + h(s')$ with tag Eq. (5).
- **Consistency Proof Steps:** Retains scaling by 0.80 and $c(s,s') \ge c_{\min}(v,w) \ge 0.80 D_{\text{haversine}}(v,w)$.
- **Synthetic Root Case:** Retains $(\text{None}, s_0)$ with $P_{\text{turn}}=0.0$ and lower bound from $s_0$.
- **Admissibility Derivation:** Retains summation along paths to destination $t$ where $h(t)=0$ proving $h(s) \le C^*(s)$.
- **Empirical Boundary Demarcation:** Retains explicit conditionality on verified multiplier floor and OSM geometry of the evaluated graph.
- **Algorithmic State Finality:** Retains optimality guarantee when a state's current-best queue entry is first extracted, explicitly noting older duplicate entries may still be popped and processed later, and confirming state reopening is unnecessary.
