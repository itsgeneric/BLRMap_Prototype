# Phase 3 note: Experiment E consolidation (Paper 2, RQ1 and RQ2)

Status: DRAFT for author approval. Nothing here is frozen.
Source: the original Experiment E data in `stage_2b_full_ablation_results.json` (25 corridors), recomputed by `phase3_expE_analysis.py`. Paper 1's A to D results are not used.
Corridors appear by ID and distance class only (no names, no coordinates).

## 1. Definitions as verified
| Quantity | Definition as used | Verified how |
|---|---|---|
| Any-alternative success | at least 1 alternative returned (22 of 25) | counted from `surviving_count` |
| Full success | 3 alternatives returned (K = 3): 14 of 25 | counted from `surviving_count` |
| Mean alternatives | mean of `surviving_count` | 2.24 over all 25 (zeros included); 2.545 over the 22 successful |
| Pairwise diversity | 1 - Jaccard, per the label in the original analysis script | stored per corridor; NOT recomputable (route geometry is not in the JSON) |
| Detour ratio, overlap ratio | stored per route; entry 0 is the primary route (1.0), alternatives are entries 1 onward | structure checked; basis (length vs cost) NOT recomputable |
| Runtime | median of 3 repetitions, in seconds | OD_01 checked against the raw repetitions |
| `rejected_overlap` | candidates rejected by the overlap filter (E3 only) | summed from the JSON |

All 56 offset alternatives respect the production filters: detour ratio at most 1.1939 (limit 1.2) and overlap at most 0.6911 (limit 0.7).

## 2. The two outstanding discrepancies, resolved from the data
1. **Diversity.** The JSON stores 0.0 for the 3 corridors that returned no alternatives (OD_04, OD_15, OD_23), where diversity is undefined. The mean over all 25 corridors is 0.4932, so it counts those failures as zero. The mean over the 22 corridors that returned at least one alternative is 0.5605 (median 0.5672). Both denominators are verified. Recommended reporting: 0.5605 (n = 22) as the diversity of returned alternatives, with 0.4932 only if labelled "failures counted as zero". The same zero-padding explains 0.3489, 0.1409 and 0.2662 in the handover for the five-corridor subset.
2. **Rejected candidates.** The JSON gives 323, not 363: 3 + 80 + 35 + 62 + 143 over the five Yen corridors. No combination of fields reproduces 363 (total E3 candidates 1,085; E2 1,022; difference 63). 363 is unsupported and must not be used. Note that 323 counts only overlap-filter rejections and is not "323 of 1,085 candidates", because the remaining candidates are not accounted for in the file.

## 3. Results
**Offset method, all 25 corridors**
| Class | n | Any alternative | Full K = 3 | Mean alternatives | Mean diversity (successful) | Median runtime (s) |
|---|---:|---:|---:|---:|---:|---:|
| Short | 7 | 6 (85.7%) | 5 | 2.43 | 0.622 | 7.71 |
| Medium | 10 | 8 (80.0%) | 5 | 1.90 | 0.530 | 9.38 |
| Long | 8 | 8 (100%) | 4 | 2.50 | 0.545 | 12.99 |
| All | 25 | 22 (88.0%) | 14 (56.0%) | 2.24 | 0.5605 | 9.09 (mean 10.52, range 7.36 to 22.54) |

Mean detour of alternatives 1.046 and mean overlap 0.496 (56 alternatives).

**Yen comparison, five corridors (descriptive only)**
| Method | Corridors with any alternative | K = 3 reached | Mean alternatives | Mean diversity, matched 3 corridors | Mean overlap of alternatives | Mean runtime (s) | Median runtime (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| E1 Offset | 3 | 1 | 1.2 | 0.582 | 0.437 | 9.50 | 8.84 |
| E2 Raw Yen | 5 | 5 | 3.0 | 0.129 | 0.926 | 42.61 | 10.36 |
| E3 Filtered Yen | 4 | 4 | 2.4 | 0.346 | 0.549 | 42.26 | 9.97 |

Matched corridors are the three where both the offset method and filtered Yen returned alternatives (OD_01, OD_02, OD_03).

## 4. What the data does and does not support
- Raw Yen reaches K = 3 everywhere, but its alternatives are near copies of the primary route (mean overlap 0.93, diversity 0.13). This is why the overlap filter exists.
- On the five Yen corridors, filtered Yen returned more alternatives than the offset method (2.4 vs 1.2; K = 3 reached on 4 vs 1). Where both succeeded, the offset alternatives were more diverse (0.58 vs 0.35) with lower overlap.
- **The 4.49x speed-up reproduces only as a ratio of means (42.61 s / 9.50 s) and is driven by one corridor.** Per-corridor ratios of raw Yen to offset runtime are 12.4, 2.3, 1.3, 0.88 and 0.01. Yen was faster on two of the five. The median ratio is 1.26. The paper should report per-corridor runtimes and not claim a general speed-up. Offset runtime stays within about 7 to 14 s on these corridors, whereas Yen ranges from 0.1 s to 174 s.
- The offset method returned no alternatives on OD_04, even though filtered Yen found three valid ones there. Failure is therefore not always due to the absence of alternatives. The handover attributes the three failures to "barriers/detour filtering", but the JSON records no exceptions, so that cause is unverified.

## 5. Limitations
- The five Yen corridors are a subset. The selection criterion is not recorded in the JSON, and the subset includes two of the three offset failures (offset any-alternative success is 60% here vs 88% overall). It is not representative.
- n = 5 for the Yen comparison, so it is descriptive. The original script runs paired tests, but with five corridors they are not reported and no significance claim is made.
- Runtimes are medians of 3 repetitions on one machine whose specification is not recorded.
- Diversity, detour and overlap definitions are taken from stored values and script labels, not recomputed.
- Corridor names are withheld. Results use IDs and distance class.

## 6. Evidence labels
| Item | Label |
|---|---|
| All counts, means, runtimes and filter checks above | Measured (original JSON) |
| Diversity, detour and overlap definitions | Unverified (not recomputable from the package) |
| Cause of the offset failures on OD_04, OD_15, OD_23 | Unverified (handover-stated) |
| 363 rejected candidates | Unsupported; 323 is measured |
| Yen subset selection rationale | Unknown |
