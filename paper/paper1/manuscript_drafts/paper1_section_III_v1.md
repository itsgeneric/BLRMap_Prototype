# Section III: Problem Formulation and Configured Road Impedance (v1.3)

**Document:** [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md)  
**Target Manuscript:** Paper 1: Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Parent Outline:** [`paper1_section_III_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_outline_v1.md) (v1.1)  
**Parent Equation Map:** [`paper1_section_III_equation_and_notation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_equation_and_notation_map_v1.md) (v1.1)  
**Parent Evidence Map:** [`paper1_section_III_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_evidence_map_v1.md) (v1.1)  
**Targeted Audit Reference:** [`paper1_section_III_targeted_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_targeted_audit.md) (Phase 7.2-S)  
**Independent Audit Reference:** [`paper1_section_III_independent_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_independent_audit.md) (Phase 7.2-U)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 7.2-V REVISED DRAFT COMPLETE (AWAITING LEAD APPROVAL)**  
**Effective Date:** 2026-11-06  

---

## Section III: Problem Formulation and Configured Road Impedance

\noindent\textbf{Directed Road-Network and Routing Problem:} The street network is extracted as a directed multigraph $G_{\text{raw}} = (V, E_{\text{raw}})$ with $|V| = 308,643$ vertices denoting intersections and shape points with coordinates $(\phi_v, \lambda_v)$ and $|E_{\text{raw}}| = 744,216$ directed edge records, wherein $3,379$ ordered node pairs contain parallel edges ($6,773$ records total, up to 4 per pair). Because graph search resolves parallel edges by selecting the minimum-impedance connection, routing operates over the effective simple directed graph $G = (V, E_s)$ containing $|E_s| = 740,822$ distinct adjacent node pairs. For each pair $(u, v) \in E_s$, effective traversal cost is $c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} \left[ \mu(u, v, k) \cdot \ell(u, v, k) \right]$, where $\mathcal{K}(u, v)$ is the parallel edge key set, $\ell(u, v, k) > 0$ is surveyed length in metres, and $\mu$ is the composite road-class multiplier. Given origin $s_0 \in V$ and destination $t \in V$, the problem discovers a directed path $P = \langle e_1, \dots, e_k \rangle$ over $E_s$. Physical distance is $D(P) = \sum_{i=1}^k \ell(e_i)$ in physical metres, whereas routing minimizes traversal impedance $C(P)$ in effective metres, reflecting vehicle-specific hierarchy weighting and turn resistance rather than measuring travel time or congestion.

\noindent\textbf{Edge-Based State Representation:} Because turning penalties depend on the approach trajectory, edge transition costs cannot be evaluated as memoryless functions over single vertices. To preserve optimal substructure without materializing a full line graph, the search space is formulated over directed edge states $s = (u, v) \in E_s$, representing arrival at vertex $v$ via predecessor vertex $u$. The state representation contains no edge key, as parallel connections are resolved by the minimum-impedance representative $c_{\min}(u, v)$. Departure from origin intersection $s_0$ is modeled by a synthetic initial state $s_0^{\text{state}} = (\text{None}, s_0)$. The expanded state space is $S = E_s \cup \{(\text{None}, s_0)\}$, yielding an exact state cardinality of $|S| = |E_s| + 1 = 740,823$, distinct from the $744,216$ raw multigraph edge records. A valid transition from state $s = (u, v)$ to state $s' = (v', w)$ requires $v' = v$ and $(v, w) \in E_s$.

\noindent\textbf{Angular Turn-Deflection Model:} For an inbound segment $(u, v)$ and outbound segment $(v, w)$ intersecting at vertex $v$, let $\theta(u, v) \in [0^\circ, 360^\circ)$ and $\theta(v, w) \in [0^\circ, 360^\circ)$ denote initial forward azimuths computed from endpoint node coordinates. The angular deflection $\Delta\theta(u, v, w)$ is defined as the smaller angular difference between the initial forward azimuths of the endpoint-to-endpoint chords $(u, v)$ and $(v, w)$:
$$\Delta\theta(u, v, w) = \min\left(|\theta(u, v) - \theta(v, w)|, \; 360^\circ - |\theta(u, v) - \theta(v, w)|\right) \in [0^\circ, 180^\circ]$$
Internal roadway polyline shape points are not evaluated. Turning penalties are assigned by a discrete piecewise function:
$$P_{\text{turn}}(u, v, w) = \begin{cases} 
25.0 & \text{if } u \ne \text{None} \text{ and } \Delta\theta(u, v, w) \ge 60.0^\circ \\ 
8.0 & \text{if } u \ne \text{None} \text{ and } 30.0^\circ \le \Delta\theta(u, v, w) < 60.0^\circ \\ 
0.0 & \text{if } u = \text{None} \text{ or } \Delta\theta(u, v, w) < 30.0^\circ 
\end{cases} \tag{1}$$
The penalty constants $25.0$ and $8.0$ are expressed in effective-distance metres, penalizing sharp angular deflections ($\ge 60.0^\circ$) and moderate course deflections ($30.0^\circ \le \Delta\theta < 60.0^\circ$) while assigning zero penalty to slight course deviations below $30.0^\circ$. By definition, departure from the origin satisfies $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$ for any outbound edge $(s_0, w) \in E_s$. These discrete costs penalize geometric course deflection rather than detecting cross-traffic conflicts or modelling collision risks.

\noindent\textbf{Configured Road-Impedance Model and Objective Function:} To incorporate vehicle-specific street hierarchy weighting into graph traversal, edge segments receive a composite multiplier $\mu(e)$:
$$\mu(e) = \begin{cases} 
0.80 \cdot m_{\text{rbt}}(e) & \text{if } \text{bridge}(e) \in \mathcal{B}^+ \text{ and } h(e) \in \mathcal{H}_{\text{main}} \\ 
f_{\text{class}}(h(e)) \cdot m_{\text{rbt}}(e) & \text{otherwise} 
\end{cases} \tag{2}$$
where $\mathcal{B}^+$ denotes affirmative bridge tags, $\mathcal{H}_{\text{main}}$ denotes qualifying main roads, and $m_{\text{rbt}}(e) = 0.95$ if $\text{junction}(e) = \text{"roundabout"}$ (otherwise $1.0$). Base weights $f_{\text{class}}$ (Table~I, Part~A) assign higher configured traversal costs to arterial corridors while favoring lower-tier local streets. On qualifying arterials, an elevated flyover replaces the base multiplier with $0.80$, lowering configured traversal cost along grade-separated infrastructure (Table~I, Part~B). The roundabout modifier scales the applicable post-bridge or base multiplier by $0.95$. In implementation, the roundabout factor is evaluated sequentially after the bridge check, meaning co-occurring tags would evaluate to $0.80 \times 0.95 = 0.76$. Across the Bengaluru graph, however, zero qualifying bridge-roundabout co-occurrences exist among 744,216 directed edges, and the minimum observed multiplier is strictly $0.80$. The condition $\mu(e) \ge 0.80$ is a dataset-verified condition for the evaluated network and a prerequisite for the theoretical guarantee in Section~IV, rather than a universal property of arbitrary graphs.

For state transition $s = (u, v)$ to $s' = (v, w)$ over $E_s$, the traversal cost and path objective are:
$$\begin{aligned}
c(s, s') &= c_{\min}(v, w) + P_{\text{turn}}(u, v, w) \\
C(P) &= \sum_{i=1}^k c_{\min}(v_{i-1}, v_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})
\end{aligned} \tag{3}$$
The objective $C(P)$ is expressed in effective metres, charging each traversed physical edge $e_i \in E_s$ exactly once via its minimum-impedance representative $c_{\min}$ and each intermediate intersection turn exactly once, with zero turn penalty at initial departure and destination termination.

---

## Table I: Configured Road-Class Impedance Multipliers and Topological Modifiers

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

## Section III Word Count Breakdown

| Subsection | Target Budget | Revised Actual Words | Variance | Status |
| :--- | :---: | :---: | :---: | :---: |
| **III-A. Directed Road-Network and Routing Problem** | ~110 words | **128 words** | $+18\text{ words}$ ($+16.4\%$) | **ACCEPTABLE (Graph Definition)** |
| **III-B. Edge-Based State Representation** | ~100 words | **113 words** | $+13\text{ words}$ ($+13.0\%$) | **ACCEPTABLE (Cardinality Definition)** |
| **III-C. Angular Turn-Deflection Model** | ~110 words | **114 words** | $+4\text{ words}$ ($+3.6\%$) | **EXACT FIT** |
| **III-D. Configured Road-Impedance Model and Objective Function** | ~150 words | **174 words** | $+24\text{ words}$ ($+16.0\%$) | **ACCEPTABLE (Modifier Disentanglement)** |
| **Total Section III Body Text** | **~470 words** | **529 words** | $\mathbf{+59\text{ words}}$ ($\mathbf{+12.5\%}$) | **CONTROLLED EXPANSION** |
