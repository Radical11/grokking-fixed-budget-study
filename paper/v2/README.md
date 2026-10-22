# Complete college paper: follow-up version

This version adds fresh policy validation at total budgets of 8,000 and 12,000 updates on three fixed dataset splits, plus a separately defined 500-update stability endpoint. It keeps the original model and numerical settings. The original delivery is archived by the `review2-original` Git tag at `d8ffc56`.

## Run and resume

From the repository root in PowerShell:

```powershell
.\run_paper_v2.ps1
```

The command resumes the fixed calibration/validation runs, runs tests, performs base-R analysis and the raw-trace audit, creates the eight-page paper and four-page supplement, builds the editable 15-slide presentation and matching PDF, screens prose against six cited PDFs, and independently reproduces numerical results, figures and manuscript text. It uses up to three worker processes, each with four CPU threads. Do not run two training parents for the same dataset concurrently.

Read progress without changing experimental files:

```powershell
.\run_paper_v2.ps1 -Status
```

Rebuild from already completed saved data without training:

```powershell
.\run_paper_v2.ps1 -AnalysisOnly
```

The presentation builder requires the documented Codex bundled artifact runtime. Scientific training and analysis use the existing Python environment and base R; no contributed R packages are required. Checkpoints are local and ignored by Git. If interrupted, resume the same command and seeds. Runtime is descriptive, and unsaved work may be repeated after recovery.

## Records and outputs

For a plain explanation of the code, training loop and data-to-paper path, see `CODE_WALKTHROUGH.md`. Use `DEFENSE_NOTES.md` for short answers to likely teacher questions.

- `configs/paper_study.json`: fixed design and counts.
- `docs/PAPER_V2_PROTOCOL.md`: prospective protocol and budget-selection disclosure.
- `docs/PAPER_V2_ANALYSIS_NOTES.md`: documented pre-validation boundary-interval detail.
- `data/paper_v2/seed_manifest.csv`: every planned run, with 20 explicitly reused source paths.
- `data/paper_v2/calibration_freeze.json` and `frozen_predictions.csv`: phase gate and frozen calibration predictions.
- `data/paper_v2/runs/`: individual configurations, traces, status and checkpoint files.
- `data/paper_v2/run_summary.csv` and `attempt_summary.csv`: endpoints and actual budget attempts.
- `output/paper_v2/`: numerical tables, eight PNG/vector-PDF figure pairs, paper/supplement Markdown/PDF, presentation, notes, source records and verification.

The final manuscript gate requires all 90 calibration observations and 540 complete policy attempts. It never substitutes planned results, synthetic test fixtures or unknown event times for actual evidence. The automated pipeline finishes in `awaiting_visual_review`; human page/slide inspection and any necessary repairs precede delivery.

## Edit the written paper without training

The delivered `paper.md` and `supplement.md` are the actual text sources used to typeset their PDFs. After editing wording or identity fields, render them directly:

```powershell
.\.venv\Scripts\python.exe -m grokking.paper_typesetting output/paper_v2/paper.md --output output/paper_v2/paper.pdf --pages 8
.\.venv\Scripts\python.exe -m grokking.paper_typesetting output/paper_v2/supplement.md --output output/paper_v2/supplement.pdf --pages 4
```

Keep figures beside the Markdown files. A standalone `---` starts a new page. Hidden Markdown comments specify caption style, figure width and table-column widths in inches; keep each comment in its own block. Ordinary paragraphs, headings, bold text, tables and figure links remain editable. The page-count check catches edits that overflow the requested length.

The complete analysis command regenerates these sources from the recorded results. Put lasting changes to generated prose in `grokking/paper_report.py` as well. A revised manuscript needs fresh numerical/visual checks and an updated package manifest to become a newly verified delivery.

## Interpretation

The primary endpoint confirms three checks; the secondary endpoint confirms 21, spanning 500 updates. Neither means permanent generalization. All policies use the same total logical budget within a condition. Exact intervals and twelve jointly Holm-adjusted Fisher tests accompany the first-confirmation comparisons. Bootstrap results remain available alongside conservative bounds that avoid collapsed uncertainty for constant binary groups. Results are separate for every split; small effects and equivalence may remain unresolved.

The source record and `LITERATURE_COMPARISON.md` attribute grokking, timing work, restart theory, multi-seed numerical controls, AdamW and transformer methods. They do not claim worldwide novelty or an institutional plagiarism score.
