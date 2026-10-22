# Assessment 9 and Assessment 10 submissions

## What to submit

- **Assessment 9:** `Assessment9_IEEE_Report.pdf`. Six pages using the unchanged IEEEtran conference class, with two columns, numbered mathematical equations, five tables, four vector figures and seven numbered references.
- **Assessment 10:** `assessment10_final/Assessment10_Final.pptx`. Ten slides with editable numerical charts/table and speaker notes, planned for about nine minutes. It explains grokking, the experiment, Python/R implementation, statistical terms, results and limitations in plain language.
- **Short document alternative:** `assessment10_final/explanation.pdf` (two pages). Its editable wording is in `explanation.md`.
- **Presentation PDF:** `assessment10_final/Assessment10_Final.pdf` matches the exported slide images.

Replace the editable name, registration number and IEEE-report affiliation fields before uploading. No presenter identity has been inferred. Follow any additional template or page limit supplied by the teacher.

## Editing the report

`Assessment9_LaTeX_Source.zip` contains `main.tex`, the unmodified IEEEtran class, vector figures and reference metadata. Upload it to a LaTeX editor such as Overleaf and select `main.tex`. Edit the author block there. `assessment9_ieee/main.tex` is the same local source. The project contains an explicitly ordered bibliography in `main.tex`; the accompanying `.bib` records complete reusable source metadata.

The class comes from CTAN, with source URL and hash in `assessment9_ieee/TEMPLATE_SOURCE.md`. IEEE's author-center template guidance is linked there. This college assessment does not claim IEEE publication or acceptance.

## Scientific evidence and interpretation

The submissions reuse the completed, versioned study. No new experiments were needed for these assessment formats. `assessment_evidence.json` hashes the source tables and recorded presentation trace. The original reports and experiment data remain unchanged.

All six split/budget conditions appear in the results table. Each policy cell contains 30 fresh independent attempts. At 8,000 updates, one run succeeds 28/30 times on every split while four starts succeed 12/30, 9/30 and 11/30. All three contrasts survive the planned twelve-test Holm correction. At 12,000 updates, only the second-split four-run contrast survives correction. Two-run comparisons remain inconclusive. Results apply to this model, task and three fixed splits.

First confirmation requires three good checks. The secondary endpoint requires 21 checks spanning 500 updates and must finish inside the same allocated budget. It is a finite window rather than a guarantee about later accuracy. The original 120-run setting analyses remain supporting exploratory evidence.

## Rebuilding without training

From the repository root, using the existing project Python environment:

```powershell
$env:PYTHONPATH=(Get-Location).Path
.venv/Scripts/python.exe scripts/assessments/build_written.py
.tools/tectonic/tectonic.exe --outdir output/assessments/assessment9_ieee --keep-logs output/assessments/assessment9_ieee/main.tex
.venv/Scripts/python.exe scripts/assessments/package.py
```

The portable Tectonic compiler used for this delivery is version 0.17.0, from its official GitHub release. The compiler and downloaded TeX packages stay outside Git. A normal LaTeX installation or the supplied source ZIP is sufficient for editing the IEEE paper.

The presentation source is `scripts/assessments/presentation.mjs`. It runs against the first-party presentation model, including the live authoring session. `finalize_presentation.mjs --rebuild` also builds it with the bundled artifact runtime. Run a copy of that module from a private build directory whose `node_modules` junction points to the bundled runtime. Set `ASSESSMENT_PPTX` to a new output path because the finalizer preserves existing delivery files. It checks editable chart data, fonts and geometry, then imports and renders the final slides. Numerical chart values use eight decimal places for portable Office workbooks; source traces retain full precision.

Rebuilds can change PDF metadata. Recheck numerical and visual content and refresh the assessment manifest after edits. The live presentation and the local final file share the same source; final numerical chart snapshots add editable embedded workbooks.

## Originality review

`source_overlap.json` records a limited exact eight-word/twelve-word phrase screen against the six cited public research PDFs. It does not provide an institutional similarity score, an internet-wide comparison, an AI-authorship assessment or a novelty certificate. The college's official checker and its settings still govern submission review.

Grokking, restart theory, timing research, AdamW and transformer methods receive attribution. The proposed project contribution is the recorded empirical comparison, with fixed budgets, fresh validation and a distinct stability endpoint.
