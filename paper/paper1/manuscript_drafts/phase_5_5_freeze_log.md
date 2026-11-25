# Phase 5.5: Section I (Introduction) Freeze Log

**Document:** [`phase_5_5_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_5_freeze_log.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Canonical Assembled Section:** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md)  
**Companion Audit:** [`phase_5_5_assembly_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_5_5_assembly_audit.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Freeze Status:** **FROZEN AND IMMUTABLE (v1.0)**  
**Effective Date:** 2026-11-05  

---

## 1. Freeze Action Record

Section I (Introduction) of Paper 1 has been assembled and frozen in its canonical state. All text, citations, mathematical symbols, and empirical results have undergone multi-stage drafting, targeted evidentiary refinement, independent citation-scope auditing, and bit-level verbatim assembly verification.

| Component | Source File | Source Status | Assembled Status |
| :--- | :--- | :--- | :--- |
| **Paragraphs 1–3** | `paper1_introduction_draft_p1_p3_v1.md` | Phase 5.4.1 Frozen Draft | **FROZEN CANONICAL** |
| **Paragraphs 4–6** | `paper1_introduction_draft_p4_p6_v1.md` | Phase 5.4.2 Approved Draft | **FROZEN CANONICAL** |
| **Complete Section I** | `paper1_introduction_v1.md` | Phase 5.5 Canonical Assembly | **FROZEN CANONICAL** |

---

## 2. Canonical Assembled Text (Section I: Introduction)

### Paragraph 1: Urban Two-Wheeler Context and Heterogeneous Mixed Traffic
Motorcycles account for a substantial share of registered vehicles in Thailand, reflecting their importance in the country's urban transport context \cite{promraksa2022lane}. Two-wheelers operate within heterogeneous mixed traffic characterized by severe speed dispersion between vehicle classes on undivided urban corridors \cite{kotagi2020modeling}. In metropolitan networks such as Bengaluru, where arterial corridors experience chronic bottleneck congestion and travel-time variability \cite{kumar2025realtime}, these heterogeneous traffic conditions motivate routing formulations that incorporate vehicle-specific road impedance across diverse street classes.

### Paragraph 2: Vertex-State Limitations and Directed Edge States
In a conventional vertex-state shortest-path formulation, the search state is identified by the current road-network vertex \cite{luxen2011realtime}. When routing evaluates intersection heading changes \cite{das2019modeling}, a vertex-only state representation cannot encode incoming-edge-dependent transition costs. Because transition cost into edge $(v, w)$ depends on arrival edge $(u, v)$, scalar vertex labels cannot differentiate competing arrival directions \cite{winter2002modeling}. Representing search states as directed edge states $s=(u, v)$ resolves this limitation, preserving the directional context needed to evaluate angular heading penalties during edge relaxation \cite{winter2002modeling}.

### Paragraph 3: Turn-Cost Formulations, Speedup Hierarchies, and Two-Wheeler Routing
Movement-expanded state spaces and line graphs were historically developed in traffic assignment to incorporate turn prohibitions and delay penalties \cite{kirby1969minimum}, \cite{winter2002modeling}. Turn-aware Contraction Hierarchies incorporate turn costs through turn-expanded core nodes and pre-computed shortcut construction \cite{geisberger2011efficient}. For metric customization, customizable hierarchies support flexible metric updates \cite{bast2016route}, while empirical studies observe that two-wheeler riders utilize lower-tier street classes differently than passenger cars \cite{fadilah2024identifying}. These approaches establish the feasibility of turn-aware routing, while motivating the examination of uncontracted search formulations for configurable vehicle-specific cost models.

### Paragraph 4: Scoped Motivation and Integrated Routing Formulation
While transportation route planning has been surveyed extensively regarding metric customization \cite{bast2016route}, two-wheeler studies such as Asvial et al. \cite{asvial2020entropy} have evaluated route suitability by post-hoc re-ranking pre-computed paths. This motivates an integrated routing formulation combining turn-aware state-expanded $A^*$ search with configured two-wheeler road impedance, conditional heuristic correctness guarantees, and controlled metropolitan corridor evaluation on an urban road network.

### Paragraph 5: Technical Contributions and Experimental Findings
We present a turn-aware routing framework with configured road impedance. The primary contributions are: (1) formulating online state-expanded search over directed edge states $s=(u, v)$ evaluating discrete angular penalties during edge relaxation; (2) integrating a configured class-dependent road impedance model with a $0.80$ override for qualifying grade-separated main-road segments; (3) establishing conditional admissibility and consistency for a Haversine heuristic scaled by $0.80$ under $\mu(e) \ge 0.80$ and nonnegative turn penalties, satisfying classical $A^*$ optimality requirements \cite{hart1968formal}; and (4) controlled evaluation across 25 corridors on Bengaluru's 744,216-edge network, showing a $34.1\%$ reduction in mean sharp turns (A0 vs. A1: $21.44$ vs. $32.52$) and a $51.21$ percentage-point arterial exposure drop (B0 vs. B1: $13.84\%$ vs. $65.05\%$) with a $15.53\%$ physical route-distance increase ($7.65$ vs. $6.62\text{ km}$).

### Paragraph 6: Paper Structure Roadmap
The remainder of this paper is organized as follows: Section II surveys related work. Section III defines the problem formulation and configured impedance. Section IV presents the turn-aware algorithm, theoretical proofs, and complexity bounds. Section V describes experimental methodology, Section VI evaluates empirical ablations, and Section VII concludes.

---

## 3. Freeze Metadata Summary and Official Word Count

### 3.1. Official Whitespace Tokenization
Counting via standard whitespace tokenization (`len(paragraph.split())`):

| Paragraph | Approved Subject Focus | Official Whitespace Count | Budget Allocation |
| :--- | :--- | :---: | :---: |
| **Paragraph 1** | Two-Wheeler Context & Heterogeneous Mixed Traffic Friction | **73 words** | ~70 words |
| **Paragraph 2** | Conventional Vertex Limitations & Directed Edge Search States | **81 words** | ~80 words |
| **Paragraph 3** | Turn Formulations, Speedup Hierarchies & Road Classes | **83 words** | ~85 words |
| **Paragraph 4** | Scoped Motivation & Integrated Routing Formulation | **59 words** | ~55–65 words |
| **Paragraph 5** | Four Core Theoretical and Empirical Contributions | **124 words** | ~115 words |
| **Paragraph 6** | Paper Organisation Roadmap (Sections II–VII) | **48 words** | ~45 words |
| **Total Section I** | **Complete Introduction Footprint** | **468 words** | **450–470 words** |

*(Note: Semantic counting treating the LaTeX math tuple `$(v, w)$` as a single unit yields 467 words. Both metrics strictly comply with the approved 450–470 word envelope).*

### 3.2. Citation Scope Correction Record
- **Correction Applied in Paragraph 3:** Replaced `"customizable hierarchies support multi-attribute cost updates"` with `"customizable hierarchies support flexible metric updates"`.
- **Primary Source Justification:** Verified against Bast et al. (2016) [`10_Bast_2016_Route_Planning_Survey.pdf`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/papers/10_Bast_2016_Route_Planning_Survey.pdf). Bast et al. directly substantiates that customizable hierarchies (such as CRP and CCH) support fast metric customization and flexible metric updates on fixed partitions (Sections 2.3 & 3.1), but does not support simultaneous multi-attribute Pareto optimization.
- **Word Count Impact:** Exactly 0-word delta (3 tokens $\to$ 3 tokens).

### 3.3. Quality and Boundary Verification
- **Total In-Text Citations:** 12 verified keys across 14 citation callouts (100% verified against `paper1_verified_references.bib`).
- **Negative Audit Status:** Zero prohibited claims (safety, travel-time, congestion, rider psychology); zero Paper 2 scope leakages.
- **Numerical Verification Status:** 100% identical to frozen Phase 13.4 ablation artifacts (`statistical_test_results.csv`, `bengaluru_graph.pkl`, `stage_2b_full_ablation_results.json`).

---

## 4. Immutability Protocol and Stop Directives

1. The text in [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) is officially frozen.
2. No further modifications to Section I are permitted without explicit written instruction from the research lead.
3. Section II (Related Work) planning and drafting is unblocked, pending formal research lead sign-off.
