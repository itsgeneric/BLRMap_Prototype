# Phase 3.4 — Final Rigorous Complexity Derivation for Paper 1

**Project:** Locally Controlled Two-Wheeler-Aware Routing Engine for Bengaluru (`BLRMap_Prototype`)  
**Phase:** Phase 3.4 — Final Complexity and Claim Wording Corrections  
**Target:** Paper 1 — *Turn-Aware State-Expanded A\* and Two-Wheeler Road Impedance Modelling*  
**Date:** 2026-11-05  
**Document:** [`phase_3_4_final_complexity_derivation.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/phase_3_4_final_complexity_derivation.md)  
**Audited Source Code:** [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) (`two_wheeler_astar`, lines 460–705)  
**Protocol References:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **AUTHORITATIVE COMPLEXITY SPECIFICATION**

---

## 1. Algorithmic Structure and Data Flow

In [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), `two_wheeler_astar` operates as a state-expanded shortest path algorithm designed to evaluate heading-dependent turn penalties.

```python
# Initial State & Data Structures
start_state = (initial_previous_node, start_node)  # (None, s_0)
g_score = {start_state: 0.0}
came_from = {}
counter = itertools.count()
open_set = []
heapq.heappush(open_set, (heuristic(start_node), next(counter), start_state))

# Main Search Loop
while open_set:
    _, _, state = heapq.heappop(open_set)
    expanded_states += 1
    previous_node, current_node = state
    visited_nodes.add(current_node)
    current_cost = g_score[state]

    if current_node == end_node:
        # Reconstruct route and return
        ...

    for next_node in graph.successors(current_node):
        explored_transitions += 1
        edge_cost = two_wheeler_edge_cost(...)
        turn_cost = _turn_penalty(graph, previous_node, current_node, next_node)
        new_cost = current_cost + edge_cost + turn_cost
        next_state = (current_node, next_node)

        if next_state not in g_score or new_cost < g_score[next_state]:
            g_score[next_state] = new_cost
            came_from[next_state] = state
            priority = new_cost + heuristic(next_node)
            heapq.heappush(open_set, (priority, next(counter), next_state))
```

### Critical Implementation Characteristics:
1. **Min-Heap without `decrease-key`:** The priority queue is implemented using Python's standard `heapq` module. When an existing state `next_state` is reached via a shorter path, a new 3-tuple `(priority, counter, next_state)` is pushed into `open_set`. The older, suboptimal entry remains dormant in the heap.
2. **Absence of Pop-Time Filtering:** When a stale entry is popped via `heapq.heappop`, there is no filter check (e.g., `if priority > g_score[state] + heuristic(...)`). The algorithm increments `expanded_states`, retrieves `current_cost = g_score[state]`, and proceeds to execute the `for next_node in graph.successors(current_node)` loop.
3. **Lazy Relaxation Suppression:** During a stale entry's successor loop, `current_cost` equals the previously minimized $g$-score. Thus, `new_cost` is identical to the earlier pop's calculation, causing `new_cost < g_score[next_state]` to evaluate to `False`. While this prevents recursive heap insertions, **it still incurs successor iterations and adjacency list lookups**.

---

## 2. Itemized Quantitative Derivations

Let $G = (V, E)$ be a directed graph. Let $d_{\text{in}}(v)$ and $d_{\text{out}}(v)$ denote the in-degree and out-degree of vertex $v \in V$.  
Define:
$$d_{\max}^{\text{in}} = \max_{v \in V} d_{\text{in}}(v), \quad d_{\max}^{\text{out}} = \max_{v \in V} d_{\text{out}}(v), \quad d_{\max} = \max(d_{\max}^{\text{in}}, d_{\max}^{\text{out}})$$

### 2.1 Number of Distinct States ($|S|$)
- Every state represents arriving at vertex $v$ from predecessor $u$, denoted $s = (u, v)$.
- For any traversable road transition, $(u, v) \in E$.
- Including the synthetic origin state $(\text{None}, s_0)$:
  $$|S| = |E| + 1$$
- In Bengaluru ($|E| = 744,216$): $|S| = 744,217$ distinct states.

### 2.2 Number of Possible State Transitions ($|E_S|$)
- A transition occurs from state $(u, v)$ to state $(v, w)$ across intersection $v$.
- For each vertex $v \in V$, there are $d_{\text{in}}(v)$ incoming states and $d_{\text{out}}(v)$ outgoing edges.
- Summing across all vertices, plus the $\text{out-deg}(s_0)$ transitions from the start state:
  $$|E_S| = d_{\text{out}}(s_0) + \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v)$$
- Asymptotic bounds:
  $$|E_S| \le d_{\max} + \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\max}^{\text{out}} = d_{\max} + |E| \cdot d_{\max}^{\text{out}} = \mathcal{O}(|E| \cdot d_{\max}^{\text{out}})$$
- In Bengaluru:
  $$|E_S| = 2,103,894 + d_{\text{out}}(s_0) \approx 2.83 \cdot |E|$$

### 2.3 Maximum Successful Relaxations
- State $(v, w)$ can be relaxed only when an incoming path through a predecessor $u$ discovers a lower cost than previously recorded in `g_score[(v, w)]`.
- There are at most $d_{\text{in}}(v)$ distinct predecessors that can transition into $(v, w)$.
- Because `current_cost` is monotonic and stale pops of $(u, v)$ retrieve the already minimized $g$-score, a single predecessor $(u, v)$ can trigger relaxation of $(v, w)$ at most once.
- Summing across all directed edges $(v, w) \in E$:
  $$\text{Max Successful Relaxations} \le \sum_{(v, w) \in E} d_{\text{in}}(v) = \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v) \le |E| \cdot d_{\max}^{\text{in}}$$
  (plus $d_{\text{out}}(s_0)$ for initial transitions from $s_0$).
- Bound: $\le |E| \cdot d_{\max}^{\text{in}} + d_{\max}^{\text{out}}$.

### 2.4 Maximum Heap Insertions
- Every insertion into `open_set` corresponds to either:
  1. The single initial start state $(\text{None}, s_0)$ ($1$ push).
  2. A successful relaxation (`new_cost < g_score[next_state]`).
- Therefore:
  $$\text{Max Heap Insertions} \le 1 + |E_S| \le 1 + |E| \cdot d_{\max}^{\text{in}} + d_{\max}^{\text{out}}$$
- In general graphs: $\mathcal{O}(|E| \cdot d_{\max})$.
- In Bengaluru: $\le 1 + 2,103,894 + 6 = 2,103,901 \approx 2.83 \cdot |E|$.

### 2.5 Maximum Heap Removals
- The search loop pops entries from `open_set` via `heapq.heappop`. An entry cannot be removed unless it was inserted.
- Therefore:
  $$\text{Max Heap Removals} \le \text{Max Heap Insertions} \le 1 + |E_S| \le 1 + |E| \cdot d_{\max}^{\text{in}} + d_{\max}^{\text{out}}$$
- Breakdown of removals:
  - **Optimal (First) Pops:** At most $|S| = |E| + 1$ removals correspond to the first extraction of each distinct state tuple $(u, v)$.
  - **Stale Removals:** The remaining removals are stale entries:
    $$\text{Max Stale Removals} \le \text{Max Heap Removals} - |S| \le |E_S| - |E| \le |E| \cdot (d_{\max}^{\text{in}} - 1) + d_{\max}^{\text{out}}$$

### 2.6 Successor Iterations Caused by Stale Entries
- When a stale entry for state $(u, v)$ is popped, the algorithm does not discard it; it executes `for next_node in graph.successors(v)`.
- The number of iterations in this loop is exactly $d_{\text{out}}(v)$.
- Each stale pop of vertex $v$ causes $d_{\text{out}}(v)$ loop iterations.
- Summing across all possible stale pops:
  $$\text{Stale Successor Iterations} \le \sum_{v \in V} (d_{\text{in}}(v) - 1) \cdot d_{\text{out}}(v) \cdot d_{\text{out}}(v) \le |E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$$
- Across all stale iterations:
  - Length, road class, and turn angle are evaluated ($\mathcal{O}(1)$ arithmetic).
  - The inequality `new_cost < g_score[next_state]` evaluates to `False`, generating zero further pushes.
  - Work per stale iteration is strictly $\mathcal{O}(1)$.
- Total computational time consumed by stale iterations:
  $$\mathcal{T}_{\text{stale\_loop}} = \mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$$

### 2.7 Auxiliary Memory Excluding the Heap
- `g_score`: Hash map storing at most $|S| = |E| + 1$ keys and float values $\implies \mathcal{O}(|E|)$.
- `came_from`: Hash map storing at most $|S| = |E| + 1$ keys and predecessor state tuples $\implies \mathcal{O}(|E|)$.
- `visited_nodes`: Set storing at most $|V|$ node IDs $\implies \mathcal{O}(|V|)$.
- Total Non-Heap Memory:
  $$\mathcal{M}_{\text{non-heap}} = \mathcal{O}(|E| + |V|) = \mathcal{O}(|E|)$$

### 2.8 Total Memory Including the Heap
- The priority queue `open_set` contains at most the total number of inserted entries remaining unpopped:
  $$|\text{open\_set}| \le \text{Max Heap Insertions} \le 1 + |E| \cdot d_{\max}^{\text{in}} + d_{\max}^{\text{out}}$$
- Each heap element is a 3-tuple `(float, int, tuple)`.
- Total Memory:
  $$\mathcal{M}_{\text{total}} = \mathcal{M}_{\text{non-heap}} + |\text{open\_set}| = \mathcal{O}(|E| + |E| \cdot d_{\max}^{\text{in}}) = \mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$$

---

## 3. Comparison of Complexity Across Network Topologies

| Complexity Metric | General Directed Graph | Bounded-Degree Graph ($d_{\max} = \mathcal{O}(1)$) | Observed Bengaluru Graph ($|E|=744,216, d_{\max}=6$) |
| :--- | :---: | :---: | :---: |
| **Distinct States ($|S|$)** | $|E| + 1$ | $|E| + 1$ | $744,217$ states ($1.00 \cdot |E|$) |
| **State Transitions ($|E_S|$)** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{out}})$ | $\mathcal{O}(|E|)$ | $2,103,894$ transitions ($2.83 \cdot |E|$) |
| **Max Heap Insertions** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$ | $\mathcal{O}(|E|)$ | $\le 2,103,901$ pushes ($2.83 \cdot |E|$) |
| **Max Heap Removals** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$ | $\mathcal{O}(|E|)$ | $\le 2,103,901$ pops ($2.83 \cdot |E|$) |
| **Stale Pop Removals** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$ | $\mathcal{O}(|E|)$ | $\le 1,359,678$ stale pops ($1.83 \cdot |E|$) |
| **Stale Successor Iterations** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$ | $\mathcal{O}(|E|)$ | $\le 8,158,068$ iterations ($\approx 4.4 \cdot |E|$ mean) |
| **Auxiliary Memory (Non-Heap)**| $\mathcal{O}(|E|)$ | $\mathcal{O}(|E|)$ | $\le 1,488,434$ dict entries ($2.00 \cdot |E|$) |
| **Total Memory (with Heap)** | $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$ | $\mathcal{O}(|E|)$ | $\le 3,592,335$ items ($4.83 \cdot |E|$) |
| **Worst-Case Time Complexity** | $\mathcal{O}(|E| \cdot d_{\max} \log |E| + |E| \cdot d_{\max}^2)$ | $\mathcal{O}(|E| \log |E|)$ | Strictly bounded by $\mathcal{O}(|E| \log |E|)$ |

---

## 4. Final Defensible Asymptotic Complexity Statement

To ensure mathematical precision, the paper must formulate its complexity claims as follows:

> **Theorem (Search Space and Computational Complexity).**  
> *Let $G = (V, E)$ be a directed road network. Turn-aware state-expanded $A^*$ operates across $|S| = |E| + 1$ search states and $|E_S| = \sum_{v \in V} d_{\text{in}}(v) \cdot d_{\text{out}}(v)$ state transitions.*  
> *When implemented using a binary min-heap without addressable key decrease, the algorithm incurs at most $|E| \cdot d_{\max}^{\text{in}}$ heap insertions and at most $|E| \cdot (d_{\max}^{\text{in}} - 1) \cdot d_{\max}^{\text{out}}$ stale successor iterations, yielding:*  
> 1. *$\mathcal{O}(|E| \cdot d_{\max}^{\text{in}})$ auxiliary memory complexity and $\mathcal{O}(|E| \cdot d_{\max}^{\text{in}} \log |E| + |E| \cdot d_{\max}^{\text{in}} \cdot d_{\max}^{\text{out}})$ time complexity on general directed graphs.*  
> 2. *$\mathcal{O}(|E|)$ auxiliary memory complexity and $\mathcal{O}(|E| \log |E|)$ worst-case time complexity on spatial road networks where intersection valence is physically bounded ($d_{\max} = \mathcal{O}(1)$).*  
> *In the evaluated metropolitan road network of Bengaluru ($|V| = 308,643$, $|E| = 744,216$), maximum in- and out-degrees are $d_{\max}^{\text{in}} = 6$ and $d_{\max}^{\text{out}} = 6$ (mean degree $2.41$), bounding the state-transition expansion ratio to $|E_S| / |E| = 2.83$ ($2,103,894$ transitions).*

---

*Specification verified and finalized under read-only protocols of `blrmap-research-protocol` and `evidence-integrity-audit`.*
