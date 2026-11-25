# Section IV-D: Computational Complexity Analysis (Draft v2.0 - Compressed)

**Document:** [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_section_IV_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_outline_v1.md)  
**Parent Blueprint:** [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)  
**Predecessor Draft:** [`paper1_section_IV_D_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v1.md) (141 words)  
**Implementation Source:** [`routing/algorithms.py#L520-L705`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L520-L705)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.2-E COMPRESSED DRAFT COMPLETE (AWAITING LEAD REVIEW)**  
**Effective Date:** 2026-11-06  

---

## Section IV: Turn-Aware A* Algorithm, Correctness and Complexity Analysis

\noindent\textbf{D. Computational Complexity Analysis:} Search operates over $|E_s|+1$ edge states. Lacking a \texttt{decrease-key} operation, relaxation pushes duplicate heap entries that are popped without immediate discard, while transitions scan up to $q_{\max}$ parallel candidates. On general directed graphs, queue operations and successor-loop evaluations yield asymptotic time and logical-memory bounds:
$$\begin{aligned}
\mathcal{T}_{\text{general}} &= \mathcal{O}\left( |E_s| d_{\max}^{\text{out}} \log(|E_s| d_{\max}^{\text{out}}) + q_{\max} |E_s| d_{\max}^{\text{in}} d_{\max}^{\text{out}} \right) \\
\mathcal{M}_{\text{general}} &= \mathcal{O}(|E_s| d_{\max}^{\text{out}} + |V|)
\end{aligned} \tag{6}$$
Under bounded in-degree, out-degree, and parallel multiplicity assumptions ($d_{\max}^{\text{in}}, d_{\max}^{\text{out}}, q_{\max} = \mathcal{O}(1)$), these expressions simplify to $\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$ and $\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|)$ logical entries. On the evaluated Bengaluru network ($|V|=308,643$, $|E_s|=740,822$, $d_{\max}^{\text{in}}=d_{\max}^{\text{out}}=6$, $q_{\max}=4$), network saturation yields theoretical upper bounds of $5,886,792$ successor-loop iterations and $3,877,450$ logical memory entries across persistent structures. These theoretical saturation limits differ from empirical query performance, where heuristic guidance prunes exploration to $119$–$129,619$ queue pops across 25 commute corridors (median latency: $174.93\text{ ms}$).

---

## Subsection IV-D Word Count and Quality Audit

| Metric | Target Budget | Draft v1.0 | Draft v2.0 Value | Variance | Compliance Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Body Word Count (Whitespace Split, excl. Eq. 6)** | 120–160 words | 141 words | **125 words** | $-16\text{ words}$ | **EXACT FIT (Within Budget)** |
| **Body Word Count (LaTeX Math as Single Token)** | 110–150 words | 130 words | **114 words** | $-16\text{ words}$ | **EXACT FIT (Within Budget)** |
| **Display Equations** | Exactly 1 | 1 | **1 (Equation 6)** | $0$ | **COMPLIANT** |
| **Float Assets (Algorithms / Figures)** | 0 | 0 | **0** | $0$ | **COMPLIANT** |

### Mathematical Preservation Checklist
- **State Space Base:** Grounded in $|E_s|+1$ edge states on the effective simple graph.
- **Heap Operation & Duplicates:** Explicitly accounts for min-heap lacking `decrease-key`, duplicate entries pushed, and absence of immediate stale-pop discard.
- **Parallel Scanning Multiplicity:** Explicitly accounts for dynamic parallel candidate scanning up to $q_{\max}$.
- **Equation (6):** Retains exact formulations $\mathcal{T}_{\text{general}}$ and $\mathcal{M}_{\text{general}}$ tagged as Eq. (6).
- **Bounded-Valence Simplification:** Retains explicit assumptions ($d_{\max}^{\text{in}}, d_{\max}^{\text{out}}, q_{\max} = \mathcal{O}(1)$) yielding $\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$ and $\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|)$.
- **Bengaluru Empirical Graph Context:** Retains $|V|=308,643$, $|E_s|=740,822$, $d_{\max}^{\text{in}}=d_{\max}^{\text{out}}=6$, $q_{\max}=4$.
- **Graph-Wide Saturation Bounds:** Retains $5,886,792$ successor-loop iterations and $3,877,450$ logical memory entries ($5.234 \times |E_s|$).
- **Empirical Query Demarcation:** Retains explicit distinction from empirical query performance ($119$–$129,619$ queue pops, $174.93\text{ ms}$ median latency).
