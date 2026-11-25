# Paper 1 Abstract (v1.0 Frozen Draft)

**Document:** [`paper1_abstract_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Length:** Exactly 213 Words (Standard IEEE Abstract Target: 180–220 words)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **AUTHORITATIVE DRAFT**

---

## IEEE Conference Abstract

In dense urban road networks with mixed vehicular traffic, powered two-wheelers represent a dominant mode of passenger transport. Conventional shortest-path navigation engines evaluate road intersections as dimensionless scalar points, ignoring vehicular heading changes during search and routing two-wheelers onto congested, high-speed arterial corridors. We present a turn-aware routing framework that couples state-expanded $A^*$ search with vehicle-specific road impedance modeling. The search operates over directed edge states $s = (u, v)$, evaluating discrete angular heading penalties during edge relaxation. Road segments are weighted using an inverted suitability hierarchy that disincentivizes multi-lane arterials, prioritizes secondary and residential streets, and incorporates grade-separated flyover overrides. Under the condition that composite edge multipliers satisfy $\mu(e) \ge 0.80$, we prove that the Haversine distance heuristic scaled by $0.80$ is admissible and monotonically consistent on the state-expanded graph, guaranteeing optimal path finality without state reopening. Evaluated across 25 metropolitan corridors on Bengaluru's 744,216-edge road network, turn-aware routing (Condition A0) eliminates $34.1\%$ of sharp maneuvers ($\ge 60^\circ$) relative to turn-unaware state-expanded routing (Condition A1: $21.44$ vs. $32.52$ turns, $p_{\text{adj}} = 4.5 \times 10^{-5}$). Concurrently, road impedance weighting reduces arterial exposure by $51.21$ percentage points ($13.84\%$ vs. $65.05\%$, $p_{\text{adj}} = 8.4 \times 10^{-5}$) at a $+15.53\%$ physical route-distance trade-off. This yields a computationally lightweight, mathematically grounded routing architecture tailored to urban two-wheeler navigation.

---

## Index Terms

Two-wheeler routing, state-expanded search, turn penalties, shortest path algorithms, road impedance modeling, heuristic admissibility, urban transportation networks.

---

*Abstract drafted and verified under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
