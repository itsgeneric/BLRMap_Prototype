# Paper 1 Final Page Budget (v1.0 Frozen)

**Document:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Compiled Constraint:** Exactly 6.0 Pages (12 Columns)  
**Parent Budget:** [`paper1_revised_six_page_budget.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_revised_six_page_budget.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **FROZEN PRODUCTION PAGE BUDGET**

---

## 1. Frozen Manuscript Planning Targets

The following planning targets are formally frozen for the manuscript authoring phase:

- **Body Text Word Count:** **$\approx 2,850\text{ words}$** (Strict Safety Range: **$2,750\text{--}3,000\text{ words}$**).
- **Abstract & Index Terms:** **$\approx 220\text{ words}$**.
- **Publication Figures:** **Exactly 3 Figures** (Figs. 1, 2, 3, all single-column).
- **Publication Tables:** **Exactly 2 Tables** (Table I: Road Impedance, 6 rows; Table II: Statistical Results, 7 rows).
- **Display Equations:** **Exactly 6 Display Equations** (Eqs. 1 to 6).
- **Verified References:** **Exactly 16 Audited Citations** ($\approx 52\text{ lines}$, requiring $\approx 0.95\text{ column}$).
- **Total Estimated Manuscript Footprint:** **$\approx 3,420\text{ words equivalent}$**.

> [!WARNING]
> **Compilation Reality Warning:**  
> A target word budget of $2,850\text{ words}$ does not automatically guarantee that the compiled PDF will terminate on Page 6. Actual LaTeX page budgets are determined by typographic glue, float placement queues, paragraph widow/orphan penalties, and BibTeX entry line breaks. Six pages is the **absolute, non-negotiable compiled limit**.

---

## 2. Frozen Section-by-Section Space Allocation

| Section | Headings & Core Content | Target Words | Float Assets | Equations | Allocated Pages & Columns |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **Header** | Title, Authors, Abstract, Index Terms | 220 words | Title Banner across 2 cols | None | Page 1, Top ($2.2\text{ in}$) |
| **I** | Introduction (Context, OSRM limits, Gap, Contributions) | 450 words | None | None | Page 1, Col 1 bot & Col 2 top |
| **II** | Related Work (Turn costs, Two-wheeler choice, Demarcation) | 340 words | None | None | Page 1, Col 2 bot & Page 2, Col 1 top |
| **III** | Problem Formulation & Mathematical Model | 470 words | **Table I** (Road Impedance, $1.6\text{ in}$) | Eqs. (1)–(3) | Page 2, Col 1 bot & Col 2 full |
| **IV** | Proposed Turn-Aware Routing Algorithm | 480 words | None (Math search specification) | Eqs. (4)–(6) | Page 3, Col 1 & Col 2 full |
| **V** | Experimental Setup & Methodology | 280 words | None (Conditions integrated into text) | None | Page 4, Col 1 top |
| **VI** | Experimental Results & Analysis (Exp A–D & Runtime) | 600 words | **Fig. 1** ($2.5\text{ in}$), **Fig. 2** ($2.1\text{ in}$), **Fig. 3** ($2.1\text{ in}$), **Table II** ($2.1\text{ in}$) | None | Page 4, Col 2 full & Page 5 full |
| **VII** | Limitations, Discussion, and Conclusion | 510 words | None | None | Page 6, Col 1 full |
| **Refs** | References (16 Audited Peer-Reviewed Citations) | ~350 equiv. | None | None | Page 6, Col 2 full |
| **TOTALS** | **Frozen Manuscript Architecture** | **$\approx 3,420\text{ words}$** | **3 Figures, 2 Tables, 0 Algorithm Boxes** | **6 Equations** | **Exactly 6.0 Pages (12.0 Cols)** |

---

## 3. Pre-Ranked Emergency Trimming Sequence

If initial LaTeX compilation spills into Page 7 (even by a single line), text will be shortened strictly in accordance with this pre-ranked emergency sequence:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PRE-RANKED EMERGENCY TRIMMING SEQUENCE                          │
├──────┬───────────────────────────────┬───────────────────────────┬─────────────────────┤
│ Step │ Target Section / Component    │ Specific Trimming Action  │ Headroom Recovered  │
├──────┼───────────────────────────────┼───────────────────────────┼─────────────────────┤
│ 1    │ Section II (Related Work)     │ Condense speedup and      │ -90 words           │
│      │                               │ multi-criteria background │ (~12 lines)         │
├──────┼───────────────────────────────┼───────────────────────────┼─────────────────────┤
│ 2    │ Section VII (Limitations)     │ Shorten implementation    │ -90 words           │
│      │                               │ and single-thread text    │ (~12 lines)         │
├──────┼───────────────────────────────┼───────────────────────────┼─────────────────────┤
│ 3    │ Display Equations             │ Inline Eq. (1) and        │ -40 words equiv.    │
│      │                               │ Eq. (4) into body text    │ (~6 lines)          │
├──────┼───────────────────────────────┼───────────────────────────┼─────────────────────┤
│ 4    │ Table I (Road Impedance)      │ Condense from 6 rows      │ -30 words equiv.    │
│      │                               │ to 4 compact grouped rows │ (~4 lines)          │
├──────┼───────────────────────────────┼───────────────────────────┼─────────────────────┤
│ 5    │ Section I (Introduction)      │ Streamline background     │ -70 words           │
│      │                               │ paragraphs 1 and 2        │ (~9 lines)          │
├──────┴───────────────────────────────┴───────────────────────────┼─────────────────────┤
│ TOTAL CONTINGENCY TRIMMING HEADROOM AVAILABLE                    │ -320 words equiv.   │
│                                                                  │ (~43 lines / 0.8 col│
└──────────────────────────────────────────────────────────────────┴─────────────────────┘
```

This ensures that the authoring agent can rapidly resolve any vertical overflow during typesetting without compromising experimental data, mathematical proofs, or citation counts.

---

*Page budget v1.0 frozen under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
