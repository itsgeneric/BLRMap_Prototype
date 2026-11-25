# Section I: Introduction (Canonical Frozen Version v1.0)

**Document:** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Parent Outline:** [`paper1_introduction_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_outline_v1.md)  
**Parent Citation Map:** [`paper1_introduction_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_citation_map_v1.md)  
**Source Drafts:** [`paper1_introduction_draft_p1_p3_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p1_p3_v1.md) and [`paper1_introduction_draft_p4_p6_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_draft_p4_p6_v1.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Companion Audits:** [`phase_5_5_assembly_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_5_assembly_audit.md) and [`phase_5_5_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_5_freeze_log.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 5.5 FROZEN CANONICAL INTRODUCTION**

---

## Section I: Introduction

Motorcycles account for a substantial share of registered vehicles in Thailand, reflecting their importance in the country's urban transport context \cite{promraksa2022lane}. Two-wheelers operate within heterogeneous mixed traffic characterized by severe speed dispersion between vehicle classes on undivided urban corridors \cite{kotagi2020modeling}. In metropolitan networks such as Bengaluru, where arterial corridors experience chronic bottleneck congestion and travel-time variability \cite{kumar2025realtime}, these heterogeneous traffic conditions motivate routing formulations that incorporate vehicle-specific road impedance across diverse street classes.

In a conventional vertex-state shortest-path formulation, the search state is identified by the current road-network vertex \cite{luxen2011realtime}. When routing evaluates intersection heading changes \cite{das2019modeling}, a vertex-only state representation cannot encode incoming-edge-dependent transition costs. Because transition cost into edge $(v, w)$ depends on arrival edge $(u, v)$, scalar vertex labels cannot differentiate competing arrival directions \cite{winter2002modeling}. Representing search states as directed edge states $s=(u, v)$ resolves this limitation, preserving the directional context needed to evaluate angular heading penalties during edge relaxation \cite{winter2002modeling}.

Movement-expanded state spaces and line graphs were historically developed in traffic assignment to incorporate turn prohibitions and delay penalties \cite{kirby1969minimum}, \cite{winter2002modeling}. Turn-aware Contraction Hierarchies incorporate turn costs through turn-expanded core nodes and pre-computed shortcut construction \cite{geisberger2011efficient}. For metric customization, customizable hierarchies support flexible metric updates \cite{bast2016route}, while empirical studies observe that two-wheeler riders utilize lower-tier street classes differently than passenger cars \cite{fadilah2024identifying}. These approaches establish the feasibility of turn-aware routing, while motivating the examination of uncontracted search formulations for configurable vehicle-specific cost models.

While transportation route planning has been surveyed extensively regarding metric customization \cite{bast2016route}, two-wheeler studies such as Asvial et al. \cite{asvial2020entropy} have evaluated route suitability by post-hoc re-ranking pre-computed paths. This motivates an integrated routing formulation combining turn-aware state-expanded $A^*$ search with configured two-wheeler road impedance, conditional heuristic correctness guarantees, and controlled metropolitan corridor evaluation on an urban road network.

We present a turn-aware routing framework with configured road impedance. The primary contributions are: (1) formulating online state-expanded search over directed edge states $s=(u, v)$ evaluating discrete angular penalties during edge relaxation; (2) integrating a configured class-dependent road impedance model with a $0.80$ override for qualifying grade-separated main-road segments; (3) establishing conditional admissibility and consistency for a Haversine heuristic scaled by $0.80$ under $\mu(e) \ge 0.80$ and nonnegative turn penalties, satisfying classical $A^*$ optimality requirements \cite{hart1968formal}; and (4) controlled evaluation across 25 corridors on Bengaluru's 744,216-edge network, showing a $34.1\%$ reduction in mean sharp turns (A0 vs. A1: $21.44$ vs. $32.52$) and a $51.21$ percentage-point arterial exposure drop (B0 vs. B1: $13.84\%$ vs. $65.05\%$) with a $15.53\%$ physical route-distance increase ($7.65$ vs. $6.62\text{ km}$).

The remainder of this paper is organized as follows: Section II surveys related work. Section III defines the problem formulation and configured impedance. Section IV presents the turn-aware algorithm, theoretical proofs, and complexity bounds. Section V describes experimental methodology, Section VI evaluates empirical ablations, and Section VII concludes.

---

## Section I Word Count and Budget Breakdown

| Paragraph | Purpose / Focus | Word Count (Split) | Stated Budget | Target Allocation |
| :--- | :--- | :---: | :---: | :---: |
| **Paragraph 1** | Urban Two-Wheeler Routing Context & Physical Friction | **73 words** | 73 words | ~70 words |
| **Paragraph 2** | Vertex-State Limitations & Directed Edge Resolution | **81 words** | 80 words | ~80 words |
| **Paragraph 3** | Turn-Aware Routing Approaches & Speedup Techniques | **83 words** | 83 words | ~85 words |
| **Paragraph 4** | Scoped Motivation & Integrated Formulation | **59 words** | 59 words | ~55–65 words |
| **Paragraph 5** | Four Core Theoretical and Empirical Contributions | **124 words** | 124 words | ~115 words |
| **Paragraph 6** | Paper Organisation Roadmap (Sections II–VII) | **48 words** | 48 words | ~45 words |
| **Total Section I** | **Complete Introduction Footprint** | **468 words** | **467 words** | **450–470 words** |

*(Note on counting methods: Standard whitespace split yields exactly 468 words. Treating the LaTeX math symbol `$(v, w)$` as a single unit yields 467 words. Both metrics strictly comply with the approved 450–470 word budget).*

---

*Assembled and frozen under Phase 5.5 research protocol. All text and numerical values are verified and immutable.*
