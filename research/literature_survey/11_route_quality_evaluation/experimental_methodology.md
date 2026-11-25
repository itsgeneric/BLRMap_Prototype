# Experimental Methodology: Route Quality Evaluation, Parameter Sensitivity, and Runtime Analysis

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 11 — Route Quality Evaluation and Experimental Analysis  
**Date:** March 2026  
**Status:** Approved Experimental Protocol  
**Location:** `research/literature_survey/11_route_quality_evaluation/experimental_methodology.md`  

---

## 1. Research Context and Objectives

Following the mathematical validation of heuristic admissibility in Phase 9 and the comparative route diversity benchmarking of Perpendicular-Offset Via-Node routing against Yen’s K-Shortest Paths (KSP) in Phase 10, **Phase 11 evaluates the empirical quality, operational usefulness, and parameter sensitivity of the generated routes**.

The objective of Phase 11 is not to implement new algorithms or alter production code, but to conduct rigorous, controlled experimental evaluations across the real-world road graph of Bengaluru, India (`bengaluru_graph.pkl`, 308,643 nodes, 744,216 edges).

### Primary Research Questions
1. **Route Structural Quality:** How do primary and alternative routes differ in physical length, two-wheeler impedance cost, road-class hierarchy (arterial vs. collector vs. residential), and maneuver complexity (turn counts and turn penalties)?
2. **Impedance Cost vs. Physical Distance:** How does the two-wheeler impedance cost diverge from physical distance, and how does road prioritization affect routing decisions?
3. **Behavioral Divergence:** In representative corridors, what physical infrastructure features (railways, lakes, grade-separated junctions, bottlenecks) cause alternative routing to succeed or fail?
4. **Parameter Sensitivity:** How sensitive are route selection, detour stretch, and alternative diversity to engineering parameters (road-class multipliers, turn penalties, bridge/flyover modifiers)?
5. **Computational Scalability & Variance:** What is the runtime distribution and variance across uniform-cost Dijkstra, standard admissible A*, aggressive A*, perpendicular-offset routing, and Yen's KSP under repeated trials?

---

## 2. Mathematical Formulations and Evaluation Metrics

### 2.1 Physical Distance vs. Two-Wheeler Impedance Cost
A fundamental methodological boundary of this evaluation is the strict distinction between physical distance and impedance cost:
- **Physical Distance $L(P)$ (meters / kilometers):**
  $$L(P) = \sum_{i=1}^{k-1} \ell(v_i, v_{i+1})$$
  where $\ell(u, v)$ is the geodesic edge length in meters extracted from OpenStreetMap road geometries.
- **Two-Wheeler Impedance Cost $C(P)$ (dimensionless cost units):**
  $$C(P) = \sum_{i=1}^{k-1} c(v_i, v_{i+1}) + \sum_{i=1}^{k-2} \tau(v_{i-1}, v_i, v_{i+1})$$
  where:
  - $c(u, v) = \ell(u, v) \cdot \mu_{\text{road}}(u, v) \cdot \mu_{\text{bridge}}(u, v) \cdot \mu_{\text{roundabout}}(u, v) \cdot \mu_{\text{surface}}(u, v)$
  - $\tau(u, v, w)$ is the maneuver/turn penalty at vertex $v$.
  - **Scientific Notice:** $C(P)$ is **not** travel time in seconds or minutes. It is an engineering impedance metric designed to prioritize two-wheeler-friendly infrastructure and penalize heavy-traffic arterials and sharp maneuvers.

### 2.2 Detour Ratios
For any alternative route $P_{\text{alt}}$ evaluated against primary route $P_{\text{primary}}$:
- **Distance Detour Ratio:**
  $$\delta_{\text{dist}}(P_{\text{alt}}) = \frac{L(P_{\text{alt}})}{L(P_{\text{primary}})}$$
- **Cost Detour Ratio:**
  $$\delta_{\text{cost}}(P_{\text{alt}}) = \frac{C(P_{\text{alt}})}{C(P_{\text{primary}})}$$
- Under the production constraint, alternatives must satisfy $\delta_{\text{dist}} \le 1.20$ ($+20\%$ detour cap).

### 2.3 Road-Class Composition
Each edge $(u, v)$ in route $P$ is classified according to its OSM `highway` attribute:
- **High-Speed / Trunk:** `motorway`, `motorway_link`, `trunk`, `trunk_link`
- **Major Arterial:** `primary`, `primary_link`
- **Sub-Arterial:** `secondary`, `secondary_link`
- **Collector:** `tertiary`, `tertiary_link`
- **Neighborhood / Local:** `residential`, `living_street`, `unclassified`
- **Access / Service:** `service`, `road`

For each route, the cumulative distance $L_{\text{class}}$ and percentage $\Pi_{\text{class}}$ are recorded:
$$\Pi_{\text{class}} = \frac{L_{\text{class}}}{L(P)} \times 100\%$$

