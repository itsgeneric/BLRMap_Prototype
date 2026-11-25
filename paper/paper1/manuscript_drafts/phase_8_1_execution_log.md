# Phase 8.1 Execution Log: Section IV Structural Planning and Mathematical Evidence Map

**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks (Paper 1)  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1 — Section IV Structural Planning and Mathematical Admissibility Evidence Map  
**Date:** 2026-11-06  
**Document:** [`phase_8_1_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_execution_log.md)  
**Role:** Research Algorithms Engineer and Mathematical Proof Auditor  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md), [`humanizer`](file:///C:/Users/comps/.gemini/config/skills/humanizer/SKILL.md)  
**Status:** **PHASE 8.1 COMPLETE (INVESTIGATION & PLANNING DELIVERABLES READY FOR LEAD REVIEW)**

---

## 1. Executive Summary and Operational Directives

Phase 8.1 was executed under strict read-only audit and planning protocols. The objective was to prepare a mathematically rigorous structural plan, codebase-grounded implementation reconstruction, and evidence map for:
> **Section IV: Proposed Turn-Aware Routing Algorithm, Correctness and Complexity Analysis**

All four mandatory deliverables have been authored with complete fidelity to the frozen codebase, empirical graph data, and Section III definitions:
1. [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)
2. [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md)
3. [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md)
4. [`phase_8_1_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_execution_log.md)

Strict stop conditions have been enforced: zero manuscript prose has been drafted in this phase.

---

## 2. Authoritative Inputs Inspected and Verified

| Input Category | File Path | Status / Checksum Verification |
| :--- | :--- | :---: |
| **Frozen Abstract** | [`research/paper1_manuscript/paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | FROZEN (v2.0, 208 words) — UNTOUCHED |
| **Frozen Introduction** | [`research/paper1_manuscript/paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | FROZEN (v1.0, 468 words) — UNTOUCHED |
| **Frozen Related Work** | [`research/paper1_manuscript/paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | FROZEN (v1.0, 349 words) — UNTOUCHED |
| **Frozen Section III** | [`research/paper1_manuscript/paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) | FROZEN (v1.3, 529 words) — UNTOUCHED |
| **Section III Governance** | [`research/paper1_manuscript/phase_7_2_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_7_2_freeze_log.md) | VERIFIED REFERENCE |
| **Targeted Audit (7.2-S)** | [`research/paper1_manuscript/paper1_section_III_targeted_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_targeted_audit.md) | VERIFIED REFERENCE |
| **Complexity Audit (3.6)** | [`research/paper1_literature/phase_3_6_final_complexity_correction.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_6_final_complexity_correction.md) | VERIFIED REFERENCE |
| **Implementation Core** | [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) | READ-ONLY AUDITED (L1–L705) |
| **Configuration Core** | [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) | READ-ONLY AUDITED (L46–L85) |
| **Serialized Graph** | [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) | READ-ONLY AUDITED (744,216 edges) |

---

## 3. Major Implementation Findings

1. **Synthetic Departure State:**
   In [`routing/algorithms.py#L522-L525`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L522-L525), the search root is initialized as `start_state = (None, start_node)`. This adds exactly $d_{\text{out}}(s_0)$ initial transitions departing from $s_0$ with zero turn penalty ($P_{\text{turn}}(\text{None}, s_0, w) = 0.0$), confirming $|S| = |E_s| + 1 = 740,823$.
2. **On-the-Fly Parallel Edge Cost Collapse:**
   In [`routing/algorithms.py#L645-L655`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L645-L655), parallel multigraph edge records between identical ordered pairs are collapsed to the minimum complete impedance cost $c_{\min}(v, w)$ during successor examination. The search space contains no edge keys.
3. **Absence of `decrease-key` and Duplicate Pushes:**
   Python's `heapq` module does not support `decrease-key`. In [`routing/algorithms.py#L679-L700`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L679-L700), whenever a strictly shorter path to state $(v, w)$ is discovered, a duplicate entry is pushed into `open_set`.
4. **Stale Heap Entry Successor Loop Execution:**
   In [`routing/algorithms.py#L552-L613`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L552-L613), stale duplicate heap entries are not discarded upon extraction. Instead, they execute the successor loop across all $d_{\text{out}}(v)$ neighbors. Inside the loop, relaxation condition `new_cost < g_score[next_state]` strictly evaluates to `False`, preventing further heap pushes but consuming $\mathcal{O}(|E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$ elementary operations across the search.
5. **Goal Condition Checked on Extraction:**
   In [`routing/algorithms.py#L566`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L566), the goal test `if current_node == end_node:` is evaluated when the state is popped from `open_set`, guaranteeing shortest-path optimality under monotonic consistency. Destination arrival incurs zero outbound turn penalty.

---

## 4. Heuristic Proof and Correctness Status

1. **Scaled Haversine Heuristic:**
   $h(s) = 0.80 \cdot D_{\text{haversine}}(v, t)$ matches `MIN_PENALTY_FLOOR = 0.8` in `routing/algorithms.py#L28` and `L511-L512`.
2. **Theorem 1 (Conditional Admissibility):**
   Rigorously outlined under Assumptions A1 ($\mu(e) \ge 0.80$), A2 ($P_{\text{turn}} \ge 0$), A3 ($\ell \ge D_{\text{haversine}}$), and A4 (parallel edge collapse preserves lower bound). Because each component is lower-bounded by $0.80 \times$ spherical chord distance, $h(s) \le c^*(s, t)$ holds unconditionally on the evaluated Bengaluru network.
3. **Theorem 2 (Conditional Monotonic Consistency):**
   Proven via the Riemannian spherical triangle inequality $D(v, t) \le D(v, w) + D(w, t)$ multiplied by $\mu_{\min} = 0.80$, directly yielding $h(s) \le c(s, s') + h(s')$.
4. **Corollary 1 (Optimal State Finality):**
   Established directly from monotonic consistency. The first extraction of directed state $(u, v)$ yields optimal traversal cost $g^*(u, v)$. No state reopenings are required.

---

## 5. Complexity Derivation Status

The complexity analysis has been re-derived from scratch based on the actual codebase implementation:
- **General Directed Graphs (Equation 6):**
  $$\mathcal{M}_{\text{general}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{out}}), \quad \mathcal{T}_{\text{general}} = \mathcal{O}\left( |E_s| \cdot d_{\max}^{\text{out}} \log(|E_s| \cdot d_{\max}^{\text{out}}) + |E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}} \right)$$
