# Section IV-A: Turn-Aware State-Expanded Search Architecture (Draft v1.0)

**Document:** [`paper1_section_IV_A_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_section_IV_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_outline_v1.md)  
**Parent Blueprint:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Parent Evidence Map:** [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.4)  
**Implementation Source:** [`routing/algorithms.py#L520-L705`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L520-L705)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.2-A STANDALONE DRAFT COMPLETE (AWAITING LEAD REVIEW)**  
**Effective Date:** 2026-11-06  

---

## Section IV: Turn-Aware A* Algorithm, Correctness and Complexity Analysis

\noindent\textbf{A. Turn-Aware State-Expanded Search Architecture:} To evaluate trajectory turns without constructing a line graph, search operates over edge states $s=(u,v) \in S$, tracking arrival at vertex $v$ from predecessor $u$. Origin departure is initialized by synthetic state $(\text{None}, s_0)$, yielding expanded state space $S=E_s \cup \{(\text{None}, s_0)\}$. For extracted state $s=(u,v)$, successors $s'=(v,w)$ are generated along directed edges $(v,w) \in E_s$. Parallel edges between $v$ and $w$ are resolved by selecting the minimum complete road impedance representative $c_{\min}(v,w)$. Transition cost $c(s,s') = c_{\min}(v,w) + P_{\text{turn}}(u,v,w)$ compounds this impedance with the discrete turn penalty from (1), with $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$. States are ordered in a binary min-heap by priority $(g(s)+h(s), \kappa, s)$ with FIFO tie-breaker $\kappa$. When a transition yields $g(s)+c(s,s') < g(s')$, tentative cost $g(s')$ is updated and $s'$ is inserted. Search terminates once a popped state reaches destination $t$, reconstructing the route via backpointers.

---

## Subsection IV-A Word Count and Quality Audit

| Metric | Target Budget | Draft v1.0 Value | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Body Word Count (Whitespace Split)** | 120–150 words | **142 words** | **EXACT FIT (Within Budget)** |
| **Body Word Count (LaTeX Math as Single Token)** | 110–140 words | **122 words** | **EXACT FIT (Within Budget)** |
| **Display Equations** | 0 | **0** | **COMPLIANT** |
| **Float Assets (Algorithms / Figures)** | 0 | **0** | **COMPLIANT (Reclaimed Vertical Space)** |

### Content Verification Checklist
1. **Edge-based state transformation:** Explicitly defined as $s=(u,v) \in S$ tracking arrival at vertex $v$ from predecessor $u$ without constructing a line graph.
2. **Synthetic initial state:** Formally specified as $(\text{None}, s_0)$, establishing expanded state space $S=E_s \cup \{(\text{None}, s_0)\}$.
3. **Successor generation:** Directed edge traversal $(v,w) \in E_s$ via physical graph successors.
4. **Transition cost composition:** Directly couples minimum complete road impedance $c_{\min}(v,w)$ with angular turn penalty $P_{\text{turn}}(u,v,w)$ from Eq. (1).
5. **Priority queue and relaxation:** Min-heap structured as $(g(s)+h(s), \kappa, s)$ with FIFO tie-breaking counter $\kappa$, updating $g(s')$ upon strict relaxation and inserting the relaxed state without unsupported `decrease-key` claims.
6. **Parallel-edge handling:** Grounded in on-the-fly selection of the minimum complete impedance representative $c_{\min}(v,w)$.
7. **Notation consistency:** Fully consistent with Section III's definitions ($S$, $E_s$, $c_{\min}$, $P_{\text{turn}}$, $s_0$, $t$).

### Technical Restriction Compliance
- Does not describe search as vertex-only.
- Does not claim queue pops equal unique states.
- Does not claim stale entries are discarded or filtered.
- Does not claim a closed-set implementation.
- Does not introduce new algorithmic optimizations or features.
- Does not discuss heuristic admissibility, consistency, or asymptotic complexity (reserved for IV-B, IV-C, and IV-D).
- Does not mention Paper 2 alternative routes.
- Does not make safety, travel-time, or rider-preference claims.
