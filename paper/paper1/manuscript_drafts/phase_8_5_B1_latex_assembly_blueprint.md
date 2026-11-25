# Phase 8.5-B1-R1: Paper 1 LaTeX Assembly Blueprint (Corrected)

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (Standard IEEE Two-Column `IEEEtran`, 6.0 Pages Maximum)  
**Document:** [`phase_8_5_B1_latex_assembly_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_5_B1_latex_assembly_blueprint.md)  
**Date:** 2026-11-07  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **REVISED ASSEMBLY BLUEPRINT COMPLETE (PLANNING AND READINESS ONLY)**

---

## 1. Executive Summary & Protocol Boundaries

This revised document establishes the corrected, implementation-ready architectural blueprint for assembling Paper 1 into a unified LaTeX document (`paper1_main.tex`). It remedies the structural mapping of Section III, rebuilds the provisional page layout plan without invented paragraph counts or unapproved acknowledgments, and explicitly categorizes toolchain dependencies.

### Strict Planning Preconditions
- **Zero Assembly Execution:** No `.tex` files have been created. No compiler (`pdflatex`, `xelatex`, `latexmk`) has been invoked.
- **Zero Template Modification:** No IEEE templates, bibliography files, figures, tables, or frozen manuscript files have been altered.
- **Strict Scope Boundaries:** Paper 2 algorithms (Perpendicular Offset alternative routing) and experimental datasets (Experiment E, Figure 4) are **strictly excluded**.
- **Empirical Layout Rule:** In accordance with research protocol, no guarantee of exact 6.0-page compliance is asserted prior to actual compilation, micro-typographical tuning, and visual PDF inspection.

---

## 2. Template and Toolchain Readiness Matrix

An exhaustive environment inspection was conducted to differentiate between **confirmed absence within workspace**, **paths restricted by sandbox boundaries**, and **dependencies requiring staging**:

### 2.1 Toolchain Readiness Matrix

| Component | Target Requirement | Status in Environment | Verification Method | Diagnostic Findings & Staging Plan |
| :--- | :--- | :---: | :--- | :--- |
| **`IEEEtran.cls`** | Official IEEE Class (v1.8b) | **CONFIRMED MISSING FROM WORKSPACE** | Recursive workspace scan | File does not exist in `research/paper1_manuscript/` or anywhere in workspace. Must be staged into manuscript directory prior to build. |
| **`IEEEtran.bst`** | Official IEEE BibTeX style | **CONFIRMED MISSING FROM WORKSPACE** | Recursive workspace scan | File does not exist in project workspace. Must be staged into manuscript directory prior to build. |
| **`pdflatex`** | Default IEEEtran compiler | **CONFIRMED MISSING FROM PATH** | `shutil.which('pdflatex')` | Binary is absent from system PATH and `C:\Users\comps\.local\bin`. Retained as default compiler target. |
| **`bibtex`** | Citation processor | **CONFIRMED MISSING FROM PATH** | `shutil.which('bibtex')` | Binary is absent from system PATH. Required for bibliography resolution. |
| **`xelatex` / `latexmk`** | Alternate TeX engines | **CONFIRMED MISSING FROM PATH** | `shutil.which(...)` | Binaries are absent from system PATH. |
| **Standard TeX Trees** | TeX Live / MiKTeX | **CONFIRMED MISSING FROM STANDARD PATHS** | Filesystem inspection | Checked `C:\texlive`, `C:\Program Files\MiKTeX`, `C:\Program Files (x86)\MiKTeX`, and `C:\ProgramData\chocolatey`. None exist. |
| **Host User Directories** | Local user installs | **INACCESSIBLE / NOT INSPECTED** | Security boundary check | Host folders outside workspace (`Downloads`, `AppData`, etc.) cannot be accessed in standard sandbox mode (`BypassSandbox: false`). |

### 2.2 Compilation Path Dependencies
To enable automated assembly and PDF generation in subsequent phases:
1. `IEEEtran.cls` and `IEEEtran.bst` must be staged directly into `research/paper1_manuscript/`.
2. A working `pdflatex` compiler and `bibtex` executable must be staged or made accessible in the execution environment.
3. Zero downloads or installations have been performed during this planning phase.

---

## 3. Canonical Assembly Source Mapping

The unified LaTeX manuscript (`paper1_main.tex`) will be constructed by mapping frozen markdown sources and publication assets directly into standard IEEEtran document environments:

| Manuscript Unit | Target LaTeX Environment / Macro | Canonical Frozen Source Document | Source Lines / Locators | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **Document Class** | `\documentclass[conference]{IEEEtran}` | Standard IEEE CSNT Template | — | Specification Ready |
| **Preamble Packages** | `amsmath,amssymb,amsfonts,graphicx,cite,booktabs,array,url` | Standard IEEE Stack | — | Ready |
| **Title** | `\title{Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks}` | Blueprint Title Metadata | — | **FROZEN** |
| **Author Block** | `\author{...}` | **UNRESOLVED STATUS** | Pending Lead Confirmation | **UNRESOLVED** *(No names/affiliations assumed)* |
| **Abstract** | `\begin{abstract} ... \end{abstract}` | [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | Line 15 (208 words) | **FROZEN** |
| **Index Terms** | `\begin{IEEEkeywords} ... \end{IEEEkeywords}` | [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | Line 29 (7 terms, 16 words) | **FROZEN** |
| **Section I (Intro)** | `\section{Introduction}` | [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | Lines 18, 20, 22, 24, 26, 28 (468 words) | **FROZEN** |
| **Section II (Related)** | `\section{Related Work}` | [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | Lines 20, 22, 24, 26 (349 words) | **FROZEN** |
| **Section III (Problem)** | `\section{Problem Formulation and Configured Road Impedance}` | [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) | Subsections III-A through III-D (529 words) | **FROZEN** |
| **— Subsection III-A** | `\noindent\textbf{Directed Road-Network and Routing Problem:}` | `paper1_section_III_v1.md` | Line 19 (128 words; multigraph $G_{\text{raw}}$, simple graph $G=(V,E_s)$, $c_{\min}$, $D(P)$, $C(P)$) | **FROZEN** |
| **— Subsection III-B** | `\noindent\textbf{Edge-Based State Representation:}` | `paper1_section_III_v1.md` | Line 21 (113 words; edge states $s=(u,v)$, synthetic root $(\text{None}, s_0)$, $|S|=|E_s|+1=740,823$) | **FROZEN** |
| **— Subsection III-C** | `\noindent\textbf{Angular Turn-Deflection Model:}` | `paper1_section_III_v1.md` | Lines 23, 25, 31 (114 words; azimuth deflection $\Delta\theta$, unnumbered deflection formula) | **FROZEN** |
| **— Equation (1)** | `\begin{equation} P_{\text{turn}} = \dots \end{equation}` | `paper1_section_III_v1.md` | Lines 26–30 (Discrete piecewise turn penalties: $25.0, 8.0, 0.0\text{ m}$) | **FROZEN** |
| **— Subsection III-D** | `\noindent\textbf{Configured Road-Impedance Model and Objective Function:}` | `paper1_section_III_v1.md` | Lines 33, 38, 40, 45 (174 words; hierarchy weights, bridge $0.80$, roundabout $0.95$, verified $\mu \ge 0.80$) | **FROZEN** |
| **— Equation (2)** | `\begin{equation} \mu(e) = \dots \end{equation}` | `paper1_section_III_v1.md` | Lines 34–37 (Composite road-class multiplier formula) | **FROZEN** |
| **— Equation (3)** | `\begin{equation}\begin{aligned} c(s,s') &= \dots \\ C(P) &= \dots \end{aligned}\end{equation}` | `paper1_section_III_v1.md` | Lines 41–44 (Transition cost $c(s,s')$ & path objective $C(P)$) | **FROZEN** |
| **— Table I** | `\begin{table}[t] ... \end{table}` | `paper1_section_III_v1.md` | Lines 52–75 (Configured multipliers: Part A base, Part B modifiers) | **FROZEN** |
| **Section IV (Turn A*)** | `\section{Turn-Aware $A^*$ Algorithm, Correctness and Complexity Analysis}` | `paper1_section_IV_A`–`D_draft_v2.md` | 4 modular subsections (529 words) | **FROZEN** |
| **— Subsection IV-A** | `\noindent\textbf{A. Turn-Aware State-Expanded Search...}` | [`paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md) | Line 18 (129 words; priority queue, relaxation, termination) | **FROZEN** |
| **— Subsection IV-B** | `\noindent\textbf{B. Scaled Haversine Heuristic...}` | [`paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md) | Lines 18, 20 (90 words; $\mu_{\min}=0.80$ motivation) | **FROZEN** |
| **— Equation (4)** | `\begin{equation} h(s) = \dots \end{equation}` | `paper1_section_IV_B_draft_v2.md` | Line 19 (Scaled Haversine heuristic $h(s) = 0.80 D_{\text{haversine}}$) | **FROZEN** |
| **— Subsection IV-C** | `\noindent\textbf{C. Heuristic Admissibility...}` | [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md) | Lines 18, 20 (185 words; 4 conditions, optimality guarantee) | **FROZEN** |
| **— Equation (5)** | `\begin{equation} h(s) \le c(s,s') + h(s') \end{equation}` | `paper1_section_IV_C_draft_v2.md` | Line 19 (Monotonic consistency condition) | **FROZEN** |
| **— Subsection IV-D** | `\noindent\textbf{D. Computational Complexity...}` | [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md) | Lines 18, 23 (125 words; graph saturation vs. query empirical pops) | **FROZEN** |
| **— Equation (6)** | `\begin{equation}\begin{aligned} ... \end{aligned}\end{equation}` | `paper1_section_IV_D_draft_v2.md` | Lines 19–22 (Asymptotic complexity bounds $\mathcal{T}_{\text{general}}, \mathcal{M}_{\text{general}}$) | **FROZEN** |
| **Section V (Setup)** | `\section{Experimental Setup and Methodology}` | [`paper1_section_V_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_V_draft_v1.md) | Subsections V-A–C (227 words; network model, 25 corridors, baselines) | **FROZEN** |
| **Section VI (Results)** | `\section{Experimental Results and Discussion}` | [`paper1_section_VI_draft_v4.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VI_draft_v4.md) | Subsections VI-A–E (644 words; Experiments A–D, inferential tests) | **FROZEN** |
| **— Figure 1** | `\begin{figure}[t] ... \includegraphics{fig1...}` | `13_ablation_study/figures/fig1_exp_a_tradeoffs.png` | Section VI-A (Exp. A trade-offs: turns, runtime, states) | **VERIFIED** |
| **— Figure 2** | `\begin{figure}[t] ... \includegraphics{fig2...}` | `13_ablation_study/figures/fig2_exp_b_road_classes.png` | Section VI-B (Exp. B road classes: arterial vs. residential shift) | **VERIFIED** |
| **— Figure 3** | `\begin{figure}[t] ... \includegraphics{fig3...}` | `13_ablation_study/figures/fig3_exp_c_sensitivity.png` | Section VI-C (Exp. C sensitivity: Pareto trade-off knee at $C_2$) | **VERIFIED** |
| **— Table II** | `\begin{table}[t] ... \end{table}` | `paper1_section_VI_draft_v4.md` | Lines 86–109 (Primary paired inferential hypothesis test results) | **FROZEN** |
| **Section VII (Concl)** | `\section{Conclusion and Future Work}` | [`paper1_section_VII_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VII_draft_v1.md) | 4 paragraphs (287 words; contributions, findings, limitations, future) | **FROZEN** |
| **References** | `\bibliographystyle{IEEEtran}\bibliography{...}` | [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib) | 14 cited entries (Phase 5.5 frozen bib) | **FROZEN** |

*(Note on Section III structure: Section III consists strictly of Subsections III-A through III-D, totaling 529 whitespace words. No Subsection III-E exists).*

---

## 4. Citation and Bibliography Mapping

### 4.1 Authoritative Bibliography Determination
- **Authoritative File:** [`research/paper1_literature/paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)
- **Status:** Formally frozen in Phase 5.5 (SHA-256: `7F05C88479225D4AB84B3529EBB22528420A1D40CD182B26698A9370416BA028`).
- **Justification:** Dedicated exclusively to Paper 1. Contains complete metadata, DOIs, and IEEE-compliant field structures for all 14 cited works. `master_bibliography.bib` contains Paper 2 references (e.g. `lee2023`, `du2021`, `abbas2022`) which are out of scope.

