# Phase 7.2-W Freeze Log: Section III Canonical Freeze

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 7.2-W — Section III Canonical Freeze  
**Date:** 2026-11-06  
**Document:** [`phase_7_2_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_freeze_log.md)  
**Canonical Frozen Manuscript:** [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (Version 1.3)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **SECTION III CANONICAL MANUSCRIPT FROZEN (APPROVED BY RESEARCH LEAD)**  

---

## 1. Formal Freeze Declaration

By explicit decision of the Research Lead, Section III of Paper 1 (*Problem Formulation and Configured Road Impedance*) is hereby declared **CANONICALLY FROZEN** at **Version 1.3**.

The frozen manuscript is located at:
> [`research/paper1_manuscript/paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md)

Under research governance protocols, no further edits, refactorings, or modifications may be applied to this file without explicit written authorization from the Research Lead.

---

## 2. Completed Audit and Correction Lifecycle

The final frozen text represents the convergence of seven formal review and verification phases:

1. **Phase 7.1 (Structural & Notation Planning):** Established the four-subsection modular blueprint, mathematical notation map, and implementation evidence map ([`phase_7_1_planning_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_1_planning_audit.md)).
2. **Phase 7.1-R (Multiplier Lower-Bound Audit):** Corrected the mathematical claim regarding modifier exclusivity, separating the theoretical combination ($0.80 \times 0.95 = 0.76$) from the dataset-verified empirical minimum ($\mu(e) \ge 0.80$).
3. **Phase 7.2 (Initial Prose Drafting):** Drafted the initial manuscript prose conforming to the 470-word allocation ([`phase_7_2_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_execution_log.md)).
4. **Phase 7.2-S (Targeted Implementation Deep-Dive):** Conducted rigorous graph, bearing, modifier, and state-cardinality audits against [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) and [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) ([`paper1_section_III_targeted_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_targeted_audit.md)).
5. **Phase 7.2-T (Technical Corrections):** Implemented all technical corrections, including multigraph projection ($G_{\text{raw}} \to G$), exact state cardinality ($|S| = |E_s| + 1 = 740,823$), chord-based forward azimuth definition, modifier decoupling in Table I, and complete purging of subjective over-claims ([`phase_7_2_T_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_T_execution_log.md)).
6. **Phase 7.2-U (Independent Technical Review):** Executed formal post-revision audit, verifying 100% mathematical and code consistency while identifying two minor presentation adjustments ([`paper1_section_III_independent_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_independent_audit.md)).
7. **Phase 7.2-V (Final Presentation Polish):** Re-enumerated display equations monotonically in physical reading order and inlined the $c_{\min}$ traversal cost formula ([`phase_7_2_V_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_V_execution_log.md)).
8. **Phase 7.2-W (Canonical Freeze):** Formal lockdown of Section III v1.3.

---

## 3. Verified Manuscript Properties (Version 1.3)

### 3.1 Body Word Count and Page Budget
- **Counting Convention:** Standard academic prose count (body text words excluding LaTeX table code, float wrappers, and display equations).
- **Subsection III-A (Directed Road-Network and Routing Problem):** 128 words
- **Subsection III-B (Edge-Based State Representation):** 113 words
- **Subsection III-C (Angular Turn-Deflection Model):** 114 words
- **Subsection III-D (Configured Road-Impedance Model and Objective Function):** 174 words
- **Total Section III Body Text:** **529 words**
- **Budget Compliance:** Modest $+59$-word (+12.5%) expansion over the 470-word blueprint target. In standard IEEE two-column 10pt format, 529 words consume $\approx 62$ lines of text ($\approx 1.35$ columns including display equations and Table I). It occupies the lower portion of Page 2, Column 1 and the entirety of Page 2, Column 2, terminating cleanly at the Page 2 boundary and leaving Page 3 completely vacant for Section IV.

### 3.2 Monotonic Equation Sequence
- **Equation (1) (Subsection III-C):** Discrete piecewise turn penalty function:
  $$P_{\text{turn}}(u, v, w) = \begin{cases} 
  25.0 & \text{if } u \ne \text{None} \text{ and } \Delta\theta(u, v, w) \ge 60.0^\circ \\ 
  8.0 & \text{if } u \ne \text{None} \text{ and } 30.0^\circ \le \Delta\theta(u, v, w) < 60.0^\circ \\ 
  0.0 & \text{if } u = \text{None} \text{ or } \Delta\theta(u, v, w) < 30.0^\circ 
  \end{cases} \tag{1}$$
- **Equation (2) (Subsection III-D):** Composite road-class impedance multiplier:
  $$\mu(e) = \begin{cases} 
  0.80 \cdot m_{\text{rbt}}(e) & \text{if } \text{bridge}(e) \in \mathcal{B}^+ \text{ and } h(e) \in \mathcal{H}_{\text{main}} \\ 
  f_{\text{class}}(h(e)) \cdot m_{\text{rbt}}(e) & \text{otherwise} 
  \end{cases} \tag{2}$$
