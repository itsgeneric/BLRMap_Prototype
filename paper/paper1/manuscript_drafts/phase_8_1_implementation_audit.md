# Phase 8.1 Implementation Audit — Algorithmic Reconstruction and Codebase Traceability (v1.3 Reconciled and Verified)

**Document:** [`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md)  
**Project:** Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks (Paper 1)  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.1-U — Final Complexity Evidence Consistency Audit  
**Date:** 2026-11-06  
**Audited Source Files:**
- [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) (Lines 1–705)
- [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py) (Lines 46–85)
- [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py) (Lines 146–260)
- [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl) (Serialized NetworkX `MultiDiGraph`)  
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE RECONCILED IMPLEMENTATION AUDIT REPORT**

---

## 1. Executive Summary

This audit reconstructs the execution of `two_wheeler_astar` in [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) line by line, documenting initialization, successor expansion, relaxation, termination, and path reconstruction. Every algorithmic mechanism is mapped to exact line numbers and inspected for structural compliance with classical A* theory. Crucial implementation realities—including the absence of `decrease-key`, the execution of successor loops on stale duplicate pops, dynamic uncached parallel-edge scanning, and the mathematical safety of goal extraction without stale-pop filtering—are rigorously analyzed to provide the foundation for Section IV.

---

## 2. Step-by-Step Implementation Reconstruction of `two_wheeler_astar`

**Function Signature:**
```python
def two_wheeler_astar(
    graph,
    start_node,
    end_node,
    graph_mgr,
    penalties=None,
    congested_nodes=None,
    heuristic_mode="admissible",
    return_metrics=False,
    initial_previous_node=None,
    banned_nodes=None,
    banned_edges=None
):
```
Location: [`routing/algorithms.py#L460-L472`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L460-L472).

---

### 2.1 Component A: Initialization

1. **Timer Initialization (L498):**
   `start_time = time.perf_counter() if return_metrics else 0.0`.
2. **Heuristic Closure Definition (L500–L517):**
   ```python
   def heuristic(node):
       h_dist = haversine_m(
           graph.nodes[node]["y"], graph.nodes[node]["x"],
           graph.nodes[end_node]["y"], graph.nodes[end_node]["x"]
       )
       if heuristic_mode in ("zero", "dijkstra"):
           return 0.0
       elif heuristic_mode == "aggressive":
           return h_dist / MIN_PENALTY_FLOOR
       elif heuristic_mode == "admissible":
           return h_dist * MIN_PENALTY_FLOOR
   ```
   - `MIN_PENALTY_FLOOR = 0.8` (defined at L28).
   - In production mode (`heuristic_mode="admissible"`), returns $0.80 \times D_{\text{haversine}}(\text{node}, \text{end\_node})$.
3. **Initial State Representation (L522–L525):**
   ```python
   start_state = (
       initial_previous_node,
       start_node
   )
   ```
   - When called for standard origin-destination routing, `initial_previous_node` defaults to `None`.
   - The initial state is the synthetic root tuple $s_0^{\text{state}} = (\text{None}, s_0)$.
   - It represents departure from the origin with no preceding trajectory.
4. **Tentative Distance Map Initialization (L527–L529):**
   ```python
   g_score = {
       start_state: 0.0
   }
   ```
   - `g_score` is a Python dictionary keyed by state tuples `(prev_node, curr_node)`.
   - $g(s_0^{\text{state}}) = 0.0$.
5. **Backpointer Predecessor Map (L531):**
   ```python
   came_from = {}
   ```
   - Tracks predecessor state transitions: `came_from[next_state] = state`.
6. **Tie-Breaker Counter (L533):**
   ```python
   counter = itertools.count()
   ```
   - Generates monotonically increasing integers ($0, 1, 2, \dots$) to break priority ties in FIFO order, preventing tuple comparison failures on state objects.
7. **Priority Queue Initialization (L535–L544):**
   ```python
   open_set = []
   heapq.heappush(
       open_set,
       (
           heuristic(start_node),
           next(counter),
           start_state
       )
   )
   ```
   - Min-heap entries are 3-tuples `(priority, tie_breaker, state)`.
   - Initial entry priority is $f(s_0^{\text{state}}) = 0.0 + h(s_0) = h(s_0)$.

---

### 2.2 Component B: Successor Expansion

1. **Search Loop and State Pop (L550–L554):**
   ```python
   while open_set:
       _, _, state = heapq.heappop(open_set)
   ```
   - Pops the entry with the minimal priority key $f(s)$.
   - The priority float and counter integer are discarded as `_`.
2. **State Unpacking and Accounting (L556–L560):**
   ```python
   expanded_states += 1
   previous_node, current_node = state
   visited_nodes.add(current_node)
   current_cost = g_score[state]
   ```
   - `previous_node` and `current_node` represent $u$ and $v$ in state $(u, v)$.
   - `current_cost` retrieves $g(u, v)$ from `g_score`.
3. **Goal Check on Extraction (L566):**
   ```python
   if current_node == end_node:
       # [Reconstruct route and return]
   ```
   - Evaluated **when popped** from `open_set`, satisfying Dijkstra/A* optimality requirements.
4. **Neighbor Traversal (L611–L620):**
   ```python
   for next_node in graph.successors(current_node):
       if banned_nodes and next_node in banned_nodes: continue
       if banned_edges and (current_node, next_node) in banned_edges: continue
   ```
   - Iterates through distinct out-neighbors $w$ of physical intersection $v$.
   - NetworkX `graph.successors(current_node)` yields each neighboring vertex **exactly once**, regardless of how many parallel edges connect $v$ and $w$.
5. **Parallel Edge Resolution and Uncached Cost Scanning (L623–L655):**
   ```python
   edge_data = graph.get_edge_data(current_node, next_node)
   if edge_data is None:
       continue
   if "length" in edge_data:
       edge_cost = two_wheeler_edge_cost(edge_data, graph_mgr, penalties, current_node, next_node, congested_nodes)
   else:
       edge_cost = min(
           two_wheeler_edge_cost(data, graph_mgr, penalties, current_node, next_node, congested_nodes)
           for data in edge_data.values()
       )
   ```
   - If multiple parallel edges exist, `edge_data` is a key-indexed dictionary `{0: dict, 1: dict, ...}`.
   - Evaluates `two_wheeler_edge_cost` dynamically across all parallel candidates without caching, selecting the **minimum impedance cost** $c_{\min}(v, w)$.
   - Bounded by maximum parallel multiplicity $q_{\max} = 4$.
6. **Turn Penalty Calculation (L661–L666):**
   ```python
   turn_cost = _turn_penalty(graph, previous_node, current_node, next_node)
   ```
   - Evaluates chord-based angular deflection $\Delta\theta(u, v, w)$ via `_turn_angle`.
   - Returns $25.0\text{ m}$ if $\Delta\theta \ge 60.0^\circ$, $8.0\text{ m}$ if $30.0^\circ \le \Delta\theta < 60.0^\circ$, and $0.0\text{ m}$ otherwise (or if `previous_node is None`).
7. **Transition Cost Assembly (L668–L677):**
   ```python
   new_cost = current_cost + edge_cost + turn_cost
   next_state = (current_node, next_node)
   ```
   - Accumulates $g(s) + c(s, s') = g(u, v) + c_{\min}(v, w) + P_{\text{turn}}(u, v, w)$.
   - Constructs successor state $s' = (v, w)$.

---

### 2.3 Component C: Relaxation and Heap Mechanics

1. **Relaxation Condition (L679–L682):**
   ```python
   if (next_state not in g_score or new_cost < g_score[next_state]):
   ```
   - Checks whether $s' = (v, w)$ has not been reached yet, or whether `new_cost` is strictly smaller than the existing tentative distance `g_score[next_state]`.
2. **Updating Distance and Predecessor (L684–L686):**
   ```python
   g_score[next_state] = new_cost
   came_from[next_state] = state
   ```
   - Updates the minimal discovered cost to state $s'$.
   - Records $s = (u, v)$ as the optimal predecessor state.
3. **Priority Evaluation and Duplicate Heap Insertion (L688–L700):**
   ```python
   priority = new_cost + heuristic(next_node)
   heapq.heappush(
       open_set,
       (
           priority,
           next(counter),
           next_state
       )
   )
   ```
   - Evaluates evaluation function $f(s') = g(s') + h(w)$.
   - Pushes a new 3-tuple to `open_set`.
   - **Crucial Finding:** Python `heapq` does not implement `decrease-key`. If `next_state` was already present in `open_set` with a higher cost, that prior entry is not updated or removed; instead, a new duplicate entry is pushed into `open_set`.
4. **Stale Entry Handling Inspection (L550–L613):**
   - **Crucial Finding:** The implementation contains **no stale-entry detection guard** upon popping:
     ```python
     while open_set:
         _, _, state = heapq.heappop(open_set)
         expanded_states += 1
         previous_node, current_node = state
         visited_nodes.add(current_node)
         current_cost = g_score[state]
     ```
     - There is no `if state in closed_set: continue` check.
     - There is no `if popped_f > g_score[state] + heuristic(current_node): continue` check.
   - When a stale duplicate entry for state $s = (u, v)$ is popped:
     - `expanded_states` is incremented.
     - `current_cost = g_score[state]` retrieves the already-minimized optimal cost $g^*(u, v)$.
     - It enters the loop `for next_node in graph.successors(current_node):` (L611).
     - Inside the loop, it evaluates `edge_cost`, `turn_cost`, and `new_cost`.
     - Because `current_cost` is identical to the first optimal pop, `new_cost` equals the already-recorded cost in `g_score[next_state]`.
     - At L681, `new_cost < g_score[next_state]` strictly evaluates to `False`.
     - No heap push occurs, but the loop executed all $d_{\text{out}}(v)$ successor iterations.
   - **Consequence for Complexity:** Total successor iterations must account for stale duplicate pops:
     - **Graph-Wide Theoretical Upper Bound (via Exact Degree Summation):** Because `graph.successors(current_node)` iterates unique adjacent vertices $v$ and resolves parallel edges inside the loop, search operates strictly over $G = (V, E_s)$. Under hypothetical full-graph saturation:
       $$I_{\text{best}} \le T_{\text{query}}^{\text{simple}} = 2,087,155 + 6 = \mathbf{2,087,161}$$
       $$I_{\text{stale},\text{exact\_sum}} = 3,799,611 + 20 = \mathbf{3,799,631}$$
       $$I_{\text{total},\text{exact\_sum}} = 2,087,161 + 3,799,631 = \mathbf{5,886,792} \text{ iterations}$$
       *(Note: This represents a theoretical graph-wide upper bound derived by exact topological degree summation under full-graph saturation; it must NOT be described as an observed individual-query iteration count).*
     - **Conservative Degree-Bounded Bound ($d_{\max}^{\text{out}} = 6$):**
       $$I_{\text{stale}} \le 1,346,339 \times 6 = \mathbf{8,078,034}$$
       $$I_{\text{total}} \le 2,087,161 + 8,078,034 = \mathbf{10,165,195} \text{ iterations}$$
     - **Crude Global Bound:** Multiplying all removals by $d_{\max}^{\text{out}} = 6$ yields $\le 2,087,162 \times 6 = \mathbf{12,522,972}$.

---

### 2.4 Component D: Termination and Path Reconstruction

1. **Termination Condition (L566):**
   ```python
   if current_node == end_node:
   ```
   - Search terminates immediately upon popping any state $s = (u, \text{end\_node})$.
2. **Turn Cost Incurred at Destination:**
   - Destination arrival incurs **zero outbound turn penalty**.
   - The inbound turn into $\text{end\_node}$ was evaluated during the transition $(u, v) \to (v, \text{end\_node})$. However, no transition departing from $\text{end\_node}$ is ever evaluated.
   - This matches Section III Eq. (3) with 100% fidelity.
3. **Safety of Goal Extraction without Stale Guard:**
   - Because $h(\text{end\_node}) = 0.0$, the priority of any goal state entry in the min-heap is simply its accumulated cost: $f(s_{\text{goal}}) = g(s_{\text{goal}})$.
   - Since min-heap extracts entries in non-decreasing order of priority, the entry with minimal cost $g^*$ is popped strictly before any stale entry with higher cost $g_{\text{stale}} > g^*$.
   - Because the algorithm terminates immediately upon the first goal pop, stale goal entries are never accepted, guaranteeing exact shortest-path optimality.
4. **Path Backtracking Loop (L568–L585):**
   ```python
   states = []
   current_state = state
   while True:
       states.append(current_state)
       if current_state == start_state:
           break
       current_state = came_from[current_state]
   states.reverse()
   ```
   - Traverses `came_from` backwards from goal state to $s_0^{\text{state}} = (\text{None}, s_0)$.
   - Reverses the list to yield chronological order: $[(\text{None}, s_0), (s_0, v_1), (v_1, v_2), \dots, (v_{k-1}, \text{end\_node})]$.
5. **Vertex Extraction and Deduplication (L586–L591):**
   ```python
   route = [s[1] for s in states]
   deduped_route = _dedupe_nodes(route)
   ```
   - Extracts the second element of each state tuple: $[s_0, v_1, v_2, \dots, \text{end\_node}]$.
   - Calls `_dedupe_nodes(route)` to eliminate any accidental consecutive duplicate node IDs.

---

## 3. Supporting Helper Function Audits

### 3.1 `_turn_angle` and `_bearing_deg`
- **Source Lines:** [`routing/algorithms.py#L63-L77`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L63-L77) and [`L110-L145`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L110-L145).
- `_bearing_deg(lat1, lng1, lat2, lng2)` evaluates the spherical forward azimuth:
  $$\theta = \text{atan2}\left(\sin\Delta\lambda \cos\phi_2, \; \cos\phi_1 \sin\phi_2 - \sin\phi_1 \cos\phi_2 \cos\Delta\lambda\right) \pmod{360^\circ}$$
- `_turn_angle` computes `incoming = _bearing_deg(u, v)` and `outgoing = _bearing_deg(v, w)`.
- It evaluates the angular deflection:
  $$\Delta\theta = \min(|\theta_{\text{in}} - \theta_{\text{out}}|, \; 360^\circ - |\theta_{\text{in}} - \theta_{\text{out}}|) \in [0^\circ, 180^\circ]$$
- **Finding:** Operates purely on intersection endpoint coordinates; intermediate roadway polyline vertices are not evaluated.

### 3.2 `two_wheeler_edge_cost`
- **Source Lines:** [`routing/algorithms.py#L266-L348`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L266-L348).
- Retrieves surveyed physical length $\ell(e)$.
- Computes base multiplier $f_{\text{class}}$ from `TWO_WHEELER_ROAD_PENALTIES` (matching Section III Table I Part A).
- Bridge override: If `is_bridge` affirmative and $h \in \mathcal{H}_{\text{main}}$, `penalty = 0.8` (replaces road class).
- Roundabout modifier: If `junction == "roundabout"`, `penalty *= 0.95`.
- Dynamic congestion / surface penalties: In standard benchmark evaluation, `congested_nodes = None` and surface quality file is neutral.
- Returns $\ell(e) \cdot \mu(e)$.

### 3.3 Excluded Experimental Stubs
- `count_filterable_junctions` ([`L174-L214`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L174-L214)) and `apply_filtering_discount` ([`L216-L234`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py#L216-L234)).
- **Finding:** Neither function is called inside `two_wheeler_astar`. Both remain completely uninvoked in production routing and are strictly excluded from Section IV.

---

## 4. Reconciled Auxiliary Memory Audit (Logical Entries)

The persistent per-query data structures instantiated in `two_wheeler_astar` are strictly enumerated below:
1. `open_set`: List storing 3-tuples `(priority, counter, state)`.
   - On authoritative simple graph search space: $N_{\text{insert}} \le 1 + T_{\text{query}}^{\text{simple}} \le \mathbf{2,087,162}$ logical entries.
   - Under conservative multigraph comparison proxy: $N_{\text{insert}} \le 1 + T_{\text{query}}^{\text{raw}} \le 2,103,901$ logical entries.
2. `g_score`: Dict mapping `state` tuple `(prev_node, curr_node)` to `float`. Maximum entries: $|S| = |E_s| + 1 = \mathbf{740,823}$ logical entries.
3. `came_from`: Dict mapping `state` tuple to predecessor `state` tuple. Maximum entries: $|E_s| = \mathbf{740,822}$ logical entries.
4. `visited_nodes`: Set storing physical node integer IDs `current_node`. Maximum entries: $|V| = \mathbf{308,643}$ logical entries.
5. Scalar Tracking Variables: `expanded_states`, `explored_transitions`, `start_time`, `counter` (an `itertools.count` object). These are $\mathcal{O}(1)$ primitive scalars that do not scale with graph size.

> [!IMPORTANT]
> **Logical Entries vs. Measured Bytes:**  
> These quantities represent **counts of discrete logical elements** (dictionary key-value pairs, heap tuples, and set elements), not measured physical memory bytes. CPython 64-bit object overhead (struct headers, hash-table buckets, pointer tables) increases actual physical RAM usage, but does not alter the asymptotic scaling $\mathcal{O}(|E_s|)$.

6. **Total Peak Logical Entries:**
   - **Authoritative Simple Graph Search Bound:**
     $$\mathcal{M}_{\text{actual}} \le 2,087,162 + 740,823 + 740,822 + 308,643 = \mathbf{3,877,450} \text{ logical entries}$$
     This represents at most $5.234 \times |E_s|$ logical items.
   - **Conservative Multigraph Comparison Proxy:**
     $$\mathcal{M}_{\text{raw\_proxy}} \le 2,103,901 + 740,823 + 740,822 + 308,643 = \mathbf{3,894,189} \text{ logical entries}$$
     This represents at most $5.257 \times |E_s|$ logical items, confirming linear space complexity $\mathcal{O}(|E_s|)$ on bounded-valence road networks.

---

## 5. Audit Conclusions and Governance Record

1. **Admissibility Implementation Fidelity:** The implementation of $h(s) = 0.80 \cdot D_{\text{haversine}}$ perfectly aligns with the mathematical proof requirements under Assumption A1.
2. **Duplicate Entry Mechanics Grounded:** The lack of `decrease-key` and the execution of successor loops on stale duplicate pops are fully reconciled and incorporated into the formal complexity statements.
3. **Goal Extraction Safety Proved:** Immediate extraction upon `current_node == end_node` is mathematically proven optimal because $h(t) = 0$ guarantees that the optimal path has lower priority than any stale goal entry.
4. **Zero Prose Drafted:** Strict phase compliance is maintained. No manuscript prose has been drafted.