- **Valence-Bounded Urban Road Networks (Assumption A2, Theorem 3):**
  Under physical junction valence bounds ($d_{\max}^{\text{in}} \le 6, d_{\max}^{\text{out}} \le 6 = \mathcal{O}(1)$):
  $$\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|), \quad \mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$$
- **Bengaluru Network Empirical Concrete Totals:**
  - Distinct states: $|S| = 740,823$.
  - State transitions: $|E_{S,\text{internal}}| = 2,103,894$ ($\approx 2.84 \cdot |E_s|$).
  - Maximum heap pushes: $N_{\text{pushes}} \le 2,103,901$.
  - Peak auxiliary memory: $\le 3,585,547$ items ($\le 4.84 \cdot |E_s|$).

---

## 6. Statement Classification Matrix (Four-Tier Integrity Audit)

Every mathematical and empirical statement planned for Section IV has been classified into one of four integrity tiers:

| Statement / Claim | Classification Tier | Evidentiary Basis |
| :--- | :---: | :--- |
| `start_state = (None, s0)` initializes departure with zero turn penalty | **Tier 1 (Code Verified)** | `routing/algorithms.py#L522-L525`, `L151-L152` |
| Parallel edges collapsed to $c_{\min}(v, w) = \min_k \mu_k \ell_k$ | **Tier 1 (Code Verified)** | `routing/algorithms.py#L645-L655` |
| Binary min-heap uses `heapq` without `decrease-key` | **Tier 1 (Code Verified)** | `routing/algorithms.py#L537-L544`, `L693-L700` |
| Stale pops execute successor loop without modifying `g_score` | **Tier 1 (Code Verified)** | `routing/algorithms.py#L552-L613`, `L679-L682` |
| Destination goal test occurs on pop without exit turn penalty | **Tier 1 (Code Verified)** | `routing/algorithms.py#L566-L592` |
| Raw multigraph contains $|E_{\text{raw}}| = 744,216$ edge records | **Tier 2 (Graph Verified)** | `bengaluru_graph.pkl` (`number_of_edges()`) |
| Effective simple directed graph contains $|E_s| = 740,822$ edges | **Tier 2 (Graph Verified)** | `bengaluru_graph.pkl` (distinct adjacent node pairs) |
| State cardinality is $|S| = |E_s| + 1 = 740,823$ | **Tier 2 (Graph Verified)** | Section III v1.3, confirmed by $|E_s| + 1$ |
| Directed state transitions $\sum_v d_{\text{in}} d_{\text{out}} = 2,103,894$ | **Tier 2 (Graph Verified)** | Phase 3.6 & Phase 7.2-S empirical validation |
| Max degree $d_{\max}^{\text{in}} = d_{\max}^{\text{out}} = 6$, mean $\bar{d} = 2.41$ | **Tier 2 (Graph Verified)** | `bengaluru_graph.pkl` degree sequence scan |
| Minimum edge multiplier $\mu(e) \ge 0.80$ holds across network | **Tier 2 (Graph Verified)** | `bengaluru_graph.pkl` (0 bridge-roundabouts in 744,216) |
| Scaled Haversine heuristic $h(s)$ is conditionally admissible | **Tier 3 (Math Derived)** | Theorem 1 proof under Assumptions A1–A4 |
| Scaled Haversine heuristic $h(s)$ is conditionally consistent | **Tier 3 (Math Derived)** | Theorem 2 proof under Assumptions A1–A4 |
| Extraction from min-heap guarantees optimal state finality | **Tier 3 (Math Derived)** | Corollary 1 derived from Theorem 2 |
| General search complexity is $\mathcal{O}(|E_s| d_{\max} \log |E_s| + |E_s| d_{\max}^2)$ | **Tier 3 (Math Derived)** | Eq. (6) re-derived from min-heap mechanics |
| Urban road network complexity is $\mathcal{O}(|E_s| \log |E_s|)$ time, $\mathcal{O}(|E_s|)$ space | **Tier 3 (Math Derived)** | Theorem 3 derived under Assumption A2 ($d_{\max} = \mathcal{O}(1)$) |
| Multiplier $\mu(e) \ge 0.80$ holds universally on arbitrary road networks | **Tier 4 (Unsupported)** | **REJECTED.** Preserved strictly as an empirical premise (A1) |
| Stale heap entries are pruned in $\mathcal{O}(1)$ before expanding successors | **Tier 4 (Unsupported)** | **REJECTED.** Code executes loop; accounted for in $\mathcal{T}_{\text{loops}}$ |
| Section IV requires an algorithm pseudocode float box | **Tier 4 (Unsupported)** | **REJECTED.** Space budget requires 0 float boxes |

