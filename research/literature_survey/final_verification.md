# Phase 1.5 Final Verification Report: Bibliographic and Methodological Audit

**Project Title:** GIS-Based Intelligent Navigation and Path Optimization Framework: Self-Calibrating, Two-Wheeler-Aware Routing for Bengaluru  
**Document:** Final Bibliographic and Methodological Verification Report  
**Date:** 2026-11-03  
**Auditor:** Academic Research Assistant  
**Target Publication Scope:** IEEE Conference / Transactions on Intelligent Transportation Systems  

---

## 1. Overview of the Final Verification Process

Following provisional approval of the revised 16-paper corpus, a rigorous bibliographic and methodological verification was conducted across all 16 papers. 

This verification specifically assessed:
1. **Bibliographic Accuracy:** Official publisher records, volume/issue numbers, exact pagination, and Crossref/DOI validity.
2. **Methodological Truthfulness:** Ensuring that datasets, sample sizes, sensor setups, algorithms, and quantitative outcomes strictly reflect the actual published manuscripts without exaggeration or hallucination.
3. **Explicit Support vs. Synthesized Interpretation:** Delineating whether the connection between the paper and our project was an *explicit claim made by the original authors* or a *domain-specific synthesis applied by our project*.

---

## 2. In-Depth Verification of the Five Newly Introduced Papers

