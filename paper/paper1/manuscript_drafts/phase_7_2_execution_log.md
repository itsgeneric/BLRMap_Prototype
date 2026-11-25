# Phase 7.2 Execution Log: Section III Manuscript Prose Drafting

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 7.2 — Section III Manuscript Prose Drafting  
**Date:** 2026-11-06  
**Document:** [`phase_7_2_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_execution_log.md)  
**Parent Blueprint:** [`paper1_final_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_blueprint_v1.md)  
**Parent Page Budget:** [`paper1_final_page_budget_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_blueprint/paper1_final_page_budget_v1.md)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 7.2 EXECUTION COMPLETE (AWAITING LEAD APPROVAL)**  

---

## 1. Overview and Operational Directives

Phase 7.2 drafted the complete manuscript text for **Section III: Problem Formulation and Configured Road Impedance** of Paper 1.

The drafting was executed strictly against:
1. Approved Outline: [`paper1_section_III_outline_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_outline_v1.md) (v1.1)
2. Equation & Notation Map: [`paper1_section_III_equation_and_notation_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_equation_and_notation_map_v1.md) (v1.1)
3. Code Evidence Map: [`paper1_section_III_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_evidence_map_v1.md) (v1.1)
4. Planning Audit: [`phase_7_1_planning_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_1_planning_audit.md) (v1.1)

---

## 2. Subsection-by-Subsection Execution Details

### Subsection III-A: Directed Road-Network and Routing Problem
- **Drafted Text:** 110 words. Target: ~110 words.
- **Key Concepts Incorporated:**
  - Directed multigraph $G = (V, E)$ with intersection coordinates $(\phi_v, \lambda_v)$.
  - Edge attributes: physical length $\ell(e) > 0$ in physical metres, OpenStreetMap highway tag $h(e)$, bridge indicator, junction tag.
  - Origin–destination routing problem from $s_0 \in V$ to $t \in V$ discovering directed path $P = \langle e_1, \dots, e_k \rangle$.
  - Explicit distinction between physical route distance $D(P) = \sum \ell(e_i)$ in physical metres and accumulated traversal impedance $C(P)$ in effective metres.
  - Guardrail: Clarified that $C(P)$ is an impedance objective penalizing turning conflicts and unsuitable street classes, not measured physical travel time or dynamic queue delay.

### Subsection III-B: Edge-Based State Representation
- **Drafted Text:** 93 words. Target: ~100 words.
- **Key Concepts Incorporated:**
  - Non-Markovian nature of turning maneuvers on standard vertex space $V$.
  - Preservation of optimal substructure without materializing a full line graph.
  - Directed edge state $s = (u, v) \in E$, representing arrival at node $v$ via predecessor segment $(u, v)$.
  - Synthetic initial root state $s_0^{\text{state}} = (\text{None}, s_0)$ modeling origin departure.
  - State space cardinality $|S| = |E| + 1$.
  - Valid transition: directed state transition $s = (u, v) \to s' = (v, w)$ for $(v, w) \in E$.

### Subsection III-C: Angular Turn-Deflection Model
- **Drafted Text:** 101 words. Target: ~110 words.
- **Key Concepts Incorporated:**
  - Incoming vector $(u, v)$ and outgoing vector $(v, w)$ at vertex $v$.
  - Forward spherical azimuth bearings $\theta(u, v)$ and $\theta(v, w)$ in $[0^\circ, 360^\circ)$.
  - Angular deflection $\Delta\theta(u, v, w) = \min(|\theta(u, v) - \theta(v, w)|, \; 360^\circ - |\theta(u, v) - \theta(v, w)|) \in [0^\circ, 180^\circ]$.
  - **Display Equation (2):** Piecewise discrete penalty function assigning $25.0\text{ m}$ for sharp turns ($\ge 60.0^\circ$), $8.0\text{ m}$ for moderate turns ($\ge 30.0^\circ, < 60.0^\circ$), and $0.0\text{ m}$ otherwise.
  - Initial departure invariance (Lemma 1): $P_{\text{turn}}(\text{None}, s_0, w) = 0.0$ by definition.
  - Guardrail: Constants described as geometric maneuver friction rather than collision probabilities or accident risk ratings.

### Subsection III-D: Configured Road-Impedance Model and Objective Function
- **Drafted Text:** 163 words. Target: ~150 words.
- **Key Concepts Incorporated:**
  - **Display Equation (1):** Multiplier $\mu(e)$ incorporating base highway weights $f_{\text{class}}$, bridge override, and roundabout factor $m_{\text{rbt}}$.
  - Grade-separated arterial flyover override: replaces the base arterial penalty with $0.80$ on qualifying roads ($h \in \mathcal{H}_{\text{main}}$).
  - Roundabout factor: $0.95\times$ applied sequentially after bridge check.
  - Multiplier lower-bound facts:
    1) Roundabout multiplier (0.95) applied sequentially after bridge override.
    2) Qualifying bridge edge with roundabout tag evaluates to $0.80 \times 0.95 = 0.76$.
    3) Bengaluru graph has zero qualifying bridge-roundabout co-occurrences among 744,216 directed edges.
    4) Minimum observed multiplier is strictly 0.80.
    5) $\mu(e) \ge 0.80$ is framed as a dataset-verified condition for the Bengaluru network and a required condition for Section IV theoretical guarantees, not an unconditional property of arbitrary graphs.
  - **Display Equation (3):** State transition cost $c(s, s') = \mu(v, w)\ell(v, w) + P_{\text{turn}}(u, v, w)$ and path objective $C(P) = \sum_{i=1}^k \mu(e_i)\ell(e_i) + \sum_{i=1}^{k-1} P_{\text{turn}}(v_{i-1}, v_i, v_{i+1})$.
  - Objective accounting: Charges each physical edge $e_i$ and each intermediate intersection turn exactly once; initial departure and destination termination contribute zero turn penalty.
  - **Table I Float:** Tabular specification of configured road-class multipliers matching `core/config.py`.

---

## 3. Code Traceability Matrix

| Section III Element | File and Line References | Verification Notes |
| :--- | :--- | :--- |
| $\ell(e)$ extraction | `routing/algorithms.py:274, 421, 632` | `length = float(edge_data.get("length", 1.0))` |
| Highway tag $h(e)$ | `routing/algorithms.py:276-283` | `hw = edge_data.get("highway", "unclassified")` |
| Road penalties | `core/config.py:61-77` | `TWO_WHEELER_ROAD_PENALTIES` map |
| Bridge override | `routing/algorithms.py:309-311` | `penalty = 0.8` (replaces arterial penalty) |
| Roundabout factor | `routing/algorithms.py:326-331` | `penalty *= 0.95` (applied sequentially) |
| Forward azimuth $\theta$ | `routing/algorithms.py:63-76` | `_bearing_deg(lat1, lng1, lat2, lng2)` |
| Turn deflection $\Delta\theta$ | `routing/algorithms.py:110-144` | `_turn_angle(graph, prev, curr, next)` |
| Turn penalties | `routing/algorithms.py:37-42, 146-167` | $25.0$ for $\ge 60^\circ$, $8.0$ for $\ge 30^\circ$, $0.0$ for $< 30^\circ$ or $u = \text{None}$ |
| State representation | `routing/algorithms.py:482-487, 674-677` | `(prev_node, curr_node)` |
| Initial state | `routing/algorithms.py:375-378, 522-525` | `(None, start_node)` |
| Destination break | `routing/algorithms.py:402, 566` | `if current_node == end_node:` halts search |
| Transition cost sum | `routing/algorithms.py:435, 668-672` | `new_cost = current_cost + edge_cost + turn_cost` |

---

## 4. Frozen File Verification

Timestamps and file byte sizes confirm zero drift on all frozen assets:
- `paper1_abstract_v2.md`: Untouched (3,287 bytes, Last modified 21:28).
- `paper1_introduction_v1.md`: Untouched (7,596 bytes, Last modified 23:04).
- `paper1_related_work_v1.md`: Untouched (6,723 bytes, Last modified 00:46).
- `paper1_verified_references.bib`: Untouched (8,817 bytes, Last modified 20:10).

---

## 5. Mandatory Stop Enforced

Phase 7.2 deliverables are complete:
- Manuscript draft: [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md)
- Draft audit: [`paper1_section_III_draft_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_draft_audit.md)
- Execution log: [`phase_7_2_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_execution_log.md)

No drafting of Section IV has been conducted. Awaiting research-lead review and formal authorization.