### 4.2 Citation Cross-Verification Matrix

All 14 citation keys called in manuscript prose were cross-audited against `paper1_verified_references.bib`:

| # | Citation Key in Prose | Canonical Section | Cited Authors & Year | Publication Venue & Scope | Verification in BibTeX |
| :---: | :--- | :---: | :--- | :--- | :---: |
| 1 | `asvial2020entropy` | Sec. I, II | Asvial et al. (2020) | *IEEE Access* (Entropy-TOPSIS candidate ranking) | **VERIFIED** |
| 2 | `bast2016route` | Sec. I, II | Bast et al. (2016) | *Foundations & Trends in TCS* (Route planning survey) | **VERIFIED** |
| 3 | `das2019modeling` | Sec. I | Das et al. (2019) | *Transportation Research Record* (Turn behavior in India) | **VERIFIED** |
| 4 | `delling2017customizable` | Sec. II | Delling et al. (2017) | *INFORMS Journal on Computing* (Customizable Contraction Hierarchies) | **VERIFIED** |
| 5 | `fadilah2024identifying` | Sec. I, II | Fadilah et al. (2024) | *Asian Transport Studies* (Motorcycle stated-preference) | **VERIFIED** |
| 6 | `geisberger2011efficient` | Sec. I, II | Geisberger & Vetter (2011) | *ESA* (Contraction Hierarchies with turn costs) | **VERIFIED** |
| 7 | `hart1968formal` | Sec. I | Hart, Nilsson, & Raphael (1968) | *IEEE Transactions on SSC* (A* formal basis) | **VERIFIED** |
| 8 | `kirby1969minimum` | Sec. I, II | Kirby & Potts (1969) | *Transportation Science* (Turn penalties on directed graphs) | **VERIFIED** |
| 9 | `kotagi2020modeling` | Sec. I, II | Kotagi et al. (2020) | *Physica A* (Mixed-traffic speed dispersion) | **VERIFIED** |
| 10 | `kumar2025realtime` | Sec. I, II | Kumar et al. (2025) | *IEEE Transactions on ITS* (Real-time dynamic traffic routing) | **VERIFIED** |
| 11 | `luxen2011realtime` | Sec. I | Luxen & Vetter (2011) | *ACM SIGSPATIAL* (OSRM automobile engine) | **VERIFIED** |
| 12 | `promraksa2022lane` | Sec. I, II | Promraksa et al. (2022) | *Transportmetrica A* (Motorcycle queue filtering) | **VERIFIED** |
| 13 | `winter2002modeling` | Sec. I, II | Winter (2002) | *IJGIS* (Turn-dependent costs without line graphs) | **VERIFIED** |
| 14 | `zografos2004heuristic` | Sec. II | Zografos & Androutsopoulos (2004) | *Transportation Research Part C* (Heuristic multiobjective routing) | **VERIFIED** |

