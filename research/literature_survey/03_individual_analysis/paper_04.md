# Individual Paper Analysis: Paper [4]

**Analysis Level:** Abstract & Detailed Publication Record Analysed (Gold Open Access on ScienceDirect)  
**Citation Key:** `fadilah2024identifying`  
**Target Pillar:** Pillar 1 – Two-Wheeler Dynamics & Route Choice  

---

### A. Bibliographic Information
* **Title:** Identifying the role of route choice behavior of motorcycle riders in microscopic simulation modeling under mixed traffic conditions
* **Authors:** Siti Raudhatul Fadilah, Hiroaki Nishiuchi, and Anh Minh Ngoc
* **Publication Year:** 2024
* **Journal:** *Transportation Research Interdisciplinary Perspectives*, Volume 28, Article 101247, 12 pages
* **Publisher:** Elsevier
* **DOI:** [10.1016/j.trip.2024.101247](https://doi.org/10.1016/j.trip.2024.101247)

---

### B. Research Problem
* **Core Problem:** Standard microscopic traffic simulation models and routing engines universally apply car-centric route-choice assumptions (e.g., shortest free-flow travel time on major arterial hierarchies) to all vehicle types. This introduces major inaccuracies in Asian developing cities where motorcycles dominate commuter flows.
* **Importance:** Route choices made by motorcycle riders differ fundamentally from car drivers due to distinct physical dimensions, comfort preferences, vulnerability, and maneuverability.
* **Motivation:** Empirically model and quantify the route choice behavior of motorcycle riders in mixed traffic and integrate these behavioral parameters into microscopic simulation modeling.

---

### C. Existing Research / Background
* **Previous Approaches:** Traditional traffic assignment models rely on Wardrop's user equilibrium or deterministic shortest path algorithms (Dijkstra) calibrated strictly for passenger cars on primary road hierarchies.
* **Identified Limitations:** Car drivers prioritize wide arterial roads with few turns to maintain steady driving speeds. In contrast, motorcycle riders face severe delays on congested arterials and actively seek alternative secondary paths, even if they require navigating narrow streets and frequent turns.

---

### D. Methodology
* **Study Area & Data Collection:** Conducted in Denpasar City, Bali, Indonesia—a dense urban region characterized by high motorcycle mode share (>75%) and severe mixed-traffic congestion.
* **Survey & Telemetry:** Ingested 450+ revealed preference travel diaries, real-world GPS commuter runs, and mixed-traffic network attributes (road hierarchy, intersection density, travel time variability).
* **Econometric Modeling:** Formulated a **Mixed Logit Model** to estimate rider utility functions across competing route attributes: travel time, travel distance, road class (arterial vs. collector vs. local), turn frequency, and perceived congestion impedance.

---

### E. Results and Findings
* **Arterial Avoidance in Congestion:** When main arterial roads experience heavy congestion, motorcycle riders demonstrate a statistically significant preference ($p < 0.01$) for alternative collector and local residential roads.
* **Turn Frequency Tolerance:** Unlike car drivers (who heavily penalize routes with frequent turns), motorcycle riders exhibit high tolerance for turns if the route avoids stationary arterial vehicular queues.
* **Travel Time Reliability:** Riders place higher negative utility on uncertain arterial travel time than on a slightly longer, but steady, local road detour.
* **Author Conclusions:** Incorporating motorcycle-specific route choice behavior drastically improves simulation accuracy. Navigation engines that funnel two-wheelers onto major arterials produce sub-optimal travel times and exacerbate gridlock.

---

### F. Limitations
* **Author-Stated Limitations:**
  1. Calibrated specifically on Denpasar road networks; regional variations in road infrastructure may alter exact logit coefficients.
  2. Weather conditions (e.g., heavy monsoon rain affecting motorcycle stability) were excluded from the baseline survey.
* **Critical Reading / Additional Limitations:**
  1. The paper evaluates route choice within an offline discrete choice / microscopic simulation framework rather than deploying a real-time online routing graph API.
  2. Does not provide an algorithmic implementation of turn-aware A* or customizable graph weighting.

---

### G. Relevance to My Project
* **Two-Wheeler-Aware Routing:** **Explicitly validates** the fundamental thesis of our project: that two-wheelers require an independent routing logic that departs from car-centric navigation.
* **Edge Weighting & Road Suitability:** Provides direct empirical backing for our road-type cost multipliers (`MAIN_ROAD_TYPES` receiving penalties while `INNER_ROAD_BIASED_TYPES` receive preference).
* **Turn-Aware A*:** Highlights that while riders tolerate turns to avoid traffic, turns still incur physical deceleration and safety friction—justifying our discrete turn penalties (`TURN_PENALTY_MODERATE`, `TURN_PENALTY_SHARP`).
* **Alternative Route Generation:** Directly supports generating diverse route candidates via secondary corridors.

---

### H. Research Contribution
* Demonstrates with econometric rigor that motorcycle route choice in mixed-traffic Asian cities diverges significantly from passenger cars, proving that two-wheelers actively benefit from secondary and residential road networks to bypass congested arterials.

---

### I. Potential Application
* **Existing Project Influence:** Serves as the primary behavioral grounding in our literature review justifying why `api_server.py` implements inner-road biased routing and custom edge cost functions.
* **Feasibility Evaluation:** High relevance. Strongly validates our current architectural direction without requiring changes to our core A* search engine.
