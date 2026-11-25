# Individual Paper Analysis: Paper [10]

**Analysis Level:** Full-Text Analysed (Archived Local PDF: `10_Bast_2016_Route_Planning_Survey.pdf`)  
**Citation Key:** `bast2016route`  
**Target Pillar:** Pillar 3 – Algorithmic Path Optimization & Routing Engines  

---

### A. Bibliographic Information
* **Title:** Route Planning in Transportation Networks
* **Authors:** Hannah Bast, Daniel Delling, Andrew Goldberg, Matthias Müller-Hannemann, Thomas Pajor, Peter Sanders, Dorothea Wagner, and Renato F. Werneck
* **Publication Year:** 2016 (Survey comprehensive through 2015)
* **Book Chapter / Journal:** *Algorithm Engineering: Selected Results and Surveys*, published in *Lecture Notes in Computer Science (LNCS)*, Volume 9220, pages 19–80 (65 pages)
* **Publisher:** Springer International Publishing
* **DOI:** [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2)

---

### B. Research Problem
* **Core Problem:** Point-to-point shortest path queries on massive transportation graphs are computationally challenging under realistic constraints: continent-sized networks contain tens of millions of vertices, queries must return in milliseconds, edge metrics change dynamically with traffic, and users demand multi-criteria optimization (cost, distance, travel time, transfer penalties).
* **Importance:** This comprehensive survey provides the authoritative benchmark taxonomy and theoretical foundations for modern navigation engines, synthesizing over two decades of algorithm engineering breakthroughs.
* **Motivation:** Present a unified algorithmic framework comparing classic graph search (Dijkstra, A\*), goal-directed speedups (ALT, Arc Flags), hierarchical techniques (Contraction Hierarchies, Hub Labeling), customizable route planning (CRP), and multi-criteria Pareto optimization.

---

### C. Existing Research / Background
* **Foundational Baseline (Section 2, pp. 3–5):**
  - *Dijkstra’s Algorithm (Dijkstra, 1959):* Settles vertices in non-decreasing order of distance from source $s$. Complexity $O(|A| + |V| \log |V|)$ using Fibonacci heaps, or $O((|A| + |V|) \log |V|)$ using standard binary 4-heaps. Visits entire circular frontiers indiscriminately.
  - *Bidirectional Search:* Executes forward search from $s$ and backward search from $t$, reducing visited area roughly by half.
* **Identified Challenges:**
  - Classic Dijkstra is too slow for interactive web queries on large metropolitan graphs (~1–5 seconds per query).
  - Advanced speed-up techniques achieve up to 6 orders of magnitude faster queries (down to nanoseconds with Hub Labeling), but trade off metric flexibility and dynamic traffic updates.

---

### D. Methodology
* **A\* Search and Heuristic Admissibility (Section 2.2, pp. 6–7):**
  - Directs search toward target $t$ by priority key $k(u) = d(s, u) + \pi(u)$, where $\pi(u)$ estimates remaining distance to $t$.
  - **Admissibility Condition:** $\pi(u) \le \text{dist}(u, t)$ for all $u \in V$. A heuristic is admissible if it never overestimates the true remaining cost.
  - **Consistency (Monotonicity) Condition:** $\pi(u) \le \ell(u, v) + \pi(v)$ for every arc $(u, v) \in A$. If $\pi$ is consistent, reduced edge costs $\ell_\pi(u, v) = \ell(u, v) - \pi(u) + \pi(v) \ge 0$, ensuring label-setting correctness (each vertex settled at most once).
  - *Euclidean / Great-Circle Potential:* $\pi(u) = \text{haversine}(u, t) / v_{max}$, where $v_{max}$ is the maximum possible traversal speed across the network.
* **Taxonomy of Speed-up Techniques (Sections 2.3–2.6, pp. 8–35):**
  - *Hierarchical Techniques:* Contraction Hierarchies (iteratively contracting vertices and inserting shortcuts), Highway Node Routing.
  - *Goal-Directed Techniques:* ALT (A\*, Landmarks, and Triangle inequality), Arc Flags.
  - *Customizable Techniques (CRP):* Decoupling topology from cost metrics via multi-level cell partitioning.
  - *Multi-Criteria Pareto Search (Section 4, pp. 43–48):* Finding non-dominated vectors $(c_1(P), c_2(P), \dots, c_k(P))$ using generalized multi-label Dijkstra.

---

### E. Results and Findings
* **Algorithmic Trade-off Spectrum (Section 2.7, pp. 35–42):**
  - *Pure Dijkstra:* 0 s preprocessing, ~1.5 s query time on continental road graphs (~20M nodes).
  - *A\* with Euclidean Bound:* 0 s preprocessing, ~300–500 ms query time (3×–5× speedup over Dijkstra).
  - *ALT:* 1–2 minutes preprocessing, ~10–50 ms query time.
  - *Contraction Hierarchies (CH):* ~5 minutes preprocessing, ~0.1–0.5 ms query time, but rigid metric.
  - *Customizable Route Planning (CRP):* ~10 minutes metric-independent partition, <1 s metric customization, ~1–2 ms query time.
* **Author Conclusion:** No single algorithm dominates in every scenario; the choice of algorithm must balance preprocessing time, update frequency, memory overhead, and metric customizability.

---

### F. Limitations
* **Author-Stated Limitations (Sections 2.7 & 5, pp. 40, 58):**
  1. Multi-criteria Pareto optimization is NP-hard in general; the number of non-dominated paths can grow exponentially with graph size.
  2. Many ultra-fast techniques (e.g., Hub Labeling, Transit Node Routing) consume gigabytes of auxiliary memory, rendering them unsuitable for lightweight or mobile embedded deployments.
* **Critical Reading / Additional Limitations:**
  1. The survey primarily treats road routing from the standpoint of homogeneous automobile networks with well-defined speed limits; it does not model non-lane-based traffic, motorcycle filtering, or informal road conditions.

---

### G. Relevance to My Project
* **Theoretical Foundation for A\*:** **Directly relevant.** Provides the mathematical proof justifying our use of the Haversine distance heuristic in `routing/algorithms.py`. By dividing spatial distance by maximum edge speed, our potential function satisfies admissibility ($\pi(u) \le \text{dist}(u, t)$) and consistency, guaranteeing optimal paths.
* **Turn-Penalty Non-Negativity:** Reinforces that turn penalties added to search costs must remain strictly non-negative ($\ge 0$) to preserve reduced-cost monotonicity in priority queue relaxation.
* **Algorithmic Architecture Justification:** Justifies our engineering decision to deploy state-expanded A\* over static Contraction Hierarchies: since our project requires dynamic, user-tunable two-wheeler cost profiles, an admissible A\* search avoids the multi-minute re-contraction penalties of CH while achieving responsive query times on Bengaluru's road network.

---

### H. Research Contribution
* Serves as the definitive reference for shortest-path algorithm engineering, rigorously formalizing A\* heuristic admissibility, priority queue mechanics, and the performance trade-offs between static speed-up hierarchies and dynamic multi-criteria routing.

---

### I. Potential Application
* **Existing Project Architecture:** Validates the correctness and mathematical admissibility of `astar_two_wheeler()` in `routing/algorithms.py`.
* **Feasibility Evaluation:** High feasibility. Forms the theoretical benchmark against which our algorithm execution times, queue expansions, and path costs are evaluated.