- **Missing Citations:** **0** (All 14 cited keys exist in `paper1_verified_references.bib`).
- **Uncited Entries in BibTeX:** 3 entries exist in `paper1_verified_references.bib` (`abraham2013alternative`, `boeing2017osmnx`, `goldberg2005computing`). Under standard BibTeX operation without `\nocite{*}`, uncited entries are automatically ignored and omitted from the compiled references section. No uncited references will be added to prose.

---

## 5. Provisional Section-Level Six-Page Layout Plan

Because precise column breaking depends on TeX line-breaking and micro-typographical hyphenation, this layout plan defines the **provisional section-level allocation** across the 6-page envelope. All 6 display equations, 2 tables, 3 figures, and 14 cited references are strictly accounted for.

```
+----------------------------------------------------------------------------------------------------+
|                               PROVISIONAL SECTION-LEVEL LAYOUT PLAN                                |
+----------------------------------------------------------------------------------------------------+
|  PAGE 1: Front Matter (Title & Authors), Abstract, Index Terms, Section I Complete                 |
|  PAGE 2: Section II Complete, Section III-A, III-B, III-C (Eq. 1), III-D Begins (Eq. 2, Table I)   |
|  PAGE 3: Section III-D Concludes (Eq. 3), Section IV Complete (IV-A to IV-D, Eqs. 4–6)             |
|  PAGE 4: Figure 1 (Exp A), Section V Complete, Figure 2 (Exp B), Section VI-A, VI-B               |
|  PAGE 5: Figure 3 (Exp C), Section VI-C, VI-D, VI-E, Table II (Hypothesis Tests + Footnote)        |
|  PAGE 6: Section VII Complete (4 Paragraphs), References (14 IEEEtran Numeric Entries)             |
+----------------------------------------------------------------------------------------------------+
```

