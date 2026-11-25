# Phase 6.1.4: Section II (Related Work) Planning and Claim-Level Evidence Audit

**Document:** [`phase_6_1_planning_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_6_1_planning_audit.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Audited Deliverables:** [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md) (v1.1) and [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md) (v1.4)  
**Master Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **PHASE 6.1.4 CLAIM-LEVEL AUDIT COMPLETE (AWAITING LEAD APPROVAL)**  
**Effective Date:** 2026-11-06  

---

## 1. Executive Summary & Granular Claim-Level Audit Findings

This audit certifies the exhaustive claim-level source evaluation conducted under Phase 6.1.4 for **Section II: Related Work**, focusing specifically on **Fadilah et al. (2024)** (DOI: [10.1016/j.trip.2024.101247](https://doi.org/10.1016/j.trip.2024.101247)):

### Granular Evaluation of Fadilah et al. (2024) Claims

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                     FADILAH ET AL. (2024) CLAIM-LEVEL AUDIT MATRIX                       │
├───────────────────────┬──────────────────────────────────┬───────────────────────────────┤
│ Audit Dimension       │ Claim 1: Passenger-Car Contrast  │ Claim 2: Dynamic Adjustments  │
├───────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ Exact Section & Pages │ Section 1 (pp. 1–2), Sec 3 (pp.  │ Section 3.2 (pp. 4–5), Table 1│
│                       │ 4–5), Section 4 (pp. 6–8)        │ (p. 6), Sec 4.3–4.4 (pp. 7–9) │
├───────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ Relevant Passage /    │ Baseline comparison of simulated │ Table 1 (SP discrete-choice   │
│ Table / Figure        │ motorcycle routes against static │ parameter estimates); Fig 5–8 │
│                       │ shortest-path assignment         │ (Aimsun MFD capacity curves)  │
├───────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ Evidence Type         │ Author interpretation / narrative│ Model estimation on SP survey │
│                       │ motivation (cars); Simulation    │ data (switching); Microscopic │
│                       │ modeling (static shortest paths) │ simulation in Aimsun (updates)│
├───────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ Crucial Distinction   │ The study did NOT collect car    │ The study did NOT observe real│
│                       │ route choices or GPS trajectories│ riders switching routes on    │
│                       │ for comparative analysis.        │ physical streets en-route.    │
├───────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ Support Verdict       │ PARTIALLY SUPPORTED / CONFLATED  │ PARTIALLY SUPPORTED /         │
│                       │ (Static shortest-path divergence │ SIMULATION-BASED (SP model    │
│                       │ is modeled; passenger-car contrast│ and Aimsun simulation; physical│
│                       │ is unmeasured literature context)│ route switching unsupported)  │
└───────────────────────┴──────────────────────────────────┴───────────────────────────────┘
```

1. **Claim 1 ("Motorcycle route-choice behaviour differing from conventional passenger-car shortest paths"):**
   - *Audit:* The empirical data in Fadilah et al. consists of an SP questionnaire administered exclusively to $N = 301$ motorcycle riders in Ninh Kiều District, Cần Thơ City, Vietnam. Passenger-car driver choices were not tracked or surveyed. In Section 1, the authors discuss passenger cars purely as theoretical motivation (noting that conventional simulation frameworks were developed for car-following behavior). The simulation baseline in Section 4 is **static shortest-path network assignment**, not passenger-car routes.
   - *Resolution:* Purge the unmeasured passenger-car comparison from Section II claims. Scoped strictly to departure from **conventional static shortest-path routing assumptions**.

2. **Claim 2 ("Dynamic route adjustment in response to encountered traffic conditions"):**
   - *Audit:* The authors did **not** empirically track real commuters dynamically switching routes mid-trip when encountering physical congestion. The empirical contribution is an SP discrete-choice model (binary and mixed binary logit) indicating that $35.6\%$ of respondents expressed a willingness to switch routes under hypothetical Variable Message Sign (VMS) guidance (Table 1). The dynamic adjustment was executed algorithmically inside an **Aimsun microscopic simulation** using Macroscopic Fundamental Diagram (MFD) feedback (Section 4.3–4.4). Furthermore, Section 1 and Section 5 emphasize that in real-world developing cities (such as Cần Thơ), roadside information infrastructure for motorcycles is **largely absent**, which in practice restricts dynamic route optimization.
   - *Resolution:* Purge claims implying observed physical en-route switching. Scope strictly to **discrete-choice stated-preference modeling and microscopic traffic simulation under traffic-information scenarios**.

3. **Recommended Narrowed Claim for Section II Manuscript:**
   > "Stated-preference discrete-choice modeling and microscopic simulation of motorcycle traffic in Ninh Kiều District, Cần Thơ, Vietnam, demonstrate that motorcycle route selection departs from static shortest-path assignments when modeled under traffic-information scenarios \cite{fadilah2024identifying}."

---

## 2. Blueprint Alignment and Word Budget Audit

| Section II Area | Thematic Focus | Word Allocation | Page Location in Blueprint | Heading Style |
| :--- | :--- | :---: | :---: | :---: |
| **Area II-A** | Movement-Expanded & Turn-Aware Routing | **~90 words** | Page 1, Col 2 Bottom | Bold Run-In Header |
| **Area II-B** | Hierarchical Routing & Metric Customization | **~80 words** | Page 1, Col 2 Bottom | Bold Run-In Header |
| **Area II-C** | Two-Wheeler Routing & Road-Class Impedance | **~95 words** | Page 2, Col 1 Top | Bold Run-In Header |
| **Area II-D** | Research Positioning & Synthesis | **~75 words** | Page 2, Col 1 Top | Bold Run-In Header |
| **Total Section II** | **Complete Related Work Section** | **340 words** | **Page 1–2 ($\approx 46\text{ lines}$)** | **Zero Line Penalty** |

---

## 3. Reconciled Citation Density & Tiering Audit

The 12 retained citations are strictly partitioned into **8 Essential Citations** and **4 Optional Contextual Citations**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        RECONCILED CITATION TIERING BREAKDOWN                            │
├────────┬─────────────────────────────┬──────────────┬───────────────────────────────────┤
│ Area   │ Citation Key                │ Tier         │ Exact Role in Section II          │
├────────┼─────────────────────────────┼──────────────┼───────────────────────────────────┤
│ II-A   │ kirby1969minimum            │ ESSENTIAL    │ Historical origin of movement-    │
│ (~90 w)│                             │              │ expanded networks for turns.      │
│        │ winter2002modeling          │ ESSENTIAL    │ Dual line graphs & directed edge  │
│        │                             │              │ states s=(u,v) in route planning. │
├────────┼─────────────────────────────┼──────────────┼───────────────────────────────────┤
│ II-B   │ geisberger2011efficient     │ ESSENTIAL    │ Turn-aware Contraction Hierarchies│
│ (~80 w)│                             │              │ with pre-computed shortcut tables.│
│        │ delling2017customizable     │ ESSENTIAL    │ Customizable Route Planning (CRP) │
│        │                             │              │ for flexible metric updates.      │
│        │ bast2016route               │ ESSENTIAL    │ Algorithmic survey of speedup and │
│        │                             │              │ metric customization (CCH).       │
│        │ luxen2011realtime           │ OPTIONAL     │ OSRM automobile baseline; can be  │
│        │                             │              │ merged or omitted if space tight. │
├────────┼─────────────────────────────┼──────────────┼───────────────────────────────────┤
│ II-C   │ asvial2020entropy           │ ESSENTIAL    │ Direct baseline: motorcycle       │
│ (~95 w)│                             │              │ routing with turn cost = 0.       │
│        │ fadilah2024identifying      │ ESSENTIAL    │ Discrete-choice SP modeling &     │
│        │                             │              │ Aimsun simulation under info.     │
│        │ promraksa2022lane           │ OPTIONAL     │ Thai motorcycle context & queues. │
│        │                             │              │ Omissible as already in Sec I.    │
│        │ kotagi2020modeling          │ OPTIONAL     │ Speed dispersion on Indian roads. │
│        │                             │              │ Omissible as already in Sec I.    │
├────────┼─────────────────────────────┼──────────────┼───────────────────────────────────┤
│ II-D   │ zografos2004heuristic       │ ESSENTIAL    │ Prior art benchmark: multi-       │
│ (~75 w)│                             │              │ objective routing on edge graphs. │
│        │ kumar2025realtime           │ OPTIONAL     │ Bengaluru traffic context.        │
│        │                             │              │ Omissible as already in Sec I.    │
└────────┴─────────────────────────────┴──────────────┴───────────────────────────────────┘
```

- **Essential Citations Count:** Exactly **8 Citations**.
- **Optional Citations Count:** Exactly **4 Citations**.
- **Total Retained Citations:** Exactly **12 Citations** ($8 + 4 = 12$).
- **Traceability:** All 12 citations exist in [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib). Zero new references proposed.

---

## 4. Geographic Scope and Source Evidence Audit

| Citation Key | Primary Publication Venue | Verified Study Location | Prohibited Geographic Extrapolations | Audit Status |
| :--- | :--- | :--- | :--- | :---: |
| `fadilah2024identifying` | *Transp. Res. Interdiscip. Perspect.* (2024) | **Ninh Kiều District, Cần Thơ City, Vietnam** | NO reference to Denpasar, Bali, or Bandung. NO extrapolation to "all Asian cities". | **PASSED** |
| `promraksa2022lane` | *J. Adv. Transp.* (2022) | **Khon Kaen, Thailand** (intersections) & **Thailand** (registrations) | NO extrapolation to "Asian urban transport" or "Southeast Asia". | **PASSED** |
| `kotagi2020modeling` | *J. Traffic Transp. Eng.* (2020) | **Bengaluru and Mangaluru, India** (undivided corridors) | Scoped strictly to undivided Indian urban roads. | **PASSED** |
| `asvial2020entropy` | *IJACSA* (2020) | **South Jakarta, Indonesia** (6 simulated OD pairs) | Scoped strictly to the authors' Jakarta simulation setup. | **PASSED** |
| `kumar2025realtime` | *Int. J. Transp. Dev. Integr.* (2025) | **Bengaluru, India** (Hosur Rd, MG Rd, Trinity Circle) | Scoped strictly to Bengaluru radial arterial corridors. Term "ground truth" prohibited. | **PASSED** |
| `geisberger2011efficient` | *Proc. SEA* (2011) | **Western European Road Network** (PTV AG data) | Continental automobile highway benchmark. | **PASSED** |
| `luxen2011realtime` | *Proc. ACM SIGSPATIAL* (2011) | **OpenStreetMap Germany / Western Europe** | European/Western automobile routing baseline. | **PASSED** |
| `winter2002modeling` | *GeoInformatica* (2002) | **Synthetic Planar Grid Graphs** | Synthetic graph-theoretic simulation. | **PASSED** |
| `kirby1969minimum` | *Transp. Res.* (1969) | **Theoretical Mathematical Network** | Formal graph expansion theory. | **PASSED** |
| `zografos2004heuristic` | *Eur. J. Oper. Res.* (2004) | **Hazardous Truck Transport Network** | Regional hazardous materials routing network. | **PASSED** |

---

## 5. Scope-Boundary and Protocol Compliance Verification

| Guarded Research Boundary | Audit Rule / Prohibition | Planned Content Compliance | Audit Status |
| :--- | :--- | :--- | :---: |
| **Safety Claims** | NO claims of safety improvements, accident reduction, crash mitigation, or fatality drops. | Confined strictly to geometric turn counts, trajectory smoothing, and angular deflection penalties. | **PASSED** |
| **Mobility Claims** | NO claims of unmeasured travel-time savings or city-wide congestion reduction. | Confined strictly to physical route distance, turn counts, and road-class exposure. | **PASSED** |
| **Congestion Prediction** | NO claims of real-time deep learning traffic prediction or sensor streaming. | Kumar et al. (2025) cited strictly for static bottleneck corridor context; term "ground truth" purged. | **PASSED** |
| **Rider Psychology** | NO claims that configured weights represent validated rider psychological preferences. | Explicitly distinguished modeled route selection (Fadilah et al.) from configured heuristic impedance. | **PASSED** |
| **Metric Customization Conflation** | Do NOT confuse metric customization with multi-criteria Pareto optimization. | Bast et al. (2016) cited strictly for flexible metric customization on fixed partitions. | **PASSED** |
| **Construct Conflation** | Do NOT confuse physical route distance with impedance cost. | Maintained separate conceptual definitions across all subsections. | **PASSED** |
| **Paper 2 Scope Leakage** | NO alternative-route generation, Yen's algorithm, route diversity, or perpendicular offset. | All Paper 2 concepts completely excluded. | **PASSED** |
| **Priority / Novelty Claims** | NO claims of global priority ("first", "only", "novel in the world"). | Research gap framed strictly around unified integration and controlled evaluation. | **PASSED** |

---

## 6. Deliverables Summary & Sign-Off Checklist

1. [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md) — 340-word structural outline confirmed unchanged (v1.1).
2. [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md) — Granular claim-level evidence map with verified Fadilah claims, Essential (8) vs. Optional (4) density tiering, and passage-level citations (v1.4).
3. [`phase_6_1_planning_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_6_1_planning_audit.md) — Complete planning and claim-level evidence audit (v1.4).

- **Unresolved Evidence Concerns:** **Zero.**
- **Section I Status:** Verbatim frozen in [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md).
- **Section II Prose Status:** **NOT DRAFTED.**
- **Next Stage:** Awaiting Research Lead authorization to open Phase 6.2 (staged prose drafting).

---

**STOP:** Phase 6.1.4 audit complete. Section II prose has NOT been drafted. Section I remains frozen. Awaiting Research Lead instructions.
