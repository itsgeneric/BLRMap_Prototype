# Paper 2 — LaTeX Package README

## Title
*Design and Empirical Evaluation of a Two-Wheeler-Aware Routing Framework for Urban Road Networks*

---

## Files in this package

| File | Description | Status |
|------|-------------|--------|
| `paper2_main.tex` | Main LaTeX source (IEEEtran, conference, 11pt, 6-page self-contained) | Ready to compile |
| `paper2_verified_references.bib` | 15 verified BibTeX entries (all DOIs verified; self-citation removed) | Complete & cited |
| `paper2_main_v2_8page_backup.tex` | Backup of prior 8-page working draft | Preserved |
| `paper2_verified_references_v2_backup.bib` | Backup of prior 16-entry bibliography | Preserved |
| `figures/fig_expE_phase3.png` | Experiment E results figure (frozen, Phase 3) | Included |
| `figures/fig_expE_phase3.pdf` | Experiment E results figure PDF version | Included |
| `figures/fig_strava_phase2.png` | Strava trajectory & time breakdown figure (frozen, Phase 2) | Included |
| `figures/fig_strava_phase2.pdf` | Strava trajectory figure PDF version | Included |
| `figures/pair_b_project.png` | Pilot Pair B — Framework screenshot | Included |
| `figures/pair_b_gmaps.png` | Pilot Pair B — Google Maps screenshot | Included |
| `figures/pair_b_waze.png` | Pilot Pair B — Waze screenshot | Included |
| `generate_figures.py` | Optional utility script | Optional |

> **Self-Containment & Figures:** 
> - The manuscript is **100% self-contained** and independent; all mentions of companion or earlier papers have been removed.
> - Fig. 1 (Architecture diagram) is embedded natively as vector TikZ.
> - Figs. 2, 3, and 4 are configured as full two-column floats (`figure*`) with high-resolution scaling (`0.94\textwidth` for Figs. 2 & 4, and `0.32\textwidth` per panel for Fig. 3), ensuring plots, labels, legends, and screenshots remain clearly legible.

---

## Compilation Instructions

Run the standard compile sequence from the `Paper_2_Full_Latex/` directory:

```bash
cd "Paper_2_Full_Latex"
pdflatex paper2_main.tex
bibtex paper2_main
pdflatex paper2_main.tex
pdflatex paper2_main.tex
```

Or using `latexmk`:
```bash
latexmk -pdf paper2_main.tex
```

**Target output:** `paper2_main.pdf` — **6 pages, including references** (IEEE conference format).

---

## Summary of Completed Revisions

1. **Complete Independence from Previous Papers:**
   - Excised all mentions of "companion paper", "earlier publication", and `\cite{anirudhr2026turnaware}` across all sections.
   - Removed the entry from `paper2_verified_references.bib`, leaving exactly 15 verified, published literature citations with active DOIs.
   - Fully explained the state-expanded search graph, turn penalties, road-class impedance, and admissible heuristic self-contained within this paper.

2. **Condensation to 6-Page Budget:**
   - Author header compressed into a unified block.
   - Removed the redundant paper-organization paragraph at the end of Introduction.
   - Compressed Related Work into three concise thematic paragraphs.
   - Removed redundant text in Section III that merely repeated Figure 1.
   - In Results, let Tables I, II, and III communicate cell numbers while text focuses on analytical interpretation.
   - Grouped Discussion into four focused, high-density paragraphs.
   - Condensed Conclusion into a single unified paragraph.

3. **Zero Em Dashes:**
   - Completely eliminated `---` and `—` across the entire manuscript.

4. **Figure Readability Maintained:**
   - Preserved large two-column dimensions for Figures 2, 3, and 4 (`figure*`).
