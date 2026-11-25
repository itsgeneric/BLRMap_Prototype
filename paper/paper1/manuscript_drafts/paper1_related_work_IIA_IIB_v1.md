# Section II: Related Work — Subsections II-A and II-B (Draft v1.2)

**Document:** [`paper1_related_work_IIA_IIB_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md)  
**Parent Citation Map:** [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md) (v1.4)  
**Master Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Status:** **PHASE 6.2.1-R2 REVISED DRAFT COMPLETE (AWAITING LEAD APPROVAL)**  
**Word Budget:** Target: ~170 words combined (II-A: ~90 words, II-B: ~80 words) | **Achieved: 172 words** (II-A: 89 words, II-B: 83 words)  

---

### II-A. Shortest-Path Routing and Turn-Aware State Representations

\noindent\textbf{Shortest-Path Routing and Turn-Aware State Representations:} Movement-expanded representations have been used in macroscopic traffic assignment, where Kirby and Potts \cite{kirby1969minimum} expanded intersections into directed movement links to enforce turn prohibitions during tree-building. For shortest-path planning, Winter \cite{winter2002modeling} formalized dual line graphs, showing that treating directed edges as vertices allows transition costs between consecutive segments to reflect turn characteristics. While macroscopic assignment models compute aggregate flows over pre-expanded networks, point-to-point algorithms can evaluate turn penalties directly during traversal. Geisberger and Vetter \cite{geisberger2011efficient} analyzed point-to-point turn-aware routing, evaluating trade-offs between expanded edge graphs and compact node representations.

---

### II-B. Hierarchical Routing and Metric Customization

\noindent\textbf{Hierarchical Routing and Metric Customization:} Hierarchical speedup techniques accelerate routing queries by pre-computing shortcuts over base road networks \cite{bast2016route}. For turn-dependent routing, Geisberger and Vetter \cite{geisberger2011efficient} extended Contraction Hierarchies, constructing shortcuts that account for turn costs across contracted nodes. To support metric updates without repeating full preprocessing, Customizable Route Planning \cite{delling2017customizable} and customizable hierarchies \cite{bast2016route} decouple metric-independent partitioning from a fast customization phase. Where vehicle-specific impedance and flyover overrides are configured directly, uncontracted state-expanded search provides an alternative engineering trade-off that operates on base graphs without intermediate customization.

---

## Word Count Summary

| Subsection | Stated Budget | Actual Word Count (Whitespace Split) | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Subsection II-A** | ~90 words | **89 words** | **EXACT MATCH** |
| **Subsection II-B** | ~80 words | **83 words** | **EXACT MATCH** |
| **Combined II-A + II-B** | ~170 words | **172 words** | **EXACT MATCH** |
