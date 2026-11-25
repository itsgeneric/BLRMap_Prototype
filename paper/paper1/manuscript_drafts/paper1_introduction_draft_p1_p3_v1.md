# Section I: Introduction (Draft: Paragraphs 1–3, v1.3 Aligned)

**Document:** [`paper1_introduction_draft_p1_p3_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p1_p3_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Parent Outline:** [`paper1_introduction_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_outline_v1.md)  
**Parent Citation Map:** [`paper1_introduction_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_citation_map_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 5.4.1 FINAL EVIDENTIARY-ALIGNED DRAFT (PARAGRAPHS 1–3)**

---

## Section I: Introduction (Prose Text: Paragraphs 1–3)

Motorcycles account for a substantial share of registered vehicles in Thailand, reflecting their importance in the country's urban transport context \cite{promraksa2022lane}. Two-wheelers operate within heterogeneous mixed traffic characterized by severe speed dispersion between vehicle classes on undivided urban corridors \cite{kotagi2020modeling}. In metropolitan networks such as Bengaluru, where arterial corridors experience chronic bottleneck congestion and travel-time variability \cite{kumar2025realtime}, these heterogeneous traffic conditions motivate routing formulations that incorporate vehicle-specific road impedance across diverse street classes.

In a conventional vertex-state shortest-path formulation, the search state is identified by the current road-network vertex \cite{luxen2011realtime}. When routing evaluates intersection heading changes \cite{das2019modeling}, a vertex-only state representation cannot encode incoming-edge-dependent transition costs. Because transition cost into edge $(v, w)$ depends on arrival edge $(u, v)$, scalar vertex labels cannot differentiate competing arrival directions \cite{winter2002modeling}. Representing search states as directed edge states $s=(u, v)$ resolves this limitation, preserving the directional context needed to evaluate angular heading penalties during edge relaxation \cite{winter2002modeling}.

Movement-expanded state spaces and line graphs were historically developed in traffic assignment to incorporate turn prohibitions and delay penalties \cite{kirby1969minimum}, \cite{winter2002modeling}. Turn-aware Contraction Hierarchies incorporate turn costs through turn-expanded core nodes and pre-computed shortcut construction \cite{geisberger2011efficient}. For metric customization, customizable hierarchies support multi-attribute cost updates \cite{bast2016route}, while empirical studies observe that two-wheeler riders utilize lower-tier street classes differently than passenger cars \cite{fadilah2024identifying}. These approaches establish the feasibility of turn-aware routing, while motivating the examination of uncontracted search formulations for configurable vehicle-specific cost models.

---

## Word Count and Budget Analysis

- **Paragraph 1:** Exactly **73 words** (Target Allocation: 70 words; Delta: $+3$ words).
- **Paragraph 2:** Exactly **80 words** (Target Allocation: 80 words; Delta: $0$ words).
- **Paragraph 3:** Exactly **83 words** (Target Allocation: 85 words; Delta: $-2$ words).
- **Total Paragraphs 1–3 Word Count:** Exactly **236 words** (Target Allocation: 235 words; Delta: $+1$ word).

---

*Drafted strictly within the allocated budget of `paper1_final_page_budget_v1.md` and verified under `blrmap-research-protocol` and `evidence-integrity-audit`.*
