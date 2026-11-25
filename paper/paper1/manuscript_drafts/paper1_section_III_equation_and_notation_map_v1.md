# Section III Equation and Notation Map — Problem Formulation and Configured Road Impedance (v1.1)

**Document:** [`paper1_section_III_equation_and_notation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_equation_and_notation_map_v1.md)  
**Paper Title:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Two-Column `IEEEtran`)  
**Phase:** Phase 7.1-R — Multiplier Lower-Bound and Objective-Function Audit  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE MATHEMATICAL NOTATION & EQUATION SPECIFICATION**

---

## 1. Master Notation Glossary

The following mathematical symbols, sets, and variables are formally defined for Section III and maintain strict algebraic consistency across the manuscript and codebase.

### 1.1 Graph Topology and Attributes

| Symbol | Mathematical Definition | Implementation Variable / Source | Domain / Range | Physical Meaning / Description |
| :--- | :--- | :--- | :--- | :--- |
| $G$ | $(V, E)$ | `graph` (`nx.MultiDiGraph`) | Directed multigraph | Metropolitan road network model |
| $V$ | Set of graph vertices | `graph.nodes` | Finite set, $|V| = 308,643$ | Road intersections and geometry curve shape points |
| $E$ | Set of directed edges | `graph.edges` | $E \subseteq V \times V$, $|E| = 744,216$ | Directed roadway segments between intersections |
| $v, u, w$ | Graph vertices | `u`, `v`, `node` | $u, v, w \in V$ | Individual physical nodes |
| $e$ | Directed edge | `(u, v)` | $e = (u, v) \in E$ | Directed roadway link from node $u$ to node $v$ |
| $(\phi_v, \lambda_v)$ | Geographic coordinates | `(nodes[v]['y'], nodes[v]['x'])` | $\phi \in [-90^\circ, 90^\circ], \lambda \in [-180^\circ, 180^\circ]$ | Latitude and longitude in decimal degrees ($^\circ$) |
| $\ell(e)$ | Physical length function | `float(edge_data['length'])` | $\ell: E \to \mathbb{R}^+$ (meters, $m$) | Surveyed spatial length of directed roadway segment $e$ |
| $h(e)$ | Highway classification | `edge_data['highway']` | $h(e) \in \mathcal{H}$ (string/tag) | OpenStreetMap functional road classification |
| $\text{bridge}(e)$ | Grade-separation tag | `edge_data.get('bridge')` | Boolean / String | Indicator of elevated arterial bridge/flyover structure |
| $\text{junction}(e)$ | Junction topology tag | `edge_data.get('junction')` | String (e.g., `'roundabout'`) | Indicator of circular traffic junction |

### 1.2 Origin–Destination Routing Problem

| Symbol | Mathematical Definition | Implementation Variable / Source | Domain / Range | Physical Meaning / Description |
| :--- | :--- | :--- | :--- | :--- |
| $s_0$ | Origin vertex | `start_node` | $s_0 \in V$ | Origin intersection for point-to-point trip |
| $t$ | Destination vertex | `end_node` | $t \in V$ | Target intersection for point-to-point trip |
| $P$ | Directed path | `route = [s[1] for s in states]` | Sequence $\langle e_1, e_2, \dots, e_k \rangle$ | Connected chain of directed edges from $s_0$ to $t$ |
| $D(P)$ | Physical route distance | Calculated post-search sum | $\mathbb{R}^+$ (physical meters, $m$) | $D(P) = \sum_{i=1}^k \ell(e_i)$, true spatial route length |
| $C(P)$ | Total impedance cost | `current_cost` / `cost` | $\mathbb{R}^+$ (effective meters, $m$) | Accumulated multi-attribute impedance objective function |

### 1.3 State-Expanded Search Space ($G_S$)

| Symbol | Mathematical Definition | Implementation Variable / Source | Domain / Range | Physical Meaning / Description |
| :--- | :--- | :--- | :--- | :--- |
| $s$ | Search state | `state = (prev_node, curr_node)` | $s = (u, v) \in E$ | Vehicle positioned at node $v$ having arrived via edge $(u, v)$ |
| $s_0^{\text{state}}$ | Synthetic root state | `start_state = (None, start_node)` | $(\text{None}, s_0)$ | Synthetic departure state from origin before entering network |
| $S$ | Full search state space | State tracking space | $S = E \cup \{(\text{None}, s_0)\}$ | Expanded state space; cardinality $|S| = |E| + 1$ |
| $s \to s'$ | Directed state transition | Successor expansion loop | $(u, v) \to (v, w)$ with $(v, w) \in E$ | Valid transition from inbound edge to outbound edge |
| $E_S$ | State transition space | Explored transitions | $E_S \subseteq S \times S$ | Set of valid transitions; $|E_S| = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) d_{\text{out}}(v)$ |
| $c(s, s')$ | Transition cost function | `edge_cost + turn_cost` | $\mathbb{R}^+$ (effective meters, $m$) | Traversal cost from state $(u, v)$ to state $(v, w)$ |

### 1.4 Angular Deflection and Turn Penalties

| Symbol | Mathematical Definition | Implementation Variable / Source | Domain / Range | Physical Meaning / Description |
| :--- | :--- | :--- | :--- | :--- |
| $\theta(u, v)$ | Forward spherical azimuth | `_bearing_deg(lat1, lng1, lat2, lng2)` | $[0^\circ, 360^\circ)$ | Forward bearing from coordinate $u$ to coordinate $v$ |
| $\Delta\theta(u, v, w)$ | Angular deflection | `_turn_angle(graph, prev, curr, next)` | $[0^\circ, 180^\circ]$ | Absolute angular heading change at vertex $v$ |
| $\Theta_{\text{mod}}$ | Moderate turn threshold | `TURN_THRESHOLD_MODERATE` | Constant: $30.0^\circ$ | Threshold for minor geometric deflection |
| $\Theta_{\text{sharp}}$ | Sharp turn threshold | `TURN_THRESHOLD_SHARP` | Constant: $60.0^\circ$ | Threshold for acute maneuver or opposing cross-traffic turn |
| $P_{\text{mod}}$ | Moderate turn penalty | `TURN_PENALTY_MODERATE` | Constant: $8.0$ (effective meters, $m$) | Additive penalty for moderate direction deflection |
| $P_{\text{sharp}}$ | Sharp turn penalty | `TURN_PENALTY_SHARP` | Constant: $25.0$ (effective meters, $m$) | Additive penalty for sharp/opposing maneuver |
| $P_{\text{turn}}(u, v, w)$ | Turn penalty function | `_turn_penalty(graph, prev, curr, next)` | $\{0.0, 8.0, 25.0\}$ (effective $m$) | Piecewise discrete maneuver penalty function |

### 1.5 Road-Class Impedance and Modifiers

| Symbol | Mathematical Definition | Implementation Variable / Source | Domain / Range | Physical Meaning / Description |
| :--- | :--- | :--- | :--- | :--- |
| $\mathcal{H}_{\text{main}}$ | Main arterial road set | `MAIN_ROAD_TYPES` | Set of 8 string tags | Arterial classes eligible for flyover replacement |
| $f_{\text{class}}(h)$ | Base road penalty map | `TWO_WHEELER_ROAD_PENALTIES.get(hw, 1.0)` | $[0.90, 4.00]$ (dimensionless, $[-]$) | Base penalty reflecting street hierarchy congestion |
| $\mu_{\text{bridge}}$ | Arterial bridge multiplier | Fixed constant in override logic | Constant: $0.80$ (dimensionless, $[-]$) | Replacement multiplier for elevated grade-separated structures |
| $m_{\text{rbt}}(e)$ | Roundabout factor | `_roundabout_multiplier` | $0.95$ if roundabout, else $1.0$ ($[-]$) | Continuous-flow incentive factor for circular junctions |
| $\mu(e)$ | Composite edge multiplier | `penalty` in `two_wheeler_edge_cost` | $[\mu_{\min}, \mu_{\max}] \subset [0.80, 4.00]$ ($[-]$) | Net non-dimensional impedance weighting on segment $e$ |
| $\mu_{\min}$ | Multiplier lower bound | `MIN_PENALTY_FLOOR` | Constant: $0.80$ (dimensionless, $[-]$) | Required theoretical bound & dataset-verified floor |

---

## 2. Display Equations for Section III

In accordance with the frozen page budget and blueprint, Section III contains **exactly three display equations** (Equations 1, 2, and 3).

### Equation (1): Two-Wheeler Road-Class Impedance Multiplier

$$\mu(e) = \begin{cases} 
0.80 \cdot m_{\text{rbt}}(e) & \text{if } \text{bridge}(e) \in \mathcal{B}^+ \text{ and } h(e) \in \mathcal{H}_{\text{main}} \\ 
f_{\text{class}}(h(e)) \cdot m_{\text{rbt}}(e) & \text{otherwise} 
\end{cases} \tag{1}$$

where $\mathcal{B}^+ = \{\text{True}, \text{"yes"}, \text{"true"}, \text{"1"}\}$, $\mathcal{H}_{\text{main}} = \{\text{motorway}, \text{trunk}, \text{primary}, \text{secondary}, \text{links}\}$, and $m_{\text{rbt}}(e) = 0.95$ if $\text{junction}(e) = \text{"roundabout"}$ (otherwise $1.0$).

> [!IMPORTANT]
> **Audit of the Multiplier Lower-Bound Mechanics:**  
> 1. In the codebase ([`routing/algorithms.py#L309-L331`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L309-L331)), the roundabout multiplier ($0.95$) is applied **after** the bridge override check (`penalty = 0.8`).  
> 2. A qualifying arterial bridge edge that also carries a roundabout tag would therefore evaluate to $\mu(e) = 0.80 \times 0.95 = 0.76$.  
> 3. The Bengaluru metropolitan network dataset contains **zero such co-occurrences** across all 744,216 directed edges.  
> 4. The minimum observed edge multiplier on this specific dataset is strictly $0.80$.  
> 
> Consequently, the condition $\mu(e) \ge 0.80$ is framed as a **dataset-verified condition** for the current experimental corpus and an **explicit operational condition (Assumption A1)** required for the theoretical heuristic admissibility proof in Section IV. It is **not** an unconditional topological property of arbitrary input graphs.

---

### Equation (2): Discrete Angular Turn Penalty Function

$$P_{\text{turn}}(u, v, w) = \begin{cases} 
25.0 & \text{if } u \ne \text{None} \text{ and } \Delta\theta(u, v, w) \ge 60.0^\circ \\ 
8.0 & \text{if } u \ne \text{None} \text{ and } 30.0^\circ \le \Delta\theta(u, v, w) < 60.0^\circ \\ 
0.0 & \text{if } u = \text{None} \text{ or } \Delta\theta(u, v, w) < 30.0^\circ 
\end{cases} \tag{2}$$

where angular deflection is computed from spherical forward azimuths:
$$\Delta\theta(u, v, w) = \min\left(|\theta(u, v) - \theta(v, w)|, \; 360^\circ - |\theta(u, v) - \theta(v, w)|\right) \in [0^\circ, 180^\circ]$$
Constants $25.0$ and $8.0$ are expressed in effective-distance meters ($m$).

---

### Equation (3): State Transition Cost and Full Path Objective Function

$$\begin{aligned}
c(s, s') &= \mu(v, w) \cdot \ell(v, w) + P_{\text{turn}}(u, v, w) \\
C(P) &= \sum_{i=1}^k \mu(e_i) \cdot \ell(e_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})
\end{aligned} \tag{3}$$

where $s = (u, v)$ and $s' = (v, w)$ with $(v, w) \in E$.

---

## 3. Rigorous Objective-Function and Summation Audit

To guarantee mathematical precision and complete identity between the algorithmic state transitions and the path-level objective, the indexing and summation limits are audited below.

### 3.1 State Trajectory Representation
Let candidate physical path $P$ from origin $s_0 \in V$ to destination $t \in V$ traverse $k$ directed physical roadway segments:
$$P = \langle e_1, e_2, \dots, e_k \rangle$$
where $e_i = (v_{i-1}, v_i) \in E$ for $i \in \{1, \dots, k\}$, with $v_0 = s_0$ and $v_k = t$. The path traverses $k+1$ vertices: $v_0, v_1, \dots, v_k$.

In state space $S = E \cup \{(\text{None}, s_0)\}$, path $P$ corresponds to a unique sequence of $k+1$ states $\langle \sigma_0, \sigma_1, \dots, \sigma_k \rangle$:
$$\begin{aligned}
\sigma_0 &= (\text{None}, v_0) = s_0^{\text{state}} \\
\sigma_1 &= (v_0, v_1) = e_1 \\
\sigma_2 &= (v_1, v_2) = e_2 \\
&\;\;\vdots \\
\sigma_k &= (v_{k-1}, v_k) = e_k
\end{aligned}$$

This sequence consists of exactly $k$ directed state transitions:
$$\tau_j = (\sigma_{j-1}, \sigma_j) \quad \text{for } j \in \{1, \dots, k\}$$

### 3.2 Transition Cost Accumulation
For each state transition $\tau_j = (\sigma_{j-1}, \sigma_j)$ where $\sigma_{j-1} = (v_{j-2}, v_{j-1})$ and $\sigma_j = (v_{j-1}, v_j) = e_j$:
$$c(\sigma_{j-1}, \sigma_j) = \mu(v_{j-1}, v_j) \cdot \ell(v_{j-1}, v_j) + P_{\text{turn}}(v_{j-2}, v_{j-1}, v_j) = \mu(e_j) \cdot \ell(e_j) + P_{\text{turn}}(v_{j-2}, v_{j-1}, v_j)$$

Evaluating across all $k$ transitions:
1. **Initial Departure ($j = 1$):**  
   $\sigma_0 = (\text{None}, v_0)$ and $\sigma_1 = (v_0, v_1) = e_1$.  
   $$c(\sigma_0, \sigma_1) = \mu(e_1) \cdot \ell(e_1) + P_{\text{turn}}(\text{None}, v_0, v_1)$$  
   By Lemma 1, $P_{\text{turn}}(\text{None}, v_0, v_1) = 0.0$. Thus:
   $$c(\sigma_0, \sigma_1) = \mu(e_1) \cdot \ell(e_1)$$
   The initial departure transition charges edge $e_1$ exactly once and contributes zero turn penalty.
2. **Intermediate Transitions ($j = 2, \dots, k$):**  
   For $j \in \{2, \dots, k\}$, the transition moves from incoming edge $e_{j-1} = (v_{j-2}, v_{j-1})$ to outgoing edge $e_j = (v_{j-1}, v_j)$.  
   $$c(\sigma_{j-1}, \sigma_j) = \mu(e_j) \cdot \ell(e_j) + P_{\text{turn}}(v_{j-2}, v_{j-1}, v_j)$$
   This transition charges the impedance of outgoing physical edge $e_j$ and the turn deflection at intermediate junction $v_{j-1}$.
3. **Destination Termination ($j = k$):**  
   State $\sigma_k = (v_{k-1}, v_k)$ is reached. In the implementation ([`routing/algorithms.py#L566`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L566)), when `current_node == end_node` ($v_k == t$), the search loop terminates immediately upon state extraction. No subsequent outgoing transition is explored, and no exit turn penalty is assessed at destination $t$.

### 3.3 Algebraic Equivalence Proof
Summing the transition costs across all $k$ steps:
$$\begin{aligned}
\sum_{j=1}^k c(\sigma_{j-1}, \sigma_j) &= \sum_{j=1}^k \left[ \mu(e_j) \cdot \ell(e_j) + P_{\text{turn}}(v_{j-2}, v_{j-1}, v_j) \right] \\
&= \sum_{j=1}^k \mu(e_j) \cdot \ell(e_j) + P_{\text{turn}}(\text{None}, v_0, v_1) + \sum_{j=2}^k P_{\text{turn}}(v_{j-2}, v_{j-1}, v_j) \\
&= \sum_{i=1}^k \mu(e_i) \cdot \ell(e_i) + 0.0 + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1}) \\
&= C(P)
\end{aligned}$$