### Detailed Provisional Page Allocations

#### **Page 1: Front Matter & Introduction**
- **Span Across Columns:** Paper Title, Author Block (`\author{...}` format, status unresolved pending Lead decision).
- **Column 1:**
  - `\begin{abstract}`: Single 208-word body paragraph ([`paper1_abstract_v2.md#L15`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md#L15)).
  - `\begin{IEEEkeywords}`: Seven indexed terms (16 words).
  - `\section{Introduction}` begins: Urban Two-Wheeler Context & Vertex-State Limitations.
- **Column 2:**
  - `\section{Introduction}` concludes: Turn-Aware Approaches, Scoped Motivation, Four Core Contributions, and Section Roadmap (complete Section I = 468 words across 6 paragraphs).
- **Estimated Density:** $\approx 468$ body words + Abstract (208 words) + Title/Author space $\approx 850\text{--}900$ word-equivalents. Cleanly fills Page 1.

#### **Page 2: Related Work & Problem Formulation (III-A through III-D Part 1)**
- **Column 1:**
  - `\section{Related Work}`: Complete Section II (349 words across Subsections II-A, II-B, II-C, II-D).
  - Transition to `\section{Problem Formulation and Configured Road Impedance}`:
    - Subsection III-A: Directed Road-Network and Routing Problem (128 words).
- **Column 2:**
  - Section III (cont.):
    - Subsection III-B: Edge-Based State Representation (113 words).
    - Subsection III-C: Angular Turn-Deflection Model (114 words) containing unnumbered deflection formula and **Equation (1)** (turn penalty piecewise function).
    - Subsection III-D begins: Configured Road-Impedance Model containing **Equation (2)** ($\mu(e)$ formula) and **Table I** (`[t]` single-column float).
- **Estimated Density:** $\approx 349 + 128 + 113 + 114 + \text{partial III-D} \approx 780\text{--}830$ words + Table I + Eqs. (1)–(2).

#### **Page 3: Problem Formulation Conclusion & Algorithmic Architecture (Section IV Complete)**
- **Column 1:**
  - Section III concludes:
    - Subsection III-D concludes: Path objective function and **Equation (3)** (composite traversal cost $c(s,s')$ and $C(P)$).
  - `\section{Turn-Aware $A^*$ Algorithm, Correctness and Complexity Analysis}` begins:
    - Subsection IV-A: Search Architecture (129 words).
    - Subsection IV-B: Scaled Haversine Heuristic Formulation (90 words) and **Equation (4)** ($h(s) = 0.80 D_{\text{haversine}}$).
- **Column 2:**
  - Section IV (cont.):
    - Subsection IV-C: Heuristic Admissibility and Consistency (185 words) and **Equation (5)** (monotonic consistency condition).
    - Subsection IV-D: Computational Complexity Analysis (125 words) and **Equation (6)** (two-line `aligned` asymptotic bounds).
- **Estimated Density:** Complete Section IV (529 words) + remainder of Section III-D + Eqs. (3)–(6) $\approx 820\text{--}870$ word-equivalents.

#### **Page 4: Experimental Setup & Results (Experiments A & B)**
- **Top of Page 4 (Column 1):**
  - **Figure 1 (`fig1_exp_a_tradeoffs.png`):** Exp. A sharp-turn reduction vs. runtime across 25 corridors (`\begin{figure}[t]`, single-column width).
- **Column 1:**
  - `\section{Experimental Setup and Methodology}`: Complete Section V (227 words: V-A 84w, V-B 72w, V-C 71w).
  - `\section{Experimental Results and Discussion}` begins:
    - Subsection VI-A: Turn Reduction and Runtime Overhead (Experiment A) (122 words).
- **Column 2:**
  - **Figure 2 (`fig2_exp_b_road_classes.png`):** Exp. B road-class composition shifts (`\begin{figure}[t]`, single-column width).
  - Subsection VI-B: Road-Class Exposure and Detour Trade-offs (Experiment B) (138 words).
- **Estimated Density:** $\approx 227 + 122 + 138 = 487$ words + Figs. 1 & 2 $\approx 850\text{--}900$ word-equivalents.

#### **Page 5: Results (Experiments C & D, Inferential Statistics)**
- **Top of Page 5 (Column 1):**
  - **Figure 3 (`fig3_exp_c_sensitivity.png`):** Exp. C turn penalty sensitivity & Pareto knee (`\begin{figure}[t]`, single-column width).
- **Column 1:**
  - Subsection VI-C: Turn Penalty Sensitivity and Knee Identification (Experiment C) (140 words).
  - Subsection VI-D: Algorithmic Scalability and Empirical Queue Pops (Experiment D) (98 words).
- **Column 2:**
  - Subsection VI-E: Paired Inferential Hypothesis Testing (146 words).
  - **Table II:** Primary Paired Inferential Hypothesis Test Results ($N=25$ Corridors, 10 test rows + explanatory footnote, `\begin{table}[t]`, single-column width, `\footnotesize`, `\tabcolsep=2.2pt`).
- **Estimated Density:** $\approx 140 + 98 + 146 = 384$ words + Fig. 3 + Table II (with detailed footnote) $\approx 830\text{--}880$ word-equivalents.

#### **Page 6: Conclusion, Limitations, Future Work & References**
- **Column 1:**
  - `\section{Conclusion and Future Work}`: Complete Section VII (287 words across 4 paragraphs: Paragraph 1 60w, Paragraph 2 78w, Paragraph 3 72w, Paragraph 4 77w).
  - *(Acknowledgment block strictly omitted; none approved).*
- **Column 2 (and lower Column 1 via column balancing):**
  - `\bibliographystyle{IEEEtran}`
  - `\bibliography{paper1_verified_references}`
  - 14 cited references formatted in standard IEEE numeric format ($\approx 35\text{--}42$ lines, $\approx 320\text{--}380$ word-equivalents).
- Remaining column capacity and float placement are unverified and will be assessed after compilation.

---

## 6. Dependency Risks and Mitigation Strategies

| Risk Factor | Severity | Description | Pre-Emptive Mitigation Strategy |
| :--- | :---: | :--- | :--- |
| **Missing Class File (`IEEEtran.cls`)** | **HIGH** | `IEEEtran.cls` does not exist in workspace. | Stage official `IEEEtran.cls` (v1.8b) into `research/paper1_manuscript/` before build. |
| **Missing TeX Binaries in PATH** | **HIGH** | `pdflatex`, `bibtex` not in system PATH. | Retain `pdflatex` as default target; identify or stage compiler pipeline before invoking build commands. |
| **Table II Column Width Overflow** | **MEDIUM** | 5 data columns plus hypothesis names in single-column width. | Apply `\setlength{\tabcolsep}{2.2pt}` and `\footnotesize` font size as verified in Section VI-E draft. |
| **Equation (6) Margin Clipping** | **LOW** | Two-line asymptotic bound equation with complex subscripts. | Wrapped in `aligned` environment within `\begin{equation} ... \end{equation}` to prevent line overruns. |
| **Float Crowding on Pages 4–5** | **MEDIUM** | Three figures and one table concentrated across 2 pages. | Enforce `[t]` positioning on all floats; use wide aspect ratios ($10:3, 8:5, 8:3$) to minimize vertical height. |

---

## 7. Explicit Unresolved Decisions (Awaiting Lead Guidance)

Prior to executing Phase 8.5-B2 (Assembly and Compilation), the following specific decisions must be resolved by the Research Lead:

1. **Compiler Pipeline Staging:**
   - Guidance: Confirm how the execution environment will provide `pdflatex` and `bibtex` (currently missing from PATH and standard locations).
2. **Author List, Affiliations, and Double-Blind Policy:**
   - Status: **UNRESOLVED.** No author names, institutional affiliations, or double-blind review assumptions are made. Awaiting explicit directive on author block formatting for IEEE CSNT 2027.

*(Note: The previously proposed acknowledgment block has been completely removed per Research Lead directive).*

---

## 8. Cryptographic Integrity and Compliance Verification

### 8.1 Verification of All 17 Canonical Manuscript Sources and Inventory
Direct SHA-256 verification confirms **zero unauthorized modifications** across all 17 canonical manuscript assets and inventory documents:

| # | Manuscript Asset / File | Approved Expected SHA-256 Digest | Recomputed SHA-256 Digest | Verification Result |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `paper1_abstract_v2.md` | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | **PASS** |
| 2 | `paper1_introduction_v1.md` | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | **PASS** |
| 3 | `paper1_related_work_v1.md` | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | **PASS** |
| 4 | `paper1_section_III_v1.md` | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | **PASS** |
| 5 | `paper1_section_IV_A_draft_v2.md` | `8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE` | `8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE` | **PASS** |
| 6 | `paper1_section_IV_B_draft_v2.md` | `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6` | `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6` | **PASS** |
| 7 | `paper1_section_IV_C_draft_v2.md` | `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1` | `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1` | **PASS** |
| 8 | `paper1_section_IV_D_draft_v2.md` | `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772` | `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772` | **PASS** |
| 9 | `paper1_section_V_draft_v1.md` | `C3330EB0E42D0BCABE6D2AAB16461B9B12BED701886F5B815BA82D5815185DD6` | `C3330EB0E42D0BCABE6D2AAB16461B9B12BED701886F5B815BA82D5815185DD6` | **PASS** |
| 10 | `paper1_section_VI_draft_v4.md` | `C6F31CAFD830F4EFE2419D4A6466132FFD66BC07771244B1902C0D321A6510DE` | `C6F31CAFD830F4EFE2419D4A6466132FFD66BC07771244B1902C0D321A6510DE` | **PASS** |
| 11 | `paper1_section_VII_draft_v1.md` | `7B65C133DB600739DDCA4BB029B4CCF49DDEA7F43D961FA863CD230B21297EDB` | `7B65C133DB600739DDCA4BB029B4CCF49DDEA7F43D961FA863CD230B21297EDB` | **PASS** |
| 12 | `phase_8_2_freeze_log.md` | `BA41DBAACE8F86CCA28BD9E774FFF6981BA9BFBF3DD75D3E0C46797C1508CB79` | `BA41DBAACE8F86CCA28BD9E774FFF6981BA9BFBF3DD75D3E0C46797C1508CB79` | **PASS** |
| 13 | `phase_8_3_B_freeze_log.md` | `53BCF6DAF9137E5A98131FECDF57905399122CD5FD8356196E9BA9D6F3BFF3DB` | `53BCF6DAF9137E5A98131FECDF57905399122CD5FD8356196E9BA9D6F3BFF3DB` | **PASS** |
| 14 | `phase_8_3_C2_freeze_log.md` | `625E7BFE4A98703232E6CB8A14738396BF6D7C5FFE84BEA272683F016A929489` | `625E7BFE4A98703232E6CB8A14738396BF6D7C5FFE84BEA272683F016A929489` | **PASS** |
| 15 | `phase_8_4_C_freeze_log.md` | `52F34A6CBD55F5C12152CC093A4336027F34D38EABA5332F1A504A1C012196D3` | `52F34A6CBD55F5C12152CC093A4336027F34D38EABA5332F1A504A1C012196D3` | **PASS** |
| 16 | `phase_8_4_A_section_VII_architecture.md` | `8DF6EA0CF38B769A4978FDB872225856D78E59F43D490A2A38D2489054D44288` | `8DF6EA0CF38B769A4978FDB872225856D78E59F43D490A2A38D2489054D44288` | **PASS** |
| 17 | `phase_8_5_A_assembly_inventory.md` | `C8627AC0B446D146BA3A13447F322E9A34F2FAE6CFBD6097EC27054A2E9ADA3D` | `C8627AC0B446D146BA3A13447F322E9A34F2FAE6CFBD6097EC27054A2E9ADA3D` | **PASS** |

### 8.2 Deliverable File Status
- **Deliverable File:** [`research/paper1_manuscript/phase_8_5_B1_latex_assembly_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_5_B1_latex_assembly_blueprint.md)
- **Status:** Modified exclusively to correct Section III structure, update the provisional page allocation plan, remove acknowledgment text, mark author information as unresolved, and specify toolchain states.

---

## 9. Conclusion & Stop Condition

This corrected blueprint establishes full architectural, structural, and bibliographic readiness for Paper 1 LaTeX assembly. All pre-conditions are met, Section III mapping is strictly reconciled to Subsections III-A through III-D, all source assets are mapped, all citation keys are verified, and no assembly code has been executed.

**STOP:** Awaiting Research Lead review and approval of `phase_8_5_B1_latex_assembly_blueprint.md` before proceeding.
