# Section II: Related Work Citation-Evidence Map (v1.4 Claim-Level Precision Reconciliation)

**Document:** [`paper1_related_work_citation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_citation_map_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md)  
**Master Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib)  
**Primary Reference Verification:** [`phase_3_1_reference_verification.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_1_reference_verification.csv)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **PHASE 6.1.4 CLAIM-LEVEL AUDIT COMPLETE (AWAITING LEAD APPROVAL)**  
**Effective Date:** 2026-11-06  

---

## 1. Executive Summary & Phase 6.1.4 Claim-Level Audit Findings

This updated evidence map incorporates the granular claim-level source audit of **Fadilah et al. (2024)** (DOI: [10.1016/j.trip.2024.101247](https://doi.org/10.1016/j.trip.2024.101247)), reconciling previous draft claims against the original full text:

1. **Claim 1: "Motorcycle route-choice behaviour differing from conventional passenger-car shortest paths"**
   - **Source Audit:**
     - The empirical data in Fadilah et al. consists exclusively of a stated-preference (SP) survey of $N = 301$ motorcycle riders in the Ninh Kiều District of Cần Thơ, Vietnam.
     - The authors did **not** collect empirical route choices or GPS trajectory data from passenger-car drivers for comparative analysis.
     - The contrast with "conventional passenger cars" appears in Section 1 (pp. 1–2) as **author interpretation and literature background**, explaining that default macroscopic and microscopic models were developed for car-following and lane-disciplined passenger cars.
     - In Section 4 (pp. 6–8), the paper compares simulated motorcycle route choice against **conventional static shortest-path traffic assignment**, not passenger-car empirical choices.
   - **Verdict:** **PARTIALLY SUPPORTED / CONFLATED**. Divergence from static shortest paths is directly supported by simulation; the empirical contrast with passenger cars is unmeasured background motivation.
   - **Correction Applied:** Narrow the manuscript claim to divergence from **static shortest-path network assignment**, removing the unverified empirical contrast with passenger-car drivers.

2. **Claim 2: "Dynamic route adjustment in response to encountered traffic conditions"**
   - **Source Audit:**
     - The study did **not** empirically observe or measure real-time en-route route switching by physical riders navigating city streets.
     - The empirical element is a **discrete-choice model estimated on stated-preference (SP) questionnaire data** (Section 3.2, Table 1, pp. 4–6), where $35.6\%$ of respondents indicated a willingness to divert under hypothetical Variable Message Sign (VMS) congestion advice.
     - The dynamic adjustment element is an **algorithmic simulation in Aimsun** (Section 4.3–4.4, pp. 6–9), where simulated motorcycle agents update their paths at virtual information nodes using Macroscopic Fundamental Diagram (MFD) feedback.
     - Crucially, the authors explicitly note in Section 1 and Section 5 that real-world roadside traffic information systems (such as VMS) for two-wheelers are **largely absent** in developing cities like Cần Thơ, which in practice restricts optimal real-time routing.
   - **Verdict:** **PARTIALLY SUPPORTED / SIMULATION-BASED**. Directly supported as an SP-estimated choice model and simulated dynamic traffic assignment under hypothetical VMS guidance; **UNSUPPORTED** as physical en-route switching by real riders.
   - **Correction Applied:** Reframe the claim to describe **discrete-choice stated-preference modeling and microscopic traffic simulation under traffic-information scenarios**, strictly distinguishing modeled compliance from unguided physical route switching.

3. **Reconciled Citation Tier Counts:** Exactly **8 Essential Citations** and **4 Optional Contextual Citations** (Total: 12 citations).
4. **Structural Stability:** Outline ([`paper1_related_work_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_outline_v1.md)) and Section I remain unchanged and frozen.

---

## 2. Reconciled Citation Density & Tiering Matrix

To fit the **340-word budget** ($\approx 46\text{ lines}$) without artificial crowding, citations are strictly partitioned:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        RECONCILED CITATION TIERING BREAKDOWN                            │
├────────┬─────────────────────────────┬──────────────┬───────────────────────────────────┤
│ Area   │ Citation Key                │ Tier         │ Exact Role in Section II          │
├────────┼─────────────────────────────┼──────────────┼───────────────────────────────────┤
│ II-A   │ kirby1969minimum            │ ESSENTIAL    │ Historical origin of movement-    │
│ (~90 w)│                             │              │ expanded networks for turns.      │
│        │ winter2002modeling          │ ESSENTIAL    │ Line graphs & directed edge states│
│        │                             │              │ s=(u,v) in route planning.        │
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

- **Essential Citations:** Exactly **8 Citations**.
- **Optional Citations:** Exactly **4 Citations**.
- **Total Retained Citations:** Exactly **12 Citations** ($8 + 4 = 12$).

---

## 3. Geographic Scope and Source Evidence Audit

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

## 4. Granular Passage-by-Passage Evidence Mapping

### Area II-A: Movement-Expanded State Spaces and Turn-Aware Routing (~90 words)

#### 1. Kirby and Potts (1969) — `kirby1969minimum`
- **Full Reference:** R. F. Kirby and R. B. Potts, "The minimum route problem for networks with turn penalties and prohibitions," *Transportation Research*, vol. 3, no. 3, pp. 397–408, 1969. DOI: [10.1016/0041-1647(69)80022-5](https://doi.org/10.1016/0041-1647(69)80022-5).
- **Physical Passages Audited:** Section 2 (pp. 398–401: Mathematical graph expansion for turn penalties/prohibitions); Section 3 (pp. 401–404: State transition equations); Section 4 (pp. 404–407: Algorithmic tree building).
- **Exact Supported Claim in Section II:**
  > Movement-expanded network representations were historically formulated in traffic assignment models to enforce turn prohibitions and junction delay penalties during tree-building.
- **Evidence Classification:** **DIRECT SUPPORT (ESSENTIAL).**
- **Limitation & Caution:** Formulated for offline macroscopic traffic assignment. Distinguish static tree-building from online goal-directed label-setting algorithms ($A^*$).

---

#### 2. Winter (2002) — `winter2002modeling`
- **Full Reference:** S. Winter, "Modeling costs of turns in route planning," *GeoInformatica*, vol. 6, no. 4, pp. 345–361, 2002. DOI: [10.1023/A:1020853410145](https://doi.org/10.1023/A:1020853410145).
- **Physical Passages Audited:** Section 3 (pp. 348–352: Dual line-graph transformation $L(G) = (V_L, E_L)$); Section 4 (pp. 353–356: Node-pair state expansion in Dijkstra); Section 5 (pp. 356–359: Demonstration that turn penalties eliminate zig-zag paths).
- **Exact Supported Claim in Section II:**
  > Dual line-graph transformations and directed edge-state representations in route planning preserve incoming-edge context, establishing that incorporating turn penalties eliminates unrealistic zig-zag maneuvers through street grids.
- **Evidence Classification:** **DIRECT SUPPORT (ESSENTIAL).**
- **Limitation & Caution:** Evaluated geometric delay penalties on planar grids without vehicle-specific road hierarchies or mode-differentiated turn kinematics.

---

### Area II-B: Hierarchical Routing and Metric Customization (~80 words)

#### 3. Luxen and Vetter (2011) — `luxen2011realtime`
- **Full Reference:** D. Luxen and C. Vetter, "Real-time routing with OpenStreetMap data," in *Proc. 19th ACM SIGSPATIAL (GIS '11)*, ACM, 2011, pp. 513–516. DOI: [10.1145/2093973.2094062](https://doi.org/10.1145/2093973.2094062).
- **Physical Passages Audited:** Section 2 (pp. 513–514: OSRM Contraction Hierarchies architecture); Section 3 (pp. 514–515: Speed profile parsing).
- **Exact Supported Claim in Section II:**
  > Open-source routing engines such as OSRM implement node-based Contraction Hierarchies calibrated for automobile speed profiles on high-capacity arterials.
- **Evidence Classification:** **DIRECT SUPPORT (OPTIONAL).**
- **Limitation & Caution:** Documents an automobile-centric baseline; can be omitted or merged if word count requires compression.

---

#### 4. Geisberger and Vetter (2011) — `geisberger2011efficient`
- **Full Reference:** R. Geisberger and C. Vetter, "Efficient Routing in Road Networks with Turn Costs," in *Proc. 10th Int. Symp. Experimental Algorithms (SEA 2011)*, LNCS 6630, Springer, 2011, pp. 100–111. DOI: [10.1007/978-3-642-20662-7_9](https://doi.org/10.1007/978-3-642-20662-7_9).
- **Physical Passages Audited:** Section 3 (pp. 102–105: Edge-based Contraction Hierarchies); Section 4 (pp. 105–108: Turn tables at junctions and shortcut construction).
- **Exact Supported Claim in Section II:**
  > Contraction Hierarchies incorporate turn costs through turn-expanded core nodes and pre-computed shortcut construction, statically embedding turn tables into shortcuts during preprocessing.
- **Evidence Classification:** **DIRECT SUPPORT (ESSENTIAL).**
- **Limitation & Caution:** Turn costs are statically integrated into shortcut construction. If turn penalties or road multipliers change dynamically, preprocessing shortcuts must be updated.

---

#### 5. Delling et al. (2017) — `delling2017customizable`
- **Full Reference:** D. Delling, A. V. Goldberg, T. Pajor, and R. F. Werneck, "Customizable Route Planning in Road Networks," *Transportation Science*, vol. 51, no. 2, pp. 566–591, 2017. DOI: [10.1287/trsc.2014.0579](https://doi.org/10.1287/trsc.2014.0579).
- **Physical Passages Audited:** Section 2 (pp. 568–571: Metric dependency problem in standard CH); Section 3 (pp. 571–576: PUNCH graph partitioning); Section 4 (pp. 577–582: Multi-level metric customization phase).
- **Exact Supported Claim in Section II:**
  > Customizable Route Planning (CRP) decouples metric-independent topology partitioning from a fast metric-dependent customization phase, enabling flexible metric updates on fixed graph partitions.
- **Evidence Classification:** **DIRECT SUPPORT (ESSENTIAL).**
- **Limitation & Caution:** CRP supports fast metric customization on fixed partitions. Do **NOT** cite Delling et al. as direct proof that uncontracted search is an immediate alternative.

---

#### 6. Bast et al. (2016) — `bast2016route`
- **Full Reference:** H. Bast, D. Delling, A. Goldberg, M. Müller-Hannemann, T. Pajor, P. Sanders, D. Wagner, and R. F. Werneck, "Route Planning in Transportation Networks," in *Algorithm Engineering*, LNCS 9220, Springer, 2016, pp. 19–80. DOI: [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2).
- **Physical Passages Audited:** Section 2.3 (pp. 8–9: Arc separators and CRP customization); Section 2.4 (pp. 9–11: Contraction Hierarchies); Section 3.1 (pp. 25–26: Preprocessing vs. customization vs. query time trade-offs; Table 2).
- **Exact Supported Claim in Section II:**
  > Surveys shortest-path speedup techniques, demonstrating that customizable hierarchies support flexible metric updates on pre-partitioned overlays while outlining trade-offs between preprocessing investment and query latency.
- **Evidence Classification:** **CONTEXTUAL SURVEY SUPPORT (ESSENTIAL).**
- **Limitation & Caution:** Must **NOT** claim that Bast et al. supports "multi-attribute cost updates" in customizable hierarchies. Citing is strictly restricted to flexible metric customization and speedup trade-offs.

---

### Area II-C: Two-Wheeler Routing and Road-Class Impedance (~95 words)

#### 7. Promraksa et al. (2022) — `promraksa2022lane`
- **Full Reference:** T. Promraksa, T. Satiennam, W. Satiennam, and N. Kronprasert, "Lane-Filtering Behavior of Motorcycle Riders at Signalized Intersections," *J. Adv. Transp.*, vol. 2022, Art. ID 5662117, 2022. DOI: [10.1155/2022/5662117](https://doi.org/10.1155/2022/5662117).
- **Physical Passages Audited:** Section 1 (p. 2: Motorcycle vehicle registration statistics in Thailand); Section 3–4 (pp. 4–11: Videographic empirical data collection across 4 signalized intersections in Khon Kaen, Thailand).
- **Exact Supported Claim in Section II:**
  > In Thailand, motorcycles constitute a substantial share of registered vehicles, and empirical videographic observations characterize motorcycle lane-filtering behavior through stationary vehicle queues at signalized intersections in Khon Kaen.
- **Evidence Classification:** **CONTEXTUAL TRAFFIC-FLOW SUPPORT (OPTIONAL).**
- **Limitation & Caution:** Restricted strictly to Thailand and observed filtering kinematics. Do **NOT** generalize across all Asian cities. Omissible from Section II if word budget requires compression, as it is already cited in Section I.

---

#### 8. Kotagi, Raj, and Asaithambi (2020) — `kotagi2020modeling`
- **Full Reference:** P. B. Kotagi, P. Raj, and G. Asaithambi, "Modeling lateral placement and movement of vehicles in mixed traffic conditions," *J. Traffic Transp. Eng.*, vol. 7, no. 6, pp. 860–873, 2020. DOI: [10.1016/j.jtte.2018.06.008](https://doi.org/10.1016/j.jtte.2018.06.008).
- **Physical Passages Audited:** Section 3 (pp. 863–867: Videographic trajectory extraction in Bengaluru and Mangaluru); Section 4 (pp. 867–871: Speed dispersion and lateral movements on undivided urban corridors).
- **Exact Supported Claim in Section II:**
  > Field measurements on undivided urban corridors in Bengaluru and Mangaluru document severe speed dispersion and lateral placement differences between two-wheelers and heavy passenger vehicles.
- **Evidence Classification:** **CONTEXTUAL TRAFFIC-FLOW SUPPORT (OPTIONAL).**
- **Limitation & Caution:** Empirical traffic-flow physics on mid-block segments; not a routing algorithm. Omissible from Section II if space is constrained.

---

#### 9. Fadilah, Nishiuchi, and Ngoc (2024) — `fadilah2024identifying`
- **Full Reference:** S. R. Fadilah, H. Nishiuchi, and A. M. Ngoc, "Identifying the role of route choice behavior of motorcycle riders in microscopic simulation modeling under mixed traffic conditions," *Transp. Res. Interdiscip. Perspect.*, vol. 28, p. 101247, 2024. DOI: [10.1016/j.trip.2024.101247](https://doi.org/10.1016/j.trip.2024.101247).
- **Physical Passages Audited:**
  - Section 1 (Introduction, pp. 1–2): Context of heterogeneous traffic; motivation regarding limitations of car-centric simulation models and conventional static shortest paths.
  - Section 2 (Study Area & Survey Design, pp. 2–4): Field context in Ninh Kiều District, Cần Thơ City, Vietnam; Stated Preference (SP) questionnaire administered to $N = 301$ motorcycle riders.
  - Section 3 (Methodology, pp. 4–6): Binary logit and mixed binary logit formulation of route choice; utility functions incorporating travel time, congestion levels, and hypothetical Variable Message Sign (VMS) information.
  - Section 4 (Results & Simulation, pp. 6–9): Table 1 (Discrete choice parameter estimation; $35.6\%$ stated route switching under VMS guidance); Aimsun dynamic traffic simulation with Macroscopic Fundamental Diagram (MFD) feedback showing up to $84\%$ capacity improvement under full compliance.
  - Section 5 (Discussion & Conclusions, pp. 9–10): Real-world limitations (lack of physical roadside information systems for motorcycles in developing cities); implications for microscopic simulation accuracy.
- **Granular Claim-by-Claim Evaluation:**
  - **Claim 1 ("Motorcycle route choice differing from conventional passenger-car shortest paths"):**
    - *Passages:* Section 1 (pp. 1–2), Section 3 (pp. 4–5), Section 4 (pp. 6–8).
    - *Evidence Type:* **Author interpretation / narrative motivation** for passenger cars (no empirical car route data collected); **Simulation modeling** for departure from static shortest paths.
    - *Distinction:* Compares modeled motorcycle routing against static shortest-path assignment, NOT empirical passenger-car routes.
    - *Verdict:* **PARTIALLY SUPPORTED / CONFLATED**. (Divergence from static shortest paths is modeled; mode comparison with passenger cars is an unmeasured narrative motivation).
  - **Claim 2 ("Dynamic route adjustment in response to encountered traffic conditions"):**
    - *Passages:* Section 3.2 (pp. 4–5), Table 1 (p. 6), Section 4.3–4.4 (pp. 7–9), Figures 5–8.
    - *Evidence Type:* **Model Estimation on Stated Preference Data** (for willingness to switch); **Microscopic Simulation in Aimsun** (for dynamic path updates).
    - *Distinction:* The study does **NOT** present empirical observations of real riders dynamically switching routes en-route during physical trips. Real-world roadside traffic information is acknowledged as largely absent in Cần Thơ. Dynamic adjustment is an algorithmic simulation mechanism under hypothetical information compliance.
    - *Verdict:* **PARTIALLY SUPPORTED / SIMULATION-BASED**. (Supported as an SP discrete-choice model and simulated dynamic traffic assignment; UNSUPPORTED as empirical physical route switching by real riders).
- **Exact Supported Claim in Section II (Narrowed & Reconciled):**
  > Stated-preference discrete-choice modeling and microscopic simulation of motorcycle traffic in Ninh Kiều District, Cần Thơ, Vietnam, demonstrate that motorcycle route selection departs from static shortest-path assignments when modeled under traffic-information scenarios.
- **Evidence Classification:** **CONTEXTUAL BEHAVIORAL & SIMULATION SUPPORT (ESSENTIAL).**
- **Limitation & Caution:**
  - Case study is strictly located in **Ninh Kiều District, Cần Thơ, Vietnam**.
  - Scoped strictly to stated-preference discrete choice modeling and Aimsun microscopic simulation; does **NOT** constitute empirical tracking of real-world dynamic route switching.
  - Does **NOT** empirically evaluate or compare passenger-car driver routes.
  - Does **NOT** validate Paper 1's configured numerical impedance multipliers ($0.90\text{--}4.00$, $0.80$ flyover override).

---

#### 10. Asvial, Pandoyo, and Arifin (2020) — `asvial2020entropy`
- **Full Reference:** M. Asvial, M. F. G. Pandoyo, and A. S. Arifin, "Entropy-Based k Shortest-Path Routing for Motorcycles: A Simulated Case Study in Jakarta," *IJACSA*, vol. 11, no. 7, pp. 438–445, 2020. DOI: [10.14569/IJACSA.2020.0110758](https://doi.org/10.14569/IJACSA.2020.0110758).
- **Physical Passages Audited:** Section III-A (p. 443: Map configuration prioritizing narrow streets); Section III-B (pp. 443–444: EBkSP formulation); Section V-A (pp. 444–445: Simulation case study across 6 OD corridors in South Jakarta).
- **Exact Supported Claim in Section II:**
  > Formulates motorcycle routing using $k$-shortest paths generated without turn penalties ($\text{turn cost} = 0$), followed by post-hoc Entropy-TOPSIS multi-criteria re-ranking over pre-computed candidate routes.
- **Evidence Classification:** **DIRECT ALGORITHMIC SUPPORT (ESSENTIAL).**
- **Limitation & Caution:** Turn costs are completely ignored during path generation; multi-criteria evaluation operates post-hoc over pre-computed shortest paths. Narrow claim strictly to Asvial et al.

---

### Area II-D: Research Positioning and Synthesis (~75 words)

#### 11. Zografos and Androutsopoulos (2004) — `zografos2004heuristic`
- **Full Reference:** K. G. Zografos and K. N. Androutsopoulos, "A heuristic algorithm for solving hazardous materials routing problems," *European Journal of Operational Research*, vol. 152, no. 2, pp. 507–519, 2004. DOI: [10.1016/S0377-2217(03)00041-9](https://doi.org/10.1016/S0377-2217(03)00041-9).
- **Physical Passages Audited:** Section 2 (pp. 509–512: Bi-criteria path finding on edge-expanded road network); Section 3 (pp. 512–515: Turn penalties and branch-and-bound heuristic).
- **Exact Supported Claim in Section II:**
  > Multi-objective shortest paths incorporating turn penalties have been formulated on edge-expanded graphs for specialized fleet operations (e.g., hazardous materials transport).
- **Evidence Classification:** **CONTEXTUAL COMPARATIVE SUPPORT (ESSENTIAL).**
- **Limitation & Caution:** Evaluated on hazmat trucks using branch-and-bound; differs fundamentally from two-wheeler urban impedance, online spatial $A^*$ search, and scaled Haversine admissibility.

---

#### 12. Kumar et al. (2025) — `kumar2025realtime`
- **Full Reference:** K. D. Kumar, M. L. Anitha, and M. N. Veena, "Real-Time Bengaluru City Traffic Congestion Prediction with Integrated Deep Learning Models," *Int. J. Transp. Dev. Integr.*, vol. 9, no. 3, pp. 619–628, 2025. DOI: [10.18280/ijtdi.090315](https://doi.org/10.18280/ijtdi.090315).
- **Physical Passages Audited:** Section 3 (pp. 621–624: Sensor data along Hosur Road, MG Road, Trinity Circle); Section 4 (pp. 624–627: Saturated arterial bottleneck congestion in Bengaluru).
- **Exact Supported Claim in Section II:**
  > Contextual background studies document chronic arterial bottleneck congestion and travel-time variability across major radial corridors in Bengaluru.
- **Evidence Classification:** **CONTEXTUAL BACKGROUND EVIDENCE (OPTIONAL).**
- **Limitation & Caution:** Provides general traffic context in Bengaluru; do **NOT** use the term "ground truth". Do not claim our search integrates deep learning prediction. Omissible if synthesis space is tight.

---

## 5. Master Bibliography Traceability and Scope Status

- **Total Retained Citations:** **12 citations** (Exactly **8 Essential**, Exactly **4 Optional**).
- **Excluded Citations:**
  - `hart1968formal`: Excluded from Section II; relocated to Section IV.
  - `goldberg2005computing`: Excluded from Section II; landmark ALT not relevant.
  - `abraham2013alternative`: Excluded from Paper 1; segregated to Paper 2.
- **Master Bibliography Match:** 100% verified in [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib).
- **New References Proposed:** **Zero.**

---

*Reconciled evidence map certified under `evidence-integrity-audit` and `blrmap-research-protocol`.*
