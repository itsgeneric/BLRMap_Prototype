# Paper 1 Six-Page Budget and Page Allocation Plan

**Document:** [`paper1_six_page_budget.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_six_page_budget.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Length:** Exactly 6.0 Pages (12 Columns)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE SPACE & BUDGET ALLOCATION**

---

## 1. IEEE Two-Column Formatting Parameters

To ensure an airtight page budget that neither overflows into Page 7 nor underfills Page 6, the following standard IEEE conference typography parameters are enforced:

- **Trim Size & Layout:** US Letter ($8.5 \times 11.0\text{ in}$), 2-column layout.
- **Margins:** Top $0.75\text{ in}$, Bottom $1.0\text{ in}$, Left/Right $0.625\text{ in}$, Column Separation $0.25\text{ in}$.
- **Column Dimensions:** Column Width $3.50\text{ in}$ ($88.9\text{ mm}$); Column Height $9.25\text{ in}$ ($235\text{ mm}$).
- **Typography:**
  - Body Text: $10\text{ pt}$ Times New Roman, $12\text{ pt}$ line leading ($\approx 55\text{ lines}$ per full column $\approx 425\text{--}450\text{ words}$).
  - Section Headings: $10\text{ pt}$ Small Caps (Level 1), $10\text{ pt}$ Italic (Level 2).
  - Abstract & Index Terms: $9\text{ pt}$ bold/italic ($\approx 200\text{ words}$).
  - Tables & Captions: $8\text{ pt}$ / $9\text{ pt}$ Times New Roman.
  - References: $9\text{ pt}$ font, $10.5\text{ pt}$ leading ($\approx 15\text{--}18\text{ citations}$ per column).

---

## 2. Page-by-Page Space Budget Matrix

| Page # | Column | Section & Primary Content | Estimated Word Count | Figures / Tables / Floats | Equations | Total Column Fraction |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **Page 1** | Col 1 | **Title, Authors, Abstract, Index Terms**<br/>**I. Introduction (Paras 1–2):** Urban two-wheeler context & OSRM failures | 200 (Abstract)<br/>240 (Intro) | Title Banner across both cols ($1.8\text{ in}$ high) | 0 | **1.00 Col** |
| | Col 2 | **I. Introduction (Paras 3–4):** Gap & 4 Contributions<br/>**II. Related Work (Paras 1–2):** Turn-cost routing & Two-wheeler choice | 220 (Intro)<br/>210 (Related) | None | 0 | **1.00 Col** |
| **Page 2** | Col 1 | **II. Related Work (Para 3):** Heuristic search & Demarcation<br/>**Table I:** Road-Class Penalties & Fallback Values<br/>**III. Problem Formulation (Paras 1–2):** Road graph & Multiplier | 140 (Related)<br/>180 (Prob Form) | **Table I** ($1\text{ col} \times 1.8\text{ in}$, Road Impedance Map) | (1), (2) | **1.00 Col** |
| | Col 2 | **III. Problem Formulation (Paras 3–5):** Turn penalty function, Lemma 1, State-space $S$, Transition cost $c(s, s')$ | 320 (Prob Form) | None | (3), (4), (5) | **1.00 Col** |
| **Page 3** | Col 1 | **IV. Proposed Turn-Aware Algorithm (Paras 1–3):** State transitions, Scaled Heuristic, Theorem 1 (Admissibility proof), Theorem 2 (Consistency proof) | 360 (Algorithm) | None | (6), (7), (8) | **1.00 Col** |
| | Col 2 | **Corollary 1 & Theorem 3 (Complexity):** Valence bounds & min-heap duplicate dynamics<br/>**Algorithm 1:** Turn-Aware State-Expanded A* Pseudo-code | 160 (Algorithm) | **Algorithm 1** ($1\text{ col} \times 4.2\text{ in}$ float box) | None | **1.00 Col** |
| **Page 4** | Col 1 | **V. Experimental Setup & Methodology (Paras 1–4):** Graph environment, Corpus, Factorial design, Statistical inference<br/>**Table II:** Factorial Matrix (A–D) | 260 (Setup) | **Table II** ($1\text{ col} \times 2.0\text{ in}$, Ablation Conditions Matrix) | None | **1.00 Col** |
| | Col 2 | **VI. Results: Exp A (Turn Awareness):** $34.1\%$ turn reduction, A1 vs A2 geometric identity, runtime overhead breakdown<br/>**Fig. 1:** Exp A Trade-offs (Boxplots) | 220 (Results) | **Fig. 1** ($1\text{ col} \times 2.6\text{ in}$, Boxplots of turns, runtime, states) | None | **1.00 Col** |
| **Page 5** | Col 1 | **VI. Results: Exp B (Road Classes):** $-51.21\text{ pp}$ arterial, $+30.73\text{ pp}$ residential<br/>**Fig. 2:** Exp B Distribution (Bar chart)<br/>**VI. Results: Exp C (Turn Sensitivity):** $C_0 \to C_3$ monotonic response | 240 (Results) | **Fig. 2** ($1\text{ col} \times 2.2\text{ in}$, Road-Class Exposure Chart) | None | **1.00 Col** |
| | Col 2 | **Fig. 3:** Exp C Sensitivity & Pareto Knee ($C_2$ knee)<br/>**VI. Results: Exp D (Bridge):** $+148.9\%$ bridge traversal<br/>**VI. Results: Runtime & Scalability:** $174.93\text{ ms}$ median | 210 (Results) | **Fig. 3** ($1\text{ col} \times 2.2\text{ in}$, Pareto Curve & Knee Plot)<br/>**Table III** ($1\text{ col} \times 2.2\text{ in}$, Paired Hypothesis Tests) | None | **1.00 Col** |
| **Page 6** | Col 1 | **VII. Limitations & Discussion (Paras 1–3):** Construct validity, sequential modifier floor, min-heap multiplicity<br/>**VII. Conclusion & Future Work (Para 4)**<br/>**Acknowledgment & Data Availability** | 380 (Discussion)<br/>120 (Conclusion)<br/>50 (Ack) | None | None | **1.00 Col** |
| | Col 2 | **References:** Exactly 16 fully formatted IEEE citations spanning historical foundations, two-wheeler modeling, heuristic theory, and street networks | ~55 lines (~350 words) | None (Standard IEEE BibTeX style) | None | **1.00 Col** |

---

## 3. Section-by-Section Word, Float, and Equation Count

| Section | Target Pages | Estimated Words | Floats (Figures & Tables) | Mathematical Equations |
| :--- | :---: | :---: | :---: | :---: |
| **Title, Abstract & Index Terms** | Page 1 | 240 words | None (Title Banner) | 0 |
| **I. Introduction** | Pages 1–2 | 460 words | None | 0 |
| **II. Related Work** | Pages 1–2 | 350 words | None | 0 |
| **III. Problem Formulation & Model** | Page 2 | 500 words | **Table I** (Road Impedance Table) | Eq. (1) to Eq. (5) |
| **IV. Proposed Turn-Aware Algorithm** | Page 3 | 520 words | **Algorithm 1** (Pseudo-code Box) | Eq. (6) to Eq. (8) |
| **V. Experimental Setup & Protocol** | Page 4 | 260 words | **Table II** (Ablation Matrix) | 0 |
| **VI. Experimental Results & Analysis** | Pages 4–5 | 670 words | **Fig. 1**, **Fig. 2**, **Fig. 3**, **Table III** | 0 |
| **VII. Limitations, Discussion & Conclusion** | Page 6 | 550 words | None | 0 |
| **References (16 Citations)** | Page 6 | ~350 words equivalent | None | 0 |
| **TOTALS** | **Exactly 6.0 Pages** | **~3,550 Words** | **3 Figures, 3 Tables, 1 Algorithm** | **8 Display Equations** |

---

## 4. Float Geometry and Height Validation

To prevent vertical overflow in LaTeX compilation:

1. **Table I (Road Impedance Mapping):** Single column, 8 rows, height $\approx 1.8\text{ in}$. Placed at top of Page 2, Column 1.
2. **Algorithm 1 (Pseudo-code Box):** Single column, 28 lines, height $\approx 4.2\text{ in}$. Placed in Page 3, Column 2.
3. **Table II (Ablation Conditions Matrix):** Single column, 7 rows, height $\approx 2.0\text{ in}$. Placed at top of Page 4, Column 1.
4. **Figure 1 (Exp A Trade-offs):** Single column, height $\approx 2.6\text{ in}$ ($300\text{ DPI}$). Placed at top of Page 4, Column 2.
5. **Figure 2 (Exp B Road-Class Exposure):** Single column, height $\approx 2.2\text{ in}$ ($300\text{ DPI}$). Placed at middle of Page 5, Column 1.
6. **Figure 3 (Exp C Pareto Sensitivity Knee):** Single column, height $\approx 2.2\text{ in}$ ($300\text{ DPI}$). Placed at top of Page 5, Column 2.
7. **Table III (Statistical Hypothesis Results):** Single column, 8 rows, height $\approx 2.2\text{ in}$. Placed at bottom of Page 5, Column 2.

**Total Float Footprint:**
- Page 2: 1 table ($1.8\text{ in}$ / $9.25\text{ in} \approx 20\%$ of 1 col).
- Page 3: 1 algorithm box ($4.2\text{ in}$ / $9.25\text{ in} \approx 45\%$ of 1 col).
- Page 4: 1 table ($2.0\text{ in}$) + 1 figure ($2.6\text{ in}$) ($\approx 25\%$ of col 1 and $\approx 28\%$ of col 2).
- Page 5: 2 figures ($2.2\text{ in}$ each) + 1 table ($2.2\text{ in}$) ($\approx 24\%$ of col 1 and $\approx 47\%$ of col 2).
- Page 6: Zero floats; Column 1 is entirely text; Column 2 is entirely references.

---

*Six-page budget verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
