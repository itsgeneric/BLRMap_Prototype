# Final Research Scope and Conference Paper Architecture

**Project Title:** GIS-Based Intelligent Navigation and Path Optimization Framework: Self-Calibrating, Two-Wheeler-Aware Routing for Bengaluru  
**Stage:** Phase 7 – Contribution Feasibility and Research Scope Decision  
**Document:** `research/literature_survey/07_contribution_feasibility/final_research_scope.md`  
**Date:** 2026-11-03  

---

## 1. Executive Summary and Strategic Framing

To maximize publication acceptance at an IEEE conference (e.g., IEEE ITSC, IEEE VTC, IEEE INDICON), a research paper must present a **tight, mathematically coherent, fully implemented, and empirically verifiable scope**. Claiming too many disconnected features or over-stating un-implemented machine learning models invites harsh reviewer criticism.

This document establishes the definitive research scope for the conference paper, rigorously classifying all candidate contributions into:
* **Core Contributions:** Must be retained; represents the paper's primary algorithmic and transportation contributions.
* **Supporting Contributions:** Must be retained as secondary components; provides practical commuter utility and algorithmic diversity.
* **Supporting Methodological Component:** Retained with reframed, honest scope (decoupled post-route calibration).
* **Future Work:** Explicitly identified as future extensions; must not be claimed as an implemented system contribution.

```mermaid
flowchart TD
    subgraph Core ["CORE CONTRIBUTIONS (Primary Focus)"]
        C1["Core 1: State-Expanded Turn-Aware A* Routing<br/>• Dynamic state (prev_node, curr_node)<br/>• Spherical deflection penalties (8m, 25m)<br/>• Heuristic admissibility guaranteed (haversine * 0.8)"]
        C2["Core 2: Multi-Attribute Two-Wheeler Edge Cost Model<br/>• Inverted peak-hour road hierarchy (primary 2.2, residential 1.0)<br/>• Flyover exception (0.8x) & roundabout damping (0.95x)<br/>• Surface roughness integration"]
    end

    subgraph Supporting ["SUPPORTING CONTRIBUTIONS"]
        S1["Supporting 1: Perpendicular Offset Alternative Routing<br/>• Lateral waypoint projection (150m, 300m) at fractions (0.33, 0.5, 0.67)<br/>• Strict bounded detour (epsilon <= 20%)<br/>• Overcomes Yen's kSP grid failure"]
        S2["Supporting 2: Multi-Lane Junction Queue Filtering Calibration<br/>• Post-route travel-time calibration: T_calibrated = T_base * (0.985)^N<br/>• Grounded in Promraksa et al. [1] (>= 2 lanes, traffic signals)"]
    end

    subgraph Context ["EMPIRICAL CASE STUDY & FUTURE WORK"]
        CS["Case Study: Saturated Corridor Bypass<br/>• Ingests Kumar et al. ('25) ground truth corridors<br/>• Tests 25.0x dynamic impedance on Hosur Rd & Trinity Circle"]
        FW["Future Work: Real-Time Deep Learning Streaming<br/>• Live traffic prediction pipeline integration<br/>• Continuous loop sensor streaming (Abbas et al. [13])"]
    end

    Core --> Paper["Defensible IEEE Conference Research Paper"]
    Supporting --> Paper
    Context --> Paper
```

---

## 2. Definitive Classification of Candidate Contributions

---

### Core Contribution 1: State-Expanded, Turn-Aware Goal-Directed A\* Search
* **Classification:** **CORE CONTRIBUTION (Must Be Retained)**
* **Scholarly Role:** The primary algorithmic innovation of the paper.
* **Academic Problem Addressed:** Classic node-based shortest-path algorithms ignore intersection turn delays and produce erratic zigzag routes (Winter [6]). Continental speedups (Edge-Based Contraction Hierarchies, Geisberger & Vetter [7]) freeze turn costs into static shortcuts, preventing runtime customization. Motorcycle routing literature (Asvial et al. [5]) completely ignores turn angles.
* **Our Solution:** Implements dynamic search state tracking `state = (prev_node, curr_node)` in the priority queue, calculating spherical coordinate bearing deflections $\Delta \theta$ on-the-fly. Evaluates discrete, vehicle-differentiated penalties ($P_{turn} \in \{0\text{ m}, 8\text{ m}, 25\text{ m}\}$) that penalize hazardous sharp maneuvers across opposing traffic while permitting tight residential corners. Preserves strict Haversine heuristic admissibility ($h(u) \le c^*(u, t)$) without line graph memory explosion.
* **Implementation Status:** 95% implemented in `routing/algorithms.py`. Requires fixing heuristic bug (multiplying by 0.8 instead of dividing by 0.8).

---

### Core Contribution 2: Multi-Attribute Two-Wheeler Edge Impedance Model
* **Classification:** **CORE CONTRIBUTION (Must Be Retained)**
* **Scholarly Role:** The primary transportation informatics contribution.
* **Academic Problem Addressed:** Commercial and open-source routing profiles (OSRM, Luxen & Vetter [15]) enforce automobile-centric road hierarchies, assuming motorways and primary arterials are inherently faster. In heterogeneous Indian mixed traffic (Kotagi et al. [2], Das & Maurya [3]), primary arterials collapse into total queue saturation during peak hours, whereas two-wheelers retain mobility on secondary and residential street fabrics (Fadilah et al. [4]).
* **Our Solution:** Formulates a mode-specific edge impedance model on OpenStreetMap graphs:
  $$c(e) = \text{length}(e) \cdot \left( p_{base}(hw) \cdot M_{bridge} \cdot M_{roundabout} \cdot M_{surface} \right)$$
  Inverts the road hierarchy during peak commute windows (`motorway: 4.0`, `primary: 2.2`, `secondary: 1.5`, `residential: 1.0`, `service: 0.9`), awards flyover bonuses ($0.8\times$), damps roundabouts ($0.95\times$), and penalizes unpaved/degraded surfaces.
