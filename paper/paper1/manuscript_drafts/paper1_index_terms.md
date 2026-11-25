# Paper 1 IEEE Index Terms Specification

**Document:** [`paper1_index_terms.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_index_terms.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE INDEX TERMS SPECIFICATION**

---

## 1. Selected IEEE Index Terms (7 Terms)

In accordance with the IEEE Computer Society and IEEE Intelligent Transportation Systems Society indexing taxonomies, the following **7 controlled index terms** are established for Paper 1:

```
Index Terms—Two-wheeler routing, state-expanded search, turn penalties, shortest path algorithms, road impedance modeling, heuristic admissibility, urban transportation networks.
```

---

## 2. Taxonomy Justification and Search Discovery Mapping

| # | Index Term | Primary IEEE Taxonomy Domain | Justification for Paper 1 | Search Discovery Value |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Two-wheeler routing** | Intelligent Transportation Systems $\to$ Vehicular Routing $\to$ Vehicle-Specific Navigation | Identifies the primary transportation domain: motorcycle and powered two-wheeler navigation in mixed urban traffic. | Maximizes discovery for researchers studying two-wheeler travel behavior and vehicle-specific routing. |
| **2** | **State-expanded search** | Computer Science $\to$ Artificial Intelligence $\to$ Heuristic Search $\to$ State Space Search | Represents the core algorithmic architecture: expanding search from physical vertices $V$ to directed edge transitions $S = E \cup \{(\text{None}, s_0)\}$. | Targets researchers in search algorithms, dual graphs, and non-Markovian path planning. |
| **3** | **Turn penalties** | Transportation Engineering $\to$ Traffic Assignment $\to$ Intersection Delays | Captures the physical cost model: penalizing discrete angular vehicular deflections ($\ge 60^\circ$ and $30^\circ\text{--}60^\circ$). | Connects with traffic engineering literature on intersection conflicts, maneuver minimization, and line-graph modeling. |
| **4** | **Shortest path algorithms** | Graph Theory & Algorithms $\to$ Network Optimization $\to$ Shortest Path | Positions the algorithm within the broader mathematical class of Dijkstra, A*, and point-to-point network search engines. | Ensures indexation under fundamental algorithmic and graph optimization taxonomies. |
| **5** | **Road impedance modeling** | Transportation Planning $\to$ Network Cost Functions $\to$ Road Hierarchies | Defines the edge-weighting methodology: inverted road-class penalties, grade-separated flyover overrides, and roundabout factors. | Targets work on multi-attribute link cost functions and urban road hierarchy calibration. |
| **6** | **Heuristic admissibility** | Artificial Intelligence $\to$ Search Algorithms $\to$ Heuristic Correctness | Identifies the theoretical contribution: formal proofs of admissibility ($h \le c^*$) and monotonic consistency ($h \le c + h'$) under road impedance scaling. | Discovered by theoreticians and practitioners verifying heuristic optimality guarantees in spatial A* variants. |
| **7** | **Urban transportation networks** | Civil & Transportation Systems $\to$ Urban Infrastructure $\to$ Road Networks | Grounding in real-world metropolitan infrastructure (large-scale spatial networks, OpenStreetMap topologies). | Connects with GIS, spatial network analysis, and urban mobility benchmarks. |

---

## 3. Strict Boundary Compliance Check

- **Exclusion of Paper 2 Terms:** Terms such as *Alternative route generation*, *Route diversity*, *Yen's algorithm*, and *Commute network validation* are **strictly excluded** from Paper 1 and reserved for Paper 2.
- **Exclusion of Prohibited Claims:** Terms such as *Accident prediction*, *Traffic safety*, *Crash reduction*, and *Dynamic congestion forecasting* are **strictly excluded** to uphold construct validity boundaries.

---

*Index terms finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
