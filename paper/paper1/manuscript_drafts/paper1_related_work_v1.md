# Section II: Related Work (Canonical Assembled Version v1.0)

**Document:** [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md) (v1.1)  
**Parent Citation Map:** [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md) (v1.4)  
**Source Deliverables:** [`paper1_related_work_IIA_IIB_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIA_IIB_v1.md) (frozen v1.2) and [`paper1_related_work_IIC_IID_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_IIC_IID_v1.md) (frozen v1.1)  
**Master Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md) (Allocated: 340 words, $\approx 46$ lines)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 6.3 CANONICAL ASSEMBLED RELATED WORK COMPLETE (AWAITING LEAD APPROVAL)**  
**Effective Date:** 2026-11-06  

---

## Section II: Related Work

\noindent\textbf{Shortest-Path Routing and Turn-Aware State Representations:} Movement-expanded representations have been used in macroscopic traffic assignment, where Kirby and Potts \cite{kirby1969minimum} expanded intersections into directed movement links to enforce turn prohibitions during tree-building. For shortest-path planning, Winter \cite{winter2002modeling} formalized dual line graphs, showing that treating directed edges as vertices allows transition costs between consecutive segments to reflect turn characteristics. While macroscopic assignment models compute aggregate flows over pre-expanded networks, point-to-point algorithms can evaluate turn penalties directly during traversal. Geisberger and Vetter \cite{geisberger2011efficient} analyzed point-to-point turn-aware routing, evaluating trade-offs between expanded edge graphs and compact node representations.

\noindent\textbf{Hierarchical Routing and Metric Customization:} Hierarchical speedup techniques accelerate routing queries by pre-computing shortcuts over base road networks \cite{bast2016route}. For turn-dependent routing, Geisberger and Vetter \cite{geisberger2011efficient} extended Contraction Hierarchies, constructing shortcuts that account for turn costs across contracted nodes. To support metric updates without repeating full preprocessing, Customizable Route Planning \cite{delling2017customizable} and customizable hierarchies \cite{bast2016route} decouple metric-independent partitioning from a fast customization phase. Where vehicle-specific impedance and flyover overrides are configured directly, uncontracted state-expanded search provides an alternative engineering trade-off that operates on base graphs without intermediate customization.

\noindent\textbf{Two-Wheeler Routing and Road-Class Impedance:} Two-wheeler navigation operates under mixed-traffic conditions characterized by vehicle speed dispersion \cite{kotagi2020modeling} and queue lane-filtering \cite{promraksa2022lane}. In Ninh Kiều District, Cần Thơ, Vietnam, Fadilah et al. \cite{fadilah2024identifying} used stated-preference modelling and microscopic simulation to examine motorcycle route selection under traffic-information scenarios, reporting departures from static shortest-path assignments in the simulated results. For two-wheeler routing, Asvial et al. \cite{asvial2020entropy} evaluated route suitability by generating candidate paths without turn penalties and applying post-hoc Entropy-TOPSIS re-ranking. Rather than re-ranking candidate paths or modeling behavioral choice, we evaluate configured road impedance directly within graph search as an engineering heuristic, without asserting that configured multipliers represent calibrated rider preferences.

\noindent\textbf{Research Positioning and Synthesis:} Prior literature establishes multi-objective routing with turn penalties on edge-expanded graphs for specialized fleet operations \cite{zografos2004heuristic}, alongside hierarchical metric customization \cite{delling2017customizable} and post-hoc two-wheeler path evaluation \cite{asvial2020entropy}. This paper addresses the integration of online turn-aware state-expanded $A^*$ search with configured two-wheeler road-class impedance and conditional heuristic admissibility and consistency. Controlled evaluation across 25 corridors in Bengaluru, where arterial networks experience chronic bottleneck congestion \cite{kumar2025realtime}, quantifies route-level trade-offs between turn avoidance, arterial exposure, and physical route distance.

---

## Section II Word Count Breakdown

| Subsection Heading | Thematic Focus | Word Count (Whitespace Split) | Blueprint Budget | Compliance Status |
| :--- | :--- | :---: | :---: | :---: |
| **Subsection II-A** | Shortest-Path & Turn-Aware Representations | **89 words** | ~90 words | **EXACT FIT** |
| **Subsection II-B** | Hierarchical Routing & Metric Customization | **83 words** | ~80 words | **EXACT FIT** |
| **Subsection II-C** | Two-Wheeler Routing & Road-Class Impedance | **101 words** | ~95 words | **EXACT FIT** |
| **Subsection II-D** | Research Positioning & Synthesis | **76 words** | ~75 words | **EXACT FIT** |
| **Total Section II** | **Canonical Assembled Related Work** | **349 words** | **340 words** | **EXACT FIT (+2.6%)** |