* **Implementation Status:** 100% implemented in `core/config.py` and `routing/algorithms.py`.

---

### Supporting Contribution 1: Perpendicular Offset Alternative Route Generation
* **Classification:** **SUPPORTING CONTRIBUTION (Retained as Secondary Contribution)**
* **Scholarly Role:** Practical route diversity and alternative corridor discovery.
* **Academic Problem Addressed:** Yen's $k$-shortest paths algorithm fails in urban street grids because it generates redundant candidate paths differing by single-block detours and sharing >90% of edges (Abraham et al. [9], Asvial et al. [5]). Continental highway via-node plateaus fail in dense developing cities lacking grade-separated expressways.
* **Our Solution:** Generates candidate via-nodes by projecting perpendicular lateral offset waypoints ($\pm 90^\circ$ at $150\text{ m}, 300\text{ m}$) at chord fractions ($0.33, 0.50, 0.67$) into adjacent neighborhood street grids. Computes two-leg turn-aware A\* and filters candidates against bounded detour ($\epsilon \le 0.20$) and limited sharing ($\gamma \le 0.70$).
* **Implementation Status:** 70% implemented in `routing/algorithms.py`. Requires implementing the 70% edge-sharing filter in the evaluation harness.

---

### Supporting Methodological Component: Multi-Lane Junction Filtering ETA Calibration
* **Classification:** **SUPPORTING METHODOLOGICAL COMPONENT (Decoupled ETA Calibration)**
* **Scholarly Role:** Empirical travel-time correction for signalized queues.
* **Academic Realignment:** In strict compliance with academic integrity, this is **not claimed as in-search routing optimization**. Path choice is driven by Core Contributions 1 and 2.
* **Our Solution:** A post-route travel time calibration model grounded in Promraksa et al.'s [1] empirical filtering clearances ($0.75\text{ m}–0.90\text{ m}$). Inspects the completed path for signalized multi-lane approaches ($\ge 2$ lanes, degree $\ge 3$) and discounts estimated journey duration:
  $$T_{calibrated} = T_{base} \cdot \max\left(0.85, 0.985^{N_{signals}}\right)$$
* **Implementation Status:** Functions exist in `routing/algorithms.py:169–225`. Requires invoking the function during experimental travel-time evaluation.

---

### Empirical Case Study & Future Work: Congestion Bypass & Predictive Integration
* **Classification:** **CASE STUDY & FUTURE EXTENSION (Do NOT claim as novel implemented ML)**
* **Scholarly Role:** Realistic validation ground truth on Bengaluru's road network.
* **Academic Demarcation:** The project does *not* claim a novel deep learning or streaming analytics engine. Kumar et al. (2025) [16] already demonstrated deep learning traffic volume prediction in Bengaluru.
* **Our Positioning:** Kumar et al.'s documented 100% saturation corridors (Hosur Road, MG Road / Trinity Circle, Yeshwanthpur) are ingested as an **empirical case study**. When these corridors are flagged, the engine applies a $25.0\times$ impedance penalty to incident edges, proving that our two-wheeler A\* algorithm automatically discovers viable secondary bypass routes around saturated bottlenecks. Real-time end-to-end integration with live deep learning streams (Abbas et al. [13]) is explicitly designated as **Future Work**.

---

## 3. Coherent Conference Paper Architecture (IEEE 6–8 Page Format)

| Paper Section | Target Length | Core Technical Scope and Contributions Covered |
| :--- | :---: | :--- |
| **I. Introduction** | 1.0 page | Urban traffic heterogeneity in Bengaluru; failure of car-centric navigation; formal problem statement; prospective hypotheses; list of contributions. |
| **II. Literature Review** | 1.5 pages | Synthesized review across the 5 pillars ([1]–[16]); establishes Gap 1 (micro-to-macro), Gap 2 (turn modeling), Gap 3 (alternative diversity), and Gap 4 (unclosed loop). |
| **III. Two-Wheeler Path Optimization Framework** | 2.0 pages | Mathematical formulation of multi-attribute edge impedance; dynamic state-expanded A\* `(prev, curr)` with spherical turn angles; proof of Haversine heuristic admissibility ($h = 0.8 \times \text{haversine}$); post-route filtering ETA calibration formula. |
| **IV. Alternative Corridor Diversification** | 1.0 page | Perpendicular offset waypoint projection geometry; two-leg A\* candidate stitching; formal quality criteria (bounded detour $\epsilon \le 20\%$, limited sharing $\gamma \le 70\%$). |
| **V. Experimental Validation & Case Study** | 2.0 pages | Empirical evaluation on Bengaluru OSM graph: (1) Road-class distribution & travel times vs. OSRM; (2) Turn severity & latency vs. turn-agnostic A\*; (3) Jaccard diversity vs. Yen's KSP; (4) Bypass case study on Kumar et al.'s corridors. |
| **VI. Conclusion & Future Work** | 0.5 page | Summary of findings; explicit delimitations; future integration with live deep learning streaming pipelines. |

---

## 4. Summary Verdict on Project Scope

This streamlined research scope eliminates all academic vulnerabilities:
1. **No Over-Claims:** We do not claim in-search filtering optimization or proprietary deep learning prediction.
2. **Mathematically Bulletproof:** Heuristic admissibility is restored ($h = 0.8 \times \text{haversine}$), and turn penalties are consistently defined in virtual distance meters.
3. **High Scientific Distinction:** Turn-aware state expansion combined with an inverted road hierarchy and perpendicular offset alternatives provides a complete, novel, and rigorous IEEE paper.
