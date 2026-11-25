# Section III Evidence Map — Code Traceability and Epistemological Audit (v1.1)

**Document:** [`paper1_section_III_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_evidence_map_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Two-Column `IEEEtran`)  
**Phase:** Phase 7.1-R — Multiplier Lower-Bound and Objective-Function Audit  
**Source Code References:** [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py), [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py)  
**Ablation Dataset:** [`research/literature_survey/13_ablation_study/`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/literature_survey/13_ablation_study/) (Frozen Phase 13.4)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE CODE TRACEABILITY AND MATHEMATICAL EVIDENCE MAP**

---

## 1. Codebase Traceability Matrix

Every mathematical parameter, threshold, formulation, and logical condition planned for Section III maps directly to the active, frozen codebase.

| Section III Mathematical Element | Notation | Exact Value / Formula | Codebase Source File | Exact Line Numbers | Implementation Logic / Code Excerpt |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Edge Physical Length** | $\ell(e)$ | Positive float ($m$) | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L274) | Lines 274, 421, 632 | `length = float(edge_data.get("length", 1.0))` |
| **Highway Classification** | $h(e)$ | String / Tag | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L276-L283) | Lines 276–283 | `hw = edge_data.get("highway", "unclassified"); if isinstance(hw, list): hw = hw[0]` |
| **Base Class Penalty Map** | $f_{\text{class}}(h)$ | $0.90\text{--}4.00$ | [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py#L61-L77) | Lines 61–77 | `TWO_WHEELER_ROAD_PENALTIES = {'motorway': 4.0, ... 'service': 0.9, 'road': 1.1}` |
| **Main Road Set** | $\mathcal{H}_{\text{main}}$ | 8 Arterial Types | [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py#L51-L54) | Lines 51–54 | `MAIN_ROAD_TYPES = {'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', ...}` |
| **Bridge Tag Extraction** | $\text{bridge}(e)$ | Boolean / String | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L298-L307) | Lines 298–307 | `is_bridge = edge_data.get("bridge"); if is_bridge and is_bridge not in ["no", "false", "0"]:` |
| **Arterial Bridge Override** | $\mu_{\text{bridge}}$ | **Replaces with 0.80** | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L311) | Lines 309–311 | `if hw in MAIN_ROAD_TYPES: penalty = 0.8` *(Direct replacement, not multiplication)* |
| **Roundabout Modifier** | $m_{\text{rbt}}(e)$ | Multiplies by $0.95$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L326-L331) | Lines 326–331 | `if edge_data.get("junction") == "roundabout": penalty *= penalty_map.get("_roundabout_multiplier", 0.95)` |
| **Minimum Multiplier Floor** | $\mu_{\min}$ | Fixed constant: $0.80$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L28) | Line 28 | `MIN_PENALTY_FLOOR = 0.8` |
| **Composite Edge Cost** | $\mu(e) \ell(e)$ | `length * penalty` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L347) | Line 347 | `return length * penalty` |
| **Forward Azimuth Bearing** | $\theta(u, v)$ | Bearing in $[0^\circ, 360^\circ)$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L63-L76) | Lines 63–76 | `_bearing_deg(lat1, lng1, lat2, lng2)` using spherical forward azimuth formula |
| **Angular Deflection** | $\Delta\theta$ | Angle in $[0^\circ, 180^\circ]$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L110-L144) | Lines 110–144 | `difference = abs(incoming - outgoing); return min(difference, 360.0 - difference)` |
| **Moderate Turn Threshold** | $\Theta_{\text{mod}}$ | Constant: $30.0^\circ$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L41) | Line 41 | `TURN_THRESHOLD_MODERATE = 30.0` |
| **Sharp Turn Threshold** | $\Theta_{\text{sharp}}$ | Constant: $60.0^\circ$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L42) | Line 42 | `TURN_THRESHOLD_SHARP = 60.0` |
| **Moderate Turn Penalty** | $P_{\text{mod}}$ | Constant: $8.0\text{ m}$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L38) | Line 38 | `TURN_PENALTY_MODERATE = 8.0` (effective meters, $m$) |
| **Sharp Turn Penalty** | $P_{\text{sharp}}$ | Constant: $25.0\text{ m}$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L37) | Line 37 | `TURN_PENALTY_SHARP = 25.0` (effective meters, $m$) |
| **Piecewise Turn Penalty** | $P_{\text{turn}}$ | $\{0.0, 8.0, 25.0\}$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L146-L167) | Lines 146–167 | `if prev_node is None: return 0.0; if angle >= 60.0: return 25.0; if angle >= 30.0: return 8.0; return 0.0` |
| **Edge-State Definition** | $s = (u, v)$ | 2-tuple of node IDs | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L482-L487) | Lines 482–487, 674–677 | `state = (previous_node, current_node)`, `next_state = (current_node, next_node)` |
| **Synthetic Origin State** | $s_0^{\text{state}}$ | `(None, start_node)` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L375-L378) | Lines 375–378, 522–525 | `start_state = (initial_previous_node, start_node)` where default is `None` |
| **Transition Cost Addition** | $c(s, s')$ | `edge_cost + turn_cost` | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L435) | Lines 435, 668–672 | `new_cost = current_cost + edge_cost + turn_cost` |
| **Destination Termination** | Path End | Halt upon popping $t$ | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L402) | Lines 402, 566 | `if current_node == end_node:` halts search loop without exit turn penalty |

---

## 2. In-Depth Operational Mechanics

### 2.1 Grade-Separated Arterial Bridge / Flyover Override Mechanics

In urban transportation networks, elevated arterial flyovers are designed to permit express vehicular movement across dense, congested ground-level intersections.

1. **Implementation Realization:**
   In [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L311):
   ```python
   if is_bridge and is_bridge not in ["no", "false", "0"]:
       if hw in MAIN_ROAD_TYPES:
           penalty = 0.8
   ```
2. **Mathematical Distinction:**
   - **Incorrect Formulation (Common Error):** $\mu(e) = f_{\text{class}}(h(e)) \times 0.80$.  
     If this were true, an elevated primary road ($2.20$) would receive a multiplier of $2.20 \times 0.80 = 1.76$, remaining heavily penalized relative to surface residential streets ($1.00$).
   - **Correct Implemented Formulation:** $\mu(e) = 0.80$.  
     The elevated structure completely bypasses surface arterial friction. The engine replaces the severe arterial penalty ($2.20\text{--}4.00$) with a priority encouraging factor of $0.80$, making the elevated corridor more attractive than parallel residential bypasses ($1.00$).
3. **Empirical Effect:**
   As verified in Phase 13.4 Experiment D (`exp_d_corridor_metrics.csv`), enabling this override increases arterial flyover traversal from $159.68\text{ m}$ to $397.44\text{ m}$ ($+148.9\%$, $p_{\text{adj}} = 0.0039$), successfully channelizing two-wheelers onto major elevated corridors (e.g., Hebbal Elevated Expressway on `OD_15` and Whitefield Flyover on `OD_04`).

---

### 2.2 Roundabout Ordering Mechanics and Multiplier Lower-Bound Facts

The relationship between the bridge override, roundabout modifier, and theoretical lower bound is audited as follows:

1. **Implementation Sequential Ordering:**  
   In [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L331), the roundabout modifier ($0.95\times$) is executed sequentially **after** the bridge override check (`penalty = 0.8`).
2. **Theoretical Value on Co-Occurring Tags:**  
   If an edge simultaneously qualifies as an arterial bridge (`bridge=yes`, $h \in \mathcal{H}_{\text{main}}$) AND carries a roundabout tag (`junction=roundabout`), the sequential calculation yields:
   $$\mu(e) = 0.80 \times 0.95 = 0.76$$
   This value falls below $0.80$.
3. **Empirical Dataset Verification on Bengaluru:**  
   In [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl), an exhaustive topological scan across all $|E| = 744,216$ directed edges confirms that **exactly zero edges** carry both tags simultaneously.
4. **Minimum Observed Multiplier:**  
   The minimum observed edge multiplier across the entire evaluated Bengaluru dataset is strictly **0.80**.
5. **Scientific Framing:**  
   - The condition $\mu(e) \ge 0.80$ is framed as a **dataset-verified condition** for the Bengaluru network in the current experiments.
   - It is also the **explicit operational condition (Assumption A1)** required for the formal proof of Haversine heuristic admissibility ($h(s) \le c^*(s)$) in Section IV.
   - **Non-Universal Limitation:** We do NOT claim that civil infrastructure universally prevents co-occurrence on arbitrary input graphs. On an arbitrary OpenStreetMap graph where tagging anomalies or elevated roundabouts exist, an edge could evaluate to $0.76$ unless an explicit code clamping floor (`max(0.80, penalty)`) is introduced.

---

### 2.3 Objective Function and Transition-to-Path Accounting

1. **Atomic State Transition:**  
   At state $s = (u, v)$, the vehicle is positioned at vertex $v$ having arrived via edge $(u, v)$. Moving to successor state $s' = (v, w)$ traverses edge $(v, w) \in E$ and performs a turn deflection at vertex $v$:
   $$c(s, s') = \mu(v, w) \cdot \ell(v, w) + P_{\text{turn}}(u, v, w)$$
   Code confirmation ([`routing/algorithms.py#L668-L672`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L668-L672)):
   ```python
   turn_cost = _turn_penalty(graph, previous_node, current_node, next_node)
   new_cost = current_cost + edge_cost + turn_cost
   ```
2. **Synthetic Initial Transition:**  
   At origin $s_0$, the root state is $\sigma_0 = (\text{None}, s_0)$. Departing along initial edge $e_1 = (s_0, w)$ executes transition $(\sigma_0, \sigma_1)$ where $\sigma_1 = (s_0, w)$:
   $$c(\sigma_0, \sigma_1) = \mu(s_0, w) \cdot \ell(s_0, w) + P_{\text{turn}}(\text{None}, s_0, w) = \mu(e_1) \cdot \ell(e_1) + 0.0$$
   Code confirmation ([`routing/algorithms.py#L151-L152`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L151-L152)):
   ```python
   if prev_node is None:
       return 0.0
   ```
3. **Destination Extraction:**  
   When state $\sigma_k = (v_{k-1}, t)$ is popped, `current_node == end_node` evaluates to True. The search loop breaks immediately ([`routing/algorithms.py#L566-L605`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L566-L605)). No successor edges from $t$ are evaluated, and zero exit turn penalty is assessed at destination $t$.
4. **Complete Route Accounting:**  
   For path $P = \langle e_1, \dots, e_k \rangle$ traversing $k$ edges and $k+1$ vertices ($v_0, \dots, v_k$):
   - Edge impedance is evaluated exactly once per physical segment: $\sum_{i=1}^k \mu(e_i) \ell(e_i)$.
   - Turn penalties are evaluated exactly once at each of the $k-1$ intermediate junctions: $\sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$.
   - The total transition summation $\sum_{j=1}^k c(\sigma_{j-1}, \sigma_j)$ is algebraically identical to the path-level objective $C(P)$.
5. **Distance Metrics Disentangled:**  
   - Physical route length $D(P) = \sum_{i=1}^k \ell(e_i)$ has units of physical surveyed meters ($m$).
   - Multi-attribute impedance cost $C(P)$ has units of effective impedance meters ($m$).
   - Turn penalties $P_{\text{turn}} \in \{0.0, 8.0, 25.0\}$ have units of effective impedance meters ($m$).

---

## 3. Epistemological Classification of Claims

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            EPISTEMOLOGICAL CLASSIFICATION OF ASSERTIONS                          │
├────────────────────────────┬─────────────────────────────────────────────────────────────────────┤
│ Epistemological Category   │ Scope of Permitted Assertions in Section III                        │
├────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ 1. Direct Implementation   │ • Exact code parameters: 25.0 m, 8.0 m, 0.0 m, 30.0°, 60.0°.       │
│    Facts (Verified)        │ • Exact multiplier table: Motorway 4.0 down to Service 0.90.        │
│                            │ • Bridge override mechanism: Replaces base penalty with 0.80.       │
│                            │ • State structure: s = (u, v), root = (None, s_0).                  │
│                            │ • State cardinality: |S| = |E| + 1.                                 │
│                            │ • Sequential ordering: Roundabout factor applied after bridge.      │
│                            │ • Search halts on popping destination t; no exit turn penalty.      │
├────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ 2. Formal Mathematical     │ • Directed multigraph G = (V, E) with physical edge lengths l(e)>0. │
│    Formulations            │ • State-expanded transition graph G_S and transition cost c(s, s'). │
│                            │ • Spherical deflection angle via forward azimuth trigonometry.      │
│                            │ • Lemma 1: Zero turn penalty on initial departure (None, s_0, w).   │
│                            │ • Exact algebraic identity between transition sum and C(P).         │
│                            │ • Dimensional consistency proof: All additive cost terms are [L].   │
├────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ 3. Engineering Modeling    │ • Road multipliers reflect functional hierarchy and congestion      │
│    Assumptions             │   susceptibility; NOT empirically fitted econometric preferences.   │
│                            │ • Turn penalties reflect geometric maneuver friction; NOT measured │
│                            │   accident probabilities or crash safety ratings.                   │
│                            │ • Assumption A1 (mu >= 0.80) is a dataset-verified condition for    │
│                            │   the Bengaluru experimental corpus and a required proof condition; │
│                            │   NOT an unconditional property of arbitrary input graphs.          │
│                            │ • Path cost C(P) is an impedance metric, NOT physical travel time.  │
├────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ 4. Strictly Prohibited     │ • NO claims that weights represent validated human rider utilities. │
│    Over-Claims             │ • NO claims of travel-time savings or vehicle queue delays.         │
│                            │ • NO claims of safety enhancements or accident prevention.          │
│                            │ • NO claims that bridge modifier scales base penalty (f_class * 0.8)│
│                            │ • NO universal civil-infrastructure guarantee that bridges and      │
│                            │   roundabouts cannot co-occur on arbitrary graphs.                  │
└────────────────────────────┴─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Missing Evidence and Gap Analysis

A rigorous audit confirms that:
1. **No Phantom Parameters:** Every numerical constant in Section III outline ($4.0, 3.0, 2.5, 2.2, 2.0, 1.5, 1.4, 1.15, 1.1, 1.0, 0.95, 0.9, 0.8, 25.0, 8.0, 30.0^\circ, 60.0^\circ$) exists in `core/config.py` and `routing/algorithms.py`.
2. **No Uncalibrated Formulae in Section III:** The uncalibrated signal-based ETA filtering formula ($T \cdot 0.985^N$) identified in Phase 13.4 is completely excluded from Section III.
3. **No Paper 2 Alternative Routing:** Waypoint generation, detour tolerances ($\epsilon \le 1.20$), and overlap thresholds ($\gamma \le 0.70$) are strictly excluded.
4. **Complete Traceability:** Zero missing evidence flags or undefined terms remain.
