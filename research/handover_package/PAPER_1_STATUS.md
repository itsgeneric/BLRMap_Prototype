# Paper 1 — Status and Frozen Research Record

## Title
*Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*

## Status
Paper 1's research content was frozen section by section, assembled in IEEE two-column format, and compiled to a six-page PDF. A revised figure package was created with single-column figures to improve readability and fit. The user was given the final PDF, LaTeX source, and Overleaf ZIP.

## Final artifacts included
- `Paper1_CSNT_Figures_Improved.pdf`
- `paper1_main_CSNT_figures_improved.tex`
- `Paper1_CSNT_Overleaf_Figures_Improved.zip`
- Additional earlier Paper 1 PDFs and Overleaf ZIPs are included as backups.

## Frozen content
- Abstract: 208 conventional words; 209 whitespace splits; 204 math-token count.
- Section I: Introduction, frozen.
- Section II: Related Work, frozen.
- Section III: exactly four subsections III-A to III-D; 529 body words excluding display equations/table wrappers.
- Section IV: four subsections IV-A to IV-D; 529 whitespace words / 452 math-token words; three equations (4)-(6); formally frozen.
- Section V: experimental setup, frozen.
- Section VI: results, frozen; 511 math-token words / 644 whitespace words; three figures and one table.
- Section VII: conclusion, frozen; 267 math-token words / 287 whitespace words.
- No Section III-E exists.

## Core Paper 1 contribution
A two-wheeler-oriented routing formulation combining:
1. State-expanded A* with directed-edge states and arrival-heading dependence.
2. Discrete angular turn penalties.
3. Road-class impedance multipliers.
4. A Haversine heuristic scaled by 0.80, admissible/consistent under stated graph-specific conditions.

## Key Paper 1 results
- Dataset: Bengaluru OSM graph with 308,643 vertices, 744,216 raw directed multigraph edge records, 740,822 distinct ordered adjacent node pairs; 25 OD corridors.
- Experiment A: turn-aware A0 vs turn-unaware A1 reduces mean sharp turns (>=60°) from 32.52 to 21.44, a 34.1% reduction; Holm-adjusted p=4.5e-5. Median runtime 174.93 ms vs 154.69 ms.
- Experiment B: production impedance B0 vs neutral B1 reduces arterial exposure from 65.05% to 13.84% (-51.21 percentage points), with mean physical route distance increasing 15.53% (7.647 vs 6.620 km).
- Experiment C: C2 captures 87.1% of the maximum observed sharp-turn reduction and is an empirical corpus-average trade-off knee, not a universal optimum.
- Experiment D: bridge and roundabout modifier factorial study. Bridge-related route changes occurred on OD_04 and OD_15; roundabout route geometry was unchanged on the 25 corridors. Important limitation: D experiment search-time objective costs were not retained; reported impedance cost is post-hoc standardized production score.
- A0 runtime distribution is variable; do not claim universal sub-second completion.
- Sharp-turn counts are geometric measures, not safety evidence.
- No real-world journey-time measurements were collected for Paper 1.

## Travel-time framing
The project objective is to support more time-efficient two-wheeler journeys. Paper 1 does not establish measured real-world travel-time savings. It measures route distance, turn counts, road-class exposure, and algorithm runtime.

## Critical separation
Experiment E and alternative-route generation are Paper 2 only. Do not introduce Paper 2 alternative route results into Paper 1.

## Final PDF note
The final revised PDF was reported as six pages, with Table II before References and all 14 references present. A minor 10.2 pt overfull vertical box warning remained in the LaTeX log, but visual inspection found no clipped manuscript content. Recompile and verify before any future submission.
