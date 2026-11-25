# Research

Experiment code, evaluation pipelines, raw results, field-study data and audit reports for the
BLRMap studies. Application code lives in `../backend`. Manuscripts live in `../paper`.

```
research/
├── experiments/                   # Re-runnable experiment & benchmark scripts
│   ├── benchmark_three_heuristics.py      → literature_survey/09_astar_correction/
│   ├── benchmark_alternative_routing.py   → literature_survey/10_alternative_routing/
│   ├── evaluate_route_quality.py          → literature_survey/11_route_quality_evaluation/
│   ├── evaluate_parameter_sensitivity.py  → literature_survey/11_route_quality_evaluation/
│   ├── evaluate_runtime_variability.py    → literature_survey/11_route_quality_evaluation/
│   ├── generate_route_visualizations.py   → 11_route_quality_evaluation/visualizations/
│   ├── generate_runtime_charts.py         → 11_route_quality_evaluation/visualizations/
│   └── robustness_testing/                → literature_survey/12_robustness_testing/
├── literature_survey/             # Phase-by-phase research log (03 → 13) and results
│   ├── 03–08_*                    # Literature analysis, research gaps, feasibility, verification
│   ├── 09–12_*                    # A* correction, alternatives, route quality, robustness
│   ├── 13_ablation_study/         # FROZEN Phase 13.4 ablation dataset, harness and figures
│   ├── papers/                    # Source PDFs of surveyed papers
│   └── master_bibliography.(bib|md)
├── field_study/                   # Paper 2 real-world validation
│   ├── strava_phase2/             # GPX ride analysis (phase2_strava_analysis.py, CSVs, figure)
│   ├── expE_phase3/               # Exp. E offset vs. Yen comparison
│   ├── pilot_protocol/            # Anonymised pilot protocol and OD pairs
│   └── route_comparison_screenshots/  # BLRMap vs Google Maps vs Waze screenshots
├── audits/                        # Stand-alone verification reports
├── handover_package/              # Self-contained handover bundle; verify with SHA256_MANIFEST.txt
└── requirements.txt               # Extra analysis deps (numpy, pandas, scipy, matplotlib)
```

## Running experiments

Run every script **from the repository root**. The scripts add `backend/` to `sys.path`
themselves, and their output paths are relative to the root.

```bash
pip install -r backend/requirements.txt -r research/requirements.txt
python research/experiments/evaluate_route_quality.py
python research/experiments/robustness_testing/run_robustness_tests.py
```

> Re-running a script **overwrites** its result files under `literature_survey/`. Those results
> back the papers, so commit or back them up first.

### Frozen Phase 13 ablation study

`literature_survey/13_ablation_study/` is frozen (Phase 13.4, 2026-11-05) and was deliberately
left byte-for-byte unchanged by the repository reorganisation. Its scripts still add only the repo
root to `sys.path`, so to import the backend they now need `PYTHONPATH`:

```bash
# Only with explicit authorisation. This regenerates frozen results.
PYTHONPATH=backend python research/literature_survey/13_ablation_study/run_smoke_test.py
```

### Field-study scripts

These take input and output folders as arguments:

```bash
python research/field_study/strava_phase2/phase2_strava_analysis.py <gpx_dir> <out_dir>
python research/field_study/expE_phase3/phase3_expE_analysis.py <stage_2b_results.json> <out_dir>
```

The GPX source rides are in `handover_package/Evidence/`.

## Note on paths inside reports

The Markdown reports and handover documents are historical records. They cite file locations as
they were when written, for example `experiments/...`, `research/paper1_manuscript/...` or
`Paper_1_Full_Latex/...`. They were not rewritten, both to keep them faithful and because the
handover package is checksum-protected. Use [`../docs/PATH_MIGRATION.md`](../docs/PATH_MIGRATION.md)
to translate old paths to new ones.