### 2.4 Turn Maneuvers and Direction Changes
For every interior vertex $v_i \in P$ ($i = 2, \dots, k-1$):
- Incoming bearing $\theta_{\text{in}} = \text{bearing}(v_{i-1}, v_i)$
- Outgoing bearing $\theta_{\text{out}} = \text{bearing}(v_i, v_{i+1})$
- Heading difference $\Delta\theta = |\theta_{\text{in}} - \theta_{\text{out}}| \pmod{360}$
- Normalized turn angle:
  $$\phi(v_i) = \min(\Delta\theta, 360^\circ - \Delta\theta)$$

Maneuvers are categorized according to production thresholds:
- **Sharp Turn:** $\phi \ge 60^\circ \implies \tau = 25.0$ cost units
- **Moderate Turn:** $30^\circ \le \phi < 60^\circ \implies \tau = 8.0$ cost units
- **Straight / Micro-deflection:** $\phi < 30^\circ \implies \tau = 0.0$ cost units

Metrics reported:
- Total maneuver count ($N_{\text{total}}$), sharp turn count ($N_{\text{sharp}}$), moderate turn count ($N_{\text{moderate}}$).
- Total turn penalty: $\tau_{\text{total}} = 25 \cdot N_{\text{sharp}} + 8 \cdot N_{\text{moderate}}$.

### 2.5 Route Diversity and Overlap Metrics
- **Shared Edge Overlap Ratio:**
  $$\Omega(P_{\text{primary}}, P_{\text{alt}}) = \frac{\sum_{e \in E(P_{\text{primary}}) \cap E(P_{\text{alt}})} \ell(e)}{\sum_{e \in E(P_{\text{alt}})} \ell(e)}$$
  (Must satisfy $\Omega \le 0.70$ to survive Phase 10 diversity filtering).
- **Jaccard Edge Similarity:**
  $$J(P_1, P_2) = \frac{\sum_{e \in E(P_1) \cap E(P_2)} \ell(e)}{\sum_{e \in E(P_1) \cup E(P_2)} \ell(e)}$$
- **Pairwise Set Diversity:**
  $$\bar{D}(\mathcal{P}) = 1 - \frac{1}{\binom{|\mathcal{P}|}{2}} \sum_{i < j} J(P_i, P_j)$$

---

## 3. Benchmark Network and Snapping Protocol

All experiments are conducted on the production Bengaluru road network:
- **File:** `bengaluru_graph.pkl`
- **Network Dimensions:** 308,643 nodes, 744,216 directed edges.
- **Snapping Method:** Nearest node snapping via OSMnx k-d tree spatial indexing:
  $$v_{\text{snap}} = \arg\min_{v \in V} \text{haversine}(\text{lat}_{\text{query}}, \text{lng}_{\text{query}}, \text{lat}_v, \text{lng}_v)$$
- **25 Pre-Defined Benchmark OD Corridors:** Preserved identically from Phase 9 and Phase 10 across short ($1.3 - 3.5\text{ km}$), medium ($4.5 - 9.0\text{ km}$), and long ($9.5 - 15.0\text{ km}$) corridors across North, South, East, West, and Central Bengaluru.

---

## 4. Controlled Parameter Sensitivity Protocol

To evaluate how parameter values influence route generation, a controlled ablation experiment is conducted on 5 structurally distinct benchmark corridors:
1. **OD_01 (Radial Core Corridor):** BNMIT to MG Road ($10.06\text{ km}$)
2. **OD_04 (Pinch-Point IT Corridor):** Whitefield to Marathahalli ($8.81\text{ km}$)
3. **OD_06 (Major Cross-City Corridor):** Jayanagar 4th Block to Malleshwaram ($12.45\text{ km}$)
4. **OD_12 (Dense Historic Grid):** Frazer Town to Shivajinagar ($2.73\text{ km}$)
5. **OD_15 (Expressway Highway Spine):** Yelahanka to Hebbal ($8.67\text{ km}$)

### Experimental Variations (One parameter group altered at a time):
1. **Baseline Production Configuration (Engineering Heuristics):**
   - Main road penalty: $1.5\times$
   - Inner road multiplier: $0.9\times$
   - Service multiplier: $0.9\times$
   - Bridge discount on main roads: $0.8\times$
   - Roundabout discount: $0.95\times$
   - Turn penalties: Sharp = $25.0$, Moderate = $8.0$
2. **Parameter Group 1: Road-Class Hierarchy Multipliers**
   - **Config 1A (Neutral / Distance-Dominant):** Main $1.0\times$, Inner $1.0\times$, Service $1.0\times$ (Eliminates two-wheeler road bias; tests pure distance path).
   - **Config 1B (Aggressive Arterial Avoidance):** Main $2.5\times$, Inner $0.75\times$, Service $0.8\times$ (Pushes two-wheelers deep into residential grids).
   - **Config 1C (Severe Highway Penalty):** Motorway $6.0\times$, Trunk $5.0\times$, Primary $3.5\times$, Secondary $2.0\times$, Inner $1.0\times$.