---

## 7. Identified Contradictions and Nuances for Research Lead Decision

1. **Nuance 1: Stale Heap Entry Successor Expansion Overhead:**
   - *Investigation:* Textbook A* descriptions often assume duplicate heap entries are discarded upon popping via `if state in closed_set: continue`. In `two_wheeler_astar`, stale entries are not guarded by a closed-set check; they execute all $d_{\text{out}}(v)$ loop iterations before failing relaxation.
   - *Resolution in Plan:* The complexity re-derivation in Deliverable 2 explicitly accounts for this overhead: total loop iterations across all pops are bounded by $I_{\text{total}} \le (1 + |E_S|) \cdot d_{\max}^{\text{out}} = \mathcal{O}(|E_s| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$. Under bounded physical junction degree ($d_{\max} = \mathcal{O}(1)$), this evaluates to $\mathcal{O}(|E_s|)$, which does not affect the dominant $\mathcal{O}(|E_s| \log |E_s|)$ heap extraction time.
2. **Nuance 2: Transition Count with Synthetic Departure State:**
   - *Investigation:* The internal line graph contains exactly $\sum_v d_{\text{in}}(v) d_{\text{out}}(v) = 2,103,894$ transitions. In a single query rooted at $s_0$, the synthetic initial state $(\text{None}, s_0)$ adds $d_{\text{out}}(s_0)$ initial transitions.
   - *Resolution in Plan:* Clarified in Deliverables 1 and 2 that $|E_S(s_0)| = d_{\text{out}}(s_0) + 2,103,894 \le 2,103,900$.
3. **Nuance 3: Empirical Multiplier Floor Boundary:**
   - *Investigation:* If bridge ($0.80$) and roundabout ($\times 0.95$) co-occurred on an edge, $\mu(e) = 0.76 < 0.80$.
   - *Resolution in Plan:* Assumption A1 is formally established as an empirically verified prerequisite of the Bengaluru network rather than an inherent topological axiom, maintaining complete mathematical honesty.

---

## 8. Master Deliverable Inventory

The four authoritative deliverables for Phase 8.1 are completed and located at:
1. **Structural Blueprint:** [`research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md)
2. **Mathematical Evidence Map:** [`research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md)
3. **Implementation Audit:** [`research/paper1_manuscript/phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md)
4. **Execution Log:** [`research/paper1_manuscript/phase_8_1_execution_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_execution_log.md)

---

## 9. Strict Stop Condition Enforcement

- Zero manuscript prose has been drafted for Section IV.
- Frozen Sections I, II, and III remain bitwise unmodified.
- Abstract and bibliography remain bitwise unmodified.
- Source code, graph assets, and experimental datasets remain bitwise unmodified.
- Zero new experiments were run.
- Phase 8.2 has not been initiated.
- Mathematical proofs are submitted for Research Lead review and are not unilaterally declared approved.
