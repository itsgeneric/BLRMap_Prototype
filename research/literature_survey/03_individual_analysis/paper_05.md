# Individual Paper Analysis: Paper [5]

**Analysis Level:** Full-Text Analysed (Archived Local PDF: `05_Asvial_2020_Entropy_Motorcycle_Routing.pdf`)  
**Citation Key:** `asvial2020entropy`  
**Target Pillar:** Pillar 1 – Two-Wheeler Dynamics & Route Choice  

---

### A. Bibliographic Information
* **Title:** Entropy-Based k Shortest-Path Routing for Motorcycles: A Simulated Case Study in Jakarta
* **Authors:** Muhamad Asvial, M. Faridz Gita Pandoyo, and Ajib Setyo Arifin
* **Publication Year:** 2020
* **Journal:** *International Journal of Advanced Computer Science and Applications (IJACSA)*, Volume 11, Number 7, pages 438–445 (8 pages)
* **Publisher:** The Science and Information (SAI) Organization
* **DOI:** [10.14569/IJACSA.2020.0110758](https://doi.org/10.14569/IJACSA.2020.0110758)

---

### B. Research Problem
* **Core Problem:** Commercial turn-by-turn navigation apps channel all motorized two-wheelers onto identical "optimal" paths, compounding arterial bottleneck congestion. Furthermore, standard navigation applications often fail to integrate narrow local streets effectively for motorcycle flow.
* **Importance:** In Southeast Asian megacities like Jakarta, motorcycles represent the majority of private vehicles. Route concentration on major roads causes severe systemic gridlock.
* **Motivation:** Develop an open-source motorcycle-specific routing system utilizing OpenStreetMap and an Entropy-Balanced $k$ Shortest Paths (EBkSP) algorithm to disperse two-wheeler traffic across viable alternative roads.

---

### C. Existing Research / Background
* **Previous Approaches:** Standard single shortest-path routing (Dijkstra/A*), random $k$-shortest path selection, and dynamic traffic assignment (DTA) through VANETs.
* **Identified Limitations (Section II, p. 2):** Standard $k$-shortest path algorithms return routes with high mutual overlap or unguided randomness. Commercial motorcycle modes (e.g., Google Maps) often exhibit a strict bias toward wide roads or avoid narrow alleyways even when narrow roads offer shorter, uncongested trajectories.

---

### D. Methodology
* **Software Architecture (Section III, pp. 2–4):** Built on open-source GIS software: OpenStreetMap (OSM) spatial network data ingested via GeoServer and OpenLayers, with a custom backend routing engine written in Java/Python.
* **Algorithm (Algorithm 1, p. 3):**
  1. *Candidate Generation:* Calculates $k$ shortest paths between origin $(x_1, y_1)$ and destination $(x_2, y_2)$.
  2. *Entropy Balancing:* Computes information entropy across route candidates based on vehicle footprint density and road capacity, distributing traffic proportionally to minimize link oversaturation.
* **Experimental Setup (Section IV, p. 5):** Evaluated across 6 real-world Origin-Destination (OD) pairs in South Jakarta/Depok centered on Universitas Indonesia (UI to Cinere, Lebak Bulus, Pasar Minggu, Ragunan, Kebagusan, and Jagakarsa) with trip lengths ranging from 4 km to 14 km.

---

### E. Results and Findings
* **Quantitative Trip Savings (Section V & VI, pp. 6–7):** For urban trips under 10 km where narrow streets offer viable bypasses, EBkSP achieved up to **8% faster travel times** than Google Maps' motorcycle mode.
* **Distance Horizon Threshold (Section V, p. 6):** For longer trips (>10 km, such as UI to Lebak Bulus), the advantage diminished because Google Maps reverted to wider arterial roads while OSM narrow-street routing accumulated minor intersection delays.
* **Computational Overhead (Section V, p. 7):** Evaluating narrow residential streets increases graph search space, but EBkSP maintained sub-second server response times suitable for real-time mobile client querying.
* **Author Conclusion (p. 7):** Dispersing motorcycles across secondary and residential road networks via entropy balancing reduces individual trip times and prevents localized secondary bottlenecks.

---

### F. Limitations
* **Author-Stated Limitations (p. 3, 7):**
  1. Traffic footprint data was synthetically generated/manually simulated rather than ingested from live GPS probe streams.
  2. Tested only on 6 OD pairs in a localized sector of Jakarta/Depok.
* **Critical Reading / Additional Limitations:**
  1. Does not implement explicit turn penalties or turn angle calculations; cost is primarily length- and capacity-weighted.
  2. Relies on static OpenStreetMap geometries without real-time travel duration calibration from commercial APIs.

---

### G. Relevance to My Project
* **Two-Wheeler-Aware Routing:** **Directly relevant.** Directly addresses motorcycle navigation in a congested Asian megacity facing traffic dynamics identical to Bengaluru.
* **OpenStreetMap Integration:** Uses OpenStreetMap as the core topological graph, matching our architecture (`bengaluru_roads_full.graphml`).
* **Alternative Route Generation & Diversity:** Validates our generation of split candidates and perpendicular offset routes to avoid funnelling all trips into a single road corridor.
* **Bengaluru Urban Road Conditions:** Supports our inner-road preference mode, confirming that local secondary roads offer up to 8% travel time savings for trips under 10 km.

---

### H. Research Contribution
* Establishes that open-source OpenStreetMap motorcycle routing can match or outperform commercial engines (Google Maps) on trips under 10 km by exploiting narrow streets and balancing traffic entropy across alternative paths.

---

### I. Potential Application
* **Existing Project Influence:** Strongly supports our split candidate generation and deduplication in `api_server.py`.
* **Feasibility Evaluation:** High feasibility. While our engine uses A* with turn penalties rather than entropy calculations, the concept of candidate route diversity on secondary roads is fully integrated.