3. **Parameter Group 2: Turn Penalties**
   - **Config 2A (Zero Turn Penalty):** Sharp = $0.0$, Moderate = $0.0$ (Tests whether path solver resorts to zig-zag alleys).
   - **Config 2B (Severe Turn Penalty):** Sharp = $60.0$, Moderate = $25.0$ (Heavily suppresses turns; tests if routes cling to straight arterials).
4. **Parameter Group 3: Grade Separation & Junction Modifiers**
   - **Config 3A (Neutral Modifiers):** Bridge = $1.0\times$ (no flyover incentive), Roundabout = $1.0\times$.
   - **Config 3B (Flyover Avoidance):** Bridge = $1.5\times$ (penalizes elevated flyover links), Roundabout = $1.2\times$. *(Note: Tested as a compound configuration with roundabout multipliers).*

**Recorded Outputs:**
- Route physical length ($L$), route impedance cost ($C$), road-class breakdown, turn counts, candidate generation count, surviving alternatives count, mean overlap, and pairwise diversity.
- **Methodological Safeguard:** All parameter sensitivity experiments are executed via isolated, in-memory parameter passing. **The production codebase and configuration files are never modified.**

---

## 5. Runtime Evaluation and Variability Protocol

To evaluate algorithmic efficiency and stability, runtime measurements are conducted with:
- **5 Algorithmic Implementations:**
  1. Dijkstra Baseline (Uniform-cost, state-expanded, $h = 0$)
  2. Standard Admissible A* ($h = 0.8 \cdot \text{haversine}$, state-expanded)
  3. Legacy Aggressive A* ($h = 1.25 \cdot \text{haversine}$, state-expanded)
  4. Perpendicular-Offset Alternative Routing (4 candidates + 70% overlap filter + detour cap)
  5. Yen’s K-Shortest Paths (K=4, state-expanded)
- **Sample Size:** All 25 benchmark corridors.
- **Repetitions:** 5 independent iterations per corridor per algorithm (totaling $25 \times 5 \times 5 = 625$ algorithm executions).
- **Timing Boundary:** High-precision monotonic clock (`time.perf_counter()`), timed strictly around the route search loop. Nearest-node snapping and graph loading times are strictly decoupled.
- **Reported Statistics:** Mean, Standard Deviation, Median, Min, Max, and Interquartile Range (IQR).

---

## 6. Case Study Selection Criteria

Five representative corridors are chosen from the 25-corridor benchmark to provide qualitative and physical infrastructure depth:
1. **OD_01 (BNMIT to MG Road):** Radial corridor from south residential suburban zone to central business district. Demonstrates successful multi-corridor discovery (RV Road, Lalbagh Fort Road, South End Circle) vs. Yen's failure.
2. **OD_04 (Whitefield to Marathahalli):** Major eastern tech hub corridor characterized by severe physical bottlenecks (railway tracks, lakes, HAL airport boundary). Representative case where perpendicular-offset fails to find surviving alternatives under the 1.20 detour cap.
3. **OD_06 (Jayanagar 4th Block to Malleshwaram):** Long $12.45\text{ km}$ trans-city corridor cutting through the heart of Bengaluru. Demonstrates collector road filtering across multi-lane arterials.
4. **OD_12 (Frazer Town to Shivajinagar):** Short $2.73\text{ km}$ high-density historic grid with dense parallel interconnects. The only corridor where Yen's KSP survived under 70% overlap filter.
5. **OD_15 (Yelahanka to Hebbal):** Northern expressway corridor (NH44 / Bellary Road) where the primary path adheres to a high-speed arterial spine. Evaluates why lateral offset alternatives exceed the detour cap.

---

## 7. Data and Implementation Limitations

1. **Static OpenStreetMap Representation:**
   The network reflects physical geometry and OSM classification tags. Dynamic live congestion, signals cycle times, and weather-dependent surface degradation are not dynamically updated in real time.
2. **Heuristic Parameter Nature:**
   The impedance multipliers (e.g., $1.5\times$ main road penalty, $0.9\times$ inner road multiplier, $25.0$ sharp turn cost) are engineering heuristics established through domain reasoning and pre-implementation testing, rather than empirically calibrated via large-scale GPS trajectory fitting.
3. **Impedance Cost Interpretation:**
   Impedance cost is a subjective cost metric. It cannot be linearly converted into travel time (minutes) or fuel consumption without an empirical calibration model.
4. **Diversity vs. Safety/Comfort:**
   Generating a distinct alternative path does not inherently imply that the path is safer, faster, or superior in road condition. Empirical road-class breakdown and turn analysis provide evidence of characteristics, not an absolute safety guarantee.