- **Equation (3) (Subsection III-D):** Edge-state transition cost and accumulated path objective:
  $$\begin{aligned}
  c(s, s') &= c_{\min}(v, w) + P_{\text{turn}}(u, v, w) \\
  C(P) &= \sum_{i=1}^k c_{\min}(v_{i-1}, v_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})
  \end{aligned} \tag{3}$$

### 3.3 Resolved Implementation and Mathematical Flaws
1. **Multigraph Projection & Edge Cost:** Clarified that raw source graph $G_{\text{raw}} = (V, E_{\text{raw}})$ contains $|V| = 308,643$ nodes and $|E_{\text{raw}}| = 744,216$ edge records. Exactly 3,379 node pairs contain parallel edges (6,773 records). Routing operates over simple directed graph $G = (V, E_s)$ with $|E_s| = 740,822$ distinct adjacent node pairs by inlining traversal cost $c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} \left[ \mu(u, v, k) \cdot \ell(u, v, k) \right]$.
2. **State Space Cardinality:** Directed edge states $s = (u, v)$ represent arrival at vertex $v$ via node $u$ without edge keys. Initial root state $s_0^{\text{state}} = (\text{None}, s_0)$ represents origin departure. The state space $S = E_s \cup \{(\text{None}, s_0)\}$ has exact cardinality $|S| = |E_s| + 1 = 740,823$.
3. **Turn-Angle Formulation:** Defined $\Delta\theta(u, v, w)$ strictly as the smaller angular difference between initial forward azimuths $\theta(u, v), \theta(v, w) \in [0^\circ, 360^\circ)$ of endpoint-to-endpoint chords $(u, v)$ and $(v, w)$ computed from coordinate tuples $(\phi, \lambda)$. Explicitly stated that intermediate polyline shape points are not evaluated.
4. **Table I Decoupling & Modifier Scope:** Table I separates base hierarchy multipliers $f_{\text{class}}$ (Part A: 0.90 to 4.00) from topological modifiers (Part B). Bridge override replaces $f_{\text{class}}$ with $0.80$ on qualifying arterials ($\mathcal{H}_{\text{main}}$). Roundabout modifier scales base/override by $\times 0.95$ across all classes carrying `junction=roundabout`.
5. **Sequential Evaluation & Lower Bound:** Sequentially evaluating bridge override followed by roundabout yields theoretical minimum $0.80 \times 0.95 = 0.76$. Across the Bengaluru graph, zero such co-occurrences exist among 744,216 edges, establishing $\mu(e) \ge 0.80$ as a dataset-verified empirical condition for Bengaluru.
6. **Dimensional Consistency:** Verified that physical length $D(P) = \sum \ell(e_i)$ is in physical metres ($m$), while routing objective $C(P)$ is in effective metres ($m$). Traversed physical edges and intermediate turns are charged exactly once. Initial departure and destination arrival incur zero turn penalty.
7. **Purged Over-Claims:** Zero claims of calibrated rider preference utilities, measured dynamic traffic congestion, accident or safety risk models, lane-level manoeuvre tracking, or ungrounded universal graph guarantees.

---

## 4. Documented Research Boundaries and Limitations

To ensure absolute scientific integrity in subsequent sections (especially Section IV and Section V), the following boundaries established in Section III v1.3 are formally recorded:

1. **Empirical Multiplier Lower Bound:** The lower bound $\mu(e) \ge 0.80$ is an empirically verified property of the extracted OpenStreetMap dataset for Bengaluru (0 co-occurring bridge-roundabouts in 744,216 records). In theoretical proofs in Section IV, this condition must be explicitly stated as an assumption/premise rather than an inherent topological axiom of arbitrary road graphs.
2. **Endpoint Secant Chord Approximation:** Turn penalties are determined from the secant chord between intersection endpoints. Roadways exhibiting continuous curved geometry between intersections do not incur internal turning penalties.
3. **Parallel Edge Representation:** In the routing graph, parallel connections between identical ordered node pairs $(u, v)$ are collapsed to their minimum complete impedance representative $c_{\min}(u, v)$. Routing does not retain sub-optimal parallel edges as distinct search alternatives.

---

## 5. Frozen Asset Invariance Audit

The following authoritative project artifacts were audited and confirmed bitwise unmodified:
- **Frozen Abstract (v2.0):** [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md)
- **Frozen Section I (v1.0):** [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md)
- **Frozen Section II (v1.0):** [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md)
- **Frozen Bibliography:** [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_verified_references.bib)
- **Frozen Audit Reports:** [`paper1_section_III_independent_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_independent_audit.md)
- **Core Implementation:** [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py)
- **Routing Implementation:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py)
- **Serialized Graph Dataset:** [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl)

---

## 6. Next Steps

With Section III canonically frozen:
- Section III drafting and refinement lifecycle is **CLOSED**.
- **Awaiting Research Lead Directive** to initiate **Phase 8.1: Section IV Structural Planning and Mathematical Admissibility Evidence Map** (A* Search on Edge-Expanded State Space and Conditional Admissibility Guarantees).