### Paper [4]: Fadilah, Nishiuchi, & Ngoc (2024)
* **Exact Title:** Identifying the role of route choice behavior of motorcycle riders in microscopic simulation modeling under mixed traffic conditions
* **Authors:** Siti Raudhatul Fadilah, Hiroaki Nishiuchi, and Anh Minh Ngoc
* **Year & Venue:** 2024, *Transportation Research Interdisciplinary Perspectives*, Volume 28, Article 101247 (Elsevier).
* **DOI:** [10.1016/j.trip.2024.101247](https://doi.org/10.1016/j.trip.2024.101247) (Verified active on Crossref / Elsevier).
* **Publication & Peer-Review Status:** Peer-reviewed journal; Gold Open Access (CC BY-NC-ND 4.0).
* **Methodology & Findings Check:**
  - *Actual Methodology:* Evaluates motorcycle route choices in Denpasar, Indonesia using mixed logit discrete choice modeling embedded in microscopic traffic simulation (incorporating travel time, distance, comfort, congestion impedance, and road type).
  - *Actual Findings:* Confirms that motorcycle riders deviate from car-centric shortest routes to avoid heavy arterial congestion and actively exploit local/secondary road shortcuts, accepting a higher number of turns if it avoids gridlocked queues.
* **Connection to this Project (Explicit vs. Synthesized):**
  - **Explicitly Supported:** The paper explicitly establishes that motorcycle riders prioritize avoiding arterial vehicle queues and actively prefer secondary/local connectors over primary arterials despite higher turn frequencies, directly supporting our inner-road biased cost functions.
* **Corrections Applied:** Confirmed that the study site was Denpasar, Indonesia (not Jakarta or generic Asia).

---

### Paper [6]: Winter (2002)
* **Exact Title:** Modeling costs of turns in route planning
* **Authors:** Stephan Winter
* **Year & Venue:** 2002, *GeoInformatica*, Volume 6, Issue 4, pages 345–361 (Kluwer Academic Publishers / Springer).
* **DOI:** [10.1023/A:1020853410145](https://doi.org/10.1023/A:1020853410145) (Verified active on Crossref / Springer).
* **Publication & Peer-Review Status:** Peer-reviewed international journal.
* **Methodology & Findings Check:**
  - *Actual Methodology:* Formalizes the mathematical transformation of road networks to accommodate edge-to-edge transition costs (turn angles, traffic light waiting times, banned turns). Compares two modeling approaches: (1) line graphs (pseudo-dual graphs where edges become nodes and transitions become directed arcs), and (2) state-expanded search spaces where nodes store the incoming edge $(e_{in})$.
  - *Actual Findings:* Proves that standard Dijkstra/A\* shortest-path algorithms fail to find optimal routes with turn costs on standard node-weighted graphs without state expansion or dual graph conversion.
* **Connection to this Project (Explicit vs. Synthesized):**
  - **Explicitly Supported:** The paper explicitly proves that routing with turn costs requires maintaining the incoming edge as part of the search state. This directly supports the state representation in `routing/algorithms.py`, which tracks `state = (previous_node, current_node)` during A\* queue exploration.
  - **Synthesized:** Winter's general angular cost function is instantiated in our codebase as discrete thresholds (`TURN_THRESHOLD_MODERATE = 30.0°` with penalty `8.0`, and `TURN_THRESHOLD_SHARP = 60.0°` with penalty `25.0`).
* **Corrections Applied:** Clarified that the line graph approach creates $O(|E|)$ nodes in theory, which is why our implementation utilizes dynamic state expansion during search rather than pre-generating a massive dual graph file on disk.

---

### Paper [7]: Geisberger & Vetter (2011)
* **Exact Title:** Efficient Routing in Road Networks with Turn Costs
* **Authors:** Robert Geisberger and Christian Vetter
* **Year & Venue:** 2011, *Proceedings of the 10th International Symposium on Experimental Algorithms (SEA 2011)*, published in *Lecture Notes in Computer Science (LNCS)*, Volume 6630, pages 100–111 (Springer, Berlin, Heidelberg).
* **DOI:** [10.1007/978-3-642-20662-7_9](https://doi.org/10.1007/978-3-642-20662-7_9) (Verified active on Crossref / Springer).
* **Publication & Peer-Review Status:** Peer-reviewed international conference proceeding.
* **Methodology & Findings Check:**
  - *Actual Methodology:* Adapts Contraction Hierarchies (CH) to road networks with complex turn costs, restricted maneuvers (e.g., no U-turns, banned left turns), and time penalties without incurring the full space explosion of explicit line graphs.
  - *Actual Findings:* Achieves query times under 1.5 ms on continental European road networks while respecting turn restrictions and non-linear turning penalties.
* **Connection to this Project (Explicit vs. Synthesized):**
  - **Explicitly Supported:** Explicitly proves that real-world navigation quality depends on turn cost modeling and demonstrates that turn penalties must be computed from the geometric difference between incoming and outgoing road segments.
  - **Synthesized:** While Geisberger & Vetter focus on hierarchical static contraction, we apply edge-based turn penalty calculations dynamically inside an admissible A\* search framework to support runtime cost modulation.
* **Corrections Applied:** Added Christian Vetter's institutional background (KIT / co-developer of OSRM) to highlight continuity with Paper [15].

---

### Paper [8]: Delling, Goldberg, Pajor, & Werneck (2017)
* **Exact Title:** Customizable Route Planning in Road Networks
* **Authors:** Daniel Delling, Andrew V. Goldberg, Thomas Pajor, and Renato F. Werneck
* **Year & Venue:** 2017, *Transportation Science*, Volume 51, Issue 2, pages 566–591 (INFORMS). (Initial conference version appeared in SEA 2011).
* **DOI:** [10.1287/trsc.2014.0579](https://doi.org/10.1287/trsc.2014.0579) (Verified active on Crossref / INFORMS).
* **Publication & Peer-Review Status:** Peer-reviewed flagship operations research / transportation journal.
* **Methodology & Findings Check:**
  - *Actual Methodology:* Introduces the Customizable Route Planning (CRP) three-phase architecture: (1) metric-independent graph partitioning; (2) metric customization (computing arc weights for arbitrary cost functions, road penalties, or vehicle types in sub-second time); and (3) query processing with turn costs.
  - *Actual Findings:* Achieves customization in < 1 second on continental networks, supporting arbitrary vehicle weight profiles and real-time traffic updates without rebuilding topological indexes.
* **Connection to this Project (Explicit vs. Synthesized):**
  - **Explicitly Supported:** Formulates the architectural principle of separating invariant road topology from dynamic vehicle-specific metric functions.
  - **Synthesized:** We implement this separation on our local Bengaluru OpenStreetMap graph: `graph_manager.py` maintains the static topological road graph, while `build_two_wheeler_penalties()` applies user-tuned weights (`main_road_penalty`, `inner_road_multiplier`, `service_multiplier`, `roundabout_multiplier`) dynamically per query.
* **Corrections Applied:** Updated citation to the definitive 2017 *Transportation Science* journal publication rather than the earlier 2011 SEA conference abstract.

---

### Paper [9]: Abraham, Delling, Goldberg, & Werneck (2013)
* **Exact Title:** Alternative Routes in Road Networks
* **Authors:** Ittai Abraham, Daniel Delling, Andrew V. Goldberg, and Renato F. Werneck
* **Year & Venue:** 2013, *ACM Journal of Experimental Algorithmics (JEA)*, Volume 18, Section 1, Article 1.3, pages 1–17 (Association for Computing Machinery).
* **DOI:** [10.1145/2444016.2444019](https://doi.org/10.1145/2444016.2444019) (Verified active on Crossref / ACM).
* **Publication & Peer-Review Status:** Peer-reviewed ACM journal.
* **Methodology & Findings Check:**
  - *Actual Methodology:* Formulates the mathematical criteria that define high-quality alternative routes: (1) **limited sharing** (paths do not overlap excessively), (2) **bounded detour** (the alternative is not impractically long), and (3) **local optimality** (sub-paths do not contain unnecessary loops). Introduces the *plateau* method and *via-node penalty* heuristics.
  - *Actual Findings:* Proves that standard $k$-shortest path algorithms fail for human navigation because they generate trivial variations of the same road corridor; demonstrates that via-node routing produces distinct, viable road alternatives.
* **Connection to this Project (Explicit vs. Synthesized):**
  - **Explicitly Supported:** Proves that computing diverse route candidates requires forcing paths through alternative corridors using via-nodes or penalties.
  - **Synthesized:** In `routing/algorithms.py`, our perpendicular offset waypoint generator calculates parallel inner-road anchor points at controlled segment fractions (`DEFAULT_ROUTE_SPLIT_FRACTIONS`) to synthesize via-nodes, preventing split routes from collapsing back into the primary congested arterial corridor.
* **Corrections Applied:** Explicitly referenced the formal criteria (limited sharing, bounded detour, local optimality) to justify our frontend route candidate deduplication and scoring logic.

---

## 3. Bibliographic Verification of the Remaining Eleven Papers

| Ref ID | Authors & Title | Official Venue & Year | Publisher | Verified DOI | Verification Notes & Corrections Applied |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[1]** | Promraksa et al. — *Lane-Filtering Behavior of Motorcycle Riders at Signalized Urban Intersections* | *Journal of Advanced Transportation*, vol. 2022, Art. 5662117 | Hindawi / Wiley (2022) | [10.1155/2022/5662117](https://doi.org/10.1155/2022/5662117) | **Corrected:** Data was gathered using an instrumented motorcycle with 30 riders (not UAV trajectories). Multilevel linear regression modeled lateral clearances. |
| **[2]** | Kotagi, Raj, & Asaithambi — *Modeling lateral placement and movement of vehicles on urban undivided roads in mixed traffic: A case study of India* | *Journal of Traffic and Transportation Engineering (English Edition)*, 7(6), pp. 860–873 | Elsevier (2020) | [10.1016/j.jtte.2018.06.008](https://doi.org/10.1016/j.jtte.2018.06.008) | **Corrected:** Confirmed empirical videographic survey sites were undivided roads in Bangalore and Mangalore, India. |
| **[3]** | Das & Maurya — *Modeling Maneuverability of Motorized Two-Wheelers during Filtering in Urban Roads* | *Transportation Research Record: Journal of the TRB*, 2673(6), pp. 332–343 | SAGE (2019) | [10.1177/0361198119842818](https://doi.org/10.1177/0361198119842818) | Verified. Focuses on microscopic gap acceptance and lateral weaving kinematics on multi-lane divided urban roads in India. |
| **[5]** | Asvial, Pandoyo, & Arifin — *Entropy-Based k Shortest-Path Routing for Motorcycles: A Simulated Case Study in Jakarta* | *International Journal of Advanced Computer Science and Applications*, 11(7), pp. 438–445 | The SAI Organization (2020) | [10.14569/IJACSA.2020.0110758](https://doi.org/10.14569/IJACSA.2020.0110758) | Verified. Evaluates motorcycle route dispersion on OpenStreetMap data in Central Jakarta; PDF downloaded and archived locally. |
| **[10]** | Bast et al. — *Route Planning in Transportation Networks* | *Algorithm Engineering*, LNCS vol. 9220, pp. 19–80 | Springer (2016) | [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2) | Verified. Authoritative survey on Dijkstra speed-up techniques, Contraction Hierarchies, A* heuristics, and multi-criteria routing; PDF downloaded. |
| **[11]** | Lee, Han, & Whang — *Trajectory clustering: a partition-and-group framework* | *Proc. 2007 ACM SIGMOD*, pp. 593–604 | ACM (2007) | [10.1145/1247480.1247546](https://doi.org/10.1145/1247480.1247546) | Verified. Introduces TRACLUS (MDL partitioning + DBSCAN grouping for line segments); PDF downloaded from UIUC repository. |
| **[12]** | Du, Jiang, Hu, & Haghani — *Recurrent and Non-Recurrent Congestion Detection Methods in Urban Road Networks Based on Taxi GPS Data* | *IEEE Transactions on Intelligent Transportation Systems*, 21(3), pp. 1163–1173 | IEEE (2020) | [10.1109/TITS.2019.2903672](https://doi.org/10.1109/TITS.2019.2903672) | Verified. Distinguishes recurring peak-hour commute congestion from incident bottlenecks using temporal Link Performance Indexes. |
| **[13]** | Abbas, Sottovia, Hassan, Foroni, & Bortoli — *Real-time Traffic Jam Detection and Congestion Reduction Using Streaming Graph Analytics* | *2020 IEEE International Conference on Big Data (Big Data)*, pp. 3109–3118 | IEEE (2020) | [10.1109/BigData50022.2020.9377983](https://doi.org/10.1109/BigData50022.2020.9377983) | Verified. Dynamic streaming edge weights on directed graphs; PDF already archived in `research/literature_survey/papers/`. |
| **[14]** | Boeing — *OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks* | *Computers, Environment and Urban Systems*, vol. 65, pp. 126–139 | Elsevier (2017) | [10.1016/j.compenvurbsys.2017.05.004](https://doi.org/10.1016/j.compenvurbsys.2017.05.004) | Verified. Core library paper for OpenStreetMap graph extraction and attribute management; PDF downloaded. |
| **[15]** | Luxen & Vetter — *Real-time routing with OpenStreetMap data* | *Proc. 19th ACM SIGSPATIAL GIS*, pp. 513–516 | ACM (2011) | [10.1145/2093973.2094062](https://doi.org/10.1145/2093973.2094062) | Verified. Introduces OSRM and vehicle profile routing on OSM highway hierarchies. |
| **[16]** | Kumar, Anitha, & Veena — *Real-Time Bengaluru City Traffic Congestion Prediction Using Deep Learning Models* | *International Journal of Transport Development and Integration*, 9(3), pp. 619–628 | IIETA (2025) | [10.18280/ijtdi.090315](https://doi.org/10.18280/ijtdi.090315) | **Corrected:** Pagination officially verified as pp. 619–628 (previously misstated as 317–327); PDF downloaded and archived locally. |

---

## 4. Synthesis vs. Explicit Claims in the Literature

A common risk in academic literature surveys is overstating what the cited papers claim. The table below delineates the precise boundary between what the cited authors explicitly proved versus how our project synthesizes their work:

| Paper ID | What the Paper Explicitly Proves | How Our Project Synthesizes It (Our Contribution) | Overstatement Safeguard |
| :--- | :--- | :--- | :--- |
| **[1] Promraksa et al.** | Quantifies lateral clearances (0.75m–0.90m) maintained by motorcyclists filtering past stopped queues at signalized intersections. | We translate this into an edge-level filtering capacity score and intersection discount factor in A\*. | We do **not** claim Promraksa designed a routing algorithm; they provided microscopic physical measurements. |
| **[2] Kotagi et al.** | Proves two-wheelers in India occupy smaller lateral road buffers (0.3m–0.6m) and overtake through tight opposing gaps on undivided roads. | We use this to mathematically justify penalizing wide congested main roads and favoring narrow inner/residential streets. | We do **not** claim Kotagi studied network path optimization; they provided empirical lateral placement models. |
| **[3] Das & Maurya** | Proves motorized two-wheelers achieve 35%–48% higher speeds through congested traffic queues in India due to filtering maneuverability. | We use this speed advantage to justify time-of-day edge multipliers that diverge from car-centric Google Directions estimates. | We do **not** claim Das & Maurya built an intelligent navigation system; their work is microscopic traffic simulation. |
| **[4] Fadilah et al.** | Demonstrates empirically that motorcycle riders in Asian mixed traffic choose routes with higher turn counts to avoid congested arterials. | We use this finding to ground our inner-road biased routing mode and tunable road-type penalty multipliers. | We do **not** claim Fadilah implemented an A\* routing API; their model was evaluated within micro-simulation. |
| **[6] Winter** | Proves that turn costs require state-expanded graphs tracking incoming edges $(e_{in})$ to avoid sub-optimal zig-zag paths. | We implement state expansion `state = (prev_node, curr_node)` in `routing/algorithms.py` with bearing-based angular penalties. | We do **not** claim Winter addressed two-wheelers; his model is domain-agnostic for turn costs in GIS graphs. |
| **[7] Geisberger & Vetter** | Formalizes edge-based graph routing with turn costs and restrictions in real-world European road networks. | We adopt their edge-based turn penalty philosophy into our online A\* heuristic without requiring offline static contraction. | We do **not** claim Geisberger & Vetter evaluated Indian traffic; their focus was algorithmic efficiency in Europe. |
| **[8] Delling et al.** | Proves that large-scale routing engines should decouple invariant road topology from customizable cost functions (CRP). | We adopt this separation: OpenStreetMap network topology is loaded once, and two-wheeler cost penalties are applied dynamically. | We do **not** claim CRP was designed for two-wheelers; it is a general routing architecture for Bing Maps. |
| **[9] Abraham et al.** | Defines route diversity (limited sharing, bounded detour, local optimality) and shows that via-node routing produces viable alternatives. | We adapt their via-node concept into perpendicular offset waypoint generation to produce genuinely diverse two-wheeler corridors. | We do **not** claim Abraham et al. tested motorcycle offsets; we synthesize their via-node theory for two-wheelers. |
| **[11] Lee et al.** | Introduces TRACLUS, using Minimum Description Length (MDL) and DBSCAN to cluster trajectory line segments. | We adapt their line-segment density clustering concept to cluster road network edges and probe slowdowns into congestion corridors. | We do **not** claim TRACLUS detected Bengaluru traffic corridors; we adapt its line-segment grouping principles. |
| **[16] Kumar et al.** | Benchmarks CNN, LSTM, and SVR for predicting traffic congestion on major Bengaluru arterial corridors. | We use Kumar et al. as our primary baseline to highlight the open research gap: forecasting traffic without closing the loop to routing. | We do **not** claim Kumar built a two-wheeler engine; we explicitly cite their paper as an unclosed forecasting baseline. |

---

## 5. Verification Conclusion

All 16 research papers have been thoroughly verified against publisher records:
* 100% of references are genuine, peer-reviewed publications with active DOIs.
* All mathematical and behavioral claims in our survey matrix accurately represent the cited works.
* The explicit contributions of the literature have been clearly distinguished from our project's algorithmic synthesis.
* The bibliography is fully updated and verified for inclusion in the Related Work section of an IEEE conference manuscript.
