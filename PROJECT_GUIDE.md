# Project guide

## How the project works

1. `grokking/` builds and trains the small model, measures accuracy and saves per-run traces and resumable checkpoints.
2. `configs/study.json` records the fixed settings, budgets and seed ranges. `data/summary.csv` and `data/policies.csv` hold run-level results; the full accuracy histories remain under `data/runs/`.
3. `analysis/analyze.R` reads the saved CSVs and writes tables and graphs under `output/review2/`.
4. `grokking/audit.py` checks that the summaries agree with the raw run traces. `grokking/report.py` assembles the paper-style PDF and Markdown under `output/pdf/`.
5. `presentation/final_prepare.py` gathers actual results for the final slides. The presentation files under `presentation/` build the editable deck, render each slide, export a matching PDF and check the final artifacts.

## Reproduce the saved final analysis

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\verify_project.py --reproduce
```

To also run the tests:

```powershell
.\.venv\Scripts\python.exe scripts\verify_project.py --reproduce --run-tests
```

These commands reproduce the R analysis, raw trace audit and report in an isolated temporary folder, then compare the generated tables and report text to the delivered outputs. They do not retrain the model. The original study collection commands and hardware/runtime details are in `README.md`.

## Main deliverables

- Final presentation and verification: `output/final_package/START_HERE.md`
- Final statistical report: `output/pdf/review2_report.pdf`
- Experimental protocol: `docs/PROTOCOL.md`
- Syllabus mapping: `docs/SYLLABUS_MAP.md`
- Source/contribution and similarity record: `output/final_package/SOURCE_AND_CONTRIBUTION.md`
- Paper documentation, abstract and bibliography: `paper/README.md`
- Mathematical/statistical details: `docs/PAPER_METHODS.md`
- Graph-to-data mapping: `docs/FIGURE_GUIDE.md`
- CSV fields and missing values: `docs/DATA_DICTIONARY.md`
