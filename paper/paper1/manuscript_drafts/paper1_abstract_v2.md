# Paper 1 Abstract (v2.0 Validated Draft)

**Document:** [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`)  
**Length:** Exactly 208 Words (Standard IEEE Abstract Target: 180–220 words)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **PHASE 5.2 APPROVED REVISION**

---

## IEEE Conference Abstract

Conventional shortest-path routing on vertex-based road graphs does not inherently account for arrival heading when evaluating successive road segments. This limits its ability to represent turn-dependent routing costs and vehicle-specific road impedance within a unified search formulation. This paper presents a two-wheeler-oriented routing approach that combines state-expanded $A^*$ search with road-class impedance modelling. The search represents states as directed edge states $s=(u,v)$ and incorporates discrete angular penalties during edge relaxation. Road segments are assigned class-dependent impedance weights, with a $0.80$ override for qualifying grade-separated main-road segments. When composite edge multipliers satisfy $\mu(e) \ge 0.80$ and turn penalties are nonnegative, we establish the admissibility and consistency of a Haversine heuristic scaled by $0.80$. The approach is evaluated on 25 origin–destination corridors using a Bengaluru road network containing 744,216 directed edges. Compared with turn-unaware state-expanded routing (A1), the turn-aware configuration (A0) reduces the mean number of sharp turns ($\ge 60^\circ$) by $34.1\%$ ($32.52$ to $21.44$ turns; Holm-adjusted $p=4.5\times 10^{-5}$). Relative to neutral road-class impedance (B1), the production impedance configuration (B0) reduces arterial exposure by $51.21$ percentage points ($65.05\%$ to $13.84\%$), with a $15.53\%$ increase in mean physical route distance ($7.65$ vs. $6.62\text{ km}$). These results demonstrate the measurable effects of incorporating heading-dependent turn costs and road-class impedance into urban two-wheeler routing.

---

## Word Count Analysis

- **Total Word Count:** 208 words (excluding section headings and metadata).
- **Target Range:** 180–220 words.
- **Budget Compliance:** Fully compliant (falls cleanly inside the target window).

---

## Index Terms

Two-wheeler routing, state-expanded search, turn penalties, shortest path algorithms, road impedance modeling, heuristic admissibility, urban transportation networks.

---

*Abstract v2.0 validated and updated per research lead directives under read-only audit protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
