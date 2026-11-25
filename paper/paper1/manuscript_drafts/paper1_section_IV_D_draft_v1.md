# Section IV-D: Computational Complexity Analysis (Draft v1.0)

**Document:** [`paper1_section_IV_D_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_section_IV_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_outline_v1.md)  
**Parent Blueprint:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Parent Evidence Map:** [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md) (v1.4)  
**Implementation Source:** [`routing/algorithms.py#L520-L705`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L520-L705)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.2-D STANDALONE DRAFT COMPLETE (AWAITING LEAD REVIEW)**  
**Effective Date:** 2026-11-06  

---

## Section IV: Turn-Aware A* Algorithm, Correctness and Complexity Analysis

\noindent\textbf{D. Computational Complexity Analysis:} Search operates over $|E_s|+1$ edge states. Because Python's binary min-heap lacks a \texttt{decrease-key} operation, relaxation pushes duplicate state entries that are popped without immediate discard, while transition evaluation dynamically scans up to $q_{\max}$ parallel edge candidates. On general directed graphs, these queue operations and successor-loop evaluations yield asymptotic time and logical-memory upper bounds:
$$\begin{aligned}
\mathcal{T}_{\text{general}} &= \mathcal{O}\left( |E_s| d_{\max}^{\text{out}} \log(|E_s| d_{\max}^{\text{out}}) + q_{\max} |E_s| d_{\max}^{\text{in}} d_{\max}^{\text{out}} \right) \\
\mathcal{M}_{\text{general}} &= \mathcal{O}(|E_s| d_{\max}^{\text{out}} + |V|)
\end{aligned} \tag{6}$$
For road networks satisfying bounded in-degree, out-degree, and parallel-edge multiplicity assumptions ($d_{\max}^{\text{in}}, d_{\max}^{\text{out}}, q_{\max} = \mathcal{O}(1)$), these expressions simplify to $\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$ and $\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|)$ logical entries. On the evaluated Bengaluru network ($|V|=308,643$, $|E_s|=740,822$, $d_{\max}^{\text{in}}=d_{\max}^{\text{out}}=6$, $q_{\max}=4$), full-network saturation entails theoretical upper bounds of $5,886,792$ successor-loop iterations and $3,877,450$ logical memory entries across all persistent search structures. These theoretical saturation limits differ fundamentally from empirical query-level performance, where goal-directed heuristic guidance prunes exploration to $119$–$129,619$ queue pops across 25 commute corridors (median latency: $174.93\text{ ms}$).

---

## Subsection IV-D Word Count and Quality Audit

| Metric | Target Budget | Draft v1.0 Value | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Body Word Count (Whitespace Split, excl. Eq. 6)** | 120–160 words | **141 words** | **EXACT FIT (Within Budget)** |
| **Body Word Count (LaTeX Math as Single Token)** | 110–150 words | **130 words** | **EXACT FIT (Within Budget)** |
| **Display Equations** | Exactly 1 | **1 (Equation 6)** | **COMPLIANT** |
| **Float Assets (Algorithms / Figures)** | 0 | **0** | **COMPLIANT (Reclaimed Vertical Space)** |

### Cumulative Section IV Word Budget Audit

| Subsection | Draft Deliverable | Whitespace Words | Math-as-Token Words | Display Eq# |
| :--- | :--- | :---: | :---: | :---: |
| **IV-A. State-Expanded Architecture** | [`paper1_section_IV_A_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v1.md) | 142 words | 122 words | 0 |
| **IV-B. Scaled Haversine Heuristic** | [`paper1_section_IV_B_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v1.md) | 106 words | 99 words | 1 (Eq. 4) |
| **IV-C. Correctness Proofs** | [`paper1_section_IV_C_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v1.md) | 190 words | 151 words | 1 (Eq. 5) |
| **IV-D. Complexity Analysis** | [`paper1_section_IV_D_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v1.md) | 141 words | 130 words | 1 (Eq. 6) |
| **Cumulative Section IV Total** | **Subsections IV-A to IV-D** | **579 words** | **502 words** | **3 Equations** |

> [!WARNING]
> **Word Budget Overrun Notice:**
> - Current cumulative whitespace count: **579 words** (581 words prior to IV-D wording refinement).
> - Blueprint page-budget ceiling: **560 words** (`paper1_final_page_budget_v1.md`).
> - Current overrun: **+19 to +21 words** ($+3.4\%$ to $+3.8\%$).
> - In strict compliance with research protocol governance, no approved text from Subsections IV-A, IV-B, or IV-C has been silently compressed or modified.
> - A dedicated, Research Lead-authorized compression pass will be required prior to final Section IV integration to bring the whitespace word count under the 560-word ceiling.

