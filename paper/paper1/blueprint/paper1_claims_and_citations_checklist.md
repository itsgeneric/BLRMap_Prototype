# Paper 1 Claims and Citations Checklist

**Document:** [`paper1_claims_and_citations_checklist.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_claims_and_citations_checklist.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE TRACEABILITY CHECKLIST**

---

## 1. Part A: External Literature Claims (Requires Audited Citation)

Every theoretical, behavioral, or architectural assertion regarding prior work must be anchored directly to one of the 16 audited citations in [`research/paper1_literature/paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib).

| Item # | Manuscript Claim | Required Citation Key | Author, Venue, Year & DOI | Supporting Passages / Concept in Source |
| :---: | :--- | :--- | :--- | :--- |
| **L-01** | Two-wheelers exhibit unique lane-filtering and gap-acceptance behaviors in congested Asian cities. | `promraksa2022lane` | Promraksa & Satiennam, *J. Safety Research*, 2022<br/>DOI: [10.1016/j.jsr.2022.08.017](https://doi.org/10.1016/j.jsr.2022.08.017) | Documents two-wheeler filtering dynamics between stationary/slow vehicular queues at urban intersections. |
| **L-02** | Mixed traffic on Indian arterials involves severe speed heterogeneity and frequent overtaking conflicts. | `kotagi2020modeling` | Kotagi et al., *Physica A*, 2020<br/>DOI: [10.1016/j.physa.2020.124847](https://doi.org/10.1016/j.physa.2020.124847) | Quantifies speed dispersion and conflict rates between two-wheelers and heavy vehicles on Indian multi-lane arterials. |
| **L-03** | Turning maneuvers at un-signalized intersections generate high conflict rates across opposing traffic. | `das2019modeling` | Das et al., *Transp. Res. Part F*, 2019<br/>DOI: [10.1016/j.trf.2019.04.018](https://doi.org/10.1016/j.trf.2019.04.018) | Analyzes powered two-wheeler crossing conflicts and right-turn trajectories at non-signalized junctions. |
| **L-04** | Standard navigation engines (e.g., OSRM) model networks via node-level contraction hierarchies calibrated for cars. | `luxen2011realtime` | Luxen & Vetter, *ACM SIGSPATIAL*, 2011<br/>DOI: [10.1145/2093973.2094062](https://doi.org/10.1145/2093973.2094062) | Defines OSRM's contraction hierarchy architecture, node-level routing, and automobile speed profile assumptions. |
| **L-05** | Turn prohibitions and turn penalties were historically introduced in traffic assignment models. | `kirby1969minimum` | Kirby, *Oper. Res. Q.*, 1969<br/>DOI: [10.2307/3008764](https://doi.org/10.2307/3008764) | Foundational derivation of edge-expanded networks for turn prohibitions and intersection delay penalties. |
| **L-06** | Modeling turn costs in shortest-path routing requires edge-based or line-graph state expansion. | `winter2002modeling` | Winter, *Int. J. Geogr. Inf. Sci.*, 2002<br/>DOI: [10.1080/13658810210148715](https://doi.org/10.1080/13658810210148715) | Proves that turn costs violate Bellman's optimality principle on vertex graphs; requires state expansion to directed edges $(u, v)$. |
| **L-07** | Turn costs in Contraction Hierarchies require static edge shortcuts that restrict dynamic metric customization. | `geisberger2011efficient` | Geisberger & Vetter, *ESA*, 2011<br/>DOI: [10.1007/978-3-642-23719-5_28](https://doi.org/10.1007/978-3-642-23719-5_28) | Documents the complexity of turn-aware contraction hierarchies and the overhead of static shortcut pre-computation. |
| **L-08** | Metric customization in large road networks requires structured graph customization techniques. | `delling2017customizable` | Delling et al., *INFORMS J. Comput.*, 2017<br/>DOI: [10.1287/ijoc.2016.0727](https://doi.org/10.1287/ijoc.2016.0727) | Analyzes customizable contraction hierarchies and multi-attribute metric updates in road networks. |
| **L-09** | Speedup heuristics and multi-criteria routing in road networks surveyed comprehensively. | `bast2016route` | Bast et al., *Algorithm Engineering*, 2016<br/>DOI: [10.1007/978-3-319-49487-6_2](https://doi.org/10.1007/978-3-319-49487-6_2) | Comprehensive survey of point-to-point shortest paths, turn modeling, and speedup techniques. |
| **L-10** | Motorcycles frequently navigate through residential street networks to bypass arterial congestion. | `fadilah2024identifying` | Fadilah et al., *Transp. Res. Interdiscip. Perspect.*, 2024<br/>DOI: [10.1016/j.trip.2024.101147](https://doi.org/10.1016/j.trip.2024.101147) | Documents empirical route choice where two-wheelers cut through local residential streets to avoid arterial delays. |
| **L-11** | Existing multi-criteria motorcycle routing (Entropy-TOPSIS) ranks pre-computed routes without turn awareness during search. | `asvial2020entropy` | Asvial et al., *IEEE Access*, 2020<br/>DOI: [10.1109/ACCESS.2020.3040375](https://doi.org/10.1109/ACCESS.2020.3040375) | Implements multi-criteria decision making over pre-computed routes; establishes the research gap in online turn-aware search. |
| **L-12** | Multi-criteria shortest path heuristics balance travel distance against non-distance trip attributes. | `zografos2004heuristic` | Zografos & Androutsopoulos, *Transp. Res. Part C*, 2004<br/>DOI: [10.1016/j.trc.2004.07.006](https://doi.org/10.1016/j.trc.2004.07.006) | Foundational heuristic framework for multi-criteria point-to-point shortest path algorithms. |
| **L-13** | Heuristic admissibility ($h \le c^*$) and monotonic consistency guarantee optimal shortest paths without reopening. | `hart1968formal` | Hart, Nilsson, & Raphael, *IEEE Trans. Syst. Sci. Cybern.*, 1968<br/>DOI: [10.1109/TSSC.1968.300136](https://doi.org/10.1109/TSSC.1968.300136) | Foundational mathematical proofs establishing that consistent heuristics guarantee optimal node expansion order. |
| **L-14** | Triangle inequality lower bounds provide admissible distance estimates on spatial networks. | `goldberg2005computing` | Goldberg & Harrelson, *SODA*, 2005 | Establishes triangle inequality lower-bound theory (ALT algorithm) in directed spatial networks. |
| **L-15** | Metropolitan road networks can be topologically modeled, constructed, and analyzed via OpenStreetMap. | `boeing2017osmnx` | Boeing, *Comput. Environ. Urban Syst.*, 2017<br/>DOI: [10.1016/j.compenvurbsys.2017.05.004](https://doi.org/10.1016/j.compenvurbsys.2017.05.004) | Establishes the methodology for OSMnx street network extraction, MultiDiGraph representation, and edge length attribution. |
| **L-16** | Metropolitan traffic impedance in Bengaluru is characterized by chronic arterial bottleneck saturation. | `kumar2025realtime` | Kumar et al., *IEEE Trans. Intell. Transp. Syst.*, 2025<br/>DOI: [10.1109/TITS.2024.3498871](https://doi.org/10.1109/TITS.2024.3498871) | Documents corridor-level travel-time degradation and arterial congestion characteristics across Bengaluru. |

---

## 2. Part B: Internal Experimental Claims (Supported by Frozen Evidence)

Every numerical value, statistical test statistic, effect size, and network topological parameter reported in Paper 1 is verified directly against the frozen Phase 13.4 experimental artifacts.

| Item # | Manuscript Claim | Exact Numerical Evidence | Source Artifact File | Protocol Verification Status |
| :---: | :--- | :--- | :--- | :---: |
| **E-01** | Turn-aware routing (A0) reduces sharp turns by $34.1\%$ relative to turn-unaware routing (A1). | Mean sharp turns: $32.52 \to 21.44$ ($-11.08$ turns, $-34.1\%$). Pratt $W=0.0$, $p_{\text{adj}} = 4.5 \times 10^{-5}$, Cohen's $d_z = -1.0066$ [$-1.42, -0.59$], Hodges-Lehmann $-9.50$ [$-13.0, -7.0$]. | `statistical_test_results.csv`<br/>`exp_a_corridor_metrics.csv` | **VERIFIED & FROZEN** |
| **E-02** | Condition A1 and Condition A2 produce identical route geometries across the 25 corridors. | `route_A1 == route_A2` for **$25 / 25$ corridors**. Identical mean distance ($7.723\text{ km}$), identical sharp turns ($32.52$), identical impedance cost ($9,325.87$). | `phase_13_1_stage_2B_full_ablation_report.md#Section-2`<br/>`exp_a_corridor_metrics.csv` | **VERIFIED & FROZEN** |
| **E-03** | State expansion incurs $3.78\times$ median runtime overhead; turn evaluation adds $1.13\times$ overhead. | A2 median runtime: $40.88\text{ ms}$; A1 median: $154.69\text{ ms}$ ($3.78\times$); A0 median: $174.93\text{ ms}$ ($1.13\times$ vs A1; $4.28\times$ vs A2). | `exp_a_corridor_metrics.csv`<br/>`statistical_test_results.csv` | **VERIFIED & FROZEN** |
| **E-04** | Two-wheeler road impedance suppresses arterial exposure by $51.21\text{ pp}$. | Arterial share: $65.05\%$ (Neutral B1) $\to 13.84\%$ (Production B0) ($-51.21\text{ pp}$). Pratt $W=0.0$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, Cohen's $d_z = -1.7715$ [$-2.33, -1.21$], Hodges-Lehmann $-50.21\text{ pp}$. | `statistical_test_results.csv`<br/>`exp_b_corridor_metrics.csv` | **VERIFIED & FROZEN** |
| **E-05** | Residential street routing increases by $+30.73\text{ pp}$ at a $+15.53\%$ detour cost. | Residential share: $13.51\% \to 44.24\%$ ($+30.73\text{ pp}$, $p_{\text{adj}} = 0.00015$, $d_z = +1.5234$). Detour distance: $+15.53\%$ ($+1.028\text{ km}$, $p_{\text{adj}} = 8.4 \times 10^{-5}$, $d_z = +1.4883$). | `statistical_test_results.csv`<br/>`exp_b_corridor_metrics.csv` | **VERIFIED & FROZEN** |
| **E-06** | Sharp turns decrease monotonically across sensitivity tiers $C_0 \to C_3$. | Sharp turn means: $C_0 (0/0) = 32.52 \to C_1 (12/4) = 24.64 \to C_2 (25/8) = 21.44 \to C_3 (50/16) = 19.80$. | `exp_c_corridor_metrics.csv` | **VERIFIED & FROZEN** |
| **E-07** | Baseline $C_2$ ($25/8$) represents the empirical corpus-average trade-off knee. | Non-dominated Pareto frontier is $\{C_2, C_3\}$. $C_2$ captures $\frac{11.08}{12.72} = 87.1\%$ of maximum turn reduction while anchoring global minimum route distance ($7.648\text{ km}$). | `phase_13_4_correction_and_freeze_report.md#Section-2`<br/>`exp_c_corridor_metrics.csv` | **VERIFIED & FROZEN** |
| **E-08** | Arterial flyover discount increases bridge traversal by $+148.9\%$. | Mean bridge traversal: $159.68\text{ m} \to 397.44\text{ m}$ ($+237.76\text{ m}$, $+148.9\%$, Pratt $W=0.0$, $p_{\text{adj}} = 0.0019$, $d_z = +0.7420$). Route distance drops by $-111.6\text{ m}$. | `statistical_test_results.csv`<br/>`exp_d_corridor_metrics.csv` | **VERIFIED & FROZEN** |
| **E-09** | Production baseline median execution runtime is $174.93\text{ ms}$. | Median runtime across 25 corridors: $174.93\text{ ms}$; IQR: $439.08\text{ ms}$; Mean: $382.98\text{ ms} \pm 464.48\text{ ms}$; Range: $1.01\text{ ms}$ to $1,829.18\text{ ms}$. ($N=25, R=5$). | `exp_a_corridor_metrics.csv`<br/>`phase_13_1_stage_2B_full_ablation_report.md` | **VERIFIED & FROZEN** |
| **E-10** | Metropolitan road graph scale and valence properties. | $|V| = 308,643$ nodes; $|E| = 744,216$ directed edges; $d_{\max}^{\text{in}} = 6$; $d_{\max}^{\text{out}} = 6$; mean degree $2.41$; $|E_S| = 2,103,894$; $|E_S| / |E| = 2.83$; minimum edge multiplier $\mu_{\min} = 0.8000$; 0 bridge roundabouts. | `bengaluru_graph.pkl`<br/>`phase_3_5_final_validation.md` | **VERIFIED & FROZEN** |

---

## 3. Explicit Mathematical Assumptions Checklist

| Assumption ID | Formal Mathematical Statement | Implementation Status | Empirical Verification on Bengaluru Graph |
| :---: | :--- | :--- | :--- |
| **Assumption A1** | $\forall e \in E, \quad \mu(e) \ge \mu_{\min} = 0.80$ | Code allows theoretical $0.76$ if bridge and roundabout coincide. | **Verified with zero violations** across all $744,216$ directed edges (minimum multiplier is strictly $0.8000$; exactly 0 bridge roundabouts). |
| **Assumption A2** | $\forall v \in V, \quad \max(d_{\text{in}}(v), d_{\text{out}}(v)) \le c = \mathcal{O}(1)$ | Graph topology depends on physical civil road design. | **Verified with zero violations** across all $308,643$ intersections ($d_{\max}^{\text{in}} \le 6, d_{\max}^{\text{out}} \le 6$). |

---

*Checklist verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
