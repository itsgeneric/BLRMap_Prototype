# Section III Targeted Graph, Bearing, and Table Audit (Phase 7.2-S)

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 7.2-S — Section III Targeted Graph, Bearing, and Table Audit  
**Date:** 2026-11-06  
**Audited Document:** [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md)  
**Investigated Code & Data Files:**
- [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py)
- [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py)
- [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py)
- [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE TARGETED TECHNICAL AUDIT REPORT**  

---

## Executive Summary

Phase 7.2-S conducts an in-depth, code-level and data-level technical investigation of Section III (*"III. PROBLEM FORMULATION AND CONFIGURED ROAD IMPEDANCE"*). It investigates four specific technical issues:
1. **Directed Multigraph and Edge Identity:** The discrepancy between the multigraph container ($|E| = 744,216$) and the search algorithm's simple vertex-pair state space ($s = (u, v)$ over $|E_{\text{simple}}| = 740,822$ distinct pairs).
2. **Roundabout Table Representation:** The flawed representation in Table I showing the $0.95$ roundabout modifier as an exclusive property of permissive streets rather than a global topological modifier.
3. **Turn Bearing Calculation:** The chord-based initial forward azimuth mechanics of `_bearing_deg` versus tangent junction deflections.
4. **Road-Impedance Interpretation:** Five specific instances of unsupported terminology claiming measured congestion, rider preferences, cross-traffic conflicts, and curvature filtering.

No manuscript text, implementation code, experimental datasets, or frozen sections were modified during this investigation.

---

## 1. Issue 1: Directed Multigraph and Edge Identity

### 1.1 Empirical Ground Truth from `bengaluru_graph.pkl`
Direct inspection of the serialized binary dataset [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) reveals:
- **Graph Container Type:** `networkx.classes.multidigraph.MultiDiGraph`.
- **Node Cardinality ($|V|$):** $308,643$ nodes.
- **Total Directed Multigraph Edges ($|E_{\text{multi}}|$):** $744,216$ edge records.
- **Distinct Ordered Directed Vertex Pairs ($|E_{\text{simple}}|$):** **$740,822$ pairs**.
- **Vertex Pairs with Parallel Edges ($> 1$ edge):** **$3,379$ pairs**.
- **Total Multi-Edges Across Parallel Pairs:** **$6,773$ edge records**.
- **Excess Parallel Edges ($|E_{\text{multi}}| - |E_{\text{simple}}|$):** **$3,394$ edges**.
- **Maximum Parallel Edges Between Any Single Pair:** **4 parallel directed edges**.

### 1.2 Routing Algorithm Implementation Mechanics
In [`routing/algorithms.py#L611-L656`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L611-L656) (`two_wheeler_astar`) and lines 415–426 (`astar_on_graph`):
```python
for next_node in graph.successors(current_node):
    edge_data = graph.get_edge_data(current_node, next_node)
    if edge_data is None:
        continue

    # Multi-edge support:
    if "length" in edge_data:
        edge_cost = two_wheeler_edge_cost(edge_data, ...)
    else:
        edge_cost = min(
            two_wheeler_edge_cost(data, ...)
            for data in edge_data.values()
        )
```
And state tracking at lines 674–677:
```python
next_state = (current_node, next_node)
```

**Key Findings:**
1. **Parallel Edge Resolution:** `graph.successors(current_node)` yields each neighboring vertex `next_node` **exactly once**, regardless of how many parallel edges connect `current_node` to `next_node`.
2. **Cost Collapse:** When multiple parallel directed edges connect `current_node` and `next_node`, `edge_data` is a key-indexed dict (`{0: {...}, 1: {...}}`). The code executes `min(...)`, **collapsing parallel edges to the single minimum-cost edge** on-the-fly.
3. **State Structure:** Search states are tracked as 2-tuples $s = (u, v) \in V \times V$. The state contains **no edge key** $k$ (i.e., it is not $(u, v, k)$).
4. **State Cardinality Inconsistency:** The manuscript currently states:
   *"Let the urban street network be represented by a directed multigraph $G = (V, E)$ ... The expanded state space is $S = E \cup \{(\text{None}, s_0)\}$, yielding state cardinality $|S| = |E| + 1$."*
   If $|E|$ refers to the multigraph edge count ($744,216$), then $|S| = |E| + 1$ is mathematically incorrect because there are only $740,822$ distinct $(u, v)$ transitions in the search space. Tracking states by $(u, v)$ yields $|S| = 740,822 + 1 = 740,823$, not $744,217$.

### 1.3 Mathematical Formulation Correction
To maintain rigorous mathematical truth without changing the implementation:
- **Formal Definition:** Clarify that while the base OpenStreetMap dataset is extracted as a directed multigraph $G_{\text{raw}} = (V, E_{\text{raw}})$ ($|E_{\text{raw}}| = 744,216$), the routing algorithm operates over the canonical simple directed graph $G = (V, E)$ where $E \subseteq V \times V$ ($|E| = 740,822$) represents the set of distinct directed vertex adjacencies.
- **Edge Cost Projection:** For adjacent pair $(u, v) \in E$, the effective edge traversal cost and length represent the minimum-impedance candidate among parallel connections:
  $$\ell_{\min}(u, v) = \min_{k} \mu(u, v, k) \cdot \ell(u, v, k)$$
- **State Cardinality:** Under this canonical simple directed graph formulation, state space $S = E \cup \{(\text{None}, s_0)\}$ satisfies $|S| = |E| + 1 = 740,823$ with complete mathematical validity.

---

## 2. Issue 2: Roundabout Table Representation

### 2.1 Implementation Reality in `routing/algorithms.py`
In [`routing/algorithms.py#L326-L331`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L326-L331):
```python
if edge_data.get("junction") == "roundabout":
    penalty *= penalty_map.get(
        "_roundabout_multiplier",
        0.95
    )
```
- **Scope of Modifier:** The condition checks **only** `edge_data.get("junction") == "roundabout"`. It does **not** inspect `highway`.
- Therefore, the $0.95$ multiplier applies to **every edge carrying `junction=roundabout`**, regardless of whether the edge is residential, tertiary, secondary, primary, trunk, or service.

### 2.2 Resulting Multipliers for Relevant Combinations

| Road Hierarchy / Structure | Base Multiplier ($f_{\text{class}}$) | Bridge Override | Roundabout Modifier | Net Effective Multiplier ($\mu$) |
| :--- | :---: | :---: | :---: | :---: |
| **Residential Standard** | $1.00$ | N/A | $1.00$ | **1.000** |
| **Residential Roundabout** | $1.00$ | N/A | **0.95** | **0.950** ($1.00 \times 0.95$) |
| **Tertiary Standard** | $1.15$ | N/A | $1.00$ | **1.150** |
| **Tertiary Roundabout** | $1.15$ | N/A | **0.95** | **1.0925** ($1.15 \times 0.95$) |
| **Secondary Standard** | $1.50$ | N/A | $1.00$ | **1.500** |
| **Secondary Roundabout** | $1.50$ | N/A | **0.95** | **1.425** ($1.50 \times 0.95$) |
| **Primary Standard** | $2.20$ | N/A | $1.00$ | **2.200** |
| **Primary Roundabout** | $2.20$ | N/A | **0.95** | **2.090** ($2.20 \times 0.95$) |
| **Service Standard** | $0.90$ | N/A | $1.00$ | **0.900** |
| **Service Roundabout** | $0.90$ | N/A | **0.95** | **0.855** ($0.90 \times 0.95$) |
| **Arterial Flyover (Bridge)** | $2.20\text{--}4.00$ | **Replaced by 0.80** | $1.00$ | **0.800** |
| **Bridge-Roundabout Combination** | $2.20\text{--}4.00$ | **Replaced by 0.80** | **0.95** | **0.760** ($0.80 \times 0.95$, $0$ in corpus) |

### 2.3 Identified Flaw in Draft Table I
In [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md), Table I placed `Roundabout (×0.95)` only in the "Permissive Street" row (`living_street`, `service`). This misleads the reader into believing the roundabout discount applies only to permissive streets.

### 2.4 Recommended Corrected Table I Design
Table I should cleanly decouple **base road-class weights** from **topological modifiers**:

```latex
\begin{table}[t]
\caption{Configured Road-Class Impedance Multipliers and Topological Modifiers}
\label{tab:road_impedance}
\centering
\footnotesize
\begin{tabular}{lllc}
\hline
\textbf{Hierarchy Category} & \textbf{OSM Classification ($h(e)$)} & \textbf{Modifier Condition} & \textbf{Effective Multiplier ($\mu$)} \\
\hline
\multicolumn{4}{l}{\textit{Part A: Base Road-Class Impedance ($f_{\mathrm{class}}$)}} \\
Arterial Trunk / Highway & \texttt{motorway}, \texttt{trunk} & Standard surface & $3.00\text{--}4.00$ \\
Primary Corridor & \texttt{primary}, \texttt{primary\_link} & Standard surface & $2.00\text{--}2.20$ \\
Secondary Corridor & \texttt{secondary}, \texttt{secondary\_link} & Standard surface & $1.40\text{--}1.50$ \\
Intermediate Collector & \texttt{tertiary}, \texttt{tertiary\_link} & Standard surface & $1.10\text{--}1.15$ \\
Local / Residential & \texttt{residential}, \texttt{unclassified} & Neutral baseline & $1.00$ \\
Permissive Street & \texttt{living\_street}, \texttt{service} & Standard surface & $0.90\text{--}0.95$ \\
\hline
\multicolumn{4}{l}{\textit{Part B: Topological Modifiers}} \\
Grade-Separated Flyover & $\mathcal{H}_{\mathrm{main}}$ on bridge structure & Replaces $f_{\mathrm{class}}$ with $0.80$ & $0.80$ \\
Continuous-Flow Roundabout & All classes with \texttt{junction=roundabout} & Scales base by $\times 0.95$ & $0.95 \cdot f_{\mathrm{class}}$ (down to $0.855$) \\
Theoretical Co-occurrence & $\mathcal{H}_{\mathrm{main}}$ bridge $+$ roundabout & $0.80 \times 0.95$ ($0$ in corpus) & $0.76$ \\
\hline
\end{tabular}
\end{table}
```

---

## 3. Issue 3: Turn Bearing Implementation

### 3.1 Code Inspection of Bearing Calculation
In [`routing/algorithms.py#L63-L76`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L63-L76):
```python
def _bearing_deg(lat1, lng1, lat2, lng2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lng2 - lng1)
    x = math.sin(dlam) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(x, y)) + 360) % 360
```
In [`routing/algorithms.py#L127-L144`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L127-L144):
```python
incoming = _bearing_deg(prev_data["y"], prev_data["x"], current_data["y"], current_data["x"])
outgoing = _bearing_deg(current_data["y"], current_data["x"], next_data["y"], next_data["x"])
difference = abs(incoming - outgoing)
return min(difference, 360.0 - difference)
```

### 3.2 Geometric and Algorithmic Analysis
1. **Incoming Bearing ($\theta_{\text{in}}$):**  
   Computed as `_bearing_deg(lat_u, lng_u, lat_v, lng_v)`.  
   This represents the **initial forward azimuth from node $u$ to node $v$**, evaluated at node $u$ along the great-circle chord connecting $u$ and $v$.  
   It is **NOT** the terminal arrival azimuth at node $v$. (On a spherical geodesic, the forward azimuth varies along the arc from $u$ to $v$).
2. **Intermediate Curve Polyline Geometry:**  
   OpenStreetMap edges often contain an internal `geometry` sequence of shape points along curved roads. The function `_turn_angle` reads **only node coordinates** (`graph.nodes[prev_node]` and `graph.nodes[current_node]`), completely ignoring intermediate polyline vertices.
3. **Outgoing Bearing ($\theta_{\text{out}}$):**  
   Computed as `_bearing_deg(lat_v, lng_v, lat_w, lng_w)`.  
   This represents the **initial forward azimuth from node $v$ to node $w$**, evaluated at node $v$ along the chord connecting $v$ and $w$.
4. **Implications for Angular Deflection Wording:**  
   - We must **never claim** that $\Delta\theta$ represents the "geodesically exact tangent turning angle at intersection $v$."
   - The manuscript must accurately define $\Delta\theta(u, v, w)$ as the angular difference between the **initial forward spherical azimuth of secant chord $(u, v)$** and the **initial forward spherical azimuth of secant chord $(v, w)$**, computed from endpoint coordinates $(\phi, \lambda)$.

---

## 4. Issue 4: Road-Impedance Interpretation and Wording Replacements

The following five phrases in [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) contain unsupported claims or informal teleological assertions:

| # | Current Draft Text (in `paper1_section_III_v1.md`) | Identified Epistemological Defect | Recommended Exact Replacement |
| :---: | :--- | :--- | :--- |
| **1** | *"To model two-wheeler routing preferences across mixed traffic hierarchies..."* (Line 31) | Implies calibrated behavioral choice or psychological preferences. | **"To incorporate vehicle-specific street hierarchy weighting into graph traversal..."** |
| **2** | *"...where base weights $f_{\text{class}}$ (Table I) penalize congested arterials while favoring local streets."* (Line 36) | Asserts dynamic congestion on static OSM road tags without real-time data. | **"...where base weights $f_{\text{class}}$ (Table I) assign higher traversal cost to higher-tier arterial street classes while favoring lower-tier local roads."** |
| **3** | *"...an elevated flyover replaces the arterial multiplier with $0.80$, prioritising grade-separated movement."* (Line 36) | Teleological/policy phrasing ("prioritising"). | **"...an elevated flyover replaces the base arterial multiplier with $0.80$, lowering traversal cost along grade-separated infrastructure."** |
| **4** | *"...penalizing sharp cross-traffic turns and moderate vehicular deflections..."* (Line 29) | Implies directional lane-crossing conflict tracking, which undirected node chords cannot measure. | **"...penalizing sharp angular deflections ($\ge 60.0^\circ$) and moderate course deflections ($30.0^\circ \le \Delta\theta < 60.0^\circ$)..."** |
| **5** | *"...while filtering minor roadway curvature below $30.0^\circ$."* (Line 29) | Implies active curve geometry filtering along curved polylines. | **"...while assigning zero penalty to slight course deviations below $30.0^\circ$."** |

---

## 5. Issue Classification and Recommendations

| Issue ID | Domain | Severity | Recommended Remediation Action |
| :---: | :--- | :---: | :--- |
| **Issue 1** | Graph Type & Parallel Edges | **MAJOR** | Formulate $G = (V, E)$ as simple directed graph where parallel edges are collapsed to minimum impedance $\ell_{\min}(u, v) = \min_k \mu_k \ell_k$; state $|E| = 740,822$ and $|S| = |E|+1 = 740,823$. |
| **Issue 2** | Roundabout Table Structure | **MAJOR** | Restructure Table I into Part A (Base Road Classes) and Part B (Topological Modifiers: Bridge Override $0.80$, Roundabout $\times 0.95$). |
| **Issue 3** | Turn Bearing Interpretation | **MINOR** | Clarify that bearings are chord-based initial forward azimuths computed from node endpoint coordinates, not tangent geodesic junction deflections. |
| **Issue 4** | Road-Impedance Wording | **MINOR** | Replace the 5 identified phrases with objective impedance and deflection descriptions. |

---

## 6. Frozen File Verification

All frozen research assets remain bitwise unmodified:
- `paper1_abstract_v2.md`: Untouched (3,287 bytes).
- `paper1_introduction_v1.md`: Untouched (7,596 bytes).
- `paper1_related_work_v1.md`: Untouched (6,723 bytes).
- `paper1_verified_references.bib`: Untouched (8,817 bytes).
- `core/config.py` & `routing/algorithms.py`: Untouched.
- `bengaluru_graph.pkl`: Untouched.

---

## 7. Stop Condition Enforced

The targeted audit report has been saved to [`paper1_section_III_targeted_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_targeted_audit.md). No manuscript files were modified during this turn. Section IV has not been started. Awaiting research-lead review and formal authorization prior to applying any revisions.
