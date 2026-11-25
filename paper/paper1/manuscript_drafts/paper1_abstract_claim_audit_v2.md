# Paper 1 Abstract Claim Audit and Evidentiary Traceability (v2.0)

**Document:** [`paper1_abstract_claim_audit_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_claim_audit_v2.md)  
**Target Abstract:** [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **PHASE 5.2 COMPLETE AUDIT (POST-REVISION)**

---

## 1. Claim-by-Claim Verification Table

| # | Abstract Statement / Claim | Evidence Source / Implementation Location | Verified Values / Details | Audit Status |
| :-: | :--- | :--- | :--- | :-: |
| **C1** | *"Conventional shortest-path routing on vertex-based road graphs does not inherently account for arrival heading when evaluating successive road segments."* | `winter2002modeling` (DOI: [10.1080/13658810210148715](https://doi.org/10.1080/13658810210148715))<br/>`luxen2011realtime` (DOI: [10.1145/2093973.2094062](https://doi.org/10.1145/2093973.2094062)) | In simple vertex graphs $G=(V,E)$, cost functions $c(u,v)$ depend only on the edge, violating subpath optimality if turn costs depend on the incoming edge $(u,v)$ and outgoing edge $(v,w)$. | **VERIFIED** |
| **C2** | *"This limits its ability to represent turn-dependent routing costs and vehicle-specific road impedance within a unified search formulation."* | `winter2002modeling`<br/>`fadilah2024identifying` (DOI: [10.1016/j.trip.2024.101147](https://doi.org/10.1016/j.trip.2024.101147)) | Standard routing engines optimize scalar car travel times, failing to incorporate directional heading penalties and motorcycle road impedance. Replaces "preferences" with formal "impedance". | **VERIFIED** |
| **C3** | *"This paper presents a two-wheeler-oriented routing approach that combines state-expanded $A^*$ search with road-class impedance modelling."* | [`routing/algorithms.py#L460-L705`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L460-L705) | Function `two_wheeler_astar` couples heading-expanded search with road-type penalty lookup. | **VERIFIED** |
| **C4** | *"The search represents states as directed edge states $s=(u,v)$ and incorporates discrete angular penalties during edge relaxation."* | [`routing/algorithms.py#L520-L525`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L520-L525)<br/>[`routing/algorithms.py#L658-L677`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L658-L677) | In source, `state = (previous_node, current_node)` represents incoming edge $(u,v) \in E$. Turn cost `_turn_penalty(graph, previous_node, current_node, next_node)` is added during relaxation. | **VERIFIED** |
| **C5** | *"Road segments are assigned class-dependent impedance weights, with a $0.80$ override for qualifying grade-separated main-road segments."* | [`core/config.py#L61-L77`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py#L61-L77)<br/>[`routing/algorithms.py#L309-L311`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L311) | `TWO_WHEELER_ROAD_PENALTIES` assigns multipliers $0.90\text{--}4.0$. Arterial bridges (`MAIN_ROAD_TYPES` on bridge) override base penalties to `0.80`. Matches code logic exactly. | **VERIFIED** |
| **C6** | *"When composite edge multipliers satisfy $\mu(e) \ge 0.80$ and turn penalties are nonnegative, we establish the admissibility and consistency of a Haversine heuristic scaled by $0.80$."* | [`phase_3_3_corrected_mathematical_claims.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_3_corrected_mathematical_claims.md)<br/>[`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) | Formal Theorems 1 & 2 prove $h(s) = 0.80 \cdot d_H(v, t)$ is admissible and monotonically consistent iff $\min_e \mu(e) \ge 0.80$ and $P_{\text{turn}} \ge 0$. Graph inspection confirms $\min \mu(e) = 0.8000$ across all 744,216 edges. Both conditions explicitly stated. | **VERIFIED** |
| **C7** | *"The approach is evaluated on 25 origin–destination corridors using a Bengaluru road network containing 744,216 directed edges."* | [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)<br/>[`stage_2b_full_ablation_results.json`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/stage_2b_full_ablation_results.json) | $G$ is a `MultiDiGraph` with $|V| = 308,643$ nodes and $|E| = 744,216$ directed edges (`G.is_directed() == True`). Benchmark corpus contains exactly 25 validated OD pairs. | **VERIFIED** |
| **C8** | *"Compared with turn-unaware state-expanded routing (A1), the turn-aware configuration (A0) reduces the mean number of sharp turns ($\ge 60^\circ$) by $34.1\%$ ($32.52$ to $21.44$ turns; Holm-adjusted $p=4.5\times 10^{-5}$)."* | [`statistical_test_results.csv#Row-2`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L2)<br/>[`exp_a_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_a_corridor_metrics.csv) | Condition A1 mean $= 32.52$, Condition A0 mean $= 21.44$. Mean difference $= -11.08$ turns ($-34.0713\% \approx -34.1\%$). Pratt Wilcoxon $W = 0.0$, raw $p = 1.5\times 10^{-5}$, Holm $p_{\text{adj}} = 4.5\times 10^{-5}$, Cohen's $d_z = -1.0066$. | **VERIFIED** |
| **C9** | *"Relative to neutral road-class impedance (B1), the production impedance configuration (B0) reduces arterial exposure by $51.21$ percentage points ($65.05\%$ to $13.84\%$), with a $15.53\%$ increase in mean physical route distance ($7.65$ vs. $6.62\text{ km}$)."* | [`statistical_test_results.csv#Row-11,Row-17`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/statistical_test_results.csv#L11)<br/>[`exp_b_corridor_metrics.csv`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/exp_b_corridor_metrics.csv) | Arterial share: B1 mean $= 65.0524\%$, B0 mean $= 13.8376\%$, $\Delta = -51.2148\text{ pp}$ ($p_{\text{adj}} = 8.4\times 10^{-5}$). Route distance: B1 mean $= 6.6196\text{ km}$, B0 mean $= 7.6475\text{ km}$, $\Delta = +1.02788\text{ km}$ ($+15.5287\% \approx +15.53\%$, $p_{\text{adj}} = 6.8\times 10^{-5}$). | **VERIFIED** |
| **C10** | *"These results demonstrate the measurable effects of incorporating heading-dependent turn costs and road-class impedance into urban two-wheeler routing."* | Experiments A & B data synthesis. | Factual summary characterizing measurable geometric and topological route changes without claiming safety or travel-time benefits. | **VERIFIED** |

---

## 2. In-Depth Technical Verification Details

### 2.1. Verification of the 15.53% Route-Distance Comparison
- **Question:** Is the $+15.53\%$ physical distance increase specifically Condition B0 versus Condition B1?
- **Ground-Truth Data:**
  - `B0_Production_2W`: Mean distance $= 7.64748\text{ km}$ (Median $= 7.784\text{ km}$, $\text{SD} = 3.655\text{ km}$).
  - `B1_Neutral_Road_Class`: Mean distance $= 6.61960\text{ km}$ (Median $= 6.403\text{ km}$, $\text{SD} = 3.407\text{ km}$).
  - `B2_Physical_Distance_Ref`: Mean distance $= 6.57736\text{ km}$ (Median $= 6.403\text{ km}$, $\text{SD} = 3.447\text{ km}$).
- **Calculations:**
  - $\Delta(\text{B0} - \text{B1}) = 7.64748 - 6.61960 = +1.02788\text{ km}$.
  - Percentage relative to B1: $\frac{+1.02788}{6.61960} = +0.155287 \to \mathbf{+15.53\%}$.
  - Percentage relative to B2: $\frac{7.64748 - 6.57736}{6.57736} = \frac{+1.07012}{6.57736} = +0.162697 \to \mathbf{+16.27\%}$.
- **Resolution:** The $+15.53\%$ figure is **strictly and exclusively** relative to Condition B1 (neutral road-class impedance). The revised abstract explicitly states the comparison relative to Condition B1, including explicit physical distances ($7.65$ vs. $6.62\text{ km}$).

### 2.2. State Representation Precision
- In [`routing/algorithms.py#L520-L525`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L520-L525), `state = (previous_node, current_node)` is an ordered pair of vertices $(u, v) \in V \times V$ representing incoming directed edge $(u, v) \in E$.
- Transition $s \to s'$ corresponds to edge pair $((u, v), (v, w))$ through intersection $v$.
- Describing $s=(u,v)$ as "directed edge states $s=(u,v)$" is mathematically rigorous.

### 2.3. Road Impedance and Flyover Modifier Alignment
- **Replacement 1 Applied:** Replaced "vehicle-specific road preferences" with "vehicle-specific road impedance". Completely avoids behavioural/psychological overclaiming.
- **Replacement 2 Applied:** Replaced "with an additional modifier for grade-separated flyovers" with "with a 0.80 override for qualifying grade-separated main-road segments". Matches [`routing/algorithms.py#L309-L311`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L311) where `penalty = 0.8` is assigned exclusively if `is_bridge` is active and `hw in MAIN_ROAD_TYPES`.
- **Replacement 3 Applied:** Replaced premise with "When composite edge multipliers satisfy $\mu(e) \ge 0.80$ and turn penalties are nonnegative, we establish...". Explicitly includes the non-negativity constraint ($P_{\text{turn}} \ge 0$), making the premise mathematically complete.

---

## 3. Literature Traceability Matrix

| Citation Key | Formal Reference | Claim Supported in Abstract | Verification Assessment |
| :--- | :--- | :--- | :--- |
| `winter2002modeling` | S. Winter, "Modeling costs of turns in route planning," *Int. J. Geogr. Inf. Sci.*, vol. 16, no. 5, pp. 403–412, 2002. | Point-vertex road graphs cannot evaluate turn costs without violating subpath optimality; requires state expansion or line graphs. | **Fully Supported:** Direct mathematical proof in Winter (2002). |
| `luxen2011realtime` | D. Luxen and C. Vetter, "Real-time routing with OpenStreetMap data," *ACM SIGSPATIAL*, pp. 513–516, 2011. | Conventional point-based contraction hierarchies prioritize automobile hierarchies and do not natively evaluate heading. | **Fully Supported:** Architectural description of node contraction in OSRM. |
| `fadilah2024identifying` | Fadilah et al., "Identifying motorcycle routes using GPS data: A case study in Surabaya, Indonesia," *Transp. Res. Interdiscip. Perspect.*, vol. 25, 2024. | Two-wheeler route choice behavior deviates from passenger car hierarchy; riders seek lower-stress local roads. | **Fully Supported:** Empirical GPS trajectory findings in mixed traffic. |
| `hart1968formal` | Hart, Nilsson, & Raphael, "A formal basis for the heuristic determination of minimum cost paths," *IEEE Trans. Syst. Sci. Cybern.*, 1968. | Admissible and consistent heuristics guarantee optimal path finality without state reopening. | **Fully Supported:** Foundational theorems of A* search. |
