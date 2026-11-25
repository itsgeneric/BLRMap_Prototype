# Paper 1 Blueprint Feasibility Audit

**Document:** [`paper1_blueprint_feasibility_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_blueprint_feasibility_audit.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Parent Blueprint:** [`paper1_structural_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_structural_blueprint.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **CRITICAL FEASIBILITY EVALUATION**

---

## 1. Critical Evaluation of the Phase 4.1 Proposed Budget

The Phase 4.1 blueprint proposed a layout consisting of:
- Approximately $3,550$ words of body text.
- Three figures (Figs. 1, 2, 3).
- Three tables (Tables I, II, III).
- One algorithm box (Algorithm 1, $\approx 28$ lines).
- Eight display equations.
- Sixteen references.
- Exactly 6.0 pages in IEEE two-column format.

### 1.1 The Reality of IEEE Two-Column Typography
In standard IEEE conference formatting (`IEEEtran.cls`, `conference`, $10\text{ pt}$ text on $12\text{ pt}$ leading, column width $3.5\text{ in}$, text height $9.25\text{ in}$):
1. **Column Line Capacity:** Exactly $55\text{ lines}$ of body text fit into one full column without headings or floats ($\approx 425\text{--}450\text{ words}$).
2. **Title & Abstract Header:** The span across Page 1 consumes $2.5\text{--}3.0\text{ in}$ vertically, eliminating $\approx 30\%$ of Page 1's text area ($-270\text{ words equivalent}$).
3. **Bibliography Footprint:** A 16-citation IEEE bibliography ($9\text{ pt}$ font, $10.5\text{ pt}$ leading, $\approx 3.5\text{ lines}$ per entry) requires $56\text{ lines}$. This **exceeds one entire column** ($55\text{ lines}$). Confining 16 references to Page 6 Column 2 alone is typography-impossible without truncation; the bibliography will inevitably spill into the lower half of Page 6 Column 1.
4. **Float Separation Overhead:** Every figure and table incurs LaTeX vertical skip penalties (`\textfloatsep`, `\intextsep`, `\dbltextfloatsep` $\approx 10\text{ pt}$ above and below). For 6 floats plus an algorithm box, spacing penalties consume an additional $\approx 1.5\text{ columns}$ of text height.

### 1.2 Quantitative Capacity Breakdown

| Component | Proposed Item Count | Physical Height in Points / Inches | Word Count Equivalent |
| :--- | :---: | :---: | :---: |
| **Title, Authors, Abstract, Index Terms** | 1 Header Banner | $180\text{ pt}$ ($2.5\text{ in}$) across 2 cols | $280\text{ words}$ |
| **3 Figures (Figs. 1, 2, 3)** | 3 Single-Column Floats | $520\text{ pt}$ ($7.2\text{ in}$) total | $390\text{ words}$ |
| **3 Tables (Tables I, II, III)** | 3 Single-Column Floats | $450\text{ pt}$ ($6.2\text{ in}$) total | $340\text{ words}$ |
| **1 Algorithm Box (Algorithm 1)** | 1 Single-Column Float | $280\text{ pt}$ ($3.9\text{ in}$) | $210\text{ words}$ |
| **8 Display Equations** | 8 Equations + Padding | $180\text{ pt}$ ($2.5\text{ in}$) | $140\text{ words}$ |
| **Headings & Section Spacing** | 7 Level-1, 10 Level-2 | $260\text{ pt}$ ($3.6\text{ in}$) | $200\text{ words}$ |
| **16 References** | 16 Citations (BibTeX) | $600\text{ pt}$ ($8.3\text{ in}$, ~1.1 cols) | $460\text{ words}$ |
| **SUBTOTAL NON-TEXT FOOTPRINT** | — | **$\approx 2,470\text{ pt}$ ($\approx 34.3\text{ in}$ / 5.5 cols)** | **$\approx 2,020\text{ words}$** |
| **Total 6-Page Raw Capacity** | 12 Full Columns | $7,992\text{ pt}$ ($111.0\text{ in}$ / 12 cols) | $\approx 5,280\text{ words}$ |
| **MAXIMUM ACHIEVABLE BODY TEXT** | — | **$\approx 5,520\text{ pt}$ ($\approx 6.5\text{ cols}$)** | **$\mathbf{\le 3,100\text{ words}}$** |

### 1.3 Feasibility Verdict
**The Phase 4.1 target of 3,550 body text words is INFEASIBLE.**  
At $3,550$ words plus 7 floats, 8 equations, and 16 references, the compiled LaTeX document will span **6.8 to 7.2 pages**, violating the mandatory 6-page limit.

**Mandated Adjustments:**
1. Body text must be strictly capped between **$2,800$ and $3,050$ words** (excluding abstract and references).
2. Total manuscript word count (including abstract, captions, and references) must not exceed **$3,600$ words**.
3. Floats must be prioritized and condensed to eliminate vertical dead space.

---

## 2. Priority Ranking and Float Condensation Strategy

To safeguard the 6.0-page boundary, all floats, equations, and pseudo-code are ranked by academic value:

### 2.1 Priority Ranking

| Priority Rank | Asset ID | Asset Description | Section | Essentiality Rating | Action if Space Exceeded |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **Rank 1** | **Fig. 1** | Algorithmic Trade-offs of Turn Awareness (Exp A: sharp turns, runtime, states) | Section VI-A | **CRITICAL** (Must Keep) | Non-negotiable core figure. |
| **Rank 2** | **Table III** | Paired Inferential Statistical Hypothesis Test Results (Families A, B, C, D) | Section VI-E | **CRITICAL** (Must Keep) | Non-negotiable evidence anchor. |
| **Rank 3** | **Fig. 3** | Turn Sensitivity Response & Empirical Pareto Knee ($C_2: 25/8$) | Section VI-C | **HIGH** (Must Keep) | Essential for proving the non-dominated Pareto knee. |
| **Rank 4** | **Fig. 2** | Metropolitan Road-Class Exposure Under Impedance (Exp B) | Section VI-B | **HIGH** (Must Keep) | Core visual for $-51.21\text{ pp}$ arterial drop. |
| **Rank 5** | **Table I** | Road-Class Impedance Multipliers and Flyover Override Factors | Section III-B | **MEDIUM** (Condense) | Condense to 6 compact rows. |
| **Rank 6** | **Table II** | Controlled Factorial Ablation Matrix (Exp A–D Conditions) | Section V-C | **LOW** (Condense / Remove) | **Prime candidate to merge into Section V text.** |
| **Rank 7** | **Algorithm 1** | Pseudo-code Box for `two_wheeler_astar` | Section IV-E | **DISPENSABLE** (Prime Cut) | **First candidate to eliminate.** Equations (3)–(8) already define the algorithm completely. |

---

## 3. Specific Condensation Plan

1. **Eliminate Algorithm 1 Float Box:**  
   In IEEE conference papers, standard A* pseudo-code (initializing `open_set`, `heappop`, `successors`, `heappush`) is considered textbook padding. Section IV already provides the formal state space $S = E \cup \{(\text{None}, s_0)\}$, transition cost $c(s, s') = \ell \cdot \mu + P_{\text{turn}}$, heuristic $h(s) = 0.80 \cdot D_{\text{haversine}}$, and Theorems 1–3. Replacing Algorithm 1 with a 3-line inline mathematical definition saves $280\text{ pt}$ ($3.9\text{ in}$ / $0.45\text{ column}$), instantly buying back $\approx 200\text{ words}$ of text headroom.
2. **Compress Table II into Section V Text:**  
   Listing conditions $A_0\text{--}A_2, B_0\text{--}B_2, C_0\text{--}C_3, D_1\text{--}D_4$ in Table II duplicates Table III. Integrating condition definitions directly into Section V-C saves another $160\text{ pt}$ ($2.2\text{ in}$ / $0.25\text{ column}$).
3. **Bibliography Spacing Optimization:**  
   The 16 references must be formatted with condensed field styles (using DOI links rather than separate URL strings, avoiding unnecessary issue numbers) to ensure they fit cleanly in $\approx 50\text{ lines}$ across the lower half of Page 6.

---

*Feasibility audit concluded under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
