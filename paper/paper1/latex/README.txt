Paper 1 — Overleaf package with improved figures

Files:
- paper1_main.tex
- paper1_verified_references.bib
- figures/fig1_exp_a_tradeoffs.{png,pdf}
- figures/fig2_exp_b_road_classes.{png,pdf}
- figures/fig3_exp_c_sensitivity.{png,pdf}

The LaTeX source includes the vector PDF versions of the three figures.
PNG versions are included as high-resolution previews/fallback assets.

The figures were regenerated from stage_2b_full_ablation_results.json using
the supplied analyze_stage2b_results.py plotting logic and the uploaded
experimental dataset. Plot data and measured outcomes were not changed.
The layouts were adjusted for single-column IEEE placement, with panels
stacked vertically where needed to improve label readability.

The revised manuscript was compiled locally with pdfLaTeX and BibTeX
(IEEEtran bibliography style). The resulting PDF is six pages.
Please recompile in Overleaf and run the conference's final PDF checker.
