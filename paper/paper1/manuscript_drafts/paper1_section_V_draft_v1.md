# Section V: Experimental Setup and Methodology (Frozen v1.0)

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** IEEE CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.3-B3 — Section V Finalisation and Freeze  
**Source Evidence Blueprint:** [`phase_8_3_A_experimental_evidence_blueprint.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_3_A_experimental_evidence_blueprint.md) (v1.6 Audited)  
**Word Count:** 227 words (prose body text, whitespace-delimited, excluding headings)  
**Status:** APPROVED & FORMALLY FROZEN (2026-11-06)  

---

## V. EXPERIMENTAL SETUP AND METHODOLOGY

### A. Urban Road Network and OD Corridor Corpus

The empirical evaluation is conducted on an OpenStreetMap road network of Bengaluru modelled as a directed graph with 308,643 vertices, 744,216 raw directed multigraph edge records, and 740,822 distinct ordered adjacent node pairs following parallel-edge collapse. Benchmarks are evaluated across 25 origin–destination corridors, with physical route distances ranging from 1.35 km to 15.82 km across the turn-unaware reference configurations (A1, A2, and C0); the individual corridor serves as the primary unit of analysis.

### B. Benchmark Configurations and Execution Protocol

Four experimental suites evaluate routing behavior across the corridor corpus. Experiment A compares turn-aware state-expanded routing against turn-unaware state expansion and a node-level reference. Experiment B benchmarks production road-class impedance against neutral hierarchy weights and physical shortest paths. Experiment C tests sensitivity across four discrete turn-penalty tiers. Experiment D assesses topological bridge and roundabout modifiers under a 2×2 factorial design. Each corridor–configuration combination is evaluated across five execution repetitions, with elapsed wall-clock runtime recorded using `time.perf_counter()`, producing 1,750 execution observations across 350 experimental cells.

### C. Statistical Analysis

For each configuration, per-corridor observations are aggregated using within-corridor medians across the five execution repetitions before paired corridor-level comparisons ($N=25$). Inferential hypothesis testing employs two-sided Wilcoxon signed-rank tests with Pratt correction for zero differences, controlling family-wise error rates via Holm–Bonferroni step-down adjustments within each comparison family. Effect sizes are reported using matched-pairs Cohen's $d_z$ with 95% confidence intervals and Hodges–Lehmann paired median difference estimates with 95% confidence intervals, where reported.