**Key Verification Invariants:**
- **Edge Summation:** Each physical edge $e_i \in P$ is summed **exactly once** in $\sum_{i=1}^k \mu(e_i) \ell(e_i)$.
- **Intermediate Turns:** Exactly $k-1$ intermediate intersections ($v_1$ to $v_{k-1}$) are assessed for turn deflection in $\sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$.
- **Initial Invariance:** Departure from $s_0$ incurs zero turn penalty ($P_{\text{turn}} = 0.0$).
- **Destination Invariance:** Destination $t$ incurs zero exit turn penalty.
- **Physical Distance:** True physical distance is $D(P) = \sum_{i=1}^k \ell(e_i)$, summing each physical segment length exactly once in physical meters ($m$).

---

## 4. Dimensional Analysis and Unit Consistency Verification

| Expression Term | Mathematical Symbol | Base Dimension | Physical Unit | Verification & Invariant Proof |
| :--- | :---: | :---: | :---: | :--- |
| Segment Length | $\ell(e)$ | $[L]$ | physical meters ($m$) | Direct geographic distance along roadway centerline. $\ell(e) > 0$. |
| Road Multiplier | $\mu(e)$ | $[1]$ | dimensionless ($[-]$) | Weighting factor scaling physical distance. Observed $\mu(e) \in [0.80, 4.00]$. |
| Weighted Edge Length | $\mu(e) \cdot \ell(e)$ | $[1] \cdot [L] = [L]$ | effective meters ($m$) | Dimensional product yields effective impedance distance. |
| Angular Deflection | $\Delta\theta$ | $[1]$ | degrees ($^\circ$) | Circular angular deviation normalized to $[0^\circ, 180^\circ]$. |
| Turn Penalty | $P_{\text{turn}}$ | $[L]$ | effective meters ($m$) | Equivalent length penalty added to accumulated impedance. |
| State Transition Cost | $c(s, s')$ | $[L] + [L] = [L]$ | effective meters ($m$) | Additive combination of two homogeneous $[L]$ terms. Strictly $c > 0$. |
| Route Impedance Cost | $C(P)$ | $[L]$ | effective meters ($m$) | Total accumulated impedance cost minimized by search algorithm. |
| Physical Distance | $D(P)$ | $[L]$ | physical meters ($m$) | Unweighted geometric sum of traversed road segment lengths. |

> [!NOTE]
> **Dimensional Homogeneity Confirmed:**  
> Weighted road impedance $\mu(e) \ell(e)$ and turn penalty $P_{\text{turn}}$ both possess physical dimension $[L]$ and are expressed in effective meters ($m$). Physical distance $D(P)$ is expressed in surveyed physical meters ($m$). Neither represents travel time in seconds ($s$) or velocity ($m/s$).

---

## 5. Formal Mathematical Invariant: Lemma 1

> **Lemma 1 (Initial Departure Invariance).**  
> *Let $s_0^{\text{state}} = (\text{None}, s_0)$ be the synthetic start state at origin intersection $s_0 \in V$. For any outgoing directed road segment $(s_0, w) \in E$, the turn penalty evaluates identically to zero:*
> $$P_{\text{turn}}(\text{None}, s_0, w) = 0.0$$
> 
> *Proof.*  
> Directly from Equation (2), the third branch specifies that if the predecessor vertex is $\text{None}$, $P_{\text{turn}}$ evaluates unconditionally to $0.0$, regardless of outgoing azimuth $\theta(s_0, w)$. $\blacksquare$

---

## 6. Notation Reconciliation with Abstract, Section I, and Section II

| Term / Notation | Abstract (`paper1_abstract_v2.md`) | Section I (`paper1_introduction_v1.md`) | Section II (`paper1_related_work_v1.md`) | Planned Section III Notation | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| Search State | $s = (u, v)$ | Dual-state $(u, v)$ | Edge-state $(u, v)$ | $s = (u, v) \in E$ | **100% IDENTICAL** |
| Root State | $(\text{None}, s_0)$ | Synthetic root state | Initial state | $s_0^{\text{state}} = (\text{None}, s_0)$ | **100% IDENTICAL** |
| State Cardinality | $|E|+1$ | $|E|+1$ | $|E|+1$ | $|S| = |E| + 1$ | **100% IDENTICAL** |
| Turn Penalty Values | $25\text{ m}, 8\text{ m}, 0\text{ m}$ | $25\text{ m}, 8\text{ m}$ | Discrete turn costs | $P_{\text{sharp}}=25.0, P_{\text{mod}}=8.0, 0.0\text{ m}$ | **100% IDENTICAL** |
| Turn Deflection | Angular deflection $\Delta\theta$ | Turning maneuvers | Deflection angles | $\Delta\theta(u, v, w) \in [0^\circ, 180^\circ]$ | **100% IDENTICAL** |
| Flyover Modifier | $0.80$ arterial bridge override | $0.80$ arterial bridge discount | Arterial bridge discount | $\mu_{\text{bridge}} = 0.80$ replaces $f_{\text{class}}$ | **100% IDENTICAL** |
| Multiplier Floor | $\mu_{\min} = 0.80$ | Lower-bound floor | Conditional lower bound | $\mu(e) \ge 0.80$ (Dataset-verified & Assumption A1) | **100% RECONCILED** |
| Road Classes | Motorway ($4.0$) to Service ($0.90$) | Road-class impedance | Differentiated street classes | Table I ($0.90\text{--}4.00$) | **100% IDENTICAL** |
| Units | Physical m vs effective m | Physical distance vs impedance | Length vs impedance | $D(P)$ physical m, $C(P)$ effective m | **100% IDENTICAL** |

Zero notation collisions or inconsistencies exist across the frozen front matter, Section I, Section II, and planned Section III.