### Mathematical Derivation and Content Verification Checklist

1. **State-Space Cardinality:** Bounded by $|S| = |E_s| + 1$ directed edge states ($740,823$ on the Bengaluru simple directed graph).
2. **Min-Heap Operation Derivation:**
   - Strict relaxation without `decrease-key` pushes a new entry upon each successful cost improvement.
   - Total successful insertions across best and suboptimal paths cannot exceed $1 + T_{\text{query}}^{\text{simple}} = 1 + \sum_{u \in V} d_{\text{in}}(u) d_{\text{out}}(u) + d_{\text{out}}(s_0) \le \mathcal{O}(|E_s| d_{\max}^{\text{out}})$.
   - Priority queue push and pop operations on a heap of size $\le \mathcal{O}(|E_s| d_{\max}^{\text{out}})$ incur $\mathcal{O}(|E_s| d_{\max}^{\text{out}} \log(|E_s| d_{\max}^{\text{out}}))$ time.
3. **Successor-Loop and Stale-Pop Accounting:**
   - The implementation does not filter stale entries upon popping; each popped state (best or duplicate) executes its successor loop over up to $d_{\max}^{\text{out}}$ adjacent outgoing edges.
   - Total states popped (best $N_{\text{best}} \le |S|$ plus stale $E_{\text{stale}} \le \sum_u d_{\text{out}}(u) \max(d_{\text{in}}(u)-1, 0) + d_{\text{out}}(s_0)$) are bounded by $\mathcal{O}(|E_s| d_{\max}^{\text{in}})$.
   - Each successor iteration dynamically scans up to $q_{\max}$ multigraph candidates, yielding $\mathcal{O}(q_{\max} |E_s| d_{\max}^{\text{in}} d_{\max}^{\text{out}})$ operations.
4. **Equation (6) Formulation:**
   $$\mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| d_{\max}^{\text{out}} \log(|E_s| d_{\max}^{\text{out}}) + q_{\max} |E_s| d_{\max}^{\text{in}} d_{\max}^{\text{out}} \right), \quad \mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| d_{\max}^{\text{out}} + |V|)$$
   Numbered Equation (6), continuing monotonically from Equation (5).
5. **Bounded-Valence Urban Simplification:**
   - Under explicit topological axioms $d_{\max}^{\text{in}} = \mathcal{O}(1)$, $d_{\max}^{\text{out}} = \mathcal{O}(1)$, and $q_{\max} = \mathcal{O}(1)$, the quadratic degree product collapses to $\mathcal{O}(|E_s|)$ and the heap logarithmic term collapses to $\mathcal{O}(|E_s| \log |E_s|)$, yielding $\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$ and $\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|)$.
6. **Authoritative Concrete Bengaluru Context:**
   - Simple directed graph: $|V| = 308,643$, $|E_s| = 740,822$.
   - Degree bounds: $d_{\max}^{\text{in}} = 6$, $d_{\max}^{\text{out}} = 6$, $q_{\max} = 4$.
   - Graph-wide successor loop upper bound: $I_{\text{total},\text{exact\_sum}} = 2,087,161 + 3,799,631 = \mathbf{5,886,792}$ iterations.
   - Logical memory bound: $\mathcal{M}_{\text{logical}} = 2,087,162 + 740,823 + 740,822 + 308,643 = \mathbf{3,877,450}$ logical entries ($5.234 \times |E_s|$).
7. **Demarcation Between Theoretical Saturation and Empirical Performance:**
   - $5,886,792$ and $3,877,450$ are theoretical graph-wide saturation upper bounds, not observed per-query figures.
   - Ground-truth empirical A0 measurements from [`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) show exploration restricted to $119$ to $129,619$ queue pops ($0.016\%$ to $17.50\%$ of state space) with median runtime of $174.93\text{ ms}$ ($382.98\text{ ms}$ mean).

### Technical Restriction Compliance
- Simple directed graph $|E_s| = 740,822$ is the authoritative basis.
- The multigraph proxy $3,894,189$ is not used as authoritative memory.
- The rejected multigraph proxy $T_{\text{internal}}^{\text{raw}} - |E_s| + 6$ is completely absent.
- $5,886,792$ is explicitly labeled a theoretical saturation bound.
- Memory is defined strictly in logical entries, without speculative conversion to physical bytes or RAM.
- No text drafted beyond Section IV-D.
