# Independent Technical Audit: Section III Manuscript (Phase 7.2-U)

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 7.2-U — Independent Section III Manuscript Audit  
**Date:** 2026-11-06  
**Auditor Role:** Independent Technical Reviewer (Formal Post-Revision Verification)  
**Audited Document:** [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (v1.2)  
**Source Evidence Grounding:**
- [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) (Inspected via NetworkX in Phase 7.2-S)
- [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py)
- [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py)
- [`paper1_section_III_targeted_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_targeted_audit.md) (Phase 7.2-S)
- [`phase_7_2_T_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_T_execution_log.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE INDEPENDENT AUDIT COMPLETE**  

---

## 1. Overall Audit Verdict

**VERDICT: CONDITIONALLY APPROVED FOR CANONICAL FREEZE (SUBJECT TO 2 MINOR PRESENTATION FIXES)**

The revised manuscript [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) (v1.2) successfully resolves all mathematical and technical flaws identified during Phase 7.2-S:
1. It rigorously distinguishes the source OpenStreetMap multigraph ($|E_{\text{raw}}| = 744,216$) from the simple directed routing graph ($|E_s| = 740,822$) and establishes exact state cardinality $|S| = |E_s| + 1 = 740,823$.
2. It correctly decouples Table I into Base Road-Class Impedance and Topological Modifiers, eliminating the previous false implication that roundabouts applied only to permissive streets.
3. It accurately defines turn angles as chord-based initial forward azimuth differences without claiming unmeasured tangent geometry or polyline curvature tracking.
4. It purges all unsupported claims of measured congestion, rider preference, cross-traffic conflicts, and safety ratings.
5. Zero critical or major technical errors remain. Two minor presentation issues (equation numbering sequence in reading order and unnumbered display equation labeling) are flagged for pre-freeze resolution.

---

## 2. Systematic Audit Checklist

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                AUDIT CHECKLIST COMPLIANCE SUMMARY                                │
├───────┬────────────────────────────────────────────────────────┬──────────────┬──────────────────┤
│ Item  │ Audit Criteria                                         │ Status       │ Severity Tier    │
├───────┼────────────────────────────────────────────────────────┼──────────────┼──────────────────┤
│ A.1   │ Multigraph vs. Simple Directed Graph Distinction       │ PASS         │ Verified Fact    │
│ A.2   │ Graph Counts Accuracy (744,216 / 740,822 / 3,379)      │ PASS         │ Verified Fact    │
│ A.3   │ Effective Edge Cost Formulation (c_min)                │ PASS         │ Verified Fact    │
│ A.4   │ Implementation Match (two_wheeler_edge_cost min)       │ PASS         │ Verified Fact    │
│ A.5   │ State Space Definition & Cardinality (|S| = 740,823)   │ PASS         │ Verified Fact    │
│ A.6   │ Transition Consistency over E_s                        │ PASS         │ Verified Fact    │
│ A.7   │ Avoidance of Raw Multigraph Records as States          │ PASS         │ Verified Fact    │
├───────┼────────────────────────────────────────────────────────┼──────────────┼──────────────────┤
│ B.1   │ Bearings Identified as Initial Forward Azimuths        │ PASS         │ Verified Fact    │
│ B.2   │ Endpoint-to-Endpoint Chord Specification               │ PASS         │ Verified Fact    │
│ B.3   │ Explicit Exclusion of Polyline Shape Points            │ PASS         │ Verified Fact    │
│ B.4   │ Angular Wraparound & Deflection Formulation            │ PASS         │ Verified Fact    │
│ B.5   │ Discrete Turn Penalty Thresholds (25.0 / 8.0 / 0.0)    │ PASS         │ Verified Fact    │
│ B.6   │ Initial Departure Zero Turn Penalty (Lemma 1)          │ PASS         │ Verified Fact    │
├───────┼────────────────────────────────────────────────────────┼──────────────┼──────────────────┤
│ C.1   │ Base Multipliers Match config.py (0.90 to 4.00)        │ PASS         │ Verified Fact    │
│ C.2   │ Bridge Override Replaces Base Multiplier (0.80)        │ PASS         │ Verified Fact    │
│ C.3   │ Roundabout Modifier Applied Across All Classes (0.95)  │ PASS         │ Verified Fact    │
│ C.4   │ Sequential Execution Order Accurately Stated           │ PASS         │ Verified Fact    │
│ C.5   │ Theoretical 0.76 Combination Documented & Scoped       │ PASS         │ Verified Fact    │
│ C.6   │ Observed Minimum (0.80) Correctly Scoped to Bengaluru  │ PASS         │ Verified Fact    │
│ C.7   │ Table I Decoupled into Base and Modifiers              │ PASS         │ Verified Fact    │
├───────┼────────────────────────────────────────────────────────┼──────────────┼──────────────────┤
│ D.1   │ Single Physical Edge Traversal Accounting              │ PASS         │ Verified Fact    │
│ D.2   │ Single Intermediate Turn Accounting                    │ PASS         │ Verified Fact    │
│ D.3   │ Departure and Arrival Turn Penalties Excluded          │ PASS         │ Verified Fact    │
│ D.4   │ Dimensional Homogeneity ([L] + [L] = [L])              │ PASS         │ Verified Fact    │
│ D.5   │ Path Objective Matches Transition Cost Equation        │ PASS         │ Verified Fact    │
│ D.6   │ All Mathematical Symbols Defined                       │ PASS         │ Verified Fact    │
├───────┼────────────────────────────────────────────────────────┼──────────────┼──────────────────┤
│ E.1   │ No Calibrated Rider Preferences or Utilities Claimed   │ PASS         │ Verified Fact    │
│ E.2   │ No Measured Dynamic Congestion Claimed                 │ PASS         │ Verified Fact    │
│ E.3   │ No Safety or Collision Reduction Claimed               │ PASS         │ Verified Fact    │
│ E.4   │ No Lane-Level Manoeuvre Detection Claimed              │ PASS         │ Verified Fact    │
│ E.5   │ No Exact Road-Centreline Curvature Claimed             │ PASS         │ Verified Fact    │
│ E.6   │ No Universal Graph Guarantees Unsupported by Assumptions│ PASS        │ Verified Fact    │
├───────┼────────────────────────────────────────────────────────┼──────────────┼──────────────────┤
│ F.1   │ Internal Notation Consistency                          │ PASS         │ Verified Fact    │
│ F.2   │ Table Labels and Cross-References                      │ PASS         │ Verified Fact    │
│ F.3   │ Reading-Order Equation Numbering Alignment             │ MINOR ISSUE  │ Presentation     │
│ F.4   │ Unnumbered Display Equation in III-A                   │ MINOR ISSUE  │ Presentation     │
│ F.5   │ Controlled Word Count Expansion (529 words)            │ PASS         │ Acceptable (+12%)│
└───────┴────────────────────────────────────────────────────────┴──────────────┴──────────────────┘
```

---

## 3. Detailed Technical Verification by Checklist Category

### Section A: Graph and Parallel-Edge Projection
1. **Multigraph vs. Simple Directed Graph Distinction:**
   - *Manuscript Text (Line 18):*  
     `"The street network is extracted as a directed multigraph $G_{\text{raw}} = (V, E_{\text{raw}})$ with $|V| = 308,643$ vertices denoting intersections and shape points with coordinates $(\phi_v, \lambda_v)$ and $|E_{\text{raw}}| = 744,216$ directed edge records, wherein $3,379$ ordered node pairs contain parallel edges ($6,773$ records total, up to 4 per pair). Because graph search resolves parallel edges by selecting the minimum-impedance connection, routing operates over the effective simple directed graph $G = (V, E_s)$ containing $|E_s| = 740,822$ distinct adjacent node pairs."`
   - *Implementation Truth:* In [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl), `type(G)` is `MultiDiGraph` with $308,643$ nodes and $744,216$ edge records. The number of distinct ordered pairs $(u, v)$ is exactly $740,822$. Exactly $3,379$ pairs have $> 1$ edge (spanning $6,773$ records; excess is $6,773 - 3,379 = 3,394$).
   - *Reviewer Assessment:* **PASS**. The distinction is mathematically rigorous, physically precise, and fully grounded in the data.
2. **Effective Edge Cost Formulation ($c_{\min}$):**
   - *Manuscript Text (Line 19):*  
     `$$c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} \left[ \mu(u, v, k) \cdot \ell(u, v, k) \right]$$`
   - *Implementation Truth:* Lines 645–655 in [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) execute `min(two_wheeler_edge_cost(data, ...) for data in edge_data.values())`.
   - *Reviewer Assessment:* **PASS**. The mathematical formulation directly captures the code execution.
3. **State Space and Cardinality:**
   - *Manuscript Text (Line 22):*  
     `"The expanded state space is $S = E_s \cup \{(\text{None}, s_0)\}$, yielding an exact state cardinality of $|S| = |E_s| + 1 = 740,823$, distinct from the $744,216$ raw multigraph edge records."`
   - *Implementation Truth:* `two_wheeler_astar` tracks states as 2-tuples `(previous_node, current_node)` without an edge key. Transitions occur between adjacent vertices over $E_s$. The number of reachable state pairs is $|E_s| + 1 = 740,823$.
   - *Reviewer Assessment:* **PASS**. The error present in earlier drafts (claiming $|S| = 744,217$) is completely corrected.

---

### Section B: Turn-Angle Formulation
1. **Initial Forward Azimuths and Endpoint Chords:**
   - *Manuscript Text (Line 24):*  
     `"For an inbound segment $(u, v)$ and outbound segment $(v, w)$ intersecting at vertex $v$, let $\theta(u, v) \in [0^\circ, 360^\circ)$ and $\theta(v, w) \in [0^\circ, 360^\circ)$ denote initial forward azimuths computed from endpoint node coordinates. The angular deflection $\Delta\theta(u, v, w)$ is defined as the smaller angular difference between the initial forward azimuths of the endpoint-to-endpoint chords $(u, v)$ and $(v, w)$: ... Internal roadway polyline shape points are not evaluated."`
   - *Implementation Truth:* `_bearing_deg` in [`routing/algorithms.py#L63-L76`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L63-L76) computes initial spherical forward azimuths using only `graph.nodes[prev_node]` and `graph.nodes[current_node]`. Shape points in `edge_data['geometry']` are ignored.
   - *Reviewer Assessment:* **PASS**. The text eliminates all prior ambiguity and accurately represents the chord-based geometry.
2. **Turn Penalty Assignment & Initial Invariance:**
   - *Manuscript Text (Lines 27–32):*  
     Equation (2) assigns $25.0$ for $\Delta\theta \ge 60.0^\circ$, $8.0$ for $30.0^\circ \le \Delta\theta < 60.0^\circ$, and $0.0$ for $< 30.0^\circ$ or $u = \text{None}$. Line 32 confirms $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$.
   - *Implementation Truth:* Matches lines 37–42 and 146–167 of [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py).
   - *Reviewer Assessment:* **PASS**.

---

### Section C: Impedance Model and Table I
1. **Table I Decoupled Structure:**
   - Table I is cleanly separated into Part A (Base Road Classes) and Part B (Topological Modifiers).
   - In Part B, the continuous-flow roundabout modifier is explicitly listed as:  
     `"All classes with junction=roundabout | Scales base by x0.95 | 0.95 * f_class (down to 0.855)"`.
   - The arterial bridge override is listed as:  
     `"H_main on bridge structure | Replaces f_class with 0.80 | 0.80"`.
   - The theoretical co-occurrence is listed as:  
     `"H_main bridge + roundabout | 0.80 x 0.95 (0 in corpus) | 0.76"`.
   - *Reviewer Assessment:* **PASS**. The misleading permissive-only representation from v1.0 has been fully eliminated.
2. **Multiplier Lower Bound and Scoping:**
   - *Manuscript Text (Line 39):*  
     `"Across the Bengaluru graph, however, zero qualifying bridge-roundabout co-occurrences exist among 744,216 directed edges, and the minimum observed multiplier is strictly $0.80$. The condition $\mu(e) \ge 0.80$ is a dataset-verified condition for the evaluated network and a prerequisite for the theoretical guarantee in Section~IV, rather than a universal property of arbitrary graphs."`
   - *Reviewer Assessment:* **PASS**. Accurately scopes the 0.80 lower bound to the experimental corpus and theoretical assumption, without making invalid universal civil engineering claims.

---

### Section D: Objective Function and Dimensional Consistency
1. **Transition Cost and Path Accumulation:**
   - *Manuscript Text (Lines 42–46):*  
     $$\begin{aligned}
     c(s, s') &= c_{\min}(v, w) + P_{\text{turn}}(u, v, w) \\
     C(P) &= \sum_{i=1}^k c_{\min}(v_{i-1}, v_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})
     \end{aligned} \tag{3}$$
   - *Reviewer Assessment:* **PASS**.
     - Edge traversal $c_{\min}(v_{i-1}, v_i)$ is evaluated across $i = 1, \dots, k$ (each physical edge in $P$ charged exactly once).
     - Intermediate turns $P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$ are evaluated across $i = 1, \dots, k-1$ (each internal intersection turn charged exactly once).
     - Origin departure ($u = \text{None}$) incurs zero turn penalty.
     - Destination arrival ($v_k = t$) halts immediately without exit turn penalty.
     - Dimensional homogeneity: Physical distance $D(P)$ in metres ($m$); traversal impedance $C(P)$ in effective metres ($m$).

---

### Section E: Claim Boundaries
1. **Purging of Prohibited Claims:**
   - *Rider Preferences:* Line 34 uses `"To incorporate vehicle-specific street hierarchy weighting into graph traversal..."`. Zero claims of calibrated utility.
   - *Measured Congestion:* Line 20 uses `"rather than measuring travel time or congestion"`, and Line 39 uses `"assign higher configured traversal costs to arterial corridors while favoring lower-tier local streets"`. Zero claims of measured traffic congestion.
   - *Safety / Accidents:* Line 32 uses `"penalize geometric course deflection rather than detecting cross-traffic conflicts or modelling collision risks"`. Zero safety claims.
   - *Curvature Filtering:* Line 32 uses `"while assigning zero penalty to slight course deviations below 30.0°"`. Zero curvature filtering claims.
   - *Reviewer Assessment:* **PASS**. 100% compliant with research boundaries.

---

## 4. Minor Identified Issues and Recommended Adjustments

During independent review, two minor presentation issues were identified. Neither affects mathematical validity or empirical truth, but resolving them will ensure flawless IEEE typesetting:

### Issue M-1: Equation Numbering Order in Physical Reading Sequence
- **Exact Quotation:**  
  In Subsection III-C (Line 27):  
  `$$P_{\text{turn}}(u, v, w) = \dots \tag{2}$$`  
  In Subsection III-D (Line 35):  
  `$$\mu(e) = \dots \tag{1}$$`  
  In Subsection III-D (Line 42):  
  `$$\begin{aligned} c(s, s') &= \dots \\ C(P) &= \dots \end{aligned} \tag{3}$$`
- **Reviewer Finding:**  
  Equation (2) physically appears in the text **before** Equation (1). In standard IEEE conference layout, equations must be numbered monotonically in the order of their physical appearance. If an automated LaTeX compiler renders `\begin{equation}`, it will automatically number $P_{\text{turn}}$ as (1) and $\mu(e)$ as (2).
- **Exact Proposed Correction:**  
  Re-number the display equations monotonically to reflect their physical order of appearance:
  - Subsection III-C (Turn Penalty): Label as **Equation (1)**.
  - Subsection III-D (Road Multiplier $\mu(e)$): Label as **Equation (2)**.
  - Subsection III-D (Transition & Path Objective): Label as **Equation (3)**.  
  *(Alternatively, move the definition of $\mu(e)$ before $P_{\text{turn}}$ if the authoring team prefers keeping $\mu(e)$ as Eq. 1).*

### Issue M-2: Labeling of the $c_{\min}$ Display Equation in Subsection III-A
- **Exact Quotation (Line 19):**  
  `$$c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} \left[ \mu(u, v, k) \cdot \ell(u, v, k) \right]$$`
- **Reviewer Finding:**  
  This equation is displayed as an unnumbered equation (`$$...$$`). In IEEE conference format, key display equations are typically numbered if referenced later (e.g., in Section IV). If it remains unnumbered, it should be verified that LaTeX does not auto-increment the equation counter.
- **Exact Proposed Correction:**  
  Either keep it explicitly unnumbered via `\begin{equation*}` or inline it into the paragraph text:  
  `"...effective traversal cost is $c_{\min}(u, v) = \min_{k \in \mathcal{K}(u, v)} [\mu(u, v, k) \ell(u, v, k)]$, where $\mathcal{K}(u, v)$ is..."`  
  Inlining this formula saves 2 vertical lines of display space in Column 1.

---

## 5. Word Count and Typography Assessment

- **Subsection III-A:** 128 words
- **Subsection III-B:** 113 words
- **Subsection III-C:** 114 words
- **Subsection III-D:** 174 words
- **Total Section III Body Text:** **529 words** (Excluding LaTeX Table code and display equations).
- **Comparison to Blueprint:** The original blueprint budgeted 470 words. The 529-word count represents a $+59$-word (+12.5%) expansion.
- **Page Budget Impact:** In standard 10pt IEEE two-column format, 529 words require $\approx 62\text{ lines}$. With equations and Table I, Section III occupies $\approx 1.35\text{ columns}$. Because Section II ends in Column 1 of Page 2, Section III occupies the bottom of Column 1 ($\approx 15\text{ lines}$) and the entirety of Column 2 ($\approx 60\text{ lines}$), plus float placement. It terminates on Page 2 and leaves Page 3 entirely clear for Section IV.
- **Reviewer Assessment:** **PASS**. The expansion is justified by the necessary mathematical disambiguation and fits within the page budget.

---

## 6. Verification of Read-Only Artifacts

The reviewer confirms that all protected files remain bitwise intact:
- `paper1_abstract_v2.md`: Untouched (3,287 bytes).
- `paper1_introduction_v1.md`: Untouched (7,596 bytes).
- `paper1_related_work_v1.md`: Untouched (6,723 bytes).
- `paper1_verified_references.bib`: Untouched (8,817 bytes).
- `core/config.py` & `routing/algorithms.py`: Untouched.
- `bengaluru_graph.pkl`: Untouched.

---

## 7. Recommendation to Research Lead

The independent audit confirms that Section III is mathematically rigorous, code-faithful, and free of over-claims.
- **Recommendation:** Approve Section III subject to applying the trivial monotonic equation numbering fix (Issue M-1).
- **Next Step:** Authorize Phase 7.3 (Section III Canonical Assembly & Freeze) once Issue M-1 is resolved, followed by Phase 8 (Section IV Planning).
