# Phase 8.3-C2 Freeze Log: Section VI Canonical Freeze

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.3-C2-R4 — Formal Freeze of Paper 1 Section VI  
**Date:** 2026-11-07  
**Document:** [`phase_8_3_C2_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_C2_freeze_log.md)  
**Canonical Frozen File:** [`paper1_section_VI_draft_v4.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VI_draft_v4.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **SECTION VI CANONICAL MANUSCRIPT FROZEN (APPROVED BY RESEARCH LEAD)**  

---

## 1. Formal Freeze Declaration

By explicit authorization of the Research Lead, Section VI of Paper 1 (*Experimental Results and Discussion*) has completed precision evidence grounding, configuration auditing, inferential interpretation decoupling, LaTeX environment formatting, and word-budget compression. Section VI Draft v4.0 is hereby declared **CANONICALLY FROZEN**.

The canonical frozen file is located at:
- [`research/paper1_manuscript/paper1_section_VI_draft_v4.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VI_draft_v4.md)

Under project research protocol and version-control governance, **no further modifications, edits, word substitutions, or refactorings may be made to this file without explicit authorization from the Research Lead.**

---

## 2. Scope of Frozen Material

The frozen scope comprises the complete body prose, LaTeX publication floats, and tables spanning Subsections VI-A through VI-E:
- **Subsection VI-A:** Turn Awareness and State-Expansion Trade-offs (including Figure 1 float).
- **Subsection VI-B:** Road-Class Impedance and Street-Hierarchy Allocation (including Figure 2 float).
- **Subsection VI-C:** Turn-Penalty Sensitivity and Empirical Trade-off Knee (including Figure 3 float).
- **Subsection VI-D:** Topological Modifiers: Bridge and Roundabout Effects.
- **Subsection VI-E:** Primary Inferential Hypothesis Test Summary (including Table II float).

---

## 3. Canonical Frozen Text

The complete, unabridged, and canonical text of Section VI from [`paper1_section_VI_draft_v4.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VI_draft_v4.md) is recorded below:

```markdown
## VI. EXPERIMENTAL RESULTS AND DISCUSSION

### A. Turn Awareness and State-Expansion Trade-offs

Evaluating Experiment A confirms that turn-aware search curtails sharp maneuvers (Fig. 1). Under turn-aware routing ($A_0$), mean sharp turns ($\ge 60^\circ$) decrease from $32.52$ under turn-unaware state expansion ($A_1$) to $21.44$ ($-34.1\%$, mean diff $-11.08$, Pratt $W = 0.0$, Holm $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$, Hodges–Lehmann $-9.50$). Turn-unaware state expansion ($A_1$) and node-level search ($A_2$) exhibit identical sharp turns (mean diff $0.00$, Pratt $W = 0.0$, $p_{\text{adj}} = 1.000$, $d_z = 0.0000$), with identical route geometries and physical distances across all corridors ($25/25$ zeros, $7.723\text{ km}$); this geometric invariance is descriptive rather than inferential.

Measured runtimes show state expansion between $A_1$ and $A_2$ ($154.69$ vs. $40.88\text{ ms}$, $3.78\times$ median increase, mean diff $+253.38\text{ ms}$, $p_{\text{adj}} < 10^{-6}$, $d_z = +0.8115$) and turn scoring between $A_0$ and $A_1$ ($174.93$ vs. $154.69\text{ ms}$, $+13.1\%$ median increase, mean diff $+41.35\text{ ms}$, $p_{\text{adj}} = 1.2 \times 10^{-5}$, $d_z = +0.7947$). Across 25 corridor medians (five repetitions each), $A_0$ runtime averages $382.98\text{ ms}$ (sample SD $464.48\text{ ms}$, median $174.93\text{ ms}$, IQR $439.08\text{ ms}$, range $1.01\text{--}1,829.18\text{ ms}$); runtime varied across corridors, and sub-second completion was not universal.

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{research/literature_survey/13_ablation_study/figures/fig1_exp_a_tradeoffs.png}
\caption{Experiment A routing trade-offs across 25 corridors: (a) sharp turns ($\ge 60^\circ$) under turn-aware ($A_0$) vs. turn-unaware state expansion ($A_1$) and node-level reference ($A_2$), (b) wall-clock runtime distributions (log scale), and (c) expanded states.}
\label{fig:exp_a_tradeoffs}
\end{figure}

### B. Road-Class Impedance and Street-Hierarchy Allocation

Under production road impedance ($B_0$, Fig. 2), arterial exposure drops from $65.05\%$ under neutral weights ($B_1$) to $13.84\%$, a $51.21$ percentage-point reduction (Pratt $W = 4.0$, Holm $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$, Hodges–Lehmann $-54.55\%$). Residential share expands from $13.51\%$ to $44.24\%$ ($+30.73$ percentage points, Pratt $W = 9.0$, Holm $p_{\text{adj}} = 1.5 \times 10^{-4}$, Cohen's $d_z = +1.5234$, Hodges–Lehmann $+31.30\%$). Arterial avoidance incurs a detour: $B_0$ paths average $7.647\text{ km}$ versus $6.620\text{ km}$ under $B_1$ ($+15.53\%$ or $+1.028\text{ km}$, Pratt $W = 7.0$, Holm $p_{\text{adj}} = 6.8 \times 10^{-5}$, Cohen's $d_z = +0.9246$, Hodges–Lehmann $+0.86\text{ km}$). Relative to physical shortest paths ($B_2$, $59.35\%$ arterial share), $B_0$ lowers arterial exposure by $45.51$ percentage points (Pratt $W = 4.0$, Holm $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.5862$, Hodges–Lehmann $-46.31\%$). Configured impedance scales edge traversal costs, distinct from physical distance or elapsed travel time.

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{research/literature_survey/13_ablation_study/figures/fig2_exp_b_road_classes.png}
\caption{Experiment B street-hierarchy allocation across 25 corridors: (a) stacked percentage composition of road classes and (b) paired arterial versus residential street exposure shift across production ($B_0$), neutral ($B_1$), and shortest-distance ($B_2$) configurations.}
\label{fig:exp_b_road_classes}
\end{figure}

### C. Turn-Penalty Sensitivity and Empirical Trade-off Knee

Across four penalty tiers (Fig. 3), mean sharp turns decline monotonically: $C_0\ (0/0\text{ m}) = 32.52 \to C_1\ (12/4\text{ m}) = 24.64 \to C_2\ (25/8\text{ m}) = 21.44 \to C_3\ (50/16\text{ m}) = 19.80$ (pairwise tests vs. $C_2$: $p_{\text{adj}} \le 1.1 \times 10^{-4}$). Baseline $C_2$ captures $87.1\%$ of maximum turn reduction ($11.08 / 12.72$ turns) at minimum corpus mean distance ($7.648\text{ km}$). Escalating to $C_3$ shows diminishing returns: sharp turns decrease by only $1.64$ at $+32.3\text{ m}$ detour ($7.648 \to 7.680\text{ km}$, $+19.7\text{ m}$ per turn avoided; Pratt $W = 0.0$, Holm $p_{\text{adj}} = 1.1 \times 10^{-4}$, Cohen's $d_z = -1.0393$, Hodges–Lehmann $-1.50\text{ turns}$). Baseline $C_2$ represents an empirical trade-off knee rather than a universally dominant optimum: corridor breakdowns reveal that $C_2$ dominates $C_3$ on 8 corridors, $C_3$ dominates $C_2$ on 7, with 5 trade-offs and 5 ties.

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{research/literature_survey/13_ablation_study/figures/fig3_exp_c_sensitivity.png}
\caption{Experiment C turn-penalty sensitivity across 25 corridors: (a) monotonic sharp turn reduction across tiers $C_0$ ($0/0\text{ m}$), $C_1$ ($12/4\text{ m}$), $C_2$ ($25/8\text{ m}$), and $C_3$ ($50/16\text{ m}$); (b) physical route distance versus sharp turns showing baseline $C_2$ as the empirical corpus-average trade-off knee.}
\label{fig:exp_c_sensitivity}
\end{figure}

### D. Topological Modifiers: Bridge and Roundabout Effects

A $2 \times 2$ factorial design ($D_1\text{--}D_4$) tested bridge ($0.80$) and roundabout ($0.95$) modifiers. Bridge comparisons ($D_1$ vs. $D_2$, roundabout off; $D_3$ vs. $D_4$, roundabout on) shifted routes only on OD_04 (approximately $-645\text{ m}$) and OD_15 (approximately $-2.15\text{ km}$); 23 of 25 corridors were unchanged ($23/25$ zeros; Post-Hoc Standardized Impedance Cost $D_3$ vs. $D_4$: mean diff $+120.92$, $p_{\text{adj}} = 0.4722$, $d_z = +0.2192$). Roundabouts ($D_1$ vs. $D_3$, $D_2$ vs. $D_4$) produced zero route or distance changes ($25/25$ zeros; OD_06 traversed $62.98\text{ m}$). Search-objective costs were not retained; post-hoc standardized production scoring yielded identical observed costs across corridors, with non-significant $D_2$ vs. $D_4$ testing ($p_{\text{adj}} = 1.000$, outside Table II).

### E. Primary Inferential Hypothesis Test Summary

Table II summarizes the ten paired primary hypothesis tests across six families ($N=25$ corridors). Eight comparisons achieved statistical significance ($p_{\text{adj}} \le 1.5 \times 10^{-4}$); two were not statistically significant ($A_1$ vs. $A_2$ sharp turns, $p_{\text{adj}} = 1.000$; $D_3$ vs. $D_4$ Post-Hoc Standardized Impedance Cost, $p_{\text{adj}} = 0.4722$). Route-geometry and distance invariance ($25/25$ zeros for $A_1$ vs. $A_2$ and $D_2$ vs. $D_4$) represent separate descriptive findings.

\begin{table}[t]
\caption{Primary Paired Inferential Hypothesis Test Results ($N=25$ Corridors)}
\label{tab:statistical_results}
\centering
\footnotesize
\setlength{\tabcolsep}{2.2pt}
\begin{tabular}{llccc}
\hline
\textbf{Comparison} & \textbf{Outcome Metric} & \textbf{Mean Diff.} & \textbf{Wilcoxon $W$} & \textbf{Holm $p_{\mathrm{adj}}$} \\
\hline
$A_0$ vs $A_1$ & Sharp Turns ($\ge 60^\circ$) & $-11.08$ & $0.0$ & $\mathbf{4.5 \times 10^{-5}}$ \\
$A_1$ vs $A_2$ & Sharp Turns ($\ge 60^\circ$) & $0.00$ & $0.0$ & $1.000$ \\
$A_0$ vs $A_1$ & Wall-Clock Runtime [ms] & $+41.35$ & $17.0$ & $\mathbf{1.2 \times 10^{-5}}$ \\
$A_1$ vs $A_2$ & Wall-Clock Runtime [ms] & $+253.38$ & $0.0$ & $\mathbf{< 10^{-6}}$ \\
$B_0$ vs $B_1$ & Arterial Share [\%] & $-51.21$ & $4.0$ & $\mathbf{8.4 \times 10^{-5}}$ \\
$B_0$ vs $B_1$ & Residential Share [\%] & $+30.73$ & $9.0$ & $\mathbf{1.5 \times 10^{-4}}$ \\
$B_0$ vs $B_1$ & Physical Distance [km] & $+1.028$ & $7.0$ & $\mathbf{6.8 \times 10^{-5}}$ \\
$B_0$ vs $B_2$ & Arterial Share [\%] & $-45.51$ & $4.0$ & $\mathbf{8.4 \times 10^{-5}}$ \\
$C_3$ vs $C_2$ & Sharp Turns ($\ge 60^\circ$) & $-1.64$ & $0.0$ & $\mathbf{1.1 \times 10^{-4}}$ \\
$D_3$ vs $D_4$ & Post-Hoc Standardized Impedance Cost & $+120.92$ & $0.0$ & $0.4722$ \\
\hline
\multicolumn{5}{p{3.3in}}{\scriptsize \textit{Note:} Paired Wilcoxon signed-rank tests with Pratt zero-difference correction across $N=25$ OD corridors (8 significant, 2 non-significant). Bold values indicate statistical significance ($p_{\mathrm{adj}} < 0.05$). The $A_1$ vs. $A_2$ test strictly evaluates sharp-turn counts ($p_{\mathrm{adj}} = 1.000$); complete route-geometry and physical-distance invariance ($25/25$ zeros) are separate descriptive corridor-level findings. Metric label "Post-Hoc Standardized Impedance Cost" evaluates paths under restored standard production scoring; actual configured search-objective costs were not retained by the harness. Route-geometry and physical-distance invariance across all 25 corridors for the roundabout modifier ($D_2$ vs. $D_4$, $25/25$ zeros) are separate descriptive findings from corridor metrics detailed in Section~VI-D.}
\end{tabular}
\end{table}
```

---

## 4. Cryptographic Fingerprint and Word Count Specification

- **Canonical File Path:** [`research/paper1_manuscript/paper1_section_VI_draft_v4.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_VI_draft_v4.md)
- **Verified SHA-256 Digest:** `C6F31CAFD830F4EFE2419D4A6466132FFD66BC07771244B1902C0D321A6510DE`
- **Total Body Math-as-Single-Token Word Count:** **511 words**
- **Total Body Whitespace Word Count:** **644 words**
- **Floats:** Three figures (Figs. 1–3) and one table (Table II).

### Detailed Subsection Word-Count Accounting
Counting scope covers prose strictly within Subsections VI-A through VI-E, excluding section headings, LaTeX figure environments, LaTeX table environments, captions, labels, and audit checklists:

| Subsection | Initial Allocation | Draft v4.0 (Math as Single Token) | Draft v4.0 (Whitespace) | Budget Reconciliation |
| :--- | :---: | :---: | :---: | :--- |
| **Subsection VI-A** | ~155 words | 150 words | 185 words | **ALIGNED** (-5 from target) |
| **Subsection VI-B** | ~115 words | 111 words | 147 words | **ALIGNED** (-4 from target) |
| **Subsection VI-C** | ~115 words | 95 words | 138 words | **ALIGNED** (-20 from target) |
| **Subsection VI-D** | ~65 words | 98 words | 109 words | **EXCEEDS LOCAL ALLOCATION** (+33 words from ~65) |
| **Subsection VI-E** | ~60 words | 57 words | 65 words | **ALIGNED** (-3 from target) |
| **Total Section VI Body** | **~510 words** | **511 words** | **644 words** | **WITHIN OVERALL BUDGET** (+1 word / +0.2%) |

### Explicit Note on Local VI-D Allocation
As explicitly instructed by the Research Lead:
- **Subsection VI-D does NOT meet its earlier local target of ~65 words.**
- At **98 math-as-single-token words**, Subsection VI-D exceeds its local target by 33 words.
- This local expansion represents an irreducible evidence floor required to formally document:
  1. Both factorial bridge comparisons ($D_1-D_2$ and $D_3-D_4$ with roundabout off and on).
  2. The specific corridor IDs (OD_04 and OD_15) and physical-distance shifts ($-645\text{ m}$ and $-2.15\text{ km}$).
  3. The descriptive invariance of roundabout geometry ($25/25$ zeros, OD_06 $62.98\text{ m}$).
  4. The distinction between non-retention of search-objective costs, identical observed post-hoc standardized costs ($25/25$ zeros), and the non-significant $D_2-D_4$ inferential test ($p_{\text{adj}} = 1.000$, reported outside Table II).
- The surplus in VI-D is fully offset by precision economies achieved in VI-A (150 words), VI-B (111 words), VI-C (95 words), and VI-E (57 words), keeping the cumulative Section VI body at **511 words**, strictly within the approved overall manuscript budget (~510 words).

---

## 5. Frozen Integrity Verification of Preceding Manuscript Sections

All previously approved and frozen sections, as well as preceding freeze logs, remain byte-for-byte identical and unmodified, verified by cryptographic SHA-256 hash matching:

| Manuscript Unit | Canonical File | Status | Expected Canonical SHA-256 | Actual Verified SHA-256 | Verification |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Abstract** | [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | FROZEN | `67272764F7DA...334DB142` | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | **MATCH** |
| **Section I** | [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | FROZEN | `3271BE72BA4A...1B64141` | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | **MATCH** |
| **Section II** | [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | FROZEN | `839C1D5936F7...2CA21BA` | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | **MATCH** |
| **Section III** | [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) | FROZEN | `CEE2B6A495D0...3692C9061` | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | **MATCH** |
| **Section IV-A** | [`paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md) | FROZEN | `8B86B3722895...6C3D7CEE` | `8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE` | **MATCH** |
| **Section IV-B** | [`paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md) | FROZEN | `CB88AC8A9263...7EDEFEB6` | `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6` | **MATCH** |
| **Section IV-C** | [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md) | FROZEN | `08262BE23D74...8FCC4C1` | `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1` | **MATCH** |
| **Section IV-D** | [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md) | FROZEN | `B1A07D5CD095...E83EC772` | `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772` | **MATCH** |
| **Section V** | [`paper1_section_V_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_V_draft_v1.md) | FROZEN | `C3330EB0E42D...15185DD6` | `C3330EB0E42D0BCABE6D2AAB16461B9B12BED701886F5B815BA82D5815185DD6` | **MATCH** |
| **Freeze Log V** | [`phase_8_3_B_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_B_freeze_log.md) | FROZEN | `53BCF6DAF913...3BFF3DB` | `53BCF6DAF9137E5A98131FECDF57905399122CD5FD8356196E9BA9D6F3BFF3DB` | **MATCH** |

---

## 6. Research Boundaries and Stop Condition Compliance

1. **Experimental Data and Code Integrity:** Zero modifications made to source code, execution harnesses, raw trajectory CSVs, statistical test results (`statistical_test_results.csv`), or publication figures.
2. **Drafting Scope Boundaries:** Section VII (*Conclusion and Future Work*) has **NOT** been drafted.
3. **Compilation Boundaries:** Full manuscript assembly or compilation into `paper1_main.tex` has **NOT** been initiated.
4. **Active Freeze:** Section VI is formally frozen as of this document.

---

## 7. Next Phase Readiness

Standing by for Research Lead instructions regarding:
- **Phase 8.4:** Section VII (Conclusion and Future Work) Architecture & Drafting, or
- **Phase 8.5:** Full Manuscript Assembly, Global Citation Reconciliation, and Final IEEEtran Compilation.
